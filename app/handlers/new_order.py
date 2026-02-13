#! handlers/new_order.py python3
from logs.set_logger import set_logger
logger = set_logger(name="handlers")
from handlers.common import typing, is_manager
from database.users import add_user, get_user_by_tg
from utils.formatters import parse_cost, add_days_from_text, format_telegram_username
from datetime import datetime
from aiogram import Router, types, F
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardRemove
from config import get_brands, UI_TEXTS, COST_DIAGNOSTIC, DIAGNOSTIC_TIME, DEVICES_RU, DEVICES_EN, EQUIPMENT, MISS, DONE, OWN_VERSION, PROBLEMS, CANCEL, ORDER, CLIENT, TYPE_ORDER, APPEARANCE
from keyboards.workshop import build_keyboard
from database import db
from database.orders import OrderService
from pdf.gen_pdf import BuildPDF
import uuid
import json

router = Router()
order = OrderService(db)
pdf = BuildPDF()




class newOrder(StatesGroup):
    client = State()
    search_client = State()
    name_client = State()
    phone_client = State()
    username_telegram = State()
    order_type = State()
    device_type = State()
    other_device = State()
    brand = State()
    other_brand = State()
    model = State()
    sn_imei = State()
    equipment = State()
    other_equipment = State()
    problem = State()
    other_problem = State()
    appearance = State()
    other_appearance = State()
    diagnostic_time = State()
    other_diagnostic_time = State()
    cost_diagnosis = State()
    other_cost_diagnosis = State()
    go_media = State()




# CANCEL STATE & KEYBOARD TO ALL HANDLERS !!!
@router.message((F.text == CANCEL["ru"]) | (F.text == CANCEL["en"]))
async def cancel(message: types.Message, state: FSMContext): 
    """ Отмена / Cancelled """
    await typing(message)
    lang = message.from_user.language_code
    await state.clear()
    if lang == "ru": await message.answer("🚫 Отменено", reply_markup=ReplyKeyboardRemove())
    else: await message.answer("🚫 Cancelled", reply_markup=ReplyKeyboardRemove())



# SAVE ORDER TO DB
async def save_order(lang: str, state: FSMContext, message: types.Message):
    """ Сохранение в базу заказа """
    await typing(message)
    state_data = await state.get_data()

    manadger_data = await get_user_by_tg(state_data.get("created_by")) # 1 
    #real_name_created = manadger_data.get("real_name", name_admin)
    real_name_created = manadger_data.get("name")

    data = {
        "sn_imei": state_data.get("sn_imei", None),
        "status": state_data.get("status", "new"),
        "order_type": state_data.get("order_type", "paid"),
        "device_type": state_data.get("device_type"),
        "device_brand": state_data.get("device_brand"),
        "device_model": state_data.get("device_model"),
        "equipment": json.dumps(state_data.get("equipment", []), ensure_ascii=False), # Пока что спсок в строку перевожу, могу забрать и обратно, пока думаю..
        "problem": json.dumps(state_data.get("problem", []), ensure_ascii=False),
        "appearance": json.dumps(state_data.get("appearance", []), ensure_ascii=False),
        "created_date": state_data.get("created_date"),
        "diagnosis_before": add_days_from_text(state_data.get("diagnostic_time")),
        "cost_diagnostics": parse_cost(state_data.get("cost_diagnostics")), # Только цена
        "path_photo": None, #state_data.get("path_photo"),
        "client_id": state_data.get("client_id"),
        "real_name_client": state_data.get("name"),
        "created_by": state_data.get("created_by"),
        "real_name_created": real_name_created,
    }

    # Create order
    order_number = await order.create_order(data) # 2
    if not order_number:
        # logging...
        if lang == "ru": await message.answer("🚫 Извините, возникла ошибка.", reply_markup=ReplyKeyboardRemove())
        else: await message.answer("🚫 Sorry, there was an error.", reply_markup=ReplyKeyboardRemove())
        return
    
    if lang == "ru": await message.answer(f"🎉 Новый заказ {order_number} сохранён в базу.", reply_markup=ReplyKeyboardRemove())
    else: await message.answer(f"🎉 The new order {order_number} has been saved to the database.", reply_markup=ReplyKeyboardRemove())

    data["order_number"] = order_number
    # После сохранения, так как будет мешать
    data["phone"] = state_data.get("phone")
    data["lang"] = lang

    # Build PDF file
    path_pdf = pdf.get_order_pdf(data)
    if not order_number:
        # logging...
        if lang == "ru": await message.answer("🚫 При генерации PDF возникла проблема, извините. Попробуйте получить PDF документ снова, войдя в заказ.", reply_markup=ReplyKeyboardRemove())
        else: await message.answer("🚫 There was a problem when generating the PDF, sorry. Try to get the PDF document again by logging in to the order.", reply_markup=ReplyKeyboardRemove())
        return

    # SEND PDF FILE
    send_text = "📄 Квитанция о приеме" if lang == "ru" else "📄 Admission receipt"
    await message.reply_document(
        document=types.input_file.FSInputFile(path_pdf),
        caption=send_text
    )




# MEDIA
@router.message(newOrder.go_media)
async def get_media(message: types.Message, state: FSMContext):
    """ Получения медиа устройства """
    await typing(message)
    lang = message.from_user.language_code

    # Позже добавлю логику, надо фото сохранять и path в базу
    # path_photo - путь где по данному заказу будут в папке фотки устройства и чела)
    if message.text in (MISS["ru"], MISS["en"]): pass
    else: return

    await save_order(lang, state, message)
    await state.clear()


# Go to get media
async def go_to_media_order(lang: str, state: FSMContext, message: types.Message):
    """ Запуск State Перехода в медиа """
    await typing(message)
    # state_data = await state.get_data() ####
    # print(state_data)

    media = []
    if lang == "ru":
        media.extend([MISS["ru"], CANCEL["ru"]])
        message_text = "📸 В разработке.."
    else:
        media.extend([MISS["en"], CANCEL["en"]])
        message_text = "📸 In development.."

    await message.answer(message_text, reply_markup = build_keyboard(media))
    await state.set_state(newOrder.go_media)


# OTHER COST_DIAGNOSTIC
@router.message(newOrder.other_cost_diagnosis)
async def other_cost_diagnosis(message: types.Message, state: FSMContext):
    """ Свой вариант цены диагностики """
    await typing(message)
    lang = message.from_user.language_code
    cost_diagnostics = message.text
    await state.update_data(cost_diagnostics=cost_diagnostics)
    await go_to_media_order(lang, state, message)


# COST_DIAGNOSTIC
@router.message(newOrder.cost_diagnosis)
async def cost_diagnosis(message: types.Message, state: FSMContext):
    """ Определение стоимости диагностики """
    await typing(message)
    lang = message.from_user.language_code
    # state_data = await state.get_data() ####
    # print(state_data)
    if message.text in set(COST_DIAGNOSTIC["ru"] + COST_DIAGNOSTIC["en"]):
        cost_diagnostics = message.text
        await state.update_data(cost_diagnostics=cost_diagnostics)

    elif message.text in (OWN_VERSION["ru"], OWN_VERSION["en"]):
        if lang == "ru": await message.answer("📝 Введите свой вариант цены диагностики:")
        else: await message.answer("📝 Enter your option for the diagnosis cost:")
        await state.set_state(newOrder.other_cost_diagnosis)
        return
    
    elif message.text in (MISS["ru"], MISS["en"]):
        await state.update_data(cost_diagnostics=None)

    else:
        if lang == "ru": await message.answer("🚫 Попробуйте еще раз выбрать пункт из меню")
        else: await message.answer("🚫 Try again to select an item from the menu")
        return

    await go_to_media_order(lang, state, message)


# Go to cost diagnost state
async def go_to_cost_diagnostic(lang: str, state: FSMContext, message: types.Message):
    """ Запуск State выбора цены диагностики """
    await typing(message)
    # state_data = await state.get_data() ####
    # print(state_data)

    if lang == "ru":
        diagnostic_time = COST_DIAGNOSTIC["ru"].copy()
        diagnostic_time.extend([OWN_VERSION["ru"], CANCEL["ru"]])
        message_text = "💵 Стоимость диагностики:"
    else:
        diagnostic_time = COST_DIAGNOSTIC["en"].copy()
        diagnostic_time.extend([OWN_VERSION["en"], CANCEL["en"]])
        message_text = "💵 The cost of diagnosis:"

    await message.answer(message_text, reply_markup = build_keyboard(diagnostic_time))
    await state.set_state(newOrder.cost_diagnosis)


# OTHER DIAGNOSTIC_TIME
@router.message(newOrder.other_diagnostic_time)
async def other_diagnostic_time(message: types.Message, state: FSMContext):
    """ Свой вариант времени диагностики """
    await typing(message)
    lang = message.from_user.language_code
    diagnostic_time = message.text
    await state.update_data(diagnostic_time=diagnostic_time)
    await go_to_cost_diagnostic(lang, state, message)


# DIAGNOSTIC_TIME
@router.message(newOrder.diagnostic_time)
async def diagnostic_time(message: types.Message, state: FSMContext):
    """ Определение сроков диагностики  """
    await typing(message)
    lang = message.from_user.language_code
    # state_data = await state.get_data() ####
    # print(state_data)
    if message.text in set(DIAGNOSTIC_TIME["ru"] + DIAGNOSTIC_TIME["en"]):
        diagnostic_time = message.text
        await state.update_data(diagnostic_time=diagnostic_time)

    elif message.text in (OWN_VERSION["ru"], OWN_VERSION["en"]):
        if lang == "ru": await message.answer("📝 Введите свой вариант срока диагностики:")
        else: await message.answer("📝 Enter your option for the diagnosis period:")
        await state.set_state(newOrder.other_diagnostic_time)
        return
    
    else:
        if lang == "ru": await message.answer("🚫 Попробуйте еще раз выбрать пункт из меню")
        else: await message.answer("🚫 Try again to select an item from the menu")
        return

    await go_to_cost_diagnostic(lang, state, message)


# OTHER APPEARANCE
@router.message(newOrder.other_appearance)
async def other_appearance(message: types.Message, state: FSMContext):
    """ Свой вариант внешнего вида устройства, добавляется к уже выбранному  """
    await typing(message)
    lang = message.from_user.language_code
    state_data = await state.get_data()
    appearance = state_data.get("appearance", []).copy()
    # Валидация позже
    appearance.append(message.text)
    await state.update_data(appearance=appearance)
    if lang == "ru": await message.answer("Описание внешнего вида (по готовности, нажмите - Готово):")
    else: await message.answer("Description of the appearance (when ready, click Done):")
    
    await state.set_state(newOrder.appearance)


# APPEARANCE
@router.message(newOrder.appearance)
async def appearance(message: types.Message, state: FSMContext):
    """ Внешний вид устройства  """
    await typing(message)
    lang = message.from_user.language_code
    flag = False
    # state_data = await state.get_data()
    # print(state_data)
    if message.text in set(APPEARANCE["ru"] + APPEARANCE["en"]):
        state_data = await state.get_data()
        appearance = state_data.get("appearance", []).copy()
        if message.text in appearance:
            if lang == "ru": await message.answer("🚫 Вы уже добавили этот элемент")
            else: await message.answer("🚫 You have already added this element")
            return
        appearance.append(message.text)
        await state.update_data(appearance=appearance)

    elif message.text in (OWN_VERSION["ru"], OWN_VERSION["en"]):
        if lang == "ru": await message.answer("📝 Опишите внешний вид устройства:")
        else: await message.answer("📝 Describe the device's appearance:")
        await state.set_state(newOrder.other_appearance)
        return

    elif message.text in (MISS["ru"], MISS["en"]):
        await state.update_data(appearance=[])
        flag = True

    elif message.text in (DONE["ru"], DONE["en"]):
        flag = True

    else:
        if lang == "ru": await message.answer("🚫 Попробуйте еще раз выбрать пункт из меню")
        else: await message.answer("🚫 Try again to select an item from the menu")
        return
    
    if not flag:
        return
    
    if lang == "ru":
        diagnostic_time = DIAGNOSTIC_TIME["ru"].copy()
        diagnostic_time.extend([OWN_VERSION["ru"], CANCEL["ru"]])
        message_text = "⏳ Сроки диагностики:"
    else:
        diagnostic_time = DIAGNOSTIC_TIME["en"].copy()
        diagnostic_time.extend([OWN_VERSION["en"], CANCEL["en"]])
        message_text = "⏳ Terms of diagnosis:"

    # await state.update_data(diagnostic_time=[]) # Заранее..
    await message.answer(message_text, reply_markup = build_keyboard(diagnostic_time))
    await state.set_state(newOrder.diagnostic_time)



# OTHER PROBLEMS
@router.message(newOrder.other_problem)
async def other_problem(message: types.Message, state: FSMContext):
    """ Свой вариант проблемы, добавляется к уже выбранному  """
    await typing(message)
    lang = message.from_user.language_code
    state_data = await state.get_data()
    problem = state_data.get("problem", []).copy()
    # Валидация позже
    problem.append(message.text)
    await state.update_data(problem=problem)
    if lang == "ru": await message.answer("Описание проблемы (по готовности, нажмите - Готово):")
    else: await message.answer("Problem description (when ready, click Done):")
    await state.set_state(newOrder.problem)


# PROBLEMS
@router.message(newOrder.problem)
async def problems(message: types.Message, state: FSMContext):
    """ Описание проблемы + готовые варианты  """
    await typing(message)
    lang = message.from_user.language_code
    flag = False

    if message.text in set(PROBLEMS["ru"] + PROBLEMS["en"]):
        state_data = await state.get_data()
        problem = state_data.get("problem", []).copy()
        if message.text in problem:
            if lang == "ru": await message.answer("🚫 Вы уже добавили этот элемент")
            else: await message.answer("🚫 You have already added this element")
            return
        problem.append(message.text)
        await state.update_data(problem=problem)
        return

    elif message.text in (OWN_VERSION["ru"], OWN_VERSION["en"]):
        if lang == "ru": await message.answer("📝 Опишите заявленные проблемы/неисправности:")
        else: await message.answer("📝 Describe the stated problems/malfunctions:")
        await state.set_state(newOrder.other_problem)
        return

    elif message.text in (DONE["ru"], DONE["en"]):
        state_data = await state.get_data()
        if not state_data.get("problem"):
            if lang == "ru": await message.answer("🚫 Выберите или опишите проблему, без этого будет трудно чинить:")
            else: await message.answer("🚫 Select or describe the problem, otherwise it will be difficult to fix:")
            return
        flag = True

    else:
        if lang == "ru": await message.answer("🚫 Попробуйте еще раз выбрать пункт из меню")
        else: await message.answer("🚫 Try again to select an item from the menu")
        return
    
    if not flag:
        return

    if lang == "ru":
        appearance = APPEARANCE["ru"].copy()
        appearance.extend([OWN_VERSION["ru"], DONE["ru"], MISS["ru"], CANCEL["ru"]])
        message_text = "🧯 Опишите внешний вид устройства:"
    else:
        appearance = APPEARANCE["en"].copy()
        appearance.extend([OWN_VERSION["en"], DONE["en"], MISS["en"], CANCEL["en"]])
        message_text = "🧯 Describe the device's appearance:"

    # await state.update_data(appearance=[]) # Заранее..
    await message.answer(message_text, reply_markup = build_keyboard(appearance))
    await state.set_state(newOrder.appearance)



# OTHER EQUIPMENT
@router.message(newOrder.other_equipment)
async def other_equipment(message: types.Message, state: FSMContext):
    """ Свой вариант комплектации, добавляется к уже выбранному  """
    await typing(message)
    lang = message.from_user.language_code
    state_data = await state.get_data()
    equipment = state_data.get("equipment", []).copy()
    # Валидация позже
    equipment.append(message.text)
    await state.update_data(equipment=equipment)
    if lang == "ru": await message.answer("Комплектация (после выбора нажмите - Готово):")
    else: await message.answer("Configuration (after selecting, click Done):")
    await state.set_state(newOrder.equipment)

# EQUIPMENT
@router.message(newOrder.equipment)
async def equipment(message: types.Message, state: FSMContext):
    """ Комплектация устройства, добавляется при нажатии  """
    await typing(message)
    lang = message.from_user.language_code
    flag = False

    if message.text in (OWN_VERSION["ru"], OWN_VERSION["en"]):
        if lang == "ru": await message.answer("📝 Напишите cвой вариант комплектации:")
        else: await message.answer("📝 Write your configuration option:")
        await state.set_state(newOrder.other_equipment)
        return
        
    elif message.text in set(EQUIPMENT["ru"] + EQUIPMENT["en"]):
        state_data = await state.get_data()
        equipment = state_data.get("equipment", []).copy()
        if message.text in equipment:
            if lang == "ru": await message.answer("🚫 Вы уже добавили этот элемент")
            else: await message.answer("🚫 You have already added this element")
            return
        equipment.append(message.text)
        await state.update_data(equipment=equipment)
        return

    elif message.text in (MISS["ru"], MISS["en"]):
        await state.update_data(equipment=[])
        flag = True

    elif message.text in (DONE["ru"], DONE["en"]):
        flag = True

    else:
        if lang == "ru": await message.answer("🚫 Попробуйте еще раз выбрать пункт из меню")
        else: await message.answer("🚫 Try again to select an item from the menu")
        return

    if not flag:
        return

    if lang == "ru":
        problems = PROBLEMS["ru"].copy()
        problems.extend([OWN_VERSION["ru"], DONE["ru"], CANCEL["ru"]])
        message_text = "💔 Выберите или опишите проблему:"
    else:
        problems = PROBLEMS["en"].copy()
        problems.extend([OWN_VERSION["en"], DONE["en"], CANCEL["en"]])
        message_text = "💔 Select or describe the problem:"

    # await state.update_data(problem=[]) # Заранее..
    await message.answer(message_text, reply_markup = build_keyboard(problems))
    await state.set_state(newOrder.problem)


# SN/IMEI
@router.message(newOrder.sn_imei)
async def sn_imei(message: types.Message, state: FSMContext):
    """ SN/imei устройства """
    await typing(message)
    lang = message.from_user.language_code
    sn_imei = message.text
    if message.text in (MISS["ru"], MISS["en"]):
        sn_imei = None
    # Валидация позже
    await state.update_data(sn_imei=sn_imei, equipment = []) # Специально equipment
    if lang == "ru":
        equipment = EQUIPMENT["ru"].copy() # !!!!!!!
        equipment.extend([MISS["ru"], OWN_VERSION["ru"], DONE["ru"], CANCEL["ru"]])
        await message.answer("Выберите комплектацию сдаваемого устройства (завершить - нажать Готово):", reply_markup = build_keyboard(equipment))
    else:
        equipment = EQUIPMENT["en"].copy() # !!!!!!!
        equipment.extend([MISS["en"], OWN_VERSION["en"], DONE["en"], CANCEL["en"]])
        await message.answer("Select the configuration of the device to be delivered (complete - click Done):", reply_markup = build_keyboard(equipment))
    await state.set_state(newOrder.equipment)


# MODEL
@router.message(newOrder.model)
async def model_device(message: types.Message, state: FSMContext):
    """ Модель устройства """
    await typing(message)
    lang = message.from_user.language_code
    # Валидация позже...
    device_model = message.text
    if message.text in (MISS["ru"], MISS["en"]):
        device_model = None
    await state.update_data(device_model=device_model)
    if lang == "ru": await message.answer("Серийный номер / IMEI:", reply_markup = build_keyboard([MISS["ru"]]))
    else: await message.answer("Serial Number / IMEI:", reply_markup = build_keyboard([MISS["en"]]))
    await state.set_state(newOrder.sn_imei)


# OTHER BRAND
@router.message(newOrder.other_brand)
async def other_brand(message: types.Message, state: FSMContext):
    """ Бренд устройства свой вариант """
    await typing(message)
    lang = message.from_user.language_code
    # Позже валидация + проверка (недопустимые символы и код, что бы в базу не залили)
    device_brand = message.text
    await state.update_data(device_brand=device_brand)
    if lang == "ru": await message.answer("💎 Модель устройства:", reply_markup = build_keyboard([MISS["ru"]]))
    else: await message.answer("💎 Device Model:", reply_markup = build_keyboard([MISS["en"]]))
    await state.set_state(newOrder.model)


# BRAND DEVICE
@router.message(newOrder.brand)
async def brand_device(message: types.Message, state: FSMContext):
    """ Бренд устройства """
    await typing(message)
    lang = message.from_user.language_code
    state_data = await state.get_data()
    brands = state_data.get("brands")

    if message.text in (OWN_VERSION["ru"], OWN_VERSION["en"]):
        if lang == "ru": await message.answer("📝 Напишите cвой вариант бренда:", reply_markup=ReplyKeyboardRemove())
        else: await message.answer("📝 Write your brand name:", reply_markup=ReplyKeyboardRemove())
        await state.set_state(newOrder.other_brand)
    
    elif message.text in brands:
        # Позже валидация + проверка (недопустимые символы и код, что бы в базу не залили)
        device_brand = message.text
        await state.update_data(device_brand=device_brand)
        if lang == "ru": await message.answer("💎 Модель устройства:", reply_markup = build_keyboard([MISS["ru"]]))
        else: await message.answer("💎 Device Model:", reply_markup = build_keyboard([MISS["en"]]))
        await state.set_state(newOrder.model)

    else:
        if lang == "ru": await message.answer("🚫 Попробуйте еще раз выбрать пункт из меню")
        else: await message.answer("🚫 Try again to select an item from the menu")



# GO TO BRANDS
async def process_device_type(device_type: str, lang: str, state: FSMContext, message: types.Message):
    """Общая логика обработки типа устройства"""
    # Получение брендов по типу устройства
    brands = get_brands(device_type)
    await state.update_data(device_type=device_type, brands=brands.copy())
    
    if lang == "ru":
        brands.extend([OWN_VERSION["ru"], CANCEL["ru"]])
        text_message = "🔮 Выберите марку/бренд устройства"
    else:
        brands.extend([OWN_VERSION["en"], CANCEL["en"]])
        text_message = "🔮 Select the make/brand of the device"
    
    await message.answer(text_message, reply_markup=build_keyboard(brands))
    await state.set_state(newOrder.brand)


# OTHER DEVICE
@router.message(newOrder.other_device)
async def other_device(message: types.Message, state: FSMContext):
    """ Тип устройства свой вариант """
    await typing(message)
    lang = message.from_user.language_code
    # Позже валидация + проверка (недопустимые символы и код, что бы в базу не залили)
    device_type = message.text
    await process_device_type(device_type, lang, state, message)


# TYPE DEVICE
@router.message(newOrder.device_type)
async def type_device(message: types.Message, state: FSMContext):
    """ Тип сдаваемого устройства """
    await typing(message)
    lang = message.from_user.language_code

    if message.text in (OWN_VERSION["ru"], OWN_VERSION["en"]):
        if lang == "ru": await message.answer("📝 Напишите cвой вариант:", reply_markup=ReplyKeyboardRemove())
        else: await message.answer("📝 Write your own version:", reply_markup=ReplyKeyboardRemove())
        await state.set_state(newOrder.other_device)

    elif message.text in set(DEVICES_RU + DEVICES_EN):
        # Позже валидация + проверка (недопустимые символы и код, что бы в базу не залили)
        device_type = message.text
        await process_device_type(device_type, lang, state, message)

    else:
        if lang == "ru": await message.answer("🚫 Попробуйте еще раз выбрать пункт из меню")
        else: await message.answer("🚫 Try again to select an item from the menu")


# TYPE ORDER
@router.message(newOrder.order_type)
async def order_type(message: types.Message, state: FSMContext):
    """ Тип заказа - платный, гарантийный """
    await typing(message)
    lang = message.from_user.language_code

    if message.text in (TYPE_ORDER["guarant_ru"], TYPE_ORDER["guarant_en"]):
        order_type = "guarant"
    elif message.text in (TYPE_ORDER["paid_ru"], TYPE_ORDER["paid_en"]):
        order_type = "paid"
    else:
        if lang == "ru": await message.answer("🚫 Попробуйте еще раз выбрать пункт из меню")
        else: await message.answer("🚫 Try again to select an item from the menu")
        return

    state_data = await state.get_data() # В нём только ser_id
    client_id = state_data.get("user_id")
    created_by = message.from_user.id
    created_date = datetime.now()
    status = "new"
    await state.update_data( 
        created_by=created_by,
        client_id=client_id, 
        created_date=created_date, 
        status=status,
        order_type=order_type
    )

    if lang == "ru": 
        devices = DEVICES_RU.copy()
        answer_text = "💡 Выберите тип устройства:"
        devices.extend([OWN_VERSION["ru"], CANCEL["ru"]])
    else:
        devices = DEVICES_EN.copy()
        answer_text = "💡 Select the device type:"
        devices.extend([OWN_VERSION["en"], CANCEL["en"]])

    await message.answer(answer_text, reply_markup = build_keyboard(devices))
    await state.set_state(newOrder.device_type)


######### START CREATE ORDER by USER_ID ##############
# Можно будет вызывать как начало state..
async def create_order(message: types.Message, state: FSMContext, user_id: uuid, name: str, phone: str):
    """ Начало формирования заказа по user_id """
    lang = message.from_user.language_code
    await state.update_data(user_id=user_id, name=name, phone=phone) # Чистый state, только user_id, name, phone
    if lang == "ru": await message.answer("Выберите тип заказа:", reply_markup = build_keyboard([TYPE_ORDER["paid_ru"], TYPE_ORDER["guarant_ru"], CANCEL["ru"]])) 
    else: await message.answer("Select the order type:", reply_markup = build_keyboard([TYPE_ORDER["paid_en"], TYPE_ORDER["guarant_en"], CANCEL["en"]])) 
    await state.set_state(newOrder.order_type)
#####################


# TELEGRAM CLIENT
@router.message(newOrder.username_telegram)
async def username_telegram(message: types.Message, state: FSMContext):
    """ username_telegram клиента """
    await typing(message)
    lang = message.from_user.language_code
    username_telegram = format_telegram_username(message.text)
    if message.text in (MISS["ru"], MISS["en"]):
        username_telegram = None
    # Проверка в базе и предупреждение + варианты действий + валидация телеграм @name + валидация ввода 
    user_id = uuid.uuid4()
    time_reg = datetime.now()

    await state.update_data(username_telegram=username_telegram, time_reg=time_reg, user_id=user_id)
    state_data = await state.get_data()
    # Create USER
    if await add_user(state_data):
        if lang == "ru": await message.answer("🎉 Новый клиент сохранен.")
        else: await message.answer("🎉 The new client has been saved.")
    else:
        if lang == "ru": await message.answer("🚫 Есть проблема с сохранением в базу клиента", reply_markup=ReplyKeyboardRemove())
        else: await message.answer("🚫 There is a problem with saving to the client's database", reply_markup=ReplyKeyboardRemove())
        await state.clear()
        return
    if lang == "ru": await message.answer("Продолжим..")
    else: await message.answer("Continue..")
    await state.clear()
    await create_order(message, state, user_id, name=state_data.get("name"), phone=state_data.get("phone"))


# PHONE CLIENT
@router.message(newOrder.phone_client)
async def phone_client(message: types.Message, state: FSMContext):
    """ Телефон клиента """
    await typing(message)
    lang = message.from_user.language_code
    phone = message.text
    if message.text in (MISS["ru"], MISS["en"]):
        phone = None
    # Проверка в базе и предупреждение + варианты действий + валидация номера + валидация ввода + фильтр
    await state.update_data(phone=phone)
    if lang == "ru": await message.answer("✉️ Введите телеграмм  клиента (@name):", reply_markup = build_keyboard([MISS["ru"]]))
    else: await message.answer("✉️ Enter the client's telegram (@name):", reply_markup = build_keyboard([MISS["en"]]))
    await state.set_state(newOrder.username_telegram)


# NAME CLIENT
@router.message(newOrder.name_client)
async def name_client(message: types.Message, state: FSMContext):
    """ Ввод имени клиента """
    await typing(message)
    lang = message.from_user.language_code
    # Проверка в базе и предупреждение клиента об этом + варианты действий + валидация + фильтр = позже
    name = message.text
    await state.update_data(name=name)
    if lang == "ru": await message.answer("📞 Введите Телефон клиента:", reply_markup = build_keyboard([MISS["ru"]]))
    else: await message.answer("📞 Enter the client's phone number:", reply_markup = build_keyboard([MISS["en"]]))
    await state.set_state(newOrder.phone_client)


# CLIENT ADDING or SEARCH at DB
@router.message(newOrder.client)
async def client(message: types.Message, state: FSMContext):
    """ Выбор добавления клиента или поиск """
    await typing(message)
    lang = message.from_user.language_code

    # if message.text in (CLIENT["serch_ru"], CLIENT["serch_en"]):
    #     await message.answer("🚫 In development..", reply_markup=ReplyKeyboardRemove()) #### !!!! ####
    #     await state.set_state(newOrder.search_client)
    #     await state.clear()
    #     return
    
    if message.text in (CLIENT["new_ru"], CLIENT["new_en"]):
        if lang == "ru": await message.answer("✍️ Введите Имя нового клиента:", reply_markup = build_keyboard([CANCEL["ru"]]))
        else: await message.answer("✍️ Enter the new client's name:", reply_markup = build_keyboard([CANCEL["en"]]))
        await state.set_state(newOrder.name_client)

    else:
        if lang == "ru": await message.answer("🚫 Попробуйте еще раз выбрать пункт из меню")
        else: await message.answer("🚫 Try again to select an item from the menu")


# START CREATE NEW ORDER
@router.message((F.text == UI_TEXTS["ru"]["new_order"]) | (F.text == UI_TEXTS["en"]["new_order"]))
async def new_order(message: types.Message, state: FSMContext):
    """ Новый заказ / New order"""
    await typing(message)
    lang = message.from_user.language_code
    user_id = message.from_user.id
    if not await is_manager(user_id):
        logger.error(f"{user_id} You don't have access")
        await message.answer("🔐 You don't have access")
        return
    if lang == "ru": text = "👨🏻‍💼 Найти клиента или создать заново:"
    else: text = "👨🏻‍💼 Find a client or create anew:"
    await message.answer(text, reply_markup = build_keyboard([UI_TEXTS[lang]["new_cli"], UI_TEXTS[lang]["serch_cli"]])) 
    await state.set_state(newOrder.client)


