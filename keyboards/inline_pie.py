from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_shop_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Пасаж", callback_data="Пасаж")],
        [InlineKeyboardButton(text="Ломоносова", callback_data="Ломоносова")]
    ])

def get_back_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Назад", callback_data="back")]
    ])
