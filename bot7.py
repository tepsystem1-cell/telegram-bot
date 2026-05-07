import os
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from openai import OpenAI

# 🔑 Railway Variables
BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# 🚀 Инициализация
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
client = OpenAI(api_key=OPENAI_API_KEY)

# 🎁 Бесплатный лимит
FREE_LIMIT = 7

# 👤 Память пользователей
user_requests = {}

# 🚀 START
@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer(
        "🎓 Привет! Я Reshala Study Bot\n\n"
        "📚 Объясняю темы\n"
        "🧮 Решаю задачи\n"
        "📝 Делаю конспекты\n\n"
        f"🎁 Бесплатно доступно {FREE_LIMIT} запросов\n\n"
        "👇 Нажми Menu возле строки ввода"
    )

# ℹ️ HELP
@dp.message(Command("help"))
async def help_command(message: types.Message):
    await message.answer(
        "ℹ️ Просто выбери действие через Menu\n\n"
        "Например:\n"
        "• Объяснить тему\n"
        "• Решить задачу\n"
        "• Сделать конспект"
    )

# 👑 PREMIUM
@dp.message(Command("premium"))
async def premium_command(message: types.Message):
    await message.answer(
        "👑 Premium доступ\n\n"
        "✅ Безлимитные запросы\n"
        "✅ Быстрые ответы\n"
        "✅ Доступ 30 дней\n\n"
        "💰 Цена: 199₽"
    )

# 💳 PAY
@dp.message(Command("pay"))
async def pay_command(message: types.Message):
    await message.answer(
        "💳 Оплата Premium\n\n"
        "Переведи 199₽ на карту:\n"
        "XXXX XXXX XXXX XXXX\n\n"
        "После оплаты отправь чек."
    )

# 📊 LIMIT
@dp.message(Command("limit"))
async def limit_command(message: types.Message):
    user_id = message.from_user.id

    count = user_requests.get(user_id, 0)
    left = FREE_LIMIT - count

    await message.answer(
        f"📊 Осталось бесплатных запросов: {left}"
    )

# 📚 EXPLAIN
@dp.message(Command("explain"))
async def explain_command(message: types.Message):
    await message.answer(
        "📚 Напиши тему, которую нужно объяснить 👇"
    )

# 🧮 SOLVE
@dp.message(Command("solve"))
async def solve_command(message: types.Message):
    await message.answer(
        "🧮 Отправь задачу 👇"
    )

# 📝 SUMMARY
@dp.message(Command("summary"))
async def summary_command(message: types.Message):
    await message.answer(
        "📝 Отправь текст или тему 👇"
    )

# 👥 INVITE
@dp.message(Command("invite"))
async def invite_command(message: types.Message):
    await message.answer(
        "👥 Пригласи друга 🚀\n\n"
        "https://t.me/Reshala_study_bot"
    )

# 🧠 AI ОТВЕТЫ
@dp.message()
async def handle_message(message: types.Message):
    user_id = message.from_user.id

    # новый пользователь
    if user_id not in user_requests:
        user_requests[user_id] = 0

    # проверка лимита
    if user_requests[user_id] >= FREE_LIMIT:
        await message.answer(
            "⛔ Бесплатные запросы закончились\n\n"
            "💳 Купи Premium для продолжения"
        )
        return

    try:
        response = client.responses.create(
            model="gpt-4.1-mini",
            input=[
                {
                    "role": "system",
                    "content": (
                        "Ты умный помощник для студентов. "
                        "Объясняй простыми словами."
                    )
                },
                {
                    "role": "user",
                    "content": message.text
                }
            ]
        )

        answer = response.output[0].content[0].text

        # +1 запрос
        user_requests[user_id] += 1

        await message.answer(answer)

    except Exception as e:
        await message.answer(f"Ошибка: {e}")

# 🚀 ЗАПУСК
async def main():
    print("Бот запущен 🚀")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
