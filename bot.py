import telebot
from telebot import types
import requests
from datetime import datetime
import time
import random
import urllib.parse

TOKEN = '8749955457:AAFrM_9bMzQoT6ibN97Kx5SHHWTKHrS0QRc'
OPENWEATHER_API_KEY = 'a64845541efe8c1134b338c2c82522ca'

bot = telebot.TeleBot(TOKEN)
user_state = {}  # None, 'game', 'calc', 'translate'

# ========== ПЕРЕВОДЧИК ==========
def translate_text(text, target_lang='ru'):
    """Переводит текст на целевой язык (по умолчанию русский)"""
    try:
        encoded_text = urllib.parse.quote(text)
        url = f"https://api.mymemory.translated.net/get?q={encoded_text}&langpair=en|{target_lang}"
        response = requests.get(url, timeout=10)
        data = response.json()
        
        if response.status_code == 200 and 'responseData' in data:
            translated = data['responseData']['translatedText']
            return f"🌐 **Перевод:**\n{translated}"
        else:
            return "❌ Не удалось перевести"
    except Exception as e:
        return f"😵 Ошибка: {str(e)}"

# ========== КАЛЬКУЛЯТОР ==========
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

# ========== ПОГОДА ==========
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

# ========== КУРСЫ ВАЛЮТ (С КОЛИЧЕСТВОМ) ==========
def get_currency_rates():
    try:
        url = "https://api.nbrb.by/exrates/rates?periodicity=0"
        r = requests.get(url, timeout=10)
        data = r.json()
        
        # ТВОЙ СПИСОК ВАЛЮТ (как ты показал)
        currencies = {
            'AUD': '🇦🇺 Австралийский доллар',
            'AMD': '🇦🇲 Армянский драм',
            'BRL': '🇧🇷 Бразильский реал',
            'UAH': '🇺🇦 Украинская гривна',
            'DKK': '🇩🇰 Датская крона',
            'AED': '🇦🇪 Дирхам ОАЭ',
            'USD': '🇺🇸 Доллар США',
            'VND': '🇻🇳 Вьетнамский донг',
            'EUR': '🇪🇺 Евро',
            'PLN': '🇵🇱 Польский злотый',
            'JPY': '🇯🇵 Японская иена',
            'INR': '🇮🇳 Индийская рупия',
            'ISK': '🇮🇸 Исландская крона',
            'CAD': '🇨🇦 Канадский доллар',
            'CNY': '🇨🇳 Китайский юань',
            'KWD': '🇰🇼 Кувейтский динар',
            'MDL': '🇲🇩 Молдавский лей',
            'NZD': '🇳🇿 Новозеландский доллар',
            'NOK': '🇳🇴 Норвежская крона',
            'RUB': '🇷🇺 Российский рубль',
            'SGD': '🇸🇬 Сингапурский доллар',
            'KGS': '🇰🇬 Киргизский сом',
            'KZT': '🇰🇿 Казахстанский тенге',
            'TRY': '🇹🇷 Турецкая лира',
            'GBP': '🇬🇧 Фунт стерлингов',
            'CZK': '🇨🇿 Чешская крона',
            'SEK': '🇸🇪 Шведская крона',
            'CHF': '🇨🇭 Швейцарский франк'
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
    except Exception as e:
        return f"😕 Ошибка: {str(e)}"

# ========== КЛАВИАТУРЫ ==========
def mode_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton("🔴 Выключить Губатого"))
    return markup

def main_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(
        types.KeyboardButton("💰 Курсы"),
        types.KeyboardButton("🌤 Погода"),
        types.KeyboardButton("🎮 Губаты"),
        types.KeyboardButton("🧮 Кальк"),
        types.KeyboardButton("🌐 Перевод")  # Новая кнопка
    )
    return markup

# ========== СТАРТ ==========
@bot.message_handler(commands=['start'])
def start(message):
    user_state[message.chat.id] = None
    bot.send_message(
        message.chat.id,
        "Выбирай:",
        reply_markup=main_keyboard()
    )

# ========== ОБРАБОТКА СООБЩЕНИЙ ==========
@bot.message_handler(func=lambda m: True)
def handle(m):
    uid = m.chat.id
    text = m.text
    
    # Кнопка выключения режима
    if text == "🔴 Выключить Губатого":
        user_state[uid] = None
        bot.send_message(uid, "Режим выключен", reply_markup=main_keyboard())
        return
    
    # Режим игры
    if user_state.get(uid) == "game":
        bot.send_message(uid, "Да" if random.choice([True, False]) else "Нет")
        return
        
    # Режим калькулятора
    if user_state.get(uid) == "calc":
        bot.send_message(uid, calculate(text))
        return
    
    # Режим переводчика
    if user_state.get(uid) == "translate":
        bot.send_message(uid, translate_text(text))
        # Не выключаем режим после одного перевода
        return
    
    # Обычные кнопки
    if text == "💰 Курсы":
        bot.send_message(uid, get_currency_rates(), parse_mode="Markdown")
        
    elif text == "🌤 Погода":
        msg = bot.send_message(uid, "Город?")
        bot.register_next_step_handler(msg, get_weather_city)
        
    elif text == "🎮 Губаты":
        user_state[uid] = "game"
        bot.send_message(
            uid,
            "🎮 Режим Губаты: пиши вопросы, буду отвечать Да/Нет",
            reply_markup=mode_keyboard()
        )
        
    elif text == "🧮 Кальк":
        user_state[uid] = "calc"
        bot.send_message(
            uid,
            "🧮 Режим Калькулятора: пиши примеры",
            reply_markup=mode_keyboard()
        )
        
    elif text == "🌐 Перевод":
        user_state[uid] = "translate"
        bot.send_message(
            uid,
            "🌐 Режим Переводчика: пиши текст на любом языке, переведу на русский",
            reply_markup=mode_keyboard()
        )
        
    else:
        bot.send_message(uid, "Жми кнопки")

# ========== ПОЛУЧЕНИЕ ПОГОДЫ ПОСЛЕ ВВОДА ГОРОДА ==========
def get_weather_city(m):
    bot.send_message(m.chat.id, get_weather(m.text.strip()))

# ========== ЗАПУСК ==========
if __name__ == "__main__":
    print("✅ Бот с переводчиком и курсами валют запущен")
    print("💰 Курсы с количеством (как ты хотел)")
    print("🌐 Переводчик в отдельном режиме")
    
    while True:
        try:
            bot.infinity_polling(timeout=60)
        except Exception as e:
            print(f"Ошибка: {e}")
            time.sleep(5)
