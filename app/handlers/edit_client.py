#! app/handlers/edit_client.py
from handlers.common import typing, is_manager
from logs.set_logger import set_logger
logger = set_logger(name="handlers")
from utils.formatters import remove_emojis, format_phone, format_date_nice, format_telegram_username, safe_int, safe_decimal, safe_float
from database.users import get_user_by_user_id, edit_client, get_user_by_tg
from utils.serialize import json_serializer, custom_json_decoder
from aiogram import Router, types, F
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import ReplyKeyboardRemove, InlineKeyboardMarkup, InlineKeyboardButton
# from aiogram.utils.keyboard import ReplyKeyboardBuilder, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext
from database.orders import OrderService
from config import UI_TEXTS, CURRENCY
from keyboards.workshop import build_keyboard
from database import db
# from handlers.viewing_orders import Order # State из viewing_orders.py для перехода
# import asyncio
import uuid
import json
from datetime import datetime
from decimal import Decimal, InvalidOperation



router = Router()
order = OrderService(db)




class EditClient(StatesGroup):
    client = State()
    data_client = State()
    role_client = State()






# SAVE DATA TO DB Сохранение в базу изменений и вывод карты клиента снова
async def edit_client_db(data: dict, state: FSMContext, message: types.Message):
    """ Изменяю в базе и вызываю снова на экран карту клиента"""
    client_id = data.get("user_id")
    lang = message.from_user.language_code
    result = await edit_client(data)
    if not result:
        logger.error("Error in saving in the database")
        if lang == "ru": await message.answer("🚫 Ошибка в сохранении в базе")
        else: await message.answer("🚫 Error in saving in the database")
        return

    if lang == "ru": await message.answer("👍 Изменения сохранены", reply_markup=ReplyKeyboardRemove())
    else: await message.answer("👍 The changes are saved", reply_markup=ReplyKeyboardRemove())
    # Вывести заказ снова, что бы видно было что изменилось..
    await start_edit_client(client_id, state, message)










    




# ADD SERVICE/WORK
@router.message(EditClient.data_client)
async def data_client(message: types.Message, state: FSMContext):
    """ Изменение данных клиента/пользователя в базе """
    await typing(message)
    lang = message.from_user.language_code
    input_text = message.text

    # STATE:
    state_data = await state.get_data()
    client_id = state_data.get("client_id")
    client_name = state_data.get("name")

    name, phone, username_telegram = state_data.get("name"), state_data.get("phone"), state_data.get("username_telegram")

    if not name:
        if input_text in UI_TEXTS[lang]["miss"]:
            data_of_client_from_db = await get_user_by_user_id(client_id)
            name = data_of_client_from_db.get("name")
        else:
            name = input_text
        await state.update_data(name=name)
        if lang == "ru": await message.answer("📞 Введите номер телефона:", reply_markup = build_keyboard([UI_TEXTS[lang]["miss"]]))
        else: await message.answer("📞 Enter phone number:", reply_markup = build_keyboard([UI_TEXTS[lang]["miss"]]))
        return

    elif name and not phone:
        if input_text in UI_TEXTS[lang]["miss"]:
            data_of_client_from_db = await get_user_by_user_id(client_id)
            phone = data_of_client_from_db.get("phone")
        else:
            phone = input_text
        phone = format_phone(phone)

        if not phone:
            if lang == "ru": await message.answer("📞 Введите номер телефона:", reply_markup = build_keyboard([UI_TEXTS[lang]["miss"]]))
            else: await message.answer("📞 Enter phone number:", reply_markup = build_keyboard([UI_TEXTS[lang]["miss"]]))
            return
        await state.update_data(phone=phone)
        if lang == "ru": await message.answer("@️ Введите телеграмм имя (@name):", reply_markup = build_keyboard([UI_TEXTS[lang]["miss"]]))
        else: await message.answer("@️ Enter telegram name (@name):", reply_markup = build_keyboard([UI_TEXTS[lang]["miss"]]))
        return

    elif name and phone and not username_telegram:
        if input_text in UI_TEXTS[lang]["miss"]:
            data_of_client_from_db = await get_user_by_user_id(client_id)
            username_telegram = data_of_client_from_db.get("username_telegram")
        else:
            username_telegram = input_text
        username_telegram = format_telegram_username(username_telegram)
        if username_telegram is None:
            if lang == "ru": await message.answer("@️ Введите телеграмм имя (@name):", reply_markup = build_keyboard([UI_TEXTS[lang]["miss"]]))
            else: await message.answer("@️ Enter telegram name (@name):", reply_markup = build_keyboard([UI_TEXTS[lang]["miss"]]))
            return

        client_data = {
            "user_id": client_id,
            "name": client_name,
            "phone": state_data.get("phone"),
            "username_telegram": username_telegram
        }

        await edit_client_db(client_data, state, message)
        # Нахожу все заказы клиента, в каждом меняю имя клиента
        orders_by_client = await order.get_orders_by_user(client_id)
        for one_order in orders_by_client:
            id_order = one_order.get("id")
            new_data_order = {"id": id_order, "real_name_client": client_name}
            await order.edit_order(new_data_order)

        await state.update_data(name=None, phone=None, username_telegram=None)





# EDIT ROLE CLIENT
@router.message(EditClient.role_client)
async def role_client(message: types.Message, state: FSMContext):
    """ Изменение роли клиента/пользователя в системе """
    await typing(message)
    lang = message.from_user.language_code
    input_text = message.text

    # STATE:
    state_data = await state.get_data()
    client_id = state_data.get("client_id")
    #client_name = state_data.get("name")

    is_admin, is_manager, is_master = state_data.get("is_admin"), state_data.get("is_manager"), state_data.get("is_master")

    if is_admin is None:
        if input_text in UI_TEXTS[lang]["miss"]:
            data_of_client_from_db = await get_user_by_user_id(client_id)
            is_admin = data_of_client_from_db.get("is_admin")

        elif input_text in UI_TEXTS[lang]["yes"]:
            is_admin = True

        elif input_text in UI_TEXTS[lang]["no"]:
            is_admin = False
        
        await state.update_data(is_admin=is_admin)
        if lang == "ru": text = "👔 Сделать пользователя менеджером:"
        else: text = "👔 Make a user a manager:"
        await message.answer(text, reply_markup = build_keyboard([UI_TEXTS[lang]["yes"], UI_TEXTS[lang]["no"], UI_TEXTS[lang]["miss"], UI_TEXTS[lang]["cancel"]]))
        return
    
    elif is_admin is not None and is_manager is None:
        if input_text in UI_TEXTS[lang]["miss"]:
            data_of_client_from_db = await get_user_by_user_id(client_id)
            is_manager = data_of_client_from_db.get("is_manager")

        elif input_text in UI_TEXTS[lang]["yes"]:
            is_manager = True

        elif input_text in UI_TEXTS[lang]["no"]:
            is_manager = False
        
        await state.update_data(is_manager=is_manager)
        if lang == "ru": text = "👨‍🔧 Сделать пользователя мастером:"
        else: text = "👨‍🔧 Make a user a master:"
        await message.answer(text, reply_markup = build_keyboard([UI_TEXTS[lang]["yes"], UI_TEXTS[lang]["no"], UI_TEXTS[lang]["miss"], UI_TEXTS[lang]["cancel"]]))
        return
    
    elif is_admin is not None and is_manager is not None and is_master is None:
        if input_text in UI_TEXTS[lang]["miss"]:
            data_of_client_from_db = await get_user_by_user_id(client_id)
            is_master = data_of_client_from_db.get("is_master")

        elif input_text in UI_TEXTS[lang]["yes"]:
            is_master = True

        elif input_text in UI_TEXTS[lang]["no"]:
            is_master = False
        
        client_data = {
            "user_id": client_id,
            "is_admin": is_admin,
            "is_manager": is_manager,
            "is_master": is_master
        }

        await edit_client_db(client_data, state, message)
        await state.update_data(is_admin=None, is_manager=None, is_master=None)



# ROUTING EDIT DATA CLIENT
@router.message(EditClient.client)
async def process_choice_client(message: types.Message, state: FSMContext):
    """ Перераспределение по выбору в меню управления клиентом """
    await typing(message)
    lang = message.from_user.language_code
    # user_id = message.from_user.id

    # EDIT MAIN DATA of CLIENT:
    if message.text in UI_TEXTS[lang]["contact"]:
        if lang == "ru": text = "🏷️ Введите новое имя:"
        else: text = "🏷️ Enter a new name:"
        await message.answer(text, reply_markup = build_keyboard([UI_TEXTS[lang]["miss"]]))
        await state.set_state(EditClient.data_client)
        return
    
    # CHANG ROLE CLIENT:
    elif message.text in UI_TEXTS[lang]["role"]:
        if lang == "ru": text = "👑 Сделать пользователя админом:"
        else: text = "👑 Make a user an admin:"
        await message.answer(text, reply_markup = build_keyboard([UI_TEXTS[lang]["yes"], UI_TEXTS[lang]["no"], UI_TEXTS[lang]["miss"], UI_TEXTS[lang]["cancel"]]))
        await state.set_state(EditClient.role_client)
        return
    

    
    # CHANG STATUS CLIENT:
    elif message.text in UI_TEXTS[lang]["status"]:
        await message.answer(f"Меняем status")
        return
    
    # ACCEPT DEVICE at CLIENT:
    elif message.text in UI_TEXTS[lang]["accdevice"]:
        await message.answer(f"accept device")
        return
    
    # QUICK SERVICE:
    elif message.text in UI_TEXTS[lang]["qserv"]: 
        await message.answer(f"Quick service")
        return

    else:
        if lang == "ru": await message.answer("🚫 Попробуйте еще раз выбрать пункт из меню")
        else: await message.answer("🚫 Try again to select an item from the menu")



# START EDIT DATA USER AT HER UUID
async def start_edit_client(client_id: uuid, state: FSMContext, message: types.Message):
    """ Меняем данные клиента """
    await typing(message)
    lang = message.from_user.language_code
    user_id = message.from_user.id

    if not await is_manager(user_id):
        logger.error(f"{user_id} You don't have access")
        await message.answer("🔐 You don't have access")
        return
    
    #await state.clear()
    user_data = await get_user_by_user_id(client_id)
    # print(user_id)
    name = user_data.get("name") or user_data.get("real_name")
    username_telegram = user_data.get("username_telegram")
    phone = user_data.get("phone")
    a_tip = user_data.get("a_tip")
    total_spent = user_data.get("total_spent")
    repair_count_total = user_data.get("repair_count_total")
    description_user = user_data.get("description_user")
    block = user_data.get("block")
    hum_quality = user_data.get("hum_quality")
    last_visit = user_data.get("last_visit")
    time_reg = user_data.get("time_reg")

    is_admin = user_data.get("is_admin")
    client_is_manager = user_data.get("is_manager")
    is_master = user_data.get("is_master")

    orders_client = await order.get_orders_by_user(client_id)

    buttons = [
        UI_TEXTS[lang]["qserv"],
        UI_TEXTS[lang]["accdevice"],
        UI_TEXTS[lang]["contact"],  # (name, phone, Telegram)"
        UI_TEXTS[lang]["role"],  # (admin / technician / manager)"
        UI_TEXTS[lang]["status"],  # (reviews, tips, block user)"
        UI_TEXTS[lang]["cancel"]
    ]
    
    if lang == "ru":
        customer_card = f"🙋 <b>{name}</b>\n"
        if username_telegram: customer_card += f"        {username_telegram}\n"
        if phone: customer_card += f"        {phone}\n"

        if total_spent or repair_count_total or a_tip: customer_card += "\n📊 <b>СТАТИСТИКА:</b>\n"
        if total_spent: customer_card += f"        Всего потрачено: {total_spent}\n"
        if repair_count_total: customer_card += f"        Всего ремонтов: {repair_count_total}\n"
        if a_tip: customer_card += f"        Чаевые: {a_tip}\n"

        customer_card += "\n👥 <b>РОЛИ:</b>\n"
        if is_admin: customer_card += f"        Админ\n"
        if client_is_manager: customer_card += f"        Менеджер\n"
        if is_master: customer_card += f"        Мастер\n"
        if not is_admin and not client_is_manager and not is_master: customer_card += f"        Клиент\n"

        if block or description_user or hum_quality: customer_card += "\n📝 <b>МЕТКИ:</b>\n"
        if description_user: customer_card += f"        Описание: {description_user}\n"
        if hum_quality: customer_card += f"        Качество: {hum_quality}\n"
        if block: customer_card += f"        Заблокирован\n"

        customer_card += "\n📅 <b>ДАТЫ:</b>\n"
        if time_reg: customer_card += f"        Регистрация: {format_date_nice(time_reg, lang)}\n"
        if last_visit: customer_card += f"        Последний визит: {format_date_nice(last_visit, lang)}\n"

        if orders_client: customer_card += "\n🔧 <b>ЗАКАЗЫ:</b>\n"
        for one_order in orders_client:
            order_number = one_order.get("order_number")
            net_profit = one_order.get("net_profit")
            created_date = one_order.get("created_date")
            customer_card += f"        {order_number}"
            if net_profit: customer_card += f" • {net_profit}{CURRENCY}"
            customer_card += f" • {format_date_nice(created_date, lang)}\n"

    else:
        customer_card = f"🙋 <b>{name}</b>\n"
        if username_telegram: customer_card += f"        {username_telegram}\n"
        if phone: customer_card += f"        {phone}\n"

        if total_spent or repair_count_total or a_tip: customer_card += "\n📊 <b>STATISTICS:</b>\n"
        if total_spent: customer_card += f"        Total spent: {total_spent}\n"
        if repair_count_total: customer_card += f"        Total repairs: {repair_count_total}\n"
        if a_tip: customer_card += f"        Tips: {a_tip}\n"

        customer_card += "\n👥 <b>ROLES:</b>\n"
        if is_admin: customer_card += f"        Admin\n"
        if client_is_manager: customer_card += f"        Manager\n"
        if is_master: customer_card += f"        Master\n"
        if not is_admin and not client_is_manager and not is_master: customer_card += f"        Customer\n"

        if block or description_user or hum_quality: customer_card += "\n📝 <b>TAGS:</b>\n"
        if description_user: customer_card += f"        Description: {description_user}\n"
        if hum_quality: customer_card += f"        Quality: {hum_quality}\n"
        if block: customer_card += f"        Blocked\n"

        customer_card += "\n📅 <b>DATES:</b>\n"
        if time_reg: customer_card += f"        Registration: {format_date_nice(time_reg, lang)}\n"
        if last_visit: customer_card += f"        Last visit: {format_date_nice(last_visit, lang)}\n"

        if orders_client: customer_card += "\n🔧 <b>ORDERS:</b>\n"
        for one_order in orders_client:
            order_number = one_order.get("order_number")
            net_profit = one_order.get("net_profit")
            created_date = one_order.get("created_date")
            customer_card += f"        {order_number}"
            if net_profit: customer_card += f" • {net_profit}{CURRENCY}"
            customer_card += f" • {format_date_nice(created_date, lang)}\n"

    await message.answer(customer_card, reply_markup = build_keyboard(buttons), parse_mode="HTML")
    await state.update_data(client_id=client_id)
    await state.set_state(EditClient.client)