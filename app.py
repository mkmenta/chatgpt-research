import os
from datetime import timedelta
from datetime import datetime

from flask import Flask, redirect, render_template, request
from flask_session import Session
from mongoengine import connect
from models.chat import Chat
from models.message import Message

from utils import HTTPMethodOverrideMiddleware, SanitizedRequest
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


# Add HTTP method override middleware (to allow PUT, DELETE etc.)
app.wsgi_app = HTTPMethodOverrideMiddleware(app.wsgi_app)

# Use improved Request class that sanitizes form data
app.request_class = SanitizedRequest

# Initialize app with login manager
# login_manager.init_app(app)


# Main routes
@app.route('/', methods=['GET'], defaults={'chat_id': None})
@app.route('/<chat_id>', methods=['GET'])
def main(chat_id):
    chats = Chat.objects.all()
    if chat_id is not None:
        current_chat = Chat.objects.get(id=chat_id)
    else:
        current_chat = None
    return render_template('chat/chat.html', chats=chats, current_chat=current_chat)


@app.route('/new/messages/send', methods=['POST'], defaults={'chat_id': None})
@app.route('/<chat_id>/messages/send', methods=['POST'])
def send_message(chat_id):
    if chat_id is not None:
        chat = Chat.objects.get(id=chat_id)
    else:
        chat = Chat(title=datetime.now().strftime("%m/%d/%Y, %H:%M"))
        chat.save()
    last_msg = Message(role="user", content=request.form.get('message').striptags())
    last_msg.save()
    chat.messages.append(last_msg)
    last_msg = Message(role="assistant", content="...")
    last_msg.save()
    chat.messages.append(last_msg)
    chat.save()
    messages = [{
        "role": "system",
        "content": "You are a helpful assistant called ChatGPT."
        # Answer as concisely as possible. "
        # f"Knowledge cutoff: 2021 Current date: {datetime.now().strftime('%d %B, %Y')}."
    }]
    messages.extend([
        {
            "role": msg.role,
            "content": msg.content
        }
        for msg in chat.messages
    ])
    # print(messages)
    # response = {'choices': [{'message': {'content': 'Hello world'}}]}
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages
    )
    last_msg.content = response['choices'][0]['message']['content']
    last_msg.save()
    return redirect(f"/{chat.id}")


# Jinja filters
@app.template_filter('env_override')
def env_override(value, key):
    return os.getenv(key, value)


""" Tackle plan:
1. Send post
2. Create a fake message "..."
3. Make visible last message with javascript and disable send mesage
4. The redirect will give the new conversation

In case before 4 the user refreshes the page
should see the fake message
If the last message is a ... then with javascript force a refresh of the page each 3 secs and disable send message
That should do it
"""
