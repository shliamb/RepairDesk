#! app/handlers/edit_client.py
from handlers.common import typing, is_manager
from logs.set_logger import set_logger
logger = set_logger(name="handlers")
from utils.formatters import remove_emojis, format_phone, format_date_nice, format_telegram_username, safe_int, safe_decimal, safe_float
from database.users import get_user_by_user_id, get_user_by_tg
from utils.serialize import json_serializer, custom_json_decoder
from aiogram import Router, types, F
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import ReplyKeyboardRemove, InlineKeyboardMarkup, InlineKeyboardButton
# from aiogram.utils.keyboard import ReplyKeyboardBuilder, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext
from database.orders import OrderService
from config import DONE, CHANGE_ORDER, CURRENCY, DEVICE_ICO, ORDER_STATUS_COLOR, ORDER_STATUS_RU, ORDER_STATUS, EDIT_ORDER, CANCEL, CLIENT
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







@router.message(EditClient.client)
async def process_choice_client(message: types.Message, state: FSMContext):
    """ Перераспределение по выбору в меню управления клиентом """
    await typing(message)
    lang = message.from_user.language_code
    user_id = message.from_user.id

    # EDIT MAIN DATA of CLIENT:
    if message.text in (CLIENT["contact_ru"], CLIENT["contact"]):
        # Отдельный вызов редактирования заказа
        #await start_edit_order(order_id, state, message)
        await message.answer(f"Меняем данные клиента")
        return
    
    # CHANG ROLE CLIENT:
    elif message.text in (CLIENT["role_ru"], CLIENT["role"]):
        await message.answer(f"Меняем role")
        return
    
    # CHANG STATUS CLIENT:
    elif message.text in (CLIENT["status_ru"], CLIENT["status"]):
        await message.answer(f"Меняем status")
        return
    
    # ACCEPT DEVICE at CLIENT:
    elif message.text in (CLIENT["accdevice_ru"], CLIENT["accdevice"]):
        await message.answer(f"accept device")
        return
    
    # QUICK SERVICE:
    elif message.text in (CLIENT["qserv_ru"], CLIENT["qserv"]): 
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


    if lang == "ru":
        buttons = [
            CLIENT["qserv_ru"],
            CLIENT["accdevice_ru"],
            CLIENT["contact_ru"], # (имя, телефон, Telegram)",
            CLIENT["role_ru"], # (админ / мастер / менеджер)",
            CLIENT["status_ru"], # (оценки, чаевые, блокировка)"
            CANCEL["ru"]
        ]

        customer_card = f"🙋 <b>{name}</b>\n"
        if username_telegram: customer_card += f"        {username_telegram}\n"
        if phone: customer_card += f"        {phone}\n"

        customer_card += "\n📊 <b>СТАТИСТИКА:</b>\n"
        if total_spent: customer_card += f"        Всего потрачено: {total_spent}\n"
        if repair_count_total: customer_card += f"        Всего ремонтов: {repair_count_total}\n"
        if a_tip: customer_card += f"        Чаевые: {a_tip}\n"

        customer_card += "\n👥 <b>РОЛИ:</b>\n"
        if is_admin: customer_card += f"        Админ\n"
        if client_is_manager: customer_card += f"        Менеджер\n"
        if is_master: customer_card += f"        Мастер\n"
        if not is_admin and not client_is_manager and not is_master: customer_card += f"        Клиент\n"

        customer_card += "\n📝 <b>МЕТКИ:</b>\n"
        if description_user: customer_card += f"        Описание: {description_user}\n"
        if hum_quality: customer_card += f"        Качество: {hum_quality}\n"
        if block: customer_card += f"        Заблокирован\n"

        customer_card += "\n📅 <b>ДАТЫ:</b>\n"
        if time_reg: customer_card += f"        Регистрация: {format_date_nice(time_reg, lang)}\n"
        if last_visit: customer_card += f"        Последний визит: {format_date_nice(last_visit, lang)}\n"

        customer_card += "\n🔧 <b>ЗАКАЗЫ:</b>\n"
        for one_order in orders_client:
            order_number = one_order.get("order_number")
            net_profit = one_order.get("net_profit")
            created_date = one_order.get("created_date")
            customer_card += f"        {order_number}"
            if net_profit: customer_card += f" • {net_profit}{CURRENCY}"
            customer_card += f" • {format_date_nice(created_date, lang)}\n"


    else:
        buttons = [
            CLIENT["qserv"],
            CLIENT["accdevice"],
            CLIENT["contact"], # (name, phone, Telegram)",
            CLIENT["role"], # (admin / technician / manager)",
            CLIENT["status"], # (reviews, tips, block user)"
            CANCEL["en"]
        ]

        customer_card = f"🙋 <b>{name}</b>\n"
        if username_telegram: customer_card += f"        {username_telegram}\n"
        if phone: customer_card += f"        {phone}\n"

        customer_card += "\n📊 <b>STATISTICS:</b>\n"
        if total_spent: customer_card += f"        Total spent: {total_spent}\n"
        if repair_count_total: customer_card += f"        Total repairs: {repair_count_total}\n"
        if a_tip: customer_card += f"        Tips: {a_tip}\n"

        customer_card += "\n👥 <b>ROLES:</b>\n"
        if is_admin: customer_card += f"        Admin\n"
        if client_is_manager: customer_card += f"        Manager\n"
        if is_master: customer_card += f"        Master\n"
        if not is_admin and not client_is_manager and not is_master: customer_card += f"        Customer\n"

        customer_card += "\n📝 <b>TAGS:</b>\n"
        if description_user: customer_card += f"        Description: {description_user}\n"
        if hum_quality: customer_card += f"        Quality: {hum_quality}\n"
        if block: customer_card += f"        Blocked\n"

        customer_card += "\n📅 <b>DATES:</b>\n"
        if time_reg: customer_card += f"        Registration: {format_date_nice(time_reg, lang)}\n"
        if last_visit: customer_card += f"        Last visit: {format_date_nice(last_visit, lang)}\n"

        customer_card += "\n🔧 <b>ORDERS:</b>\n"
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