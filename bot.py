import telebot
import time

TOKEN = '8440001186:AAF6wIlSpkeqN3_BxjD1yxpfRR15HQz9HuM'

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(
        message.chat.id,
        f"Привет, {message.from_user.first_name}! 👋\n\nЭто мини-приложение."
    )

@bot.message_handler(func=lambda m: True)
def echo(message):
    bot.send_message(message.chat.id, "Я ещё в разработке. Скоро появятся функции!")

if __name__ == "__main__":
    print("✅ Новый бот запущен")
    while True:
        try:
            bot.infinity_polling(timeout=60)
        except:
            time.sleep(5)
