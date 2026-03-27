import telebot
from telebot import types
import requests
import time
import os
import json

TOKEN = '8749955457:AAFrM_9bMzQoT6ibN97Kx5SHHWTKHrS0QRc'
OPENROUTER_API_KEY = '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'
ADMIN_ID = 8749955457

bot = telebot.TeleBot(TOKEN)
user_state = {}
USERS_FILE = 'users.json'

def save_user(user_id, first_name, username):
    try:
        users = get_all_users()
        for user in users:
            if user['id'] == user_id:
                return False
        users.append({
            'id': user_id,
            'name': first_name,
            'username': username or 'нет username'
        })
        with open(USERS_FILE, 'w', encoding='utf-8') as f:
            json.dump(users, f, ensure_ascii=False, indent=2)
        return True
    except:
        return False

def get_all_users():
    try:
        if not os.path.exists(USERS_FILE):
            return []
        with open(USERS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return []

def ask_ai(msg, name):
    """Запрос к OpenRouter (DeepSeek)"""
    try:
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "deepseek/deepseek-chat",
                "messages": [
                    {"role": "system", "content": f"Ты дружелюбный помощник по имени Губаты. Общаешься с {name}. Отвечай кратко и дружелюбно."},
                    {"role": "user", "content": msg}
                ],
                "max_tokens": 500
            },
            timeout=30
        )
        
        if response.status_code != 200:
            return f"😕 Ошибка API: {response.status_code}"
        
        data = response.json()
        return data['choices'][0]['message']['content']
        
    except Exception as e:
        return f"😵 Ошибка: {e}"

@bot.message_handler(commands=['67'])
def send_67(message):
    for i in range(67):
        bot.send_message(message.chat.id, "six seven")

@bot.message_handler(commands=['users'])
def show_users_count(message):
    if message.from_user.id != ADMIN_ID:
        return
    users = get_all_users()
    bot.send_message(message.chat.id, f"👥 Всего: {len(users)}")

@bot.message_handler(commands=['users_list'])
def show_users_list(message):
    if message.from_user.id != ADMIN_ID:
        return
    users = get_all_users()
    if not users:
        bot.send_message(message.chat.id, "📭 Нет пользователей")
        return
    text = f"📋 Список ({len(users)}):\n\n"
    for i, u in enumerate(users, 1):
        un = f"@{u['username']}" if u['username'] != 'нет username' else 'без username'
        text += f"{i}. {u['name']} ({un}) — ID: {u['id']}\n"
    bot.send_message(message.chat.id, text)

@bot.message_handler(commands=['broadcast'])
def broadcast(message):
    if message.from_user.id != ADMIN_ID:
        bot.send_message(message.chat.id, "❌ Нет прав")
        return
    text = message.text.replace('/broadcast', '', 1).strip()
    if not text:
        bot.send_message(message.chat.id, "❌ Введите текст")
        return
    users = get_all_users()
    if not users:
        bot.send_message(message.chat.id, "📭 Нет пользователей")
        return
    bot.send_message(message.chat.id, f"📢 Рассылка {len(users)} пользователям...")
    ok = 0
    fail = 0
    for u in users:
        try:
            bot.send_message(u['id'], f"📢 {text}")
            ok += 1
            time.sleep(0.05)
        except:
            fail += 1
    bot.send_message(message.chat.id, f"✅ Отправлено: {ok}\n❌ Не доставлено: {fail}")

@bot.message_handler(commands=['start'])
def start(message):
    save_user(message.chat.id, message.from_user.first_name, message.from_user.username)
    user_state[message.chat.id] = None
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton("🤖 Начать чат"))
    bot.send_message(
        message.chat.id,
        f"Привет, {message.from_user.first_name}! 👋\n\n"
        f"Я Губаты. Нажми '🤖 Начать чат' чтобы поговорить со мной.",
        reply_markup=markup
    )

@bot.message_handler(func=lambda m: True)
def handle(m):
    uid = m.chat.id
    txt = m.text
    
    if txt == "🔴 Выключить Губатого":
        user_state[uid] = None
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(types.KeyboardButton("🤖 Начать чат"))
        bot.send_message(uid, "Чат завершён", reply_markup=markup)
        return
    
    if user_state.get(uid) == "chat":
        bot.send_chat_action(uid, 'typing')
        ans = ask_ai(txt, m.from_user.first_name)
        bot.send_message(uid, ans)
        return
    
    if txt == "🤖 Начать чат":
        user_state[uid] = "chat"
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(types.KeyboardButton("🔴 Выключить Губатого"))
        bot.send_message(uid, "🤖 Режим чата включён! Пиши сообщения.", reply_markup=markup)
        return
    
    bot.send_message(uid, "Нажми '🤖 Начать чат' чтобы общаться")

if __name__ == "__main__":
    print("✅ Бот с OpenRouter запущен")
    while True:
        try:
            bot.infinity_polling(timeout=60)
        except:
            time.sleep(5)
