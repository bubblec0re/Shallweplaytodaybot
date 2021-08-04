import telebot
import json

bot = telebot.TeleBot("***REMOVED***")


@bot.message_handler(commands=["help"])
def reply_to_help(message):
    bot.send_message(
        message.from_user.id,
        "Я ежедневно высылаю в группу опросник с вопросом, будем ли мы сегодня играть.",
    )

    save_message(message)


@bot.message_handler(commands=["poll"])
def send_poll(message):
    bot.send_poll(
        message.from_user.id,
        "Будем играть сегодня?",
        ["Да", "Нет", "Пока не знаю"],
        False,
    )

    save_message(message)


@bot.message_handler(content_types=["text"])
def get_text_messages(message):
    if message.text == "Тест":
        bot.send_message(message.from_user.id, "Тест сработал")
    else:
        bot.send_message(
            message.from_user.id, "Другого функционала пока не предусмотрено."
        )

    save_message(message)


def save_message(message):
    with open("messages.txt", 'a', encoding='utf-8') as f:
        json.dump(message.json, f, indent=4, ensure_ascii=False)


bot.polling(True, 2)
