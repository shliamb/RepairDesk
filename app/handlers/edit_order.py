#! app/handlers/edit_order.py
from handlers.common import typing, is_manager
from logs.set_logger import set_logger
logger = set_logger(name="handlers")
from aiogram import Router, types, F
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import ReplyKeyboardRemove, InlineKeyboardMarkup, InlineKeyboardButton
# from aiogram.utils.keyboard import ReplyKeyboardBuilder, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext
from database.orders import OrderService
from config import get_brands, ACTIVE_STATUSES, CANCEL, ORDER, IN_PROGRESS_STATUSES, READY_STATUSES, CURRENCY
from keyboards.workshop import build_keyboard
from database import db
from handlers.viewing_orders import Order
# from decimal import Decimal
# import asyncio
import json





router = Router()
order = OrderService(db)















######### START EDIT ##############
@router.message(Order.edit)
async def process_edit_order(message: types.Message, state: FSMContext):
    """  """
    state_data = await state.get_data()
    order_id = state_data.get("id")
    lang = message.from_user.language_code

    if message.text == "📋 Заказ":
        await message.answer(f"Редактируем заказ {order_id}")
    elif message.text == "👤 Клиент":
        await message.answer(f"Меняем данные клиента под заказом {order_id}")
    elif message.text == "📊 Статус":
        await message.answer(f"Меняем статус заказа {order_id}")
    else:
        if lang == "ru": await message.answer("🚫 Попробуйте еще раз выбрать пункт из меню")
        else: await message.answer("🚫 Try again to select an item from the menu")

    #await state.clear()


################# START ACTION #############
@router.message(Order.action)
async def process_action_order(message: types.Message, state: FSMContext):
    """  """
    state_data = await state.get_data()
    order_id = state_data.get("id")
    lang = message.from_user.language_code

    if message.text == "📸 Фото":
        await message.answer(f"Фотав по заказу нэту {order_id}")
    elif message.text == "📄 PDF":
        await message.answer(f"Тута пдф по заказу {order_id}")
    elif message.text == "📤 Выдать заказ":
        await message.answer(f"Выдаем заказа - {order_id}")
    else:
        if lang == "ru": await message.answer("🚫 Попробуйте еще раз выбрать пункт из меню")
        else: await message.answer("🚫 Try again to select an item from the menu")

    #await state.clear()
    