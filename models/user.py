from utils import now_mytz
import bcrypt
from flask_login import UserMixin
from mongoengine import Document, fields


class User(Document, UserMixin):
    username = fields.StringField(required=True, unique=True)
    email = fields.StringField(required=True, unique=True)
    hash = fields.StringField(required=True)
    admin = fields.BooleanField(default=False)
    terms_accepted = fields.BooleanField(default=False)
    created_at = fields.DateTimeField(required=True, default=now_mytz)

    @staticmethod
    def register(username: str, email: str, password: str):
        salt = bcrypt.gensalt()  # rounds=12 by default
        hashpw = bcrypt.hashpw(password.encode('utf-8'), salt)
        user = User(username=username, email=email, hash=hashpw)
        user.save()
        return user

    def update_password(self, password: str):
        salt = bcrypt.gensalt()  # rounds=12 by default
        hashpw = bcrypt.hashpw(password.encode('utf-8'), salt)
        self.hash = hashpw.decode('utf-8')
        self.save()

    def authenticate(self, password: str):
        if bcrypt.checkpw(password.encode('utf-8'), self.hash.encode('utf-8')):
            return True
        else:
            return False
