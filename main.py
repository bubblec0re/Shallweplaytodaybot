import telebot

bot = telebot.TeleBot("***REMOVED***")


@bot.message_handler(commands=["help"])
def reply_to_help(message):
    bot.send_message(
        message.from_user.id,
        "Я ежедневно высылаю в группу опросник с вопросом, будем ли мы сегодня играть.",
    )


@bot.message_handler(content_types=["text"])
def get_text_messages(message):
    if message.text == "Тест":
        bot.send_message(message.from_user.id, "Тест сработал")
    else:
        bot.send_message(
            message.from_user.id, "Другого функционала пока не предусмотрено."
        )


bot.polling(True, 5)
