from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ContentType

# Стани форми списання квітів
class WriteOffForm(StatesGroup):
    store = State()
    florist_name = State()
    flower_name = State()
    flower_height = State()
    flower_price = State()
    photo = State()
    confirm_more = State()

# Клавіатура магазинів
store_keyboard = ReplyKeyboardMarkup(resize_keyboard=True).add(
    KeyboardButton("Пасаж"),
    KeyboardButton("Ломоносова"),
    KeyboardButton("Теремки"),
    KeyboardButton("Пулюя")
)

# Клавіатура дій
action_keyboard = ReplyKeyboardMarkup(resize_keyboard=True).add(
    KeyboardButton("➕ Додати ще"),
    KeyboardButton("✅ Завершити")
)

def register_writeoff_handlers(dp: Dispatcher):
    @dp.message_handler(lambda msg: msg.text == "📦 Списання квітів", state="*")
    async def start_writeoff(message: types.Message, state: FSMContext):
        await message.answer("📍 Виберіть магазин:", reply_markup=store_keyboard)
        await WriteOffForm.store.set()

    @dp.message_handler(state=WriteOffForm.store)
    async def get_store(message: types.Message, state: FSMContext):
        await state.update_data(store=message.text)
        await message.answer("👩‍🎨 Введіть ім’я та прізвище флориста:")
        await WriteOffForm.florist_name.set()

    @dp.message_handler(state=WriteOffForm.florist_name)
    async def get_florist_name(message: types.Message, state: FSMContext):
        await state.update_data(florist_name=message.text)
        await message.answer("🌸 Назва квітки:")
        await WriteOffForm.flower_name.set()

    @dp.message_handler(state=WriteOffForm.flower_name)
    async def get_flower_name(message: types.Message, state: FSMContext):
        await state.update_data(flower_name=message.text)
        await message.answer("📏 Зріст квітки (в см):")
        await WriteOffForm.flower_height.set()

    @dp.message_handler(state=WriteOffForm.flower_height)
    async def get_height(message: types.Message, state: FSMContext):
        await state.update_data(flower_height=message.text)
        await message.answer("💰 Ціна на вітрині (грн):")
        await WriteOffForm.flower_price.set()

    @dp.message_handler(state=WriteOffForm.flower_price)
    async def get_price(message: types.Message, state: FSMContext):
        await state.update_data(flower_price=message.text)
        await message.answer("📸 Надішліть фото списаної квітки:")
        await WriteOffForm.photo.set()

    @dp.message_handler(state=WriteOffForm.photo, content_types=ContentType.PHOTO)
    async def get_photo(message: types.Message, state: FSMContext):
        data = await state.get_data()

        flower_data = {
            "flower_name": data["flower_name"],
            "flower_height": data["flower_height"],
            "flower_price": data["flower_price"],
            "photo_id": message.photo[-1].file_id
        }

        flower_list = data.get("flower_list", [])
        flower_list.append(flower_data)
        await state.update_data(flower_list=flower_list)

        await message.answer("✅ Записано. Додати ще одну квітку чи завершити?", reply_markup=action_keyboard)
        await WriteOffForm.confirm_more.set()

    @dp.message_handler(lambda msg: msg.text == "➕ Додати ще", state=WriteOffForm.confirm_more)
    async def add_another_flower(message: types.Message, state: FSMContext):
        await message.answer("🌸 Назва квітки:")
        await WriteOffForm.flower_name.set()

    @dp.message_handler(lambda msg: msg.text == "✅ Завершити", state=WriteOffForm.confirm_more)
    async def finish_writeoff(message: types.Message, state: FSMContext):
        data = await state.get_data()

        summary_text = (
            f"📦 *Списання квітів*\n\n"
            f"🏪 Магазин: {data['store']}\n"
            f"👩‍🎨 Флорист: {data['florist_name']}\n"
            f"📅 Списано квітів: {len(data['flower_list'])}"
        )

        admin_chat_id = -1002580389822  # 🔁 Замінити на ваш ID групи

        await message.answer("📤 Надсилаємо звіт адміністратору...")

        for flower in data["flower_list"]:
            caption = (
                f"🌸 *{flower['flower_name']}*\n"
                f"📏 Зріст: {flower['flower_height']} см\n"
                f"💰 Ціна: {flower['flower_price']} грн"
            )
            await message.bot.send_photo(admin_chat_id, photo=flower["photo_id"], caption=caption, parse_mode="Markdown")

        await message.bot.send_message(admin_chat_id, summary_text, parse_mode="Markdown")
        await message.answer("✅ Списання завершено.")
        await state.finish()
