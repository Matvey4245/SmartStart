import os
import asyncio
import re
import random
from aiogram import Bot, Dispatcher, types, F # Added F for filters
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command # Removed Text from here
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram_calendar import SimpleCalendar, SimpleCalendarCallback

# Получаем данные из окружения Railway
TOKEN = "7640751648:AAEfw4o4ElnSeCf_qPvxHwdUFFM-0waa-lM"  # Токен бота
ADMIN_ID = 7139278611 # Вставьте сюда свой ID администратора

bot = Bot(token=TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)


### FSM состояния

class ConsultForm(StatesGroup):
    waiting_for_name = State()
    waiting_for_phone = State()
    waiting_for_phone_code = State()
    waiting_for_email = State()
    waiting_for_date = State()
    waiting_for_time = State()


class QuizForm(StatesGroup):
    waiting_for_phone = State()
    waiting_for_code = State()
    visa_type = State()
    has_invite = State()
    was_in_us = State()
    income = State()
    family = State()
    refusals = State()


### Главное меню
def main_menu():
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="Гайд", callback_data="/guide"),
            InlineKeyboardButton(text="Консультация", callback_data="/consult"),
            InlineKeyboardButton(text="SSN", callback_data="/ssn"),
        ],
        [
            InlineKeyboardButton(text="Адрес", callback_data="/address"),
            InlineKeyboardButton(text="Банк", callback_data="/bank"),
            InlineKeyboardButton(text="Сим-карта", callback_data="/phone"),
        ],
        [
            InlineKeyboardButton(text="Жильё", callback_data="/housing"),
            InlineKeyboardButton(text="Работа", callback_data="/job"),
            InlineKeyboardButton(text="Ошибки", callback_data="/errors"),
        ],
        [
            InlineKeyboardButton(text="Глоссарий", callback_data="/glossary"),
            InlineKeyboardButton(text="Английский", callback_data="/english"),
            InlineKeyboardButton(text="О нас", callback_data="/about"),
        ],
        [
            InlineKeyboardButton(text="Квиз: шанс визы", callback_data="/quiz"),
            InlineKeyboardButton(text="Помощь", callback_data="/help")
        ]
    ])
    return kb


### Универсальная функция для FAQ и гайд-блоков
async def send_faq(message: types.Message, text: str):
    await message.answer(text, reply_markup=main_menu())


### Старт и help
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(
        "👋 Привет! Я — бот Smart Start USA 🇺🇸\n"
        "Помогаю адаптироваться в США: жильё, работа, документы, консультации и многое другое.\n"
        "Выберите интересующий вас раздел 👇", reply_markup=main_menu())


@dp.message(Command("help"))
async def cmd_help(message: types.Message):
    await send_faq(message, "🆘 Помощь и команды:\n"
                            "/guide — Гайд по переезду\n"
                            "/consult — Запись на консультацию\n"
                            "/ssn — Как получить SSN\n"
                            "/address — Как указать адрес\n"
                            "/bank — Как открыть счёт\n"
                            "/phone — Как подключить симку\n"
                            "/housing — Как найти жильё\n"
                            "/job — Поиск работы\n"
                            "/errors — Частые ошибки\n"
                            "/glossary — Глоссарий терминов\n"
                            "/english — Курсы английского\n"
                            "/about — О проекте\n"
                            "/quiz — Квиз «шанс визы»\n"
                            "Или используйте меню ниже.")


### Гайды
@dp.message(Command("guide"))
async def cmd_guide(message: types.Message, state: FSMContext): await send_faq(message,
                                                            "📘 Гайд по адаптации в США\n\n"
                                                            "Здесь вы найдёте пошаговые инструкции по переезду и адаптации в США. Мы расскажем:\n"
                                                            "— как выбрать штат\n— как подготовиться до вылета\n— что делать в первую неделю\n— как оформить документы, жильё, работу.")


@dp.message(Command("ssn"))
async def cmd_ssn(message: types.Message, state: FSMContext): await send_faq(message,
                                                          "🧾 Получение SSN (Social Security Number)\n\n"
                                                          "SSN — ваш идентификатор в США для работы, налогов, банков.\n"
                                                          "• Запишитесь в SSA (через сайт или по телефону)\n• Нужны документы (паспорт, статус, адрес)\n• SSN приходит по почте за 2–4 недели.")


@dp.message(Command("address"))
async def cmd_address(message: types.Message, state: FSMContext): await send_faq(message,
                                                              "📮 Указание адреса в США\n\n"
                                                              "Адрес нужен для получения документов (SSN, EAD и др).\n"
                                                              "• Друзья/знакомые, платные почтовые сервисы или стабильное жильё.\n"
                                                              "Внимание: почта может теряться, следите за ней!")


@dp.message(Command("bank"))
async def cmd_bank(message: types.Message, state: FSMContext): await send_faq(message,
                                                           "🏦 Открытие банковского счёта в США\n\n"
                                                           "• Популярные банки: BoA, Chase, Wells Fargo\n"
                                                           "• Часто нужен только паспорт и адрес\n"
                                                           "• Некоторые банки открывают счёт без SSN.")


@dp.message(Command("phone"))
async def cmd_phone(message: types.Message, state: FSMContext): await send_faq(message,
                                                            "📱 SIM-карта и номер\n\n"
                                                            "• Операторы: T-Mobile, AT&T, Verizon\n"
                                                            "• Бюджетно: Mint Mobile, Visible\n"
                                                            "• SIM можно купить в магазине или заказать онлайн.")


@dp.message(Command("housing"))
async def cmd_housing(message: types.Message, state: FSMContext): await send_faq(message,
                                                              "🏠 Жильё в США\n\n"
                                                              "• Сайты: Zillow, Craigslist, Facebook Marketplace\n"
                                                              "• Часто нужен поручитель или депозит\n"
                                                              "• Airbnb — хороший вариант на первое время.")


@dp.message(Command("job"))
async def cmd_job(message: types.Message, state: FSMContext): await send_faq(message,
                                                          "💼 Поиск работы в США\n\n"
                                                          "• indeed.com, linkedin.com, craigslist.org\n"
                                                          "• Готовьте резюме, указывайте местный адрес и номер.\n"
                                                          "Внимание: следите за легальностью вакансии.")


@dp.message(Command("errors"))
async def cmd_errors(message: types.Message, state: FSMContext): await send_faq(message,
                                                             "⚠️ Частые ошибки иммигрантов\n\n"
                                                             "• Откладывают оформление SSN и адреса\n"
                                                             "• Доверяют сомнительным посредникам\n"
                                                             "• Не считают бюджет на первые месяцы.")


@dp.message(Command("glossary"))
async def cmd_glossary(message: types.Message, state: FSMContext): await send_faq(message,
                                                               "📚 Глоссарий иммигранта\n\n"
                                                               "SSN, EAD, I-94, asylum, TPS, USCIS, SSA и др. — используйте как шпаргалку.")


@dp.message(Command("english"))
async def cmd_english(message: types.Message, state: FSMContext): await send_faq(message,
                                                              "🇺🇸 Курсы английского\n\n"
                                                              "• Бесплатные ESL-курсы от колледжей и библиотек\n"
                                                              "• Онлайн-ресурсы: Duolingo, BBC Learning, LingQ\n"
                                                              "• Индивидуальные занятия.")


@dp.message(Command("about"))
async def cmd_about(message: types.Message, state: FSMContext): await send_faq(message,
                                                            "ℹ️ О проекте Smart Start USA\n\n"
                                                            "Мы — команда эмигрантов. Консультируем новичков, готовим гайды и шаблоны, проводим курсы.")


### --- Консультация: FSM с подтверждением телефона, email, датой, временем ---
@dp.message(Command("consult"))
async def consult_start(message: types.Message, state: FSMContext):
    await message.answer("Запишитесь на персональную консультацию.\nКак вас зовут?")
    await state.set_state(ConsultForm.waiting_for_name)


@dp.message(ConsultForm.waiting_for_name)
async def consult_name(message: types.Message, state: FSMContext):
    await state.update_data(user_name=message.text)
    await message.answer("Укажите ваш телефон (пример: +12345678900):")
    await state.set_state(ConsultForm.waiting_for_phone)


@dp.message(ConsultForm.waiting_for_phone)
async def consult_phone(message: types.Message, state: FSMContext):
    phone = message.text.strip()
    if not re.match(r"^\+?\d{10,15}$", phone):
        await message.answer("❗ Введите корректный телефон (пример: +12345678900):")
        return
    code = str(random.randint(1000, 9999))
    await state.update_data(user_phone=phone, confirm_code=code)
    await message.answer(f"🟢 На номер {phone} отправлен 4-значный код (тест: {code}). Введите этот код:")
    await state.set_state(ConsultForm.waiting_for_phone_code)


@dp.message(ConsultForm.waiting_for_phone_code)
async def consult_phone_code(message: types.Message, state: FSMContext):
    data = await state.get_data()
    if message.text.strip() == data['confirm_code']:
        await message.answer("✅ Телефон подтверждён. Теперь укажите ваш email:")
        await state.set_state(ConsultForm.waiting_for_email)
    else:
        await message.answer("❗ Код неверный. Попробуйте ещё раз:")


@dp.message(ConsultForm.waiting_for_email)
async def consult_email(message: types.Message, state: FSMContext):
    email = message.text.strip()
    if not re.match(r"^[-\w.]+@([A-z0-9][-A-z0-9]+\.)+[A-z]{2,}$", email):
        await message.answer("❗ Введите корректный email (пример: user@email.com):")
        return
    await state.update_data(user_email=email)
    await message.answer("Выберите дату консультации:", reply_markup=await SimpleCalendar().start_calendar())
    await state.set_state(ConsultForm.waiting_for_date)


@dp.callback_query(SimpleCalendarCallback.filter(), ConsultForm.waiting_for_date)
async def consult_calendar(call: types.CallbackQuery, callback_data: SimpleCalendarCallback, state: FSMContext):
    selected, date = await SimpleCalendar().process_selection(call, callback_data)
    if selected:
        await state.update_data(consult_date=date.strftime("%d.%m.%Y"))
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=time, callback_data=f"consult_time:{time}")]
            for time in ["10:00", "11:00", "12:00", "13:00", "14:00", "15:00", "16:00", "17:00", "18:00", "19:00"]
        ])
        await call.message.answer("Выберите удобное время:", reply_markup=kb)
        await state.set_state(ConsultForm.waiting_for_time)


@dp.callback_query(F.data.startswith("consult_time:"), ConsultForm.waiting_for_time) # Used F.data
async def consult_time(call: types.CallbackQuery, state: FSMContext):
    time = call.data.split(":")[1]
    await state.update_data(consult_time=time)
    data = await state.get_data()
    await call.message.answer(
        f"🎉 Вы записаны на консультацию {data['consult_date']} в {time}.\n"
        f"Инструкция будет на email: {data['user_email']}. Специалист свяжется с вами по телефону: {data['user_phone']}")
    # Уведомление админу
    msg = (f"🆕 Новая консультация:\n"
           f"Имя: {data['user_name']}\n"
           f"Телефон: {data['user_phone']}\n"
           f"Email: {data['user_email']}\n"
           f"Дата: {data['consult_date']}\n"
           f"Время: {data['consult_time']}")
    await bot.send_message(ADMIN_ID, msg)
    await state.clear()
    await call.answer()


### --- Квиз: шанс визы ---
@dp.message(Command("quiz"))
async def quiz_start(message: types.Message, state: FSMContext):
    await message.answer(
        "🚦 Квиз: Узнай свой шанс на получение визы в США!\n\nУкажите свой телефон (пример: +12345678900):")
    await state.set_state(QuizForm.waiting_for_phone)


@dp.callback_query(F.data == "/quiz") # Used F.data
async def quiz_callback(call: types.CallbackQuery, state: FSMContext):
    await call.message.answer(
        "🚦 Квиз: Узнай свой шанс на получение визы в США!\n\nУкажите свой телефон (пример: +12345678900):")
    await state.set_state(QuizForm.waiting_for_phone)
    await call.answer()


@dp.message(QuizForm.waiting_for_phone)
async def quiz_phone(message: types.Message, state: FSMContext):
    phone = message.text.strip()
    if not re.match(r"^\+?\d{10,15}$", phone):
        await message.answer("❗ Введите корректный телефон (пример: +12345678900):")
        return
    code = str(random.randint(1000, 9999))
    await state.update_data(user_phone=phone, confirm_code=code)
    await message.answer(f"🟢 На номер {phone} отправлен 4-значный код (тест: {code}). Введите этот код ниже:")
    await state.set_state(QuizForm.waiting_for_code)


@dp.message(QuizForm.waiting_for_code)
async def quiz_code(message: types.Message, state: FSMContext):
    data = await state.get_data()
    if message.text.strip() == data['confirm_code']:
        await message.answer(
            "✅ Телефон подтверждён!\n\n1/7. Для какой визы вы подаёте?\n1 — Туризм\n2 — Учёба\n3 — Работа\n4 — Воссоединение семьи")
        await state.set_state(QuizForm.visa_type)
    else:
        await message.answer("❗ Код неверный. Попробуйте ещё раз:")


@dp.message(QuizForm.visa_type)
async def quiz_visa_type(message: types.Message, state: FSMContext):
    # Basic validation for visa_type to ensure it's one of the expected numbers
    if message.text.strip() not in ["1", "2", "3", "4"]:
        await message.answer("Пожалуйста, введите номер от 1 до 4.")
        return
    await state.update_data(visa_type=message.text.strip())
    await message.answer("2/7. Есть ли у вас официальное приглашение? (да/нет)")
    await state.set_state(QuizForm.has_invite)


@dp.message(QuizForm.has_invite)
async def quiz_has_invite(message: types.Message, state: FSMContext):
    normalized_text = message.text.lower().strip()
    if normalized_text not in ["да", "нет"]:
        await message.answer("Пожалуйста, ответьте 'да' или 'нет'.")
        return
    await state.update_data(has_invite=normalized_text)
    await message.answer("3/7. Были ли у вас визы в США или шенген за последние 5 лет? (да/нет)")
    await state.set_state(QuizForm.was_in_us)


@dp.message(QuizForm.was_in_us)
async def quiz_was_in_us(message: types.Message, state: FSMContext):
    normalized_text = message.text.lower().strip()
    if normalized_text not in ["да", "нет"]:
        await message.answer("Пожалуйста, ответьте 'да' или 'нет'.")
        return
    await state.update_data(was_in_us=normalized_text)
    await message.answer("4/7. Ваш доход за месяц в $ (пример: 1000):")
    await state.set_state(QuizForm.income)


@dp.message(QuizForm.income)
async def quiz_income(message: types.Message, state: FSMContext):
    income_str = message.text.strip()
    if not income_str.isdigit():
        await message.answer("Пожалуйста, введите ваш доход числом (пример: 1000):")
        return
    await state.update_data(income=income_str)
    await message.answer("5/7. Семья (жена/дети/родители) остаётся на родине? (да/нет)")
    await state.set_state(QuizForm.family)


@dp.message(QuizForm.family)
async def quiz_family(message: types.Message, state: FSMContext):
    normalized_text = message.text.lower().strip()
    if normalized_text not in ["да", "нет"]:
        await message.answer("Пожалуйста, ответьте 'да' или 'нет'.")
        return
    await state.update_data(family=normalized_text)
    await message.answer("6/7. Были ли отказы по визам в США или других странах? (да/нет)")
    await state.set_state(QuizForm.refusals)


@dp.message(QuizForm.refusals)
async def quiz_refusals(message: types.Message, state: FSMContext):
    normalized_text = message.text.lower().strip()
    if normalized_text not in ["да", "нет"]:
        await message.answer("Пожалуйста, ответьте 'да' или 'нет'.")
        return
    await state.update_data(refusals=normalized_text)
    data = await state.get_data()
    score = 0
    if data['visa_type'] == "1":
        score += 2
    if data['has_invite'] == "да":
        score += 2
    if data['was_in_us'] == "да":
        score += 2
    try:
        income_val = int(data['income'])
        if income_val >= 1500:
            score += 2
        elif income_val >= 700:
            score += 1
    except ValueError:
        pass  # Income validation already happened, but good to handle potential errors here too
    if data['family'] == "да":
        score += 1
    if data['refusals'] == "нет":
        score += 2

    # Max possible score is 2+2+2+2+1+2 = 11
    percent = int(score * 100 / 11)

    if percent >= 80:
        result = f"Ваш шанс на получение визы — {percent}%\n👍 Отличные шансы! Главное — грамотно подготовить документы."
    elif percent >= 50:
        result = f"Ваш шанс — {percent}%\n👌 Всё реально, но стоит подготовиться. Особое внимание — объяснению связи с родиной."
    else:
        result = f"Ваш шанс — {percent}%\n⚠️ Рекомендуем получить консультацию и собрать дополнительные подтверждающие документы."

    await message.answer(
        f"Спасибо за ответы!\n\n{result}\n\nДля подробной консультации — напишите /consult или выберите в меню.")
    # Уведомление админу
    admin_msg = (f"📝 Прошли квиз на шанс визы:\n"
                 f"Телефон: {data['user_phone']}\n"
                 f"Виза: {data['visa_type']}\n"
                 f"Приглашение: {data['has_invite']}\n"
                 f"Визы в США/шенген: {data['was_in_us']}\n"
                 f"Доход: {data['income']}\n"
                 f"Семья остаётся: {data['family']}\n"
                 f"Отказы: {data['refusals']}\n"
                 f"Шанс (оценка): {percent}%")
    await bot.send_message(ADMIN_ID, admin_msg)
    await state.clear()


### --- Обработка callback-кнопок ---
@dp.callback_query()
async def menu_callback(call: types.CallbackQuery, state: FSMContext):
    data = call.data
    # Для команд — вызови соответствующий хендлер
    # Также добавил большинство хендлеров в cmd_map, чтобы они работали с кнопками
    # Некоторые хендлеры были изменены, чтобы принимать `state`
    cmd_map = {
        "/guide": cmd_guide,
        "/consult": consult_start,
        "/ssn": cmd_ssn,
        "/address": cmd_address,
        "/bank": cmd_bank,
        "/phone": cmd_phone,
        "/housing": cmd_housing,
        "/job": cmd_job,
        "/errors": cmd_errors,
        "/glossary": cmd_glossary,
        "/english": cmd_english,
        "/about": cmd_about,
        "/help": cmd_help,
        # Этот обработчик теперь тоже вызывается отсюда
        "/quiz": quiz_callback,
    }

    if data in cmd_map:
        # Для quiz_callback нужен объект `call`, а для остальных - `call.message`
        if data == "/quiz":
            await quiz_callback(call, state)
        else:
            # Универсальный вызов для большинства команд
            # Передаем call.message и state, если они нужны хендлеру
            # Это может потребовать небольшой доработки хендлеров гайдов, если они начнут использовать FSM
            # Пока что для них `state` просто будет проигнорирован
            await cmd_map[data](call.message, state)
    await call.answer()


### --- Fallback на неизвестное ---
@dp.message()
async def fallback(message: types.Message):
    await message.answer("⚠️ Не понимаю команду. Напишите /help или выберите кнопку ниже.", reply_markup=main_menu())


### --- Запуск ---
async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())