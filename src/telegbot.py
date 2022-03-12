import telebot
import re

from .models import *
from . import main

tgbot = telebot.TeleBot('5162461863:AAGpVulVti1UpHHx-kPBB4-CNZT9mpvfk6Q')


def listen_tg_bot():
    tgbot.polling(none_stop=True, interval=1)


def send_message(text, chat_id):
    tgbot.send_message(chat_id, text)


@tgbot.message_handler(commands=['reg'])
def reg_command(message):
    with main:
        user = User.query.filter_by(tlg_chat_id=message.from_user.id).first()
        if not user:
            tgbot.send_message(message.from_user.id, "Введите свой номер телефона в формате 8 9** *** ** ** :")
        else:
            tgbot.send_message(user.tlg_chat_id,
                         f"Вы уже выполнили вход как пользователь: {user.name} с номером телефона: {user.phone_number} вы: {user.app_role}")


@tgbot.message_handler(regexp="\b\[8](\s*\d{3}\s*\d{3}\s*\d{2}\s*\d{2})\b")
def phone_number(message):
    s = re.fullmatch(r'\b\[8](\s*\d{3}\s*\d{3}\s*\d{2}\s*\d{2})\b', message.text)
    tgbot.send_message(message.from_user.id, s)


@tgbot.message_handler(content_types=['text'])
def get_text_messages(message):
    tgbot.send_message(message.from_user.id,
                       "Если вы еще не выполнили вход: отправьте команду /reg\n, иначе просто периодически проверяйте входящие сообщения")
