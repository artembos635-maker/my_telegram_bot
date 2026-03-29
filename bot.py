import telebot
from telebot import types
import json
import os
import time
from datetime import datetime, timedelta

TOKEN = '8786806064:AAGnZbQeNQCow4txVsS_O_-BQkDLkARk6RU'
ADMINS = [7717477509, 1334363706]

bot = telebot.TeleBot(TOKEN)
USERS_FILE = 'users.json'

# ========== РАБОТА С ФАЙЛОМ (НЕ ТРОГАЕТСЯ ПРИ ОБНОВЛЕНИИ) ==========
def get_users():
    try:
        if not os.path.exists(USERS_FILE):
            with open(USERS_FILE, 'w', encoding='utf-8') as f:
                json.dump([], f, ensure_ascii=False, indent=2)
            return []
        with open(USERS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Ошибка чтения: {e}")
        return []

def save_users(users):
    try:
        with open(USERS_FILE, 'w', encoding='utf-8') as f:
            json.dump(users, f, ensure_ascii=False, indent=2)
        print(f"✅ Сохранено {len(users)} пользователей")
    except Exception as e:
        print(f"Ошибка сохранения: {e}")

def add_user(user_id, name, username):
    users = get_users()
    for u in users:
        if u.get('id') == user_id:
            u['last_active'] = datetime.now().isoformat()
            save_users(users)
            return False
    users.append({
        'id': user_id,
        'name': name,
        'username': username or 'нет username',
        'joined': datetime.now().isoformat(),
        'last_active': datetime.now().isoformat()
    })
    save_users(users)
    print(f"✅ Новый пользователь: {name} (ID: {user_id})")
    return True

def is_admin(user_id):
    return user_id in ADMINS

# ========== СТАТИСТИКА ==========
def get_stats():
    users = get_users()
    total = len(users)
    now = datetime.now()
    today_start = datetime(now.year, now.month, now.day)
    week_ago = now - timedelta(days=7)
    month_ago = now - timedelta(days=30)
    
    new_today = new_week = new_month = active_week = 0
    for u in users:
        joined = datetime.fromisoformat(u.get('joined', '2000-01-01'))
        last_active = datetime.fromisoformat(u.get('last_active', '2000-01-01'))
        if joined >= today_start: new_today += 1
        if joined >= week_ago: new_week += 1
        if joined >= month_ago: new_month += 1
        if last_active >= week_ago: active_week += 1
    
    return (f"📊 **Статистика**\n\n👥 Всего: {total}\n\n📈 Новые:\n   • За сегодня: {new_today}\n   • За неделю: {new_week}\n   • За месяц: {new_month}\n\n🔥 Активные за неделю: {active_week}")

# ========== КНОПКА ==========
def start_keyboard():
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(text="🌿 БАДы", url="https://nspgoods.by/bady/"))
    return markup

# ========== ПЕРЕМЕННЫЕ ДЛЯ РАССЫЛКИ ФОТО ==========
broadcast_photo = None
broadcast_caption = None

# ========== КОМАНДЫ ==========
@bot.message_handler(commands=['start'])
def start(message):
    add_user(message.chat.id, message.from_user.first_name, message.from_user.username)
    bot.send_message(
        message.chat.id,
        f"Привет, {message.from_user.first_name}! 👋\n\nНажми на кнопку, чтобы перейти в каталог.",
        reply_markup=start_keyboard()
    )

@bot.message_handler(commands=['stats'])
def stats_command(message):
    if not is_admin(message.from_user.id):
        return
    bot.send_message(message.chat.id, get_stats(), parse_mode="Markdown")

@bot.message_handler(commands=['users'])
def users_count(message):
    if not is_admin(message.from_user.id):
        return
    users = get_users()
    bot.send_message(message.chat.id, f"👥 Всего пользователей: {len(users)}")

@bot.message_handler(commands=['users_list'])
def users_list(message):
    if not is_admin(message.from_user.id):
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
    if not is_admin(message.from_user.id):
        return
    text = message.text.replace('/broadcast', '', 1).strip()
    if not text:
        bot.send_message(message.chat.id, "❌ Введите текст\nПример: /broadcast Всем привет!")
        return
    users = get_users()
    if not users:
        bot.send_message(message.chat.id, "📭 Нет пользователей")
        return
    broadcast_text = f"🛡️ **Сообщение от модератора:**\n\n{text}"
    bot.send_message(message.chat.id, f"📢 Рассылка {len(users)} пользователям...")
    ok = fail = 0
    for u in users:
        try:
            bot.send_message(u['id'], broadcast_text, parse_mode="Markdown")
            ok += 1
            time.sleep(0.05)
        except:
            fail += 1
    bot.send_message(message.chat.id, f"✅ Отправлено: {ok}\n❌ Не доставлено: {fail}")

# ========== РАССЫЛКА ФОТО ==========
@bot.message_handler(commands=['send_photo'])
def send_photo_start(message):
    if not is_admin(message.from_user.id):
        bot.send_message(message.chat.id, "❌ Нет прав")
        return
    
    users = get_users()
    if not users:
        bot.send_message(message.chat.id, "📭 Нет пользователей в базе! Сначала нажми /start")
        return
    
    bot.send_message(message.chat.id, f"👥 В базе {len(users)} пользователей. Отправь фото для рассылки.")
    bot.register_next_step_handler(message, get_photo_for_broadcast)

def get_photo_for_broadcast(message):
    global broadcast_photo, broadcast_caption
    if message.photo:
        broadcast_photo = message.photo[-1].file_id
        bot.send_message(message.chat.id, "✍️ Теперь отправь текст к фото (или нажми /skip чтобы без текста).")
        bot.register_next_step_handler(message, get_caption_for_broadcast)
    else:
        bot.send_message(message.chat.id, "❌ Это не фото. Попробуй ещё раз /send_photo")

def get_caption_for_broadcast(message):
    global broadcast_photo, broadcast_caption
    if message.text == "/skip":
        broadcast_caption = None
    else:
        broadcast_caption = f"🛡️ **Сообщение от модератора:**\n\n{message.text}"
    
    users = get_users()
    if not users:
        bot.send_message(message.chat.id, "📭 Нет пользователей")
        broadcast_photo = None
        broadcast_caption = None
        return
    
    bot.send_message(message.chat.id, f"📢 Рассылка фото {len(users)} пользователям...")
    
    ok = fail = 0
    for u in users:
        try:
            bot.send_photo(u['id'], broadcast_photo, caption=broadcast_caption, parse_mode="Markdown")
            ok += 1
            time.sleep(0.05)
        except:
            fail += 1
    
    bot.send_message(message.chat.id, f"✅ Отправлено: {ok}\n❌ Не доставлено: {fail}")
    broadcast_photo = None
    broadcast_caption = None

# ========== СОХРАНЕНИЕ ВСЕХ, КТО ПИШЕТ ==========
@bot.message_handler(func=lambda m: True)
def save_all(m):
    add_user(m.chat.id, m.from_user.first_name, m.from_user.username)

# ========== ЗАПУСК ==========
if __name__ == "__main__":
    print("✅ Бот Badiworldbot запущен")
    print(f"Админы: {ADMINS}")
    print(f"Пользователей в базе: {len(get_users())}")
    while True:
        try:
            bot.infinity_polling(timeout=60)
        except Exception as e:
            print(f"Ошибка: {e}")
            time.sleep(5)
