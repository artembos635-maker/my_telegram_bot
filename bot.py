import telebot
from telebot import types
import json
import os
import time
from datetime import datetime, timedelta
import random
import string
import hashlib
import sqlite3
from collections import defaultdict
import threading
import re
import logging
from typing import Dict, List, Tuple, Optional, Any
import requests
from io import BytesIO
import matplotlib.pyplot as plt
from PIL import Image, ImageDraw, ImageFont
import pandas as pd
from apscheduler.schedulers.background import BackgroundScheduler
import asyncio
import aiohttp
from functools import wraps
import smtplib
from email.mime.text import MimeText
import qrcode
import pytz
from googletrans import Translator
import calendar

# ========== НАСТРОЙКИ И КОНФИГУРАЦИЯ ==========
TOKEN = '8786806064:AAGnZbQeNQCow4txVsS_O_-BQkDLkARk6RU'
ADMINS = [7717477509, 1334363706]

# Настройки базы данных
DB_FILE = 'bot_database.db'
USERS_FILE = 'users.json'
REFERRALS_FILE = 'referrals.json'
FEEDBACK_FILE = 'feedback.json'
POLLS_FILE = 'polls.json'
TASKS_FILE = 'tasks.json'
ACHIEVEMENTS_FILE = 'achievements.json'
ECOMMERCE_FILE = 'ecommerce.json'
TICKETS_FILE = 'support_tickets.json'
MODERATION_FILE = 'moderation.json'

# Настройки бота
MAX_MESSAGE_LENGTH = 4096
MAX_PHOTO_SIZE = 10 * 1024 * 1024  # 10MB
SUPPORTED_LANGUAGES = ['ru', 'en', 'uz', 'ky', 'tg', 'kz']
DEFAULT_LANGUAGE = 'ru'
COOLDOWN_TIME = 2  # секунды между командами
DAILY_BONUS = 100
REFERRAL_BONUS = 50
REFERRAL_PERCENT = 10

# Настройки для магазина
PRODUCTS = {
    'vitamin_c': {'name': 'Витамин C', 'price': 500, 'stock': 100, 'description': 'Укрепляет иммунитет'},
    'omega_3': {'name': 'Омега-3', 'price': 800, 'stock': 50, 'description': 'Полезна для сердца'},
    'magnesium': {'name': 'Магний', 'price': 600, 'stock': 75, 'description': 'Для нервной системы'},
    'zinc': {'name': 'Цинк', 'price': 400, 'stock': 120, 'description': 'Для иммунитета и кожи'},
    'vitamin_d': {'name': 'Витамин D', 'price': 450, 'stock': 90, 'description': 'Для костей и иммунитета'},
    'collagen': {'name': 'Коллаген', 'price': 1200, 'stock': 40, 'description': 'Для кожи и суставов'},
    'probiotics': {'name': 'Пробиотики', 'price': 700, 'stock': 60, 'description': 'Для пищеварения'},
    'b_complex': {'name': 'Витамины группы B', 'price': 550, 'stock': 85, 'description': 'Для энергии'}
}

# Настройки для заданий
DAILY_TASKS = {
    'daily_visit': {'name': 'Ежедневный визит', 'reward': 50, 'description': 'Зайдите в бота каждый день'},
    'share_contact': {'name': 'Поделиться контактом', 'reward': 100, 'description': 'Поделитесь номером телефона'},
    'invite_friend': {'name': 'Пригласить друга', 'reward': 150, 'description': 'Пригласите друга по реферальной ссылке'},
    'rate_bot': {'name': 'Оценить бота', 'reward': 75, 'description': 'Поставьте оценку боту'},
    'make_purchase': {'name': 'Совершить покупку', 'reward': 200, 'description': 'Купите любой товар'}
}

# Достижения
ACHIEVEMENTS = {
    'first_visit': {'name': 'Первый визит', 'points': 10, 'icon': '🎉', 'description': 'Впервые зашли в бота'},
    'loyal_member': {'name': 'Верный участник', 'points': 50, 'icon': '⭐', 'description': 'Активны 7 дней подряд'},
    'social_butterfly': {'name': 'Социальная бабочка', 'points': 100, 'icon': '🦋', 'description': 'Пригласили 5 друзей'},
    'big_spender': {'name': 'Крупный покупатель', 'points': 200, 'icon': '💰', 'description': 'Потратили 5000+'},
    'helper': {'name': 'Помощник', 'points': 150, 'icon': '🤝', 'description': 'Помогли другим 10 раз'},
    'expert': {'name': 'Эксперт', 'points': 300, 'icon': '🎓', 'description': 'Получили уровень 5'},
    'collector': {'name': 'Коллекционер', 'points': 250, 'icon': '📦', 'description': 'Купили все товары'},
    'marathon': {'name': 'Марафонец', 'points': 180, 'icon': '🏃', 'description': '30 дней активности'},
    'philanthropist': {'name': 'Филантроп', 'points': 400, 'icon': '❤️', 'description': 'Сделали 20 добрых дел'},
    'influencer': {'name': 'Влиятельный', 'points': 500, 'icon': '👑', 'description': 'Пригласили 50 друзей'}
}

# Валюты и бонусы
BONUS_COINS = 'bonic_coins'
LOYALTY_POINTS = 'loyalty_points'

# Эмодзи и иконки
EMOJIS = {
    'check': '✅', 'error': '❌', 'warning': '⚠️', 'info': 'ℹ️',
    'money': '💰', 'star': '⭐', 'heart': '❤️', 'fire': '🔥',
    'gift': '🎁', 'trophy': '🏆', 'crown': '👑', 'diamond': '💎',
    'mail': '📧', 'phone': '📞', 'location': '📍', 'calendar': '📅',
    'time': '⏰', 'chart': '📊', 'settings': '⚙️', 'help': '🆘',
    'shop': '🛒', 'cart': '🛍️', 'coupon': '🎫', 'discount': '🏷️',
    'user': '👤', 'users': '👥', 'admin': '🔧', 'moderator': '🛡️',
    'level': '📈', 'points': '🔢', 'coins': '🪙', 'credit': '💳'
}

# ========== ЛОГГИРОВАНИЕ ==========
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ========== БАЗА ДАННЫХ SQLITE ==========
class Database:
    def __init__(self, db_file):
        self.db_file = db_file
        self.init_db()
    
    def get_connection(self):
        return sqlite3.connect(self.db_file)
    
    def init_db(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Таблица пользователей
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                last_name TEXT,
                language TEXT DEFAULT 'ru',
                registration_date TIMESTAMP,
                last_active TIMESTAMP,
                balance INTEGER DEFAULT 0,
                loyalty_points INTEGER DEFAULT 0,
                level INTEGER DEFAULT 1,
                experience INTEGER DEFAULT 0,
                referrer_id INTEGER,
                is_banned BOOLEAN DEFAULT 0,
                is_premium BOOLEAN DEFAULT 0,
                premium_until TIMESTAMP,
                total_purchases INTEGER DEFAULT 0,
                total_spent INTEGER DEFAULT 0,
                daily_streak INTEGER DEFAULT 0,
                last_daily TIMESTAMP,
                phone_number TEXT,
                email TEXT,
                birth_date TEXT,
                city TEXT,
                avatar_file_id TEXT,
                notification_settings TEXT DEFAULT '{}'
            )
        ''')
        
        # Таблица транзакций
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                type TEXT,
                amount INTEGER,
                description TEXT,
                timestamp TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        ''')
        
        # Таблица рефералов
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS referrals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                referrer_id INTEGER,
                referred_id INTEGER,
                reward_amount INTEGER,
                timestamp TIMESTAMP,
                FOREIGN KEY (referrer_id) REFERENCES users(user_id),
                FOREIGN KEY (referred_id) REFERENCES users(user_id)
            )
        ''')
        
        # Таблица покупок
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS purchases (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                product_id TEXT,
                quantity INTEGER,
                price INTEGER,
                total_amount INTEGER,
                timestamp TIMESTAMP,
                status TEXT DEFAULT 'pending',
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        ''')
        
        # Таблица выполненных заданий
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS completed_tasks (
                user_id INTEGER,
                task_id TEXT,
                completed_date TIMESTAMP,
                reward_claimed BOOLEAN DEFAULT 1,
                PRIMARY KEY (user_id, task_id),
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        ''')
        
        # Таблица достижений
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_achievements (
                user_id INTEGER,
                achievement_id TEXT,
                unlocked_date TIMESTAMP,
                PRIMARY KEY (user_id, achievement_id),
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        ''')
        
        # Таблица опросов
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS polls (
                poll_id INTEGER PRIMARY KEY AUTOINCREMENT,
                creator_id INTEGER,
                question TEXT,
                options TEXT,
                votes TEXT,
                created_date TIMESTAMP,
                end_date TIMESTAMP,
                is_active BOOLEAN DEFAULT 1,
                FOREIGN KEY (creator_id) REFERENCES users(user_id)
            )
        ''')
        
        # Таблица заявок в поддержку
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS support_tickets (
                ticket_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                subject TEXT,
                message TEXT,
                status TEXT DEFAULT 'open',
                created_date TIMESTAMP,
                updated_date TIMESTAMP,
                assigned_admin INTEGER,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        ''')
        
        # Таблица сообщений поддержки
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS support_messages (
                message_id INTEGER PRIMARY KEY AUTOINCREMENT,
                ticket_id INTEGER,
                sender_id INTEGER,
                message TEXT,
                timestamp TIMESTAMP,
                attachments TEXT,
                FOREIGN KEY (ticket_id) REFERENCES support_tickets(ticket_id)
            )
        ''')
        
        # Таблица купонов
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS coupons (
                coupon_code TEXT PRIMARY KEY,
                discount_percent INTEGER,
                valid_until TIMESTAMP,
                max_uses INTEGER,
                used_count INTEGER DEFAULT 0,
                created_by INTEGER
            )
        ''')
        
        # Таблица использованных купонов
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS used_coupons (
                user_id INTEGER,
                coupon_code TEXT,
                used_date TIMESTAMP,
                PRIMARY KEY (user_id, coupon_code),
                FOREIGN KEY (user_id) REFERENCES users(user_id),
                FOREIGN KEY (coupon_code) REFERENCES coupons(coupon_code)
            )
        ''')
        
        # Таблица напоминаний
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS reminders (
                reminder_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                title TEXT,
                description TEXT,
                reminder_date TIMESTAMP,
                is_completed BOOLEAN DEFAULT 0,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        ''')
        
        # Таблица заметок
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS notes (
                note_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                title TEXT,
                content TEXT,
                created_date TIMESTAMP,
                updated_date TIMESTAMP,
                color TEXT DEFAULT 'white',
                is_pinned BOOLEAN DEFAULT 0,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        ''')
        
        # Таблица обратной связи
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS feedback (
                feedback_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                rating INTEGER,
                comment TEXT,
                timestamp TIMESTAMP,
                is_responded BOOLEAN DEFAULT 0,
                response TEXT,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        ''')
        
        # Таблица статистики бота
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS bot_stats (
                stat_key TEXT PRIMARY KEY,
                stat_value TEXT,
                updated_date TIMESTAMP
            )
        ''')
        
        # Таблица временных блокировок
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cooldowns (
                user_id INTEGER,
                command TEXT,
                last_used TIMESTAMP,
                PRIMARY KEY (user_id, command)
            )
        ''')
        
        # Таблица ежедневных бонусов
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS daily_bonus_history (
                user_id INTEGER,
                bonus_date DATE,
                amount INTEGER,
                PRIMARY KEY (user_id, bonus_date),
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        ''')
        
        # Таблица голосований в чате
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS chat_votes (
                vote_id INTEGER PRIMARY KEY AUTOINCREMENT,
                chat_id INTEGER,
                creator_id INTEGER,
                question TEXT,
                options TEXT,
                votes TEXT,
                created_date TIMESTAMP,
                end_date TIMESTAMP,
                is_active BOOLEAN DEFAULT 1
            )
        ''')
        
        # Таблица голосов
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS votes (
                vote_id INTEGER,
                user_id INTEGER,
                option_index INTEGER,
                timestamp TIMESTAMP,
                PRIMARY KEY (vote_id, user_id),
                FOREIGN KEY (vote_id) REFERENCES chat_votes(vote_id)
            )
        ''')
        
        # Таблица модерации
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS moderation_actions (
                action_id INTEGER PRIMARY KEY AUTOINCREMENT,
                moderator_id INTEGER,
                target_user_id INTEGER,
                action_type TEXT,
                reason TEXT,
                duration TEXT,
                timestamp TIMESTAMP,
                FOREIGN KEY (moderator_id) REFERENCES users(user_id),
                FOREIGN KEY (target_user_id) REFERENCES users(user_id)
            )
        ''')
        
        # Таблица уровней
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS level_requirements (
                level INTEGER PRIMARY KEY,
                experience_needed INTEGER,
                bonus_coins INTEGER,
                loyalty_points INTEGER
            )
        ''')
        
        # Заполняем требования к уровням
        for level in range(1, 101):
            exp_needed = level * 100
            bonus_coins = level * 50
            loyalty_points = level * 10
            cursor.execute('''
                INSERT OR IGNORE INTO level_requirements (level, experience_needed, bonus_coins, loyalty_points)
                VALUES (?, ?, ?, ?)
            ''', (level, exp_needed, bonus_coins, loyalty_points))
        
        conn.commit()
        conn.close()
    
    def execute_query(self, query, params=()):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(query, params)
        conn.commit()
        result = cursor.fetchall()
        conn.close()
        return result
    
    def execute_insert(self, query, params=()):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(query, params)
        conn.commit()
        last_id = cursor.lastrowid
        conn.close()
        return last_id

# ========== ИНИЦИАЛИЗАЦИЯ ==========
db = Database(DB_FILE)
bot = telebot.TeleBot(TOKEN)
scheduler = BackgroundScheduler()
translator = Translator()

# Словари для хранения временных данных
user_states = {}
user_temp_data = {}
poll_messages = {}
broadcast_data = {}
feedback_data = {}
ticket_data = {}
reminder_data = {}
note_data = {}
vote_messages = {}
level_up_messages = {}

# ========== ДЕКОРАТОРЫ И УТИЛИТЫ ==========
def rate_limit(limit_per_minute=30):
    """Декоратор для ограничения частоты запросов"""
    def decorator(func):
        last_called = {}
        
        @wraps(func)
        def wrapper(message, *args, **kwargs):
            user_id = message.from_user.id
            current_time = time.time()
            
            if user_id in last_called:
                if current_time - last_called[user_id] < 60.0 / limit_per_minute:
                    bot.reply_to(message, f"{EMOJIS['warning']} Пожалуйста, не спамьте! Подождите немного.")
                    return
            
            last_called[user_id] = current_time
            return func(message, *args, **kwargs)
        
        return wrapper
    return decorator

def admin_required(func):
    """Декоратор для проверки прав администратора"""
    @wraps(func)
    def wrapper(message, *args, **kwargs):
        if not is_admin(message.from_user.id):
            bot.reply_to(message, f"{EMOJIS['error']} У вас нет прав для выполнения этой команды!")
            return
        return func(message, *args, **kwargs)
    return wrapper

def user_exists(func):
    """Декоратор для проверки существования пользователя"""
    @wraps(func)
    def wrapper(message, *args, **kwargs):
        if not user_exists_in_db(message.from_user.id):
            bot.reply_to(message, f"{EMOJIS['error']} Пожалуйста, сначала нажмите /start")
            return
        return func(message, *args, **kwargs)
    return wrapper

def log_command(func):
    """Декоратор для логирования команд"""
    @wraps(func)
    def wrapper(message, *args, **kwargs):
        logger.info(f"Command {func.__name__} from user {message.from_user.id}")
        return func(message, *args, **kwargs)
    return wrapper

def get_user_language(user_id):
    """Получить язык пользователя"""
    result = db.execute_query("SELECT language FROM users WHERE user_id = ?", (user_id,))
    if result:
        return result[0][0]
    return DEFAULT_LANGUAGE

def get_translation(text, user_id):
    """Перевести текст на язык пользователя"""
    language = get_user_language(user_id)
    if language == 'ru':
        return text
    
    try:
        translated = translator.translate(text, dest=language)
        return translated.text
    except:
        return text

def is_admin(user_id):
    """Проверка является ли пользователь администратором"""
    return user_id in ADMINS

def user_exists_in_db(user_id):
    """Проверка существования пользователя в БД"""
    result = db.execute_query("SELECT 1 FROM users WHERE user_id = ?", (user_id,))
    return len(result) > 0

def add_or_update_user(user_id, username, first_name, last_name=None, referrer_id=None):
    """Добавление или обновление пользователя в БД"""
    now = datetime.now()
    
    # Проверяем существует ли пользователь
    if user_exists_in_db(user_id):
        db.execute_query(
            "UPDATE users SET last_active = ?, username = ?, first_name = ? WHERE user_id = ?",
            (now, username, first_name, user_id)
        )
        return False
    
    # Добавляем нового пользователя
    db.execute_query('''
        INSERT INTO users (user_id, username, first_name, last_name, registration_date, last_active, balance, referrer_id)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (user_id, username, first_name, last_name, now, now, 0, referrer_id))
    
    # Обработка реферала
    if referrer_id and referrer_id != user_id:
        # Начисляем бонус рефереру
        db.execute_query(
            "UPDATE users SET balance = balance + ? WHERE user_id = ?",
            (REFERRAL_BONUS, referrer_id)
        )
        
        # Записываем реферальную связь
        db.execute_query('''
            INSERT INTO referrals (referrer_id, referred_id, reward_amount, timestamp)
            VALUES (?, ?, ?, ?)
        ''', (referrer_id, user_id, REFERRAL_BONUS, now))
        
        # Добавляем транзакцию
        add_transaction(referrer_id, 'referral', REFERRAL_BONUS, f"Бонус за приглашение {username}")
        
        # Проверяем достижения
        check_referral_achievements(referrer_id)
    
    # Проверяем достижения
    check_achievements(user_id)
    
    return True

def add_transaction(user_id, transaction_type, amount, description):
    """Добавить транзакцию"""
    db.execute_query('''
        INSERT INTO transactions (user_id, type, amount, description, timestamp)
        VALUES (?, ?, ?, ?, ?)
    ''', (user_id, transaction_type, amount, description, datetime.now()))

def add_experience(user_id, exp_amount):
    """Добавить опыт пользователю"""
    current_exp = db.execute_query("SELECT experience, level FROM users WHERE user_id = ?", (user_id,))[0]
    new_exp = current_exp[0] + exp_amount
    current_level = current_exp[1]
    
    # Проверяем повышение уровня
    level_req = db.execute_query("SELECT experience_needed FROM level_requirements WHERE level = ?", (current_level + 1,))
    if level_req and new_exp >= level_req[0][0]:
        level_up(user_id, current_level + 1)
    
    db.execute_query("UPDATE users SET experience = ? WHERE user_id = ?", (new_exp, user_id))

def level_up(user_id, new_level):
    """Повышение уровня пользователя"""
    # Получаем бонусы за новый уровень
    level_bonus = db.execute_query("SELECT bonus_coins, loyalty_points FROM level_requirements WHERE level = ?", (new_level,))[0]
    bonus_coins = level_bonus[0]
    loyalty_points = level_bonus[1]
    
    # Начисляем бонусы
    db.execute_query('''
        UPDATE users SET level = ?, balance = balance + ?, loyalty_points = loyalty_points + ?
        WHERE user_id = ?
    ''', (new_level, bonus_coins, loyalty_points, user_id))
    
    # Добавляем транзакции
    add_transaction(user_id, 'level_up', bonus_coins, f"Бонус за достижение {new_level} уровня")
    
    # Отправляем уведомление
    user_lang = get_user_language(user_id)
    message = f"{EMOJIS['level']} Поздравляем! Вы достигли {new_level} уровня!\n"
    message += f"Награда: {bonus_coins} {BONUS_COINS} и {loyalty_points} баллов лояльности!"
    
    bot.send_message(user_id, message)
    
    # Проверяем достижения
    check_level_achievements(user_id, new_level)

def check_achievements(user_id):
    """Проверка и выдача достижений"""
    user_data = db.execute_query("SELECT total_purchases, daily_streak FROM users WHERE user_id = ?", (user_id,))[0]
    total_purchases = user_data[0]
    daily_streak = user_data[1]
    
    # Получаем количество рефералов
    referrals_count = db.execute_query("SELECT COUNT(*) FROM referrals WHERE referrer_id = ?", (user_id,))[0][0]
    
    # Проверяем каждое достижение
    achievements_to_unlock = []
    
    if total_purchases >= 1 and not check_achievement_unlocked(user_id, 'first_purchase'):
        achievements_to_unlock.append('first_purchase')
    
    if daily_streak >= 7 and not check_achievement_unlocked(user_id, 'weekly_warrior'):
        achievements_to_unlock.append('weekly_warrior')
    
    if daily_streak >= 30 and not check_achievement_unlocked(user_id, 'monthly_master'):
        achievements_to_unlock.append('monthly_master')
    
    if referrals_count >= 5 and not check_achievement_unlocked(user_id, 'social_butterfly'):
        achievements_to_unlock.append('social_butterfly')
    
    if referrals_count >= 50 and not check_achievement_unlocked(user_id, 'influencer'):
        achievements_to_unlock.append('influencer')
    
    # Выдаем достижения
    for ach_id in achievements_to_unlock:
        unlock_achievement(user_id, ach_id)

def check_achievement_unlocked(user_id, achievement_id):
    """Проверка получено ли достижение"""
    result = db.execute_query(
        "SELECT 1 FROM user_achievements WHERE user_id = ? AND achievement_id = ?",
        (user_id, achievement_id)
    )
    return len(result) > 0

def unlock_achievement(user_id, achievement_id):
    """Выдать достижение пользователю"""
    achievement = ACHIEVEMENTS.get(achievement_id)
    if not achievement:
        return
    
    db.execute_query('''
        INSERT INTO user_achievements (user_id, achievement_id, unlocked_date)
        VALUES (?, ?, ?)
    ''', (user_id, achievement_id, datetime.now()))
    
    # Начисляем очки
    db.execute_query(
        "UPDATE users SET loyalty_points = loyalty_points + ? WHERE user_id = ?",
        (achievement['points'], user_id)
    )
    
    # Отправляем уведомление
    message = f"{achievement['icon']} НОВОЕ ДОСТИЖЕНИЕ!\n"
    message += f"★ {achievement['name']}\n"
    message += f"{achievement['description']}\n"
    message += f"Награда: +{achievement['points']} баллов лояльности!"
    
    bot.send_message(user_id, message)

def check_referral_achievements(user_id):
    """Проверка достижений по рефералам"""
    referrals_count = db.execute_query("SELECT COUNT(*) FROM referrals WHERE referrer_id = ?", (user_id,))[0][0]
    
    if referrals_count >= 1 and not check_achievement_unlocked(user_id, 'first_referral'):
        unlock_achievement(user_id, 'first_referral')
    
    if referrals_count >= 10 and not check_achievement_unlocked(user_id, 'referral_master'):
        unlock_achievement(user_id, 'referral_master')
    
    if referrals_count >= 50 and not check_achievement_unlocked(user_id, 'referral_legend'):
        unlock_achievement(user_id, 'referral_legend')

def check_level_achievements(user_id, level):
    """Проверка достижений по уровням"""
    if level >= 5 and not check_achievement_unlocked(user_id, 'level_5'):
        unlock_achievement(user_id, 'level_5')
    
    if level >= 10 and not check_achievement_unlocked(user_id, 'level_10'):
        unlock_achievement(user_id, 'level_10')
    
    if level >= 25 and not check_achievement_unlocked(user_id, 'level_25'):
        unlock_achievement(user_id, 'level_25')
    
    if level >= 50 and not check_achievement_unlocked(user_id, 'level_50'):
        unlock_achievement(user_id, 'level_50')
    
    if level >= 100 and not check_achievement_unlocked(user_id, 'level_100'):
        unlock_achievement(user_id, 'level_100')

def get_daily_bonus(user_id):
    """Получить ежедневный бонус"""
    today = datetime.now().date()
    
    # Проверяем получал ли уже бонус сегодня
    result = db.execute_query(
        "SELECT 1 FROM daily_bonus_history WHERE user_id = ? AND bonus_date = ?",
        (user_id, today)
    )
    
    if result:
        return None, "Сегодня вы уже получили бонус! Возвращайтесь завтра!"
    
    # Получаем текущую серию
    user_data = db.execute_query("SELECT daily_streak FROM users WHERE user_id = ?", (user_id,))[0]
    current_streak = user_data[0]
    
    # Проверяем был ли вчера бонус
    yesterday = today - timedelta(days=1)
    had_yesterday = db.execute_query(
        "SELECT 1 FROM daily_bonus_history WHERE user_id = ? AND bonus_date = ?",
        (user_id, yesterday)
    )
    
    if had_yesterday:
        new_streak = current_streak + 1
    else:
        new_streak = 1
    
    # Рассчитываем бонус
    bonus_amount = DAILY_BONUS + (new_streak * 5)  # +5 за каждый день серии
    bonus_amount = min(bonus_amount, 500)  # Максимум 500
    
    # Начисляем бонус
    db.execute_query(
        "UPDATE users SET balance = balance + ?, daily_streak = ? WHERE user_id = ?",
        (bonus_amount, new_streak, user_id)
    )
    
    # Записываем в историю
    db.execute_query('''
        INSERT INTO daily_bonus_history (user_id, bonus_date, amount)
        VALUES (?, ?, ?)
    ''', (user_id, today, bonus_amount))
    
    # Добавляем транзакцию
    add_transaction(user_id, 'daily_bonus', bonus_amount, f"Ежедневный бонус (серия: {new_streak} дней)")
    
    message = f"{EMOJIS['gift']} Ежедневный бонус!\n"
    message += f"Вы получили {bonus_amount} {BONUS_COINS}\n"
    message += f"🔥 Серия: {new_streak} дней!\n"
    
    if new_streak >= 7:
        message += f"Вы в огне! Продолжайте в том же духе! 🔥"
    
    return bonus_amount, message

# ========== ОСНОВНЫЕ КОМАНДЫ ==========
@bot.message_handler(commands=['start'])
@log_command
def start_command(message):
    """Обработчик команды /start"""
    user_id = message.from_user.id
    username = message.from_user.username
    first_name = message.from_user.first_name
    last_name = message.from_user.last_name
    
    # Проверяем реферальный код
    referrer_id = None
    if len(message.text.split()) > 1:
        try:
            referrer_code = message.text.split()[1]
            # Декодируем реферальный код
            referrer_id = decode_referral_code(referrer_code)
        except:
            pass
    
    # Добавляем пользователя
    is_new = add_or_update_user(user_id, username, first_name, last_name, referrer_id)
    
    # Создаем клавиатуру
    markup = create_main_keyboard(user_id)
    
    # Приветственное сообщение
    welcome_text = f"{EMOJIS['heart']} Добро пожаловать, {first_name}!\n\n"
    welcome_text += "Я бот компании **NSP Goods**! 🍃\n\n"
    welcome_text += "Я помогу вам:\n"
    welcome_text += "✓ Найти и заказать качественные БАДы\n"
    welcome_text += "✓ Получить консультацию специалиста\n"
    welcome_text += "✓ Участвовать в акциях и получать бонусы\n"
    welcome_text += "✓ Отслеживать заказы\n\n"
    
    if is_new:
        welcome_text += f"{EMOJIS['gift']} В подарок вы получили **100 бонусных монет**!\n"
        welcome_text += f"{EMOJIS['info']} Введите /help чтобы узнать о всех возможностях бота"
    else:
        welcome_text += f"{EMOJIS['info']} Рады снова вас видеть! Используйте /help для помощи"
    
    bot.send_message(user_id, welcome_text, parse_mode="Markdown", reply_markup=markup)
    
    # Отправляем приветствие админам о новом пользователе
    if is_new:
        for admin in ADMINS:
            bot.send_message(admin, f"{EMOJIS['user']} Новый пользователь!\n"
                                   f"Имя: {first_name}\n"
                                   f"Username: @{username or 'нет'}\n"
                                   f"ID: {user_id}")

def create_main_keyboard(user_id):
    """Создание главной клавиатуры"""
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    
    buttons = [
        types.KeyboardButton(f"{EMOJIS['shop']} Каталог"),
        types.KeyboardButton(f"{EMOJIS['star']} Акции"),
        types.KeyboardButton(f"{EMOJIS['user']} Профиль"),
        types.KeyboardButton(f"{EMOJIS['coins']} Бонусы"),
        types.KeyboardButton(f"{EMOJIS['chart']} Статистика"),
        types.KeyboardButton(f"{EMOJIS['help']} Помощь"),
        types.KeyboardButton(f"{EMOJIS['settings']} Настройки")
    ]
    
    # Проверяем является ли админом
    if is_admin(user_id):
        buttons.append(types.KeyboardButton(f"{EMOJIS['admin']} Админ панель"))
    
    markup.add(*buttons)
    return markup

def decode_referral_code(code):
    """Декодирование реферального кода"""
    try:
        # Простое декодирование - в реальном проекте используйте шифрование
        import base64
        decoded = base64.b64decode(code.encode()).decode()
        user_id = int(decoded.split(':')[1])
        return user_id
    except:
        return None

def encode_referral_code(user_id):
    """Кодирование реферального кода"""
    import base64
    code_string = f"ref:{user_id}:{int(time.time())}"
    return base64.b64encode(code_string.encode()).decode()

# ========== ПРОФИЛЬ ПОЛЬЗОВАТЕЛЯ ==========
@bot.message_handler(func=lambda message: message.text == f"{EMOJIS['user']} Профиль" or message.text == "/profile")
@user_exists
@log_command
def profile_command(message):
    """Показать профиль пользователя"""
    user_id = message.from_user.id
    user_data = get_user_full_data(user_id)
    
    if not user_data:
        bot.send_message(user_id, f"{EMOJIS['error']} Ошибка получения данных")
        return
    
    profile_text = f"{EMOJIS['user']} **Ваш профиль**\n\n"
    profile_text += f"**Имя:** {user_data['first_name']}\n"
    if user_data['username']:
        profile_text += f"**Username:** @{user_data['username']}\n"
    profile_text += f"**Уровень:** {user_data['level']} {get_level_icon(user_data['level'])}\n"
    profile_text += f"**Опыт:** {user_data['experience']}/{get_next_level_exp(user_data['level'])}\n"
    profile_text += f"**Баланс:** {user_data['balance']} {BONUS_COINS}\n"
    profile_text += f"**Баллы лояльности:** {user_data['loyalty_points']}\n"
    profile_text += f"**Рефералов:** {user_data['referrals_count']}\n"
    profile_text += f"**Покупок:** {user_data['total_purchases']}\n"
    profile_text += f"**Потрачено:** {user_data['total_spent']} монет\n"
    profile_text += f"**Серия дней:** {user_data['daily_streak']} 🔥\n"
    profile_text += f"**Дата регистрации:** {user_data['registration_date'].strftime('%d.%m.%Y')}\n"
    
    if user_data['is_premium']:
        premium_until = datetime.fromisoformat(user_data['premium_until']) if user_data['premium_until'] else None
        if premium_until and premium_until > datetime.now():
            profile_text += f"{EMOJIS['crown']} **Premium** до {premium_until.strftime('%d.%m.%Y')}\n"
    
    # Создаем клавиатуру для профиля
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton(f"{EMOJIS['chart']} Статистика", callback_data="profile_stats"),
        types.InlineKeyboardButton(f"{EMOJIS['gift']} Достижения", callback_data="profile_achievements"),
        types.InlineKeyboardButton(f"{EMOJIS['settings']} Редактировать", callback_data="profile_edit"),
        types.InlineKeyboardButton(f"{EMOJIS['mail']} Реферальная ссылка", callback_data="profile_referral")
    )
    
    # Прогресс-бар опыта
    exp_percent = (user_data['experience'] / get_next_level_exp(user_data['level'])) * 100
    progress_bar = create_progress_bar(exp_percent)
    profile_text += f"\n**Прогресс до следующего уровня:**\n{progress_bar} {exp_percent:.1f}%"
    
    bot.send_message(user_id, profile_text, parse_mode="Markdown", reply_markup=markup)

def get_user_full_data(user_id):
    """Получить полные данные пользователя"""
    result = db.execute_query('''
        SELECT first_name, username, level, experience, balance, loyalty_points, 
               total_purchases, total_spent, daily_streak, registration_date, 
               is_premium, premium_until
        FROM users WHERE user_id = ?
    ''', (user_id,))
    
    if not result:
        return None
    
    data = result[0]
    referrals_count = db.execute_query("SELECT COUNT(*) FROM referrals WHERE referrer_id = ?", (user_id,))[0][0]
    
    return {
        'first_name': data[0],
        'username': data[1],
        'level': data[2],
        'experience': data[3],
        'balance': data[4],
        'loyalty_points': data[5],
        'total_purchases': data[6],
        'total_spent': data[7],
        'daily_streak': data[8],
        'registration_date': datetime.fromisoformat(data[9]) if isinstance(data[9], str) else data[9],
        'is_premium': bool(data[10]),
        'premium_until': data[11],
        'referrals_count': referrals_count
    }

def get_next_level_exp(current_level):
    """Получить опыт для следующего уровня"""
    result = db.execute_query("SELECT experience_needed FROM level_requirements WHERE level = ?", (current_level + 1,))
    if result:
        return result[0][0]
    return current_level * 100

def get_level_icon(level):
    """Получить иконку для уровня"""
    if level >= 100:
        return "🏆"
    elif level >= 50:
        return "💎"
    elif level >= 25:
        return "⭐"
    elif level >= 10:
        return "🌟"
    elif level >= 5:
        return "✨"
    else:
        return "🌱"

def create_progress_bar(percent, length=20):
    """Создать прогресс-бар"""
    filled = int(length * percent / 100)
    empty = length - filled
    return "█" * filled + "░" * empty

# ========== ДОСТИЖЕНИЯ ==========
@bot.callback_query_handler(func=lambda call: call.data == "profile_achievements")
def show_achievements(call):
    """Показать достижения пользователя"""
    user_id = call.from_user.id
    
    # Получаем все достижения пользователя
    user_achievements = db.execute_query('''
        SELECT achievement_id, unlocked_date FROM user_achievements WHERE user_id = ?
    ''', (user_id,))
    
    user_achievements_dict = {ach[0]: datetime.fromisoformat(ach[1]) if isinstance(ach[1], str) else ach[1] 
                              for ach in user_achievements}
    
    # Создаем текст
    text = f"{EMOJIS['trophy']} **Ваши достижения**\n\n"
    
    total_points = 0
    unlocked_count = 0
    
    for ach_id, ach_data in ACHIEVEMENTS.items():
        if ach_id in user_achievements_dict:
            unlocked_count += 1
            total_points += ach_data['points']
            status = f"{EMOJIS['check']} Получено"
            icon = ach_data['icon']
        else:
            status = f"{EMOJIS['error']} Не получено"
            icon = "❓"
        
        text += f"{icon} **{ach_data['name']}**\n"
        text += f"   {ach_data['description']}\n"
        text += f"   {status} | +{ach_data['points']} баллов\n\n"
    
    text += f"\n**Всего получено:** {unlocked_count}/{len(ACHIEVEMENTS)}\n"
    text += f"**Всего баллов:** {total_points}"
    
    bot.edit_message_text(text, call.message.chat.id, call.message.message_id, parse_mode="Markdown")

# ========== РЕФЕРАЛЬНАЯ СИСТЕМА ==========
@bot.callback_query_handler(func=lambda call: call.data == "profile_referral")
def show_referral_info(call):
    """Показать реферальную информацию"""
    user_id = call.from_user.id
    
    # Получаем количество рефералов
    referrals_count = db.execute_query("SELECT COUNT(*) FROM referrals WHERE referrer_id = ?", (user_id,))[0][0]
    
    # Получаем сумму бонусов
    total_bonus = db.execute_query("SELECT SUM(reward_amount) FROM referrals WHERE referrer_id = ?", (user_id,))[0][0] or 0
    
    # Последние рефералы
    recent_refs = db.execute_query('''
        SELECT u.first_name, u.username, r.timestamp
        FROM referrals r
        JOIN users u ON r.referred_id = u.user_id
        WHERE r.referrer_id = ?
        ORDER BY r.timestamp DESC
        LIMIT 5
    ''', (user_id,))
    
    # Создаем реферальный код
    ref_code = encode_referral_code(user_id)
    ref_link = f"https://t.me/{bot.get_me().username}?start={ref_code}"
    
    text = f"{EMOJIS['users']} **Реферальная программа**\n\n"
    text += f"**Ваша статистика:**\n"
    text += f"• Приглашено друзей: {referrals_count}\n"
    text += f"• Заработано бонусов: {total_bonus} {BONUS_COINS}\n\n"
    
    text += f"**Как это работает:**\n"
    text += f"1️⃣ Отправьте другу вашу реферальную ссылку\n"
    text += f"2️⃣ Друг переходит по ссылке и регистрируется\n"
    text += f"3️⃣ Вы получаете {REFERRAL_BONUS} {BONUS_COINS} бонусом!\n"
    text += f"4️⃣ Друг получает {REFERRAL_BONUS} {BONUS_COINS} на счет!\n\n"
    
    text += f"**Ваша реферальная ссылка:**\n"
    text += f"`{ref_link}`\n\n"
    
    if recent_refs:
        text += f"**Последние приглашенные:**\n"
        for ref in recent_refs:
            date = ref[2].strftime('%d.%m.%Y') if hasattr(ref[2], 'strftime') else ref[2][:10]
            text += f"• {ref[0]} (@{ref[1] or 'нет'}) - {date}\n"
    
    # Создаем клавиатуру
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(f"{EMOJIS['mail']} Поделиться ссылкой", callback_data="share_referral"))
    markup.add(types.InlineKeyboardButton(f"{EMOJIS['chart']} Полная статистика", callback_data="referral_stats"))
    
    bot.edit_message_text(text, call.message.chat.id, call.message.message_id, 
                         parse_mode="Markdown", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "share_referral")
def share_referral(call):
    """Поделиться реферальной ссылкой"""
    user_id = call.from_user.id
    ref_code = encode_referral_code(user_id)
    ref_link = f"https://t.me/{bot.get_me().username}?start={ref_code}"
    
    text = f"🎁 Привет! Я нашел отличного бота с БАДами!\n"
    text += f"Переходи по ссылке и получи бонус: {ref_link}"
    
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(f"{EMOJIS['mail']} Отправить другу", switch_inline_query=text))
    
    bot.answer_callback_query(call.id, "Ссылка скопирована!")
    bot.send_message(call.message.chat.id, f"{EMOJIS['check']} Ваша реферальная ссылка:\n`{ref_link}`", 
                    parse_mode="Markdown", reply_markup=markup)

# ========== ЕЖЕДНЕВНЫЙ БОНУС ==========
@bot.message_handler(func=lambda message: message.text == f"{EMOJIS['coins']} Бонусы" or message.text == "/bonus")
@user_exists
@log_command
def bonus_command(message):
    """Показать информацию о бонусах"""
    user_id = message.from_user.id
    
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton(f"{EMOJIS['gift']} Забрать бонус", callback_data="claim_daily_bonus"),
        types.InlineKeyboardButton(f"{EMOJIS['chart']} История бонусов", callback_data="bonus_history"),
        types.InlineKeyboardButton(f"{EMOJIS['info']} Как заработать", callback_data="bonus_info")
    )
    
    # Получаем текущую серию
    user_data = db.execute_query("SELECT daily_streak FROM users WHERE user_id = ?", (user_id,))[0]
    current_streak = user_data[0]
    
    # Следующий бонус
    next_bonus = DAILY_BONUS + (current_streak * 5)
    next_bonus = min(next_bonus, 500)
    
    text = f"{EMOJIS['gift']} **Бонусная система**\n\n"
    text += f"**Ежедневный бонус:**\n"
    text += f"• Сегодня вы можете получить {next_bonus} {BONUS_COINS}\n"
    text += f"• Текущая серия: {current_streak} дней 🔥\n\n"
    
    text += f"**Как получить больше бонусов:**\n"
    text += f"• Приглашайте друзей: +{REFERRAL_BONUS} {BONUS_COINS}\n"
    text += f"• Выполняйте задания: до 200 {BONUS_COINS}\n"
    text += f"• Повышайте уровень: бонус за каждый уровень\n"
    text += f"• Покупайте товары: кешбек 5%\n"
    text += f"• Участвуйте в акциях: двойные бонусы\n\n"
    
    text += f"**Ваш баланс:** {get_user_balance(user_id)} {BONUS_COINS}"
    
    bot.send_message(user_id, text, parse_mode="Markdown", reply_markup=markup)

def get_user_balance(user_id):
    """Получить баланс пользователя"""
    result = db.execute_query("SELECT balance FROM users WHERE user_id = ?", (user_id,))
    if result:
        return result[0][0]
    return 0

@bot.callback_query_handler(func=lambda call: call.data == "claim_daily_bonus")
def claim_daily_bonus(call):
    """Забрать ежедневный бонус"""
    user_id = call.from_user.id
    
    bonus_amount, message_text = get_daily_bonus(user_id)
    
    if bonus_amount is None:
        bot.answer_callback_query(call.id, message_text, show_alert=True)
        return
    
    bot.answer_callback_query(call.id, f"Вы получили {bonus_amount} монет!")
    bot.edit_message_text(message_text, call.message.chat.id, call.message.message_id, parse_mode="Markdown")

# ========== ЗАДАНИЯ И КВЕСТЫ ==========
@bot.message_handler(commands=['tasks'])
@user_exists
@log_command
def tasks_command(message):
    """Показать доступные задания"""
    user_id = message.from_user.id
    
    # Получаем выполненные задания
    completed_tasks = db.execute_query(
        "SELECT task_id FROM completed_tasks WHERE user_id = ?",
        (user_id,)
    )
    completed_ids = [ct[0] for ct in completed_tasks]
    
    text = f"{EMOJIS['star']} **Ежедневные задания**\n\n"
    
    for task_id, task in DAILY_TASKS.items():
        status = f"{EMOJIS['check']} Выполнено" if task_id in completed_ids else f"{EMOJIS['warning']} Не выполнено"
        text += f"**{task['name']}**\n"
        text += f"{task['description']}\n"
        text += f"Награда: {task['reward']} {BONUS_COINS}\n"
        text += f"Статус: {status}\n\n"
    
    # Создаем клавиатуру
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(f"{EMOJIS['gift']} Выполнить задание", callback_data="do_task"))
    markup.add(types.InlineKeyboardButton(f"{EMOJIS['chart']} Моя статистика", callback_data="task_stats"))
    
    bot.send_message(user_id, text, parse_mode="Markdown", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "do_task")
def do_task_menu(call):
    """Меню выбора задания"""
    markup = types.InlineKeyboardMarkup(row_width=1)
    
    for task_id, task in DAILY_TASKS.items():
        markup.add(types.InlineKeyboardButton(
            f"{task['name']} (+{task['reward']})",
            callback_data=f"complete_task_{task_id}"
        ))
    
    markup.add(types.InlineKeyboardButton(f"{EMOJIS['error']} Назад", callback_data="back_to_tasks"))
    
    bot.edit_message_text(f"{EMOJIS['star']} Выберите задание для выполнения:",
                          call.message.chat.id, call.message.message_id,
                          reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("complete_task_"))
def complete_task(call):
    """Выполнить задание"""
    user_id = call.from_user.id
    task_id = call.data.replace("complete_task_", "")
    
    # Проверяем не выполнено ли уже
    completed = db.execute_query(
        "SELECT 1 FROM completed_tasks WHERE user_id = ? AND task_id = ?",
        (user_id, task_id)
    )
    
    if completed:
        bot.answer_callback_query(call.id, "Вы уже выполнили это задание сегодня!", show_alert=True)
        return
    
    task = DAILY_TASKS.get(task_id)
    if not task:
        bot.answer_callback_query(call.id, "Задание не найдено!")
        return
    
    # Проверяем условия задания
    can_complete, message = check_task_completion(user_id, task_id)
    
    if not can_complete:
        bot.answer_callback_query(call.id, message, show_alert=True)
        return
    
    # Выполняем задание
    db.execute_query('''
        INSERT INTO completed_tasks (user_id, task_id, completed_date, reward_claimed)
        VALUES (?, ?, ?, 1)
    ''', (user_id, task_id, datetime.now()))
    
    # Начисляем награду
    db.execute_query(
        "UPDATE users SET balance = balance + ? WHERE user_id = ?",
        (task['reward'], user_id)
    )
    
    # Добавляем транзакцию
    add_transaction(user_id, 'task', task['reward'], f"Выполнено задание: {task['name']}")
    
    bot.answer_callback_query(call.id, f"Задание выполнено! Вы получили {task['reward']} монет!")
    bot.send_message(user_id, f"{EMOJIS['check']} Поздравляю! Задание '{task['name']}' выполнено!\n"
                              f"Вы получили {task['reward']} {BONUS_COINS}!")

def check_task_completion(user_id, task_id):
    """Проверить можно ли выполнить задание"""
    if task_id == 'daily_visit':
        return True, "Просто зайдите в бота!"
    
    elif task_id == 'share_contact':
        # Проверяем есть ли номер телефона
        phone = db.execute_query("SELECT phone_number FROM users WHERE user_id = ?", (user_id,))
        if phone and phone[0][0]:
            return True, "Номер уже есть!"
        return False, "Поделитесь номером телефона через /phone"
    
    elif task_id == 'invite_friend':
        # Проверяем рефералов за сегодня
        today = datetime.now().date()
        referrals_today = db.execute_query('''
            SELECT COUNT(*) FROM referrals 
            WHERE referrer_id = ? AND date(timestamp) = ?
        ''', (user_id, today))
        return referrals_today[0][0] > 0, "Пригласите друга сегодня!"
    
    elif task_id == 'rate_bot':
        # Проверяем оценку
        rating = db.execute_query("SELECT 1 FROM feedback WHERE user_id = ? AND date(timestamp) = date('now')", (user_id,))
        return len(rating) > 0, "Оцените бота через /rate"
    
    elif task_id == 'make_purchase':
        # Проверяем покупки за сегодня
        purchases_today = db.execute_query('''
            SELECT COUNT(*) FROM purchases 
            WHERE user_id = ? AND date(timestamp) = date('now')
        ''', (user_id,))
        return purchases_today[0][0] > 0, "Совершите покупку сегодня!"
    
    return False, "Задание временно недоступно"

# ========== МАГАЗИН И ТОВАРЫ ==========
@bot.message_handler(func=lambda message: message.text == f"{EMOJIS['shop']} Каталог" or message.text == "/shop")
@user_exists
@log_command
def shop_command(message):
    """Показать каталог товаров"""
    user_id = message.from_user.id
    
    # Создаем категории товаров
    categories = {
        'vitamins': 'Витамины и минералы',
        'omega': 'Омега-3 и жирные кислоты',
        'probiotics': 'Пробиотики и пищеварение',
        'special': 'Специализированные БАДы'
    }
    
    markup = types.InlineKeyboardMarkup(row_width=2)
    
    for cat_id, cat_name in categories.items():
        markup.add(types.InlineKeyboardButton(f"📦 {cat_name}", callback_data=f"category_{cat_id}"))
    
    markup.add(types.InlineKeyboardButton(f"{EMOJIS['cart']} Корзина", callback_data="view_cart"))
    markup.add(types.InlineKeyboardButton(f"{EMOJIS['coupon']} Промокоды", callback_data="promocodes"))
    
    bot.send_message(user_id, f"{EMOJIS['shop']} **Добро пожаловать в магазин!**\n\n"
                              f"Выберите категорию товаров:",
                    parse_mode="Markdown", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("category_"))
def show_category(call):
    """Показать товары категории"""
    category = call.data.replace("category_", "")
    
    # Фильтруем товары по категории
    category_products = {
        'vitamins': ['vitamin_c', 'vitamin_d', 'zinc', 'magnesium', 'b_complex'],
        'omega': ['omega_3'],
        'probiotics': ['probiotics', 'collagen'],
        'special': ['collagen']
    }
    
    products_in_category = category_products.get(category, [])
    
    text = f"{EMOJIS['shop']} **Товары в категории:**\n\n"
    markup = types.InlineKeyboardMarkup(row_width=1)
    
    for product_id in products_in_category:
        product = PRODUCTS.get(product_id)
        if product:
            text += f"**{product['name']}**\n"
            text += f"{product['description']}\n"
            text += f"💰 Цена: {product['price']} {BONUS_COINS}\n"
            text += f"📦 В наличии: {product['stock']} шт.\n\n"
            
            markup.add(types.InlineKeyboardButton(
                f"🛒 Купить {product['name']}",
                callback_data=f"buy_{product_id}"
            ))
    
    markup.add(types.InlineKeyboardButton(f"{EMOJIS['error']} Назад", callback_data="back_to_shop"))
    
    bot.edit_message_text(text, call.message.chat.id, call.message.message_id,
                         parse_mode="Markdown", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("buy_"))
def buy_product(call):
    """Покупка товара"""
    user_id = call.from_user.id
    product_id = call.data.replace("buy_", "")
    
    product = PRODUCTS.get(product_id)
    if not product:
        bot.answer_callback_query(call.id, "Товар не найден!")
        return
    
    if product['stock'] <= 0:
        bot.answer_callback_query(call.id, "Товар временно отсутствует!", show_alert=True)
        return
    
    # Запрашиваем количество
    user_temp_data[user_id] = {'buying': product_id}
    
    markup = types.InlineKeyboardMarkup(row_width=3)
    for qty in [1, 2, 3, 5, 10]:
        markup.add(types.InlineKeyboardButton(str(qty), callback_data=f"qty_{qty}"))
    markup.add(types.InlineKeyboardButton(f"{EMOJIS['error']} Отмена", callback_data="cancel_buy"))
    
    bot.edit_message_text(f"{EMOJIS['shop']} **{product['name']}**\n"
                          f"Цена: {product['price']} {BONUS_COINS}\n\n"
                          f"Выберите количество:",
                          call.message.chat.id, call.message.message_id,
                          parse_mode="Markdown", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("qty_"))
def set_quantity(call):
    """Установить количество товара"""
    user_id = call.from_user.id
    quantity = int(call.data.replace("qty_", ""))
    
    if user_id not in user_temp_data or 'buying' not in user_temp_data[user_id]:
        bot.answer_callback_query(call.id, "Ошибка! Попробуйте снова.")
        return
    
    product_id = user_temp_data[user_id]['buying']
    product = PRODUCTS.get(product_id)
    
    if not product:
        bot.answer_callback_query(call.id, "Товар не найден!")
        return
    
    if quantity > product['stock']:
        bot.answer_callback_query(call.id, f"Доступно только {product['stock']} шт!", show_alert=True)
        return
    
    total_price = product['price'] * quantity
    user_balance = get_user_balance(user_id)
    
    if user_balance < total_price:
        bot.answer_callback_query(call.id, f"Недостаточно средств! Нужно {total_price} монет", show_alert=True)
        return
    
    # Подтверждение покупки
    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton(f"{EMOJIS['check']} Подтвердить", callback_data=f"confirm_{product_id}_{quantity}"),
        types.InlineKeyboardButton(f"{EMOJIS['error']} Отмена", callback_data="cancel_buy")
    )
    
    bot.edit_message_text(f"{EMOJIS['shop']} **Подтверждение покупки**\n\n"
                          f"Товар: {product['name']}\n"
                          f"Количество: {quantity} шт.\n"
                          f"Сумма: {total_price} {BONUS_COINS}\n"
                          f"Ваш баланс: {user_balance} {BONUS_COINS}\n\n"
                          f"Подтверждаете покупку?",
                          call.message.chat.id, call.message.message_id,
                          parse_mode="Markdown", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("confirm_"))
def confirm_purchase(call):
    """Подтверждение покупки"""
    user_id = call.from_user.id
    _, product_id, quantity = call.data.split("_")
    quantity = int(quantity)
    
    product = PRODUCTS.get(product_id)
    if not product:
        bot.answer_callback_query(call.id, "Ошибка!")
        return
    
    total_price = product['price'] * quantity
    user_balance = get_user_balance(user_id)
    
    if user_balance < total_price:
        bot.answer_callback_query(call.id, "Недостаточно средств!", show_alert=True)
        return
    
    if product['stock'] < quantity:
        bot.answer_callback_query(call.id, "Товара нет в наличии!", show_alert=True)
        return
    
    # Списываем средства
    db.execute_query(
        "UPDATE users SET balance = balance - ?, total_spent = total_spent + ?, total_purchases = total_purchases + ? WHERE user_id = ?",
        (total_price, total_price, quantity, user_id)
    )
    
    # Обновляем склад
    PRODUCTS[product_id]['stock'] -= quantity
    
    # Записываем покупку
    db.execute_query('''
        INSERT INTO purchases (user_id, product_id, quantity, price, total_amount, timestamp, status)
        VALUES (?, ?, ?, ?, ?, ?, 'completed')
    ''', (user_id, product_id, quantity, product['price'], total_price, datetime.now()))
    
    # Добавляем транзакцию
    add_transaction(user_id, 'purchase', -total_price, f"Покупка: {product['name']} x{quantity}")
    
    # Начисляем кешбек (5%)
    cashback = int(total_price * 0.05)
    if cashback > 0:
        db.execute_query(
            "UPDATE users SET balance = balance + ? WHERE user_id = ?",
            (cashback, user_id)
        )
        add_transaction(user_id, 'cashback', cashback, f"Кешбек за покупку {product['name']}")
    
    # Очищаем временные данные
    if user_id in user_temp_data:
        del user_temp_data[user_id]
    
    # Проверяем достижения
    check_achievements(user_id)
    
    bot.answer_callback_query(call.id, f"Покупка совершена! Вы получили {cashback} кешбек!")
    bot.edit_message_text(f"{EMOJIS['check']} **Покупка успешно совершена!**\n\n"
                          f"Товар: {product['name']}\n"
                          f"Количество: {quantity} шт.\n"
                          f"Сумма: {total_price} {BONUS_COINS}\n"
                          f"Кешбек: +{cashback} {BONUS_COINS}\n"
                          f"Новый баланс: {get_user_balance(user_id)} {BONUS_COINS}\n\n"
                          f"Спасибо за покупку!",
                          call.message.chat.id, call.message.message_id,
                          parse_mode="Markdown")

# ========== СТАТИСТИКА И АНАЛИТИКА ==========
@bot.message_handler(commands=['stats'])
@admin_required
@log_command
def stats_command(message):
    """Показать общую статистику бота"""
    # Получаем общую статистику из БД
    total_users = db.execute_query("SELECT COUNT(*) FROM users")[0][0]
    active_today = db.execute_query("SELECT COUNT(*) FROM users WHERE date(last_active) = date('now')")[0][0]
    active_week = db.execute_query("SELECT COUNT(*) FROM users WHERE last_active >= datetime('now', '-7 days')")[0][0]
    active_month = db.execute_query("SELECT COUNT(*) FROM users WHERE last_active >= datetime('now', '-30 days')")[0][0]
    
    new_today = db.execute_query("SELECT COUNT(*) FROM users WHERE date(registration_date) = date('now')")[0][0]
    new_week = db.execute_query("SELECT COUNT(*) FROM users WHERE registration_date >= datetime('now', '-7 days')")[0][0]
    new_month = db.execute_query("SELECT COUNT(*) FROM users WHERE registration_date >= datetime('now', '-30 days')")[0][0]
    
    total_purchases = db.execute_query("SELECT COUNT(*) FROM purchases")[0][0]
    total_revenue = db.execute_query("SELECT SUM(total_amount) FROM purchases WHERE status = 'completed'")[0][0] or 0
    total_referrals = db.execute_query("SELECT COUNT(*) FROM referrals")[0][0]
    
    total_balance = db.execute_query("SELECT SUM(balance) FROM users")[0][0] or 0
    level_100_plus = db.execute_query("SELECT COUNT(*) FROM users WHERE level >= 100")[0][0]
    
    # Создаем график
    img = create_stats_chart()
    
    text = f"📊 **СТАТИСТИКА БОТА**\n\n"
    text += f"👥 **Пользователи:**\n"
    text += f"   • Всего: {total_users}\n"
    text += f"   • За сегодня: +{new_today}\n"
    text += f"   • За неделю: +{new_week}\n"
    text += f"   • За месяц: +{new_month}\n\n"
    
    text += f"✅ **Активность:**\n"
    text += f"   • Сегодня: {active_today}\n"
    text += f"   • За неделю: {active_week}\n"
    text += f"   • За месяц: {active_month}\n\n"
    
    text += f"💰 **Экономика:**\n"
    text += f"   • Всего покупок: {total_purchases}\n"
    text += f"   • Выручка: {total_revenue} монет\n"
    text += f"   • Баланс пользователей: {total_balance} монет\n"
    text += f"   • Реферальных связей: {total_referrals}\n\n"
    
    text += f"🏆 **Достижения:**\n"
    text += f"   • Пользователей 100+ уровня: {level_100_plus}\n"
    
    # Отправляем с графиком
    if img:
        bot.send_photo(message.chat.id, img, caption=text, parse_mode="Markdown")
    else:
        bot.send_message(message.chat.id, text, parse_mode="Markdown")

def create_stats_chart():
    """Создать график статистики"""
    try:
        # Получаем данные за последние 7 дней
        daily_users = []
        dates = []
        
        for i in range(7):
            date = (datetime.now() - timedelta(days=i)).date()
            count = db.execute_query(
                "SELECT COUNT(*) FROM users WHERE date(registration_date) = ?",
                (date,)
            )[0][0]
            daily_users.append(count)
            dates.append(date.strftime("%d.%m"))
        
        daily_users.reverse()
        dates.reverse()
        
        # Создаем график
        plt.figure(figsize=(10, 6))
        plt.plot(dates, daily_users, marker='o', linewidth=2, markersize=8)
        plt.title('Новые пользователи по дням', fontsize=16, fontweight='bold')
        plt.xlabel('Дата', fontsize=12)
        plt.ylabel('Количество пользователей', fontsize=12)
        plt.grid(True, alpha=0.3)
        plt.xticks(rotation=45)
        
        # Сохраняем в буфер
        buffer = BytesIO()
        plt.savefig(buffer, format='png', bbox_inches='tight', dpi=100)
        buffer.seek(0)
        plt.close()
        
        return buffer
    except Exception as e:
        logger.error(f"Error creating chart: {e}")
        return None

# ========== ПОДДЕРЖКА И ОБРАТНАЯ СВЯЗЬ ==========
@bot.message_handler(commands=['support'])
@user_exists
@log_command
def support_command(message):
    """Создать обращение в поддержку"""
    user_id = message.from_user.id
    
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton(f"{EMOJIS['mail']} Создать обращение", callback_data="new_ticket"),
        types.InlineKeyboardButton(f"{EMOJIS['chart']} Мои обращения", callback_data="my_tickets"),
        types.InlineKeyboardButton(f"{EMOJIS['star']} FAQ", callback_data="faq")
    )
    
    bot.send_message(user_id, f"{EMOJIS['help']} **Служба поддержки**\n\n"
                              f"Выберите действие:",
                    parse_mode="Markdown", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "new_ticket")
def new_ticket(call):
    """Создание нового обращения"""
    user_id = call.from_user.id
    
    msg = bot.send_message(call.message.chat.id, 
                          f"{EMOJIS['mail']} Опишите вашу проблему или вопрос.\n"
                          f"Напишите подробно, чтобы мы могли вам помочь.\n\n"
                          f"Для отмены отправьте /cancel")
    
    user_states[user_id] = {'state': 'waiting_ticket_text', 'message_id': msg.message_id}

@bot.message_handler(func=lambda message: user_states.get(message.from_user.id, {}).get('state') == 'waiting_ticket_text')
def process_ticket_text(message):
    """Обработка текста обращения"""
    user_id = message.from_user.id
    ticket_text = message.text
    
    if ticket_text == '/cancel':
        del user_states[user_id]
        bot.send_message(user_id, f"{EMOJIS['error']} Создание обращения отменено")
        return
    
    # Сохраняем обращение
    ticket_id = db.execute_insert('''
        INSERT INTO support_tickets (user_id, subject, message, status, created_date, updated_date)
        VALUES (?, ?, ?, 'open', ?, ?)
    ''', (user_id, ticket_text[:50], ticket_text, datetime.now(), datetime.now()))
    
    # Уведомляем пользователя
    bot.send_message(user_id, f"{EMOJIS['check']} Ваше обращение #{ticket_id} создано!\n"
                              f"Мы ответим вам в ближайшее время.")
    
    # Уведомляем админов
    for admin in ADMINS:
        markup = types.InlineKeyboardMarkup()
        markup.add(
            types.InlineKeyboardButton("✏️ Ответить", callback_data=f"answer_ticket_{ticket_id}"),
            types.InlineKeyboardButton("✅ Закрыть", callback_data=f"close_ticket_{ticket_id}")
        )
        
        bot.send_message(admin, f"{EMOJIS['mail']} **Новое обращение #{ticket_id}**\n\n"
                               f"От: {message.from_user.first_name} (@{message.from_user.username or 'нет'})\n"
                               f"Текст: {ticket_text[:200]}\n"
                               f"ID: {user_id}",
                        parse_mode="Markdown", reply_markup=markup)
    
    del user_states[user_id]

# ========== ОПРОСЫ И ГОЛОСОВАНИЯ ==========
@bot.message_handler(commands=['poll'])
@admin_required
@log_command
def create_poll_command(message):
    """Создать новый опрос"""
    user_id = message.from_user.id
    
    msg = bot.send_message(user_id, f"{EMOJIS['chart']} Создание опроса.\n\n"
                                    f"Введите вопрос для опроса:")
    
    user_states[user_id] = {'state': 'poll_question', 'message_id': msg.message_id}

@bot.message_handler(func=lambda message: user_states.get(message.from_user.id, {}).get('state') == 'poll_question')
def poll_question(message):
    """Получение вопроса опроса"""
    user_id = message.from_user.id
    question = message.text
    
    user_states[user_id] = {'state': 'poll_options', 'question': question}
    
    bot.send_message(user_id, f"{EMOJIS['info']} Введите варианты ответов через запятую.\n"
                              f"Пример: Да,Нет,Возможно")

@bot.message_handler(func=lambda message: user_states.get(message.from_user.id, {}).get('state') == 'poll_options')
def poll_options(message):
    """Получение вариантов ответов"""
    user_id = message.from_user.id
    options_text = message.text
    
    options = [opt.strip() for opt in options_text.split(',')]
    
    if len(options) < 2:
        bot.send_message(user_id, f"{EMOJIS['error']} Нужно минимум 2 варианта ответа!")
        return
    
    if len(options) > 10:
        bot.send_message(user_id, f"{EMOJIS['error']} Максимум 10 вариантов!")
        return
    
    # Сохраняем опрос
    poll_id = db.execute_insert('''
        INSERT INTO polls (creator_id, question, options, votes, created_date, end_date, is_active)
        VALUES (?, ?, ?, ?, ?, ?, 1)
    ''', (user_id, user_states[user_id]['question'], json.dumps(options), json.dumps({}), 
          datetime.now(), datetime.now() + timedelta(days=7)))
    
    # Отправляем опрос
    send_poll_to_users(poll_id)
    
    bot.send_message(user_id, f"{EMOJIS['check']} Опрос создан и отправлен пользователям!")
    del user_states[user_id]

def send_poll_to_users(poll_id):
    """Отправить опрос всем пользователям"""
    poll_data = db.execute_query(
        "SELECT question, options FROM polls WHERE poll_id = ?",
        (poll_id,)
    )[0]
    
    question = poll_data[0]
    options = json.loads(poll_data[1])
    
    # Создаем клавиатуру для голосования
    markup = types.InlineKeyboardMarkup(row_width=2)
    for i, option in enumerate(options):
        markup.add(types.InlineKeyboardButton(option, callback_data=f"vote_{poll_id}_{i}"))
    
    # Получаем всех пользователей
    users = db.execute_query("SELECT user_id FROM users")
    
    for user in users:
        try:
            bot.send_message(user[0], f"{EMOJIS['chart']} **НОВЫЙ ОПРОС!**\n\n"
                                      f"❓ {question}\n\n"
                                      f"Проголосуйте, выбрав один из вариантов:",
                            parse_mode="Markdown", reply_markup=markup)
            time.sleep(0.05)
        except:
            continue

@bot.callback_query_handler(func=lambda call: call.data.startswith("vote_"))
def process_vote(call):
    """Обработка голоса"""
    user_id = call.from_user.id
    _, poll_id, option_index = call.data.split("_")
    poll_id = int(poll_id)
    option_index = int(option_index)
    
    # Проверяем активен ли опрос
    poll = db.execute_query(
        "SELECT is_active, options, votes FROM polls WHERE poll_id = ?",
        (poll_id,)
    )
    
    if not poll or not poll[0][0]:
        bot.answer_callback_query(call.id, "Этот опрос уже завершен!")
        return
    
    # Получаем текущие голоса
    votes = json.loads(poll[0][2])
    
    # Проверяем не голосовал ли уже
    if str(user_id) in votes:
        bot.answer_callback_query(call.id, "Вы уже голосовали в этом опросе!")
        return
    
    # Добавляем голос
    votes[str(user_id)] = option_index
    db.execute_query(
        "UPDATE polls SET votes = ? WHERE poll_id = ?",
        (json.dumps(votes), poll_id)
    )
    
    options = json.loads(poll[0][1])
    bot.answer_callback_query(call.id, f"Вы проголосовали за: {options[option_index]}")
    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)

# ========== АКЦИИ И ПРОМОКОДЫ ==========
@bot.message_handler(commands=['promo'])
@user_exists
@log_command
def promo_command(message):
    """Активировать промокод"""
    user_id = message.from_user.id
    
    msg = bot.send_message(user_id, f"{EMOJIS['coupon']} Введите промокод:")
    user_states[user_id] = {'state': 'waiting_promo', 'message_id': msg.message_id}

@bot.message_handler(func=lambda message: user_states.get(message.from_user.id, {}).get('state') == 'waiting_promo')
def process_promo(message):
    """Обработка промокода"""
    user_id = message.from_user.id
    promo_code = message.text.upper().strip()
    
    # Проверяем промокод
    coupon = db.execute_query('''
        SELECT discount_percent, valid_until, max_uses, used_count
        FROM coupons WHERE coupon_code = ?
    ''', (promo_code,))
    
    if not coupon:
        bot.send_message(user_id, f"{EMOJIS['error']} Промокод не найден!")
        del user_states[user_id]
        return
    
    discount, valid_until, max_uses, used_count = coupon[0]
    
    # Проверяем срок действия
    valid_date = datetime.fromisoformat(valid_until) if isinstance(valid_until, str) else valid_until
    if valid_date < datetime.now():
        bot.send_message(user_id, f"{EMOJIS['error']} Срок действия промокода истек!")
        del user_states[user_id]
        return
    
    # Проверяем лимит использований
    if max_uses and used_count >= max_uses:
        bot.send_message(user_id, f"{EMOJIS['error']} Промокод больше не действителен!")
        del user_states[user_id]
        return
    
    # Проверяем не использовал ли уже пользователь
    used = db.execute_query(
        "SELECT 1 FROM used_coupons WHERE user_id = ? AND coupon_code = ?",
        (user_id, promo_code)
    )
    
    if used:
        bot.send_message(user_id, f"{EMOJIS['error']} Вы уже использовали этот промокод!")
        del user_states[user_id]
        return
    
    # Активируем промокод
    db.execute_query('''
        INSERT INTO used_coupons (user_id, coupon_code, used_date)
        VALUES (?, ?, ?)
    ''', (user_id, promo_code, datetime.now()))
    
    db.execute_query(
        "UPDATE coupons SET used_count = used_count + 1 WHERE coupon_code = ?",
        (promo_code,)
    )
    
    # Начисляем бонус
    bonus_amount = discount
    db.execute_query(
        "UPDATE users SET balance = balance + ? WHERE user_id = ?",
        (bonus_amount, user_id)
    )
    
    add_transaction(user_id, 'promo', bonus_amount, f"Активация промокода {promo_code}")
    
    bot.send_message(user_id, f"{EMOJIS['check']} Промокод активирован!\n"
                              f"Вы получили {bonus_amount} {BONUS_COINS}!")
    
    del user_states[user_id]

@bot.message_handler(commands=['create_promo'])
@admin_required
@log_command
def create_promo_command(message):
    """Создать новый промокод"""
    user_id = message.from_user.id
    
    msg = bot.send_message(user_id, f"{EMOJIS['coupon']} Создание промокода.\n\n"
                                    f"Введите сумму бонуса (в монетах):")
    
    user_states[user_id] = {'state': 'promo_amount', 'message_id': msg.message_id}

@bot.message_handler(func=lambda message: user_states.get(message.from_user.id, {}).get('state') == 'promo_amount')
def promo_amount(message):
    """Получение суммы бонуса"""
    user_id = message.from_user.id
    
    try:
        amount = int(message.text)
        if amount <= 0:
            raise ValueError
    except:
        bot.send_message(user_id, f"{EMOJIS['error']} Введите корректное число!")
        return
    
    user_states[user_id]['amount'] = amount
    user_states[user_id]['state'] = 'promo_validity'
    
    bot.send_message(user_id, f"{EMOJIS['calendar']} Введите срок действия в днях:")

@bot.message_handler(func=lambda message: user_states.get(message.from_user.id, {}).get('state') == 'promo_validity')
def promo_validity(message):
    """Получение срока действия"""
    user_id = message.from_user.id
    
    try:
        days = int(message.text)
        if days <= 0:
            raise ValueError
    except:
        bot.send_message(user_id, f"{EMOJIS['error']} Введите корректное число дней!")
        return
    
    # Генерируем промокод
    promo_code = generate_promo_code()
    valid_until = datetime.now() + timedelta(days=days)
    
    # Сохраняем промокод
    db.execute_query('''
        INSERT INTO coupons (coupon_code, discount_percent, valid_until, max_uses, used_count, created_by)
        VALUES (?, ?, ?, ?, 0, ?)
    ''', (promo_code, user_states[user_id]['amount'], valid_until, None, user_id))
    
    bot.send_message(user_id, f"{EMOJIS['check']} Промокод создан!\n\n"
                              f"**Код:** `{promo_code}`\n"
                              f"**Бонус:** {user_states[user_id]['amount']} монет\n"
                              f"**Действителен до:** {valid_until.strftime('%d.%m.%Y')}\n\n"
                              f"Пользователи могут активировать его командой /promo",
                    parse_mode="Markdown")
    
    del user_states[user_id]

def generate_promo_code(length=8):
    """Сгенерировать случайный промокод"""
    letters = string.ascii_uppercase + string.digits
    return ''.join(random.choice(letters) for _ in range(length))

# ========== НАПОМИНАНИЯ ==========
@bot.message_handler(commands=['remind'])
@user_exists
@log_command
def remind_command(message):
    """Создать напоминание"""
    user_id = message.from_user.id
    
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton(f"{EMOJIS['calendar']} Новое напоминание", callback_data="new_reminder"),
        types.InlineKeyboardButton(f"{EMOJIS['chart']} Мои напоминания", callback_data="my_reminders")
    )
    
    bot.send_message(user_id, f"{EMOJIS['time']} **Напоминания**\n\n"
                              f"Напоминания помогут вам не забыть принять БАДы или другие важные дела.",
                    parse_mode="Markdown", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "new_reminder")
def new_reminder(call):
    """Создание нового напоминания"""
    user_id = call.from_user.id
    
    msg = bot.send_message(call.message.chat.id, f"{EMOJIS['calendar']} Введите название напоминания:")
    user_states[user_id] = {'state': 'reminder_title', 'message_id': msg.message_id}

@bot.message_handler(func=lambda message: user_states.get(message.from_user.id, {}).get('state') == 'reminder_title')
def reminder_title(message):
    """Получение названия напоминания"""
    user_id = message.from_user.id
    title = message.text
    
    user_states[user_id]['title'] = title
    user_states[user_id]['state'] = 'reminder_desc'
    
    bot.send_message(user_id, f"{EMOJIS['info']} Введите описание (или отправьте /skip):")

@bot.message_handler(func=lambda message: user_states.get(message.from_user.id, {}).get('state') == 'reminder_desc')
def reminder_desc(message):
    """Получение описания напоминания"""
    user_id = message.from_user.id
    
    if message.text == "/skip":
        description = ""
    else:
        description = message.text
    
    user_states[user_id]['description'] = description
    user_states[user_id]['state'] = 'reminder_date'
    
    bot.send_message(user_id, f"{EMOJIS['time']} Введите дату и время в формате:\n"
                              f"`ДД.ММ.ГГГГ ЧЧ:ММ`\n\n"
                              f"Пример: 25.12.2024 15:30",
                    parse_mode="Markdown")

@bot.message_handler(func=lambda message: user_states.get(message.from_user.id, {}).get('state') == 'reminder_date')
def reminder_date(message):
    """Получение даты напоминания"""
    user_id = message.from_user.id
    
    try:
        reminder_date = datetime.strptime(message.text, "%d.%m.%Y %H:%M")
        if reminder_date < datetime.now():
            bot.send_message(user_id, f"{EMOJIS['error']} Дата должна быть в будущем!")
            return
    except:
        bot.send_message(user_id, f"{EMOJIS['error']} Неверный формат! Используйте: ДД.ММ.ГГГГ ЧЧ:ММ")
        return
    
    # Сохраняем напоминание
    reminder_id = db.execute_insert('''
        INSERT INTO reminders (user_id, title, description, reminder_date, is_completed)
        VALUES (?, ?, ?, ?, 0)
    ''', (user_id, user_states[user_id]['title'], user_states[user_id].get('description', ''), reminder_date))
    
    # Планируем отправку
    scheduler.add_job(
        send_reminder,
        'date',
        run_date=reminder_date,
        args=[user_id, reminder_id, user_states[user_id]['title'], user_states[user_id].get('description', '')]
    )
    
    bot.send_message(user_id, f"{EMOJIS['check']} Напоминание создано!\n"
                              f"Я напомню вам {reminder_date.strftime('%d.%m.%Y в %H:%M')}")
    
    del user_states[user_id]

def send_reminder(user_id, reminder_id, title, description):
    """Отправить напоминание"""
    text = f"{EMOJIS['time']} **НАПОМИНАНИЕ!**\n\n"
    text += f"**{title}**\n"
    if description:
        text += f"{description}\n\n"
    text += f"Не забудьте выполнить!"
    
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(f"{EMOJIS['check']} Выполнено", callback_data=f"reminder_done_{reminder_id}"))
    
    bot.send_message(user_id, text, parse_mode="Markdown", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("reminder_done_"))
def reminder_done(call):
    """Отметить напоминание как выполненное"""
    reminder_id = int(call.data.replace("reminder_done_", ""))
    
    db.execute_query(
        "UPDATE reminders SET is_completed = 1 WHERE reminder_id = ?",
        (reminder_id,)
    )
    
    bot.answer_callback_query(call.id, "Напоминание отмечено как выполненное!")
    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)

# ========== ЗАМЕТКИ ==========
@bot.message_handler(commands=['notes'])
@user_exists
@log_command
def notes_command(message):
    """Работа с заметками"""
    user_id = message.from_user.id
    
    # Получаем заметки пользователя
    notes = db.execute_query('''
        SELECT note_id, title, content, created_date, is_pinned
        FROM notes WHERE user_id = ?
        ORDER BY is_pinned DESC, updated_date DESC
        LIMIT 10
    ''', (user_id,))
    
    if not notes:
        text = f"{EMOJIS['info']} У вас пока нет заметок.\n"
        text += f"Создайте новую заметку командой /new_note"
    else:
        text = f"{EMOJIS['info']} **Ваши заметки:**\n\n"
        for note in notes:
            pin_icon = "📌 " if note[4] else ""
            text += f"{pin_icon}**{note[1]}**\n"
            text += f"{note[2][:100]}...\n"
            text += f"📅 {note[3].strftime('%d.%m.%Y')}\n"
            text += f"🔗 /note_{note[0]}\n\n"
    
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(f"{EMOJIS['calendar']} Новая заметка", callback_data="new_note"))
    
    bot.send_message(user_id, text, parse_mode="Markdown", reply_markup=markup)

@bot.message_handler(commands=['new_note'])
@user_exists
@log_command
def new_note_command(message):
    """Создать новую заметку"""
    user_id = message.from_user.id
    
    msg = bot.send_message(user_id, f"{EMOJIS['calendar']} Введите заголовок заметки:")
    user_states[user_id] = {'state': 'note_title', 'message_id': msg.message_id}

@bot.message_handler(func=lambda message: user_states.get(message.from_user.id, {}).get('state') == 'note_title')
def note_title(message):
    """Получение заголовка заметки"""
    user_id = message.from_user.id
    title = message.text
    
    user_states[user_id]['title'] = title
    user_states[user_id]['state'] = 'note_content'
    
    bot.send_message(user_id, f"{EMOJIS['info']} Введите содержание заметки:")

@bot.message_handler(func=lambda message: user_states.get(message.from_user.id, {}).get('state') == 'note_content')
def note_content(message):
    """Получение содержания заметки"""
    user_id = message.from_user.id
    content = message.text
    
    # Сохраняем заметку
    note_id = db.execute_insert('''
        INSERT INTO notes (user_id, title, content, created_date, updated_date, is_pinned)
        VALUES (?, ?, ?, ?, ?, 0)
    ''', (user_id, user_states[user_id]['title'], content, datetime.now(), datetime.now()))
    
    bot.send_message(user_id, f"{EMOJIS['check']} Заметка создана!\n"
                              f"Просмотреть: /note_{note_id}")
    
    del user_states[user_id]

@bot.message_handler(func=lambda message: message.text.startswith('/note_'))
def view_note(message):
    """Просмотр заметки"""
    user_id = message.from_user.id
    note_id = int(message.text.replace('/note_', ''))
    
    note = db.execute_query('''
        SELECT title, content, created_date, updated_date, is_pinned
        FROM notes WHERE note_id = ? AND user_id = ?
    ''', (note_id, user_id))
    
    if not note:
        bot.send_message(user_id, f"{EMOJIS['error']} Заметка не найдена!")
        return
    
    pin_icon = "📌 " if note[0][4] else ""
    text = f"{pin_icon}**{note[0][0]}**\n\n"
    text += f"{note[0][1]}\n\n"
    text += f"📅 Создано: {note[0][2].strftime('%d.%m.%Y %H:%M')}\n"
    text += f"✏️ Обновлено: {note[0][3].strftime('%d.%m.%Y %H:%M')}"
    
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton(f"{EMOJIS['settings']} Редактировать", callback_data=f"edit_note_{note_id}"),
        types.InlineKeyboardButton(f"{EMOJIS['error']} Удалить", callback_data=f"delete_note_{note_id}")
    )
    
    if not note[0][4]:
        markup.add(types.InlineKeyboardButton(f"📌 Закрепить", callback_data=f"pin_note_{note_id}"))
    
    bot.send_message(user_id, text, parse_mode="Markdown", reply_markup=markup)

# ========== АДМИН ПАНЕЛЬ ==========
@bot.message_handler(func=lambda message: message.text == f"{EMOJIS['admin']} Админ панель" or message.text == "/admin")
@admin_required
@log_command
def admin_panel(message):
    """Админ панель"""
    user_id = message.from_user.id
    
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton(f"{EMOJIS['users']} Пользователи", callback_data="admin_users"),
        types.InlineKeyboardButton(f"{EMOJIS['chart']} Статистика", callback_data="admin_stats"),
        types.InlineKeyboardButton(f"{EMOJIS['mail']} Рассылка", callback_data="admin_broadcast"),
        types.InlineKeyboardButton(f"{EMOJIS['shop']} Управление товарами", callback_data="admin_products"),
        types.InlineKeyboardButton(f"{EMOJIS['coupon']} Промокоды", callback_data="admin_promos"),
        types.InlineKeyboardButton(f"{EMOJIS['ticket']} Обращения", callback_data="admin_tickets"),
        types.InlineKeyboardButton(f"{EMOJIS['moderator']} Модерация", callback_data="admin_moderation"),
        types.InlineKeyboardButton(f"{EMOJIS['settings']} Настройки", callback_data="admin_settings")
    )
    
    # Статистика для админа
    stats = get_admin_stats()
    
    bot.send_message(user_id, f"{EMOJIS['admin']} **Админ панель**\n\n"
                              f"{stats}\n"
                              f"Выберите действие:",
                    parse_mode="Markdown", reply_markup=markup)

def get_admin_stats():
    """Получить статистику для админ панели"""
    total_users = db.execute_query("SELECT COUNT(*) FROM users")[0][0]
    active_24h = db.execute_query("SELECT COUNT(*) FROM users WHERE last_active >= datetime('now', '-1 day')")[0][0]
    new_24h = db.execute_query("SELECT COUNT(*) FROM users WHERE registration_date >= datetime('now', '-1 day')")[0][0]
    open_tickets = db.execute_query("SELECT COUNT(*) FROM support_tickets WHERE status = 'open'")[0][0]
    
    return (f"📊 **Быстрая статистика**\n"
            f"👥 Всего: {total_users}\n"
            f"✅ Активны 24ч: {active_24h}\n"
            f"🆕 Новые 24ч: {new_24h}\n"
            f"🎫 Открытых обращений: {open_tickets}")

@bot.callback_query_handler(func=lambda call: call.data == "admin_broadcast")
def admin_broadcast_menu(call):
    """Меню рассылки"""
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton(f"{EMOJIS['mail']} Текстовая рассылка", callback_data="broadcast_text"),
        types.InlineKeyboardButton(f"{EMOJIS['star']} Рассылка с фото", callback_data="broadcast_photo"),
        types.InlineKeyboardButton(f"{EMOJIS['chart']} Рассылка с кнопкой", callback_data="broadcast_button"),
        types.InlineKeyboardButton(f"{EMOJIS['error']} Назад", callback_data="back_to_admin")
    )
    
    bot.edit_message_text(f"{EMOJIS['mail']} **Выберите тип рассылки:**",
                          call.message.chat.id, call.message.message_id,
                          parse_mode="Markdown", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "broadcast_text")
def broadcast_text(call):
    """Текстовая рассылка"""
    msg = bot.send_message(call.message.chat.id, 
                          f"{EMOJIS['mail']} Введите текст для рассылки:\n\n"
                          f"Для отмены отправьте /cancel")
    
    user_states[call.from_user.id] = {'state': 'broadcast_text', 'message_id': msg.message_id}

@bot.message_handler(func=lambda message: user_states.get(message.from_user.id, {}).get('state') == 'broadcast_text')
def process_broadcast_text(message):
    """Обработка текстовой рассылки"""
    user_id = message.from_user.id
    broadcast_text = message.text
    
    if broadcast_text == '/cancel':
        del user_states[user_id]
        bot.send_message(user_id, f"{EMOJIS['error']} Рассылка отменена")
        return
    
    # Получаем всех пользователей
    users = db.execute_query("SELECT user_id FROM users")
    
    confirm_msg = f"{EMOJIS['warning']} **Подтверждение рассылки**\n\n"
    confirm_msg += f"Текст: {broadcast_text[:200]}\n"
    confirm_msg += f"Количество получателей: {len(users)}\n\n"
    confirm_msg += f"Отправить?"
    
    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton(f"{EMOJIS['check']} Отправить", callback_data=f"confirm_broadcast_{hash(broadcast_text)}"),
        types.InlineKeyboardButton(f"{EMOJIS['error']} Отмена", callback_data="cancel_broadcast")
    )
    
    broadcast_data[hash(broadcast_text)] = broadcast_text
    bot.send_message(user_id, confirm_msg, parse_mode="Markdown", reply_markup=markup)
    del user_states[user_id]

@bot.callback_query_handler(func=lambda call: call.data.startswith("confirm_broadcast_"))
def confirm_broadcast(call):
    """Подтверждение рассылки"""
    broadcast_hash = int(call.data.replace("confirm_broadcast_", ""))
    broadcast_text = broadcast_data.get(broadcast_hash)
    
    if not broadcast_text:
        bot.answer_callback_query(call.id, "Ошибка! Попробуйте снова.")
        return
    
    users = db.execute_query("SELECT user_id FROM users")
    
    bot.answer_callback_query(call.id, f"Начинаю рассылку {len(users)} пользователям...")
    
    success = 0
    failed = 0
    
    for user in users:
        try:
            bot.send_message(user[0], f"{EMOJIS['mail']} **РАССЫЛКА**\n\n{broadcast_text}", 
                           parse_mode="Markdown")
            success += 1
            time.sleep(0.05)
        except:
            failed += 1
    
    bot.edit_message_text(f"{EMOJIS['check']} **Рассылка завершена!**\n\n"
                          f"✅ Успешно: {success}\n"
                          f"❌ Не доставлено: {failed}",
                          call.message.chat.id, call.message.message_id,
                          parse_mode="Markdown")
    
    del broadcast_data[broadcast_hash]

# ========== ОБРАБОТЧИКИ КНОПОК ==========
@bot.callback_query_handler(func=lambda call: call.data == "back_to_shop")
def back_to_shop(call):
    """Вернуться в магазин"""
    shop_command(call.message)

@bot.callback_query_handler(func=lambda call: call.data == "back_to_admin")
def back_to_admin(call):
    """Вернуться в админ панель"""
    admin_panel(call.message)

@bot.callback_query_handler(func=lambda call: call.data == "cancel_buy")
def cancel_buy(call):
    """Отмена покупки"""
    user_id = call.from_user.id
    if user_id in user_temp_data:
        del user_temp_data[user_id]
    
    bot.answer_callback_query(call.id, "Покупка отменена")
    bot.delete_message(call.message.chat.id, call.message.message_id)

@bot.callback_query_handler(func=lambda call: call.data == "cancel_broadcast")
def cancel_broadcast(call):
    """Отмена рассылки"""
    bot.answer_callback_query(call.id, "Рассылка отменена")
    bot.delete_message(call.message.chat.id, call.message.message_id)

# ========== ОБРАБОТЧИК ОШИБОК И ЗАПУСК ==========
@bot.message_handler(content_types=['text'])
def handle_all_messages(message):
    """Обработка всех текстовых сообщений"""
    user_id = message.from_user.id
    
    # Проверяем есть ли состояние
    if user_id in user_states:
        return
    
    # Обновляем время последней активности
    db.execute_query(
        "UPDATE users SET last_active = ? WHERE user_id = ?",
        (datetime.now(), user_id)
    )
    
    # Обработка обычных сообщений
    text = message.text.lower()
    
    if text == "каталог" or text == f"{EMOJIS['shop']} каталог":
        shop_command(message)
    elif text == "профиль" or text == f"{EMOJIS['user']} профиль":
        profile_command(message)
    elif text == "помощь" or text == f"{EMOJIS['help']} помощь" or text == "/help":
        show_help(message)
    elif text == "бонусы" or text == f"{EMOJIS['coins']} бонусы":
        bonus_command(message)
    elif text == "статистика" or text == f"{EMOJIS['chart']} статистика":
        user_stats(message)
    elif text == "настройки" or text == f"{EMOJIS['settings']} настройки":
        settings_command(message)
    elif text == "акции" or text == f"{EMOJIS['star']} акции":
        promotions_command(message)
    else:
        # Обычный ответ
        bot.send_message(user_id, 
                        f"{EMOJIS['info']} Используйте кнопки меню или команду /help для списка команд.\n"
                        f"Я понимаю только команды и кнопки меню.")

def show_help(message):
    """Показать справку"""
    user_id = message.from_user.id
    
    help_text = f"{EMOJIS['help']} **Помощь и команды**\n\n"
    help_text += "**Основные команды:**\n"
    help_text += "/start - Запустить бота\n"
    help_text += "/help - Показать эту справку\n"
    help_text += "/profile - Ваш профиль\n"
    help_text += "/shop - Каталог товаров\n"
    help_text += "/bonus - Бонусная система\n"
    help_text += "/tasks - Ежедневные задания\n"
    help_text += "/referral - Реферальная программа\n\n"
    
    help_text += "**Полезные команды:**\n"
    help_text += "/remind - Создать напоминание\n"
    help_text += "/notes - Мои заметки\n"
    help_text += "/support - Поддержка\n"
    help_text += "/feedback - Оставить отзыв\n"
    help_text += "/promo - Активировать промокод\n"
    help_text += "/stats - Статистика (админ)\n"
    
    if is_admin(user_id):
        help_text += "\n**Админ команды:**\n"
        help_text += "/admin - Админ панель\n"
        help_text += "/broadcast - Рассылка\n"
        help_text += "/create_promo - Создать промокод\n"
        help_text += "/poll - Создать опрос\n"
    
    bot.send_message(user_id, help_text, parse_mode="Markdown")

def user_stats(message):
    """Показать личную статистику пользователя"""
    user_id = message.from_user.id
    
    # Получаем статистику пользователя
    stats = db.execute_query('''
        SELECT 
            COUNT(DISTINCT date(registration_date)) as days_active,
            (SELECT COUNT(*) FROM purchases WHERE user_id = ?) as purchases_count,
            (SELECT SUM(total_amount) FROM purchases WHERE user_id = ?) as total_spent,
            (SELECT COUNT(*) FROM referrals WHERE referrer_id = ?) as referrals_count,
            (SELECT COUNT(*) FROM completed_tasks WHERE user_id = ?) as tasks_completed
        FROM users WHERE user_id = ?
    ''', (user_id, user_id, user_id, user_id, user_id, user_id))
    
    if stats:
        data = stats[0]
        text = f"{EMOJIS['chart']} **Ваша статистика**\n\n"
        text += f"📅 Активных дней: {data[0]}\n"
        text += f"🛒 Совершено покупок: {data[1]}\n"
        text += f"💰 Потрачено всего: {data[2] or 0} монет\n"
        text += f"👥 Приглашено друзей: {data[3]}\n"
        text += f"✅ Выполнено заданий: {data[4]}\n"
        
        bot.send_message(user_id, text, parse_mode="Markdown")

def settings_command(message):
    """Настройки пользователя"""
    user_id = message.from_user.id
    
    user_lang = get_user_language(user_id)
    
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton(f"🇷🇺 Русский", callback_data="set_lang_ru"),
        types.InlineKeyboardButton(f"🇺🇿 O'zbek", callback_data="set_lang_uz"),
        types.InlineKeyboardButton(f"🇰🇬 Кыргызча", callback_data="set_lang_ky"),
        types.InlineKeyboardButton(f"🇹🇯 Тоҷикӣ", callback_data="set_lang_tg"),
        types.InlineKeyboardButton(f"🇰🇿 Қазақша", callback_data="set_lang_kz"),
        types.InlineKeyboardButton(f"🇬🇧 English", callback_data="set_lang_en")
    )
    
    bot.send_message(user_id, f"{EMOJIS['settings']} **Настройки**\n\n"
                              f"Текущий язык: {user_lang.upper()}\n\n"
                              f"Выберите язык:",
                    parse_mode="Markdown", reply_markup=markup)

def promotions_command(message):
    """Показать текущие акции"""
    user_id = message.from_user.id
    
    text = f"{EMOJIS['star']} **ТЕКУЩИЕ АКЦИИ**\n\n"
    text += f"🎁 **Приветственный бонус**\n"
    text += f"Новые пользователи получают 100 бонусных монет!\n\n"
    
    text += f"👥 **Реферальная программа**\n"
    text += f"Пригласи друга - получи {REFERRAL_BONUS} монет!\n"
    text += f"Друг тоже получит {REFERRAL_BONUS} монет!\n\n"
    
    text += f"🔥 **Ежедневный бонус**\n"
    text += f"Заходи каждый день и получай до 500 монет!\n"
    text += f"Серия дней увеличивает награду!\n\n"
    
    text += f"💎 **Кешбек 5%**\n"
    text += f"За каждую покупку возвращаем 5% бонусами!\n\n"
    
    text += f"🎯 **Ежедневные задания**\n"
    text += f"Выполняй задания и зарабатывай до 200 монет в день!\n"
    
    bot.send_message(user_id, text, parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: call.data.startswith("set_lang_"))
def set_language(call):
    """Установить язык пользователя"""
    user_id = call.from_user.id
    language = call.data.replace("set_lang_", "")
    
    if language in SUPPORTED_LANGUAGES:
        db.execute_query(
            "UPDATE users SET language = ? WHERE user_id = ?",
            (language, user_id)
        )
        
        bot.answer_callback_query(call.id, f"Язык изменен на {language.upper()}")
        bot.edit_message_text(f"{EMOJIS['check']} Язык успешно изменен на {language.upper()}!",
                             call.message.chat.id, call.message.message_id)
    else:
        bot.answer_callback_query(call.id, "Неподдерживаемый язык!")

@bot.message_handler(commands=['feedback'])
@user_exists
@log_command
def feedback_command(message):
    """Оставить отзыв"""
    user_id = message.from_user.id
    
    markup = types.InlineKeyboardMarkup(row_width=5)
    buttons = []
    for i in range(1, 6):
        buttons.append(types.InlineKeyboardButton(str(i), callback_data=f"rate_{i}"))
    markup.add(*buttons)
    
    bot.send_message(user_id, f"{EMOJIS['star']} Оцените нашего бота от 1 до 5:",
                    reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("rate_"))
def process_rating(call):
    """Обработка оценки"""
    user_id = call.from_user.id
    rating = int(call.data.replace("rate_", ""))
    
    user_states[user_id] = {'state': 'feedback_comment', 'rating': rating}
    
    bot.answer_callback_query(call.id, "Спасибо за оценку!")
    bot.send_message(user_id, f"{EMOJIS['mail']} Напишите ваш отзыв (или отправьте /skip):")

@bot.message_handler(func=lambda message: user_states.get(message.from_user.id, {}).get('state') == 'feedback_comment')
def process_feedback_comment(message):
    """Обработка комментария отзыва"""
    user_id = message.from_user.id
    rating = user_states[user_id]['rating']
    
    if message.text == "/skip":
        comment = ""
    else:
        comment = message.text
    
    # Сохраняем отзыв
    db.execute_query('''
        INSERT INTO feedback (user_id, rating, comment, timestamp, is_responded)
        VALUES (?, ?, ?, ?, 0)
    ''', (user_id, rating, comment, datetime.now()))
    
    bot.send_message(user_id, f"{EMOJIS['check']} Спасибо за ваш отзыв!")
    
    # Уведомляем админов
    for admin in ADMINS:
        bot.send_message(admin, f"{EMOJIS['star']} **Новый отзыв**\n\n"
                               f"Оценка: {rating}/5\n"
                               f"Комментарий: {comment or 'Без комментария'}\n"
                               f"От: {message.from_user.first_name}")
    
    del user_states[user_id]

@bot.message_handler(commands=['referral'])
@user_exists
@log_command
def referral_command(message):
    """Показать реферальную информацию"""
    user_id = message.from_user.id
    ref_code = encode_referral_code(user_id)
    ref_link = f"https://t.me/{bot.get_me().username}?start={ref_code}"
    
    referrals_count = db.execute_query("SELECT COUNT(*) FROM referrals WHERE referrer_id = ?", (user_id,))[0][0]
    total_bonus = db.execute_query("SELECT SUM(reward_amount) FROM referrals WHERE referrer_id = ?", (user_id,))[0][0] or 0
    
    text = f"{EMOJIS['users']} **Ваша реферальная ссылка:**\n"
    text += f"`{ref_link}`\n\n"
    text += f"**Статистика:**\n"
    text += f"• Приглашено: {referrals_count}\n"
    text += f"• Заработано: {total_bonus} {BONUS_COINS}\n\n"
    text += f"За каждого приглашенного друга вы получаете {REFERRAL_BONUS} {BONUS_COINS}!\n"
    text += f"Друг тоже получает {REFERRAL_BONUS} {BONUS_COINS} на счет!"
    
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(f"{EMOJIS['mail']} Поделиться", callback_data="share_referral"))
    
    bot.send_message(user_id, text, parse_mode="Markdown", reply_markup=markup)

# ========== ЗАПУСК БОТА ==========
if __name__ == "__main__":
    print("=" * 50)
    print(f"{EMOJIS['check']} Бот NSP Goods запущен!")
    print(f"{EMOJIS['users']} База данных инициализирована")
    print(f"{EMOJIS['admin']} Администраторы: {ADMINS}")
    
    # Запускаем планировщик
    scheduler.start()
    
    # Запускаем бота
    while True:
        try:
            bot.infinity_polling(timeout=60)
        except Exception as e:
            logger.error(f"Ошибка бота: {e}")
            time.sleep(5)
