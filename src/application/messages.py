import threading
import time
import traceback

from flask import Blueprint, render_template, request, flash, url_for, redirect
from flask_login import login_required, current_user
from sqlalchemy import or_

from app import init_db
from telegbot import send_tgmessage
from vkontaktebot import send_vkmessage
from constants import *
from models import *

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
    if user.tlg_authorized or user.vk_authorized:
        message_text = request.form.get('message_content')
        content = Content.query.filter_by(message=message_text).first()
        if not content:
            content = Content(message=message_text)
            db.session.add(content)
            db.session.commit()
        message = Message(is_group=False,
                          user_id=user.id,
                          sender_id=current_user.id,
                          content_id=content.id,
                          tlg_received=False,
                          vk_received=False,
                          date=datetime.strftime(datetime.utcnow(), '%Y-%m-%d %H:%M:%S'))
        db.session.add(message)
        db.session.commit()
        if user.tlg_authorized:
            send_tgmessage(f'{message.content.message}\n\nОтправитель:{message.sender.name}\n',
                           chat_id=user.tlg_chat_id, message_id=message.id)
            flash('Сообщение отправлено в телеграм')
        if user.vk_authorized:
            send_vkmessage(f'{message.content.message}\n\nОтправитель:{message.sender.name}\n', chat_id=user.vk_chat_id)
            flash('Сообщение отправлено в вк')
    else:
        flash('Нельзя отправить сообщение пользователю который не подтвердил один из мессенджеров')
    return redirect(url_for('messages.usermessage', id=id))


@messages.route('/<int:id>/groupmessage', methods=['POST'])
@login_required
def groupmessage_post(id):
    message_text = request.form.get('message_content')
    try:
       sender = threading.Thread(target=send_group_mailing, args=(id, message_text, current_user.id)).start()
    except BaseException as e:
        print('SENDER EXCEPTION:', traceback.format_exc())
    return redirect(url_for('messages.groupmessage', id=id))


def send_group_mailing(id, message_text, current_user_id):
    with init_db().app_context():
        group = Group.query.filter_by(id=id).first()
        relations = db.session.query(users_groups_relations).filter_by(group_id=group.id).all()
        if len(relations) > 0:
            group_users = []
            for row in relations:
                group_users.append(row.user_id)
            users = User.query.filter(User.id.in_(group_users)).filter(or_(User.tlg_authorized == True, User.vk_authorized==True)).order_by(User.name).all()
            counter = 1
            content = Content.query.filter_by(message=message_text).first()
            if not content:
                content = Content(message=message_text)
                db.session.add(content)
                db.session.commit()
            for user in users:
                if counter > 28:
                    time.sleep(2)
                    counter = 1
                message = Message(is_group=True,
                                  user_id=user.id,
                                  sender_id=current_user_id,
                                  content_id=content.id,
                                  group_id=group.id,
                                  tlg_received=False,
                                  vk_received=False,
                                  date=datetime.strftime(datetime.utcnow(), '%Y-%m-%d %H:%M:%S'))
                db.session.add(message)
                db.session.commit()
                if user.tlg_authorized:
                    send_tgmessage(
                        f'{message.content.message}\n\nОтправитель:\n    группа: {group.name}\n   {message.sender.name}\n',
                        chat_id=user.tlg_chat_id, message_id=message.id)
                if user.vk_authorized:
                    send_vkmessage(
                        f'{message.content.message}\n\nОтправитель:\n  группа: {group.name}\n  {message.sender.name}\n',
                        chat_id=user.vk_chat_id)
