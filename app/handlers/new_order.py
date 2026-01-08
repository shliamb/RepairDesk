#! handlers/new_order.py python3
from logs.set_logger import set_logger
logger = set_logger(name="handlers")
from handlers.common import typing, is_manager
from database.users import add_user, get_user_by_tg
from aiogram import Router, types, F
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardRemove, InlineKeyboardMarkup
from config import get_brands, DEVICES_RU, DEVICES_EN, EQUIPMENT_RU
from keyboards.workshop import build_keyboard
from common import day_utcnow
import uuid

router = Router()


#!!!! Позже добавить два языка!!!
# !!! Возможно упростить добавление
# Очень нужна валидация, хоть и менеджеры не 
# должны ломать и передавать злой код, но все же..



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


# state_data = await state.get_data()
# print(state_data)
#await state.clear()

# device_type = "Материнская плата"
# available_brands = DEVICE_BRANDS_RU.get(device_type, ["Другой"])

# print(available_brands)




# equipment - в цикл, что бы добавлялось, готово.. типа..

# SN/IMEI
@router.message(newOrder.sn_imei)
async def sn_imei(message: types.Message, state: FSMContext):
    """ SN/imei устройства """
    await typing(message)
    sn_imei = message.text
    if sn_imei == "🎲 Пропустить":
        sn_imei = None
    # Валидация позже
    await state.update_data(sn_imei=sn_imei)
    equipment = EQUIPMENT_RU
    equipment.append("🎲 Пропустить")
    await message.answer("Комплектация:", reply_markup = build_keyboard(equipment))
    await state.set_state(newOrder.equipment)

# MODEL
@router.message(newOrder.model)
async def model_device(message: types.Message, state: FSMContext):
    """ Модель устройства """
    await typing(message)

    # Валидация позже...
    answer = message.text
    if answer == "🎲 Пропустить":
        device_model = None
    
    device_model = answer

    await state.update_data(device_model=device_model)
    await message.answer("Серийный номер / IMEI:", reply_markup = build_keyboard(["🎲 Пропустить"]))
    await state.set_state(newOrder.sn_imei)

# OTHER BRAND
@router.message(newOrder.other_brand)
async def other_brand(message: types.Message, state: FSMContext):
    """ Бренд устройства свой вариант """
    await typing(message)
    # Позже валидация + проверка (недопустимые символы и код, что бы в базу не залили)
    device_brand = message.text
    await state.update_data(device_type=device_brand)
    await message.answer("Модель устройства:", reply_markup = build_keyboard(["🎲 Пропустить"]))
    await state.set_state(newOrder.model)

# BRAND DEVICE
@router.message(newOrder.brand)
async def brand_device(message: types.Message, state: FSMContext):
    """ Бренд устройства """
    await typing(message)
    state_data = await state.get_data()
    brands = state_data.get("brands")

    if message.text == "📝 Свой вариант":
        await message.answer("📝 Напишите cвой вариант бренда:", reply_markup=ReplyKeyboardRemove())
        await state.set_state(newOrder.other_brand)
    
    elif message.text in brands:
        # Позже валидация + проверка (недопустимые символы и код, что бы в базу не залили)
        device_brand = message.text
        await state.update_data(device_type=device_brand)
        await message.answer("Модель устройства:", reply_markup = build_keyboard(["🎲 Пропустить"]))
        await state.set_state(newOrder.model)

    else:
        await message.answer("Попробуйте еще раз выбрать из меню пункт")

# OTHER DEVICE
@router.message(newOrder.other_device)
async def other_device(message: types.Message, state: FSMContext):
    """ Тип устройства свой вариант """
    await typing(message)
    # Позже валидация + проверка (недопустимые символы и код, что бы в базу не залили)
    device_type = message.text
    # Получение брендов по типу устройства
    brands = get_brands(device_type)
    await state.update_data(device_type=device_type, brands=brands)
    brands.append("📝 Свой вариант")
    await message.answer("Выберите марку/бренд устройства", reply_markup = build_keyboard(brands)) 
    await state.set_state(newOrder.brand)

# TYPE DEVICE
@router.message(newOrder.device_type)
async def type_device(message: types.Message, state: FSMContext):
    """ Тип сдаваемого устройства """
    await typing(message)
    if message.text == "📝 Свой вариант":
        await message.answer("📝 Напишите cвой вариант:", reply_markup=ReplyKeyboardRemove())
        await state.set_state(newOrder.other_device)

    elif message.text in DEVICES_RU:
        # Позже валидация + проверка (недопустимые символы и код, что бы в базу не залили)
        device_type = message.text
        # Получение брендов по типу устройства
        brands = get_brands(device_type)
        await state.update_data(device_type=device_type, brands=brands)
        brands.append("📝 Свой вариант")
        await message.answer("Выберите марку/бренд устройства", reply_markup = build_keyboard(brands)) 
        await state.set_state(newOrder.brand)

    else:
        await message.answer("Попробуйте еще раз выбрать из меню пункт")


# TYPE ORDER
@router.message(newOrder.order_type)
async def order_type(message: types.Message, state: FSMContext):
    """ Тип заказа - платный, гарантийный """
    await typing(message)

    if message.text == "🤬 Гарантийный":
        order_type = "guaranteed"
    elif message.text == "🤑 Платный":
        order_type = "paid"
    else:
        await message.answer("Попробуйте еще раз выбрать из меню пункт")
        return

    state_data = await state.get_data() # В нём только ser_id
    client_id = state_data.get("user_id")
    created_by = message.from_user.id
    created_date = await day_utcnow()
    status = "new"
    await state.update_data( 
        created_by=created_by,
        client_id=client_id, 
        created_date=created_date, 
        status=status,
        order_type=order_type
    )
    await message.answer("Выберите тип устройства:", reply_markup = build_keyboard(DEVICES_RU)) 
    await state.set_state(newOrder.device_type)

# START CREATE ORDER by USER_ID
# Можно будет вызывать как начало..
async def create_order(message: types.Message, state: FSMContext, user_id: uuid):
    """ Начало формирования заказа по user_id """
    await state.update_data(user_id=user_id) # Чистый, только user_id
    await message.answer("Выберите тип заказа", reply_markup = build_keyboard(["🤑 Платный", "🤬 Гарантийный"])) 
    await state.set_state(newOrder.order_type)

# TELEGRAM CLIENT
@router.message(newOrder.username_telegram)
async def username_telegram(message: types.Message, state: FSMContext):
    """ username_telegram клиента """
    await typing(message)
    answer = message.text
    if answer == "🎲 Пропустить":
        answer = None
    # Проверка в базе и предупреждение + варианты действий + валидация телеграм @name + валидация ввода 
    user_id = uuid.uuid4()
    time_reg = await day_utcnow()
    await state.update_data(username_telegram=answer, time_reg=time_reg, user_id=user_id)
    state_data = await state.get_data()
    print(state_data) # Удалить, для проверки выводил..

    # Create USER
    if await add_user(state_data):
        await message.answer("🎉 Новый клиент сохранен.")
    else:
        await message.answer("🚫 Есть проблема с сохранением в базу клиента")
        await state.clear()
        return
    await message.answer("Продолжим..")
    await state.clear()
    await create_order(message, state, user_id)

# PHONE CLIENT
@router.message(newOrder.phone_client)
async def phone_client(message: types.Message, state: FSMContext):
    """ Телефон клиента """
    await typing(message)
    answer = message.text
    if answer == "🎲 Пропустить":
        answer = None
    # Проверка в базе и предупреждение + варианты действий + валидация номера + валидация ввода + фильтр
    await state.update_data(phone=answer)
    await message.answer("Введите Телеграмм @Username клиента:", reply_markup = build_keyboard(["🎲 Пропустить"]))
    await state.set_state(newOrder.username_telegram)

# NAME CLIENT
@router.message(newOrder.name_client)
async def name_client(message: types.Message, state: FSMContext):
    """ Ввод имени клиента """
    await typing(message)
    # Проверка в базе и предупреждение клиента об этом + варианты действий + валидация + фильтр = позже
    await state.update_data(name=message.text)
    await message.answer("Введите Телефон клиента:", reply_markup = build_keyboard(["🎲 Пропустить"]))
    await state.set_state(newOrder.phone_client)

# CLIENT ADDING or SEARCH at DB
@router.message(newOrder.client)
async def client(message: types.Message, state: FSMContext):
    """Выбор добавления клиента или поиск """
    await typing(message)
    if message.text == "🔎 Найти клиента":
        await message.answer("В разработке..", reply_markup=ReplyKeyboardRemove())
        await state.set_state(newOrder.search_client)
        await state.clear()
        return
    elif message.text == "📝 Создать клиента":
        await message.answer("Введите Имя клиента:", reply_markup = build_keyboard([]))
        await state.set_state(newOrder.name_client)
    else:
        await message.answer("Попробуйте еще раз выбрать из меню пункт")


# START CREATE NEW ORDER
@router.message(F.text == "📝 Новый заказ")
async def new_order(message: types.Message, state: FSMContext):
    """ Новый заказ """
    await typing(message)
    user_id = message.from_user.id
    if not await is_manager(user_id):
        logger.error(f"{user_id} попытка не санкционированного доступа в 📝 Новый заказ")
        return

    await message.answer(
        "Найти клиента или создать заново:",
        reply_markup = build_keyboard(["📝 Создать клиента", "🔎 Найти клиента"])
    )
    await state.set_state(newOrder.client)

# CANCEL STATE & KEYBOARD
@router.message(F.text == "✖️ Отмена")
async def cancel(message: types.Message, state: FSMContext): 
    """ Отмена """
    await typing(message)
    await state.clear()
    await message.answer(
        "Отменено. Состояние сброшено.",
        reply_markup=ReplyKeyboardRemove()
    )
