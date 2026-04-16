from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web
import os

TOKEN = "8221315194:AAHlIGn55-hYNUa4nMQOwuHOkYUQ9osNDXQ"

bot = Bot(token=TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer("🧊 Добро пожаловать в ICE Studio!")

async def on_startup(bot: Bot):
    # Railway даёт случайный порт через переменную PORT
    port = int(os.environ.get("PORT", 8080))
    webhook_url = f"https://{os.environ.get('RAILWAY_PUBLIC_DOMAIN', 'localhost')}"
    await bot.set_webhook(f"{webhook_url}/webhook")
    print(f"Webhook set to {webhook_url}")

async def on_shutdown(bot: Bot):
    await bot.delete_webhook()

def main():
    app = web.Application()
    
    # Webhook handler
    webhook_requests_handler = SimpleRequestHandler(dispatcher=dp, bot=bot)
    webhook_requests_handler.register(app, path="/webhook")
    setup_application(app, dp, bot=bot)
    
    app.on_startup.append(lambda _: on_startup(bot))
    app.on_shutdown.append(lambda _: on_shutdown(bot))
    
    port = int(os.environ.get("PORT", 8080))
    web.run_app(app, host="0.0.0.0", port=port)

if __name__ == "__main__":
    main()
