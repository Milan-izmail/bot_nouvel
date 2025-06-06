from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def get_main_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📦 Списання квітів")],
            [KeyboardButton(text="🌿 Поради по догляду")],
        ],
        resize_keyboard=True
    )
