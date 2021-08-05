import telebot
import json, sched, time

# https://api.telegram.org/bot***REMOVED***/getupdates

try:
    f = open("settings.json")
    botSettings = json.load(f)
finally:
    botSettings = {
        "groupID": None,
        "lastSentPollID": None,
        "autoSendPoll": False,
        "timeForPoll": 0,
    }


bot = telebot.TeleBot("***REMOVED***")


@bot.message_handler(commands=["poll"])
def poll_reply(message: telebot.types.Message):

    save_message(message)

    chat_id = message.chat.id
    reply = send_poll(chat_id)
    save_message(reply)


def send_poll(chat_id: int):

    sentPoll = bot.send_poll(
        chat_id,
        "Будем играть сегодня?",
        ["Да", "Скорее да", "Скорее нет", "Нет", "Пока не знаю"],
        False,
    )

    botSettings.lastSentPollID = sentPoll.message_id
    bot.pin_chat_message(chat_id, sentPoll.message_id)
    return sentPoll


@bot.message_handler(commands=["autopollon", "autopolloff"])
def toggle_autopoll(message: telebot.types.Message):

    if message.text == "/autopollon":
        botSettings.autoSendPoll = True
    elif message.text == "autopolloff":
        botSettings.autoSendPoll = False

    save_settings_to_file()


@bot.message_handler(commands=["help"])
def reply_to_help(message):
    save_message(message)

    reply = bot.send_message(
        message.from_user.id,
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
    botSettings.groupID = chat_member_updated.chat.id


def save_message(message: telebot.types.Message):
    with open("messages.json", "a", encoding="utf-8") as f:
        json.dump("/n" + message.json, f, indent=4, ensure_ascii=False)


def save_settings_to_file():
    with open("settings.json", "w") as f:
        json.dump(botSettings, f)


pollScheduler = sched.scheduler(time.time, time.sleep)
pollScheduler.enterabs(time.time() + 60, 1, send_poll, (botSettings.groupID))

bot.polling(True, 2)
