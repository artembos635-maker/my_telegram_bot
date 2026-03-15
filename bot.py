import telebot
from telebot import types
import requests
from datetime import datetime
import time

# ========== ТОКЕНЫ ПРЯМО В КОДЕ ==========
TOKEN = '8749955457:AAFrM_9bMzQoT6ibN97Kx5SHHWTKHrS0QRc'
OPENWEATHER_API_KEY = 'a64845541efe8c1134b338c2c82522ca'  # ⚠️ ТВОЙ КЛЮЧ ВСТАВЛЕН!

bot = telebot.TeleBot(TOKEN)

# ========== ФУНКЦИЯ ПОЛУЧЕНИЯ ПОГОДЫ ==========
def get_weather(city):
    """
    Получает погоду для указанного города через OpenWeatherMap API
    """
    try:
        # Запрос к API OpenWeatherMap
        url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={OPENWEATHER_API_KEY}&units=metric&lang=ru"
        
        response = requests.get(url, timeout=10)
        data = response.json()
        
        # Проверяем, найден ли город
        if data.get('cod') != 200:
            if data.get('cod') == '404':
                return f"❌ Город '{city}' не найден. Проверь название."
            else:
                return f"❌ Ошибка API: {data.get('message', 'Неизвестная ошибка')}"
        
        # Извлекаем данные о погоде
        city_name = data['name']
        country = data['sys']['country']
        temp = data['main']['temp']
        feels_like = data['main']['feels_like']
        humidity = data['main']['humidity']
        pressure = data['main']['pressure']
        wind_speed = data['wind']['speed']
        weather_desc = data['weather'][0]['description'].capitalize()
        
        # Формируем красивое сообщение
        weather_text = f"🌍 **Погода в {city_name}, {country}**\n\n"
        weather_text += f"🌡 **Температура:** {temp:.1f}°C\n"
        weather_text += f"🤔 **Ощущается как:** {feels_like:.1f}°C\n"
        weather_text += f"☁️ **Описание:** {weather_desc}\n"
        weather_text += f"💧 **Влажность:** {humidity}%\n"
        weather_text += f"🌀 **Ветер:** {wind_speed} м/с\n"
        weather_text += f"📊 **Давление:** {pressure} гПа\n"
        
        return weather_text
        
    except requests.exceptions.ConnectionError:
        return "🔌 Ошибка подключения. Проверь интернет."
    except requests.exceptions.Timeout:
        return "⏱️ Сервер погоды не отвечает. Попробуй позже."
    except Exception as e:
        return f"😵 Произошла ошибка: {str(e)}"

# ========== ФУНКЦИЯ КУРСОВ ВАЛЮТ ==========
def get_currency_rates():
    """Получает курсы валют с сайта Нацбанка Беларуси"""
    try:
        url = "https://api.nbrb.by/exrates/rates?periodicity=0"
        response = requests.get(url, timeout=10)
        data = response.json()
        
        text = "🇧🇾 **Курсы НБРБ**\n"
        text += f"📅 {datetime.now().strftime('%d.%m.%Y')}\n\n"
        
        currencies = ['USD', 'EUR', 'RUB', 'PLN', 'UAH', 'CNY']
        
        for currency in data:
            if currency['Cur_Abbreviation'] in currencies:
                name = currency['Cur_Abbreviation']
                rate = currency['Cur_OfficialRate']
                scale = currency['Cur_Scale']
                text += f"{scale} {name} = {rate:.4f} BYN\n"
        
        return text
    except Exception as e:
        return f"😕 Не удалось получить курсы: {str(e)}"

# ========== КНОПКИ ==========
def main_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(
        types.KeyboardButton("💰 Курсы валют"),
        types.KeyboardButton("🌤 Погода"),
        types.KeyboardButton("👋 Дарово"),
        types.KeyboardButton("😢 пока"),
        types.KeyboardButton("🤔 Как делишки?")
    )
    return markup

# ========== СТАРТ ==========
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(
        message.chat.id,
        f"Привет, {message.from_user.first_name}! 👋\n\n"
        f"Я бот Артёма. Теперь я умею:\n"
        f"💰 Показывать курсы валют НБРБ\n"
        f"🌤 Показывать погоду в любом городе\n"
        f"👋 Отвечать на кнопки\n\n"
        f"Нажимай кнопки внизу!",
        reply_markup=main_keyboard()
    )

# ========== ПОМОЩЬ ==========
@bot.message_handler(commands=['help'])
def help_command(message):
    bot.send_message(
        message.chat.id,
        "**Доступные команды:**\n"
        "/start - запуск\n"
        "/help - помощь\n"
        "/rates - курсы валют\n"
        "/weather [город] - погода (например: /weather Москва)\n\n"
        "Или просто жми кнопки внизу!",
        parse_mode="Markdown"
    )

# ========== КУРСЫ ==========
@bot.message_handler(commands=['rates'])
def rates_command(message):
    rates = get_currency_rates()
    bot.send_message(message.chat.id, rates, parse_mode="Markdown")

# ========== ПОГОДА ПО КОМАНДЕ ==========
@bot.message_handler(commands=['weather'])
def weather_command(message):
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        bot.send_message(
            message.chat.id,
            "🌍 Укажи город после команды.\n"
            "Например: `/weather Москва` или`/weather Лондон`",
            parse_mode="Markdown"
        )
        return
    
    city = parts[1]
    bot.send_chat_action(message.chat.id, 'typing')
    weather = get_weather(city)
    bot.send_message(message.chat.id, weather, parse_mode="Markdown")

# ========== ОБРАБОТКА КНОПОК ==========
@bot.message_handler(func=lambda message: True)
def handle_text(message):
    text = message.text
    
    if text == "💰 Курсы валют":
        bot.send_chat_action(message.chat.id, 'typing')
        rates = get_currency_rates()
        bot.send_message(message.chat.id, rates, parse_mode="Markdown")
        
    elif text == "🌤 Погода":
        bot.send_message(
            message.chat.id,
            "🌍 **Введи название города** (например: Минск, Москва, Лондон):",
            parse_mode="Markdown"
        )
        bot.register_next_step_handler(message, process_city_input)
        
    elif text == "👋 Дарово":
        bot.send_message(message.chat.id, "Дарово! 😊")
        
    elif text == "😢 пока":
        bot.send_message(message.chat.id, "Пока! Заходи ещё! 👋")
        
    elif text == "🤔 Как делишки?":
        markup = types.InlineKeyboardMarkup()
        markup.add(
            types.InlineKeyboardButton("✅ Отлично", callback_data="good"),
            types.InlineKeyboardButton("❌ Не очень", callback_data="bad")
        )
        bot.send_message(
            message.chat.id,
            "У меня всё хорошо! А у тебя?",
            reply_markup=markup
        )
        
    else:
        bot.send_message(
            message.chat.id,
            "Используй кнопки внизу экрана или команды /help"
        )

# ========== ОБРАБОТКА ВВОДА ГОРОДА ==========
def process_city_input(message):
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
    print("✅ Бот с погодой и курсами запущен...")
    print(f"Токен Telegram: {TOKEN[:10]}...")
    print(f"OpenWeather ключ: {OPENWEATHER_API_KEY[:5]}... (вставлен в код)")
    
    # Бесконечный цикл с обработкой ошибок
    while True:
        try:
            bot.infinity_polling(timeout=60, long_polling_timeout=60)
        except Exception as e:
            print(f"Ошибка: {e}")
            time.sleep(5)
