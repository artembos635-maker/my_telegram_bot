import asyncio
import logging

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# Токен прямо в коде
BOT_TOKEN = "8648265890:AAHlxr8DH_B4R-NtKUkSkNZDOiFdkEFt_lU"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


def get_main_keyboard() -> InlineKeyboardMarkup:
    """Главное меню"""
    buttons = [
        [InlineKeyboardButton(text="🛍 Каталог", callback_data="catalog")],
        [InlineKeyboardButton(text="📞 Контакты", callback_data="contacts")],
        [InlineKeyboardButton(text="ℹ️ О компании", callback_data="about")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_catalog_keyboard() -> InlineKeyboardMarkup:
    """Меню каталога"""
    buttons = [
        [InlineKeyboardButton(text="👕 Спецодежда", callback_data="cat_clothes")],
        [InlineKeyboardButton(text="👢 Обувь", callback_data="cat_shoes")],
        [InlineKeyboardButton(text="🧤 СИЗ (перчатки/каски)", callback_data="cat_ppe")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_main")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_back_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура с кнопкой Назад"""
    buttons = [[InlineKeyboardButton(text="🔙 Назад в меню", callback_data="back_to_main")]]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


# ===== ОБРАБОТЧИКИ КОМАНД =====

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    """Приветственное сообщение при /start"""
    welcome_text = (
        f"👋 Здравствуйте, {message.from_user.first_name}!\n\n"
        f"🛡️ Вас приветствует демо-бот каталога <b>«Восток-Сервис»</b>\n\n"
        f"Здесь вы можете ознакомиться с ассортиментом спецодежды, обуви и средств индивидуальной защиты.\n\n"
        f"⚠️ <i>Бот работает в демо-режиме. Точные цены и наличие уточняйте у менеджера.</i>\n\n"
        f"Выберите раздел:"
    )
    await message.answer(welcome_text, parse_mode="HTML", reply_markup=get_main_keyboard())


@dp.message(Command("help"))
async def cmd_help(message: types.Message):
    """Справка по командам"""
    help_text = (
        "📋 <b>Доступные команды:</b>\n"
        "/start — Главное меню\n"
        "/help — Справка\n"
        "/catalog — Перейти в каталог\n"
        "/contacts — Контакты филиалов\n"
        "/about — О компании\n"
    )
    await message.answer(help_text, parse_mode="HTML")


@dp.message(Command("catalog"))
async def cmd_catalog(message: types.Message):
    """Быстрый переход в каталог"""
    await message.answer("🛍 Выберите категорию товаров:", reply_markup=get_catalog_keyboard())


@dp.message(Command("contacts"))
async def cmd_contacts(message: types.Message):
    """Контакты"""
    contacts_text = (
        "📞 <b>Контакты «Восток-Сервис»</b>\n\n"
        "🏢 Центральный офис: г. Москва\n"
        "📱 Телефон: 8 (800) 700-42-42\n"
        "🌐 Сайт: vostok.ru\n\n"
        "📍 Более 120 филиалов в России и СНГ.\n"
        "Для уточнения наличия в вашем регионе свяжитесь с менеджером."
    )
    await message.answer(contacts_text, parse_mode="HTML", reply_markup=get_back_keyboard())


@dp.message(Command("about"))
async def cmd_about(message: types.Message):
    """О компании"""
    about_text = (
        "ℹ️ <b>ГК «Восток-Сервис»</b>\n\n"
        "Крупнейший поставщик спецодежды, обуви и средств индивидуальной защиты.\n\n"
        "✅ Более 30 лет на рынке\n"
        "✅ Собственные торговые марки\n"
        "✅ Соответствие ГОСТ и ТР ТС\n\n"
        "<i>Ассортимент: более 12 000 позиций</i>"
    )
    await message.answer(about_text, parse_mode="HTML", reply_markup=get_back_keyboard())


# ===== ОБРАБОТЧИКИ CALLBACK (КНОПКИ) =====

@dp.callback_query(lambda c: c.data == "back_to_main")
async def back_to_main(callback: types.CallbackQuery):
    """Возврат в главное меню"""
    await callback.message.edit_text(
        "🏠 Главное меню. Выберите раздел:",
        reply_markup=get_main_keyboard()
    )
    await callback.answer()


@dp.callback_query(lambda c: c.data == "catalog")
async def show_catalog(callback: types.CallbackQuery):
    """Показ каталога"""
    await callback.message.edit_text(
        "🛍 <b>Каталог продукции</b>\nВыберите интересующую категорию:",
        parse_mode="HTML",
        reply_markup=get_catalog_keyboard()
    )
    await callback.answer()


@dp.callback_query(lambda c: c.data == "contacts")
async def show_contacts(callback: types.CallbackQuery):
    """Показ контактов"""
    contacts_text = (
        "📞 <b>Контакты «Восток-Сервис»</b>\n\n"
        "🏢 Центральный офис: г. Москва\n"
        "📱 Телефон: 8 (800) 700-42-42\n"
        "🌐 Сайт: vostok.ru\n\n"
        "📍 Более 120 филиалов в России и СНГ."
    )
    await callback.message.edit_text(contacts_text, parse_mode="HTML", reply_markup=get_back_keyboard())
    await callback.answer()


@dp.callback_query(lambda c: c.data == "about")
async def show_about(callback: types.CallbackQuery):
    """Показ информации о компании"""
    about_text = (
        "ℹ️ <b>ГК «Восток-Сервис»</b>\n\n"
        "Крупнейший поставщик спецодежды, обуви и средств индивидуальной защиты.\n\n"
        "✅ Более 30 лет на рынке\n"
        "✅ Собственные торговые марки\n"
        "✅ Соответствие ГОСТ и ТР ТС"
    )
    await callback.message.edit_text(about_text, parse_mode="HTML", reply_markup=get_back_keyboard())
    await callback.answer()


# Заглушки для категорий каталога
@dp.callback_query(lambda c: c.data in ["cat_clothes", "cat_shoes", "cat_ppe"])
async def show_category_placeholder(callback: types.CallbackQuery):
    """Временная заглушка для категорий"""
    category_names = {
        "cat_clothes": "👕 Спецодежда",
        "cat_shoes": "👢 Обувь",
        "cat_ppe": "🧤 СИЗ"
    }
    name = category_names.get(callback.data, "Товары")
    text = f"📦 <b>{name}</b>\n\nРаздел находится в разработке.\nСкоро здесь появится каталог продукции."
    await callback.message.edit_text(text, parse_mode="HTML", reply_markup=get_back_keyboard())
    await callback.answer()


# ===== ЗАПУСК =====

async def main():
    logger.info("🚀 Бот запущен!")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
