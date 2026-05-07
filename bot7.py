Похоже, у тебя была включена английская раскладка.
Ты написал:

```text id="s1"
ghbikb yjdsq rjl wtkbrjv
```

Это читается как:

```text id="s2"
пришли новый код целиком
```

Вот полный обновлённый код с тарифами:

* 2.5 USDT → 100 запросов / 1 месяц
* 6 USDT → 400 запросов / 3 месяца

```python id="s3"
import os
import asyncio
import sqlite3
from datetime import datetime, timedelta

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from openai import OpenAI

from aiocryptopay import AioCryptoPay, Networks

# 🔑 TOKENS
BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
CRYPTO_PAY_TOKEN = os.getenv("CRYPTO_PAY_TOKEN")

# 🤖 BOT
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

client = OpenAI(
    api_key=OPENAI_API_KEY
)

crypto = AioCryptoPay(
    token=CRYPTO_PAY_TOKEN,
    network=Networks.MAIN_NET
)

# 🎁 FREE LIMIT
FREE_LIMIT = 7

# 🗄 DATABASE
conn = sqlite3.connect(
    "users.db",
    check_same_thread=False
)

conn.row_factory = sqlite3.Row
cursor = conn.cursor()

# 👤 USERS
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    free_requests INTEGER DEFAULT 0,
    paid_requests INTEGER DEFAULT 0,
    premium_until TEXT DEFAULT '',
    tariff TEXT DEFAULT 'FREE'
)
""")

# 💳 INVOICES
cursor.execute("""
CREATE TABLE IF NOT EXISTS invoices (
    invoice_id INTEGER,
    user_id INTEGER,
    tariff TEXT
)
""")

conn.commit()

# 🚀 START
@dp.message(Command("start"))
async def start(message: types.Message):

    await message.answer(
        "🎓 Reshala Study Bot\n\n"
        "📚 Объясняю темы\n"
        "🧮 Решаю задачи\n"
        "📝 Делаю конспекты\n\n"
        "🎁 Бесплатно: 7 запросов\n\n"
        "💎 Тарифы:\n"
        "• 2.5 USDT → 100 запросов / 1 месяц\n"
        "• 6 USDT → 400 запросов / 3 месяца\n\n"
        "💳 Для покупки используй /pay"
    )

# 📊 STATUS
@dp.message(Command("status"))
async def status(message: types.Message):

    user_id = message.from_user.id

    cursor.execute(
        "SELECT * FROM users WHERE user_id=?",
        (user_id,)
    )

    user = cursor.fetchone()

    if user is None:

        await message.answer(
            "🎁 Бесплатный аккаунт\n"
            f"Осталось запросов: {FREE_LIMIT}"
        )

        return

    free_left = FREE_LIMIT - user["free_requests"]

    if free_left < 0:
        free_left = 0

    await message.answer(
        f"👤 Тариф: {user['tariff']}\n\n"
        f"🎁 Бесплатных запросов: {free_left}\n"
        f"💎 Premium запросов: {user['paid_requests']}\n"
        f"📅 Premium до: {user['premium_until']}"
    )

# 💳 PAY
@dp.message(Command("pay"))
async def pay(message: types.Message):

    keyboard = types.InlineKeyboardMarkup(
        inline_keyboard=[
            [
                types.InlineKeyboardButton(
                    text="💎 100 запросов / 1 месяц — 2.5 USDT",
                    callback_data="buy_start"
                )
            ],
            [
                types.InlineKeyboardButton(
                    text="🚀 400 запросов / 3 месяца — 6 USDT",
                    callback_data="buy_pro"
                )
            ]
        ]
    )

    await message.answer(
        "💳 Выбери тариф:",
        reply_markup=keyboard
    )

# 💎 START PLAN
@dp.callback_query(lambda c: c.data == "buy_start")
async def buy_start(callback: types.CallbackQuery):

    invoice = await crypto.create_invoice(
        asset="USDT",
        amount=2.5,
        description="START PLAN"
    )

    cursor.execute(
        "INSERT INTO invoices VALUES (?, ?, ?)",
        (
            invoice.invoice_id,
            callback.from_user.id,
            "START"
        )
    )

    conn.commit()

    keyboard = types.InlineKeyboardMarkup(
        inline_keyboard=[
            [
                types.InlineKeyboardButton(
                    text="💳 Оплатить",
                    url=invoice.bot_invoice_url
                )
            ]
        ]
    )

    await callback.message.answer(
        "💎 Нажми кнопку для оплаты START тарифа",
        reply_markup=keyboard
    )

# 🚀 PRO PLAN
@dp.callback_query(lambda c: c.data == "buy_pro")
async def buy_pro(callback: types.CallbackQuery):

    invoice = await crypto.create_invoice(
        asset="USDT",
        amount=6,
        description="PRO PLAN"
    )

    cursor.execute(
        "INSERT INTO invoices VALUES (?, ?, ?)",
        (
            invoice.invoice_id,
            callback.from_user.id,
            "PRO"
        )
    )

    conn.commit()

    keyboard = types.InlineKeyboardMarkup(
        inline_keyboard=[
            [
                types.InlineKeyboardButton(
                    text="💳 Оплатить",
                    url=invoice.bot_invoice_url
                )
            ]
        ]
    )

    await callback.message.answer(
        "🚀 Нажми кнопку для оплаты PRO тарифа",
        reply_markup=keyboard
    )

# ✅ CHECK PAYMENT
@dp.message(Command("check"))
async def check(message: types.Message):

    user_id = message.from_user.id

    invoices = await crypto.get_invoices(
        status="paid"
    )

    for invoice in invoices.items:

        cursor.execute(
            "SELECT * FROM invoices WHERE invoice_id=?",
            (invoice.invoice_id,)
        )

        db_invoice = cursor.fetchone()

        if db_invoice is None:
            continue

        if db_invoice["user_id"] != user_id:
            continue

        tariff = db_invoice["tariff"]

        # 💎 START
        if tariff == "START":

            premium_until = (
                datetime.now() + timedelta(days=30)
            ).strftime("%Y-%m-%d")

            cursor.execute("""
            UPDATE users
            SET
                paid_requests = paid_requests + 100,
                premium_until = ?,
                tariff = 'START'
            WHERE user_id = ?
            """, (
                premium_until,
                user_id
            ))

        # 🚀 PRO
        elif tariff == "PRO":

            premium_until = (
                datetime.now() + timedelta(days=90)
            ).strftime("%Y-%m-%d")

            cursor.execute("""
            UPDATE users
            SET
                paid_requests = paid_requests + 400,
                premium_until = ?,
                tariff = 'PRO'
            WHERE user_id = ?
            """, (
                premium_until,
                user_id
            ))

        conn.commit()

        await message.answer(
            "✅ Оплата найдена!\n\n"
            "Premium активирован 🚀"
        )

        return

    await message.answer(
        "❌ Оплата пока не найдена"
    )

# 🤖 AI
@dp.message(lambda message: message.text and not message.text.startswith("/"))
async def ai(message: types.Message):

    user_id = message.from_user.id

    cursor.execute(
        "SELECT * FROM users WHERE user_id=?",
        (user_id,)
    )

    user = cursor.fetchone()

    # 👤 NEW USER
    if user is None:

        cursor.execute("""
        INSERT INTO users (
            user_id,
            free_requests,
            paid_requests,
            premium_until,
            tariff
        )
        VALUES (?, ?, ?, ?, ?)
        """, (
            user_id,
            0,
            0,
            "",
            "FREE"
        ))

        conn.commit()

        cursor.execute(
            "SELECT * FROM users WHERE user_id=?",
            (user_id,)
        )

        user = cursor.fetchone()

    # 📅 PREMIUM CHECK
    premium_active = False

    if user["premium_until"]:

        try:

            premium_date = datetime.strptime(
                user["premium_until"],
                "%Y-%m-%d"
            )

            if premium_date > datetime.now():
                premium_active = True

        except:
            pass

    # 💎 PREMIUM REQUESTS
    if premium_active and user["paid_requests"] > 0:

        cursor.execute("""
        UPDATE users
        SET paid_requests = paid_requests - 1
        WHERE user_id=?
        """, (user_id,))

        conn.commit()

    else:

        # 🎁 FREE LIMIT
        if user["free_requests"] >= FREE_LIMIT:

            await message.answer(
                "⛔ Лимит закончился\n\n"
                "💳 Используй /pay"
            )

            return

        cursor.execute("""
        UPDATE users
        SET free_requests = free_requests + 1
        WHERE user_id=?
        """, (user_id,))

        conn.commit()

    # 🧠 OPENAI
    try:

        response = client.responses.create(
            model="gpt-4.1-mini",
            input=[
                {
                    "role": "system",
                    "content": (
                        "Ты AI помощник для студентов. "
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

        await message.answer(answer)

    except Exception as e:

        await message.answer(
            f"Ошибка: {e}"
        )

# 🚀 RUN
async def main():

    print("Бот запущен 🚀")

    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
```
