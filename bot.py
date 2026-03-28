import telebot
import json
import os
import time

TOKEN = '8749955457:AAFrM_9bMzQoT6ibN97Kx5SHHWTKHrS0QRc'
ADMIN_ID = 7717477509  # ТВОЙ ID

bot = telebot.TeleBot(TOKEN)
USERS_FILE = 'users.json'

def get_all_users():
    try:
        if not os.path.exists(USERS_FILE):
            return []
        with open(USERS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return []

@bot.message_handler(commands=['clear_users'])
def clear_users(message):
    if message.from_user.id != ADMIN_ID:
        bot.send_message(message.chat.id, "❌ Нет прав. Только админ может очистить базу.")
        return
    try:
        with open(USERS_FILE, 'w', encoding='utf-8') as f:
            json.dump([], f)
        bot.send_message(message.chat.id, "✅ Все пользователи удалены!")
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Ошибка: {e}")

@bot.message_handler(commands=['users_count'])
def users_count(message):
    if message.from_user.id != ADMIN_ID:
        return
    users = get_all_users()
    bot.send_message(message.chat.id, f"👥 Всего пользователей: {len(users)}")

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Привет! Команды:\n/clear_users — удалить всех пользователей\n/users_count — показать количество")

@bot.message_handler(func=lambda m: True)
def echo(m):
    bot.send_message(m.chat.id, "Используй /start для списка команд")

if __name__ == "__main__":
    print("✅ Бот запущен. Админ ID: 7717477509")
    while True:
        try:
            bot.infinity_polling(timeout=60)
        except:
            time.sleep(5)
