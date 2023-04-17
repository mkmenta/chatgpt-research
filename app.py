import os
from datetime import timedelta

from flask import Flask, redirect, render_template, request, send_from_directory
from flask_session import Session
from flask_login import login_required, current_user

from mongoengine import connect
import pytz
from models.chat import Chat
from models.message import Message
from models.user import User
from routes.users import blueprint as users_blueprint, login_manager


from utils import HTTPMethodOverrideMiddleware, SanitizedRequest, TokenCounter, now_mytz
import openai
# Initialize app
app = Flask(__name__)

# Connect to MongoDB
connect(host=os.environ.get('MONGOURI'))

# Connect to OpenAI
openai.organization = os.getenv("OPENAI_ORGANIZATION")
openai.api_key = os.getenv("OPENAI_API_KEY")

# Initialize sessions
app.secret_key = os.environ.get('CHATGPT_RESEARCH_SECRET')
SESSION_COOKIE_NAME = "cgptrsch"  # Name of the session cookie in the browser
SESSION_USE_SIGNER = True  # Sign with secret key
SESSION_TYPE = 'filesystem'  # Save session data to file system
SESSION_FILE_DIR = '/tmp'  # Save session data into /tmp
SESSION_COOKIE_HTTPONLY = True  # Avoid XSS
PERMANENT_SESSION_LIFETIME = timedelta(days=7)  # Lifetime of the session cookie
# SESSION_COOKIE_SECURE = True  # TODO: this should be set for production
app.config.from_object(__name__)
Session(app)

SYSTEM_PROMPT = "You are a helpful assistant called ChatGPT."
SYSTEM_TOKENS = 17
MAX_TOKENS = 4097
MARGIN_TOKENS = 1024
MODEL = "gpt-3.5-turbo-0301"
token_counter = TokenCounter(MODEL)

# Add HTTP method override middleware (to allow PUT, DELETE etc.)
app.wsgi_app = HTTPMethodOverrideMiddleware(app.wsgi_app)

# Use improved Request class that sanitizes form data
app.request_class = SanitizedRequest

# Initialize app with login manager
login_manager.init_app(app)

app.register_blueprint(users_blueprint, url_prefix='/')


# Main routes
@app.route('/', methods=['GET'], defaults={'chat_id': None})
@app.route('/<chat_id>', methods=['GET'])
@login_required
def main(chat_id):
    user_id = request.args.get('user_id')
    user_to_show = User.objects.get(id=user_id) if user_id is not None else current_user
    chats = list(Chat.objects.filter(user=user_to_show))
    chats.reverse()
    usage = {chat.id: int(chat.total_tokens * 100 // (MAX_TOKENS - MARGIN_TOKENS))
             for chat in chats}
    if chat_id is not None:
        current_chat = Chat.objects.get(id=chat_id)
        if current_chat.user != user_to_show:
            raise Exception("Chat does not belong to user")
    else:
        current_chat = None
    if current_user.admin:
        users = User.objects.filter(username__not__startswith="test-")
    else:
        users = []
    return render_template('chat/chat2.html', chats=chats, current_chat=current_chat, users=users,
                           user_to_show=user_to_show, usage=usage)


@app.route('/new/messages/send', methods=['POST'], defaults={'chat_id': None})
@app.route('/<chat_id>/messages/send', methods=['POST'])
@login_required
def send_message(chat_id):
    if chat_id is not None:
        chat = Chat.objects.get(id=chat_id)
    else:
        chat = Chat(title=now_mytz().strftime("%d/%m/%Y, %H:%M"), user=current_user)
        chat.save()
    if chat.user != current_user:
        raise Exception("Chat does not belong to user")
    last_usr_msg = Message(role="user", content=request.form.get('message').striptags())
    last_usr_msg.num_tokens = token_counter.num_tokens_from_string(last_usr_msg.content)
    last_usr_msg.save()
    chat.messages.append(last_usr_msg)
    last_bot_msg = Message(role="assistant", content="Writing...")
    last_bot_msg.save()
    chat.messages.append(last_bot_msg)
    chat.save()
    messages = [{
        "role": "system",
        "content": SYSTEM_PROMPT
        # num_tokens=18
        # Answer as concisely as possible. "
        # f"Knowledge cutoff: 2021 Current date: {datetime.now().strftime('%d %B, %Y')}."
    }]
    message_objs = chat.messages
    if chat.total_tokens > (MAX_TOKENS-MARGIN_TOKENS + SYSTEM_TOKENS):
        # Keep last messages that sum less than (MAX_TOKENS-MARGIN_TOKENS + SYSTEM_TOKENS)
        n_tokens = 0
        for i in range(1, len(chat.messages)+1):
            n_tokens += chat.messages[-i].num_tokens
            if n_tokens > (MAX_TOKENS-MARGIN_TOKENS + SYSTEM_TOKENS):
                message_objs = message_objs[-i+1:]
                break
        del n_tokens
    messages.extend([
        {
            "role": msg.role,
            "content": msg.content
        }
        for msg in message_objs[:-1]
    ])
    try:
        response = openai.ChatCompletion.create(
            model=MODEL,
            messages=messages,
            temperature=0.7,
            top_p=1.,
            n=1,
            stream=False,
            stop=None,
            presence_penalty=0.,
            frequency_penalty=0.,
        )
        last_bot_msg.content = response['choices'][0]['message']['content']
        last_bot_msg.compute_time = response.response_ms/1000
        last_bot_msg.num_tokens = token_counter.num_tokens_from_string(last_bot_msg.content)
        last_bot_msg.save()
        chat.total_tokens = sum([msg.num_tokens for msg in chat.messages])
        chat.save()
    except Exception as e:
        print(f"Exception {type(e)}: {e.code} {e.user_message if hasattr(e,'user_message') else ''} {e}")
        last_bot_msg.delete()
        last_usr_msg.delete()
    return redirect(f"/{chat.id}")


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'imgs/favicon/favicon.ico', mimetype='image/vnd.microsoft.icon')


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=54928)
