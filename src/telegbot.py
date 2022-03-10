import threading
import telebot

tgbot = telebot.TeleBot('5162461863:AAGpVulVti1UpHHx-kPBB4-CNZT9mpvfk6Q')



def listen_tg_bot():
    tgbot.polling(none_stop=True, interval=1)


@tgbot.message_handler(content_types=['text'])
def get_text_messages(message):
    if message.text == "Привет":
        tgbot.send_message(message.from_user.id, "Привет, чем я могу тебе помочь?")
    elif message.text == "/help":
        tgbot.send_message(message.from_user.id, "Напиши привет")
    else:
        tgbot.send_message(message.from_user.id, "Я тебя не понимаю. Напиши /help.")
