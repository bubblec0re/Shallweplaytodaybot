import json
# import sched
# import time
import datetime as dt

import telebot
from telebot import apihelper


# https://api.telegram.org/bot***REMOVED***/getupdates

# Settings
#
apihelper.SESSION_TIME_TO_LIVE = 5*60
bot = telebot.TeleBot("***REMOVED***")
try:
    with open("settings.json") as f:
        bot_settings = json.load(f)
except Exception:
    bot_settings = {
        "group_id": None,
        "last_sent_poll_id": None,
        "auto_send_poll": False,
        "time_for_poll": 20,
        "last_manual_poll_time": 0,
    }
poll_send_task_id = 0


# Command and update handlers

@bot.message_handler(commands=["poll"])
def poll_reply(message: telebot.types.Message):

    save_message(message)

    try:
        bot.unpin_chat_message(
            bot_settings["group_id"], bot_settings["last_sent_poll_id"]
        )
    except Exception:
        pass

    chat_id = message.chat.id
    reply = send_poll(chat_id)
    bot_settings["last_manual_poll_time"] = dt.datetime.timestamp(dt.datetime.now())
    # schedule_poll_unpin()
    save_message(reply)


@bot.message_handler(commands=["autopollon", "autopolloff"])
def toggle_autopoll(message: telebot.types.Message):

    if message.text.startswith("/autopollon"):
        bot_settings["auto_send_poll"] = True
    elif message.text.startswith("/autopolloff"):
        bot_settings["auto_send_poll"] = False
    save_message(message)

    reply = bot.send_message(
        message.chat.id,
        f"""Автоматический опрос {'включен' if bot_settings['auto_send_poll'] else 'выключен'}. 
Время автоматического опроса: {bot_settings['time_for_poll']}:00.
Следующий автоматический опрос в: {next_datetime(dt.datetime.utcnow(), hour=bot_settings['time_for_poll'], minute=0, second=0)}""",
    )
    save_message(reply)

    save_settings_to_file()


@bot.message_handler(commands=["help"])
def reply_to_help(message: telebot.types.Message):
    save_message(message)

    reply = bot.send_message(
        message.chat.id,
        """Я ежедневно высылаю в группу опросник с вопросом "будем ли мы сегодня играть".
Допустимые команды:
/help - эта подсказка
/poll - инициировать новый опрос
/autopollon - включить автоматическую отправку опроса
/autopolloff - отключить автоматическую отправку опроса""",
    )
    save_message(reply)


@bot.my_chat_member_handler()
def membership_update_handler(chat_member_updated: telebot.types.ChatMemberUpdated):
    if chat_member_updated.new_chat_member.is_member:
        bot_settings["group_id"] = chat_member_updated.chat.id
        save_settings_to_file()


# Other functions

def save_message(message: telebot.types.Message):
    print(
        f"{dt.datetime.fromtimestamp(message.date)}: сообщение: {message.text} от {message.from_user.username}"
    )


def save_settings_to_file():
    with open("settings.json", "w") as f:
        json.dump(bot_settings, f)


def poll_answers():
    # return ["Да", "Скорее да", "Скорее нет", "Нет", "Пока не знаю"]
    return ["Да", "Нет", "Не знаю"]


def send_scheduled_poll():
    pass
    # if bot_settings["auto_send_poll"]:
    #     sent_poll = bot.send_poll(
    #         bot_settings["group_id"],
    #         "Будем играть сегодня?",
    #         poll_answers(),
    #         False,
    #     )

    #     bot_settings["last_sent_poll_id"] = sent_poll.message_id
    #     bot.pin_chat_message(bot_settings["group_id"], sent_poll.message_id)

    # next_time = next_datetime(
    #     dt.datetime.utcnow(), hour=bot_settings["time_for_poll"], minute=0, second=0
    # )
    # print(f"Время следующего автоматического опроса: {next_time}")
    # poll_scheduler.enterabs(dt.datetime.timestamp(next_time), 1, send_scheduled_poll)
    # schedule_poll_unpin()
    # save_settings_to_file()


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
    # schedule_poll_unpin()
    save_settings_to_file()
    return sent_poll


def next_datetime(current: dt.datetime, hour: int, **kwargs) -> dt.datetime:
    repl = current.replace(hour=hour, **kwargs)
    while repl <= current:
        repl = repl + dt.timedelta(days=1)
    return repl


def schedule_poll_unpin():
    pass
    # now = dt.datetime.utcnow()
    # next_time = next_datetime(now, hour=0, minute=0, second=0)
    # print(
    #     f"Время открепления опроса с ID {bot_settings['last_sent_poll_id']}: {next_time}"
    # )
    # poll_scheduler.enter(
    #     dt.datetime.timestamp(next_time),
    #     1,
    #     bot.unpin_chat_message,
    #     (bot_settings["group_id"], bot_settings["last_sent_poll_id"]),
    # )


# now = dt.datetime.utcnow()
# print(f"Текущее время: {now}")
# next_time = next_datetime(now, bot_settings["time_for_poll"], minute=0, second=0)
# print(f"Время следующего автоматического опроса: {next_time}")
# poll_scheduler = sched.scheduler(time.time, time.sleep)
# poll_scheduler.enterabs(dt.datetime.timestamp(next_time), 1, send_scheduled_poll)

print("bot polling started")
bot.polling(True, 2)

# pollScheduler.run(False)
# print('scheduler started')
