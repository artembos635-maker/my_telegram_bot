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

# Хранилище состояний
user_state = {}  # 'game' или 'calc'

# ========== ФУНКЦИЯ КАЛЬКУЛЯТОРА ==========
def calculate(expression):
    """Безопасно вычисляет математическое выражение"""
    try:
        # Разрешаем только цифры и базовые операторы
        allowed_chars = set('0123456789+-*/.() ')
        if not all(c in allowed_chars for c in expression):
            return "❌ Только цифры и операторы (+, -, *, /)"
        
        # Вычисляем
        result = eval(expression, {"__builtins__": {}}, {})
        return f"✅ **Результат:** {result}"
    except ZeroDivisionError:
        return "❌ На ноль делить нельзя!"
    except Exception:
        return "❌ Некорректное выражение"

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
        weather_desc = data['weather'][0]['description'].capitalize()
        
        weather_text = f"🌍 **Погода в {city_name}, {country}**\n\n"
        weather_text += f"🌡 **Температура:** {temp:.1f}°C\n"
        weather_text += f"🤔 **Ощущается:** {feels_like:.1f}°C\n"
        weather_text += f"☁️ **{weather_desc}**\n"
        
        return weather_text
    except:
        return "😵 Ошибка получения погоды"

# ========== ФУНКЦИЯ КУРСОВ ==========
def get_currency_rates():
    try:
        url = "https://api.nbrb.by/exrates/rates?periodicity=0"
        response = requests.get(url, timeout=10)
        data = response.json()
        
        text = "🇧🇾 **Курсы НБРБ**\n"
        text += f"📅 {datetime.now().strftime('%d.%m.%Y')}\n\n"
        
        currencies = {
            'USD': '🇺🇸 Доллар США',
            'EUR': '🇪🇺 Евро',
            'RUB': '🇷🇺 Российский рубль',
            'PLN': '🇵🇱 Польский злотый',
            'UAH': '🇺🇦 Украинская гривна',
            'CNY': '🇨🇳 Китайский юань',
            'GBP': '🇬🇧 Фунт стерлингов',
            'ARS': '🇦🇷 Аргентинское песо',
            'BRL': '🇧🇷 Бразильский реал'
        }
        
        for currency in data:
            code = currency['Cur_Abbreviation']
            if code in currencies:
                name = currencies[code]
                rate = currency['Cur_OfficialRate']
                scale = currency['Cur_Scale']
                text += f"{name}: {scale} = {rate:.4f} BYN\n"
        
        return text
    except:
        return "😕 Не удалось получить курсы"

# ========== КНОПКИ ==========
def main_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(
        types.KeyboardButton("💰 Курсы валют"),
        types.KeyboardButton("🌤 Погода"),
        types.KeyboardButton("🎮 Губаты"),
        types.KeyboardButton("🧮 Калькулятор"),  # Новая кнопка
        types.KeyboardButton("👋 Дарово"),
        types.KeyboardButton("😢 пока"),
        types.KeyboardButton("🤔 Как делишки?")
    )
    return markup

# ========== СТАРТ ==========
@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.chat.id
    user_state[user_id] = None
    
    bot.send_message(
        message.chat.id,
        f"Привет, {message.from_user.first_name}! 👋\n\n"
        f"🧮 **Теперь с калькулятором!**\n"
        f"💰 Курсы валют\n"
        f"🌤 Погода\n"
        f"🎮 Губаты — Да/Нет\n"
        f"🧮 Калькулятор — примеры\n\n"
        f"Нажимай кнопки внизу!",
        reply_markup=main_keyboard(),
        parse_mode="Markdown"
    )

# ========== ОБРАБОТКА КНОПОК ==========
@bot.message_handler(func=lambda message: True)
def handle_text(message):
    user_id = message.chat.id
    text = message.text
    
    # Обработка режимов
    if user_state.get(user_id) == "game":
        answer = "Да ✅" if random.choice([True, False]) else "Нет ❌"
        bot.send_message(user_id, answer)
        user_state[user_id] = None
        return
        
    elif user_state.get(user_id) == "calc":
        result = calculate(text)
        bot.send_message(user_id, result, parse_mode="Markdown")
        user_state[user_id] = None
        return
    
    # Обычные кнопки
    if text == "💰 Курсы валют":
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
        user_state[user_id] = "game"
        bot.send_message(user_id, "Задай шуточный вопрос:")
        
    elif text == "🧮 Калькулятор":
        user_state[user_id] = "calc"
        bot.send_message(
            user_id,
            "🧮 **Введи пример** (например: 2+2, 10*5, (8+2)/2):",
            parse_mode="Markdown"
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
        bot.send_message(user_id, "У меня всё хорошо! А у тебя?", reply_markup=markup)
        
    else:
        bot.send_message(user_id, "Используй кнопки внизу экрана")

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
        bot.send_message(call.message.chat.id, "😔 Всё наладится!")
    bot.answer_callback_query(call.id)

# ========== ЗАПУСК ==========
if __name__ == "__main__":
    print("✅ Бот с калькулятором запущен...")
    print("🧮 Жми 'Калькулятор' и считай!")
    
    while True:
        try:
            bot.infinity_polling(timeout=60, long_polling_timeout=60)
        except Exception as e:
            print(f"Ошибка: {e}")
            time.sleep(5)
