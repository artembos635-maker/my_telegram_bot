import telebot
from telebot import types
import requests
from datetime import datetime
import time

# Токен
TOKEN = '8749955457:AAFrM_9bMzQoT6ibN97Kx5SHHWTKHrS0QRc'
bot = telebot.TeleBot(TOKEN)

# ========== ФУНКЦИЯ КУРСОВ ВАЛЮТ (УПРОЩЕННАЯ) ==========
def get_currency_rates():
    """Получает курсы валют с сайта Нацбанка Беларуси"""
    try:
        # Используем простое API, которое всегда работает
        url = "https://api.nbrb.by/exrates/rates?periodicity=0"
        
        # Добавляем заголовки, чтобы имитировать браузер
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        
        # Проверяем, что ответ успешный
        if response.status_code != 200:
            return f"❌ Ошибка API: {response.status_code}"
        
        data = response.json()
        
        # Формируем сообщение с курсами
        text = "🇧🇾 **Курсы НБРБ**\n"
        text += f"📅 {datetime.now().strftime('%d.%m.%Y')}\n\n"
        
        # Список валют, которые нас интересуют
        currencies = ['USD', 'EUR', 'RUB', 'PLN', 'UAH', 'CNY']
        
        found = False
        for currency in data:
            if currency['Cur_Abbreviation'] in currencies:
                found = True
                name = currency['Cur_Abbreviation']
                rate = currency['Cur_OfficialRate']
                scale = currency['Cur_Scale']
                text += f"{scale} {name} = {rate} BYN\n"
        
        if not found:
            return "😕 Валюты не найдены в ответе API"
        
        return text
        
    except requests.exceptions.ConnectionError:
        return "🔌 Ошибка подключения к API"
    except requests.exceptions.Timeout:
        return "⏱️ Таймаут API"
    except Exception as e:
        return f"😵 Ошибка: {str(e)}"

# ========== КНОПКИ ==========
def main_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(
        types.KeyboardButton("💰 Курсы валют"),
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
        f"Привет, {message.from_user.first_name}! 👋\n\nЯ бот Артёма. Нажимай кнопки внизу!",
        reply_markup=main_keyboard()
    )

# ========== ПОМОЩЬ ==========
@bot.message_handler(commands=['help'])
def help_command(message):
    bot.send_message(
        message.chat.id,
        "Доступные команды:\n"
        "/start - запуск\n"
        "/help - помощь\n"
        "/rates - курсы валют\n\n"
        "Или просто жми кнопки внизу!"
    )

# ========== КУРСЫ ПО КОМАНДЕ ==========
@bot.message_handler(commands=['rates'])
def rates_command(message):
    rates = get_currency_rates()
    bot.send_message(message.chat.id, rates, parse_mode="Markdown")

# ========== ОБРАБОТКА СООБЩЕНИЙ ==========
@bot.message_handler(func=lambda message: True)
def handle_text(message):
    text = message.text
    
    if text == "💰 Курсы валют":
        # Показываем статус "печатает..."
        bot.send_chat_action(message.chat.id, 'typing')
        rates = get_currency_rates()
        bot.send_message(message.chat.id, rates, parse_mode="Markdown")
        
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
            "Используй кнопки внизу экрана!"
        )

# ========== ОБРАБОТКА INLINE КНОПОК ==========
@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    if call.data == "good":
        bot.send_message(call.message.chat.id, "😊 Отлично! Рад за тебя!")
    elif call.data == "bad":
        bot.send_message(call.message.chat.id, "😔 Не расстраивайся! Всё наладится!")
    bot.answer_callback_query(call.id)

# ========== ЗАПУСК ==========
if __name__ == "__main__":
    print("✅ Бот с курсами валют запущен...")
    print(f"Токен: {TOKEN[:10]}...")
    
    # Проверяем API при старте
    print("Проверка API курсов...")
    test_rates = get_currency_rates()
    print(f"Результат: {test_rates[:50]}...")
    
    # Бесконечный цикл с обработкой ошибок
    while True:
        try:
            bot.infinity_polling(timeout=60, long_polling_timeout=60)
        except Exception as e:
            print(f"Ошибка: {e}")
            time.sleep(5)
