import logging
import asyncio
import os
from aiogram import Bot, Dispatcher, F, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import CommandStart
from aiogram.fsm.storage.memory import MemoryStorage
from dotenv import load_dotenv
from openai import OpenAI
from datetime import datetime, timedelta

load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

logging.basicConfig(level=logging.INFO)

bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher(storage=MemoryStorage())
client = OpenAI(api_key=OPENAI_API_KEY)

main_menu = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[
    [KeyboardButton(text="🧠 Наши нейросети (описание)")],
    [KeyboardButton(text="🤖 Выбрать ИИ (при подписке)")],
    [KeyboardButton(text="💫 Премиум"), KeyboardButton(text="👤 Профиль")]
])

user_model = {}
user_gpt4_usage = {}
user_last_reset = {}
GPT4_DAILY_LIMIT = 5

premium_tariffs = {
    "text_ai": {
        "title": "📝 Все текстовые ИИ",
        "desc": "Доступ к GPT-4, GPT-4 Omni и будущим текстовым ИИ.",
        "month": 349,
        "year": 2490
    },
    "image_ai": {
        "title": "🖼 ИИ для изображений",
        "desc": "DALL·E, Midjourney, Stable Diffusion (в разработке).",
        "month": 299,
        "year": 1990
    },
    "full_access": {
        "title": "🚀 Полный доступ",
        "desc": "Весь функционал: текст + изображения без ограничений.",
        "month": 499,
        "year": 3690
    }
}

model_descriptions = {
    "gpt-3.5-turbo": "🧠 GPT-3.5 — бесплатная и быстрая модель.",
    "gpt-4": "🚀 GPT-4 — премиум-модель с высокой точностью.",
    "gpt-4o": "🤖 GPT-4 Omni — самый мощный ИИ на сегодня.",
    "dalle": "🎨 DALL·E 3 — генерация изображений по тексту.",
    "midjourney": "🖌 Midjourney — художественный ИИ.",
    "stablediff": "🧠 Stable Diffusion — генератор изображений."
}

@dp.message(CommandStart())
async def send_welcome(message: types.Message):
    user_id = message.from_user.id
    user_model[user_id] = "gpt-3.5-turbo"
    user_gpt4_usage[user_id] = 0
    user_last_reset[user_id] = datetime.now()
    await message.answer(
    await message.answer(
        """👋 Добро пожаловать в NUMBER ONE — мир нейросетей!

📌 GPT-3.5 — бесплатно
🚀 GPT-4, DALL·E и прочее — пока отключены или под подписку."""
    )
        "🚀 GPT-4, DALL·E и прочее — пока отключены или под подписку.",
        reply_markup=main_menu
    )

@dp.message(F.text == "🧠 Наши нейросети (описание)")
async def show_models(message: types.Message):
    text = "🧠 <b>Доступные нейросети:</b>

"
    for desc in model_descriptions.values():
        text += f"{desc}

"
    await message.answer(text.strip(), parse_mode="HTML")

@dp.message(F.text == "💫 Премиум")
async def premium_info(message: types.Message):
    text = "💎 <b>Премиум-подписки</b>

"
    for key, data in premium_tariffs.items():
        text += f"{data['title']}
{data['desc']}
1 мес: {data['month']}₽ | 1 год: {data['year']}₽

"
    await message.answer(text.strip(), parse_mode="HTML")

@dp.message(F.text == "👤 Профиль")
async def profile_info(message: types.Message):
    user_id = message.from_user.id
    model = user_model.get(user_id, "gpt-3.5-turbo")
    await message.answer(f"👤 Ваш ID: {user_id}
🧠 Активная модель: {model}")

@dp.message(F.text == "🤖 Выбрать ИИ (при подписке)")
async def choose_model(message: types.Message):
    user_id = message.from_user.id
    current = user_model.get(user_id, "gpt-3.5-turbo")
    def label(name, code):
        return f"{name} ✅" if code == current else name
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=label("GPT-3.5", "gpt-3.5-turbo"), callback_data="select_gpt-3.5-turbo")],
        [InlineKeyboardButton(text=label("GPT-4", "gpt-4"), callback_data="select_gpt-4")],
        [InlineKeyboardButton(text=label("GPT-4 Omni", "gpt-4o"), callback_data="select_gpt-4o")],
        [InlineKeyboardButton(text=label("DALL·E 3", "dalle"), callback_data="select_dalle")],
        [InlineKeyboardButton(text=label("Midjourney", "midjourney"), callback_data="select_midjourney")],
        [InlineKeyboardButton(text=label("Stable Diffusion", "stablediff"), callback_data="select_stablediff")]
    ])
    await message.answer("Выберите ИИ:", reply_markup=kb)

@dp.callback_query(F.data.startswith("select_"))
async def model_selected(callback: types.CallbackQuery):
    model = callback.data.replace("select_", "")
    user_model[callback.from_user.id] = model
    await callback.message.answer(f"✅ Модель {model} выбрана.")
    await callback.answer()

@dp.message()
async def chat_handler(message: types.Message):
    user_id = message.from_user.id
    model = user_model.get(user_id, "gpt-3.5-turbo")

    if model in ["gpt-4", "gpt-4o"]:
        await message.answer("🚫 Подписка GPT-4 временно отключена.")
        return

    if model in ["dalle", "midjourney", "stablediff"]:
        await message.answer("🖼 Генерация изображений скоро появится.")
        return

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "Ты полезный Telegram-бот."},
                {"role": "user", "content": message.text}
            ]
        )
        await message.answer(response.choices[0].message.content)
    except Exception as e:
        await message.answer(f"⚠️ Ошибка: {e}")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
