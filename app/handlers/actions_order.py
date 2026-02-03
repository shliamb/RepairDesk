#! app/handlers/actions_order.py
from handlers.common import typing, is_manager
from logs.set_logger import set_logger
logger = set_logger(name="handlers")
from utils.formatters import remove_emojis, extract_emoji, format_phone, format_date_nice, format_telegram_username, safe_int, safe_decimal
from database.users import get_user_by_user_id, get_user_by_tg
from utils.serialize import json_serializer, custom_json_decoder
from utils.parse import is_number
from handlers.edit_client import start_edit_client
from aiogram import Router, types, F
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from database.orders import OrderService
from config import UI_TEXTS
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



# CANCEL STATE & KEYBOARD TO ALL HANDLERS !!!
@router.message((F.text == UI_TEXTS["en"]["cancel"]) | (F.text == UI_TEXTS["ru"]["cancel"]))
async def cancel(message: types.Message, state: FSMContext): 
    """ Отмена / Cancelled """
    await typing(message)
    lang = message.from_user.language_code
    await state.clear()
    if lang == "ru": await message.answer("🚫 Отменено", reply_markup=ReplyKeyboardRemove())
    else: await message.answer("🚫 Cancelled", reply_markup=ReplyKeyboardRemove())




@router.message(Action.pay_method)
async def choosing_payment_method(message: types.Message, state: FSMContext):
    """ Выбор способа оплаты и все остальное..  """
    await typing(message)
    lang = message.from_user.language_code
    #user_id = message.from_user.id
    input_text = message.text
    state_data = await state.get_data()

    metod_pay, amount = state_data.get("metod_pay") or None, state_data.get("amount") or None


    if metod_pay is None:
        if input_text in (UI_TEXTS[lang]["card"], UI_TEXTS[lang]["cash"], UI_TEXTS[lang]["crypto"], UI_TEXTS[lang]["no_payment"]):
            for key, value in UI_TEXTS[lang].items():
                if input_text == value:
                    await state.update_data(metod_pay=key)
                    if lang == "ru": message_text = "💰 Введите вносимую сумму:"
                    else: message_text = "💰 Enter payment amount:"
                    await message.answer(message_text, reply_markup = build_keyboard([UI_TEXTS[lang]["cancel"]]))
        else:
            if lang == "ru": await message.answer("🚫 Попробуйте еще раз выбрать пункт из меню")
            else: await message.answer("🚫 Try again to select an item from the menu")
            return
        
    elif metod_pay and amount is None:
        if not is_number(input_text):
            if lang == "ru": await message.answer("🚫 Введите вносимую сумму:")
            else: await message.answer("🚫 Enter payment amount:")
            return
        
        await state.update_data(amount=input_text)
        if lang == "ru": message_text = "Отлично"
        else: message_text = "Perfect"
        await message.answer(message_text, reply_markup = build_keyboard([UI_TEXTS[lang]["cancel"]]))


        state_data = await state.get_data()
        print(state_data)


        # Get status:

        await state.update_data(id=None, metod_pay=None, amount=None)




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
        #await state.update_data(order_id=order_id)
        if lang == "ru": message_text = "📝 Введите свой вариант срока диагностики:"
        else: message_text = "📝 Enter your option for the diagnosis period:"
        buttons = [UI_TEXTS[lang]["card"], UI_TEXTS[lang]["cash"], UI_TEXTS[lang]["crypto"], UI_TEXTS[lang]["no_payment"], UI_TEXTS[lang]["cancel"]]
        await message.answer(message_text, reply_markup = build_keyboard(buttons))
        await state.set_state(Action.pay_method)
        return
