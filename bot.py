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

# ========== ВАРИАНТЫ ОТВЕТОВ ДЛЯ ИГРЫ ==========
answers = [
    "Да ✅",
    "Нет ❌",
    "100% да! 🔥",
    "Ага, конечно 😏",
    "Неа 😅",
    "Даже не думай",
    "Возможно... 🤔",
    "Шансы есть!",
    "Сомневаюсь",
    "Губаты говорят — да! 🐱",
    "Губаты говорят — нет! 😼",
    "Спроси у Губатого",
    "Мяу значит да 🐱",
    "Мяу значит нет 😾"
    "Иди читайГубаты"
]

# Храним состояние: ждёт ли бот вопрос от пользователя
waiting_for_question = {}

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
        
        currencies = ['USD', 'EUR', 'RUB']
        
        for currency in data:
            if currency['Cur_Abbreviation'] in currencies:
                name = currency['Cur_Abbreviation']
                rate = currency['Cur_OfficialRate']
                scale = currency['Cur_Scale']
                text += f"{scale} {name} = {rate:.4f} BYN\n"
        
        return text
    except:
        return "😕 Не удалось получить курсы"

# ========== КНОПКИ ==========
def main_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(
        types.KeyboardButton("💰 Курсы валют"),
        types.KeyboardButton("🌤 Погода"),
        types.KeyboardButton("🎮 Губаты"),  # Кнопка игры
        types.KeyboardButton("👋 Дарово"),
        types.KeyboardButton("😢 пока"),
        types.KeyboardButton("🤔 Как делишки?")
    )
    return markup

# ========== СТАРТ ==========
@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.chat.id
    waiting_for_question[user_id] = False  # Сбрасываем состояние
    
    bot.send_message(
        message.chat.id,
        f"Привет, {message.from_user.first_name}! 👋\n\n"
        f"🎮 Новая кнопка **'Губаты'** — жми и задавай вопрос!\n"
        f"Я отвечу Да или Нет 😄",
        reply_markup=main_keyboard(),
        parse_mode="Markdown"
    )

# ========== ОБРАБОТКА КНОПОК ==========
@bot.message_handler(func=lambda message: True)
def handle_text(message):
    user_id = message.chat.id
    text = message.text
    
    # Если ждём вопрос от пользователя
    if waiting_for_question.get(user_id, False):
        # Получаем вопрос и отвечаем
        question = text
        answer = random.choice(answers)  # Случайный ответ
        
        bot.send_message(
            user_id,
            f"❓ Твой вопрос: {question}\n\n"
            f"🎱 **Губаты говорят:** {answer}",
            parse_mode="Markdown"
        )
        
        # Сбрасываем состояние
        waiting_for_question[user_id] = False
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
        # Включаем режим ожидания вопроса
        waiting_for_question[user_id] = True
        bot.send_message(
            user_id,
            "🤔 **Напиши свой шуточный вопрос**, а я отвечу Да или Нет!\n\n"
            "Например:\n"
            "• Я сегодня выиграю в Brawl Stars?\n"
            "• Губаты меня любят?\n"
            "• Стоит ли идти гулять?",
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
        bot.send_message(call.message.chat.id, "😔 Всё наладится!")
    bot.answer_callback_query(call.id)

# ========== ЗАПУСК ==========
if __name__ == "__main__":
    print("✅ Бот с игрой 'Губаты' запущен...")
    print("🎮 Жми кнопку 'Губаты' и задавай вопросы!")
    
    while True:
        try:
            bot.infinity_polling(timeout=60, long_polling_timeout=60)
        except Exception as e:
            print(f"Ошибка: {e}")
            time.sleep(5)
