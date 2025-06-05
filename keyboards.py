from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup

# --- Головне меню ---
main_menu = ReplyKeyboardMarkup(resize_keyboard=True)
main_menu.add(
    KeyboardButton("💳 Оплата"),
    KeyboardButton("🌱 Поради по догляду"),
    KeyboardButton("📝 Відгук"),
    KeyboardButton("🚚 Доставка")
)
main_menu.add(KeyboardButton("📦 Списання квітів"))

# --- Клавіатура магазинів ---
store_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
store_keyboard.add(
    KeyboardButton("Пасаж"),
    KeyboardButton("Ломоносова"),
    KeyboardButton("Теремки"),
    KeyboardButton("Пулюя")
)
store_keyboard.add(KeyboardButton("🔙 Назад"))

# --- Відгуки (Google Maps) ---
review_keyboard = InlineKeyboardMarkup(row_width=2).add(
    InlineKeyboardButton("Пасаж", url="https://maps.app.goo.gl/J1nCe2tDGvehh5Nb8"),
    InlineKeyboardButton("Ломоносова", url="https://maps.app.goo.gl/nb1HeQK5JAnSzTHd6"),
    InlineKeyboardButton("Теремки", url="https://maps.app.goo.gl/6frLtZkuFHz9tmGJ7"),
    InlineKeyboardButton("Пулюя", url="https://maps.app.goo.gl/9vq2w9rpnhWYGpB49")
)
