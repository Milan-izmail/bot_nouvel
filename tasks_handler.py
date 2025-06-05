from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ContentType

# Кнопки для вибору магазину
shop_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
shop_keyboard.add("Пасаж", "Ломоносова").add("Пулюя", "Теремки")

# Кнопка назад
back_keyboard = ReplyKeyboardMarkup(resize_keyboard=True).add(KeyboardButton("🔙 Назад до меню"))

class TaskForm(StatesGroup):
    shop = State()
    florist = State()
    flower_name = State()
    flower_height = State()
    flower_price = State()
    flower_quantity = State()
    flower_photo = State()
    confirm_more = State()

def register_task_handlers(dp: Dispatcher, bot, admin_chat_id: int):
    @dp.message_handler(lambda msg: msg.text == "📝 Завдання", state="*")
    async def start_task(message: types.Message, state: FSMContext):
        await message.answer("🏪 Оберіть магазин:", reply_markup=shop_keyboard)
        await TaskForm.shop.set()

    @dp.message_handler(state=TaskForm.shop)
    async def get_shop(message: types.Message, state: FSMContext):
        await state.update_data(shop=message.text)
        await message.answer("👤 Введіть ім’я флориста:", reply_markup=back_keyboard)
        await TaskForm.florist.set()

    @dp.message_handler(state=TaskForm.florist)
    async def get_florist(message: types.Message, state: FSMContext):
        await state.update_data(florist=message.text)
        await message.answer("🌸 Назва квітки:")
        await TaskForm.flower_name.set()

    @dp.message_handler(state=TaskForm.flower_name)
    async def get_flower_name(message: types.Message, state: FSMContext):
        await state.update_data(flower_name=message.text)
        await message.answer("📏 Зріст квітки (см):")
        await TaskForm.flower_height.set()

    @dp.message_handler(state=TaskForm.flower_height)
    async def get_flower_height(message: types.Message, state: FSMContext):
        await state.update_data(flower_height=message.text)
        await message.answer("💵 Ціна на вітрині (грн):")
        await TaskForm.flower_price.set()

    @dp.message_handler(state=TaskForm.flower_price)
    async def get_flower_price(message: types.Message, state: FSMContext):
        await state.update_data(flower_price=message.text)
        await message.answer("🔢 Кількість:")
        await TaskForm.flower_quantity.set()

    @dp.message_handler(state=TaskForm.flower_quantity)
    async def get_flower_quantity(message: types.Message, state: FSMContext):
        await state.update_data(flower_quantity=message.text)
        await message.answer("📷 Надішліть фото:")
        await TaskForm.flower_photo.set()

    @dp.message_handler(state=TaskForm.flower_photo, content_types=ContentType.PHOTO)
    async def get_flower_photo(message: types.Message, state: FSMContext):
        await state.update_data(flower_photo=message.photo[-1].file_id)

        data = await state.get_data()

        # Текст звіту
        task_report = (
            f"📝 *Списання квітів (Завдання)*\n\n"
            f"🏪 Магазин: {data['shop']}\n"
            f"👤 Флорист: {data['florist']}\n"
            f"🌸 Квітка: {data['flower_name']}\n"
            f"📏 Зріст: {data['flower_height']} см\n"
            f"💵 Ціна: {data['flower_price']} грн\n"
            f"🔢 Кількість: {data['flower_quantity']}"
        )

        await bot.send_photo(chat_id=admin_chat_id, photo=data['flower_photo'], caption=task_report, parse_mode="Markdown")

        await message.answer("➕ Додати ще одну квітку?", reply_markup=ReplyKeyboardMarkup(resize_keyboard=True).add("Так", "Ні"))
        await TaskForm.confirm_more.set()

    @dp.message_handler(state=TaskForm.confirm_more)
    async def handle_confirm_more(message: types.Message, state: FSMContext):
        if message.text.lower() == "так":
            await message.answer("🌸 Назва квітки:")
            await TaskForm.flower_name.set()
        else:
            await message.answer("✅ Завдання завершено. Повертаємось до меню.", reply_markup=back_keyboard)
            await state.finish()
