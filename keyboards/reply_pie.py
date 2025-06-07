def get_main_keyboard():
    return ReplyKeyboardMarkup(resize_keyboard=True).add(
        KeyboardButton("💳 Оплата"),
        KeyboardButton("🌱 Поради по догляду"),
        KeyboardButton("📝 Відгук"),
        KeyboardButton("🚚 Доставка")
    ).add(
        KeyboardButton("📦 Списання квітів"),
        KeyboardButton("💬 Онлайн-чат для клієнта"),
        KeyboardButton("📝 Завдання")
    )
