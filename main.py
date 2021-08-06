import telebot
import json
import sched, time
import datetime as dt

# https://api.telegram.org/bot***REMOVED***/getupdates

# Settings
#
bot = telebot.TeleBot("***REMOVED***")
try:
    f = open("settings.json")
    botSettings = json.load(f)
except Exception:
    botSettings = {
        "groupID": None,
        "lastSentPollID": None,
        "autoSendPoll": False,
        "timeForPoll": 20,
    }
pollSendTaskID = 0


# Command and update handlers
#
@bot.message_handler(commands=["poll"])
def poll_reply(message: telebot.types.Message):

    save_message(message)

    chat_id = message.chat.id
    reply = send_poll(chat_id)
    schedule_poll_unpin()
    save_message(reply)


@bot.message_handler(commands=["autopollon", "autopolloff"])
def toggle_autopoll(message: telebot.types.Message):

    if message.text == "/autopollon":
        botSettings["autoSendPoll"] = True
    elif message.text == "autopolloff":
        botSettings["autoSendPoll"] = False
    save_message(message)

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
    with open("updates.json", "a", encoding="utf-8") as f:
        chat_info = vars(chat_member_updated.chat)
        chat_info["AmMember"] = chat_member_updated.new_chat_member.is_member
        json.dump(chat_info, f, indent=4, ensure_ascii=False)
    botSettings["groupID"] = chat_member_updated.chat.id
    save_settings_to_file()


# Other functions
#
def save_message(message: telebot.types.Message):
    with open("messages.json", "a", encoding="utf-8") as f:
        json.dump(message.json, f, indent=4, ensure_ascii=False)


def save_settings_to_file():
    with open("settings.json", "w") as f:
        json.dump(botSettings, f)


def poll_answers():
    # return ["Да", "Скорее да", "Скорее нет", "Нет", "Пока не знаю"]
    return ["Да", "Нет"]


def send_scheduled_poll():

    if botSettings["autoSendPoll"]:
        sentPoll = bot.send_poll(
            botSettings["groupID"],
            "Будем играть сегодня?",
            poll_answers(),
            False,
        )

        botSettings["lastSentPollID"] = sentPoll.message_id
        bot.pin_chat_message(botSettings["groupID"], sentPoll.message_id)

    next_time = dt.datetime.timestamp(
        next_datetime(dt.datetime.utcnow(), hour=botSettings["timeForPoll"])
    )
    pollScheduler.enterabs(next_time, 1, send_scheduled_poll)
    schedule_poll_unpin()
    save_settings_to_file()


def send_poll(chat_id: int):

    sentPoll = bot.send_poll(
        chat_id,
        "Будем играть сегодня?",
        poll_answers(),
        False,
    )

    if botSettings["lastSentPollID"] != 0:
        try:
            bot.unpin_chat_message(chat_id, botSettings["lastSentPollID"])
        except Exception:
            pass

    botSettings["lastSentPollID"] = sentPoll.message_id
    bot.pin_chat_message(chat_id, sentPoll.message_id)
    save_settings_to_file()
    return sentPoll


def next_datetime(current: dt.datetime, hour: int, **kwargs) -> dt.datetime:
    repl = current.replace(hour=hour, **kwargs)
    while repl <= current:
        repl = repl + dt.timedelta(days=1)
    return repl


def schedule_poll_unpin():
    now = dt.datetime.utcnow()
    next_time = dt.datetime.timestamp(next_datetime(now, hour=0))
    pollScheduler.enter(
        next_time,
        1,
        bot.unpin_chat_message,
        (botSettings["groupID"], botSettings["lastSentPollID"]),
    )


now = dt.datetime.utcnow()
next_time = dt.datetime.timestamp(next_datetime(now, hour=botSettings["timeForPoll"]))
pollScheduler = sched.scheduler(time.time, time.sleep)
pollScheduler.enterabs(next_time, 1, send_scheduled_poll)
# pollScheduler.run()


bot.polling(True, 2)
