import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import Message
from openai import AsyncOpenAI

# ========== КЛЮЧИ ==========
TELEGRAM_TOKEN = "8221315194:AAHlIGn55-hYNUa4nMQOwuHOkYUQ9osNDXQ"
OPENROUTER_API_KEY = "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"

client = AsyncOpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_API_KEY,
)

SYSTEM_PROMPT = """
Ты — официальный ИИ студии мобильных игр ICE.
Два программиста (бывшие одноклассники) основали студию после ссоры.
Твой стиль: холодный, дерзкий, с ледяными метафорами, но дружелюбный.
Отвечай коротко (1-3 предложения). Ты геймдев, а не энциклопедия.
"""

bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def start_cmd(message: Message):
    await message.answer(
        "🧊 *ICE AI* активирован.\n"
        "Мы — студия мобильных игр. Код холодный, игры горячие.\n"
        "Задавай вопрос — отвечу в стиле ICE.",
        parse_mode="Markdown"
    )

@dp.message()
async def ai_reply(message: Message):
    await bot.send_chat_action(message.chat.id, action="typing")
    
    try:
        response = await client.chat.completions.create(
            model="deepseek/deepseek-chat-v3-0324:free",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": message.text}
            ],
            temperature=0.8,
            max_tokens=200
        )
        reply = response.choices[0].message.content
        await message.answer(reply)
    except Exception as e:
        await message.answer("❄️ *Заморозка связи.* Попробуй позже.", parse_mode="Markdown")

async def main():
    print("🧊 ICE Bot запущен!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
