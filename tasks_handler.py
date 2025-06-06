from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InputFile
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from keyboards.reply import get_main_keyboard
from keyboards.inline import get_shop_keyboard, get_back_keyboard


router = Router()

# --- FSM States ---
class TaskForm(StatesGroup):
    choosing_shop = State()
    entering_florist = State()
    uploading_photo = State()

# --- Start Task ---
@router.message(F.text.lower() == "📦 списання квітів")
async def start_task(message: Message, state: FSMContext):
    await state.set_state(TaskForm.choosing_shop)
    await message.answer("📍 Виберіть магазин:", reply_markup=get_shop_keyboard())

# --- Handle Shop Selection ---
@router.callback_query(TaskForm.choosing_shop)
async def handle_shop_selection(callback: CallbackQuery, state: FSMContext):
    await state.update_data(shop=callback.data)
    await state.set_state(TaskForm.entering_florist)
    await callback.message.edit_text("👩‍🎨 Введіть ім'я та прізвище флориста:", reply_markup=get_back_keyboard())
    await callback.answer()

# --- Handle Florist Input ---
@router.message(TaskForm.entering_florist, F.text)
async def handle_florist_input(message: Message, state: FSMContext):
    await state.update_data(florist=message.text)
    await state.set_state(TaskForm.uploading_photo)
    await message.answer("📷 Завантажте фото", reply_markup=get_back_keyboard())

# --- Handle Photo Upload ---
@router.message(TaskForm.uploading_photo, F.photo)
async def handle_photo_upload(message: Message, state: FSMContext):
    photo_id = message.photo[-1].file_id
    data = await state.get_data()

    summary = (
        f"✅ Завдання збережено!\n"
        f"🏬 Магазин: {data['shop']}\n"
        f"👤 Флорист: {data['florist']}"
    )

    await message.answer_photo(photo_id, caption=summary, reply_markup=get_main_keyboard())
    await state.clear()

# --- Кнопка "Назад" ---
@router.callback_query(F.data == "back")
async def go_back(callback: CallbackQuery, state: FSMContext):
    current = await state.get_state()

    if current == TaskForm.uploading_photo:
        await state.set_state(TaskForm.entering_florist)
        await callback.message.edit_text("👩‍🎨 Введіть ім'я та прізвище флориста:", reply_markup=get_back_keyboard())
    elif current == TaskForm.entering_florist:
        await state.set_state(TaskForm.choosing_shop)
        await callback.message.edit_text("📍 Виберіть магазин:", reply_markup=get_shop_keyboard())
    else:
        await state.clear()
        await callback.message.answer("Операція скасована", reply_markup=get_main_keyboard())

    await callback.answer()
