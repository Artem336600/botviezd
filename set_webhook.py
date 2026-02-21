import asyncio
import os
from aiogram import Bot
from dotenv import load_dotenv

load_dotenv()

async def set_webhook():
    bot = Bot(token=os.environ.get("BOT_TOKEN"))
    url = input("Enter your Vercel bot URL (e.g. https://mybot.vercel.app/api/webhook): ")
    await bot.set_webhook(url)
    print(f"Webhook set to {url}")
    await bot.session.close()

if __name__ == "__main__":
    asyncio.run(set_webhook())
