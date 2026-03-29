import telebot
import json
import os
import time
from datetime import datetime, timedelta

TOKEN = '8786806064:AAGnZbQeNQCow4txVsS_O_-BQkDLkARk6RU'
ADMIN_ID = 7717477509

bot = telebot.TeleBot(TOKEN)
USERS_FILE = 'users.json'

# ========== РАБОТА С ФАЙЛОМ (НЕ ПЕРЕЗАПИСЫВАЕТ ПРИ ОБНОВЛЕНИИ) ==========
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
    print(f"✅ Новый пользователь: {name} (ID: {user_id})")
    return True

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

# ========== КОМАНДЫ ==========
@bot.message_handler(commands=['start'])
def start(message):
    add_user(message.chat.id, message.from_user.first_name, message.from_user.username)
    bot.send_message(message.chat.id, f"Привет, {message.from_user.first_name}! 👋\n\nНажми на кнопку, чтобы перейти в каталог.", reply_markup=start_keyboard())

def start_keyboard():
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(telebot.types.InlineKeyboardButton(text="🌿 БАДы", url="https://nspgoods.by/bady/"))
    return markup

@bot.message_handler(commands=['stats'])
def stats_command(message):
    if message.from_user.id != ADMIN_ID:
        return
    bot.send_message(message.chat.id, get_stats(), parse_mode="Markdown")

@bot.message_handler(commands=['users'])
def users_count(message):
    if message.from_user.id != ADMIN_ID:
        return
    users = get_users()
    bot.send_message(message.chat.id, f"👥 Всего: {len(users)}")

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
        return
    text = message.text.replace('/broadcast', '', 1).strip()
    if not text:
        bot.send_message(message.chat.id, "❌ Введите текст")
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

# ========== СОХРАНЯЕМ ВСЕХ, КТО ПИШЕТ ==========
@bot.message_handler(func=lambda m: True)
def save_all(m):
    add_user(m.chat.id, m.from_user.first_name, m.from_user.username)

# ========== ЗАПУСК ==========
if __name__ == "__main__":
    print("✅ Бот запущен")
    print(f"Админ: {ADMIN_ID}")
    print(f"Пользователей в базе: {len(get_users())}")
    while True:
        try:
            bot.infinity_polling(timeout=60)
        except:
            time.sleep(5)
