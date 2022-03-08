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
        app_role = request.form.get('org_role')
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
        group_ids.append(row.user_id)
    user_groups = Group.query.filter(Group.id.in_(group_ids)).order_by(db.desc(Group.id)).all()
    messages = Message.query.filter_by(user_id=user.id).all()
    return render_template('edituser.html', user=user, user_groups=user_groups, user_messages=messages)