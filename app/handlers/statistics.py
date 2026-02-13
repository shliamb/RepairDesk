#! handlers/statistics.py python3
from logs.set_logger import set_logger
logger = set_logger(name="handlers")
from handlers.common import typing, is_manager, is_super_admin
from database.users import add_user, get_user_by_tg
from database.finstat import get_fin_stats
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
@router.message(Statistic.period)
async def get_statistics_period(message: types.Message, state: FSMContext):
    """ Статистика за период """
    await typing(message)
    lang = message.from_user.language_code
    user_id = message.from_user.id
    input_mes = message.text

    if not await is_super_admin(user_id):
        if lang == "ru": await message.answer("🔐 Вы не имеете доступа!")
        else: await message.answer("🔐 You don't have access")
        return
    

    if input_mes == UI_TEXTS[lang]["today"]:
        period = "day"
    
    elif input_mes == UI_TEXTS[lang]["month"]:
        period = "month"

    elif input_mes == UI_TEXTS[lang]["year"]:
        period ="year"
    
    elif input_mes == UI_TEXTS[lang]["years"]:
        period = "years"
    
    else:
        return

    data_orders = await get_fin_stats(period)
    print(data_orders)
    

    buttons = [
        UI_TEXTS[lang]['stats_revenue'],
        UI_TEXTS[lang]['stats_orders_count'],
        UI_TEXTS[lang]['stats_payment_methods'],
        UI_TEXTS[lang]['stats_by_master'],
        UI_TEXTS[lang]['stats_by_device'],
        UI_TEXTS[lang]["cancel"]
    ]

    if lang == "ru": text = "Выберите условие:"
    else: text = "Select a condition:"
    await message.answer(text, reply_markup = build_keyboard(buttons)) 
    



# GET STATISTICS
@router.message((F.text == UI_TEXTS["en"]['stat']) | (F.text == UI_TEXTS["ru"]['stat']))
async def get_statistics(message: types.Message, state: FSMContext):
    """ Статистика для админов"""
    await typing(message)
    lang = message.from_user.language_code
    user_id = message.from_user.id

    if not await is_super_admin(user_id):
        if lang == "ru": await message.answer("🔐 Вы не имеете доступа!")
        else: await message.answer("🔐 You don't have access")
        return
    
    if lang == "ru": text = "Выберите условие:"
    else: text = "Select a condition:"
    await message.answer(text, reply_markup = build_keyboard([UI_TEXTS[lang]["today"], UI_TEXTS[lang]["month"], UI_TEXTS[lang]["year"], UI_TEXTS[lang]["years"], UI_TEXTS[lang]["cancel"]])) 
    
    await state.set_state(Statistic.period)
