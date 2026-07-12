#! handlers/viewing_orders.py.py
from handlers.common import typing, is_manager
from handlers.workshop import workshop_panel
from logs.set_logger import set_logger
logger = set_logger(name="handlers")
from utils.formatters import format_date_nice, safe_decimal
from aiogram import Router, types, F
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from database.orders import OrderService
from config import CANCEL, ORDER, IN_PROGRESS_STATUSES, READY_STATUSES, \
    CURRENCY, VIEW_ORDER, CHANGE_ORDER, ACTION_ORDER, ORDER_STATUS_RU, ORDER_STATUS, UI_TEXTS, COMPLETED_STATUSES, NEW
from keyboards.workshop import build_keyboard
from database import db
import json


router = Router()
order = OrderService(db)



class Order(StatesGroup):
    edit = State()
    action = State()




# OUTPUTTING ORDERS TO THE TELEGRAMM BOT
async def push_orders_bot(
    message: types.Message,
    state: FSMContext,
    lang: str, 
    records: list,
    offset: int = 0,
    page_size: int = 10,
):
    """ Вывод заказов в телеграмм боте.
    
        Для работы с заказами использую 
        id (id SERIAL PRIMARY KEY) - это 
        быстре и проще для внутренней работы, 
        для клиента - order_number """
    
    await typing(message)

    if not records:
        if lang == "ru": await message.answer("Заказов нет")
        else: await message.answer("There are no orders")
        return
    
    # Вычисляем, сколько осталось записей после текущей страницы
    total_records = len(records)

    if offset + page_size > total_records:
        end_index = total_records
    else:
        end_index = offset + page_size
    
    # Выводим только текущую страницу
    for i in range(offset, end_index):
        one = records[i]
        order = ""
        id = one.get("id")
        # print("id order:", id)
        order_number = one.get("order_number")
        order_type = one.get("order_type")
        device_type = one.get("device_type")
        device_brand = one.get("device_brand")
        device_model = one.get("device_model") or ""
        real_name_client = one.get("real_name_client")
        # real_name_created = one.get("real_name_created")
        # problem = json.loads(one.get("problem")) if one.get("problem") else ""
        # problem = ", ".join(problem.copy())
        problem_data = one.get("problem")
        if problem_data:
            try:
                problem_list = json.loads(problem_data)
                if isinstance(problem_list, list):
                    problem = ", ".join(problem_list)
                else:
                    problem = str(problem_list)
            except json.JSONDecodeError:
                problem = problem_data
        else:
            problem = ""

        status = one.get("status")

        if status in ("issued", "paid_not_issued"):
            icon_payd = "💵"
        elif status in "ready":
            icon_payd = "⏳"
        else:
            icon_payd = None

        created_date = one.get("created_date")
        created_date = format_date_nice(created_date, lang)
        diagnosis_before = one.get("diagnosis_before")
        diagnosis_before = format_date_nice(diagnosis_before, lang)
        # cost_diagnostics = int(one.get("cost_diagnostics")) or 0
        cost_repair = one.get("cost_repair") or 0
        cost_of_parts = one.get("cost_of_parts") or 0
        total = float(cost_repair) + float(cost_of_parts)

        if lang == "ru":
            order = (
                f'<b>📋 {order_number}</b>{" • Гарантия" if order_type == "guarant" else ""} • {ORDER_STATUS_RU.get(status)}\n\n'
                f'   • <b>{real_name_client}</b>\n'
                f'   • <b>{device_type}</b> {device_brand} {device_model}\n'
                f'   • до {diagnosis_before}\n\n'
                f'   • {problem}\n\n'
            )

            if total:
                order += f'   <b>ИТОГО: {total:,.0f} {CURRENCY}</b>'
            if icon_payd:
                order += f' {icon_payd}'

        else:
            order = (
                f'<b>📋 {order_number}</b>{" • Guaranty" if order_type == "guarant" else ""} • {ORDER_STATUS.get(status)}\n\n'
                f'   • <b>{real_name_client}</b>\n'
                f'   • <b>{device_type}</b> {device_brand} {device_model}\n'
                f'   • until {diagnosis_before}\n\n'
                f'   • {problem}\n\n'
            )

            if total:
                order += f'   <b>TOTAL: {total:,.0f} {CURRENCY}</b>'
            if icon_payd:
                order += f' {icon_payd}'
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=VIEW_ORDER["change_ru"] if lang == "ru" else VIEW_ORDER["change_en"], 
                    callback_data=f"edit_order_{one.get('id')}"
                ),
                InlineKeyboardButton(
                    text=VIEW_ORDER["action_ru"] if lang == "ru" else VIEW_ORDER["action_en"], 
                    callback_data=f"action_order_{one.get('id')}"
                )
            ]
        ])
        
        await message.answer(order, parse_mode="HTML", reply_markup=keyboard)
    
    # Если есть ещё записи - добавляем кнопку "Ещё"
    if end_index < total_records:

        await state.update_data(records=records, offset=offset+page_size, page_size=page_size)

        remaining = total_records - end_index
        button_load = f"📥 {f'Ещё {remaining}' if lang == 'ru' else f'Load {remaining}'}"
        text_message = f"📄 {end_index}/{total_records}" + (f"\nЗагрузить ещё {remaining}?" if lang == "ru" else f"\nLoad {remaining} more?")
        await message.answer(text_message, reply_markup = build_keyboard([button_load, UI_TEXTS[lang]['cancel']]))
    
    else:
        await state.update_data(records=[], offset=0, page_size=None)
        # if lang == "ru": await message.answer("👍 Больше записей нет", reply_markup=ReplyKeyboardRemove())
        # else: await message.answer("👍 Done", reply_markup=ReplyKeyboardRemove())
        await workshop_panel(message, state)




# Обработчик кнопки "Ещё"
@router.message(
        F.text.startswith("📥 Load") |
        F.text.startswith("📥 Ещё")
)
async def load_more_orders(message: types.Message, state: FSMContext):
    """ Догрузить еще заказы"""
    await typing(message)
    lang = message.from_user.language_code
    state_data = await state.get_data()
    records = state_data.get("records")
    offset = state_data.get("offset")
    page_size = state_data.get("page_size")
    await push_orders_bot(message, state, lang, records, offset=offset, page_size=page_size)
    





# OPEN ORDER
@router.callback_query(F.data.startswith("edit_order_"))
async def edit_order(callback: types.CallbackQuery, state: FSMContext):
    """ Выбор объекта изменения под каждым заказом """
    lang = callback.from_user.language_code
    id = callback.data.split("_")[-1]  # вытащить ID
    if not isinstance(id, int): id = int(id)
    else: logger.error(f"{id} is not digit")
    #await callback.message.answer(f"Редактируем заказ {id}")
    # await callback.message.answer(f"process_edit_order_{id}", parse_mode=None)
    buttons = [UI_TEXTS[lang]["order"], UI_TEXTS[lang]["client"], UI_TEXTS[lang]["cancel"]]
    if lang == "ru": intro_text = f"Выберите действие по заказу:"
    else: intro_text = f"Select the order action:"
    await callback.message.answer(intro_text, reply_markup = build_keyboard(buttons))
    await state.update_data(id=id)
    await state.set_state(Order.edit)
    await callback.answer()



# ACTION ORDER
@router.callback_query(F.data.startswith("action_order_"))
async def action_order(callback: types.CallbackQuery, state: FSMContext):
    """ Выбор действий под каждым заказом """
    lang = callback.from_user.language_code
    id = callback.data.split("_")[-1]
    if not isinstance(id, int): id = int(id)
    else: logger.error(f"{id} is not digit")
    buttons = [UI_TEXTS[lang]["get_photo"], UI_TEXTS[lang]["get_pdf"], UI_TEXTS[lang]["payd"], UI_TEXTS[lang]["delet"], UI_TEXTS[lang]["feedback"], UI_TEXTS[lang]["cancel"]]
    if lang == "ru": intro_text = f"Выберите действие по заказу:"
    else: intro_text = f"Select the order action:"
    await callback.message.answer(intro_text, reply_markup = build_keyboard(buttons))
    await state.update_data(id=id)
    await state.set_state(Order.action)
    await callback.answer()









# START GET NEW
@router.message(
    F.text.startswith(UI_TEXTS["ru"]["new_orders"]) | 
    F.text.startswith(UI_TEXTS["en"]["new_orders"])
)
async def get_new(message: types.Message, state: FSMContext):
    """ Показать заказы в работе"""
    await typing(message)
    lang = message.from_user.language_code
    user_id = message.from_user.id
    if not await is_manager(user_id):
        logger.error(f"{user_id} You don't have access")
        await message.answer("🔐 You don't have access")
        return
    
    # Собрать в процессе Заказы из базы
    records = await order.get_orders_by_statuses(NEW)
    await push_orders_bot(message, state, lang, records)




# START GET ISSUED
@router.message(
    F.text.startswith(UI_TEXTS["ru"]["issued"]) | 
    F.text.startswith(UI_TEXTS["en"]["issued"])
)
async def get_issued(message: types.Message, state: FSMContext):
    """ Показать заказы в работе"""
    await typing(message)
    lang = message.from_user.language_code
    user_id = message.from_user.id
    if not await is_manager(user_id):
        logger.error(f"{user_id} You don't have access")
        await message.answer("🔐 You don't have access")
        return
    
    # Собрать в процессе Заказы из базы
    records = await order.get_orders_by_statuses(COMPLETED_STATUSES)
    await push_orders_bot(message, state, lang, records)




# START GET IN PROGRESS ORDERS
@router.message(
    F.text.startswith(UI_TEXTS["ru"]["in_work"]) | 
    F.text.startswith(UI_TEXTS["en"]["in_work"])
)
async def get_in_work(message: types.Message, state: FSMContext):
    """ Показать заказы в работе"""
    await typing(message)
    lang = message.from_user.language_code
    user_id = message.from_user.id
    if not await is_manager(user_id):
        logger.error(f"{user_id} You don't have access")
        await message.answer("🔐 You don't have access")
        return
    
    # Собрать в процессе Заказы из базы
    records = await order.get_orders_by_statuses(IN_PROGRESS_STATUSES)
    await push_orders_bot(message, state, lang, records)



# START GET READY ORDERS
@router.message(
    F.text.startswith(UI_TEXTS["ru"]["ready_orders"]) | 
    F.text.startswith(UI_TEXTS["en"]["ready_orders"])
)
async def get_ready_orders(message: types.Message, state: FSMContext):
    """ Показать готовые заказы """
    await typing(message)
    lang = message.from_user.language_code
    user_id = message.from_user.id
    if not await is_manager(user_id):
        logger.error(f"{user_id} You don't have access")
        await message.answer("🔐 You don't have access")
        return

    # Собрать Готовые Заказы из базы
    records = await order.get_orders_by_statuses(READY_STATUSES)
    await push_orders_bot(message, state, lang, records)

    # Выдать сумму ожидаемую к оплате:
    amount = 0
    for rec in records:
        net_profit = safe_decimal(rec.get("net_profit")) or 0
        amount += net_profit
    
    if lang == "ru": await message.answer(f"💰 Потенциально к оплате: {amount} {CURRENCY}")
    else: await message.answer(f"💰 Potential payment: {amount} {CURRENCY}")




# GET LAST ORDERS
@router.message(
    F.text.startswith(UI_TEXTS["ru"]["last_orders"]) | 
    F.text.startswith(UI_TEXTS["en"]["last_orders"])
)
async def get_last(message: types.Message, state: FSMContext):
    """ Показать все заказы от большего к меньшему """
    await typing(message)
    lang = message.from_user.language_code
    user_id = message.from_user.id
    if not await is_manager(user_id):
        logger.error(f"{user_id} You don't have access")
        await message.answer("🔐 You don't have access")
        return

    records = await order.get_last_orders_all()
    await push_orders_bot(message, state, lang, records, page_size=10)


