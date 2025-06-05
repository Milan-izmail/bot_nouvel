from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ContentType

# --- Стан машини ---
class OrderForm(StatesGroup):
    client_name = State()
    client_phone = State()
    recipient_phone = State()
    delivery_type = State()
    delivery_address = State()
    delivery_date = State()
    delivery_time = State()
    prepayment_amount = State()
    remaining_payment = State()
    prepayment_method = State()
    payment_method = State()
    check_photo = State()

# --- Реєстрація обробників ---
def register_order_handlers(dp: Dispatcher):
    @dp.message_handler(lambda msg: msg.text == "📝 Завдання", state="*")
    async def start_order(message: types.Message, state: FSMContext):
        await message.answer("📝 Введіть ім’я клієнта:")
        await OrderForm.client_name.set()

    @dp.message_handler(state=OrderForm.client_name)
    async def get_client_name(message: types.Message, state: FSMContext):
        await state.update_data(client_name=message.text)
        await message.answer("📞 Введіть номер телефону клієнта:")
        await OrderForm.client_phone.set()

    @dp.message_handler(state=OrderForm.client_phone)
    async def get_client_phone(message: types.Message, state: FSMContext):
        await state.update_data(client_phone=message.text)
        await message.answer("📞 Введіть номер телефону отримувача:")
        await OrderForm.recipient_phone.set()

    @dp.message_handler(state=OrderForm.recipient_phone)
    async def get_recipient_phone(message: types.Message, state: FSMContext):
        await state.update_data(recipient_phone=message.text)
        await message.answer("🚚 Самовивіз чи доставка?")
        await OrderForm.delivery_type.set()

    @dp.message_handler(state=OrderForm.delivery_type)
    async def get_delivery_type(message: types.Message, state: FSMContext):
        await state.update_data(delivery_type=message.text)
        await message.answer("🏠 Введіть адресу доставки:")
        await OrderForm.delivery_address.set()

    @dp.message_handler(state=OrderForm.delivery_address)
    async def get_address(message: types.Message, state: FSMContext):
        await state.update_data(delivery_address=message.text)
        await message.answer("📅 Введіть дату доставки:")
        await OrderForm.delivery_date.set()

    @dp.message_handler(state=OrderForm.delivery_date)
    async def get_date(message: types.Message, state: FSMContext):
        await state.update_data(delivery_date=message.text)
        await message.answer("⏰ Введіть час доставки (з - до):")
        await OrderForm.delivery_time.set()

    @dp.message_handler(state=OrderForm.delivery_time)
    async def get_time(message: types.Message, state: FSMContext):
        await state.update_data(delivery_time=message.text)
        await message.answer("💵 Сума передплати:")
        await OrderForm.prepayment_amount.set()

    @dp.message_handler(state=OrderForm.prepayment_amount)
    async def get_prepayment(message: types.Message, state: FSMContext):
        await state.update_data(prepayment_amount=message.text)
        await message.answer("💰 Залишок до сплати:")
        await OrderForm.remaining_payment.set()

    @dp.message_handler(state=OrderForm.remaining_payment)
    async def get_remaining(message: types.Message, state: FSMContext):
        await state.update_data(remaining_payment=message.text)
        await message.answer("💳 Форма передплати (готівка / безготівка):")
        await OrderForm.prepayment_method.set()

    @dp.message_handler(state=OrderForm.prepayment_method)
    async def get_prepayment_method(message: types.Message, state: FSMContext):
        await state.update_data(prepayment_method=message.text)
        await message.answer("💳 Форма доплати (готівка / безготівка):")
        await OrderForm.payment_method.set()

    @dp.message_handler(state=OrderForm.payment_method)
    async def get_payment_method(message: types.Message, state: FSMContext):
        await state.update_data(payment_method=message.text)
        await message.answer("📸 Надішліть фото чека передплати:")
        await OrderForm.check_photo.set()

    @dp.message_handler(state=OrderForm.check_photo, content_types=ContentType.PHOTO)
    async def get_check_photo(message: types.Message, state: FSMContext):
        await state.update_data(check_photo=message.photo[-1].file_id)

        data = await state.get_data()
        text = (
            f"📝 НОВЕ ЗАВДАННЯ:\n\n"
            f"👤 Клієнт: {data['client_name']}\n"
            f"📞 Телефон клієнта: {data['client_phone']}\n"
            f"📞 Телефон отримувача: {data['recipient_phone']}\n"
            f"🚚 Спосіб: {data['delivery_type']}\n"
            f"🏠 Адреса: {data['delivery_address']}\n"
            f"📅 Дата: {data['delivery_date']}\n"
            f"⏰ Час: {data['delivery_time']}\n"
            f"💵 Передплата: {data['prepayment_amount']} грн\n"
            f"💰 Залишок: {data['remaining_payment']} грн\n"
            f"💳 Форма передплати: {data['prepayment_method']}\n"
            f"💳 Форма доплати: {data['payment_method']}\n"
            f"📌 *Не забудьте внести замовлення в ПАПЕРОВИЙ журнал*"
        )

        # 🔔 Надсилання до адмін-групи (заміни на свій chat_id)
        admin_chat_id = -1002580389822
        await message.bot.send_photo(chat_id=admin_chat_id, photo=data['check_photo'], caption=text, parse_mode="Markdown")

        await message.answer("✅ Завдання збережено. Дякуємо!")
        await state.finish()
