from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_shop_keyboard():
    return InlineKeyboardMarkup().add(
        InlineKeyboardButton("Пасаж", callback_data="shop_passage"),
        InlineKeyboardButton("Ломоносова", callback_data="shop_lomonosova")
    )

def get_back_keyboard():
    return InlineKeyboardMarkup().add(
        InlineKeyboardButton("⬅️ Назад", callback_data="go_back")
    )
