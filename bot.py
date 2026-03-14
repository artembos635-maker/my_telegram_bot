import telebot
from telebot import types
import requests
from datetime import datetime
import time

# ========== ТОКЕН ПРЯМО ЗДЕСЬ ==========
TOKEN = '8749955457:AAFrM_9bMzQoT6ibN97Kx5SHHWTKHrS0QRc'

# Создаем бота
bot = telebot.TeleBot(TOKEN)

# ========== ФУНКЦИЯ КУРСОВ ВАЛЮТ ==========
def get_belarus_rates():
    """Получает курсы валют с сайта Нацбанка Беларуси"""
    try:
        url = "https://api.nbrb.by/exrates/rates?periodicity=0"
        response = requests.get(url, timeout=10)
        data = response.json()
        
        rates = {}
        currencies = {
            'USD': 'Доллар США',
            'EUR': 'Евро',
            'RUB': 'Российский рубль',
            'PLN': 'Польский злотый',
            'UAH': 'Украинская гривна',
            'CNY': 'Китайский юань'
        }
        
        for currency in data:
            if currency['Cur_Abbreviation'] in currencies:
                rates[currency['Cur_Abbreviation']] = {
                    'name': currencies[currency['Cur_Abbreviation']],
                    'rate': currency['Cur_OfficialRate'],
                    'scale': currency['Cur_Scale']
                }
        return rates
    except:
        return None

# ========== КОМАНДА /start ==========
@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_name = message.from_user.first_name
    
    # Клавиатура
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(
        types.KeyboardButton("👋 Дарово"),
        types.KeyboardButton("😢 пока"),
        types.KeyboardButton("🤔 Как делишки?"),
        types.KeyboardButton("💰 Курсы валют")
    )
    
    bot.send_message(
        message.chat.id,
        f"Привет, {user_name}! 👋\nЯ бот Артёма\n\n"
        f"🇧🇾 Курсы Нацбанка Беларуси\n\n"
        f"Нажимай кнопки внизу!",
        reply_markup=markup
    )

# ========== КОМАНДА /help ==========
@bot.message_handler(commands=['help'])
def send_help(message):
    bot.send_message(
        message.chat.id,
        "🇧🇾 **Бот курсов валют**\n\n"
        "Команды:\n"
        "/start - запуск\n"
        "/help - помощь\n"
        "/rates - курсы валют",
        parse_mode="Markdown"
    )

# ========== КОМАНДА /rates ==========
@bot.message_handler(commands=['rates'])
def show_rates_command(message):
    show_rates(message)

# ========== ПОКАЗ КУРСОВ ==========
def show_rates(message):
    rates = get_belarus_rates()
    
    if not rates:
        bot.send_message(message.chat.id, "😕 Не удалось получить курсы")
        return
    
    text = "🇧🇾 **Курсы НБРБ**\n"
    text += f"📅 {datetime.now().strftime('%d.%m.%Y')}\n\n"
    
    for code, data in rates.items():
        text += f"{data['scale']} {code} = {data['rate']:.4f} BYN\n"
    
    bot.send_message(message.chat.id, text, parse_mode="Markdown")

# ========== ОБРАБОТКА СООБЩЕНИЙ ==========
@bot.message_handler(func=lambda message: True)
def handle_text(message):
    text = message.text
    
    if text == "👋 Дарово":
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
        
    elif text == "💰 Курсы валют":
        show_rates(message)
        
    else:
        bot.send_message(
            message.chat.id,
            "Используй кнопки внизу экрана!"
        )

# ========== КНОПКИ ==========
@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    if call.data == "good":
        bot.send_message(call.message.chat.id, "😊 Отлично!")
    elif call.data == "bad":
        bot.send_message(call.message.chat.id, "😔 Всё наладится!")
    bot.answer_callback_query(call.id)

# ========== ЗАПУСК ==========
if __name__ == "__main__":
    print("✅ Бот с курсами валют запущен...")
    while True:
        try:
            bot.infinity_polling(timeout=60, long_polling_timeout=60)
        except Exception as e:
            print(f"Ошибка: {e}")
            time.sleep(5)
