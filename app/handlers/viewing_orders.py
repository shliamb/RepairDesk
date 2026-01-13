#! handlers/active_orders.py
from handlers.common import typing, is_manager
from logs.set_logger import set_logger
logger = set_logger(name="handlers")
from aiogram import Router, types, F
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import ReplyKeyboardRemove, InlineKeyboardMarkup, InlineKeyboardButton
# from aiogram.utils.keyboard import ReplyKeyboardBuilder, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext
from database.orders import OrderService
from config import get_brands, ACTIVE_STATUSES, CANCEL, ORDER, IN_PROGRESS_STATUSES, READY_STATUSES
from keyboards.workshop import build_keyboard
from database import db
from decimal import Decimal
import asyncio
import json





router = Router()
order = OrderService(db)






class newOrder(StatesGroup):
    active = State()







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
        diagnosis_before = one.get("diagnosis_before")
        cost_diagnostics = one.get("cost_diagnostics")

        order_ru = (
            f'<b>📋 Заказ: {order_number}</b> {"🤑" if order_type == "paid" else "🤬"}\n\n'
            f'<b>📊 Статус заказа:</b> {status}\n'
            f'<b>🙋 {real_name_client}</b>\n'
            f'<b>{device_type}:</b> {device_brand} {device_model}\n'
            f'<b>👨‍💻 Принял:</b> {real_name_created} {created_date}\n'
            f'<b>⏰ Диагностика до:</b> {diagnosis_before}\n'
            f'<b>💰 Стоимость диагностики:</b> {cost_diagnostics}\n\n'
            f'<b>⚠️ Неисправность:</b> {problem}\n'
        )

        order_en = (
            f'<b>📋 Order: {order_number}</b> {"🤑" if order_type == "paid" else "🤬"}\n\n'
            f'<b>📊 Order status:</b> {status}\n'
            f'<b>🙋 {real_name_client}</b>\n'
            f'<b>{device_type}:</b> {device_brand} {device_model}\n'
            f'<b>👨‍💻 Has accepted:</b> {real_name_created} {created_date}\n'
            f'<b>⏰ Diagnosis before:</b> {diagnosis_before}\n'
            f'<b>💰 The cost of diagnosis:</b> {cost_diagnostics}\n\n'
            f'<b>⚠️ Malfunction:</b> {problem}\n'
        )
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text=f"{'📝 Изменить' if lang == 'ru' else '📝 Сhange'}", callback_data=f"edit_order_{id}"),
                InlineKeyboardButton(text=f"{'📸 Фото' if lang == 'ru' else '📸 Photo'}", callback_data=f"view_photos_{id}"),
            ],
            [
                InlineKeyboardButton(text=f"{'📄 PDF' if lang == 'ru' else '📄 PDF'}", callback_data=f"get_pdf_{id}"),
                InlineKeyboardButton(text=f"{'📤 Выдать' if lang == 'ru' else '📤 Issue'}", callback_data=f"issue_order_{id}"),
            ]
        ])
        
        if lang == "ru": await message.answer(order_ru, parse_mode="HTML", reply_markup=keyboard)
        else: await message.answer(order_en, parse_mode="HTML", reply_markup=keyboard)
        #await asyncio.sleep(0.1)


# EDIT ORDER
@router.callback_query(F.data.startswith("edit_order_"))
async def edit_order(callback: types.CallbackQuery):
    """ Редактировать заказ """
    id = callback.data.split("_")[-1]  # вытащить ID
    await callback.message.answer(f"Редактируем заказ {id}")
    await callback.answer()


# GET PHOTO ORDER
@router.callback_query(F.data.startswith("view_photos_"))
async def view_photos(callback: types.CallbackQuery):
    """ Фотографии уустройства при приёме заказа """
    id = callback.data.split("_")[-1]
    await callback.message.answer(f"Фотографии принятого устройства заказа {id}")
    await callback.answer()


# GET PDF ORDER
@router.callback_query(F.data.startswith("get_pdf_"))
async def get_pdf(callback: types.CallbackQuery):
    """ PDF заказа """
    id = callback.data.split("_")[-1]
    await callback.message.answer(f"PDF заказа {id}")
    await callback.answer()


# ISSUE ORDER
@router.callback_query(F.data.startswith("issue_order_"))
async def issue_order(callback: types.CallbackQuery):
    """ Выдать заказ """
    id = callback.data.split("_")[-1]
    await callback.message.answer(f"Выдаю заказ {id}")
    await callback.answer()


# CANCEL STATE & KEYBOARD
@router.message((F.text == CANCEL["ru"]) | (F.text == CANCEL["en"]))
async def cancel(message: types.Message, state: FSMContext): 
    """ Отмена / Cancelled """
    await typing(message)
    lang = message.from_user.language_code
    await state.clear()
    if lang == "ru": await message.answer("🚫 Отменено", reply_markup=ReplyKeyboardRemove())
    else: await message.answer("🚫 Cancelled", reply_markup=ReplyKeyboardRemove())


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
    
    await message.answer("Статистика")
