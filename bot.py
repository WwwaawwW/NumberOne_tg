import logging
import asyncio
from datetime import datetime
from aiogram import Bot, Dispatcher, types, F
from aiogram.enums import ParseMode
from aiogram.types import Message
from aiogram.fsm.storage.memory import MemoryStorage
from dotenv import load_dotenv
import os
import openai

# Загрузка токенов из .env
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not BOT_TOKEN:
    raise ValueError("❌ BOT_TOKEN не найден в .env или Railway Variables.")
if not OPENAI_API_KEY:
    raise ValueError("❌ OPENAI_API_KEY не найден в .env или Railway Variables.")

openai.api_key = OPENAI_API_KEY

# Настройка Telegram-бота
bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher(storage=MemoryStorage())

# Хранилище пользователей
user_model = {}
user_gpt4_usage = {}
user_last_reset = {}

model_descriptions = {
    "gpt-3.5-turbo": "🤖 GPT-3.5 Turbo — быстрый и бесплатный.",
    "gpt-4": "🚀 GPT-4 — скоро будет доступен по подписке.",
}

@dp.message(F.text == "/start")
async def cmd_start(message: types.Message):
    user_id = message.from_user.id
    user_model[user_id] = "gpt-3.5-turbo"
    user_gpt4_usage[user_id] = 0
    user_last_reset[user_id] = datetime.now()

    await message.answer(
        """👋 Добро пожаловать в NUMBER ONE — мир нейросетей!

📌 GPT-3.5 — бесплатно
🚀 GPT-4, DALL·E и прочее — пока отключены или под подписку."""
    )

@dp.message(F.text == "🧠 Наши нейросети (описание)")
async def show_models(message: types.Message):
    text = "🧠 <b>Доступные нейросети:</b>\n\n"
    for desc in model_descriptions.values():
        text += f"{desc}\n"
    await message.answer(text)

@dp.message(F.text)
async def handle_message(message: Message):
    prompt = message.text
    await message.answer("⚙️ Генерирую ответ от GPT-3.5...")

    try:
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        reply = response.choices[0].message.content
        await message.answer(reply)

    except Exception as e:
        await message.answer(f"❌ OpenAI ошибка:\n<code>{str(e)}</code>", parse_mode="HTML")
        print("OpenAI Error:", e)

async def main():
    logging.basicConfig(level=logging.INFO)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
