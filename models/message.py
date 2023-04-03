from mongoengine import Document, fields


class Message(Document):
    role = fields.StringField(required=True)
    content = fields.StringField(required=True)
