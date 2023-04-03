import os
from datetime import timedelta

from flask import Flask, render_template
from flask_session import Session
from mongoengine import connect

from utils import HTTPMethodOverrideMiddleware, SanitizedRequest

# Initialize app
app = Flask(__name__)

# Connect to MongoDB
connect(host=os.environ.get('MONGOURI'))

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
@app.route('/', methods=['GET'])
def main():
    return render_template('white_chat.html')


# Jinja filters
@app.template_filter('env_override')
def env_override(value, key):
    return os.getenv(key, value)
