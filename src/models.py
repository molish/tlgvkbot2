from datetime import datetime

from flask_login import UserMixin

from . import db

users_groups_relations = db.Table('user_groups_relations',
                                  db.Column('group_id', db.Integer, db.ForeignKey('group.id')),
                                  db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
                                  extend_existing=True
                                  )


class User(UserMixin, db.Model):
    id = db.Column(db.Integer,
                   nullable=False,
                   unique=True,
                   primary_key=True,
                   autoincrement=True)  # primary keys are required by SQLAlchemy
    password = db.Column(db.String(100))  # пароль есть только у администраторов и модераторов
    name = db.Column(db.String(100))  # имя фамилия
    phone_number = db.Column(db.String(11), unique=True)  # номер телефона
    vk_authorized = db.Column(db.Boolean, default=False)  # авторизован вк или нет
    tlg_authorized = db.Column(db.Boolean, default=False)  # авторизован в телеграм или нет
    status = db.Column(db.String(30))  # статус пользователя(ожидает подтверждения\в архиве\подтвержден)
    app_role = db.Column(db.String(20))  # роль в приложении(админ, модератор, пользователь)
    organisation_role = db.Column(db.String(100))  # должность в организации


class Group(db.Model):
    id = db.Column(db.Integer,
                   nullable=False,
                   unique=True,
                   primary_key=True,
                   autoincrement=True)  # primary keys are required by SQLAlchemy
    name = db.Column(db.String(100), unique=True)  # название группы
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))  # идентификатор создателя или владельца
    owner = db.relationship('User', backref='owner', lazy='subquery')


class Content(db.Model):
    id = db.Column(db.Integer,
                   nullable=False,
                   unique=True,
                   primary_key=True,
                   autoincrement=True)  # primary keys are required by SQLAlchemy
    message = db.Column(db.String(10000))


class Message(db.Model):
    id = db.Column(db.Integer,
                   nullable=False,
                   unique=True,
                   primary_key=True,
                   autoincrement=True)  # primary keys are required by SQLAlchemy
    is_group = db.Column(db.Boolean, default=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    group_id = db.Column(db.Integer, db.ForeignKey('group.id'))
    content_id = db.Column(db.Integer, db.ForeignKey('content.id'))
    sender = db.relationship('User', foreign_keys=[sender_id], backref='sender', lazy='subquery')
    user = db.relationship('User', foreign_keys=[user_id], backref='user', lazy='subquery')
    group = db.relationship('Group', backref='group', lazy='subquery')
    content = db.relationship('Content', backref='content', lazy='subquery')
    tlg_received = db.Column(db.Boolean, default=False)
    vk_received = db.Column(db.Boolean, default=False)
    date = db.Column(db.TEXT, default=datetime.utcnow)
