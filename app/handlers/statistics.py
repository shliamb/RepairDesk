#! handlers/statistics.py python3
from logs.set_logger import set_logger
logger = set_logger(name="handlers")
from handlers.common import typing, is_manager, is_super_admin
from database.users import add_user, get_user_by_tg
from database.finstat import get_payments
from utils.formatters import parse_cost, add_days_from_text, format_telegram_username
from datetime import datetime
from aiogram import Router, types, F
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardRemove
from config import get_brands, UI_TEXTS, CANCEL
from keyboards.workshop import build_keyboard
from database import db
from database.orders import OrderService
from pdf.gen_pdf import BuildPDF
import uuid
import json

router = Router()
order = OrderService(db)




class Statistic(StatesGroup):
    period = State()
    filter = State()







# CANCEL STATE & KEYBOARD TO ALL HANDLERS !!!
@router.message((F.text == CANCEL["ru"]) | (F.text == CANCEL["en"]))
async def cancel(message: types.Message, state: FSMContext): 
    """ Отмена / Cancelled """
    await typing(message)
    lang = message.from_user.language_code
    await state.clear()
    if lang == "ru": await message.answer("🚫 Отменено", reply_markup=ReplyKeyboardRemove())
    else: await message.answer("🚫 Cancelled", reply_markup=ReplyKeyboardRemove())






# GET STATISTICS PERIOD
@router.message(Statistic.filter)
async def get_period(message: types.Message, state: FSMContext):
    """  """
    await typing(message)
    lang = message.from_user.language_code
    user_id = message.from_user.id
    input_mes = message.text
    state_data = await state.get_data()
    data_orders = state_data.get("data_orders")
    period = state_data.get("period")


    if input_mes == UI_TEXTS[lang]['stats_orders_count']:
        n = len(data_orders)
        print(n)
        return



    # if lang == "ru": await message.answer("🚫 Попробуйте еще раз выбрать пункт из меню")
    # else: await message.answer("🚫 Try again to select an item from the menu")





# GET STATISTICS PERIOD
@router.message(Statistic.period)
async def get_statistics(message: types.Message, state: FSMContext):
    """ Статистика за период """
    await typing(message)
    lang = message.from_user.language_code
    user_id = message.from_user.id
    input_mes = message.text

    if input_mes == UI_TEXTS[lang]["today"]: period = "today"
    elif input_mes == UI_TEXTS[lang]["month"]: period = "month"
    elif input_mes == UI_TEXTS[lang]["year"]: period ="year"
    elif input_mes == UI_TEXTS[lang]["years"]: period = "years"
    else:
        if lang == "ru": await message.answer("🚫 Попробуйте еще раз выбрать пункт из меню")
        else: await message.answer("🚫 Try again to select an item from the menu")
        return

    data_orders = await get_payments(period)
    print(data_orders)

    if not data_orders:
        if lang == "ru": await message.answer("🌀 Нет результатов")
        else: await message.answer("🌀 No results")
        return
    
    buttons = [
        UI_TEXTS[lang]['stats_revenue'],
        UI_TEXTS[lang]['stats_orders_count'],
        UI_TEXTS[lang]['stats_payment_methods'],
        UI_TEXTS[lang]['stats_by_master'],
        UI_TEXTS[lang]['stats_by_device'],
        UI_TEXTS[lang]["cancel"]
    ]

    await state.update_data(data_orders=data_orders, period=period)

    if lang == "ru": text = "Выберите фильтр:"
    else: text = "Select a filter:"
    await message.answer(text, reply_markup = build_keyboard(buttons)) 
    await state.set_state(Statistic.filter)
    



# RUN STATISTICS PROCESS
@router.message((F.text == UI_TEXTS["en"]['stat']) | (F.text == UI_TEXTS["ru"]['stat']))
async def run_statistics(message: types.Message, state: FSMContext):
    """ Статистика для админов"""
    await typing(message)
    lang = message.from_user.language_code
    user_id = message.from_user.id

    if not await is_super_admin(user_id):
        if lang == "ru": await message.answer("🔐 Вы не имеете доступа!")
        else: await message.answer("🔐 You don't have access")
        return
    
    if lang == "ru": text = "Выберите период:"
    else: text = "Select a period:"
    await message.answer(text, reply_markup = build_keyboard([UI_TEXTS[lang]["today"], UI_TEXTS[lang]["month"], UI_TEXTS[lang]["year"], UI_TEXTS[lang]["years"], UI_TEXTS[lang]["cancel"]])) 
    
    await state.set_state(Statistic.period)
