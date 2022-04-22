import telebot
import re
from .constants import CONFIRMED

from .models import *
from . import init_db, db

tgbot = telebot.TeleBot('5162461863:AAGpVulVti1UpHHx-kPBB4-CNZT9mpvfk6Q')
phone_num = re.compile('^((8|\+7)[\- ]?)?(\(?\d{3}\)?[\- ]?)?[\d\- ]{7,10}$')
msg_id = re.compile('^msg(\d{1,10})$')


def listen_tg_bot():
    tgbot.polling(none_stop=True, interval=1)


def send_tgmessage(text, chat_id, message_id):
    keyboard = telebot.types.InlineKeyboardMarkup()
    keyboard.add(telebot.types.InlineKeyboardButton(text="Получил", callback_data=f'msg{message_id}'))
    tgbot.send_message(text=f"{text}\n\n\nПожалуйста нажмите на кнопку получил, чтобы подтвердить, что вы получили сообщение",
                       chat_id=chat_id,
                       reply_markup=keyboard)


@tgbot.callback_query_handler(func=lambda call: msg_id.match(call.data))
def mark_msg(call: telebot.types.CallbackQuery):
    with init_db().app_context():
        chat_id = call.from_user.id
        message_id = re.search('(\d{1,10})',call.data).group()
        user = User.query.filter_by(tlg_chat_id=chat_id).first()
        if user:
            message = Message.query.filter_by(id=message_id, user_id=user.id).first()
            if message:
                Message.query.filter_by(id=message_id).update({'tlg_received': True})
                db.session.commit()


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
    with init_db().app_context():
        s = phone_num.match(message.text).string.replace(' ', '').replace('-', '')
        user = User.query.filter_by(phone_number=s).first()
        if user and not user.tlg_authorized:
            User.query.filter_by(phone_number=s).update({'status': CONFIRMED, 'tlg_authorized': True, 'tlg_chat_id': message.chat.id})
            db.session.commit()
            tgbot.send_message(message.from_user.id,
                               f'Вы успешно авторизованы как пользователь {user.name} {user.phone_number}')
        elif user and user.tlg_authorized and user.tlg_chat_id == message.chat.id:
            tgbot.send_message(message.from_user.id,
                               f'Вы уже авторизованы как пользователь {user.name} {user.phone_number}')
        elif user and user.tlg_authorized and user.tlg_chat_id != message.chat.id:
            tgbot.send_message(message.from_user.id, 'Пользователь с таким номером телефона уже авторизован в системе')
        else:
            tgbot.send_message(message.from_user.id,
                'Пользователь с таким номером телефона еще не добавлен администратором, обратитесь к администратору для решения этого вопроса')


@tgbot.message_handler(regexp='((8|\+7)[\- ]?)?(\(?\d{3}\)?[\- ]?)?[\d\- ]{7,10}')
def phone_number_wrong(message):
    s = phone_num.match(message.text)
    tgbot.send_message(message.from_user.id,
                       'неверно введен номер телефона, строка не должна содержать иных символов и слов кроме номера телефона')


@tgbot.message_handler(content_types=['text'])
def get_text_messages(message):
    tgbot.send_message(message.from_user.id,
                       "Если вы еще не выполнили вход: отправьте команду /reg\n, иначе просто периодически проверяйте входящие сообщения")
