import telebot
import json
import os
import time

TOKEN = '8749955457:AAFrM_9bMzQoT6ibN97Kx5SHHWTKHrS0QRc'
ADMINS = [7717477509]

bot = telebot.TeleBot(TOKEN)
USERS_FILE = 'users.json'

def is_admin(user_id):
    return user_id in ADMINS

def get_all_users():
    try:
        if not os.path.exists(USERS_FILE):
            return []
        with open(USERS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return []

def save_users(users):
    with open(USERS_FILE, 'w', encoding='utf-8') as f:
        json.dump(users, f, ensure_ascii=False, indent=2)

@bot.message_handler(commands=['clear_users'])
def clear_users(message):
    if not is_admin(message.from_user.id):
        bot.send_message(message.chat.id, "❌ Нет прав")
        return
    try:
        # Полное удаление
        save_users([])
        # Проверяем, что удалилось
        if os.path.exists(USERS_FILE):
            with open(USERS_FILE, 'r') as f:
                content = f.read()
            bot.send_message(message.chat.id, f"✅ Все пользователи удалены! Файл очищен.")
        else:
            bot.send_message(message.chat.id, "✅ Файл удалён.")
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Ошибка: {e}")

@bot.message_handler(commands=['users_count'])
def users_count(message):
    if not is_admin(message.from_user.id):
        return
    users = get_all_users()
    bot.send_message(message.chat.id, f"👥 Всего пользователей: {len(users)}")

@bot.message_handler(commands=['show_users'])
def show_users(message):
    if not is_admin(message.from_user.id):
        return
    users = get_all_users()
    if not users:
        bot.send_message(message.chat.id, "📭 Нет пользователей")
        return
    text = f"📋 Список ({len(users)}):\n\n"
    for i, u in enumerate(users, 1):
        text += f"{i}. {u.get('name', '?')} — ID: {u.get('id', '?')}\n"
        if len(text) > 3500:
            bot.send_message(message.chat.id, text)
            text = ""
    if text:
        bot.send_message(message.chat.id, text)

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Привет! Команды:\n/clear_users — удалить всех\n/users_count — количество\n/show_users — список")

@bot.message_handler(func=lambda m: True)
def echo(m):
    bot.send_message(m.chat.id, "Используй /start для списка команд")

if __name__ == "__main__":
    print("✅ Бот запущен")
    # Показываем текущее количество при старте
    users = get_all_users()
    print(f"👥 Текущих пользователей: {len(users)}")
    while True:
        try:
            bot.infinity_polling(timeout=60)
        except Exception as e:
            print(f"Ошибка: {e}")
            time.sleep(5)
