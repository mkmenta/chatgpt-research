from bson import ObjectId
from flask import Blueprint, render_template, request, flash, abort, redirect, session
from flask_login import LoginManager, login_user, login_required, logout_user
from mongoengine import NotUniqueError, DoesNotExist

from models.user import User
from utils import is_safe_url

blueprint = Blueprint('users', __name__, template_folder='templates')

login_manager = LoginManager()

login_manager.login_view = "/login"
login_manager.login_message_category = "error"


@login_manager.user_loader
def load_user(user_id):
    return User.objects.get(id=ObjectId(user_id))


@blueprint.route('/register', methods=['GET'])
def register_user():
    return render_template('users/register.html')


@blueprint.route('/register', methods=['POST'])
def post_register_user():
    try:
        user = User.register(**request.form)
    except NotUniqueError:
        flash("User already exists.", "error")
        return redirect("/register")
    flash('User registered!', 'success')
    return redirect("/register")


@blueprint.route('/login', methods=['GET'])
def get_login_user():
    # session['next'] = request.args.get('next')
    return render_template('users/login.html')


@blueprint.route('/login', methods=['POST'])
def post_login_user():
    try:
        user = User.objects.get(username=request.form['username'])
        if user.authenticate(request.form['password']):
            login_user(user)
            # flash('Welcome back!', 'success')
            # next = session['next']
            # del session['next']
            # if not is_safe_url(next):
            # return abort(400)
            return redirect('/terms')
    except DoesNotExist:
        pass
    flash("Password or username is incorrect.", "error")
    return redirect("/login")


@blueprint.route('/logout', methods=['GET'])
@login_required
def get_logout_user():
    logout_user()
    flash('Goodbye!', 'success')
    return redirect('/')
