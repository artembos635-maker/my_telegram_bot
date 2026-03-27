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

# ========== КОМАНДА /67 ==========
@bot.message_handler(commands=['67'])
def send_67(message):
    for i in range(67):
        bot.send_message(message.chat.id, "six seven")
        # Без задержки

# ========== ПЕРЕВОДЧИК ==========
def translate_text(text, target_lan
