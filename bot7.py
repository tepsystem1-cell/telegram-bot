import os
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from openai import OpenAI

# берём ключи из Railway
BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# инициализация
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
client = OpenAI(api_key=OPENAI_API_KEY)


# команда /start
@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer("Привет! Напиши любой вопрос 🙂")


# обработка всех сообщений
@dp.message()
async def handle_message(message: types.Message):
    try:
        response = client.responses.create(
            model="gpt-4.1-mini",
            input=message.text
        )

        answer = response.output[0].content[0].text
        await message.answer(answer)

    except Exception as e:
        await message.answer(f"Ошибка: {e}")


# запуск
async def main():
    print("Бот запущен 🚀")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
