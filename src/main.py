from flask import Blueprint, render_template
from flask_login import login_required, current_user
from .models import *

main = Blueprint('main', __name__)


@main.route('/')
def index():
    return render_template('index.html')


@main.route('/workallusers')
@login_required
def workallusers():
    users = User.query.all()
    relations = db.session.query(users_groups_relations).all()
    groups = Group.query.all()
    return render_template('workallusers.html', users=users, groups=groups, relations=relations)


@main.route('./workallusers')
@login_required
def workallgroups():
    users = User.query.all()
    relations = db.session.query(users_groups_relations).all()
    groups = Group.query.all()
    return render_template('workallgroups.html', users=users, groups=groups, relations=relations)