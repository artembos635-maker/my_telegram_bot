import telebot
from telebot import types
import json
import os
import time
from datetime import datetime, timedelta
import re

TOKEN = '8786806064:AAGnZbQeNQCow4txVsS_O_-BQkDLkARk6RU'
ADMINS = [7717477509, 1334363706]
GROUP_ID = -1003514715489

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

# ========== КНОПКА ==========
def start_keyboard():
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(text="🌍 Официальный сайт NSP", url="https://naturessunshine.ru/"))
    return markup

# ========== ОТПРАВКА В ГРУППУ ==========
def send_to_group(user_id, user_name, username, text=None, photo=None, caption_text=None):
    try:
        header = f"📩 **Сообщение от пользователя**\n👤 {user_name} (@{username if username else 'нет username'})\n🆔 `{user_id}`"
        
        if photo:
            # Фото с подписью или без
            final_caption = header
            if caption_text:
                final_caption += f"\n\n📝 {caption_text}"
            bot.send_photo(GROUP_ID, photo, caption=final_caption, parse_mode="Markdown")
        elif text:
            bot.send_message(GROUP_ID, header, parse_mode="Markdown")
            bot.send_message(GROUP_ID, text)
    except Exception as e:
        print(f"Ошибка отправки: {e}")

# ========== ОТВЕТ ПОЛЬЗОВАТЕЛЮ ==========
@bot.message_handler(func=lambda m: m.chat.id == GROUP_ID and m.reply_to_message)
def answer_from_group(message):
    if not is_admin(message.from_user.id):
        bot.send_message(GROUP_ID, "❌ Ты не админ")
        return
    try:
        original = message.reply_to_message
        if not original:
            return
        match = re.search(r"🆔 `(\d+)`", original.text if original.text else str(original.caption or ""))
        if not match:
            bot.send_message(GROUP_ID, "❌ Не найден ID пользователя")
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
        f"Привет, {message.from_user.first_name}! 👋\n\nНажми на кнопку, чтобы перейти на официальный сайт NSP.\n\n"
        f"**Как отправить сообщение модераторам:**\n"
        f"• Текст: `/otp твой текст`\n"
        f"• Фото: отправь фото с подписью `/otp`\n"
        f"• Фото с текстом: отправь фото с подписью `/otp твой текст`",
        reply_markup=start_keyboard(),
        parse_mode="Markdown"
    )

@bot.message_handler(commands=['otp', 'Otp', 'OTP'])
def otp_text(message):
    user_id = message.chat.id
    user_name = message.from_user.first_name
    username = message.from_user.username
    add_user(user_id, user_name, username)
    
    text = message.text.replace('/otp', '', 1).replace('/Otp', '', 1).replace('/OTP', '', 1).strip()
    if text:
        send_to_group(user_id, user_name, username, text=text)
    else:
        bot.send_message(user_id, "❌ Напиши текст после команды /otp\nПример: `/otp Здравствуйте!`", parse_mode="Markdown")

@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    user_id = message.chat.id
    user_name = message.from_user.first_name
    username = message.from_user.username
    add_user(user_id, user_name, username)
    
    caption = message.caption or ""
    
    # Проверяем, есть ли команда /otp в подписи
    if caption.lower().startswith('/otp'):
        # Убираем /otp из подписи
        clean_caption = re.sub(r'^/otp\s*', '', caption, flags=re.IGNORECASE).strip()
        send_to_group(user_id, user_name, username, photo=message.photo[-1].file_id, caption_text=clean_caption if clean_caption else None)
    else:
        # Если нет команды /otp — просто сохраняем пользователя, но не пересылаем
        pass

# ========== АВТОМАТИЧЕСКАЯ ПЕРЕСЫЛКА ГОЛОСОВЫХ ==========
@bot.message_handler(content_types=['voice'])
def handle_voice(message):
    user_id = message.chat.id
    user_name = message.from_user.first_name
    username = message.from_user.username
    add_user(user_id, user_name, username)
    
    header = f"📩 **Голосовое сообщение от пользователя**\n👤 {user_name} (@{username if username else 'нет username'})\n🆔 `{user_id}`"
    try:
        bot.send_voice(GROUP_ID, message.voice.file_id, caption=header, parse_mode="Markdown")
    except Exception as e:
        print(f"Ошибка пересылки голосового: {e}")

# ========== СОХРАНЕНИЕ ПОЛЬЗОВАТЕЛЕЙ ==========
@bot.message_handler(func=lambda m: True)
def save_user_handler(message):
    add_user(message.chat.id, message.from_user.first_name, message.from_user.username)

# ========== ЗАПУСК ==========
if __name__ == "__main__":
    print("✅ Бот запущен. /otp — текст или фото с подписью /otp")
    print(f"Админы: {ADMINS}")
    print(f"ID группы: {GROUP_ID}")
    while True:
        try:
            bot.infinity_polling(timeout=60)
        except:
            time.sleep(5)
