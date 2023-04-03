from mongoengine import Document, fields, PULL, EmbeddedDocument

from models.message import Message
# from models.user import User


class Chat(Document):
    title = fields.StringField(required=True)
    # author = fields.ReferenceField(User)
    messages = fields.ListField(fields.ReferenceField(Message, reverse_delete_rule=PULL))  # Auto-remove if Review removed
