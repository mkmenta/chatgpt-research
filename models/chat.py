from mongoengine import Document, fields, PULL, EmbeddedDocument

from models.message import Message
from models.user import User
from utils import now_mytz


class Chat(Document):
    title = fields.StringField(required=True)
    user = fields.ReferenceField(User, required=True)
    messages = fields.ListField(fields.ReferenceField(Message, reverse_delete_rule=PULL))  # Auto-remove if Review removed
    created_at = fields.DateTimeField(required=True, default=now_mytz)
