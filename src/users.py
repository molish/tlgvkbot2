from flask import Blueprint, render_template, request, flash, url_for, redirect
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash

from .constants import *
from .models import *

users = Blueprint('users', __name__)


# ВСЕ ЧТО СВЯЗАНО С ПОЛЬЗОВАТЕЛЯМИ!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
@users.route('/createuser')
@login_required
def createuser():
    return render_template('createuser.html')


# метод добавления группы в бд
@users.route('/createuser', methods=['POST'])
@login_required
def createuser_post():
    db_name = request.form.get('user_name')
    db_phone_number = request.form.get('phone_number')
    db_org_role = request.form.get('org_role')
    db_app_role = USER
    db_password = ''
    if current_user.app_role == ADMIN:
        app_role = request.form.get('app_role')
        if app_role == ADMIN:
            db_app_role = ADMIN
        if app_role == MODERATOR:
            db_app_role = MODERATOR
        password = request.form.get('pass')
        if password:
            db_password = generate_password_hash(password, method='sha256')
    if not db_name or not db_phone_number:
        flash('Поля имени и телефона пользователя не могут быть пустыми')
        return redirect(url_for('users.createuser'))
    else:
        user = User.query.filter_by(phone_number=db_phone_number).first()
        if not user:
            user = User(name=db_name, phone_number=db_phone_number, app_role=db_app_role,
                        vk_authorized=False, tlg_authorized=False, status=WAITING_CONFIRMENT,
                        organisation_role=db_org_role, password=db_password)
            db.session.add(user)
            db.session.commit()
        else:
            flash(f'Пользователь с номером телефона {db_phone_number} уже существует!')
            return redirect(url_for('main.createuser'))
    return redirect(url_for('main.workallusers'))


@users.route('/<int:id>/edituser')
@login_required
def edituser(id):
    user = User.query.filter_by(id=id).first()
    relations = db.session.query(users_groups_relations).filter_by(user_id=user.id).all()
    group_ids = []
    for row in relations:
        group_ids.append(row.group_id)
    user_groups = Group.query.filter(Group.id.in_(group_ids)).order_by(db.desc(Group.id)).all()
    messages = Message.query.filter_by(user_id=user.id).all()
    user_groups_admin = Group.query.filter_by(owner_id=id).order_by(db.desc(Group.id)).all()
    msg_content = {}
    for message in messages:
        message.date = datetime.strptime(message.date, '%Y-%m-%d %H:%M:%S')
        db_msg = message.content.message
        db_sender = message.sender.name
        msg_content[f'message{message.id}'] = db_msg
        msg_content[f'sender{message.sender_id}'] = db_sender
    return render_template('edituser.html', user=user, user_groups=user_groups,
                           user_groups_admin=user_groups_admin,
                           user_messages=messages,
                           messages_content=msg_content)


@users.route('/<int:id>/edituser', methods=['POST'])
@login_required
def edituser_post(id):
    user = User.query.filter_by(id=id).first()
    if not user:
        flash('Такого пользователя не существует!')
        return redirect(url_for('main.workallusers'))
    new_user = User()
    db_name = request.form.get('user_name')
    db_phone_number = request.form.get('phone_number')
    db_org_role = request.form.get('org_role')
    db_password = ''
    if db_name:
        new_user.name = db_name
    else:
        new_user.name = user.name
    if db_phone_number:
        new_user.status = WAITING_CONFIRMENT
        new_user.phone_number = db_phone_number
    else:
        new_user.status = user.status
        new_user.phone_number = user.phone_number
    if db_org_role:
        new_user.organisation_role = db_org_role
    else:
        new_user.organisation_role = user.organisation_role
    if current_user.app_role == ADMIN:
        app_role = request.form.get('app_role')
        if app_role == ADMIN:
            new_user.app_role = ADMIN
        if app_role == MODERATOR:
            new_user.app_role = MODERATOR
        if app_role == USER:
            new_user.app_role = USER
        password = request.form.get('pass')
        if password:
            new_user.password = generate_password_hash(password, method='sha256')
    else:
        new_user.app_role = user.app_role
        new_user.password = user.password
    User.query.filter_by(id=id).update({
        'name': new_user.name,
        'password': new_user.password,
        'phone_number': new_user.phone_number,
        'app_role': new_user.app_role,
        'status': new_user.status,
        'organisation_role': new_user.organisation_role})
    db.session.commit()
    return redirect(url_for('users.edituser', id=id))


@users.route('/<int:id>/deleteuser')
@login_required
def deleteuser(id):
    user = User.query.filter_by(id=id).first()
    if current_user.app_role != ADMIN or current_user.id == user.id:  # чтобы сам себя не мог удалить
        return redirect(url_for('users.edituser', id=id))
    User.query.filter_by(id=id).delete()
    Message.query.filter_by(user_id=id).delete()
    db.session.query(users_groups_relations).filter_by(user_id=id).delete()
    db.session.commit()
    flash(f'Пользователь {user.name} {user.phone_number} удален')
    return redirect(url_for('main.workallusers'))


@users.route('/<int:id>/movetoarchive')
@login_required
def movetoarchive(id):
    user = User.query.filter_by(id=id).first()
    if current_user.app_role == ADMIN:
        User.query.filter_by(id=id).update({'status': ARCHIEVED})
        db.session.commit()
        flash(f'Пользователь {user.name} {user.phone_number} перенесен в архив')
    if current_user.app_role == MODERATOR:
        User.query.filter_by(id=id).update({'status': WAITING_ARCHIEVED})
        db.session.commit()
        flash(f'Пользователь {user.name} {user.phone_number} вскоре будет перенесен в архив')
    return redirect(url_for('users.edituser', id=id))


@users.route('/<int:id>/restoreuser')
@login_required
def restoreuser(id):
    user = User.query.filter_by(id=id).first()
    if current_user.app_role == ADMIN:
        User.query.filter_by(id=id).update({'status': CONFIRMED})
        db.session.commit()
        flash(f'Пользователь {user.name} {user.phone_number} восстановлен')
    if current_user.app_role == MODERATOR:
        User.query.filter_by(id=id).update({'status': WAITING_RESTORE})
        db.session.commit()
        flash(f'Пользователь {user.name} {user.phone_number} вскоре будет Восстановлен')
    return redirect(url_for('users.edituser', id=id))
