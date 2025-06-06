from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def get_main_menu_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📦 Списання квітів"), KeyboardButton(text="📝 Завдання")],
            [KeyboardButton(text="📤 Оплата"), KeyboardButton(text="🌱 Поради по догляду")],
            [KeyboardButton(text="📦 Доставка"), KeyboardButton(text="✉️ Відгук")],
            [KeyboardButton(text="💬 Онлайн-чат для клієнта")]
        ],
        resize_keyboard=True
    )
