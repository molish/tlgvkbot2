from flask import Blueprint, render_template
from flask_login import login_required, current_user
from . import db
from . import models
from .models import User

main = Blueprint('main', __name__)


@main.route('/')
def index():
    return render_template('index.html')


@main.route('/workallusers')
@login_required
def profile():
    users = User.query.filter_by().all()
    return render_template('workallusers.html', users=users)
