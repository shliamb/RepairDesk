#! app/handlers/edit_order.py
from handlers.common import typing, is_manager, is_admin, is_master
from logs.set_logger import set_logger
logger = set_logger(name="handlers")
from utils.formatters import remove_emojis, extract_emoji, format_phone, format_date_nice, format_telegram_username, safe_int, safe_decimal
from database.users import get_user_by_user_id, get_user_by_tg
from utils.serialize import json_serializer, custom_json_decoder
from handlers.edit_client import start_edit_client
from handlers.actions_order import actions_order_tap
from aiogram import Router, types, F
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from database.orders import OrderService
from config import HUMAN_QUALITY, CHANGE_ORDER, CURRENCY, DEVICE_ICO, ORDER_STATUS_COLOR, ORDER_STATUS_RU, ORDER_STATUS, EDIT_ORDER, CANCEL, UI_TEXTS, ADMIN_ID
from keyboards.workshop import build_keyboard
from database import db
from handlers.viewing_orders import Order # State из viewing_orders.py для перехода
import json
from datetime import datetime
from decimal import Decimal



router = Router()
order = OrderService(db)









######## EDIT ORDER ############
""" states import from handlers/viewing_orders.py.py Order.edit and Order.action
    AT DB ORDERS example :
    ...
    'services': [{'work': 'Замена экрана', 'pieces': '1', 'price': '1000', 'warranty_period': '3'}] - str,
    'parts': [{'part': 'Матрица', 'pieces': '1', 'price': '2500', 'clean_price': '350', 'warranty_period': '1'}],
    'prepayment': [{'description': 'На матрицу', 'amount': '2500', 'date': '14.12.2025...'}],
"""

class Edit(StatesGroup):
    order = State()
    status = State()
    diagnos = State()
    notes = State()
    work = State()
    part = State()
    prepayment = State()



# SAVE DATA TO DB Сохранение в базу изменений и вывод заказа снова
async def edit_order_db(data: dict, state: FSMContext, message: types.Message):
    """ Изменяю в базе и вызываю снова на экран заказ"""
    id = data.get("id")
    lang = message.from_user.language_code
    result = await order.edit_order(data)
    if not result:
        logger.error("Error in saving in the database")
        if lang == "ru": await message.answer("🚫 Ошибка в сохранении в базе")
        else: await message.answer("🚫 Error in saving in the database")
        return

    if lang == "ru": await message.answer("👍 Изменения сохранены", reply_markup=ReplyKeyboardRemove())
    else: await message.answer("👍 The changes are saved", reply_markup=ReplyKeyboardRemove())
    # Вывести заказ снова, что бы видно было что изменилось..
    await start_edit_order(id, state, message)


# STATUS ORDER
@router.message(Edit.status)
async def choose_status(message: types.Message, state: FSMContext):
    """ Выбор статуса заказа """
    await typing(message)
    lang = message.from_user.language_code

    if message.text in list(ORDER_STATUS_RU.values()):
        # dict в котором меняем key и values, что бы вернуть ключь для базы:
        revers = {value: key for key, value in ORDER_STATUS_RU.items()}

    elif message.text in list(ORDER_STATUS.values()):
        revers = {value: key for key, value in ORDER_STATUS.items()}

    else:
        if lang == "ru": await message.answer("🚫 Попробуйте еще раз выбрать пункт из меню")
        else: await message.answer("🚫 Try again to select an item from the menu")
        return
        
    state_data = await state.get_data()
    new_status = revers[message.text]
    data = {
        "id": state_data.get("id"),
        "status": new_status
    }
    if new_status == "ready": data["completion_date"] = datetime.now()
    await edit_order_db(data, state, message)


# DIAGNOSTICS
@router.message(Edit.diagnos)
async def edit_diagnos(message: types.Message, state: FSMContext):
    """ Заполнение диагностики """
    await typing(message)
    lang = message.from_user.language_code
    user_tele_id = message.from_user.id

    if message.text:
        state_data = await state.get_data()
        await state.update_data(data={"id": state_data.get("id"), "diagnosis": message.text})
    
    else:
        if lang == "ru": await message.answer("🚫 Наберите текст диагностики")
        else: await message.answer("🚫 Type the diagnostic text")
        return

    state_data = await state.get_data()
    data_user = await get_user_by_tg(user_tele_id)
    user_id = data_user.get("user_id") # UUID MASTER
    data = {
        "id": state_data.get("id"),
        "diagnosis": message.text,
        "master": user_id # UUID
    }
    await edit_order_db(data, state, message)


# NOTES / COMMENTS ORDER
@router.message(Edit.notes)
async def add_note(message: types.Message, state: FSMContext):
    """ Добавление заметки / комментария к заказу"""
    await typing(message)
    lang = message.from_user.language_code

    if not message.text:
        if lang == "ru": await message.answer("🚫 Наберите текст комментария")
        else: await message.answer("🚫 Type the comment text")
        return

    state_data = await state.get_data()
    id = state_data.get("id")
    data_order = await order.get_order_id(id)

    id_user = message.from_user.id
    data_user = await get_user_by_tg(id_user) # real_name  name
    user_telegram_name = data_user.get("username_telegram")

    comments = data_order.get("comments", []) or []
    if comments: comments = json.loads(comments).copy()


    comments.append({"note": message.text, "date": datetime.now(), "user_name_telegram": user_telegram_name})
    data = {
        "id": state_data.get("id"),
        "comments": json.dumps(comments, default=json_serializer, ensure_ascii=False)
    }
    await edit_order_db(data, state, message)



# ADD SERVICE/WORK
@router.message(Edit.work)
async def add_work(message: types.Message, state: FSMContext):
    """ Добавление услуги/работы 
        да, колхоз.. но на одном State """
    await typing(message)

    lang = message.from_user.language_code
    user_tele_id = message.from_user.id
    state_data = await state.get_data()
    work, pieces, price, warranty_period = state_data.get("work"), state_data.get("pieces"), state_data.get("price"), state_data.get("warranty_period")
    
    if not work:
        await state.update_data(work=message.text)
        if lang == "ru": await message.answer("🧮 Введите количество этой услуги:")
        else: await message.answer("🧮 Enter quantity:")
        return
    
    elif work and not pieces:
        pieces = safe_int(message.text)
        if not pieces:
            if lang == "ru": await message.answer("🚫 Введите количество:")
            else: await message.answer("🚫 Enter the quantity:")
            return
        if lang == "ru": await message.answer("💲 Введите стоимость услуги:")
        else: await message.answer("💲 Enter the cost of the service:")
        await state.update_data(pieces=pieces)
        return
    
    elif work and pieces and price is None:
        price = safe_decimal(message.text)
        if price is None:
            if lang == "ru": await message.answer("🚫 Введите стоимость услуги:")
            else: await message.answer("🚫 Enter the cost of the service:")
            return
        if lang == "ru": await message.answer("📅 Введите срок гарантии:")
        else: await message.answer("📅 Enter the warranty period:")
        await state.update_data(price=price)
        return

    elif work and pieces and price is not None and not warranty_period:
        warranty_period = safe_int(message.text)
        if warranty_period is None:
            if lang == "ru": await message.answer("🚫 Введите срок гарантии:")
            else: await message.answer("🚫 Enter the warranty period:")
            return
        await state.update_data(warranty_period=warranty_period) # !?

        # STATE:
        state_data = await state.get_data()
        id = state_data.get("id")
        work: str = state_data.get("work")
        pieces: int = state_data.get("pieces")
        price: Decimal = state_data.get("price")
        warranty_period: int = state_data.get("warranty_period")

        # ORDER:
        data_order = await order.get_order_id(id)
        old_services = data_order.get("services")
        old_services: list = json.loads(old_services) if old_services else []

        # ДОБАВЛЕНИЕ НОВОЙ УСЛУГИ
        services = {
            'work': work,
            'pieces': pieces,
            'price': json_serializer(price),
            'warranty_period': warranty_period,
        }
        old_services.append(services)

        cost_repair = Decimal(0)
        for one in old_services:
            cost_repair += safe_decimal(one.get("price", Decimal("0"))) * int(one.get("pieces"))

        # Сохранение результатов в базу
        data_user = await get_user_by_tg(user_tele_id)
        user_id = data_user.get("user_id") # UUID MASTER
        data = {
            'id': id,
            'services': json.dumps(old_services, ensure_ascii=False),
            'cost_repair': cost_repair,
            'master': user_id # UUID
        }
        await edit_order_db(data, state, message)
        await state.update_data(work=None, pieces=None, price=None, warranty_period=None)
        return
    


# ADD PART
@router.message(Edit.part)
async def add_part(message: types.Message, state: FSMContext):
    """ Добавление запчастей """
    await typing(message)

    lang = message.from_user.language_code
    user_tele_id = message.from_user.id
    state_data = await state.get_data()
    part, pieces, price, clean_price, warranty_period = state_data.get("part"), state_data.get("pieces"), state_data.get("price"), state_data.get("clean_price"), state_data.get("warranty_period")
    
    if not part:
        await state.update_data(part=message.text)
        if lang == "ru": await message.answer("🧮 Введите количество:")
        else: await message.answer("🧮 Enter quantity:")
        return
    
    elif part and not pieces:
        pieces = safe_int(message.text)
        if not pieces:
            if lang == "ru": await message.answer("🚫 Введите количество:")
            else: await message.answer("🚫 Enter the quantity:")
            return
        if lang == "ru": await message.answer("💲 Введите стоимость запчасти для клиента:")
        else: await message.answer("💲 Enter the cost of the spare part for the customer:")
        await state.update_data(pieces=pieces)
        return
    
    elif part and pieces and price is None:
        price = safe_decimal(message.text)
        if price is None:
            if lang == "ru": await message.answer("🚫 Введите стоимость запчасти:")
            else: await message.answer("🚫 Enter the cost of the spare part:")
            return
        if lang == "ru": await message.answer("📦 Введите закупочную цену запчасти:")
        else: await message.answer("📦 Enter the purchase price of the spare part:")
        await state.update_data(price=price)
        return
    
    elif part and pieces and price is not None and clean_price is None:
        clean_price = safe_decimal(message.text)
        if clean_price is None:
            if lang == "ru": await message.answer("🚫 Введите закупочную цену запчасти:")
            else: await message.answer("🚫 Enter the purchase price of the spare part:")
            return
        if lang == "ru": await message.answer("📅 Введите срок гарантии:")
        else: await message.answer("📅 Enter the warranty period:")
        await state.update_data(clean_price=clean_price)

    elif part and pieces and price is not None and clean_price is not None and not warranty_period:
        warranty_period = safe_int(message.text)
        if warranty_period is None:
            if lang == "ru": await message.answer("🚫 Введите срок гарантии:")
            else: await message.answer("🚫 Enter the warranty period:")
            return
        await state.update_data(warranty_period=warranty_period) # !?

        # STATE:
        state_data = await state.get_data()
        id = state_data.get("id")
        part: str = state_data.get("part")
        pieces: int = state_data.get("pieces")
        price: Decimal = state_data.get("price")
        clean_price: Decimal = state_data.get("clean_price")
        warranty_period: int = state_data.get("warranty_period")

        # ORDER:
        data_order = await order.get_order_id(id)
        old_parts = data_order.get("parts")
        old_parts: list = json.loads(old_parts) if old_parts else []

        # ДОБАВЛЕНИЕ НОВОЙ ЗАПЧАСТИ
        data_part = {
            'part': part,
            'pieces': pieces,
            'price': json_serializer(price),
            'clean_price': json_serializer(clean_price),
            'warranty_period': warranty_period,
        }
        old_parts.append(data_part)

        cost_of_parts, cost_price = Decimal(0), Decimal(0)

        for one in old_parts:
            cost_of_parts += safe_decimal(one.get("price")) * int(one.get("pieces"))
            cost_price += safe_decimal(one.get("clean_price", Decimal("0")))

        # Сохранение результатов в базу
        data_user = await get_user_by_tg(user_tele_id)
        user_id = data_user.get("user_id") # UUID MASTER
        data = {
            'id': id,
            'parts': json.dumps(old_parts, ensure_ascii=False),
            'cost_of_parts': cost_of_parts, # Цена за все запчасти
            'cost_price': cost_price, # Цена всех запчастей по себистоимости
            'master': user_id # UUID
        }
        await edit_order_db(data, state, message)

        await state.update_data(part=None, pieces=None, price=None, clean_price=None, warranty_period=None)
        return


# ADD PREPAYMENT:
@router.message(Edit.prepayment)
async def add_prepayment(message: types.Message, state: FSMContext):
    """ Внесение предоплаты клиента """
    await typing(message)

    lang = message.from_user.language_code
    state_data = await state.get_data()
    description, amount = state_data.get("description"), state_data.get("amount")
    
    if not description:
        await state.update_data(description=message.text)
        if lang == "ru": await message.answer("💲 Вносимая сумма:")
        else: await message.answer("💲 Deposit amount:")
        return
    
    elif description and not amount:
        amount = safe_decimal(message.text)
        if not amount:
            if lang == "ru": await message.answer("🚫 Введите вносимую сумму:")
            else: await message.answer("🚫 Enter the amount to be deposited:")
            return
        await state.update_data(amount=amount)

        # STATE:
        state_data = await state.get_data()
        id = state_data.get("id")
        description: str = state_data.get("description")
        amount: Decimal = state_data.get("amount")

        # ORDER:
        data_order = await order.get_order_id(id)
        old_prepayment = data_order.get("prepayment")
        old_prepayment: list = json.loads(old_prepayment) if old_prepayment else []

        # ДОБАВЛЕНИЕ УСЛУГИ
        prepayment = {
            'description': description,
            'amount': amount,
            'date': datetime.now(),
        }
        old_prepayment.append(prepayment)

        cost_prepayment = Decimal(0)

        for one in old_prepayment:
            cost_prepayment += safe_decimal(one.get("amount"))

        # Сохранение результатов в базу
        data = {
            'id': id,
            'prepayment': json.dumps(old_prepayment, default=json_serializer, ensure_ascii=False),
            'cost_prepayment': cost_prepayment
        }
        await edit_order_db(data, state, message)

        await state.update_data(description=None, amount=None, date=None)
        return


# PUSH BUTTONS EDITION ORDER
@router.message(Edit.order)
async def choose_edit_order(message: types.Message, state: FSMContext):
    """ PUSH BUTTONS EDITION ORDER """
    await typing(message)
    lang = message.from_user.language_code
    user_id = message.from_user.id

    # CHANGE STATUS ORDER
    if message.text in (EDIT_ORDER["stat_ru"], EDIT_ORDER["stat"]):

        # Проверка на мастера:
        if not await is_master(user_id):
            if lang == "ru": await message.answer("🚫 У вас нет доступа. Вы не мастер.")
            else: await message.answer("🚫 You don't have access. You are not a master.")
            return

        if lang == "ru":
            buttons = list(ORDER_STATUS_RU.values())
            buttons.append(CANCEL["ru"])
            message_text = "📊 Выберите статус заказа:"
        else:
            buttons = list(ORDER_STATUS.values())
            buttons.append(CANCEL["en"])
            message_text = "📊 Select the order status:"

        await message.answer(message_text, reply_markup = build_keyboard(buttons))
        await state.set_state(Edit.status)

    # WRITE DIAGNOSTIC
    elif message.text in (EDIT_ORDER["dia_ru"], EDIT_ORDER["dia"]):

        # Проверка на мастера:
        if not await is_master(user_id):
            if lang == "ru": await message.answer("🚫 У вас нет доступа. Вы не мастер.")
            else: await message.answer("🚫 You don't have access. You are not a master.")
            return

        buttons = []
        if lang == "ru":
            buttons.append(CANCEL["ru"])
            message_text = "📝 Напишите текст диагностики:"
        else:
            buttons.append(CANCEL["en"])
            message_text = "📝 Write the diagnostic text:"

        await message.answer(message_text, reply_markup = build_keyboard(buttons))
        await state.set_state(Edit.diagnos)

    # ADD COMMENTS
    elif message.text in (EDIT_ORDER["notes_ru"], EDIT_ORDER["notes"]):
        buttons = []
        if lang == "ru":
            buttons.append(CANCEL["ru"])
            message_text = "💬 Напишите комментарий к заказу:"
        else:
            buttons.append(CANCEL["en"])
            message_text = "💬 Write a comment on the order:"

        await message.answer(message_text, reply_markup = build_keyboard(buttons))
        await state.set_state(Edit.notes)

    # CLEAR PARTS AND WORK
    elif message.text in (EDIT_ORDER["clear_ru"], EDIT_ORDER["clear"]):

        # Очистка только ADMIN:
        if not await is_admin(user_id):
            if lang == "ru": await message.answer("🚫 У вас нет доступа. Обратитесь к администратору")
            else: await message.answer("🚫 You don't have access. Contact the administrator")
            return
        
        state_data = await state.get_data()
        data = {
            "id": state_data.get("id"),
            "services": None,
            "parts": None,
            "prepayment": None,
            "net_profit": None,
            "cost_repair": None,
            "cost_of_parts": None,
            "cost_prepayment": None,
            "master": None
            # "cost_diagnostics": None
        }
        await edit_order_db(data, state, message)


    # ADD SERVICE/WORK
    elif message.text in (EDIT_ORDER["add_serv_ru"], EDIT_ORDER["add_serv"]):

        # Проверка на мастера:
        if not await is_master(user_id):
            if lang == "ru": await message.answer("🚫 У вас нет доступа. Вы не мастер.")
            else: await message.answer("🚫 You don't have access. You are not a master.")
            return

        buttons = []
        if lang == "ru":
            buttons.append(CANCEL["ru"])
            message_text = "🔧 Опишите выполненную работу:"
        else:
            buttons.append(CANCEL["en"])
            message_text = "🔧 Describe the completed work:"

        await message.answer(message_text, reply_markup = build_keyboard(buttons))
        await state.set_state(Edit.work)


    # ADD PART
    elif message.text in (EDIT_ORDER["add_part_ru"], EDIT_ORDER["add_part"]):

        # Проверка на мастера:
        if not await is_master(user_id):
            if lang == "ru": await message.answer("🚫 У вас нет доступа. Вы не мастер.")
            else: await message.answer("🚫 You don't have access. You are not a master.")
            return

        buttons = []
        if lang == "ru":
            buttons.append(CANCEL["ru"])
            message_text = "🔩 Введите название запчасти:"
        else:
            buttons.append(CANCEL["en"])
            message_text = "🔩 Enter the name of the spare part:"

        await message.answer(message_text, reply_markup = build_keyboard(buttons))
        await state.set_state(Edit.part)


    # ADD PREPAYMENT
    elif message.text in (EDIT_ORDER["prepayment_ru"], EDIT_ORDER["prepayment"]):
        buttons = []
        if lang == "ru":
            buttons.append(CANCEL["ru"])
            message_text = "📝 Описания предоплаты:"
        else:
            buttons.append(CANCEL["en"])
            message_text = "📝 Prepayment Descriptions:"

        await message.answer(message_text, reply_markup = build_keyboard(buttons))
        await state.set_state(Edit.prepayment)


    # GET ACTION
    elif message.text in UI_TEXTS[lang]["action"]:
        state_data = await state.get_data()
        id = state_data.get("id")

        buttons = [UI_TEXTS[lang]["get_photo"], UI_TEXTS[lang]["get_pdf"], UI_TEXTS[lang]["payd"], UI_TEXTS[lang]["delet"], UI_TEXTS[lang]["cancel"]]
        if lang == "ru": intro_text = f"Выберите действие по заказу:"
        else: intro_text = f"Select the order action:"

        await message.answer(intro_text, reply_markup = build_keyboard(buttons))
        await state.update_data(id=id)
        await state.set_state(Order.action)
        

    else:
        if lang == "ru": await message.answer("🚫 Попробуйте еще раз выбрать пункт из меню")
        else: await message.answer("🚫 Try again to select an item from the menu")
        return
    





#### UTILS OPEN FULL ORDER  ####
async def format_order_card(lang, **kwargs):
    """Форматирует карточку заказа"""
    
    if lang == "ru":
        device_ico = DEVICE_ICO
        order_status_color = ORDER_STATUS_COLOR
        status_dict = ORDER_STATUS_RU
        texts = {
            'order': '📋 ЗАКАЗ',
            'status': 'СОСТОЯНИЕ',
            'client': 'КЛИЕНТ',
            'device': 'УСТРОЙСТВО',
            'accepted': '📥 ПРИНЯЛ',
            'master': '👨‍🔧 МАСТЕР',
            'diagnosis': '⏱️ ДИАГНОСТИКА',
            'diagnostic_result': '🔍 РЕЗУЛЬТ. ДИАГНОСТИКИ',
            'problem': '⚠️ ПРОБЛЕМА',
            'services': '🛠️ УСЛУГИ',
            'parts': '🔩 ЗАПЧАСТИ',
            'prepayment': '💸 ПРЕДОПЛАТА',
            'total_prepayment': 'предоплата',
            'total': '💰 К ОПЛАТЕ',
            'total_work': 'работы',
            'total_parts': 'запчасти',
            'tips': 'Чай',
            'comments': '💬 КОММЕНТАРИИ',
            'month': 'мес',
            'equipment': 'Комплектация',
            'appearance': 'Состояние',
            'paid': 'Платный',
            'warranty': 'Гарантийный',
            'by': 'от',
            'until': 'до',
            'phone': 'Телефон',
            'empty': 'Не указано',
            'tips': 'Чаевые',
            'total_tips': 'чаевые',
            'total_profit': 'прибыль',
            'buy': 'закупка'
        }

    else:
        device_ico = DEVICE_ICO
        order_status_color = ORDER_STATUS_COLOR
        status_dict = ORDER_STATUS
        texts = {
            'order': '📋 ORDER',
            'status': 'CONDITION',
            'client': 'CLIENT',
            'device': 'DEVICE',
            'accepted': '📥 ACCEPTED BY',
            'master': '👨‍🔧 MASTER',
            'diagnosis': '⏱️ DIAGNOSIS',
            'diagnostic_result': '🔍 DIAGNOSTIC RESULT',
            'problem': '⚠️ PROBLEM',
            'services': '🛠️ SERVICES',
            'parts': '🔩 PARTS',
            'prepayment': '💸 PREPAYMENT',
            'total_prepayment': 'prepayment',
            'total': '💰 TOTAL',
            'total_work': 'work',
            'total_parts': 'parts',
            'tips': 'tips',
            'comments': '💬 COMMENTS',
            'month': 'mth',
            'equipment': 'Equipment',
            'appearance': 'Appearance',
            'paid': 'Paid',
            'warranty': 'Warranty',
            'by': 'by',
            'until': 'until',
            'phone': 'Phone',
            'empty': 'Not specified',
            'tips': 'Tips',
            'total_tips': 'tips',
            'total_profit': 'profit',
            'buy': 'purchase'
        }
    
    # Сбор визуализации вывода заказа
    order_card = ""
    # Заказ номер:
    order_card += (
        f"<b>{texts['order']} {kwargs.get('order_number')}:</b>\n"
        "\n"
    )
    # Статус заказа, платный/гарантийный
    order_card += (
        f"<b>{order_status_color.get(kwargs.get('status'), '')} {texts['status']}:</b>\n"
        f"        {texts['paid'] if kwargs.get('order_type') == 'paid' else texts['warranty']}\n"
        f"        {status_dict.get(kwargs.get('status'), '')}\n"
        "\n"
    )
    # Инфа о клиенте:
    order_card += (
        f"<b>{kwargs.get('ico_client')} {texts['client']}:</b>\n"
        f"        {kwargs.get('real_name_client')}\n"
    )
    if kwargs.get('client_phone'):
        formatted_phone = format_phone(kwargs.get('client_phone'))
        order_card += f"        {formatted_phone or texts['empty']}\n"

    if kwargs.get('client_telegram'): order_card += f"        {kwargs.get('client_telegram')}\n"
    if kwargs.get('a_tip'): order_card += f"        {texts['tips']}: {kwargs.get('a_tip')}{CURRENCY}\n"
    order_card += "\n"

    # Инфа о устройстве:
    order_card += (
        f"<b>{device_ico.get(kwargs.get('device_type', ''))} {texts['device']}:</b>\n"
        f"        {kwargs.get('device_type') or texts['empty']}\n"
    )
    if kwargs.get('device_brand'): order_card += f"        {kwargs.get('device_brand')}"
    if kwargs.get('device_model'): order_card += f" • {kwargs.get('device_model')}"
    order_card += "\n"
    if kwargs.get('sn_imei'): order_card += f"        SN/IMEI: {kwargs.get('sn_imei')}\n"
    if kwargs.get('equipment'): order_card += f"        {texts['equipment']}: {kwargs.get('equipment')}\n"
    if kwargs.get('appearance'): order_card += f"        {texts['appearance']}: {kwargs.get('appearance')}\n"
    order_card += "\n"

    # Кто принял устройство:
    order_card += (
        f"<b>{texts['accepted']}:</b>\n"
        f"        {texts['by']} {kwargs.get('real_name_created')}\n"
        f"        {kwargs.get('created_date')}\n"
    )
    if kwargs.get('created_telegram'): order_card += f"        {kwargs.get('created_telegram')}\n"
    #f"        Комментарии: Очень спешил.\n\n"
    order_card += "\n"

    # Кто из мастеров взял заказ:
    if kwargs.get('real_name_master'):
        order_card += (
            f"<b>{texts['master']}:</b>\n"
            f"        {kwargs.get('real_name_master')}\n"
        )
        if kwargs.get('master_telegram'): order_card += f"        {kwargs.get('master_telegram')}\n"
        #f"        Комментарии: В пятницу доделаю, не давите бля!\n\n" # коммент от мастера
        order_card += "\n"

    # Диагностика до и цена
    order_card += (
        f"<b>{texts['diagnosis']}:</b>\n"
        f"        {texts['until']} {kwargs.get('diagnosis_before')}\n"
        f"        {kwargs.get('cost_diagnostics', 0)} {CURRENCY}\n"
    )
    order_card += "\n"

    # Описание проблемы устройства:
    order_card += (
        f"<b>{texts['problem']}:</b>\n"
        f"        {kwargs.get('problem')}\n"
    )
    order_card += "\n"

    # Комментарии по пунктам..
    comments = kwargs.get('comments')
    if comments:
        order_card += f"<b>{texts['comments']}:</b>\n"
        for one in comments:
            order_card += f"        <b>• {one.get('user_name_telegram')} {format_date_nice(one.get('date'), lang)}</b>: {one.get('note')}\n"
        order_card += "\n"

    # Результат диагностики:
    if kwargs.get('diagnosis'):
        order_card += (
            f"<b>{texts['diagnostic_result']}:</b>\n"
            f"        <pre>{kwargs.get('diagnosis')}</pre>\n"
        )
        order_card += "\n"

    # SERVICES:
    if kwargs.get('services'):
        i = 1
        services = kwargs.get('services')
        order_card += (
            f"<b>{texts['services']}:</b>\n"
        )
        for one in services:
            order_card += f"        {i}. {one.get('work')}  x{one.get('pieces')} • {one.get('price')}{CURRENCY} • {one.get('warranty_period')} {texts['month']}\n"
            i += 1

        order_card += "\n"

    # PARTS:
    if kwargs.get('parts'):
        i = 1
        parts = kwargs.get('parts')
        order_card += (
            f"<b>{texts['parts']}:</b>\n"
        )
        for one in parts:
            order_card += f"        {i}. {one.get('part')}  x{one.get('pieces')} • {one.get('price')}{CURRENCY} ({one.get('clean_price', '0')}{CURRENCY}) • {one.get('warranty_period')} {texts['month']}\n"
            i += 1

        order_card += "\n"

    # PREPAYMENT:
    if kwargs.get('prepayment'):
        i = 1
        prepayment = kwargs.get('prepayment')
        order_card += (
            f"<b>{texts['prepayment']}:</b>\n"
        )
        for one in prepayment:
            order_card += f"        {i}. {one.get('description')} • {one.get('amount')}{CURRENCY} • {format_date_nice(one.get('date'), lang)}\n"
            i += 1
        
        order_card += "\n"


    if kwargs.get('services') or kwargs.get('parts'):
        total = kwargs.get('cost_repair') + kwargs.get('cost_of_parts') - kwargs.get('cost_prepayment')
        net_profit = kwargs.get('cost_repair') + kwargs.get('cost_of_parts') - kwargs.get('cost_price')
        data = {'id': kwargs.get('id'), 'net_profit': net_profit}
        await order.edit_order(data)

        # <b>
        # <i>
        # <u>  - подчеркивание
        # <code> 
        # <pre>

        order_card += (
            f"-------------------------------\n"
            f"• <i>{texts['total_work']}: {kwargs.get('cost_repair') or 0:.0f} {CURRENCY}</i>\n"
            f"• <i>{texts['total_parts']}: {kwargs.get('cost_of_parts') or 0:.0f} {CURRENCY}</i>\n" # / {texts['buy']}: {kwargs.get('cost_price'):.0f} {CURRENCY}</i>\n"      # • parts: 5,400.00 ₽ | закупка: 2,300.00 ₽ buy
            f"• <i>{texts['total_prepayment']}: {kwargs.get('cost_prepayment') or 0:.0f} {CURRENCY}</i>\n"
            f"• <i>{texts['total_tips']}: {kwargs.get('a_tip') or 0:.0f} {CURRENCY}</i>\n"
            f"• <i>{texts['total_profit']}: {net_profit or 0:.0f} {CURRENCY}</i>\n"
            f"-------------------------------\n"
            f"<b>{texts['total']}: {total:,} {CURRENCY}</b>\n"
        )
        order_card += "\n"

    
    return order_card



# START OPEN FULL ORDER
async def start_edit_order(order_id: int, state: FSMContext, message: types.Message):
    """ Выводит заказ полностью и кнопки с редактированием """
    await typing(message)
    lang = message.from_user.language_code
    if not isinstance(order_id, int):
        logger.error(f"{id} is not digit")
        return
    
    await state.clear() # !!!!!
    
    data_order = await order.get_order_id(order_id)

    id = data_order.get("id")
    # order_number = data_order.get("order_number")
    # location = data_order.get("location")
    # sn_imei = data_order.get("sn_imei")
    # status = data_order.get("status")
    # order_type = data_order.get("order_type")
    # device_type = data_order.get("device_type")
    # device_brand = data_order.get("device_brand")
    # device_model = data_order.get("device_model")
    # # equipment = data_order.get("equipment")
    # # problem = data_order.get("problem")
    # # appearance = data_order.get("appearance")
    # created_date = data_order.get("created_date")
    # diagnosis_before = data_order.get("diagnosis_before")
    # cost_repair = data_order.get("cost_repair")
    # cost_of_parts = data_order.get("cost_of_parts")
    # cost_diagnostics = int(data_order.get("cost_diagnostics"))
    # guarantee = data_order.get("guarantee")
    # path_photo = data_order.get("guarantee")
    # # client_id = data_order.get("client_id")
    # # created_by = data_order.get("created_by") # telegram id !!
    # # real_name_created = data_order.get("real_name_created")
    # # master = data_order.get("master")
    # edit_history = data_order.get("edit_history")
    # # comments = data_order.get("comments")
    # completed_works = data_order.get("completed_works")
    # diagnosis = data_order.get("diagnosis")
    # #a_tip = data_order.get("a_tip")

    # PROBLEN
    problem = data_order.get("problem")
    problem = json.loads(problem) if problem else ""
    problem = " • ".join(problem.copy())

    # EQUIPMENT
    equipment = data_order.get("equipment")
    equipment = json.loads(equipment) if equipment else ""
    equipment = " • ".join(equipment.copy())

    # APPEARANCE
    appearance = data_order.get("appearance")
    appearance = json.loads(appearance) if appearance else ""
    appearance = " • ".join(appearance.copy())

    # GET DATA CLIENT:
    client_uuid = data_order.get("client_id")
    # Получение данных клиента:
    data_client = await get_user_by_user_id(client_uuid)
    client_telegram = format_telegram_username(data_client.get("username_telegram"))
    client_name = data_client.get("real_name") or data_client.get("name")
    client_phone = data_client.get("phone")
    hum_quality = data_client.get("hum_quality")

    # GET DATA MANAGER:
    created_by_telegram_id = data_order.get("created_by") # telegram id !!
    data_created = await get_user_by_tg(created_by_telegram_id)
    real_name_created = data_created.get("real_name_created") or data_created.get("name")
    created_telegram = format_telegram_username(data_created.get("username_telegram"))

    # GET DATA MASTER:
    uuid_master = data_order.get("master") # UUID
    # print("data_order:", data_order)
    # print("uuid_master:", uuid_master)
    data_master = await get_user_by_user_id(uuid_master)
    real_name_master = data_master.get("real_name_created") or data_master.get("name")
    master_telegram = format_telegram_username(data_master.get("username_telegram"))

    # COMMENTS:
    comments: list = data_order.get("comments", []) or []
    if comments: comments = json.loads(comments, object_hook=custom_json_decoder).copy() # из str -> в Json

    # SERVICE
    services: list = data_order.get("services", []) or []
    if services: services = json.loads(services).copy()

    # PARTS
    parts: list = data_order.get("parts", []) or []
    if parts: parts = json.loads(parts).copy()

    # PREPAYMENT
    prepayment: list = data_order.get("prepayment")
    if prepayment: prepayment = json.loads(prepayment, object_hook=custom_json_decoder).copy() # из str -> в Json


    # NET PROFIT
    net_profit: Decimal = data_order.get("net_profit") or 0

    # COST REPAIR
    cost_repair: Decimal = data_order.get("cost_repair") or 0

    # COST PARTS Цена всех запчастей
    cost_of_parts: Decimal = data_order.get("cost_of_parts") or 0

    # COST PREPAYMENT
    cost_prepayment: Decimal = data_order.get("cost_prepayment") or 0

    # COST PART PRICE Цена закупки запчастей
    cost_price: Decimal = data_order.get("cost_price") or 0


    quality = HUMAN_QUALITY[lang].get(hum_quality) or ""
    ico_client = extract_emoji(quality) or "😐"


    # NEW DATA
    order_data = {
        'id': id,
        'order_number': data_order.get("order_number"),
        'order_type': data_order.get("order_type"),
        'status': data_order.get("status"),
        'real_name_client': client_name,
        'client_phone': client_phone,
        'client_telegram': client_telegram,
        'device_type': remove_emojis(data_order.get("device_type")),
        'device_brand': data_order.get("device_brand"),
        'device_model': data_order.get("device_model"),
        'sn_imei': data_order.get("sn_imei"),
        'equipment': equipment,
        'appearance': appearance,
        'real_name_created': real_name_created,
        'created_telegram': created_telegram,
        'created_date': format_date_nice(data_order.get("created_date"), lang),
        'diagnosis_before': format_date_nice(data_order.get("diagnosis_before"), lang),
        'cost_diagnostics': safe_decimal(data_order.get("cost_diagnostics")), # !?
        'problem': problem,
        'comments': comments,
        'master': data_order.get("master"),
        'diagnosis': data_order.get("diagnosis"),
        'a_tip': data_order.get("a_tip"),
        'real_name_master': real_name_master,
        'master_telegram': master_telegram,
        'services': services,
        'parts': parts,
        'cost_price': cost_price, # Цена всех запчастей по закупке
        'prepayment': prepayment,
        'net_profit': net_profit,
        'cost_repair': cost_repair,
        'cost_of_parts': cost_of_parts, # Цена всех запчастей для клиента
        'cost_prepayment': cost_prepayment,
        'ico_client': ico_client
    }

    await message.answer(await format_order_card(lang, **order_data), parse_mode="HTML")
    if lang == "ru":
        message_text = "Выберите то, что хотите изменить:"

        buttons = [EDIT_ORDER["stat_ru"], EDIT_ORDER["dia_ru"], EDIT_ORDER["add_serv_ru"], EDIT_ORDER["add_part_ru"], EDIT_ORDER["notes_ru"], EDIT_ORDER["prepayment_ru"], EDIT_ORDER["clear_ru"], UI_TEXTS[lang]["action"], CANCEL["ru"]]
    else:
        message_text = "Select what you want to change:"
        buttons = [EDIT_ORDER["stat"], EDIT_ORDER["dia"], EDIT_ORDER["add_serv"], EDIT_ORDER["add_part"], EDIT_ORDER["notes"], EDIT_ORDER["prepayment"], EDIT_ORDER["clear"], UI_TEXTS[lang]["action"], CANCEL["en"]]
    await message.answer(message_text, reply_markup = build_keyboard(buttons))

    await state.update_data(id=id, order_number=id)
    await state.set_state(Edit.order)




    




######### START EDIT ##############
@router.message(Order.edit)
async def process_edit_order(message: types.Message, state: FSMContext):
    """ После нажатия кнопки Открыть на заказе, выбираем что менять 
        заказ или данные клиента """
    await typing(message)
    state_data = await state.get_data()
    order_id = state_data.get("id")
    lang = message.from_user.language_code

    # EDIT ORDER:
    if message.text in (CHANGE_ORDER["order_ru"], CHANGE_ORDER["order_en"]):
        # Отдельный вызов редактирования заказа
        await start_edit_order(order_id, state, message)
        return

    # EDIT CLIENT:
    elif message.text in (CHANGE_ORDER["client_ru"], CHANGE_ORDER["client_en"]):
        data_order = await order.get_order_id(order_id)
        client_id = data_order.get("client_id")
        await start_edit_client(client_id, state, message)
        #await message.answer(f"Меняем данные клиента под заказом {order_id}")
        return

    else:
        if lang == "ru": await message.answer("🚫 Попробуйте еще раз выбрать пункт из меню")
        else: await message.answer("🚫 Try again to select an item from the menu")



################# START ACTION #############
@router.message(Order.action)
async def process_action_order(message: types.Message, state: FSMContext):
    """ Нажатие кнопки - Действия  заказа """
    await typing(message)
    state_data = await state.get_data()
    order_id = state_data.get("id")
    lang = message.from_user.language_code

    if message.text == UI_TEXTS[lang]["get_photo"]:
        action = "photo"
    elif message.text == UI_TEXTS[lang]["get_pdf"]:
        action = "pdf"
    elif message.text == UI_TEXTS[lang]["payd"]:
        action = "payd"
    elif message.text == UI_TEXTS[lang]["delet"]:
        action = "delet"
    else:
        if lang == "ru": await message.answer("🚫 Попробуйте еще раз выбрать пункт из меню")
        else: await message.answer("🚫 Try again to select an item from the menu")
        return
    
    await actions_order_tap(order_id, action, message, state)

    
# buttons = [UI_TEXTS[lang]["get_photo"], UI_TEXTS[lang]["get_pdf"], UI_TEXTS[lang]["payd"], UI_TEXTS[lang]["cancel"]]
# buttons = [UI_TEXTS[lang]["order"], UI_TEXTS[lang]["client"], UI_TEXTS[lang]["cancel"]]