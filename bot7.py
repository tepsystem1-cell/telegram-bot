import os
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from openai import OpenAI

# ключи Railway
BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# запуск
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
client = OpenAI(api_key=OPENAI_API_KEY)

# лимит
FREE_LIMIT = 7

# память пользователей
user_requests = {}

# кнопки
keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📚 Объяснить тему"),
         KeyboardButton(text="🧮 Решить задачу")],

        [KeyboardButton(text="📝 Сделать конспект"),
         KeyboardButton(text="📷 Отправить фото задачи")],

        [KeyboardButton(text="📊 Осталось запросов"),
         KeyboardButton(text="👑 Premium")],

        [KeyboardButton(text="💳 Оплата"),
         KeyboardButton(text="👥 Пригласить друга")],

        [KeyboardButton(text="ℹ️ Помощь")]
    ],
    resize_keyboard=True
)

# /start
@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer(
        "🎓 Привет! Я Reshala Study Bot\n\n"
        "📚 Объясняю темы\n"
        "🧮 Решаю задачи\n"
        "📝 Делаю конспекты\n\n"
        f"🎁 У тебя есть {FREE_LIMIT} бесплатных запросов\n\n"
        "👇 Выбери действие ниже",
        reply_markup=keyboard
    )

# 📚 объяснение
@dp.message(lambda message: message.text == "📚 Объяснить тему")
async def explain(message: types.Message):
    await message.answer("📚 Напиши тему, которую нужно объяснить")

# 🧮 задача
@dp.message(lambda message: message.text == "🧮 Решить задачу")
async def solve(message: types.Message):
    await message.answer("🧮 Отправь задачу")

# 📝 конспект
@dp.message(lambda message: message.text == "📝 Сделать конспект")
async def summary(message: types.Message):
    await message.answer("📝 Отправь тему или текст")

# 📷 фото
@dp.message(lambda message: message.text == "📷 Отправить фото задачи")
async def photo(message: types.Message):
    await message.answer(
        "📷 Функция фото скоро появится 🚀"
    )

# 📊 остаток
@dp.message(lambda message: message.text == "📊 Осталось запросов")
async def remaining(message: types.Message):
    user_id = message.from_user.id

    count = user_requests.get(user_id, 0)
    left = FREE_LIMIT - count

    await message.answer(
        f"📊 Осталось запросов: {left}"
    )

# 👑 premium
@dp.message(lambda message: message.text == "👑 Premium")
async def premium(message: types.Message):
    await message.answer(
        "👑 Premium доступ:\n\n"
        "✅ Безлимитные запросы\n"
        "✅ Быстрые ответы\n"
        "✅ Доступ 30 дней\n\n"
        "💰 Цена: 199₽"
    )

# 💳 оплата
@dp.message(lambda message: message.text == "💳 Оплата")
async def payment(message: types.Message):
    await message.answer(
        "💳 Оплата Premium\n\n"
        "💰 Стоимость: 199₽\n\n"
        "Переведи оплату на карту:\n"
        "XXXX XXXX XXXX XXXX\n\n"
        "После оплаты отправь чек."
    )

# 👥 друзья
@dp.message(lambda message: message.text == "👥 Пригласить друга")
async def invite(message: types.Message):
    await message.answer(
        "👥 Пригласи друга и получи бонус 🚀\n\n"
        "Отправь другу ссылку на бота:\n"
        "https://t.me/Reshala_study_bot"
    )

# ℹ️ помощь
@dp.message(lambda message: message.text == "ℹ️ Помощь")
async def help_message(message: types.Message):
    await message.answer(
        "ℹ️ Просто напиши вопрос\n\n"
        "Например:\n"
        "• Объясни фотосинтез\n"
        "• Реши уравнение\n"
        "• Сделай конспект"
    )

# главный обработчик
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
            "💳 Для продолжения нужен Premium"
        )
        return

    try:
        response = client.responses.create(
            model="gpt-4.1-mini",
            input=[
                {
                    "role": "system",
                    "content": "Ты помощник для студентов. Объясняй просто и понятно."
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

# запуск
async def main():
    print("Бот запущен 🚀")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
