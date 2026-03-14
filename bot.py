import telebot
from telebot import types
import requests
from datetime import datetime
import os
import time

# ========== НАСТРОЙКИ ==========
# Твой токен из переменных окружения (Railway)
TOKEN ='8749955457:AAFrM_9bMzQoT6ibN97Kx5SHHWTKHrS0QRc'
# Ключ DeepSeek (добавим в Railway)
DEEPSEEK_API_KEY = os.environ.get('DEEPSEEK_API_KEY')

# Создаем бота
bot = telebot.TeleBot(TOKEN)

# Словарь для хранения истории разговоров
conversation_history = {}

# ========== ФУНКЦИЯ ДЛЯ ЗАПРОСА К DEEPSEEK ==========
def ask_deepseek(user_message, chat_id, user_name):
    """Отправляет запрос к DeepSeek API и получает ответ"""
    try:
        # Проверяем наличие ключа
        if not DEEPSEEK_API_KEY:
            return "🔑 Ошибка: не настроен ключ DeepSeek API. Попроси Артёма добавить его в Railway!"

        # Инициализируем историю чата
        if chat_id not in conversation_history:
            conversation_history[chat_id] = []
        
        # Добавляем сообщение пользователя в историю
        conversation_history[chat_id].append({
            "role": "user",
            "content": user_message
        })
        
        # Ограничиваем историю последними 1000 сообщениями
        if len(conversation_history[chat_id]) > 1000:
            conversation_history[chat_id] = conversation_history[chat_id][-1000:]
        
        # Формируем сообщения для API
        messages = [
            {"role": "system", "content": f"Ты дружелюбный ИИ-помощник. Ты общаешься с пользователем по имени {user_name}. Отвечай кратко, по делу, но дружелюбно."}
        ]
        messages.extend(conversation_history[chat_id])
        
        # Запрос к DeepSeek API
        response = requests.post(
            url="https://api.deepseek.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "deepseek-chat",
                "messages": messages,
                "max_tokens": 1000,
                "temperature": 0.7
            },
            timeout=30
        )
        
        # Проверяем ответ
        if response.status_code != 200:
            print(f"Ошибка API: {response.status_code}")
            return f"😕 Ошибка API: {response.status_code}"
        
        # Получаем ответ
        data = response.json()
        ai_message = data['choices'][0]['message']['content']
        
        # Добавляем ответ в историю
        conversation_history[chat_id].append({
            "role": "assistant",
            "content": ai_message
        })
        
        return ai_message
        
    except Exception as e:
        print(f"Ошибка: {e}")
        return f"😵 Произошла ошибка, но бот работает! Попробуй еще раз."

# ========== ФУНКЦИЯ КУРСОВ ВАЛЮТ ==========
def get_belarus_rates():
    """Получает курсы валют с сайта Нацбанка Беларуси"""
    try:
        url = "https://api.nbrb.by/exrates/rates?periodicity=0"
        response = requests.get(url, timeout=10)
        data = response.json()
        
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
    except:
        return None

# ========== КОМАНДА /start ==========
@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_name = message.from_user.first_name
    chat_id = message.chat.id
    
    # Очищаем историю
    if chat_id in conversation_history:
        conversation_history[chat_id] = []
    
    # Клавиатура
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(
        types.KeyboardButton("👋 Дарово"),
        types.KeyboardButton("😢 пока"),
        types.KeyboardButton("🤔 Как делишки?"),
        types.KeyboardButton("💰 Курсы валют"),
        types.KeyboardButton("🤖 Спросить DeepSeek")
    )
    
    bot.send_message(
        message.chat.id,
        f"Привет, {user_name}! 👋\nЯ ИИ созданный Артёмом\n\n"
        f"🇧🇾 Курсы Нацбанка Беларуси\n"
        f"🤖 Работаю на DeepSeek\n\n"
        f"Нажми '🤖 Спросить DeepSeek' и задавай вопросы!",
        reply_markup=markup
    )

# ========== КОМАНДА /help ==========
@bot.message_handler(commands=['help'])
def send_help(message):
    bot.send_message(
        message.chat.id,
        "🇧🇾 **Бот с DeepSeek**\n\n"
        "Команды:\n"
        "/start - запуск\n"
        "/help - помощь\n"
        "/rates - курсы валют\n"
        "/clear - очистить историю",
        parse_mode="Markdown"
    )

# ========== КОМАНДА /clear ==========
@bot.message_handler(commands=['clear'])
def clear_history(message):
    chat_id = message.chat.id
    if chat_id in conversation_history:
        conversation_history[chat_id] = []
    bot.send_message(message.chat.id, "🧹 История очищена!")

# ========== КОМАНДА /rates ==========
@bot.message_handler(commands=['rates'])
def show_rates_command(message):
    show_rates(message)

# ========== ПОКАЗ КУРСОВ ==========
def show_rates(message):
    rates = get_belarus_rates()
    
    if not rates:
        bot.send_message(message.chat.id, "😕 Не удалось получить курсы")
        return
    
    text = "🇧🇾 **Курсы НБРБ**\n"
    text += f"📅 {datetime.now().strftime('%d.%m.%Y')}\n\n"
    
    for code, data in rates.items():
        text += f"{data['scale']} {code} = {data['rate']:.4f} BYN\n"
    
    bot.send_message(message.chat.id, text, parse_mode="Markdown")

# ========== ОБРАБОТКА СООБЩЕНИЙ ==========
@bot.message_handler(func=lambda message: True)
def handle_text(message):
    text = message.text
    chat_id = message.chat.id
    user_name = message.from_user.first_name
    
    # Кнопки
    if text == "👋 Дарово":
        bot.send_message(chat_id, "Дарово! 😊")
        
    elif text == "😢 пока":
        bot.send_message(chat_id, "Пока! 👋")
        
    elif text == "🤔 Как делишки?":
        markup = types.InlineKeyboardMarkup()
        markup.add(
            types.InlineKeyboardButton("✅ Отлично", callback_data="good"),
            types.InlineKeyboardButton("❌ Не очень", callback_data="bad")
        )
        bot.send_message(chat_id, "У меня всё хорошо! А у тебя?", reply_markup=markup)
        
    elif text == "💰 Курсы валют":
        show_rates(message)
        
    elif text == "🤖 Спросить DeepSeek":
        bot.send_message(
            chat_id,
            "🤖 **Режим DeepSeek**\n\nПиши любые вопросы!",
            parse_mode="Markdown"
        )
        
    else:
        # Отправляем в DeepSeek
        bot.send_chat_action(chat_id, 'typing')
        response = ask_deepseek(text, chat_id, user_name)
        bot.send_message(chat_id, response)

# ========== КНОПКИ ==========
@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    if call.data == "good":
        bot.send_message(call.message.chat.id, "😊 Отлично!")
    elif call.data == "bad":
        bot.send_message(call.message.chat.id, "😔 Всё наладится!")
    bot.answer_callback_query(call.id)

# ========== ЗАПУСК ==========
if __name__ == "__main__":
    print("✅ Бот запущен...")
    while True:
        try:
            bot.infinity_polling(timeout=60, long_polling_timeout=60)
        except Exception as e:
            print(f"Ошибка: {e}")
            time.sleep(5)
