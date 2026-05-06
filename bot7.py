import asyncio
from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.filters import CommandStart
from openai import OpenAI

# 🔴 ВСТАВЬ СЮДА ТОКЕН БОТА
BOT_TOKEN = "8539257046:AAGr1IjkC3YiEcssnZOVWhd1aBpS8ivaRRo"

# 🔴 ВСТАВЬ СЮДА API КЛЮЧ OPENAI
client = OpenAI(api_key="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")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

@dp.message(CommandStart())
async def start(message: Message):
    await message.answer("Привет 👋 Напиши вопрос")

@dp.message()
async def ai_answer(message: Message):
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": message.text}]
        )

        answer = response.choices[0].message.content

        await message.answer(answer)

    except Exception as e:
        print("ОШИБКА:", e)  # 👈 ВАЖНО
        await message.answer("Ошибка 😔 смотри консоль")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())