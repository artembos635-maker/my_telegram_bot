import telebot
from telebot import types

# Твой токен (не забудь вставить!)
TOKEN = "8749955457:AAFrM_9bMzQoT6ibN97Kx5SHHWTKHrS0QRc"

bot = telebot.TeleBot(TOKEN)

# ========== КОМАНДА /start ==========
@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_name = message.from_user.first_name
    
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    
    btn1 = types.KeyboardButton("👋 Привет")
    btn2 = types.KeyboardButton("😢 Пока")
    btn3 = types.KeyboardButton("🤔 Как дела?")
    btn4 = types.KeyboardButton("💰 Курс валют")
    
    markup.add(btn1, btn2, btn3, btn4)
    
    bot.send_message(
        message.chat.id, 
        f"Привет, {user_name}! 👋\nЯ ИИ созданный Артёмом Рызвановичем", 
        reply_markup=markup
    )

# ========== КОМАНДА /help ==========
@bot.message_handler(commands=['help'])
def send_help(message):
    bot.send_message(
        message.chat.id,
        "Я бот с кнопками. Просто нажимай на кнопки внизу экрана!"
    )

# ========== ОБРАБОТКА ТЕКСТОВЫХ СООБЩЕНИЙ ==========
@bot.message_handler(func=lambda message: True)
def handle_text(message):
    text = message.text
    
    if text == "👋 Привет":
        bot.send_message(message.chat.id, "Привет! Рад тебя видеть! 😊")
        
    elif text == "😢 Пока":
        bot.send_message(message.chat.id, "Пока! Заходи ещё! 👋")
        
    elif text == "🤔 Как дела?":
        markup = types.InlineKeyboardMarkup(row_width=2)
        
        btn_yes = types.InlineKeyboardButton("✅ Отлично!", callback_data="good")
        btn_no = types.InlineKeyboardButton("❌ Не очень", callback_data="bad")
        
        markup.add(btn_yes, btn_no)
        
        bot.send_message(
            message.chat.id, 
            "У меня всё хорошо! А у тебя?", 
            reply_markup=markup
        )
        
    elif text == "💰 Курс валют":
        markup = types.InlineKeyboardMarkup(row_width=2)
        
        btn_usd = types.InlineKeyboardButton("💵 Доллар (USD)", callback_data="usd")
        btn_eur = types.InlineKeyboardButton("💶 Евро (EUR)", callback_data="eur")
        
        markup.add(btn_usd, btn_eur)
        
        bot.send_message(
            message.chat.id,
            "Выбери валюту:",
            reply_markup=markup
        )
        
    else:
        bot.send_message(
            message.chat.id, 
            f"Ты написал: {text}\nИспользуй кнопки для общения 😉"
        )

# ========== ОБРАБОТКА НАЖАТИЙ НА КНОПКИ ==========
@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    if call.data == "good":
        bot.send_message(call.message.chat.id, "😊 Отлично! Рад за тебя!")
        
    elif call.data == "bad":
        bot.send_message(
            call.message.chat.id, 
            "😔 Не расстраивайся! Всё наладится!"
        )
    
    elif call.data == "usd":
        bot.send_message(call.message.chat.id, "💵 Курс доллара: 90.50 руб.")
        
    elif call.data == "eur":
        bot.send_message(call.message.chat.id, "💶 Курс евро: 99.80 руб.")
    
    bot.answer_callback_query(call.id)

# ========== ЗАПУСК ==========
print("🚀 Бот с кнопками запущен...")
bot.infinity_polling()
