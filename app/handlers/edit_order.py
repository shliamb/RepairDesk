#! app/handlers/edit_order.py
from handlers.common import typing, is_manager
from logs.set_logger import set_logger
logger = set_logger(name="handlers")
from utils.formatters import remove_emojis, format_phone, format_date_nice
from aiogram import Router, types, F
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import ReplyKeyboardRemove, InlineKeyboardMarkup, InlineKeyboardButton
# from aiogram.utils.keyboard import ReplyKeyboardBuilder, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext
from database.orders import OrderService
from config import CHANGE_ORDER, CURRENCY, DEVICE_ICO, ORDER_STATUS_COLOR, ORDER_STATUS_RU, ORDER_STATUS_EN
from keyboards.workshop import build_keyboard
from database import db
from handlers.viewing_orders import Order
# import asyncio
import json
from datetime import datetime



router = Router()
order = OrderService(db)




def format_order_card(lang, **kwargs):
    """Форматирует карточку заказа"""
    
    if lang == "ru":
        device_ico = DEVICE_ICO
        order_status_color = ORDER_STATUS_COLOR
        status_dict = ORDER_STATUS_RU
        texts = {
            'order': '📋 ЗАКАЗ',
            'status': 'СОСТОЯНИЕ',
            'client': '👨‍💼 КЛИЕНТ',
            'device': 'УСТРОЙСТВО',
            'accepted': '📥 ПРИНЯЛ',
            'master': '👨‍🔧 МАСТЕР',
            'diagnosis': '⏱️ ДИАГНОСТИКА',
            'diagnostic_result': '🔍 РЕЗУЛЬТ. ДИАГНОСТИКИ',
            'problem': '⚠️ ПРОБЛЕМА',
            'services': '🛠️ УСЛУГИ',
            'parts': '🔩 ЗАПЧАСТИ',
            'total': '💰 ИТОГО',


            'equipment': 'Комплектация',
            'appearance': 'Состояние',
            'paid': 'Платный',
            'warranty': 'Гарантийный',
            'by': 'от',
            'until': 'до',
            'phone': 'Телефон'
        }

    else:
        device_ico = DEVICE_ICO
        order_status_color = ORDER_STATUS_COLOR
        status_dict = DEVICE_ICO
        texts = {
            'order': '📋 ORDER',
            'status': 'CONDITION',
            'client': '👨‍💼 CLIENT',
            'device': 'DEVICE',
            'accepted': '📥 ACCEPTED BY',
            'master': '👨‍🔧 MASTER',
            'diagnosis': '⏱️ DIAGNOSIS',
            'diagnostic_result': '🔍 DIAGNOSTIC RESULT',
            'problem': '⚠️ PROBLEM',
            'services': '🛠️ SERVICES',
            'parts': '🔩 PARTS',
            'total': '💰 TOTAL',

            'equipment': 'Equipment',
            'appearance': 'Appearance',
            'paid': 'Paid',
            'warranty': 'Warranty',
            'by': 'by',
            'until': 'until',
            'phone': 'Phone'
        }
    
    # Форматируем телефон
    formatted_phone = format_phone(kwargs.get('client_phone', ''))
    
    order_card = (

        f"<b>{texts['order']} {kwargs.get('order_number')}:</b>\n\n"

        f"<b>{order_status_color.get(kwargs.get('status', 'new'), '')} {texts['status']}:</b>\n"
        f"        {texts['paid'] if kwargs.get('order_type') == 'paid' else texts['warranty']}\n"
        f"        {status_dict.get(kwargs.get('status', 'new'), '')}\n\n"
        
        f"<b>{texts['client']}:</b>\n"
        f"        {kwargs.get('real_name_client', '')}\n"
        f"        {formatted_phone}\n"
        f"        @client\n"
        f"        Чаевые 0{CURRENCY}\n\n" # a_tip
        
        f"<b>{device_ico.get(kwargs.get('device_type', ''), '')} {texts['device']}:</b>\n"
        f"        {kwargs.get('device_type', '')}\n"
        f"        {kwargs.get('device_brand', '')} • {kwargs.get('device_model', '')}\n"
        f"        SN/IMEI: {kwargs.get('sn_imei', '')}\n"
        f"        {texts['equipment']}: {kwargs.get('equipment', '')}\n"
        f"        {texts['appearance']}: {kwargs.get('appearance', '')}\n\n"

        
        f"<b>{texts['accepted']}:</b>\n"
        f"        {texts['by']} {kwargs.get('real_name_created', '')}\n"
        f"        {kwargs.get('created_date', '')}\n"
        f"        {kwargs.get('created_by', '')}\n" # user_id ????!!!
        f"        @Shliamb\n\n" # username_telegram

        f"<b>{texts['master']}:</b>\n"
        f"        Alex\n" # 
        f"        @Shliamb\n" # # username_telegram
        f"        В пятницу доделаю, не давите бля!\n\n" # коммент от мастера
        
        f"<b>{texts['diagnosis']}:</b>\n"
        f"        {texts['until']} {kwargs.get('diagnosis_before', '')}\n"
        f"        {kwargs.get('cost_diagnostics', 0)} {CURRENCY}\n\n"
        
        f"<b>{texts['problem']}:</b>\n"
        f"        {kwargs.get('problem', '')}\n\n"

        f"<b>{texts['diagnostic_result']}:</b>\n"
        f"        ожидается\n\n"

        f"<b>{texts['services']}:</b>\n"
        f"        1. Замена экрана - 2000{CURRENCY}\n\n"

        f"<b>{texts['parts']}:</b>\n"
        f"        1. Экран sn34334 - 3500{CURRENCY}\n\n"

        f"----------------------------\n"

        f"<b>{texts['total']}:</b>\n"
        f"        <b>5500{CURRENCY}</b>\n\n"
    )
    
    # Добавляем примечание, если есть
    if kwargs.get('notes'):
        note_text = '📝 Примечание' if lang == 'ru' else '📝 Notes'
        order_card += f"\n<b>{note_text}:</b>\n        {kwargs.get('notes')}\n"
    
    return order_card






# OPEN FULL ORDER
async def start_edit_order(lang: str, order_id: int, state: FSMContext, message: types.Message):
    """ Начало изменения данных заказа """

    await typing(message)
    lang = message.from_user.language_code
    if not isinstance(order_id, int):
        logger.error(f"{id} is not digit")
        return
    
    data_order = await order.get_order_id(order_id)

    id = data_order.get("id")
    order_number = data_order.get("order_number")
    location = data_order.get("location")
    sn_imei = data_order.get("sn_imei")
    status = data_order.get("status")
    order_type = data_order.get("order_type")
    device_type = data_order.get("device_type")
    device_brand = data_order.get("device_brand")
    device_model = data_order.get("device_model")
    # equipment = data_order.get("equipment")
    # problem = data_order.get("problem")
    # appearance = data_order.get("appearance")
    created_date = data_order.get("created_date")
    diagnosis_before = data_order.get("diagnosis_before")
    cost_repair = data_order.get("cost_repair")
    cost_of_parts = data_order.get("cost_of_parts")
    cost_diagnostics = int(data_order.get("cost_diagnostics"))
    guarantee = data_order.get("guarantee")
    path_photo = data_order.get("guarantee")
    client_id = data_order.get("client_id")
    real_name_client = data_order.get("real_name_client")
    created_by = data_order.get("created_by")
    real_name_created = data_order.get("real_name_created")
    master = data_order.get("master")
    edit_history = data_order.get("edit_history")
    comments = data_order.get("comments")
    completed_works = data_order.get("completed_works")


    problem = data_order.get("problem")
    problem = json.loads(problem) if problem else ""
    problem = " • ".join(problem.copy())

    equipment = data_order.get("equipment")
    equipment = json.loads(equipment) if equipment else ""
    equipment = " • ".join(equipment.copy())

    appearance = data_order.get("appearance")
    appearance = json.loads(appearance) if appearance else ""
    appearance = " • ".join(appearance.copy())

    # Client:
    # username_telegram
    # phone

    # Master:
    # maser - имя когда принимает заказ
    # username_telegram

    # Manadger:
    # username_telegram


    order_data = {
        'order_number': data_order.get("order_number"),
        'order_type': data_order.get("order_type"),
        'status': data_order.get("status"),
        'real_name_client': data_order.get("real_name_client"),
        'client_phone': '79999544332',
        'device_type': remove_emojis(data_order.get("device_type")),
        'device_brand': data_order.get("device_brand"),
        'device_model': data_order.get("device_model"),
        'sn_imei': data_order.get("sn_imei"),
        'equipment': equipment,
        'appearance': appearance,
        'real_name_created': data_order.get("real_name_created"),
        'created_by': data_order.get("created_by"),
        'created_date': format_date_nice(data_order.get("created_date"), lang),
        'diagnosis_before': format_date_nice(data_order.get("diagnosis_before"), lang),
        'cost_diagnostics': int(data_order.get("cost_diagnostics")),
        'problem': problem,
        'comments': data_order.get("comments"),
        'master': data_order.get("master")
    }

    await message.answer(format_order_card(lang, **order_data), parse_mode="HTML")







######### START EDIT ##############
@router.message(Order.edit)
async def process_edit_order(message: types.Message, state: FSMContext):
    """  """
    await typing(message)
    state_data = await state.get_data()
    order_id = state_data.get("id")
    lang = message.from_user.language_code

    if message.text in (CHANGE_ORDER["order_ru"], CHANGE_ORDER["order_en"]):
        # Отдельный вызов редактирования заказа
        await start_edit_order(lang, order_id, state, message)
        await state.clear()
        return

    elif message.text == "👤 Клиент":
        await message.answer(f"Меняем данные клиента под заказом {order_id}")

    elif message.text == "📊 Статус":
        await message.answer(f"Меняем статус заказа {order_id}")

    else:
        if lang == "ru": await message.answer("🚫 Попробуйте еще раз выбрать пункт из меню")
        else: await message.answer("🚫 Try again to select an item from the menu")



################# START ACTION #############
@router.message(Order.action)
async def process_action_order(message: types.Message, state: FSMContext):
    """  """
    await typing(message)
    state_data = await state.get_data()
    order_id = state_data.get("id")
    lang = message.from_user.language_code

    if message.text == "📸 Фото":
        await message.answer(f"Фотав по заказу нэту {order_id}")
    elif message.text == "📄 PDF":
        await message.answer(f"Тута пдф по заказу {order_id}")
    elif message.text == "📤 Выдать заказ":
        await message.answer(f"Выдаем заказа - {order_id}")
    else:
        if lang == "ru": await message.answer("🚫 Попробуйте еще раз выбрать пункт из меню")
        else: await message.answer("🚫 Try again to select an item from the menu")

    #await state.clear()
    