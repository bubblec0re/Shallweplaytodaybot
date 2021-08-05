import telebot
import json

bot = telebot.TeleBot("***REMOVED***")
# https://api.telegram.org/bot***REMOVED***/getupdates


try:
    f = open("settings.json")
    bot_settings = json.load(f)
finally:
    bot_settings = {"groupID": None, "lastSentPollID": None, "autoSendPoll": False}


@bot.message_handler(commands=["poll"])
def poll_reply(message):
    save_message(message)

    chat_id = message.chat.id
    reply = send_poll_reply(message)
    save_message(reply)
    bot.pin_chat_message(chat_id, reply.message_id)


def send_poll_reply(message: telebot.types.Message):
    chat_id = message.chat.id
    reply = bot.send_poll(
        chat_id,
        "Будем играть сегодня?",
        ["Да", "Скорее да", "Скорее нет", "Нет", "Пока не знаю"],
        False,
    )
    return reply


@bot.message_handler(commands=["autopollon", "autopolloff"])
def toggle_autopoll(message: telebot.types.Message):
    if message.text == "/autopollon":
        bot_settings.autoSendPoll = True
    elif message.text == "autopolloff":
        bot_settings.autoSendPoll = False

    save_settings()


@bot.message_handler(commands=["help"])
def reply_to_help(message):
    save_message(message)

    reply = bot.send_message(
        message.from_user.id,
        """Я ежедневно высылаю в группу опросник с вопросом "будем ли мы сегодня играть".
        Допустимые команды: /help, /poll, /autopollon, /autopolloff""",
    )
    save_message(reply)


@bot.my_chat_member_handler()
def membership_update_handler(chat_member_updated: telebot.types.ChatMemberUpdated):
    with open("updates.json", "a", encoding="utf-8") as f:
        chat_info = vars(chat_member_updated.chat)
        chat_info["AmMember"] = chat_member_updated.new_chat_member.is_member
        json.dump(chat_info, f, indent=4, ensure_ascii=False)
    bot_settings.groupID = chat_member_updated.chat.id


def save_message(message: telebot.types.Message):
    with open("messages.json", "a", encoding="utf-8") as f:
        json.dump("/n" + message.json, f, indent=4, ensure_ascii=False)


def save_settings():
    with open("settings.json", "w") as f:
        json.dump(bot_settings, f)


bot.polling(True, 2)
