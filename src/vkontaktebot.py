import re

import vk_api

from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.utils import get_random_id

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
                    send_vkmessage(text=f'Ваш номер {phone_num.match(event.text).string}', chat_id=event.user_id)
                else:
                    send_vkmessage(text=f'Неизвестна команда попробуйте снова {event.user_id}', chat_id=event.user_id)
