from flask import Blueprint, render_template, request, flash, url_for, redirect
from flask_login import login_required, current_user
from sqlalchemy import insert, delete, and_

from .constants import *
from .models import *

groups = Blueprint('groups', __name__)


# ВСЕ ЧТО СВЯЗАНО С ГРУППАМИ !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# окно создания группы
@groups.route('/creategroup')
@login_required
def creategroup():
    return render_template('creategroup.html')


# метод добавления группы в бд
@groups.route('/creategroup', methods=['POST'])
@login_required
def creategroup_post():
    group_name = request.form.get('group_name')
    if not group_name:
        flash('Имя группы не может быть пустым')
        return redirect(url_for('groups.creategroup'))
    else:
        group = Group(name=group_name, owner_id=current_user.id)
        db.session.add(group)
        db.session.commit()
    return redirect(url_for('main.workallgroups'))


# окно редактирования и просмотра группы с пользователями
@groups.route('/<int:id>/editgroup')
@login_required
def editgroup(id):
    group = Group.query.filter_by(id=id).first()
    if current_user.app_role != ADMIN and current_user.id != group.owner_id:
        flash(f'Только модератор группы и администраторы могут просматривать информацию о группе {group.name}!')
        return redirect(url_for('main.workallusers'))
    owner = User.query.filter_by(id=group.owner_id).first()
    relations = db.session.query(users_groups_relations).filter_by(group_id=group.id).all()
    group_users = []
    for row in relations:
        group_users.append(row.user_id)
    users = User.query.filter(User.id.in_(group_users)).order_by(User.name).all()
    not_in_group = User.query.filter(User.id.not_in(group_users),
                                     User.status.in_([WAITING_RESTORE, WAITING_CONFIRMENT, CONFIRMED])).order_by(
        User.name).all()
    return render_template('editgroup.html', group=group, owner=owner, users=users, not_in_group=not_in_group)


# мето добавления изменений в группу в бд
@groups.route('/<int:id>/editgroup', methods=['POST'])
@login_required
def editgroup_post(id):
    new_group_name = request.form.get('new_group_name')
    if not new_group_name:
        flash('Имя группы не может быть пустым')
    else:
        Group.query.filter_by(id=id).update({'name': new_group_name})
        db.session.commit()
    return redirect(url_for('groups.editgroup', id=id))


# метод удаления группы из бд
@groups.route('/<int:id>/deletegroup')
@login_required
def deletegroup(id):
    group = Group.query.filter_by(id=id).first()
    if current_user.app_role != ADMIN and current_user.id != group.owner_id:
        flash(f'Только модератор группы и администраторы могут удалить группу: {group.name}!')
        return redirect(url_for('groups.editgroup', id=id))
    Group.query.filter_by(id=id).delete()
    db.session.query(users_groups_relations).filter_by(group_id=id).delete()
    db.session.commit()
    flash('Группа удалена')
    return redirect(url_for('main.workallgroups'))


@groups.route('/<int:user_id>-<int:group_id>/removeuser')
@login_required
def removeuser(user_id, group_id):
    user = User.query.filter_by(id=user_id).first()
    group = Group.query.filter_by(id=group_id).first()
    rel = db.session.query(users_groups_relations).filter_by(group_id=group.id, user_id=user.id).first()
    if rel:
        old_rel = delete(users_groups_relations).where(users_groups_relations.c.group_id==group.id).where(users_groups_relations.c.user_id==user.id)
        db.session.execute(old_rel)
        db.session.commit()
        flash(f'Пользователь {user.name} {user.phone_number} удален')
    return redirect(url_for('groups.editgroup', id=group.id))


@groups.route('/<int:user_id>-<int:group_id>/adduser')
@login_required
def adduser(user_id, group_id):
    user = User.query.filter_by(id=user_id).first()
    group = Group.query.filter_by(id=group_id).first()
    rel = db.session.query(users_groups_relations).filter_by(group_id=group.id, user_id=user.id).first()
    if not rel:
        new_rel = users_groups_relations.insert().values(group_id=group.id, user_id=user.id)
        db.session.execute(new_rel)
        db.session.commit()
        flash(f'Пользователь {user.name} {user.phone_number} добавлен')
    return redirect(url_for('groups.editgroup', id=group.id))
