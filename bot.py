import telebot
from telebot import types
import json
import os
import time
from datetime import datetime, timedelta

TOKEN = '8786806064:AAGnZbQeNQCow4txVsS_O_-BQkDLkARk6RU'
ADMINS = [7717477509, 1334363706]
GROUP_ID = -1003514715489  # ТВОЙ ID ГРУППЫ

bot = telebot.TeleBot(TOKEN)
USERS_FILE = 'users.json'

# ========== ПОЛЬЗОВАТЕЛИ ==========
def get_users():
    try:
        if not os.path.exists(USERS_FILE):
            with open(USERS_FILE, 'w', encoding='utf-8') as f:
                json.dump([], f)
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
    
    return (f"📊 Статистика\n\n👥 Всего: {total}\n\n📈 Новые:\n   • За сегодня: {new_today}\n   • За неделю: {new_week}\n   • За месяц: {new_month}\n\n🔥 Активные за неделю: {active_week}")

# ========== КНОПКА ==========
def start_keyboard():
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(text="🌍 Официальный сайт NSP", url="https://naturessunshine.ru/"))
    return markup

# ========== ПЕРЕСЫЛКА В ГРУППУ ==========
def forward_to_group(message, user_id):
    try:
        user = message.from_user
        caption = f"📩 **Сообщение от пользователя**\n👤 {user.first_name} (@{user.username if user.username else 'нет username'})\n🆔 `{user_id}`"
        
        if message.text:
            bot.send_message(GROUP_ID, caption, parse_mode="Markdown")
            bot.send_message(GROUP_ID, message.text)
        elif message.photo:
            bot.send_photo(GROUP_ID, message.photo[-1].file_id, caption=caption, parse_mode="Markdown")
        elif message.video:
            bot.send_video(GROUP_ID, message.video.file_id, caption=caption, parse_mode="Markdown")
        elif message.document:
            bot.send_document(GROUP_ID, message.document.file_id, caption=caption, parse_mode="Markdown")
        elif message.voice:
            bot.send_voice(GROUP_ID, message.voice.file_id, caption=caption, parse_mode="Markdown")
    except Exception as e:
        print(f"Ошибка пересылки: {e}")

# ========== ОТВЕТ ПОЛЬЗОВАТЕЛЮ ИЗ ГРУППЫ ==========
@bot.message_handler(func=lambda m: m.chat.id == GROUP_ID and m.reply_to_message)
def answer_from_group(message):
    if not is_admin(message.from_user.id):
        bot.send_message(GROUP_ID, "❌ Ты не админ")
        return
    try:
        original = message.reply_to_message
        if not original:
            return
        
        import re
        match = re.search(r"🆔 `(\d+)`", original.text if original.text else str(original.caption or ""))
        if not match:
            bot.send_message(GROUP_ID, "❌ Не найден ID пользователя в исходном сообщении")
            return
        
        user_id = int(match.group(1))
        bot.send_message(user_id, f"🛡️ **Ответ от модератора:**\n\n{message.text}")
        bot.send_message(GROUP_ID, f"✅ Ответ отправлен пользователю")
    except Exception as e:
        bot.send_message(GROUP_ID, f"❌ Ошибка: {e}")

# ========== КОМАНДЫ ==========
@bot.message_handler(commands=['start'])
def start(message):
    add_user(message.chat.id, message.from_user.first_name, message.from_user.username)
    bot.send_message(
        message.chat.id,
        f"Привет, {message.from_user.first_name}! 👋\n\nНажми на кнопку, чтобы перейти на официальный сайт NSP.",
        reply_markup=start_keyboard()
    )

@bot.message_handler(commands=['stats'])
def stats_command(message):
    if not is_admin(message.from_user.id):
        return
    bot.send_message(message.chat.id, get_stats())

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
    broadcast_text = f"🛡️ Сообщение от модератора:\n\n{text}"
    bot.send_message(message.chat.id, f"📢 Рассылка {len(users)} пользователям...")
    ok = fail = 0
    for u in users:
        try:
            bot.send_message(u['id'], broadcast_text)
            ok += 1
            time.sleep(0.05)
        except:
            fail += 1
    bot.send_message(message.chat.id, f"✅ Отправлено: {ok}\n❌ Не доставлено: {fail}")

# ========== СОХРАНЕНИЕ И ПЕРЕСЫЛКА ==========
@bot.message_handler(func=lambda m: True)
def save_and_forward(message):
    user_id = message.chat.id
    add_user(user_id, message.from_user.first_name, message.from_user.username)
    forward_to_group(message, user_id)

# ========== ЗАПУСК ==========
if __name__ == "__main__":
    print("✅ Бот запущен. Все сообщения пересылаются в группу.")
    print(f"Админы: {ADMINS}")
    print(f"ID группы: {GROUP_ID}")
    print(f"Пользователей: {len(get_users())}")
    while True:
        try:
            bot.infinity_polling(timeout=60)
        except:
            time.sleep(5)
