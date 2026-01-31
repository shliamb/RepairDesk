#! handlers/search_order.py python3
from logs.set_logger import set_logger
logger = set_logger(name="handlers")
from handlers.common import typing, is_manager
# from database.users import search_clients
# from handlers.edit_client import start_edit_client
from utils.formatters import format_date_nice, remove_emojis, extract_emoji, clean_user_input, parse_cost, add_days_from_text, format_telegram_username, format_phone
from utils.parse import detect_search_field_order
# from datetime import datetime
from aiogram import Router, types, F
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
# from aiogram.filters import Command
from aiogram.types import ReplyKeyboardRemove, InlineKeyboardMarkup, InlineKeyboardButton
from config import CURRENCY, HUMAN_QUALITY, UI_TEXTS, CANCEL
from keyboards.workshop import build_keyboard
from database import db
from database.orders import OrderService
import uuid
# import json

router = Router()
order = OrderService(db)



class SearchOrder(StatesGroup):
    search = State()




# CANCEL STATE & KEYBOARD TO ALL HANDLERS !!!
@router.message((F.text == CANCEL["ru"]) | (F.text == CANCEL["en"]))
async def cancel(message: types.Message, state: FSMContext): 
    """ Отмена / Cancelled """
    await typing(message)
    lang = message.from_user.language_code
    await state.clear()
    if lang == "ru": await message.answer("🚫 Отменено", reply_markup=ReplyKeyboardRemove())
    else: await message.answer("🚫 Cancelled", reply_markup=ReplyKeyboardRemove())



# # OPEN CLIENT CARD
# @router.callback_query(F.data.startswith("open_client_"))
# async def select_client(callback: types.CallbackQuery, state: FSMContext):
#     """ Нажатие кнопки открыть контакт """
#     lang = callback.from_user.language_code
#     client_id = callback.data.split("_")[-1]  # вытащить client_id
#     if isinstance(client_id, str): client_id = uuid.UUID(client_id)
#     else: logger.error(f"{client_id} is not UUID")

#     user_id = callback.from_user.id
#     lang = callback.from_user.language_code

#     await start_edit_client(client_id, state, callback.message, user_id, lang)
#     await callback.answer()



# START SEARCH ORDER
@router.message(SearchOrder.search)
async def get_patern_order(message: types.Message, state: FSMContext):
    """ Получения данных поиска заказа в базе """
    await typing(message)
    lang = message.from_user.language_code
    # user_id = message.from_user.id

    if message.text.startswith('/'):
        if lang == "ru": await message.answer("🚫 Для выхода из поиска заказа, нажмите - Отмена")
        else: await message.answer("🚫 To exit the order search, click Cancel")
        return

    imput_text = clean_user_input(message.text)
    if not imput_text:
        if lang == "ru": await message.answer("🚫 Попробуйте что то ввести для поиска заказа")
        else: await message.answer("🚫 Try to enter something to search for a order")
        return

    patern, clear_input = detect_search_field_order(imput_text)
    # print(patern, clear_input)

    if patern == "order_number_suffix":
        data_orders = await order.search_by_order_suffix(clear_input)
    else:
        data_orders = await order.search_order_pattern(patern, clear_input)

    # print(data_orders)

    if not data_orders:
        if lang == "ru": await message.answer("🌀 Нет результатов")
        else: await message.answer("🌀 No results")
        return
    
    for data_order in data_orders:
        order_card = ""

        order_number = data_order.get("order_number")
        sn_imei = data_order.get("sn_imei")
        status = data_order.get("status")
        order_type = data_order.get("order_type")

        device_type = data_order.get("device_type")
        device_brand = data_order.get("device_brand")
        device_model = data_order.get("device_model")
        equipment = data_order.get("equipment")
        problem = data_order.get("problem")
        appearance = data_order.get("appearance")
        created_date = data_order.get("created_date")
        completion_date = data_order.get("completion_date")

        diagnosis_before = data_order.get("diagnosis_before")
        created_by = data_order.get("created_by")


        if lang == "ru":
            order_card = f"<b>{order_number}</b>\n"
#             if username_telegram: customer_card += f"        {format_telegram_username(username_telegram)}\n"
#             if phone: customer_card += f"        {phone}\n"

#             if total_spent or repair_count_total or a_tip: customer_card += "\n📊 <b>СТАТИСТИКА:</b>\n"
#             if total_spent: customer_card += f"        Всего потрачено: {total_spent}\n"
#             if repair_count_total: customer_card += f"        Всего ремонтов: {repair_count_total}\n"
#             if a_tip: customer_card += f"        Чаевые: {a_tip}\n"

#             # customer_card += "\n👥 <b>РОЛИ:</b>\n"
#             # if is_admin: customer_card += f"        Админ\n"
#             # if client_is_manager: customer_card += f"        Менеджер\n"
#             # if is_master: customer_card += f"        Мастер\n"
#             # if not is_admin and not client_is_manager and not is_master: customer_card += f"        Клиент\n"

#             # if block or description_user or hum_quality: customer_card += "\n⭐ <b>МЕТКИ:</b>\n"
#             # if description_user: customer_card += f"        Описание: {description_user}\n"
#             # if hum_quality: customer_card += f"        Качество: {hum_quality}\n"
#             # if block: customer_card += f"        Заблокирован\n"

#             customer_card += "\n📅 <b>ДАТЫ:</b>\n"
#             if time_reg: customer_card += f"        Регистрация: {format_date_nice(time_reg, lang)}\n"
#             if last_visit: customer_card += f"        Последний визит: {format_date_nice(last_visit, lang)}\n"

#             # if orders_client: customer_card += "\n🔧 <b>ЗАКАЗЫ:</b>\n"
#             # for one_order in orders_client:
#             #     order_number = one_order.get("order_number")
#             #     net_profit = one_order.get("net_profit")
#             #     created_date = one_order.get("created_date")
#             #     customer_card += f"        {order_number}"
#             #     if net_profit: customer_card += f" • {net_profit}{CURRENCY}"
#             #     customer_card += f" • {format_date_nice(created_date, lang)}\n"

        else:
            order_card = f"<b>{order_number}</b>\n"
#             if username_telegram: customer_card += f"        {format_telegram_username(username_telegram)}\n"
#             if phone: customer_card += f"        {phone}\n"

#             if total_spent or repair_count_total or a_tip: customer_card += "\n📊 <b>STATISTICS:</b>\n"
#             if total_spent: customer_card += f"        Total spent: {total_spent}\n"
#             if repair_count_total: customer_card += f"        Total repairs: {repair_count_total}\n"
#             if a_tip: customer_card += f"        Tips: {a_tip}\n"

#             # customer_card += "\n👥 <b>ROLES:</b>\n"
#             # if is_admin: customer_card += f"        Admin\n"
#             # if client_is_manager: customer_card += f"        Manager\n"
#             # if is_master: customer_card += f"        Master\n"
#             # if not is_admin and not client_is_manager and not is_master: customer_card += f"        Customer\n"

#             # if block or description_user or hum_quality: customer_card += "\n⭐ <b>TAGS:</b>\n"
#             # if description_user: customer_card += f"        Description: {description_user}\n"
#             # if hum_quality: customer_card += f"        Quality: {hum_quality}\n"
#             # if block: customer_card += f"        Blocked\n"

#             customer_card += "\n📅 <b>DATES:</b>\n"
#             if time_reg: customer_card += f"        Registration: {format_date_nice(time_reg, lang)}\n"
#             if last_visit: customer_card += f"        Last visit: {format_date_nice(last_visit, lang)}\n"

#             # if orders_client: customer_card += "\n🔧 <b>ORDERS:</b>\n"
#             # for one_order in orders_client:
#             #     order_number = one_order.get("order_number")
#             #     net_profit = one_order.get("net_profit")
#             #     created_date = one_order.get("created_date")
#             #     customer_card += f"        {order_number}"
#             #     if net_profit: customer_card += f" • {net_profit}{CURRENCY}"
#             #     customer_card += f" • {format_date_nice(created_date, lang)}\n"


        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text=f'{UI_TEXTS[lang]["open"]}', callback_data=f"open_order_{order_number}")
            ]
        ])
        
#         # print(f"open_client_{client_id}")
        await message.answer(order_card, parse_mode="HTML", reply_markup=keyboard)

    return



# START SEARCH ORDER
@router.message((F.text == UI_TEXTS["ru"]["serch_order"]) | (F.text == UI_TEXTS["en"]["serch_order"]))
async def start_search_order(message: types.Message, state: FSMContext):
    """ Запуск поиска заказа в базе """
    await typing(message)
    lang = message.from_user.language_code

    if lang == "ru": text = "🔎 Введите что то для поиска заказа:"
    else: text = "🔎 Enter something to search for an order:"

    await message.answer(text, reply_markup = build_keyboard([UI_TEXTS[lang]['cancel']]))
    await state.set_state(SearchOrder.search)

