#! app/handlers/actions_order.py
from handlers.common import typing, is_manager
from logs.set_logger import set_logger
logger = set_logger(name="handlers")
from utils.formatters import remove_emojis, extract_emoji, format_phone, format_date_nice, format_telegram_username, safe_int, safe_decimal, safe_float
from database.users import get_user_by_user_id, get_user_by_tg, edit_client
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





# START PAYD ORDER:
@router.message(Action.pay_method)
async def choosing_payment_method(message: types.Message, state: FSMContext):
    """ Выбор способа оплаты и все остальное..  """
    await typing(message)
    lang = message.from_user.language_code
    #user_id = message.from_user.id
    input_text = message.text
    state_data = await state.get_data()

    metod_pay, amount, take, a_tip, order_id, status_order = state_data.get("metod_pay"), state_data.get("amount"), state_data.get("take"), state_data.get("a_tip"), state_data.get("id"), state_data.get("status")

    if metod_pay is None:
        if input_text == UI_TEXTS[lang]["no_payment"]:
            status_order = "issued_not_paid"
            metod_pay = "no_payment",
            amount = 0,
            take = True,
            a_tip = 0

        elif input_text in (UI_TEXTS[lang]["card"], UI_TEXTS[lang]["cash"], UI_TEXTS[lang]["crypto"], UI_TEXTS[lang]["no_payment"]):
            for key, value in UI_TEXTS[lang].items():
                if input_text == value:
                    await state.update_data(metod_pay=key)
                    if lang == "ru": message_text = "💰 Введите вносимую сумму:"
                    else: message_text = "💰 Enter payment amount:"
                    await message.answer(message_text, reply_markup = build_keyboard([UI_TEXTS[lang]["cancel"]]))
                    return
        else:
            if lang == "ru": await message.answer("🚫 Попробуйте еще раз выбрать пункт из меню")
            else: await message.answer("🚫 Try again to select an item from the menu")
            return
        
    elif metod_pay and amount is None:
        if not is_number(input_text):
            if lang == "ru": await message.answer("🚫 Введите вносимую сумму:")
            else: await message.answer("🚫 Enter payment amount:")
            return
        
        await state.update_data(amount=safe_float(input_text))
        if lang == "ru": message_text = "📤 Клиент забирает устройство?:"
        else: message_text = "📤 Is the client picking up the device?:"
        await message.answer(message_text, reply_markup = build_keyboard([UI_TEXTS[lang]["yes"], UI_TEXTS[lang]["no"], UI_TEXTS[lang]["cancel"]]))
        return

    elif metod_pay and amount and take is None:
        if input_text not in (UI_TEXTS[lang]["yes"], UI_TEXTS[lang]["no"]):
            if lang == "ru": await message.answer("🚫 Попробуйте еще раз выбрать пункт из меню")
            else: await message.answer("🚫 Try again to select an item from the menu")
            return
        
        if input_text == UI_TEXTS[lang]["yes"]: take = True
        elif input_text == UI_TEXTS[lang]["no"]: take = False

        await state.update_data(take=take)
        if lang == "ru": message_text = "🫰 Оставили чаевые:"
        else: message_text = "🫰 Tip added:"
        await message.answer(message_text, reply_markup = build_keyboard([UI_TEXTS[lang]["miss"], UI_TEXTS[lang]["cancel"]]))
        return


    elif metod_pay and amount and take is not None and a_tip is None:
        if input_text == UI_TEXTS[lang]["miss"]:
            a_tip = 0
            await state.update_data(a_tip=a_tip)

        elif not is_number(input_text):
            if lang == "ru": await message.answer("🚫 Введите сумму чаевых:")
            else: await message.answer("🚫 Enter the tip amount:")
            return
        
        else:
            a_tip = safe_float(input_text)
            await state.update_data(a_tip=a_tip)


    # COLLECTING DATA USER:
    data_order = await order.get_order_id(order_id)
    client_id = data_order.get("client_id")

    data_user = await get_user_by_user_id(client_id)
    old_a_tip = data_user.get("a_tip")
    old_total_spent = data_user.get("total_spent")
    old_repair_count_total = data_user.get("repair_count_total")

    updata_client = {
        "user_id": client_id,
        "a_tip": safe_decimal(safe_float(old_a_tip) + (safe_float(a_tip) or 0)),
        "total_spent": safe_decimal(safe_float(old_total_spent) + safe_float(amount)),
        "repair_count_total": safe_int(old_repair_count_total) + 1
    }

    # GET STATUS ORDER:
    # status_order = 

    # GET DATA FIN STATISTIC:
    #

    print("metod_pay:", metod_pay, "amount:", amount, "take:", take, "a_tip:", a_tip, "status_order:", status_order)
    print(updata_client)



    # UPDATE FIN STATISTIC:
    #

    # UPDATE ORDER:
    #

    # UPDATE CLIENT DATA:
    # if not await edit_client(updata_client):
    #     if lang == "ru": await message.answer("🚫 Ошибка в обновлении данных клиента")
    #     else: await message.answer("🚫 Error in updating client data")

    await state.update_data(id=None, metod_pay=None, amount=None, take=None, a_tip=None)
    if lang == "ru": await message.answer("👍 Изменения сохранены", reply_markup=ReplyKeyboardRemove())
    else: await message.answer("👍 The changes are saved", reply_markup=ReplyKeyboardRemove())








# CHOICE ACTIONS ORDER: 
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
        # await state.update_data(order_id=order_id) Уже есть внутри id = order_id
        if lang == "ru": message_text = "💰 Выберите способ оплаты:"
        else: message_text = "💰 Select payment method:"
        buttons = [UI_TEXTS[lang]["card"], UI_TEXTS[lang]["cash"], UI_TEXTS[lang]["crypto"], UI_TEXTS[lang]["no_payment"], UI_TEXTS[lang]["cancel"]]
        await message.answer(message_text, reply_markup = build_keyboard(buttons))
        await state.set_state(Action.pay_method)
        return
