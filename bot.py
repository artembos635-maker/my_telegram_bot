import telebot
from telebot import types
import requests
from datetime import datetime
import os

# Твой токен из переменных окружения (Railway)
TOKEN = os.environ.get('TOKEN')

bot = telebot.TeleBot(TOKEN)

# ========== ФУНКЦИЯ ДЛЯ ПОЛУЧЕНИЯ КУРСОВ НБРБ ==========
def get_belarus_rates():
    """
    Получает курсы валют с сайта Нацбанка Беларуси
    """
    try:
        # API Национального банка РБ (официальное, бесплатное)
        url = "https://api.nbrb.by/exrates/rates?periodicity=0"
        
        response = requests.get(url, timeout=10)
        data = response.json()
        
        # Создаем словарь с нужными валютами
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
    except Exception as e:
        print(f"Ошибка при получении курсов: {e}")
        return None

# ========== КОМАНДА /start ==========
@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_name = message.from_user.first_name
    
    # Создаём клавиатуру с кнопками
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    
    btn1 = types.KeyboardButton("👋 Дарово")
    btn2 = types.KeyboardButton("😢 пока")
    btn3 = types.KeyboardButton("🤔 Как делишки?")
    btn4 = types.KeyboardButton("💰 Курсы валют (Беларусь)")
    
    markup.add(btn1, btn2, btn3, btn4)
    
    bot.send_message(
        message.chat.id, 
        f"Привет, {user_name}! 👋\nЯ ИИ созданный Артёмом Рызвановичем\n\n"
        f"🇧🇾 Я показываю официальные курсы Нацбанка Беларуси!", 
        reply_markup=markup
    )

# ========== КОМАНДА /help ==========
@bot.message_handler(commands=['help'])
def send_help(message):
    bot.send_message(
        message.chat.id,
        "🇧🇾 **Бот курсов валют НБРБ**\n\n"
        "Команды:\n"
        "/start - запуск\n"
        "/help - помощь\n"
        "/rates - курсы всех валют\n\n"
        "Или просто жми кнопки внизу!",
        parse_mode="Markdown"
    )

# ========== КОМАНДА /rates ==========
@bot.message_handler(commands=['rates'])
def show_rates_command(message):
    show_rates(message)

# ========== ФУНКЦИЯ ПОКАЗА КУРСОВ ==========
def show_rates(message):
    rates = get_belarus_rates()
    
    if not rates:
        bot.send_message(
            message.chat.id,
            "😕 Не удалось получить курсы. Иди читай Губаты."
        )
        return
    
    # Формируем сообщение с курсами
    text = "🇧🇾 **Официальные курсы НБРБ**\n"
    text += f"📅 {datetime.now().strftime('%d.%m.%Y')}\n\n"
    
    # USD
    if 'USD' in rates:
        text += f"💵 **{rates['USD']['name']}**\n"
        text += f"{rates['USD']['scale']} USD = {rates['USD']['rate']:.4f} BYN\n\n"
    
    # EUR
    if 'EUR' in rates:
        text += f"💶 **{rates['EUR']['name']}**\n"
        text += f"{rates['EUR']['scale']} EUR = {rates['EUR']['rate']:.4f} BYN\n\n"
    
    # RUB (особое внимание - российский рубль)
    if 'RUB' in rates:
        text += f"🇷🇺 **{rates['RUB']['name']}**\n"
        text += f"{rates['RUB']['scale']} RUB = {rates['RUB']['rate']:.4f} BYN\n\n"
    
    # PLN (польский злотый - актуально для Беларуси)
    if 'PLN' in rates:
        text += f"🇵🇱 **{rates['PLN']['name']}**\n"
        text += f"{rates['PLN']['scale']} PLN = {rates['PLN']['rate']:.4f} BYN\n\n"
    
    # UAH
    if 'UAH' in rates:
        text += f"🇺🇦 **{rates['UAH']['name']}**\n"
        text += f"{rates['UAH']['scale']} UAH = {rates['UAH']['rate']:.4f} BYN\n\n"
    
    # CNY
    if 'CNY' in rates:
        text += f"🇨🇳 **{rates['CNY']['name']}**\n"
        text += f"{rates['CNY']['scale']} CNY = {rates['CNY']['rate']:.4f} BYN"
    
    bot.send_message(message.chat.id, text, parse_mode="Markdown")

# ========== ОБРАБОТКА ТЕКСТОВЫХ СООБЩЕНИЙ ==========
@bot.message_handler(func=lambda message: True)
def handle_text(message):
    text = message.text
    
    if text == "👋 Дарово":                          # Исправлено!
        bot.send_message(message.chat.id, "Дарово! Рад тебя видеть! 😊")
        
    elif text == "😢 пока":                           # Исправлено!
        bot.send_message(message.chat.id, "Пока! Заходи ещё! 👋")
        
    elif text == "🤔 Как делишки?":                   # Исправлено!
        markup = types.InlineKeyboardMarkup(row_width=2)
        btn_yes = types.InlineKeyboardButton("✅ Отлично!", callback_data="good")
        btn_no = types.InlineKeyboardButton("❌ Не очень", callback_data="bad")
        markup.add(btn_yes, btn_no)
        
        bot.send_message(
            message.chat.id, 
            "У меня всё хорошо! А у тебя?", 
            reply_markup=markup
        )
        
    elif text == "💰 Курсы валют (Беларусь)":
        show_rates(message)
        
    else:
        bot.send_message(
            message.chat.id, 
            f"Ты написал: {text}\n\nИспользуй кнопки внизу экрана или команды:\n/start\n/help\n/rates"
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
    
    bot.answer_callback_query(call.id)

# ========== ЗАПУСК ==========
print("🇧🇾 Бот с курсами НБРБ запущен...")
bot.infinity_polling()

  
