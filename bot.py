import telebot
from telebot import types
import json
import os
import time

TOKEN = '8786806064:AAGnZbQeNQCow4txVsS_O_-BQkDLkARk6RU'
ADMIN_ID = 7717477509

bot = telebot.TeleBot(TOKEN)
USERS_FILE = 'users.json'

# ------------------ РАБОТА С ПОЛЬЗОВАТЕЛЯМИ ------------------
def get_users():
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

def add_user(user_id, name, username):
    users = get_users()
    for u in users:
        if u.get('id') == user_id:
            return False
    users.append({
        'id': user_id,
        'name': name,
        'username': username or 'нет username'
    })
    save_users(users)
    return True

# ------------------ КНОПКИ ------------------
def start_keyboard():
    markup = types.InlineKeyboardMarkup()
    btn = types.InlineKeyboardButton(
        text="🌿 БАДы", 
        url="https://nspgoods.by/bady/"
    )
    markup.add(btn)
    return markup

# ------------------ КОМАНДЫ ------------------
@bot.message_handler(commands=['start'])
def start(message):
    add_user(message.chat.id, message.from_user.first_name, message.from_user.username)
    bot.send_message(
        message.chat.id,
        f"Привет, {message.from_user.first_name}! 👋\n\n"
        f"Я бот о биологически активных добавках.\n"
        f"Нажми на кнопку, чтобы перейти в каталог.",
        reply_markup=start_keyboard()
    )

@bot.message_handler(commands=['users'])
def users_count(message):
    if message.from_user.id != ADMIN_ID:
        return
    users = get_users()
    bot.send_message(message.chat.id, f"👥 Всего пользователей: {len(users)}")

@bot.message_handler(commands=['users_list'])
def users_list(message):
    if message.from_user.id != ADMIN_ID:
        return
    users = get_users()
    if not users:
        bot.send_message(message.chat.id, "📭 Нет пользователей")
        return
    text = f"📋 Список ({len(users)}):\n\n"
    for i, u in enumerate(users, 1):
        un = f"@{u['username']}" if u['username'] != 'нет username' else 'без username'
        text += f"{i}. {u['name']} ({un}) — ID: {u['id']}\n"
        if len(text) > 3500:
            bot.send_message(message.chat.id, text)
            text = ""
    if text:
        bot.send_message(message.chat.id, text)

@bot.message_handler(commands=['broadcast'])
def broadcast(message):
    if message.from_user.id != ADMIN_ID:
        bot.send_message(message.chat.id, "❌ Нет прав")
        return
    
    text = message.text.replace('/broadcast', '', 1).strip()
    if not text:
        bot.send_message(message.chat.id, "❌ Введите текст\nПример: /broadcast Всем привет!")
        return
    
    users = get_users()
    if not users:
        bot.send_message(message.chat.id, "📭 Нет пользователей")
        return
    
    # Текст с подписью "Модератор"
    broadcast_text = f"🛡️ **Сообщение от модератора:**\n\n{text}"
    
    bot.send_message(message.chat.id, f"📢 Рассылка {len(users)} пользователям...")
    
    ok = 0
    fail = 0
    
    for u in users:
        try:
            bot.send_message(u['id'], broadcast_text, parse_mode="Markdown")
            ok += 1
            time.sleep(0.05)
        except:
            fail += 1
    
    bot.send_message(
        message.chat.id,
        f"✅ Отправлено: {ok}\n❌ Не доставлено: {fail}\n👥 Всего: {len(users)}"
    )

# ------------------ ЗАПУСК ------------------
if __name__ == "__main__":
    print("✅ Бот Badiworldbot запущен")
    print(f"Админ: {ADMIN_ID}")
    print(f"Пользователей: {len(get_users())}")
    
    while True:
        try:
            bot.infinity_polling(timeout=60)
        except:
            time.sleep(5)
