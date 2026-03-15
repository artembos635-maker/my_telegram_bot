import telebot
from telebot import types
import requests
from datetime import datetime
import time
import random

# ========== ТОКЕНЫ ==========
TOKEN = '8749955457:AAFrM_9bMzQoT6ibN97Kx5SHHWTKHrS0QRc'
OPENWEATHER_API_KEY = 'a64845541efe8c1134b338c2c82522ca'

bot = telebot.TeleBot(TOKEN)

# Хранилище: кто сейчас в режиме игры
game_mode = {}

# ========== ВАРИАНТЫ ОТВЕТОВ ДЛЯ ИГРЫ (только Да/Нет) ==========
# (не используются, но оставим на будущее)

# ========== ФУНКЦИЯ ПОГОДЫ ==========
def get_weather(city):
    try:
        url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={OPENWEATHER_API_KEY}&units=metric&lang=ru"
        response = requests.get(url, timeout=10)
        data = response.json()
        
        if data.get('cod') != 200:
            return f"❌ Город '{city}' не найден"
        
        city_name = data['name']
        country = data['sys']['country']
        temp = data['main']['temp']
        feels_like = data['main']['feels_like']
        humidity = data['main']['humidity']
        pressure = data['main']['pressure']
        wind_speed = data['wind']['speed']
        weather_desc = data['weather'][0]['description'].capitalize()
        
        weather_text = f"🌍 **Погода в {city_name}, {country}**\n\n"
        weather_text += f"🌡 **Температура:** {temp:.1f}°C\n"
        weather_text += f"🤔 **Ощущается:** {feels_like:.1f}°C\n"
        weather_text += f"☁️ **{weather_desc}**\n"
        weather_text += f"💧 **Влажность:** {humidity}%\n"
        weather_text += f"🌀 **Ветер:** {wind_speed} м/с\n"
        weather_text += f"📊 **Давление:** {pressure} гПа\n"
        
        return weather_text
    except Exception as e:
        return f"😵 Ошибка получения погоды: {str(e)}"

# ========== ФУНКЦИЯ КУРСОВ ==========
def get_currency_rates():
    try:
        url = "https://api.nbrb.by/exrates/rates?periodicity=0"
        response = requests.get(url, timeout=10)
        data = response.json()
        
        text = "🇧🇾 **Курсы НБРБ**\n"
        text += f"📅 {datetime.now().strftime('%d.%m.%Y')}\n\n"
        
        # Словарь валют с флагами (ISO код -> флаг)
        currencies = {
            'USD': '🇺🇸 Доллар США',
            'EUR': '🇪🇺 Евро',
            'RUB': '🇷🇺 Российский рубль',
            'PLN': '🇵🇱 Польский злотый',
            'UAH': '🇺🇦 Украинская гривна',
            'CNY': '🇨🇳 Китайский юань',
            'GBP': '🇬🇧 Фунт стерлингов',
            'JPY': '🇯🇵 Японская иена',
            'CHF': '🇨🇭 Швейцарский франк',
            'CAD': '🇨🇦 Канадский доллар',
            'AUD': '🇦🇺 Австралийский доллар',
            'ARS': '🇦🇷 Аргентинское песо',
            'BRL': '🇧🇷 Бразильский реал',
            'MXN': '🇲🇽 Мексиканское песо',
            'TRY': '🇹🇷 Турецкая лира',
            'INR': '🇮🇳 Индийская рупия',
            'KRW': '🇰🇷 Южнокорейская вона',
            'ZAR': '🇿🇦 Южноафриканский рэнд'
        }
        
        found = False
        for currency in data:
            code = currency['Cur_Abbreviation']
            if code in currencies:
                found = True
                name = currencies[code]
                rate = currency['Cur_OfficialRate']
                scale = currency['Cur_Scale']
                text += f"{name}: {scale} = {rate:.4f} BYN\n"
        
        if not found:
            text += "😕 Валюты не найдены"
        
        return text
    except Exception as e:
        return f"😕 Не удалось получить курсы: {str(e)}"

# ========== КНОПКИ ==========
def main_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(
        types.KeyboardButton("💰 Курсы валют"),
        types.KeyboardButton("🌤 Погода"),
        types.KeyboardButton("🎮 Губаты"),
        types.KeyboardButton("👋 Дарово"),
        types.KeyboardButton("😢 пока"),
        types.KeyboardButton("🤔 Как делишки?")
    )
    return markup

# ========== СТАРТ ==========
@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.chat.id
    game_mode[user_id] = False  # Сбрасываем режим игры
    
    bot.send_message(
        message.chat.id,
        f"Привет, {message.from_user.first_name}! 👋\n\n"
        f"🇧🇾 **Курсы валют НБРБ** с флагами стран!\n"
        f"🌤 Погода в любом городе\n"
        f"🎮 Губаты — задай вопрос и получи Да/Нет\n\n"
        f"Нажимай кнопки внизу!",
        reply_markup=main_keyboard(),
        parse_mode="Markdown"
    )

# ========== ОБРАБОТКА КНОПОК ==========
@bot.message_handler(func=lambda message: True)
def handle_text(message):
    user_id = message.chat.id
    text = message.text
    
    # Если пользователь в режиме игры — отвечаем Да/Нет
    if game_mode.get(user_id, False):
        # Случайный ответ: только Да или Нет
        answer = "Да ✅" if random.choice([True, False]) else "Нет ❌"
        bot.send_message(user_id, answer)
        game_mode[user_id] = False  # Выключаем режим игры
        return
    
    # Обычные кнопки
    if text == "💰 Курсы валют":
        bot.send_chat_action(user_id, 'typing')
        rates = get_currency_rates()
        bot.send_message(user_id, rates, parse_mode="Markdown")
        
    elif text == "🌤 Погода":
        bot.send_message(
            user_id,
            "🌍 **Введи название города:**",
            parse_mode="Markdown"
        )
        bot.register_next_step_handler(message, process_weather)
        
    elif text == "🎮 Губаты":
        # Включаем режим игры
        game_mode[user_id] = True
        bot.send_message(
            user_id,
            "Задай шуточный вопрос:"
        )
        
    elif text == "👋 Дарово":
        bot.send_message(user_id, "Дарово! 😊")
        
    elif text == "😢 пока":
        bot.send_message(user_id, "Пока! 👋")
        
    elif text == "🤔 Как делишки?":
        markup = types.InlineKeyboardMarkup()
        markup.add(
            types.InlineKeyboardButton("✅ Отлично", callback_data="good"),
            types.InlineKeyboardButton("❌ Не очень", callback_data="bad")
        )
        bot.send_message(
            user_id,
            "У меня всё хорошо! А у тебя?",
            reply_markup=markup
        )
        
    else:
        bot.send_message(
            user_id,
            "Используй кнопки внизу экрана"
        )

# ========== ОБРАБОТКА ВВОДА ГОРОДА ==========
def process_weather(message):
    city = message.text.strip()
    bot.send_chat_action(message.chat.id, 'typing')
    weather = get_weather(city)
    bot.send_message(message.chat.id, weather, parse_mode="Markdown")

# ========== INLINE КНОПКИ ==========
@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    if call.data == "good":
        bot.send_message(call.message.chat.id, "😊 Отлично! Рад за тебя!")
    elif call.data == "bad":
        bot.send_message(call.message.chat.id, "😔 Не расстраивайся! Всё наладится!")
    bot.answer_callback_query(call.id)

# ========== ЗАПУСК ==========
if __name__ == "__main__":
    print("✅ Бот с флагами валют и игрой 'Губаты' запущен...")
    print("🇧🇾 Курсы НБРБ с флагами стран")
    print("🎮 Губаты: кнопка → вопрос → Да/Нет")
    
    while True:
        try:
            bot.infinity_polling(timeout=60, long_polling_timeout=60)
        except Exception as e:
            print(f"Ошибка: {e}")
            time.sleep(5)
