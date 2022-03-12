import telebot
import re

from .models import *
from . import init_db

tgbot = telebot.TeleBot('5162461863:AAGpVulVti1UpHHx-kPBB4-CNZT9mpvfk6Q')
phone_num = re.compile('^((8|\+7)[\- ]?)?(\(?\d{3}\)?[\- ]?)?[\d\- ]{7,10}$')


def listen_tg_bot():
    tgbot.polling(none_stop=True, interval=1)


def send_message(text, chat_id, message_id):
    keyboard = telebot.types.InlineKeyboardMarkup()
    keyboard.add(telebot.types.InlineKeyboardButton(text="Получил", callback_data=message_id))
    await tgbot.send_message("Пожалуйста нажмите на кнопку получил, чтобы подтвердить что вы получили сообщение", reply_markup=keyboard)


@tgbot.message_handler(commands=['reg'])
def reg_command(message):
    with init_db().app_context():
        user = User.query.filter_by(tlg_chat_id=message.from_user.id).first()
        if not user:
            tgbot.send_message(message.from_user.id, "Введите свой номер телефона в формате 8 9** *** ** ** :")
        else:
            tgbot.send_message(user.tlg_chat_id,
                               f"Вы уже выполнили вход как пользователь: {user.name} с номером телефона: {user.phone_number} вы: {user.app_role}")


@tgbot.message_handler(regexp='^((8|\+7)[\- ]?)?(\(?\d{3}\)?[\- ]?)?[\d\- ]{7,10}$')
def phone_number(message):
    s = phone_num.match(message.text).string.replace(' ', '').replace('-','')
    tgbot.send_message(message.from_user.id, s)


@tgbot.message_handler(regexp='((8|\+7)[\- ]?)?(\(?\d{3}\)?[\- ]?)?[\d\- ]{7,10}')
def phone_number(message):
    s = phone_num.match(message.text)
    tgbot.send_message(message.from_user.id, 'неверно введен номер телефона, строка не должна содержать иных символов и слов кроме номера телефона')

@tgbot.message_handler(content_types=['text'])
def get_text_messages(message):
    tgbot.send_message(message.from_user.id,
                       "Если вы еще не выполнили вход: отправьте команду /reg\n, иначе просто периодически проверяйте входящие сообщения")
