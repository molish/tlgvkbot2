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


@main.route('/workallgroups')
@login_required
def workallgroups():
    users = User.query.all()
    relations = db.session.query(users_groups_relations).all()
    groups = Group.query.all()
    users_with_groups = {}
    not_in_group = {}
    in_group = False
    for group in groups:
        userlist = []
        for user in users:
            for row in relations:
                if row.group_id == group.id and row.user_id == user.id:
                    in_group = True
                    break
            if not in_group:
                userlist.append(user)
            in_group = False
        not_in_group[group.id] = userlist
    return render_template('workallgroups.html', users=users, groups=groups, relations=relations,
                           not_in_group=not_in_group)
