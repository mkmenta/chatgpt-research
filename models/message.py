from utils import now_mytz
from mongoengine import Document, fields


class Message(Document):
    role = fields.StringField(required=True)
    content = fields.StringField(required=True)
    compute_time = fields.FloatField(required=True, default=0.0)
    num_tokens = fields.IntField(required=True, default=0)
    created_at = fields.DateTimeField(required=True, default=now_mytz)
