import telebot
import requests
from datetime import datetime
import time
import random
import urllib.parse
import json
import os

TOKEN = '8749955457:AAFrM_9bMzQoT6ibN97Kx5SHHWTKHrS0QRc'
ADMIN_ID = 8749955457

bot = telebot.TeleBot(TOKEN)
USERS_FILE = 'users.json'

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
user_game_mode = {}

def start_game(chat_id):
    user_game_mode[chat_id] = True
    return "🎮 Игра Губаты! Задавай вопросы, я отвечаю Да/Нет. Выход: /stop"

def stop_game(chat_id):
    user_game_mode[chat_id] = False
    return "🎮 Игра завершена. /help — список команд"

def play_game(question):
    answers = ["Да ✅", "Нет ❌"]
    return random.choice(answers)

# ========== КОМАНДА HELP ==========
def show_help():
    return (
        "📋 **Команды:**\n\n"
        "🇧🇾 **/val** — курсы валют\n"
        "🧮 **/kal** — калькулятор (пример: /kal 2+2)\n"
        "🌐 **/tran** — перевод (пример: /tran Hello)\n"
        "🎮 **/gubati** — игра Да/Нет\n"
        "🛑 **/stop** — выйти из игры\n"
        "❓ **/help** — этот список"
    )

# ========== КОМАНДЫ ==========
@bot.message_handler(commands=['start'])
def start(message):
    save_user(message.chat.id, message.from_user.first_name, message.from_user.username)
    bot.send_message(
        message.chat.id,
        f"Привет, {message.from_user.first_name}! 👋\n\n"
        f"Напиши **/help** для списка команд"
    )

@bot.message_handler(commands=['help'])
def help_command(message):
    bot.send_message(message.chat.id, show_help(), parse_mode="Markdown")

@bot.message_handler(commands=['val'])
def val(message):
    bot.send_message(message.chat.id, get_currency_rates(), parse_mode="Markdown")

@bot.message_handler(commands=['kal'])
def kal(message):
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        bot.send_message(message.chat.id, "❌ Пример: /kal 2+2")
        return
    expr = parts[1]
    bot.send_message(message.chat.id, calculate(expr))

@bot.message_handler(commands=['tran'])
def tran(message):
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        bot.send_message(message.chat.id, "❌ Пример: /tran Hello")
        return
    text = parts[1]
    bot.send_chat_action(message.chat.id, 'typing')
    bot.send_message(message.chat.id, translate_text(text))

@bot.message_handler(commands=['gubati'])
def gubati(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, start_game(chat_id))

@bot.message_handler(commands=['stop'])
def stop(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, stop_game(chat_id))

@bot.message_handler(commands=['67'])
def secret_67(message):
    for i in range(67):
        bot.send_message(message.chat.id, "six seven")
        time.sleep(0.05)

# ========== НЕИЗВЕСТНЫЕ КОМАНДЫ ==========
@bot.message_handler(func=lambda m: m.text and m.text.startswith('/'))
def unknown(message):
    bot.send_message(message.chat.id, show_help(), parse_mode="Markdown")

# ========== ОБЫЧНЫЕ СООБЩЕНИЯ ==========
@bot.message_handler(func=lambda m: True)
def handle(message):
    chat_id = message.chat.id
    
    if user_game_mode.get(chat_id, False):
        if message.text.startswith('/'):
            return
        bot.send_message(chat_id, play_game(message.text))
    else:
        bot.send_message(chat_id, show_help(), parse_mode="Markdown")

# ========== ЗАПУСК ==========
if __name__ == "__main__":
    print("✅ Бот Губаты запущен!")
    print("Команды: /val, /kal, /tran, /gubati, /stop, /help, /67")
    while True:
        try:
            bot.infinity_polling(timeout=60)
        except Exception as e:
            print(f"Ошибка: {e}")
            time.sleep(5)
