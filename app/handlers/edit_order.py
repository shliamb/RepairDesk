#! app/handlers/edit_order.py
from handlers.common import typing, is_manager
from logs.set_logger import set_logger
logger = set_logger(name="handlers")
from aiogram import Router, types, F
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import ReplyKeyboardRemove, InlineKeyboardMarkup, InlineKeyboardButton
# from aiogram.utils.keyboard import ReplyKeyboardBuilder, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext
from database.orders import OrderService
from config import CHANGE_ORDER, CURRENCY #, ORDER_STATUS_RU
from keyboards.workshop import build_keyboard
from database import db
from handlers.viewing_orders import Order
# from decimal import Decimal
# import asyncio
import json
from datetime import datetime



router = Router()
order = OrderService(db)






# Словари для локализации
ORDER_STATUS_RU = {
    'new': '🟢 Новый',
    'diagnosis': '🟡 Диагностика',
    'repair': '🟠 В ремонте',
    'testing': '🔵 Тестирование',
    'ready': '🟣 Готов к выдаче',
    'completed': '✅ Завершен',
    'cancelled': '❌ Отменен',
}

ORDER_STATUS_EN = {
    'new': '🟢 New',
    'diagnosis': '🟡 Diagnosis',
    'repair': '🟠 In repair',
    'testing': '🔵 Testing',
    'ready': '🟣 Ready for pickup',
    'completed': '✅ Completed',
    'cancelled': '❌ Cancelled',
}

def format_phone(phone):
    """Форматирует телефон в красивый вид: +7 (999) 954-43-32"""
    if not phone:
        return "Не указан"
    phone = str(phone).replace(" ", "").replace("-", "").replace("(", "").replace(")", "")
    if len(phone) == 11 and phone.startswith('8'):
        phone = '7' + phone[1:]
    if len(phone) == 11 and phone.startswith('7'):
        return f"+7 ({phone[1:4]}) {phone[4:7]}-{phone[7:9]}-{phone[9:]}"
    return phone

def format_order_card(lang="ru", **kwargs):
    """Форматирует карточку заказа"""
    
    if lang == "ru":
        status_dict = ORDER_STATUS_RU
        texts = {
            'order': '📋 ЗАКАЗ',
            'client': '👨‍💼 КЛИЕНТ',
            'device': '💻 УСТРОЙСТВО',
            'accepted': '📥 ПРИНЯЛ',
            'diagnosis': '⏱️ ДИАГНОСТИКА',
            'problem': '⚠️ ПРОБЛЕМА',
            'paid': '💸 Платный',
            'warranty': '🛡️ Гарантийный',
            'by': 'от',
            'until': 'до',
            'phone': '📱 Телефон'
        }
        currency = '₽'
    else:
        status_dict = ORDER_STATUS_EN
        texts = {
            'order': '📋 ORDER',
            'client': '👨‍💼 CLIENT',
            'device': '💻 DEVICE',
            'accepted': '📥 ACCEPTED BY',
            'diagnosis': '⏱️ DIAGNOSIS',
            'problem': '⚠️ PROBLEM',
            'paid': '💸 Paid',
            'warranty': '🛡️ Warranty',
            'by': 'by',
            'until': 'until',
            'phone': '📱 Phone'
        }
        currency = 'RUB'
    
    # Форматируем телефон
    formatted_phone = format_phone(kwargs.get('client_phone', ''))
    
    order_card = (
        f"<b>{texts['order']} {kwargs.get('order_number', '')}:</b>\n"
        f"        {texts['paid'] if kwargs.get('order_type') == 'paid' else texts['warranty']}\n"
        f"        {status_dict.get(kwargs.get('status', 'new'), '')}\n\n"
        
        f"<b>{texts['client']}:</b>\n"
        f"        {kwargs.get('real_name_client', '')}\n"
        f"        {texts['phone']}: {formatted_phone}\n\n"
        
        f"<b>{texts['device']}:</b>\n"
        f"        {kwargs.get('device_type', '')}\n"
        f"        {kwargs.get('device_brand', '')} • {kwargs.get('device_model', '')}\n"
        f"        📍 SN/IMEI: {kwargs.get('sn_imei', '')}\n\n"
        
        f"<b>{texts['accepted']}:</b>\n"
        f"        {texts['by']} {kwargs.get('real_name_created', '')}\n"
        f"        {kwargs.get('created_date', '')}\n"
        f"        👤 @{kwargs.get('created_by', '')}\n\n"
        
        f"<b>{texts['diagnosis']}:</b>\n"
        f"        {texts['until']} {kwargs.get('diagnosis_before', '')}\n"
        f"        💰 {kwargs.get('cost_diagnostics', 0)} {currency}\n\n"
        
        f"<b>{texts['problem']}:</b>\n"
        f"        🔧 {kwargs.get('problem', '')}\n"
    )
    
    # Добавляем примечание, если есть
    if kwargs.get('notes'):
        note_text = '📝 Примечание' if lang == 'ru' else '📝 Notes'
        order_card += f"\n<b>{note_text}:</b>\n        {kwargs.get('notes')}\n"
    
    return order_card

# Пример использования с улучшенными данными
def format_date_nice(dt_str, lang="ru"):
    """Преобразует дату из строки в красивый формат"""
    try:
        # Если dt_str уже datetime
        if hasattr(dt_str, 'strftime'):
            dt = dt_str
        else:
            # Парсим строку
            dt = datetime.strptime(dt_str, "%d.%m.%y %H:%M")
        
        if lang == "ru":
            months = {
                1: "января", 2: "февраля", 3: "марта", 4: "апреля",
                5: "мая", 6: "июня", 7: "июля", 8: "августа",
                9: "сентября", 10: "октября", 11: "ноября", 12: "декабря"
            }
            return f"{dt.day} {months[dt.month]} {dt.year}, {dt.strftime('%H:%M')}"
        else:
            months = {
                1: "January", 2: "February", 3: "March", 4: "April",
                5: "May", 6: "June", 7: "July", 8: "August",
                9: "September", 10: "October", 11: "November", 12: "December"
            }
            return f"{dt.strftime('%d')} {months[dt.month]} {dt.year}, {dt.strftime('%H:%M')}"
            
    except:
        return dt_str  # Возвращаем как есть, если ошибка













# SAVE ORDER TO DB
async def start_edit_order(lang: str, order_id: int, state: FSMContext, message: types.Message):
    """ Начало изменения данных заказа """

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
    equipment = data_order.get("equipment")
    problem = json.loads(data_order.get("problem")) if data_order.get("problem") else ""
    problem = ", ".join(problem.copy())
    appearance = data_order.get("device_brand")
    created_date = data_order.get("created_date")
    created_date = created_date.strftime("%d.%m.%y %H:%M")
    # completion_date = data_order.get("created_date")
    diagnosis_before = data_order.get("diagnosis_before")
    diagnosis_before = diagnosis_before.strftime("%d.%m.%y %H:%M")
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


    order_data_ru = {
        'order_number': 'GR-2026-0001',
        'order_type': 'paid',
        'status': 'diagnosis',
        'real_name_client': 'Пётр Иванов',
        'client_phone': '79999544332',
        'device_type': 'Ноутбук',
        'device_brand': 'ASUS',
        'device_model': 'ROG Strix G15',
        'sn_imei': 'SN1234567890',
        'real_name_created': 'Александр Петров',
        'created_by': 'alex_tech',
        'created_date': format_date_nice('14.01.26 21:21', 'ru'),
        'diagnosis_before': format_date_nice('16.01.26 21:21', 'ru'),
        'cost_diagnostics': '1 000',
        'problem': 'Не включается, черный экран, нет звука загрузки',
        'notes': 'Клиент просит сохранить данные'
    }


    # # Генерация карточек
    # print("RUSSIAN VERSION:")
    # print(format_order_card(lang="ru", **order_data_ru))






    # order_ru = (
    #         f'<b>📋 {order_number}:</b>\n'
    #         f'        {"Платный" if order_type == "paid" else "Гарантийный"}\n'
    #         f'        {ORDER_STATUS_RU[status]}\n\n'
    #         f'<b>👨‍💼 КЛИЕНТ:</b>\n'
    #         f'        {real_name_client}\n'
    #         f'        +7(999) 954-43-32\n\n'
    #         f'<b>{device_type}:</b>\n'
    #         f'        {sn_imei}\n'
    #         f'        {device_brand} • {device_model}\n\n'
    #         f'<b>📥 ПРИНЯЛ:</b>\n'
    #         f'        {created_date}\n'
    #         f'        {real_name_created}\n'
    #         f'        {created_by}\n\n'
    #         f'<b>⏱️ ДИАГНОСТИКА:</b>\n'
    #         f'        до {diagnosis_before}\n'
    #         f'        {cost_diagnostics} {CURRENCY}\n\n'
    #         f'<b>⚠️ ПРОБЛЕМА:</b>\n'
    #         f'        {problem}\n\n'
    #     )              

    # order_ru = (
    #     f'<b>📋 Заказ: {order_number}</b> {"🤑" if order_type == "paid" else "🤬"}\n\n'
    #     f'<b>📊 Статус заказа:</b> {status}\n'
    #     f'<b>🙋 {real_name_client}</b>\n'
    #     f'<b>{device_type}:</b> {device_brand} {device_model}\n'
    #     f'<b>👨‍💻 Принял:</b> {real_name_created} {created_date}\n'
    #     f'<b>⏰ Диагностика до:</b> {diagnosis_before}\n'
    #     f'<b>💰 Стоимость диагностики:</b> {cost_diagnostics} {CURRENCY}\n\n'
    #     f'<b>⚠️ Неисправность:</b> {problem}\n'
    # )

    order_en = (
        f'<b>📋 Order: {order_number}</b> {"🤑" if order_type == "paid" else "🤬"}\n\n'
        f'<b>📊 Order status:</b> {status}\n'
        f'<b>🙋 {real_name_client}</b>\n'
        f'<b>{device_type}:</b> {device_brand} {device_model}\n'
        f'<b>👨‍💻 Has accepted:</b> {real_name_created} {created_date}\n'
        f'<b>⏰ Diagnosis before:</b> {diagnosis_before}\n'
        f'<b>💰 The cost of diagnosis:</b> {cost_diagnostics} {CURRENCY}\n\n'
        f'<b>⚠️ Malfunction:</b> {problem}\n'
    )
    
    # keyboard = InlineKeyboardMarkup(inline_keyboard=[
    #     [
    #         InlineKeyboardButton(text=f'{VIEW_ORDER["change_ru"] if lang == "ru" else VIEW_ORDER["change_en"]}', callback_data=f"edit_order_{id}"),
    #         InlineKeyboardButton(text=f'{VIEW_ORDER["action_ru"] if lang == "ru" else VIEW_ORDER["action_en"]}', callback_data=f"action_order_{id}")
    #     ]
    # ])
    
    # if lang == "ru": await message.answer(order_ru, parse_mode="HTML", reply_markup=keyboard)
    # else: await message.answer(order_en, parse_mode="HTML", reply_markup=keyboard)

    if lang == "ru": await message.answer(format_order_card(lang="ru", **order_data_ru), parse_mode="HTML")
    else: await message.answer(order_en, parse_mode="HTML")





######### START EDIT ##############
@router.message(Order.edit)
async def process_edit_order(message: types.Message, state: FSMContext):
    """  """
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
    