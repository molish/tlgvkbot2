import re

import vk_api

from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.utils import get_random_id

from src import init_db, db
from src.constants import CONFIRMED
from src.models import User

vk_session = vk_api.VkApi(token='c9f2b2ddad9d6fcedbe9b4f217c030ef233f5b8cd7ff0cf2bec0420a7445bc065c4581d4fd71e9e541a84')
phone_num = re.compile('^((8|\+7)[\- ]?)?(\(?\d{3}\)?[\- ]?)?[\d\- ]{7,10}$')


def send_vkmessage(text, chat_id):
    vk = vk_session.get_api()
    vk.messages.send(user_id=chat_id, message=f"{text}", random_id=get_random_id())


def start_vkbot():
    longpoll = VkLongPoll(vk_session)
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me and event.text:
            if event.from_user:
                if phone_num.match(event.text):
                    with init_db().app_context():
                        s = phone_num.match(event.text).string.replace(' ', '').replace('-', '')
                        user = User.query.filter_by(phone_number=s).first()
                        if user and not user.vk_authorized:
                            User.query.filter_by(phone_number=s).update(
                                {'status': CONFIRMED, 'vk_authorized': True, 'vk_chat_id': event.user_id})
                            db.session.commit()
                            send_vkmessage(f'Вы успешно авторизованы как пользователь {user.name} {user.phone_number}',
                                           event.user_id)
                        elif user and user.tlg_authorized and user.vk_chat_id == event.user_id:
                            send_vkmessage(f'Вы уже авторизованы как пользователь {user.name} {user.phone_number}',
                                           event.user_id)
                        elif user and user.vk_authorized and user.vk_chat_id != event.user_id:
                            send_vkmessage('Пользователь с таким номером телефона уже авторизован в системе',
                                           event.user_id)
                        else:
                            send_vkmessage('Пользователь с таким номером телефона еще не добавлен администратором, обратитесь к администратору для решения этого вопроса',
                                               event.user_id)
                elif event.text == '/reg':
                    with init_db().app_context():
                        user = User.query.filter_by(vk_chat_id=event.user_id).first()
                        if not user:
                            send_vkmessage("Введите свой номер телефона в формате 8 9** *** ** ** :", event.user_id)
                        else:
                            send_vkmessage(f"Вы уже выполнили вход как пользователь: {user.name} с номером телефона: {user.phone_number} вы: {user.app_role}",
                                user.vk_chat_id)
                else:
                    send_vkmessage(text=f'Отправьте команду /reg для авторизации', chat_id=event.user_id)
