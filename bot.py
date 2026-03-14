import telebot
from telebot import types
import requests
from datetime import datetime
import time

# Токен
TOKEN = '8749955457:AAFrM_9bMzQoT6ibN97Kx5SHHWTKHrS0QRc'
bot = telebot.TeleBot(TOKEN)

# Функция курсов
def get_rates():
    try:
        url = "https://api.nbrb.by/exrates/rates?periodicity=0"
        r = requests.get(url)
        data = r.json()
        
        # Словарь с нужными валютами
        result = "🇧🇾 **Курсы НБРБ**\n"
        result += f"📅 {datetime.now().strftime('%d.%m.%Y')}\n\n"
        
        for curr in data:
            if curr['Cur_Abbreviation'] in ['USD', 'EUR', 'RUB', 'PLN', 'UAH', 'CNY']:
                name = curr['Cur_Abbreviation']
                rate = curr['Cur_OfficialRate']
                scale = curr['Cur_Scale']
                result += f"{scale} {name} = {rate} BYN\n"
        
        return result
    except:
        return "😕 Ошибка получения курсов"

# Кнопки
def main_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("💰 Курсы валют")
    btn2 = types.KeyboardButton("👋 Дарово")
    btn3 = types.KeyboardButton("😢 пока")
    btn4 = types.KeyboardButton("🤔 Как делишки?")
    markup.add(btn1, btn2, btn3, btn4)
    return markup

# Старт
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(
        message.chat.id,
        f"Привет, {message.from_user.first_name}!",
        reply_markup=main_keyboard()
    )

# Текст
@bot.message_handler(func=lambda m: True)
def handle_text(message):
    text = message.text
    
    if text == "💰 Курсы валют":
        rates = get_rates()
        bot.send_message(message.chat.id, rates, parse_mode="Markdown")
        
    elif text == "👋 Дарово":
        bot.send_message(message.chat.id, "Дарово! 😊")
        
    elif text == "😢 пока":
        bot.send_message(message.chat.id, "Пока! 👋")
        
    elif text == "🤔 Как делишки?":
        markup = types.InlineKeyboardMarkup()
        markup.add(
            types.InlineKeyboardButton("✅ Отлично", callback_data="good"),
            types.InlineKeyboardButton("❌ Не очень", callback_data="bad")
        )
        bot.send_message(message.chat.id, "У меня всё хорошо! А у тебя?", reply_markup=markup)
        
    else:
        bot.send_message(message.chat.id, "Используй кнопки внизу!")

# Кнопки inline
@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    if call.data == "good":
        bot.send_message(call.message.chat.id, "😊 Отлично!")
    elif call.data == "bad":
        bot.send_message(call.message.chat.id, "😔 Всё наладится!")
    bot.answer_callback_query(call.id)

# Запуск
print("✅ Бот запущен")
bot.infinity_polling()
