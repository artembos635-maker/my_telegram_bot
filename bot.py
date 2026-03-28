import telebot
import time

TOKEN = '8749955457:AAFrM_9bMzQoT6ibN97Kx5SHHWTKHrS0QRc'
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Привет!")

@bot.message_handler(func=lambda m: True)
def echo(m):
    bot.send_message(m.chat.id, "Я ничего не умею. Напиши /start")

if __name__ == "__main__":
    print("✅ Пустой бот запущен")
    while True:
        try:
            bot.infinity_polling(timeout=60)
        except:
            time.sleep(5)
