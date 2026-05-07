import os
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
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

# 🔘 Кнопки
keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="📚 Объяснить тему"),
            KeyboardButton(text="🧮 Решить задачу")
        ],
        [
            KeyboardButton(text="📝 Сделать конспект"),
            KeyboardButton(text="📊 Осталось запросов")
        ],
        [
            KeyboardButton(text="👑 Premium"),
            KeyboardButton(text="💳 Оплата")
        ],
        [
            KeyboardButton(text="👥 Пригласить друга"),
            KeyboardButton(text="ℹ️ Помощь")
        ]
    ],
    resize_keyboard=True
)

# 🚀 START
@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer(
        "🎓 Привет! Я Reshala Study Bot\n\n"
        "📚 Объясняю темы\n"
        "🧮 Решаю задачи\n"
        "📝 Делаю конспекты\n\n"
        f"🎁 Бесплатно доступно {FREE_LIMIT} запросов\n\n"
        "👇 Выбери действие:",
        reply_markup=keyboard
    )

# 📚 explain
@dp.message(Command("explain"))
async def explain_command(message: types.Message):
    await message.answer(
        "📚 Напиши тему для объяснения"
    )

# 🧮 solve
@dp.message(Command("solve"))
async def solve_command(message: types.Message):
    await message.answer(
        "🧮 Отправь задачу"
    )

# 📝 summary
@dp.message(Command("summary"))
async def summary_command(message: types.Message):
    await message.answer(
        "📝 Отправь тему или текст"
    )

# 👥 invite
@dp.message(Command("invite"))
async def invite_command(message: types.Message):
    await message.answer(
        "👥 Пригласи друга 🚀\n\n"
        "https://t.me/Reshala_study_bot"
    )

# 💳 pay
@dp.message(Command("pay"))
async def pay_command(message: types.Message):
    await message.answer(
        "💳 Оплата Premium\n\n"
        "Переведи 199₽ на карту:\n"
        "XXXX XXXX XXXX XXXX\n\n"
        "После оплаты отправь чек."
    )

# 👑 premium
@dp.message(Command("premium"))
async def premium_command(message: types.Message):
    await message.answer(
        "👑 Premium доступ\n\n"
        "✅ Безлимитные запросы\n"
        "✅ Быстрые ответы\n"
        "✅ Доступ 30 дней\n\n"
        "💰 Цена: 199₽"
    )

# 📊 limit
@dp.message(Command("limit"))
async def limit_command(message: types.Message):
    user_id = message.from_user.id

    count = user_requests.get(user_id, 0)
    left = FREE_LIMIT - count

    await message.answer(
        f"📊 Осталось запросов: {left}"
    )

# ℹ️ help
@dp.message(Command("help"))
async def help_command(message: types.Message):
    await message.answer(
        "ℹ️ Просто напиши вопрос или выбери действие 👇"
    )

# 📚 кнопка
@dp.message(lambda message: message.text == "📚 Объяснить тему")
async def explain(message: types.Message):
    await message.answer(
        "📚 Напиши тему 👇"
    )

# 🧮 кнопка
@dp.message(lambda message: message.text == "🧮 Решить задачу")
async def solve(message: types.Message):
    await message.answer(
        "🧮 Отправь задачу 👇"
    )

# 📝 кнопка
@dp.message(lambda message: message.text == "📝 Сделать конспект")
async def summary(message: types.Message):
    await message.answer(
        "📝 Отправь текст или тему 👇"
    )

# 📊 кнопка
@dp.message(lambda message: message.text == "📊 Осталось запросов")
async def remaining(message: types.Message):
    user_id = message.from_user.id

    count = user_requests.get(user_id, 0)
    left = FREE_LIMIT - count

    await message.answer(
        f"📊 Осталось запросов: {left}"
    )

# 👑 кнопка
@dp.message(lambda message: message.text == "👑 Premium")
async def premium(message: types.Message):
    await message.answer(
        "👑 Premium доступ\n\n"
        "💰 Цена: 199₽"
    )

# 💳 кнопка
@dp.message(lambda message: message.text == "💳 Оплата")
async def payment(message: types.Message):
    await message.answer(
        "💳 Оплата Premium\n\n"
        "Переведи 199₽ на карту:\n"
        "XXXX XXXX XXXX XXXX\n\n"
        "После оплаты отправь чек."
    )

# 👥 кнопка
@dp.message(lambda message: message.text == "👥 Пригласить друга")
async def invite(message: types.Message):
    await message.answer(
        "👥 Пригласи друга 🚀\n\n"
        "https://t.me/Reshala_study_bot"
    )

# ℹ️ кнопка
@dp.message(lambda message: message.text == "ℹ️ Помощь")
async def help_message(message: types.Message):
    await message.answer(
        "ℹ️ Просто напиши вопрос.\n\n"
        "Например:\n"
        "• Объясни фотосинтез\n"
        "• Реши уравнение\n"
        "• Сделай конспект"
    )

# 🧠 Главный AI обработчик
@dp.message()
async def handle_message(message: types.Message):
    user_id = message.from_user.id

    # новый пользователь
    if user_id not in user_requests:
        user_requests[user_id] = 0

    # лимит
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
                    "content": "Ты помощник для студентов. Отвечай просто и понятно."
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

# 🚀 Запуск
async def main():
    print("Бот запущен 🚀")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
