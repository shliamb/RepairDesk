#! handlers/active_orders.py
from handlers.common import typing, is_manager
from logs.set_logger import set_logger
logger = set_logger(name="handlers")
from utils.formatters import remove_emojis, format_phone, format_date_nice
from aiogram import Router, types, F
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import ReplyKeyboardRemove, InlineKeyboardMarkup, InlineKeyboardButton
# from aiogram.utils.keyboard import ReplyKeyboardBuilder, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext
from database.orders import OrderService
from config import get_brands, ACTIVE_STATUSES, CANCEL, ORDER, IN_PROGRESS_STATUSES, READY_STATUSES, \
    CURRENCY, VIEW_ORDER, CHANGE_ORDER, ACTION_ORDER, ORDER_STATUS_RU
from keyboards.workshop import build_keyboard
from database import db
# from decimal import Decimal
# import asyncio
import json


router = Router()
order = OrderService(db)

class Order(StatesGroup):
    edit = State()
    action = State()


# from datetime import datetime

# def format_date_localized(dt: datetime, lang: str) -> str:
#     """
#     Форматирует дату на русском или английском языке
    
#     Args:
#         dt: datetime объект
#         lang: язык ('ru' или 'en')
    
#     Returns:
#         Строка с отформатированной датой
#     """
#     if lang == "ru":
#         months = {
#             1: "января", 2: "февраля", 3: "марта", 4: "апреля",
#             5: "мая", 6: "июня", 7: "июля", 8: "августа",
#             9: "сентября", 10: "октября", 11: "ноября", 12: "декабря"
#         }
#         month_name = months[dt.month]
#         return f"{dt.day} {month_name} {dt.year}" #, {dt.strftime('%H:%M')}"
    
#     elif lang == "en":
#         # Английские названия месяцев
#         months = {
#             1: "January", 2: "February", 3: "March", 4: "April",
#             5: "May", 6: "June", 7: "July", 8: "August",
#             9: "September", 10: "October", 11: "November", 12: "December"
#         }
#         month_name = months[dt.month]
        
#         # Определяем суффикс для дня (st, nd, rd, th)
#         day = dt.day
#         if 4 <= day <= 20 or 24 <= day <= 30:
#             suffix = "th"
#         else:
#             suffix = {1: "st", 2: "nd", 3: "rd"}.get(day % 10, "th")
        
#         return f"{day}{suffix} {month_name} {dt.year}" #, {dt.strftime('%H:%M')}"
    
#     else:
#         # Fallback на английский
#         return dt.strftime("%d %B %Y, %H:%M")



# OUTPUTTING ORDERS TO THE TELEGRAMM BOT
async def push_orders_bot(message: types.Message, lang: str, records: list):
    """ Вывод заказов в телеграмм боте.
    
        Для работы с заказами использую 
        id (id SERIAL PRIMARY KEY) - это 
        быстре и проще для внутренней работы, 
        для клиента - order_number """
    
    if not records:
        if lang == "ru": await message.answer("Заказов нет")
        else: await message.answer("There are no orders")
        return


    for one in records:

        id = one.get("id")
        order_number = one.get("order_number")
        order_type = one.get("order_type")
        device_type = one.get("device_type")
        device_brand = one.get("device_brand")
        device_model = one.get("device_model")
        real_name_client = one.get("real_name_client")
        real_name_created = one.get("real_name_created")
        problem = json.loads(one.get("problem")) if one.get("problem") else ""
        problem = ", ".join(problem.copy())
        status = one.get("status")
        created_date = one.get("created_date")
        created_date = format_date_nice(created_date, lang) #created_date.strftime("%d.%m.%y %H:%M")
        diagnosis_before = one.get("diagnosis_before")
        diagnosis_before = format_date_nice(diagnosis_before, lang) #diagnosis_before.strftime("%d.%m.%y %H:%M")
        cost_diagnostics = int(one.get("cost_diagnostics"))


        order_ru = (
            f'<b>📋 Заказ: {order_number}</b> {"🤑" if order_type == "paid" else "🤬"}\n\n'
            f'<b>📊 Статус заказа:</b> {status}\n'
            f'<b>🙋 {real_name_client}</b>\n'
            f'<b>{device_type}:</b> {device_brand} {device_model}\n'
            f'<b>👨‍💻 Принял:</b> {real_name_created} {created_date}\n'
            f'<b>⏰ Диагностика до:</b> {diagnosis_before}\n'
            f'<b>💰 Стоимость диагностики:</b> {cost_diagnostics} {CURRENCY}\n\n'
            f'<b>⚠️ Неисправность:</b> {problem}\n'
        )

        order_en = (
            f'<b>📋 Order: {order_number}</b> {"🤑" if order_type == "paid" else "🤬"}\n\n'
            f'<b>🎯 Order status:</b> {status}\n'
            f'<b>👨‍💼 {real_name_client}</b>\n'
            f'<b>{device_type}:</b> {device_brand} {device_model}\n'
            f'<b>📥 Has accepted:</b> {real_name_created} {created_date}\n'
            f'<b>⏱️ Diagnosis before:</b> {diagnosis_before}\n'
            f'<b>💵 The cost of diagnosis:</b> {cost_diagnostics} {CURRENCY}\n\n'
            f'<b>⚠️ Malfunction:</b> {problem}\n'
        )
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text=f'{VIEW_ORDER["change_ru"] if lang == "ru" else VIEW_ORDER["change_en"]}', callback_data=f"edit_order_{id}"),
                InlineKeyboardButton(text=f'{VIEW_ORDER["action_ru"] if lang == "ru" else VIEW_ORDER["action_en"]}', callback_data=f"action_order_{id}")
            ]
        ])
        
        if lang == "ru": await message.answer(order_ru, parse_mode="HTML", reply_markup=keyboard)
        else: await message.answer(order_en, parse_mode="HTML", reply_markup=keyboard)
        #await asyncio.sleep(0.1)


# EDIT ORDER
@router.callback_query(F.data.startswith("edit_order_"))
async def edit_order(callback: types.CallbackQuery, state: FSMContext):
    """ Выбор объекта изменения под каждым заказом """
    lang = callback.from_user.language_code
    id = callback.data.split("_")[-1]  # вытащить ID
    if not isinstance(id, int): id = int(id)
    else: logger.error(f"{id} is not digit")
    #await callback.message.answer(f"Редактируем заказ {id}")
    # await callback.message.answer(f"process_edit_order_{id}", parse_mode=None)
    if lang == "ru": buttons = [CHANGE_ORDER["order_ru"], CHANGE_ORDER["client_ru"], CHANGE_ORDER["status_ru"], CANCEL["ru"]]
    else: buttons = [CHANGE_ORDER["order_en"], CHANGE_ORDER["client_en"], CHANGE_ORDER["status_en"], CANCEL["en"]]
    if lang == "ru": intro_text = f"Выберите действие по заказу:"
    else: intro_text = f"Select the order action:"
    await callback.message.answer(intro_text, reply_markup = build_keyboard(buttons))
    await state.update_data(id=id)
    await state.set_state(Order.edit)
    await callback.answer()


# ACTION ORDER
@router.callback_query(F.data.startswith("action_order_"))
async def action_order(callback: types.CallbackQuery, state: FSMContext):
    """ Выбор действий под каждым заказом """
    lang = callback.from_user.language_code
    id = callback.data.split("_")[-1]
    if not isinstance(id, int): id = int(id)
    else: logger.error(f"{id} is not digit")
    if lang == "ru": buttons = [ACTION_ORDER["get_photo_ru"], ACTION_ORDER["get_pdf_ru"], ACTION_ORDER["issue_ru"], CANCEL["ru"]]
    else: buttons = [ACTION_ORDER["get_photo_en"], ACTION_ORDER["get_pdf_en"], ACTION_ORDER["issue_en"], CANCEL["en"]]
    if lang == "ru": intro_text = f"Выберите ействие по заказу {id}:"
    else: intro_text = f"Select the product by order {id}:"
    await callback.message.answer(intro_text, reply_markup = build_keyboard(buttons))
    await state.update_data(id=id)
    await state.set_state(Order.action)
    await callback.answer()


# START GET ACTIVE ORDERS
@router.message((F.text == ORDER["activ_ru"]) | (F.text == ORDER["activ_en"]))
async def get_active_orders(message: types.Message):#, state: FSMContext):
    """ Показать активные заказы """
    await typing(message)
    lang = message.from_user.language_code
    user_id = message.from_user.id
    if not await is_manager(user_id):
        logger.error(f"{user_id} You don't have access")
        await message.answer("🔐 You don't have access")
        return
    
    # Собрать Активные Заказы из базы
    records = await order.get_orders_by_statuses(ACTIVE_STATUSES)
    await push_orders_bot(message, lang, records)


# START GET IN PROGRESS ORDERS
@router.message((F.text == ORDER["in_work_ru"]) | (F.text == ORDER["in_work_en"]))
async def get_inprogress_orders(message: types.Message):#, state: FSMContext):
    """ Показать заказы в работе"""
    await typing(message)
    lang = message.from_user.language_code
    user_id = message.from_user.id
    if not await is_manager(user_id):
        logger.error(f"{user_id} You don't have access")
        await message.answer("🔐 You don't have access")
        return
    
    # Собрать в процессе Заказы из базы
    records = await order.get_orders_by_statuses(IN_PROGRESS_STATUSES)
    await push_orders_bot(message, lang, records)


# START GET READY ORDERS
@router.message((F.text == ORDER["ready_ru"]) | (F.text == ORDER["ready_en"]))
async def get_ready_orders(message: types.Message):#, state: FSMContext):
    """ Показать готовые заказы """
    await typing(message)
    lang = message.from_user.language_code
    user_id = message.from_user.id
    if not await is_manager(user_id):
        logger.error(f"{user_id} You don't have access")
        await message.answer("🔐 You don't have access")
        return

    # Собрать Готовые Заказы из базы
    records = await order.get_orders_by_statuses(READY_STATUSES)
    await push_orders_bot(message, lang, records)


# START GET STATISTICS ORDERS
@router.message((F.text == ORDER["stat_ru"]) | (F.text == ORDER["stat_en"]))
async def get_statistic(message: types.Message):#, state: FSMContext):
    """ Показать статистику """
    await typing(message)
    lang = message.from_user.language_code
    user_id = message.from_user.id
    if not await is_manager(user_id):
        logger.error(f"{user_id} You don't have access")
        await message.answer("🔐 You don't have access")
        return
    
    stats = await db.get_pool_stats()
    print(f"Статистика: {json.dumps(stats, indent=2)}")
    await message.answer(f"Статистика: total: {stats}", parse_mode=None)
    # await message.answer(f"Статистика: total: {stats.get("total")}, used: {stats.get("used")}, idle: {stats.get("idle")}, percent_used: {stats.get("percent_used")}")
