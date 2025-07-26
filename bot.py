import os
import logging
import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.fsm.storage.memory import MemoryStorage
from dotenv import load_dotenv
import openai

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not BOT_TOKEN or not OPENAI_API_KEY:
    raise RuntimeError("❌ Убедись, что переменные BOT_TOKEN и OPENAI_API_KEY заданы!")

openai.api_key = OPENAI_API_KEY
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

@dp.message(F.text == "/start")
async def start(message: types.Message):
    await message.answer("✅ Бот запущен! Напиши мне что-нибудь.")

@dp.message(F.text)
async def gpt_reply(message: types.Message):
    await message.answer("💬 Думаю...")

    try:
        res = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": message.text}]
        )
        reply = res.choices[0].message.content
        await message.answer(reply)

    except Exception as e:
        await message.answer(f"❌ Ошибка:\n<code>{e}</code>", parse_mode="HTML")
        print("OpenAI Error:", e)

async def main():
    logging.basicConfig(level=logging.INFO)
    print("✅ Бот запускается...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
