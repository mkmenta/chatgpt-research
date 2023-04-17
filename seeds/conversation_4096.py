"""Script to test cases with maximum number of tokens."""
import os
import random

from mongoengine import connect

from models.chat import Chat
from models.message import Message
from models.user import User
from utils import now_mytz

if __name__ == "__main__":
    connect(host=os.environ.get('MONGOURI'))

    user = User.objects.get(username="mkmenta")

    chat = Chat(title=now_mytz().strftime("%d/%m/4096, %H:%M"), user=user)
    chat.save()

    n_tokens = 400
    for i in range((4096 // n_tokens)+1):
        last_usr_msg = Message(role="user", content="Message 1")
        last_usr_msg.num_tokens = n_tokens
        last_usr_msg.save()
        chat.messages.append(last_usr_msg)
        last_bot_msg = Message(role="assistant", content="Answer 1")
        last_bot_msg.num_tokens = n_tokens
        last_bot_msg.save()
        chat.messages.append(last_bot_msg)
    chat.save()
    chat.total_tokens = sum([msg.num_tokens for msg in chat.messages])
    chat.save()
