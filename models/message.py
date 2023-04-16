from utils import now_mytz
from mongoengine import Document, fields


class Message(Document):
    role = fields.StringField(required=True)
    content = fields.StringField(required=True)
    created_at = fields.DateTimeField(required=True, default=now_mytz)
