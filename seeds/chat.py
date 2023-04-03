"""Seed MongoDB with data."""
import os
import random

from mongoengine import connect

from models.chat import Chat
from models.message import Message
from models.user import User

if __name__ == "__main__":
    connect(host=os.environ.get('MONGOURI'))

    user = User.objects.get(username="student1")

    # Remove all chats and messages
    Chat.drop_collection()
    Message.drop_collection()
    with open('seeds/lorem.txt', 'r') as f:
        lorem = f.read().splitlines()

    # Add random chats
    K = 5
    chats = []
    for i in range(K):
        chats.append(
            Chat(
                title=f"Chat {i}",
                user=user,
                messages=[

                ]
            )

        )
    Chat.objects.insert(chats)
    for chat in chats:
        for j in range(random.randint(1, 10)):
            msg = Message(
                role='user' if j % 2 == 0 else 'assistant',
                content=lorem[random.randint(0, len(lorem) - 1)]
            )
            msg.save()
            chat.messages.append(msg)
            chat.save()
