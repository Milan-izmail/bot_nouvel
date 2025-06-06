from aiogram import Bot, Dispatcher, types
from aiogram.types import (
from keyboards.inline_pie import get_shop_keyboard, get_back_keyboard
from keyboards.replay_pie import get_main_menu_keyboard
ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)
from aiogram.utils import executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import os
from dotenv import load_dotenv

from mono_api import create_payment_url
from intent_matcher import match_intent
from gpt_assistant import ask_gpt
from writeoff_handler import register_writeoff_handlers
from order_handler import register_order_handlers
from tasks_handler import register_task_handlers

# --- Ініціалізація ---
load_dotenv()
bot = Bot(token=os.getenv("BOT_TOKEN"))
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# --- Меню ---
main_menu = ReplyKeyboardMarkup(resize_keyboard=True)
main_menu.add(
    KeyboardButton("💳 Оплата"),
    KeyboardButton("🌱 Поради по догляду"),
    KeyboardButton("📝 Відгук"),
    KeyboardButton("🚚 Доставка")
)
main_menu.add(
    KeyboardButton("📦 Списання квітів"),
    KeyboardButton("💬 Онлайн-чат для клієнта"),
    KeyboardButton("📝 Завдання")
)

# --- Google-відгуки ---
review_keyboard = InlineKeyboardMarkup(row_width=2).add(
    InlineKeyboardButton("Пасаж", url="https://maps.app.goo.gl/J1nCe2tDGvehh5Nb8"),
    InlineKeyboardButton("Ломоносова", url="https://maps.app.goo.gl/nb1HeQK5JAnSzTHd6"),
    InlineKeyboardButton("Теремки", url="https://maps.app.goo.gl/6frLtZkuFHz9tmGJ7"),
    InlineKeyboardButton("Пулюя", url="https://maps.app.goo.gl/9vq2w9rpnhWYGpB49")
)

# --- /start ---
@dp.message_handler(commands=['start'])
async def handle_start(message: types.Message):
    await message.answer(
        "👋 Вітаю команду *Nouvel Amour Flowers*!\n\n"
        "Я ваш бот-помічник. Можу:\n"
        "• Надати поради по догляду 🌿\n"
        "• Створити посилання на оплату 💳\n"
        "• Дати посилання на Google-відгуки 📝\n"
        "• Допомогти зі списанням квітів 📦\n"
        "• Оформити завдання 📝\n"
        "• Відправити клієнту чат підтримки 💬",
        reply_markup=main_menu,
        parse_mode="Markdown"
    )

# --- Онлайн-чат для клієнта ---
@dp.message_handler(lambda message: message.text == "💬 Онлайн-чат для клієнта")
async def handle_support_chat(message: types.Message):
    await message.reply(
        "📨 Онлайн-чат підтримки для клієнта:\n"
        "Скопіюйте або перешліть це посилання клієнту:\n"
        "👉 https://widgets.binotel.com/w/chat/pages/?wgt=eNtZkyFjj9JvMSr4IJd0"
    )

# --- Доставка ---
@dp.message_handler(lambda message: message.text == "🚚 Доставка")
async def handle_delivery(message: types.Message):
    keyboard = InlineKeyboardMarkup().add(
        InlineKeyboardButton("📋 Як пояснити клієнту", callback_data="explain_delivery")
    )
    await message.reply(
        "🚚 Політика доставки по Києву:\n\n"
        "• Базова доставка — 190 грн\n"
        "• В негоду або в години пік — 290–390 грн\n"
        "• Максимум для клієнта — 490 грн\n"
        "• Безкоштовно — від суми 2500 грн\n"
        "• Під час тривоги — затримка, але без доплат\n"
        "• Комфорт Таун — спецтарифи\n\n"
        "✅ Ми прагнемо чесного сервісу без прихованих платежів.",
        reply_markup=keyboard
    )

@dp.callback_query_handler(lambda c: c.data == "explain_delivery")
async def explain_delivery_callback(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(
        callback_query.from_user.id,
        "📋 Як пояснити клієнту:\n\n"
        "– Основний тариф: 190 грн\n"
        "– В негоду або годину пік — до 490 грн\n"
        "– Якщо замовлення > 2500 грн — доставка безкоштовна\n"
        "– Ми не беремо доплат під час повітряної тривоги\n"
        "– Остаточна ціна завжди погоджується наперед"
    )

# --- Обробка всіх інших повідомлень ---
fsm_buttons = ["📦 Списання квітів", "📝 Завдання"]

@dp.message_handler(lambda msg: msg.text not in fsm_buttons, state=None)
async def handle_message(message: types.Message):
    text = message.text.strip().lower()
    admin_chat_id = -1002580389822
    user_info = f"{message.from_user.full_name} ({message.from_user.id})"
    log_message = f"📩 Запит від {user_info}:\n{text}"
    await bot.send_message(admin_chat_id, log_message)

    intent = match_intent(text)

    if intent == "payment_request":
        await message.reply("💳 Напишіть суму для оплати у форматі: `оплата 300` або просто число", parse_mode="Markdown")

    elif text.startswith("оплата") or text.isdigit():
        try:
            amount = int(text.replace("оплата", "").strip())
            url = create_payment_url(amount)
            if url.startswith("http"):
                keyboard = InlineKeyboardMarkup().add(
                    InlineKeyboardButton(f"Оплатити {amount} грн", url=url)
                )
                await message.reply("✅ Ось ваше посилання для оплати:", reply_markup=keyboard)
            else:
                await message.reply(url)
        except Exception:
            await message.reply("⚠️ Не вдалося розпізнати суму. Напишіть у форматі: `оплата 300` або просто число.")

    elif intent == "care_advice":
        await message.reply("🌱 Напишіть назву квітки або вазона, і я підкажу, як за нею доглядати.")

    elif intent == "thank_you":
        await message.reply("💐 Радий допомогти! Якщо клієнт був задоволений — запропонуйте залишити відгук:", reply_markup=review_keyboard)

    elif intent == "review_request":
        await message.reply("📝 Оберіть магазин для відгуку:", reply_markup=review_keyboard)

    elif intent == "greeting":
        await message.reply("👋 Привіт, колего! Оберіть дію з меню або напишіть, чим можу допомогти.")

    else:
        await message.reply("🧠 Готую пораду... Трохи терпіння 🌿")
        gpt_reply = ask_gpt(text)
        await message.reply(gpt_reply)

# --- Запуск ---
if __name__ == "__main__":
    register_writeoff_handlers(dp)
    register_order_handlers(dp)
    register_task_handlers(dp, bot, admin_chat_id=-1002580389822)
    executor.start_polling(dp, skip_updates=True)
