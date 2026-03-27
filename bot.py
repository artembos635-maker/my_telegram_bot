import telebot
from telebot import types
import requests
import time
import random
import os
import json

TOKEN = '8749955457:AAFrM_9bMzQoT6ibN97Kx5SHHWTKHrS0QRc'
DEEPSEEK_API_KEY = 'sk-ba66a52f0c8c46698cb924c3469b86e8'
ADMIN_ID = 8749955457  # ТВОЙ TELEGRAM ID

bot = telebot.TeleBot(TOKEN)
user_state = {}  # None или 'chat'

# Файлы для хранения
USERS_FILE = 'users.json'  # теперь JSON, чтобы хранить имена и ID

# ========== ФУНКЦИИ ДЛЯ РАБОТЫ С ПОЛЬЗОВАТЕЛЯМИ ==========
def save_user(user_id, first_name, username):
    """Сохраняет пользователя с именем и username"""
    try:
        # Загружаем существующих пользователей
        users = get_all_users()
        
        # Проверяем, есть ли уже такой ID
        user_exists = False
        for user in users:
            if user['id'] == user_id:
                user_exists = True
                break
        
        # Если нет — добавляем
        if not user_exists:
            users.append({
                'id': user_id,
                'name': first_name,
                'username': username or 'нет username'
            })
            
            with open(USERS_FILE, 'w', encoding='utf-8') as f:
                json.dump(users, f, ensure_ascii=False, indent=2)
            return True
        return False
    except Exception as e:
        print(f"Ошибка сохранения: {e}")
        return False

def get_all_users():
    """Возвращает список всех пользователей с их данными"""
    try:
        if not os.path.exists(USERS_FILE):
            return []
        with open(USERS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return []

def get_all_user_ids():
    """Возвращает список всех ID пользователей"""
    users = get_all_users()
    return [str(user['id']) for user in users]

# ========== КОМАНДА /67 ==========
@bot.message_handler(commands=['67'])
def send_67(message):
    for i in range(67):
        bot.send_message(message.chat.id, "six seven")

# ========== КОМАНДА /users (количество) ==========
@bot.message_handler(commands=['users'])
def show_users_count(message):
    if message.from_user.id != ADMIN_ID:
        return
    users = get_all_users()
    bot.send_message(message.chat.id, f"👥 Всего пользователей: {len(users)}")

# ========== КОМАНДА /users_list (список с именами) ==========
@bot.message_handler(commands=['users_list'])
def show_users_list(message):
    if message.from_user.id != ADMIN_ID:
        bot.send_message(message.chat.id, "❌ Нет доступа")
        return
    
    users = get_all_users()
    if not users:
        bot.send_message(message.chat.id, "📭 Нет сохранённых пользователей")
        return
    
    text = f"📋 **Список пользователей ({len(users)}):**\n\n"
    for i, user in enumerate(users, 1):
        username_display = f"@{user['username']}" if user['username'] != 'нет username' else 'без username'
        text += f"{i}. **{user['name']}** ({username_display}) — ID: `{user['id']}`\n"
    
    # Разбиваем на несколько сообщений, если слишком длинное
    if len(text) > 4000:
        bot.send_message(message.chat.id, text[:4000])
        bot.send_message(message.chat.id, text[4000:])
    else:
        bot.send_message(message.chat.id, text, parse_mode="Markdown")

# ========== РАССЫЛКА ==========
@bot.message_handler(commands=['broadcast'])
def broadcast(message):
    if message.from_user.id != ADMIN_ID:
        bot.send_message(message.chat.id, "❌ У вас нет прав на рассылку")
        return
    
    text = message.text.replace('/broadcast', '', 1).strip()
    if not text:
        bot.send_message(message.chat.id, "❌ Введите текст\nПример: /broadcast Привет!")
        return
    
    users = get_all_users()
    if not users:
        bot.send_message(message.chat.id, "📭 Нет пользователей")
        return
    
    bot.send_message(message.chat.id, f"📢 Рассылка {len(users)} пользователям...")
    
    success = 0
    failed = 0
    
    for user in users:
        try:
            bot.send_message(user['id'], f"📢 **Сообщение от админа:**\n\n{text}", parse_mode="Markdown")
            success += 1
            time.sleep(0.05)
        except:
            failed += 1
    
    bot.send_message(
        message.chat.id,
        f"✅ **Рассылка завершена!**\n\n"
        f"📨 Отправлено: {success}\n"
        f"❌ Не доставлено: {failed}\n"
        f"👥 Всего: {len(users)}"
    )

# ========== ИИ ==========
def ask_deepseek(user_message, user_name):
    try:
        if not DEEPSEEK_API_KEY:
            return "🔑 Ключ DeepSeek не настроен"
        
        url = "https://api.deepseek.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "deepseek-chat",
            "messages": [
                {"role": "system", "content": f"Ты дружелюбный ИИ-помощник. Тебя зовут Губаты. Ты общаешься с пользователем по имени {user_name}. Отвечай кратко и дружелюбно."},
                {"role": "user", "content": user_message}
            ],
            "max_tokens": 500
        }
        
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        
        if response.status_code != 200:
            return f"😕 Ошибка API: {response.status_code}"
        
        data = response.json()
        return data['choices'][0]['message']['content']
        
    except Exception as e:
        return f"😵 Ошибка: {str(e)}"

# ========== КЛАВИАТУРЫ ==========
def chat_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton("🔴 Выключить Губатого"))
    return markup

def start_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton("🤖 Начать чат"))
    return markup

# ========== СТАРТ ==========
@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.chat.id
    user_name = message.from_user.first_name
    username = message.from_user.username
    
    # Сохраняем пользователя
    save_user(user_id, user_name, username)
    
    user_state[user_id] = None
    bot.send_message(
        message.chat.id,
        f"Привет, {user_name}! 👋\n\n"
        f"Я Губаты — твой ИИ-помощник.\n"
        f"Нажми '🤖 Начать чат' чтобы общаться.",
        reply_markup=start_keyboard()
    )

# ========== ОБРАБОТКА СООБЩЕНИЙ ==========
@bot.message_handler(func=lambda m: True)
def handle(m):
    uid = m.chat.id
    text = m.text
    
    # Сохраняем пользователя, если он пишет (на всякий случай)
    save_user(uid, m.from_user.first_name, m.from_user.username)
    
    if text == "🔴 Выключить Губатого":
        user_state[uid] = None
        bot.send_message(uid, "Чат завершён", reply_markup=start_keyboard())
        return
    
    if user_state.get(uid) == "chat":
        bot.send_chat_action(uid, 'typing')
        answer = ask_deepseek(text, m.from_user.first_name)
        bot.send_message(uid, answer)
        return
    
    if text == "🤖 Начать чат":
        user_state[uid] = "chat"
        bot.send_message(
            uid,
            "🤖 Режим чата включён!\n\n"
            "Просто пиши сообщения, я буду отвечать.\n"
            "Чтобы выйти — нажми '🔴 Выключить Губатого'",
            reply_markup=chat_keyboard()
        )
        return
    
    else:
        bot.send_message(uid, "Нажми '🤖 Начать чат' чтобы общаться")

# ========== ЗАПУСК ==========
if __name__ == "__main__":
    print("✅ Чат-бот Губаты с рассылкой и списком пользователей запущен!")
    print(f"👥 Текущих пользователей: {len(get_all_users())}")
    print("📋 /users — количество")
    print("📋 /users_list — список с именами и ID")
    print("📢 /broadcast текст — рассылка")
    print("🎮 /67 — пасхалка")
    
    while True:
        try:
            bot.infinity_polling(timeout=60)
        except Exception as e:
            print(f"Ошибка: {e}")
            time.sleep(5)
