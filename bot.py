import telebot
import re
import time

TOKEN = '8786806064:AAGnZbQeNQCow4txVsS_O_-BQkDLkARk6RU'
GROUP_ID = -1003514715489

bot = telebot.TeleBot(TOKEN)

# ========== КОМАНДА /otp ДЛЯ ТЕКСТА ==========
@bot.message_handler(commands=['otp', 'Otp', 'OTP'])
def otp_text(message):
    user_id = message.chat.id
    user_name = message.from_user.first_name
    username = message.from_user.username or "нет username"
    
    text = re.sub(r'^/otp\s*', '', message.text, flags=re.IGNORECASE).strip()
    
    if not text:
        bot.send_message(user_id, "❌ Напиши текст после команды /otp\nПример: /otp Здравствуйте!")
        return
    
    header = f"📩 Сообщение от пользователя\n👤 {user_name} (@{username})\n🆔 {user_id}"
    
    try:
        bot.send_message(GROUP_ID, header)
        bot.send_message(GROUP_ID, text)
        bot.send_message(user_id, "✅ Твоё сообщение отправлено модераторам!")
    except Exception as e:
        bot.send_message(user_id, f"❌ Ошибка: {e}")

# ========== ФОТО С ПОДПИСЬЮ /otp ==========
@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    user_id = message.chat.id
    user_name = message.from_user.first_name
    username = message.from_user.username or "нет username"
    
    caption = message.caption or ""
    
    if re.match(r'^/otp\s*', caption, re.IGNORECASE):
        clean_caption = re.sub(r'^/otp\s*', '', caption, flags=re.IGNORECASE).strip()
        header = f"📩 Сообщение от пользователя\n👤 {user_name} (@{username})\n🆔 {user_id}"
        if clean_caption:
            header += f"\n\n📝 {clean_caption}"
        try:
            bot.send_photo(GROUP_ID, message.photo[-1].file_id, caption=header)
            bot.send_message(user_id, "✅ Твоё фото отправлено модераторам!")
        except Exception as e:
            bot.send_message(user_id, f"❌ Ошибка: {e}")

# ========== ОТВЕТ ПОЛЬЗОВАТЕЛЮ ИЗ ГРУППЫ ==========
@bot.message_handler(func=lambda m: m.chat.id == GROUP_ID and m.reply_to_message)
def answer_from_group(message):
    try:
        original = message.reply_to_message
        if not original:
            return
        
        # Ищем ID пользователя в тексте или подписи
        text_to_search = original.text if original.text else (original.caption if original.caption else "")
        match = re.search(r"🆔 (\d+)", text_to_search)
        if not match:
            bot.send_message(GROUP_ID, "❌ Не найден ID пользователя")
            return
        
        user_id = int(match.group(1))
        bot.send_message(user_id, f"🛡️ Ответ от модератора:\n\n{message.text}")
        bot.send_message(GROUP_ID, f"✅ Ответ отправлен пользователю")
    except Exception as e:
        bot.send_message(GROUP_ID, f"❌ Ошибка: {e}")

# ========== ПРИВЕТСТВИЕ ==========
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(
        message.chat.id,
        f"Привет, {message.from_user.first_name}! 👋\n\n"
        f"Чтобы отправить сообщение модераторам, напиши:\n"
        f"/otp твой текст\n\n"
        f"Или отправь фото с подписью /otp"
    )

# ========== ЗАПУСК ==========
if __name__ == "__main__":
    print("✅ Бот запущен")
    print(f"ID группы: {GROUP_ID}")
    while True:
        try:
            bot.infinity_polling(timeout=60)
        except:
            time.sleep(5)
