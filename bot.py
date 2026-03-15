import telebot
from telebot import types
import requests
from datetime import datetime
import time
import random

TOKEN = '8749955457:AAFrM_9bMzQoT6ibN97Kx5SHHWTKHrS0QRc'
OPENWEATHER_API_KEY = 'a64845541efe8c1134b338c2c82522ca'

bot = telebot.TeleBot(TOKEN)
user_state = {}

def calculate(expression):
    try:
        allowed = set('0123456789+-*/.() ')
        if not all(c in allowed for c in expression):
            return "❌ Только цифры и + - * /"
        result = eval(expression, {"__builtins__": {}}, {})
        return f"✅ {result}"
    except ZeroDivisionError:
        return "❌ На ноль нельзя"
    except:
        return "❌ Ошибка"

def get_weather(city):
    try:
        url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={OPENWEATHER_API_KEY}&units=metric&lang=ru"
        r = requests.get(url, timeout=10)
        data = r.json()
        if data.get('cod') != 200:
            return f"❌ Город не найден"
        t = data['main']['temp']
        desc = data['weather'][0]['description'].capitalize()
        return f"🌍 {city}: {t}°C, {desc}"
    except:
        return "😵 Ошибка"

def get_currency_rates():
    try:
        url = "https://api.nbrb.by/exrates/rates?periodicity=0"
        r = requests.get(url, timeout=10)
        data = r.json()
        currencies = {
            'USD': '🇺🇸 USD', 'EUR': '🇪🇺 EUR', 'RUB': '🇷🇺 RUB',
            'PLN': '🇵🇱 PLN', 'UAH': '🇺🇦 UAH', 'CNY': '🇨🇳 CNY',
            'GBP': '🇬🇧 GBP', 'ARS': '🇦🇷 ARS', 'BRL': '🇧🇷 BRL'
        }
        text = "🇧🇾 Курсы НБРБ\n\n"
        for c in data:
            if c['Cur_Abbreviation'] in currencies:
                name = currencies[c['Cur_Abbreviation']]
                rate = c['Cur_OfficialRate']
                text += f"{name}: {rate:.4f} BYN\n"
        return text
    except:
        return "😕 Ошибка"

@bot.message_handler(commands=['start'])
def start(message):
    user_state[message.chat.id] = None
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add("💰 Курсы", "🌤 Погода", "🎮 Губаты", "🧮 Кальк")
    bot.send_message(message.chat.id, "Выбирай:", reply_markup=markup)

@bot.message_handler(func=lambda m: True)
def handle(m):
    uid = m.chat.id
    text = m.text
    
    if user_state.get(uid) == "game":
        bot.send_message(uid, "Да" if random.choice([True, False]) else "Нет")
        user_state[uid] = None
        return
    elif user_state.get(uid) == "calc":
        bot.send_message(uid, calculate(text))
        user_state[uid] = None
        return
    
    if text == "💰 Курсы":
        bot.send_message(uid, get_currency_rates())
    elif text == "🌤 Погода":
        bot.send_message(uid, "Город:")
        bot.register_next_step_handler(m, get_weather_city)
    elif text == "🎮 Губаты":
        user_state[uid] = "game"
        bot.send_message(uid, "Вопрос?")
    elif text == "🧮 Кальк":
        user_state[uid] = "calc"
        bot.send_message(uid, "Пример:")
    else:
        bot.send_message(uid, "Жми кнопки")

def get_weather_city(m):
    bot.send_message(m.chat.id, get_weather(m.text.strip()))

if __name__ == "__main__":
    print("✅ Бот работает")
    while True:
        try:
            bot.infinity_polling(timeout=60)
        except:
            time.sleep(5)
