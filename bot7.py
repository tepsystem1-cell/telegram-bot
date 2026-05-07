import os
import asyncio
import sqlite3

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

# 🗄️ SQLite база
conn = sqlite3.connect(
    "users.db",
    check_same_thread=False
)

conn.row_factory = sqlite3.Row

cursor = conn.cursor()

# 👥 Таблица пользователей
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    requests INTEGER DEFAULT 0,
    premium INTEGER DEFAULT 0
)
""")

conn.commit()

# 🚀 START
@dp.message(Command("start"))
async def start(message: types.Message):

    await message.answer(
        "🎓 Привет! Я Reshala Study Bot\n\n"
        "📚 Объясняю темы\n"
        "🧮 Решаю задачи\n"
        "📝 Делаю конспекты\n\n"
        f"🎁 Бесплатно доступно {FREE_LIMIT} запросов\n\n"
        "👇 Нажми Menu возле строки ввода",
        reply_markup=types.ReplyKeyboardRemove()
    )

# ℹ️ HELP
@dp.message(Command("help"))
async def help_command(message: types.Message):

    await message.answer(
        "ℹ️ Команды бота:\n\n"
        "/explain — объяснить тему\n"
        "/solve — решить задачу\n"
        "/summary — сделать конспект\n"
        "/limit — остаток запросов\n"
        "/premium — Premium доступ"
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

    cursor.execute(
        "SELECT requests FROM users WHERE user_id=?",
        (user_id,)
    )

    user = cursor.fetchone()

    if user is None:

        cursor.execute(
            "INSERT INTO users (user_id, requests, premium) VALUES (?, ?, ?)",
            (user_id, 0, 0)
        )

        conn.commit()

        requests_count = 0

    else:
        requests_count = user["requests"]

    left = FREE_LIMIT - requests_count

    if left < 0:
        left = 0

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
@dp.message(lambda message: message.text and not message.text.startswith("/"))
async def handle_message(message: types.Message):

    user_id = message.from_user.id

    # 🔍 Проверяем пользователя
    cursor.execute(
        "SELECT requests, premium FROM users WHERE user_id=?",
        (user_id,)
    )

    user = cursor.fetchone()

    # 👤 Новый пользователь
    if user is None:

        cursor.execute(
            "INSERT INTO users (user_id, requests, premium) VALUES (?, ?, ?)",
            (user_id, 0, 0)
        )

        conn.commit()

        requests_count = 0
        premium = 0

    else:
        requests_count = user["requests"]
        premium = user["premium"]

    # ⛔ Проверка лимита
    if requests_count >= FREE_LIMIT and premium == 0:

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

        # ➕ Обновляем счётчик
        cursor.execute(
            "UPDATE users SET requests = requests + 1 WHERE user_id=?",
            (user_id,)
        )

        conn.commit()

        await message.answer(answer)

    except Exception as e:

        await message.answer(
            f"Ошибка: {e}"
        )

# 🚀 ЗАПУСК
async def main():

    print("Бот запущен 🚀")

    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
