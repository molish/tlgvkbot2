from flask import Blueprint, render_template, request, flash, url_for, redirect
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash

from .constants import *
from .models import *

messages = Blueprint('messages', __name__)


@messages.route('/<int:id>/groupmessages')
@login_required
def groupmessages(id):
    group = Group.query.filter_by(id=id).first()
    if current_user.app_role != ADMIN and current_user.id != group.owner_id:
        flash(f'Только модератор группы и администратор могут просматривать сообщения группы: {group.name}!')
        return redirect(url_for('main.workallgroups'))
    messages = Message.query.filter_by(group_id=group.id).all()
    msg_content = {}
    if len(messages) <= 0:
        no_messages = True
    else:
        no_messages = False
        for message in messages:
            message.date = datetime.strptime(message.date, '%Y-%m-%d %H:%M:%S')
            db_msg = message.content.message
            db_sender = message.sender.name
            db_receiver = message.user.name
            msg_content[f'message{message.id}'] = db_msg
            msg_content[f'sender{message.sender_id}'] = db_sender
            msg_content[f'receiver{message.user_id}'] = db_receiver
    return render_template('groupmessages.html', group=group, messages=messages, messages_content=msg_content,
                           noMessages=no_messages)


@messages.route('/<int:id>/groupmessage')
@login_required
def groupmessage(id):
    group = Group.query.filter_by(id=id).first()
    owner = User.query.filter_by(id=group.owner_id).first()
    return render_template('groupmessage.html', group=group, owner=owner)


@messages.route('/<int:id>/usermessage')
@login_required
def usermessage(id):
    user = User.query.filter_by(id=id).first()
    return render_template('usermessage.html', user=user)


@messages.route('/<int:id>/usermessage', methods=['POST'])
@login_required
def usermessage_post(id):
    user = User.query.filter_by(id=id).first()
    return render_template('usermessage.html', user=user)
