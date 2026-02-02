#! app/handlers/actions_order.py
from handlers.common import typing, is_manager
from logs.set_logger import set_logger
logger = set_logger(name="handlers")
from utils.formatters import remove_emojis, extract_emoji, format_phone, format_date_nice, format_telegram_username, safe_int, safe_decimal
from database.users import get_user_by_user_id, get_user_by_tg
from utils.serialize import json_serializer, custom_json_decoder
from handlers.edit_client import start_edit_client
from aiogram import Router, types, F
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from database.orders import OrderService
from config import HUMAN_QUALITY, CHANGE_ORDER, CURRENCY, DEVICE_ICO, ORDER_STATUS_COLOR, ORDER_STATUS_RU, ORDER_STATUS, EDIT_ORDER, CANCEL
from keyboards.workshop import build_keyboard
from database import db
from handlers.viewing_orders import Order # State из viewing_orders.py для перехода
import json
from datetime import datetime
from decimal import Decimal



router = Router()
order = OrderService(db)



class Action(StatesGroup):
    pay_method = State()






@router.message(Action.pay_method)
async def choosing_payment_method(message: types.Message, state: FSMContext):
    """ Выбор способа оплаты """
    print(message.text)



async def actions_order_tap(order_id: int, action: str, message: types.Message, state: FSMContext):
    """ Выбор вариантов при нажатии - действия на заказе """
    await typing(message)
    lang = message.from_user.language_code
    user_id = message.from_user.id

    if not await is_manager(user_id):
        logger.error(f"{user_id} You don't have access")
        await message.answer("🔐 You don't have access")
        return
    
    if action == "photo":
        await message.answer("🚫 photo")
        return

    elif action == "pdf":
        await message.answer("🚫 pdf")
        return

    elif action == "payd":
        if lang == "ru": message_text = "📝 Введите свой вариант срока диагностики:"
        else: message_text = "📝 Enter your option for the diagnosis period:"
        buttons = ["карта", "наличность", "крипта", "анал", "Отмена"]
        await message.answer(message_text, reply_markup = build_keyboard(buttons))
        await state.set_state(Action.pay_method)
        return
