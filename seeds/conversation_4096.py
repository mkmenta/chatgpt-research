"""Script to test cases with maximum number of tokens."""
import os
import random

from mongoengine import connect

from models.chat import Chat
from models.message import Message
from models.user import User
from utils import TokenCounter, now_mytz

TEXT = "ChatGPT is an AI-powered conversational chatbot created using Natural Language Processing (NLP) and Machine Learning (ML) technologies. The development of ChatGPT involved several steps, including: 1. Data Collection: Massive amounts of conversational data were collected from various sources, including social media, messaging apps, and online forums. 2. Preprocessing: The collected data was preprocessed to remove irrelevant information, such as emoji, URLs, and special characters. 3. Training: The preprocessed data was then used to train a deep learning model based on the GPT (Generative Pre-trained Transformer) architecture. The model was trained to understand natural language and generate responses based on the context of the conversation. 4. Testing and Fine-tuning: After training, the model was tested on a set of validation data to ensure its performance. The model was then fine-tuned based on the feedback received from the validation data. ChatGPT is an AI-powered conversational chatbot created using Natural Language Processing (NLP) and Machine Learning (ML) technologies. The development of ChatGPT involved several steps, including: 1. Data Collection: Massive amounts of conversational data were collected from various sources, including social media, messaging apps, and online forums. 2. Preprocessing: The collected data was preprocessed to remove irrelevant information, such as emoji, URLs, and special characters. 3. Training: The preprocessed data was then used to train a deep learning model based on the GPT (Generative Pre-trained Transformer) architecture. The model was trained to understand natural language and generate responses based on the context of the conversation. 4. Testing and Fine-tuning: After training, the model was tested on a set of validation data to ensure its performance. The model was then fine-tuned based on the feedback received from the validation data."

if __name__ == "__main__":
    connect(host=os.environ.get('MONGOURI'))

    user = User.objects.get(username="mkmenta")

    chat = Chat(title=now_mytz().strftime("%d/%m/4096, %H:%M"), user=user)
    chat.save()
    token_counter = TokenCounter()
    NTOKENS = token_counter.num_tokens_from_string(TEXT)
    for i in range((4096 // (NTOKENS*2))+1):
        last_usr_msg = Message(role="user", content=TEXT)
        last_usr_msg.num_tokens = NTOKENS
        last_usr_msg.save()
        chat.messages.append(last_usr_msg)
        last_bot_msg = Message(role="assistant", content=TEXT)
        last_bot_msg.num_tokens = NTOKENS
        last_bot_msg.save()
        chat.messages.append(last_bot_msg)
    chat.save()
    chat.total_tokens = sum([msg.num_tokens for msg in chat.messages])
    chat.save()
