from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import Dispatcher
from aiogram.types import CallbackQuery

from keyboards.reply_pie import get_main_menu_keyboard
from keyboards.inline_pie import get_shop_keyboard, get_back_keyboard

# --- FSM States ---
class TaskForm(StatesGroup):
    choosing_shop = State()
    entering_florist = State()
    uploading_photo = State()

# --- Реєстрація хендлерів ---
def register_task_handlers(dp: Dispatcher, bot, admin_chat_id: int):
    
    # --- Start Task ---
    @dp.message_handler(lambda msg: msg.text == "📦 Списання квітів", state=None)
    async def start_task(message: types.Message, state: FSMContext):
        await state.set_state(TaskForm.choosing_shop.state)
        await message.answer("📍 Виберіть магазин:", reply_markup=get_shop_keyboard())

    # --- Handle Shop Selection ---
    @dp.callback_query_handler(lambda c: c.data.startswith("shop_"), state=TaskForm.choosing_shop)
    async def handle_shop_selection(callback: CallbackQuery, state: FSMContext):
        await state.update_data(shop=callback.data)
        await state.set_state(TaskForm.entering_florist.state)
        await callback.message.answer("👤 Введіть ім’я та прізвище флориста:", reply_markup=get_back_keyboard())
        await state.finish()
        await callback.message.answer("🔙 Повернення до головного меню", reply_markup=reply_pie.get_main_menu_keyboard())
        await callback.answer()
        
    # --- Enter Florist Name ---
    @dp.message_handler(state=TaskForm.entering_florist)
    async def handle_florist_name(message: types.Message, state: FSMContext):
        florist_name = message.text
        data = await state.get_data()
        shop = data.get("shop")

        # Можна зберігати або надсилати кудись
        await message.answer(
            f"✅ Списання розпочато.\nМагазин: {shop}\nФлорист: {florist_name}",
            reply_markup=get_main_keyboard()
        )

        await state.finish()
