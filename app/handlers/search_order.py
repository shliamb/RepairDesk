#! handlers/search_order.py python3
from logs.set_logger import set_logger
logger = set_logger(name="handlers")
from handlers.common import typing, is_manager
from handlers.viewing_orders import push_orders_bot
from utils.formatters import clean_user_input
from utils.parse import detect_search_field_order
from aiogram import Router, types, F
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardRemove
from config import UI_TEXTS, CANCEL
from keyboards.workshop import build_keyboard
from database import db
from database.orders import OrderService


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
    
    # Вывод заказов с кнопками
    await push_orders_bot(message, state, lang, data_orders)



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

