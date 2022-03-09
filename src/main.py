from flask import Blueprint, render_template, request, flash, url_for, redirect
from flask_login import login_required, current_user

from .constants import *
from .models import *

main = Blueprint('main', __name__)


# ГЛАВНЫЕ ОКНА!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# главная страница
@main.route('/')
def index():
    return render_template('index.html')


# отображение всех пользователей
@main.route('/workallusers')
@login_required
def workallusers():
    users = User.query.filter(User.status.in_([CONFIRMED, WAITING_ARCHIEVED])).order_by(User.name).all()
    relations = db.session.query(users_groups_relations).all()
    groups = Group.query.all()
    return render_template('workallusers.html', users=users, groups=groups, relations=relations)


# отображение пользователей по группам
@main.route('/workallgroups')
@login_required
def workallgroups():
    users = User.query.all()
    relations = db.session.query(users_groups_relations).all()
    groups = Group.query.order_by(db.desc(Group.id)).all()
    return render_template('workallgroups.html', users=users, groups=groups, relations=relations)
