import json

import datetime as dt

import telebot
from telebot import apihelper


### https://api.telegram.org/bot***REMOVED***/getupdates

### Settings

apihelper.SESSION_TIME_TO_LIVE = 5 * 60
bot = telebot.TeleBot("***REMOVED***")
try:
    with open("settings.json") as f:
        bot_settings = json.load(f)
except Exception:
    bot_settings = {
        "group_id": None,
        "last_sent_poll_id": None,
        "last_manual_poll_time": 0,
    }
poll_send_task_id = 0


### Command and update handlers


@bot.message_handler(commands=["poll"])
def poll_reply(message: telebot.types.Message):

    save_message(message)

    if message.chat.type != "private":
        try:
            bot.unpin_chat_message(
                bot_settings["group_id"], bot_settings["last_sent_poll_id"]
            )
        except Exception:
            pass

    chat_id = message.chat.id
    reply = send_poll(chat_id)
    bot_settings["last_manual_poll_time"] = dt.datetime.timestamp(dt.datetime.now())
    save_message(reply)


@bot.message_handler(commands=["help"])
def reply_to_help(message: telebot.types.Message):
    save_message(message)

    reply = bot.send_message(
        message.chat.id,
        """Я ежедневно высылаю в группу опросник с вопросом "будем ли мы сегодня играть".
Допустимые команды:
/help - эта подсказка
/poll - инициировать новый опрос""",
    )
    save_message(reply)


### Other functions


def save_message(message: telebot.types.Message):
    print(
        f"{dt.datetime.fromtimestamp(message.date)}: сообщение: {message.text} от {message.from_user.username}"
    )


def save_settings_to_file():
    with open("settings.json", "w") as f:
        json.dump(bot_settings, f, ensure_ascii=False)


def poll_answers():
    try:
        with open("answers.json", "r") as f:
            answers = json.loads(f)
    except Exception:
        answers = ["Да", "Нет", "Не знаю"]
        with open("answers.json", "w") as f:
            json.dump(answers, f, ensure_ascii=False)
    return answers


def send_poll(chat_id: int):

    sent_poll = bot.send_poll(
        chat_id,
        "Будем играть сегодня?",
        poll_answers(),
        False,
    )

    if bot_settings["last_sent_poll_id"] != 0:
        try:
            bot.unpin_chat_message(chat_id, bot_settings["last_sent_poll_id"])
        except Exception:
            pass

    bot_settings["last_sent_poll_id"] = sent_poll.message_id
    bot.pin_chat_message(chat_id, sent_poll.message_id)
    save_settings_to_file()
    return sent_poll


print("bot polling started")
bot.infinity_polling()
