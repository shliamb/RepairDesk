#! handlers/search.py python3
from logs.set_logger import set_logger
logger = set_logger(name="handlers")
from handlers.common import typing, is_manager
from database.users import search_clients
from handlers.edit_client import start_edit_client
from utils.formatters import format_date_nice, remove_emojis, extract_emoji, clean_user_input, parse_cost, add_days_from_text, format_telegram_username, format_phone
from utils.parse import detect_search_field
from datetime import datetime
from aiogram import Router, types, F
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardRemove, InlineKeyboardMarkup, InlineKeyboardButton
from config import CURRENCY, get_brands, HUMAN_QUALITY, UI_TEXTS, COST_DIAGNOSTIC, DIAGNOSTIC_TIME, DEVICES_RU, DEVICES_EN, EQUIPMENT, MISS, DONE, OWN_VERSION, PROBLEMS, CANCEL, ORDER, CLIENT, TYPE_ORDER, APPEARANCE
from keyboards.workshop import build_keyboard
from database import db
from database.orders import OrderService
import uuid
import json

router = Router()
order = OrderService(db)



class Client(StatesGroup):
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







# async def get_searching_data(message: types.Message, state: FSMContext):
# start_edit_client(client_id: uuid, state: FSMContext, message: types.Message)
#     pass



# START SEARCH CLIENT
@router.message(Client.search)
async def get_patern_client(message: types.Message, state: FSMContext):
    """ Получения данных поиска клиента в базе """
    await typing(message)
    lang = message.from_user.language_code
    # user_id = message.from_user.id

    if message.text.startswith('/'):
        if lang == "ru": await message.answer("🚫 Для выхода из поиска пользователя, нажмите - Отмена")
        else: await message.answer("🚫 To exit the user search, click Cancel")
        return

    imput_text = clean_user_input(message.text)
    if not imput_text:
        if lang == "ru": await message.answer("🚫 Попробуйте что то ввести для поиска клиента")
        else: await message.answer("🚫 Try to enter something to search for a client")
        return

    pater, clear_input = detect_search_field(imput_text)
    data_clients = await search_clients(pater, clear_input)

    if not data_clients:
        if lang == "ru": await message.answer("🌀 Нет результатов")
        else: await message.answer("🌀 No results")
        return
    
    for client in data_clients:
        customer_card = ""

        client_id = client.get("user_id")
        name = client.get("name")
        phone = format_phone(client.get("phone"))
        username_telegram = client.get("username_telegram")

        a_tip = client.get("a_tip")
        total_spent = client.get("total_spent")
        repair_count_total = client.get("repair_count_total")
        description_user = client.get("description_user")
        block = client.get("block")
        hum_quality = client.get("hum_quality")
        last_visit = client.get("last_visit")
        time_reg = client.get("time_reg")

        is_admin = client.get("is_admin")
        client_is_manager = client.get("is_manager")
        is_master = client.get("is_master")

        orders_client = await order.get_orders_by_user(client_id)

        quality = HUMAN_QUALITY[lang].get(hum_quality) or ""
        hum_quality = remove_emojis(quality) or None
        ico_client = extract_emoji(quality) or "😐"

        if lang == "ru":
            customer_card = f"{ico_client} <b>{name}</b>\n"
            if username_telegram: customer_card += f"        {format_telegram_username(username_telegram)}\n"
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

            if block or description_user or hum_quality: customer_card += "\n⭐ <b>МЕТКИ:</b>\n"
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
            customer_card = f"<b>{ico_client} {name}</b>\n"
            if username_telegram: customer_card += f"        {format_telegram_username(username_telegram)}\n"
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

            if block or description_user or hum_quality: customer_card += "\n⭐ <b>TAGS:</b>\n"
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


        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text=f'{UI_TEXTS[lang]["open"]}', callback_data=f"open_client_{client_id}")
            ]
        ])
        
        # print(f"open_client_{client_id}")
        await message.answer(customer_card, parse_mode="HTML", reply_markup=keyboard)

    return



# # EDIT ORDER
# @router.callback_query(F.data.startswith("edit_order_"))
# async def edit_order(callback: types.CallbackQuery, state: FSMContext):
#     """ Выбор объекта изменения под каждым заказом """
#     lang = callback.from_user.language_code
#     id = callback.data.split("_")[-1]  # вытащить ID
#     if not isinstance(id, int): id = int(id)
#     else: logger.error(f"{id} is not digit")
#     #await callback.message.answer(f"Редактируем заказ {id}")
#     # await callback.message.answer(f"process_edit_order_{id}", parse_mode=None)
#     if lang == "ru": buttons = [CHANGE_ORDER["order_ru"], CHANGE_ORDER["client_ru"], CANCEL["ru"]] # CHANGE_ORDER["status_ru"],
#     else: buttons = [CHANGE_ORDER["order_en"], CHANGE_ORDER["client_en"], CANCEL["en"]] # CHANGE_ORDER["status_en"],
#     if lang == "ru": intro_text = f"Выберите действие по заказу:"
#     else: intro_text = f"Select the order action:"
#     await callback.message.answer(intro_text, reply_markup = build_keyboard(buttons))
#     await state.update_data(id=id)
#     await state.set_state(Order.edit)
#     await callback.answer()



# START SEARCH CLIENT
@router.message((F.text == UI_TEXTS["ru"]["serch_cli"]) | (F.text == UI_TEXTS["en"]["serch_cli"]))
async def start_search_client(message: types.Message, state: FSMContext):
    """ Запуск поиска клиента в базе """
    await typing(message)
    lang = message.from_user.language_code

    if lang == "ru": text = "🔎 Введите Имя, Фамилию, телеграмм (@username), телефон, часть данных:"
    else: text = "🔎 Enter: Name, telegram (@username), phone, or part of data:"

    await message.answer(text, reply_markup = build_keyboard([UI_TEXTS[lang]['cancel']]))
    await state.set_state(Client.search)

