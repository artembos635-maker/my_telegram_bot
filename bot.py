import telebot
from telebot import types
import requests
from datetime import datetime
import time
import random
import urllib.parse
import json
import os

TOKEN = '8749955457:AAFrM_9bMzQoT6ibN97Kx5SHHWTKHrS0QRc'
OPENROUTER_API_KEY = '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'
ADMIN_ID = 8749955457

bot = telebot.TeleBot(TOKEN)
USERS_FILE = 'users.json'
user_game_mode = {}  # для игры
user_ai_mode = {}    # для ИИ

# ========== СОХРАНЕНИЕ ПОЛЬЗОВАТЕЛЕЙ ==========
def save_user(user_id, first_name, username):
    try:
        users = get_all_users()
        for user in users:
            if user['id'] == user_id:
                return False
        users.append({
            'id': user_id,
            'name': first_name,
            'username': username or 'нет username'
        })
        with open(USERS_FILE, 'w', encoding='utf-8') as f:
            json.dump(users, f, ensure_ascii=False, indent=2)
        return True
    except:
        return False

def get_all_users():
    try:
        if not os.path.exists(USERS_FILE):
            return []
        with open(USERS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return []

# ========== ИИ (OPENROUTER) ==========
def ask_ai(msg, name):
    try:
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "mistralai/mistral-7b-instruct",
                "messages": [
                    {"role": "system", "content": f"Ты дружелюбный помощник по имени Губаты. Общаешься с {name}. Отвечай кратко и дружелюбно."},
                    {"role": "user", "content": msg}
                ],
                "max_tokens": 500
            },
            timeout=30
        )
        
        if response.status_code != 200:
            return f"😕 Ошибка API: {response.status_code}"
        
        data = response.json()
        return data['choices'][0]['message']['content']
        
    except Exception as e:
        return f"😵 Ошибка: {e}"

# ========== КУРСЫ ВАЛЮТ ==========
def get_currency_rates():
    try:
        url = "https://api.nbrb.by/exrates/rates?periodicity=0"
        r = requests.get(url, timeout=10)
        data = r.json()
        
        currencies = {
            'USD': '🇺🇸 Доллар США',
            'EUR': '🇪🇺 Евро',
            'RUB': '🇷🇺 Российский рубль',
            'PLN': '🇵🇱 Польский злотый',
            'UAH': '🇺🇦 Украинская гривна',
            'CNY': '🇨🇳 Китайский юань',
            'GBP': '🇬🇧 Фунт стерлингов'
        }
        
        text = "🇧🇾 **Курсы НБРБ**\n"
        text += f"📅 {datetime.now().strftime('%d.%m.%Y')}\n\n"
        
        for c in data:
            code = c['Cur_Abbreviation']
            if code in currencies:
                name = currencies[code]
                rate = c['Cur_OfficialRate']
                scale = c['Cur_Scale']
                text += f"{name}: {scale} = {rate:.4f} BYN\n"
        
        return text
    except:
        return "😕 Не удалось получить курсы"

# ========== КАЛЬКУЛЯТОР ==========
def calculate(expression):
    try:
        allowed = set('0123456789+-*/.() ')
        if not all(c in allowed for c in expression):
            return "❌ Только цифры и + - * / ( )"
        result = eval(expression, {"__builtins__": {}}, {})
        return f"✅ {result}"
    except ZeroDivisionError:
        return "❌ На ноль нельзя"
    except:
        return "❌ Ошибка"

# ========== ПЕРЕВОДЧИК ==========
def translate_text(text):
    try:
        encoded = urllib.parse.quote(text)
        url = f"https://api.mymemory.translated.net/get?q={encoded}&langpair=en|ru"
        r = requests.get(url, timeout=10)
        data = r.json()
        if 'responseData' in data:
            return f"🌐 {data['responseData']['translatedText']}"
        return "❌ Не удалось перевести"
    except:
        return "😵 Ошибка перевода"

# ========== ИГРА ГУБАТЫ ==========
def start_game(chat_id):
    user_game_mode[chat_id] = True
    user_ai_mode[chat_id] = False
    return "🎮 Игра Губаты! Задавай вопросы, я отвечаю Да/Нет. Нажми 'Выход' чтобы закончить."

def stop_game(chat_id):
    user_game_mode[chat_id] = False
    return "🎮 Игра завершена."

def play_game(question):
    return random.choice(["Да ✅", "Нет ❌"])

# ========== ИИ РЕЖИМ ==========
def start_ai(chat_id):
    user_ai_mode[chat_id] = True
    user_game_mode[chat_id] = False
    return "🤖 Режим ИИ включён! Задавай любые вопросы. Нажми 'Выход' чтобы закончить."

def stop_ai(chat_id):
    user_ai_mode[chat_id] = False
    return "🤖 Режим ИИ завершён."

# ========== КЛАВИАТУРА ==========
def main_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(
        types.KeyboardButton("💰 Курсы"),
        types.KeyboardButton("🧮 Калькулятор"),
        types.KeyboardButton("🌐 Перевод"),
        types.KeyboardButton("🎮 Губаты"),
        types.KeyboardButton("🤖 ИИ"),
        types.KeyboardButton("❓ Помощь")
    )
    return markup

def mode_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton("🚪 Выход"))
    return markup

# ========== КОМАНДА /67 ==========
@bot.message_handler(commands=['67'])
def secret_67(message):
    for i in range(67):
        bot.send_message(message.chat.id, "six seven")
        time.sleep(0.05)

# ========== КОМАНДА /start ==========
@bot.message_handler(commands=['start'])
def start(message):
    save_user(message.chat.id, message.from_user.first_name, message.from_user.username)
    user_game_mode[message.chat.id] = False
    user_ai_mode[message.chat.id] = False
    bot.send_message(
        message.chat.id,
        f"Привет, {message.from_user.first_name}! 👋\n\n"
        f"Нажимай кнопки внизу экрана!",
        reply_markup=main_keyboard()
    )

# ========== ОБРАБОТКА КНОПОК ==========
@bot.message_handler(func=lambda m: True)
def handle_buttons(message):
    chat_id = message.chat.id
    text = message.text
    
    # Режим игры
    if user_game_mode.get(chat_id, False):
        if text == "🚪 Выход":
            bot.send_message(chat_id, stop_game(chat_id), reply_markup=main_keyboard())
        else:
            bot.send_message(chat_id, play_game(text))
        return
    
    # Режим ИИ
    if user_ai_mode.get(chat_id, False):
        if text == "🚪 Выход":
            bot.send_message(chat_id, stop_ai(chat_id), reply_markup=main_keyboard())
        else:
            bot.send_chat_action(chat_id, 'typing')
            answer = ask_ai(text, message.from_user.first_name)
            bot.send_message(chat_id, answer)
        return
    
    # Обычные кнопки
    if text == "💰 Курсы":
        bot.send_message(chat_id, get_currency_rates(), parse_mode="Markdown")
        
    elif text == "🧮 Калькулятор":
        msg = bot.send_message(chat_id, "🧮 Введи пример:\n(например: 2+2 или 10*5)")
        bot.register_next_step_handler(msg, calc_handler)
        
    elif text == "🌐 Перевод":
        msg = bot.send_message(chat_id, "🌐 Введи текст для перевода на русский:")
        bot.register_next_step_handler(msg, translate_handler)
        
    elif text == "🎮 Губаты":
        bot.send_message(chat_id, start_game(chat_id), reply_markup=mode_keyboard())
        
    elif text == "🤖 ИИ":
        bot.send_message(chat_id, start_ai(chat_id), reply_markup=mode_keyboard())
        
    elif text == "❓ Помощь":
        bot.send_message(
            chat_id,
            "📋 **Команды и кнопки:**\n\n"
            "💰 **Курсы** — курсы валют НБРБ\n"
            "🧮 **Калькулятор** — введи пример (2+2, 10*5)\n"
            "🌐 **Перевод** — переведу любой текст на русский\n"
            "🎮 **Губаты** — игра Да/Нет, задавай вопросы\n"
            "🤖 **ИИ** — умный помощник, отвечает на любые вопросы\n"
            "🚪 **Выход** — выйти из игры или ИИ\n\n"
            "🔹 /67 — секретная команда",
            parse_mode="Markdown"
        )
    else:
        bot.send_message(chat_id, "Используй кнопки внизу экрана!", reply_markup=main_keyboard())

# ========== ОБРАБОТЧИКИ ДЛЯ КАЛЬКУЛЯТОРА И ПЕРЕВОДА ==========
def calc_handler(message):
    chat_id = message.chat.id
    expr = message.text.strip()
    if expr == "/cancel":
        bot.send_message(chat_id, "❌ Отменено", reply_markup=main_keyboard())
        return
    bot.send_message(chat_id, calculate(expr), reply_markup=main_keyboard())

def translate_handler(message):
    chat_id = message.chat.id
    text = message.text.strip()
    if text == "/cancel":
        bot.send_message(chat_id, "❌ Отменено", reply_markup=main_keyboard())
        return
    bot.send_chat_action(chat_id, 'typing')
    bot.send_message(chat_id, translate_text(text), reply_markup=main_keyboard())

# ========== ЗАПУСК ==========
if __name__ == "__main__":
    print("✅ Бот Губаты с ИИ и кнопками запущен!")
    print("🤖 Использует Mistral 7B (бесплатно)")
    while True:
        try:
            bot.infinity_polling(timeout=60)
        except Exception as e:
            print(f"Ошибка: {e}")
            time.sleep(5)
