import os
import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
import datetime

# --- Конфигурация токена и ID администратора ---
TOKEN = os.getenv('BOT_TOKEN')
ADMIN_ID = int(os.getenv('ADMIN_ID', '123456789'))  # В .env задать BOT_TOKEN и ADMIN_ID

bot = Bot(token=TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# --- Все тексты блоков и услуг вынесены сюда ---
ABOUT_TEXT = "🤖 О компании\n\nКраткое описание компании и ваших преимуществ. (Текст легко изменить здесь)"
SERVICES_TEXT = "🛠️ Наши услуги:\n\nВыберите нужную услугу для заказа."
ADVANTAGE_TEXT = "🔥 Ваша выгода\n\nУТП и конкурентные преимущества вашего бота/сервиса."
CONTACTS_TEXT = "📞 Контакты\n\nг. Москва, ул. Примерная, д.1\nТел: +7 900 123-45-67\n@your_support"

# --- Описание и стоимость услуг ---
SERVICE_LIST = [
    {
        "name": "Бот + инструкция по доработке и размещению",
        "price": "3000 руб.",
        "desc": "Готовый бот + подробная инструкция по доработке и размещению.",
        "cb": "order_bot"
    },
    {
        "name": "Разовая настройка и размещение бота",
        "price": "5000 руб.",
        "desc": "Всё сделаем за вас под ключ.",
        "cb": "order_setup"
    },
    {
        "name": "Подписка на бота (разовая настройка + поддержка)",
        "price": "5000 руб. + 1000 руб/мес.",
        "desc": "Настройка, размещение и ежемесячная поддержка с 1 правкой в месяц.",
        "cb": "order_sub"
    },
]

# --- FSM для сбора контактов при заказе услуги и консультации ---
class OrderForm(StatesGroup):
    waiting_for_phone = State()

class ConsultForm(StatesGroup):
    waiting_for_name = State()
    waiting_for_phone = State()
    waiting_for_date = State()
    waiting_for_time = State()

# --- Главное меню (можно менять порядок) ---
def main_menu():
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="О компании", callback_data="about")],
        [InlineKeyboardButton(text="Услуги", callback_data="services")],
        [InlineKeyboardButton(text="Записаться на консультацию", callback_data="consult")],
        [InlineKeyboardButton(text="Ваша выгода", callback_data="advantage")],
        [InlineKeyboardButton(text="Контакты", callback_data="contacts")]
    ])
    return kb

# --- Запуск бота, стартовое сообщение ---
@dp.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("Добро пожаловать!\nВыберите интересующий раздел:", reply_markup=main_menu())

@dp.callback_query(F.data == "about")
async def about_handler(call: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await call.message.answer(ABOUT_TEXT, reply_markup=main_menu())
    await call.answer()

@dp.callback_query(F.data == "services")
async def services_handler(call: types.CallbackQuery, state: FSMContext):
    await state.clear()
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(
                text=f"{s['name']} — {s['price']}", callback_data=s["cb"]
            )] for s in SERVICE_LIST
        ] + [[InlineKeyboardButton(text="⬅️ Главное меню", callback_data="start")]]
    )
    await call.message.answer(SERVICES_TEXT, reply_markup=kb)
    await call.answer()

# --- Заказ любой услуги (через 1 форму, узнаем телефон) ---
@dp.callback_query(lambda c: c.data.startswith("order_"))
async def order_service_start(call: types.CallbackQuery, state: FSMContext):
    await state.clear()
    service = next((s for s in SERVICE_LIST if s["cb"] == call.data), None)
    if not service:
        await call.message.answer("Ошибка выбора услуги. Попробуйте снова.")
        return
    await state.update_data(service_name=service['name'])
    await call.message.answer(
        f"Вы выбрали: <b>{service['name']}</b>\nСтоимость: {service['price']}\n\n"
        "Опишите кратко задачу (или оставьте поле пустым):\n"
        "Пожалуйста, укажите ваш номер телефона для связи:",
        parse_mode="HTML"
    )
    await state.set_state(OrderForm.waiting_for_phone)
    await call.answer()

@dp.message(OrderForm.waiting_for_phone)
async def order_get_phone(message: types.Message, state: FSMContext):
    phone = message.text.strip()
    data = await state.get_data()
    msg = (
        f"🆕 <b>Новая заявка на услугу</b>\n"
        f"Услуга: {data.get('service_name','')}\n"
        f"Телефон: {phone}\n"
        f"От: {message.from_user.first_name} (@{message.from_user.username or 'нет username'})"
    )
    await message.answer("✅ Заявка отправлена! Мы свяжемся с вами в ближайшее время.", reply_markup=main_menu())
    await bot.send_message(ADMIN_ID, msg, parse_mode="HTML")
    await state.clear()

# --- Блок "Ваша выгода" ---
@dp.callback_query(F.data == "advantage")
async def advantage_handler(call: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await call.message.answer(ADVANTAGE_TEXT, reply_markup=main_menu())
    await call.answer()

# --- Контакты ---
@dp.callback_query(F.data == "contacts")
async def contacts_handler(call: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await call.message.answer(CONTACTS_TEXT, reply_markup=main_menu())
    await call.answer()

# --- Календарь (упрощённый) и запись на консультацию ---
@dp.callback_query(F.data == "consult")
async def consult_start(call: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await call.message.answer("Укажите ваше имя:")
    await state.set_state(ConsultForm.waiting_for_name)
    await call.answer()

@dp.message(ConsultForm.waiting_for_name)
async def consult_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text.strip())
    await message.answer("Введите номер телефона:")
    await state.set_state(ConsultForm.waiting_for_phone)

@dp.message(ConsultForm.waiting_for_phone)
async def consult_phone(message: types.Message, state: FSMContext):
    await state.update_data(phone=message.text.strip())
    # Календарь — спрашиваем дату в формате ДД.ММ.ГГГГ (простая валидация)
    await message.answer("Выберите дату консультации (ДД.ММ.ГГГГ):")
    await state.set_state(ConsultForm.waiting_for_date)

@dp.message(ConsultForm.waiting_for_date)
async def consult_date(message: types.Message, state: FSMContext):
    try:
        date = datetime.datetime.strptime(message.text.strip(), "%d.%m.%Y")
        if date.date() < datetime.date.today():
            raise ValueError
    except Exception:
        await message.answer("Введите дату в формате ДД.ММ.ГГГГ (например, 20.07.2025):")
        return
    await state.update_data(date=message.text.strip())
    # Часы — простое меню
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=f"{h}:00", callback_data=f"consult_time_{h}")]
            for h in range(10, 20)
        ]
    )
    await message.answer("Выберите время:", reply_markup=kb)
    await state.set_state(ConsultForm.waiting_for_time)

@dp.callback_query(lambda c: c.data.startswith("consult_time_"), ConsultForm.waiting_for_time)
async def consult_time(call: types.CallbackQuery, state: FSMContext):
    time_str = call.data.split("_")[-1] + ":00"
    await state.update_data(time=time_str)
    data = await state.get_data()
    msg = (
        f"🗓️ <b>Новая запись на консультацию</b>\n"
        f"Имя: {data['name']}\n"
        f"Телефон: {data['phone']}\n"
        f"Дата: {data['date']} {time_str}\n"
        f"От: @{call.from_user.username or 'нет username'}"
    )
    await call.message.answer(
        f"✅ Запись подтверждена!\n{data['date']} в {time_str}.\nМы свяжемся с вами для уточнения деталей.",
        reply_markup=main_menu()
    )
    await bot.send_message(ADMIN_ID, msg, parse_mode="HTML")
    await state.clear()
    await call.answer()

# --- Возврат в главное меню ---
@dp.callback_query(F.data == "start")
async def cb_start(call: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await call.message.answer("Главное меню:", reply_markup=main_menu())
    await call.answer()

# --- Fallback на любое непонятное сообщение ---
@dp.message()
async def fallback(message: types.Message):
    await message.answer("Пожалуйста, выберите действие из меню:", reply_markup=main_menu())

# --- Запуск бота ---
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

# ------------------------------------------
#  ПОЯСНЕНИЯ:
# - Тексты для блоков (о компании, услуги, выгоды и т.д.) легко редактировать в начале файла.
# - Любую услугу можно добавить или изменить в SERVICE_LIST.
# - FSM используется только для коротких форм — легко добавить/убрать поля.
# - Время консультации — через простой inline-календарь, дата руками (это упрощает поддержку).
# - Все заявки отправляются в ADMIN_ID.
# - Главное меню и переходы максимально прозрачные.
# ------------------------------------------
