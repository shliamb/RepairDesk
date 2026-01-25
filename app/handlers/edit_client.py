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
from config import DONE, CHANGE_ORDER, CURRENCY, DEVICE_ICO, ORDER_STATUS_COLOR, ORDER_STATUS_RU, ORDER_STATUS, EDIT_ORDER, CANCEL
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


    if lang == "ru":
        buttons = [
            "📋 Контактные данные", # (имя, телефон, Telegram)",
            "👥 Роль", # (админ / мастер / менеджер)",
            "⭐ Рейтинг и статус", # (оценки, чаевые, блокировка)"
            "Отмена"
        ]
        text = "Что изменим для пользователя?"
    else:
        buttons = [
            "📋 Contact info", # (name, phone, Telegram)",
            "👥 User role", # (admin / technician / manager)",
            "⭐ Rating & status", # (reviews, tips, block user)"
            "Cansel"
        ]

        text = "What would you like to edit for this user?"

    await message.answer(text, reply_markup = build_keyboard(buttons))