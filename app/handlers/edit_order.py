#! app/handlers/edit_order.py
from handlers.common import typing, is_manager
from logs.set_logger import set_logger
logger = set_logger(name="handlers")
from utils.formatters import remove_emojis, format_phone, format_date_nice
from database.users import get_user_by_user_id, get_user_by_tg
from utils.serialize import json_serializer, datetime_parser
from aiogram import Router, types, F
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import ReplyKeyboardRemove, InlineKeyboardMarkup, InlineKeyboardButton
# from aiogram.utils.keyboard import ReplyKeyboardBuilder, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext
from database.orders import OrderService
from config import DONE, CHANGE_ORDER, CURRENCY, DEVICE_ICO, ORDER_STATUS_COLOR, ORDER_STATUS_RU, ORDER_STATUS, EDIT_ORDER, CANCEL
from keyboards.workshop import build_keyboard
from database import db
from handlers.viewing_orders import Order # State из viewing_orders.py для перехода
# import asyncio
import json
from datetime import datetime



router = Router()
order = OrderService(db)


# states import from handlers/viewing_orders.py.py Order.edit and Order.action
class Edit(StatesGroup):
    order = State()
    status = State()
    diagnos = State()
    notes = State()








# SAVE DATA TO DB Сохранение в базу изменений и вывод заказа снова
async def edit_order_db(lang, data, state, message):
    """ Изменяю в базе и вызываю снова на экран заказ"""
    id = data.get("id")
    result = await order.edit_order(data)
    if not result:
        logger.error("Error in saving in the database")
        if lang == "ru": await message.answer("🚫 Ошибка в сохранении в базе")
        else: await message.answer("🚫 Error in saving in the database")
        return

    if lang == "ru": await message.answer("👍 Изменения сохранены", reply_markup=ReplyKeyboardRemove())
    else: await message.answer("👍 The changes are saved", reply_markup=ReplyKeyboardRemove())
    # Вывести заказ снова, что бы видно было что изменилось..
    await start_edit_order(lang, id, state, message)


# STATUS ORDER
@router.message(Edit.status)
async def choose_status(message: types.Message, state: FSMContext):
    """ Выбор статуса заказа """
    await typing(message)
    lang = message.from_user.language_code

    if message.text in list(ORDER_STATUS_RU.values()):
        # dict в котором меняем key и values, что бы вернуть ключь для базы:
        revers = {value: key for key, value in ORDER_STATUS_RU.items()}

    elif message.text in list(ORDER_STATUS.values()):
        revers = {value: key for key, value in ORDER_STATUS.items()}

    else:
        if lang == "ru": await message.answer("🚫 Попробуйте еще раз выбрать пункт из меню")
        else: await message.answer("🚫 Try again to select an item from the menu")
        return
        
    state_data = await state.get_data()
    data = {
        "id": state_data.get("id"),
        "status": revers[message.text]
    }
    await edit_order_db(lang, data, state, message)


# DIAGNOSTICS
@router.message(Edit.diagnos)
async def edit_diagnos(message: types.Message, state: FSMContext):
    """ Заполнение диагностики """
    await typing(message)
    lang = message.from_user.language_code

    if message.text:
        state_data = await state.get_data()
        await state.update_data(data={"id": state_data.get("id"), "diagnosis": message.text})
    
    else:
        if lang == "ru": await message.answer("🚫 Наберите текст диагностики")
        else: await message.answer("🚫 Type the diagnostic text")
        return

    state_data = await state.get_data()
    data = {
        "id": state_data.get("id"),
        "diagnosis": message.text
    }
    await edit_order_db(lang, data, state, message)


# NOTES / COMMENTS ORDER
@router.message(Edit.notes)
async def add_note(message: types.Message, state: FSMContext):
    """ Добавление заметки / комментария к заказу"""
    await typing(message)
    lang = message.from_user.language_code

    if not message.text:
        if lang == "ru": await message.answer("🚫 Наберите текст комментария")
        else: await message.answer("🚫 Type the comment text")
        return

    state_data = await state.get_data()
    id = state_data.get("id")
    data_order = await order.get_order_id(id)
    comments = data_order.get("comments", []) or []
    if comments: comments = json.loads(comments).copy()
    comments.append({"note": message.text, "date": datetime.now()})
    data = {
        "id": state_data.get("id"),
        "comments": json.dumps(comments, default=json_serializer, ensure_ascii=False)
    }
    await edit_order_db(lang, data, state, message)


# PUSH BUTTONS EDITION ORDER
@router.message(Edit.order)
async def choose_edit_order(message: types.Message, state: FSMContext):
    """ PUSH BUTTONS EDITION ORDER """
    await typing(message)
    lang = message.from_user.language_code

    # CHANGE STATUS ORDER
    if message.text in (EDIT_ORDER["stat_ru"], EDIT_ORDER["stat"]):
        if lang == "ru":
            buttons = list(ORDER_STATUS_RU.values())
            buttons.append(CANCEL["ru"])
            message_text = "📊 Выберите статус заказа:"
        else:
            buttons = list(ORDER_STATUS.values())
            buttons.append(CANCEL["en"])
            message_text = "📊 Select the order status:"

        await message.answer(message_text, reply_markup = build_keyboard(buttons))
        await state.set_state(Edit.status)

    # WRITE DIAGNOSTIC
    elif message.text in (EDIT_ORDER["dia_ru"], EDIT_ORDER["dia"]):
        buttons = []
        if lang == "ru":
            buttons.append(CANCEL["ru"])
            message_text = "📝 Напишите текст диагностики:"
        else:
            buttons.append(CANCEL["en"])
            message_text = "📝 Write the diagnostic text:"

        await message.answer(message_text, reply_markup = build_keyboard(buttons))
        await state.set_state(Edit.diagnos)

    # ADD COMMENTS
    elif message.text in (EDIT_ORDER["notes_ru"], EDIT_ORDER["notes"]):
        buttons = []
        if lang == "ru":
            buttons.append(CANCEL["ru"])
            message_text = "💬 Напишите комментарий к заказу:"
        else:
            buttons.append(CANCEL["en"])
            message_text = "💬 Write a comment on the order:"

        await message.answer(message_text, reply_markup = build_keyboard(buttons))
        await state.set_state(Edit.notes)

    # CLEAR PARTS AND WORK
    elif message.text in (EDIT_ORDER["clear_ru"], EDIT_ORDER["clear"]):
        
        state_data = await state.get_data()
        data = {
            "id": state_data.get("id"),
            "diagnosis": message.text
        }
        await edit_order_db(lang, data, state, message)


        # buttons = []
        # if lang == "ru":
        #     buttons.append(CANCEL["ru"])
        #     message_text = "💬 Напишите комментарий к заказу:"
        # else:
        #     buttons.append(CANCEL["en"])
        #     message_text = "💬 Write a comment on the order:"

        # await message.answer(message_text, reply_markup = build_keyboard(buttons))
        # await state.set_state(Edit.notes)


        #EDIT_ORDER["clear_ru"]

        


        # state_data = await state.get_data()
        # problem = state_data.get("problem", []).copy()
        # if message.text in problem:
        #     if lang == "ru": await message.answer("🚫 Вы уже добавили этот элемент")
        #     else: await message.answer("🚫 You have already added this element")
        #     return
        # problem.append(message.text)
        # await state.update_data(problem=problem)
        # return

    # elif message.text in (OWN_VERSION["ru"], OWN_VERSION["en"]):
    #     if lang == "ru": await message.answer("📝 Опишите заявленные проблемы/неисправности:")
    #     else: await message.answer("📝 Describe the stated problems/malfunctions:")
    #     await state.set_state(newOrder.other_problem)
    #     return

    # elif message.text in (DONE["ru"], DONE["en"]):
    #     state_data = await state.get_data()
    #     if not state_data.get("problem"):
    #         if lang == "ru": await message.answer("🚫 Выберите или опишите проблему, без этого будет трудно чинить:")
    #         else: await message.answer("🚫 Select or describe the problem, otherwise it will be difficult to fix:")
    #         return
    #     flag = True

    else:
        if lang == "ru": await message.answer("🚫 Попробуйте еще раз выбрать пункт из меню")
        else: await message.answer("🚫 Try again to select an item from the menu")
        return








#### UTILS OPEN FULL ORDER  ####
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
            'comments': '💬 Комментарии',


            'equipment': 'Комплектация',
            'appearance': 'Состояние',
            'paid': 'Платный',
            'warranty': 'Гарантийный',
            'by': 'от',
            'until': 'до',
            'phone': 'Телефон',
            'empty': 'Не указано',
            'tips': 'Чаевые'
        }

    else:
        device_ico = DEVICE_ICO
        order_status_color = ORDER_STATUS_COLOR
        status_dict = ORDER_STATUS
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
            'comments': '💬 Comments',

            'equipment': 'Equipment',
            'appearance': 'Appearance',
            'paid': 'Paid',
            'warranty': 'Warranty',
            'by': 'by',
            'until': 'until',
            'phone': 'Phone',
            'empty': 'Not specified',
            'tips': 'Tips'
        }
    





    # Сбор визуализации вывода заказа
    order_card = ""
    # Заказ номер:
    order_card += (
        f"<b>{texts['order']} {kwargs.get('order_number')}:</b>\n"
        "\n"
    )
    # Статус заказа, платный/гарантийный
    order_card += (
        f"<b>{order_status_color.get(kwargs.get('status'), '')} {texts['status']}:</b>\n"
        f"        {texts['paid'] if kwargs.get('order_type') == 'paid' else texts['warranty']}\n"
        f"        {status_dict.get(kwargs.get('status'), '')}\n"
        "\n"
    )
    # Инфа о клиенте:
    order_card += (
        f"<b>{texts['client']}:</b>\n"
        f"        {kwargs.get('real_name_client')}\n"
    )
    if kwargs.get('client_phone'):
        formatted_phone = format_phone(kwargs.get('client_phone'))
        order_card += f"        {formatted_phone or texts['empty']}\n"

    if kwargs.get('client_telegram'): order_card += f"        {kwargs.get('client_telegram')}\n"
    if kwargs.get('a_tip'): order_card += f"        {texts['tips']}: {kwargs.get('a_tip')}{CURRENCY}\n"
    order_card += "\n"

    # Инфа о устройстве:
    order_card += (
        f"<b>{device_ico.get(kwargs.get('device_type', ''))} {texts['device']}:</b>\n"
        f"        {kwargs.get('device_type') or texts['empty']}\n"
    )
    if kwargs.get('device_brand'): order_card += f"        {kwargs.get('device_brand')}"
    if kwargs.get('device_model'): order_card += f" • {kwargs.get('device_model')}"
    order_card += "\n"
    if kwargs.get('sn_imei'): order_card += f"        SN/IMEI: {kwargs.get('sn_imei')}\n"
    if kwargs.get('equipment'): order_card += f"        {texts['equipment']}: {kwargs.get('equipment')}\n"
    if kwargs.get('appearance'): order_card += f"        {texts['appearance']}: {kwargs.get('appearance')}\n"
    order_card += "\n"

    # Кто принял устройство:
    order_card += (
        f"<b>{texts['accepted']}:</b>\n"
        f"        {texts['by']} {kwargs.get('real_name_created')}\n"
        f"        {kwargs.get('created_date')}\n"
    )
    if kwargs.get('created_telegram'): order_card += f"        {kwargs.get('created_telegram')}\n"
    #f"        Комментарии: Очень спешил.\n\n"
    order_card += "\n"

    # Кто из мастеров взял заказ:
    if kwargs.get('real_name_master'):
        order_card += (
            f"<b>{texts['master']}:</b>\n"
            f"        {kwargs.get('real_name_master')}\n"
        )
        if kwargs.get('master_telegram'): order_card += f"        {kwargs.get('master_telegram')}\n"
        #f"        Комментарии: В пятницу доделаю, не давите бля!\n\n" # коммент от мастера
        order_card += "\n"

    # Диагностика до и цена
    order_card += (
        f"<b>{texts['diagnosis']}:</b>\n"
        f"        {texts['until']} {kwargs.get('diagnosis_before')}\n"
        f"        {kwargs.get('cost_diagnostics', 0)} {CURRENCY}\n"
    )
    order_card += "\n"

    # Описание проблемы устройства:
    order_card += (
        f"<b>{texts['problem']}:</b>\n"
        f"        {kwargs.get('problem')}\n"
    )
    order_card += "\n"

    # Комментарии по пунктам..
    comments = kwargs.get('comments')
    if comments:
        order_card += f"<b>{texts['comments']}:</b>\n"
        for one in comments:
            order_card += f"        <b>• {format_date_nice(one.get('date'), lang)}</b>: {one.get('note')}\n"
        order_card += "\n"

    # Результат диагностики:
    if kwargs.get('diagnosis'):
        order_card += (
            f"<b>{texts['diagnostic_result']}:</b>\n"
            f"        {kwargs.get('diagnosis') or texts['empty']}\n"
        )
        order_card += "\n"

    # Работы / Цены / Гарантии
    order_card += (
        f"<b>{texts['services']}:</b>\n"
        f"        1. Замена экрана  x1  2000{CURRENCY}  0\n\n"

        f"<b>{texts['parts']}:</b>\n"
        f"        1. Экран sn34334  x1  3500{CURRENCY}  3 мес.\n\n"

        f"----------------------------\n"

        f"<b>{texts['total']}:</b>\n"
        f"        <b>5500{CURRENCY}</b>\n\n"
    )
    
    return order_card






# START OPEN FULL ORDER
async def start_edit_order(lang: str, order_id: int, state: FSMContext, message: types.Message):
    """ Выводит заказ полностью и кнопки с редактированием """
    await typing(message)
    lang = message.from_user.language_code
    if not isinstance(order_id, int):
        logger.error(f"{id} is not digit")
        return
    
    await state.clear() # !!!!!
    
    data_order = await order.get_order_id(order_id)

    id = data_order.get("id")
    order_number = data_order.get("order_number")
    # location = data_order.get("location")
    # sn_imei = data_order.get("sn_imei")
    # status = data_order.get("status")
    # order_type = data_order.get("order_type")
    # device_type = data_order.get("device_type")
    # device_brand = data_order.get("device_brand")
    # device_model = data_order.get("device_model")
    # # equipment = data_order.get("equipment")
    # # problem = data_order.get("problem")
    # # appearance = data_order.get("appearance")
    # created_date = data_order.get("created_date")
    # diagnosis_before = data_order.get("diagnosis_before")
    # cost_repair = data_order.get("cost_repair")
    # cost_of_parts = data_order.get("cost_of_parts")
    # cost_diagnostics = int(data_order.get("cost_diagnostics"))
    # guarantee = data_order.get("guarantee")
    # path_photo = data_order.get("guarantee")
    # # client_id = data_order.get("client_id")
    # # created_by = data_order.get("created_by") # telegram id !!
    # # real_name_created = data_order.get("real_name_created")
    # # master = data_order.get("master")
    # edit_history = data_order.get("edit_history")
    # # comments = data_order.get("comments")
    # completed_works = data_order.get("completed_works")
    # diagnosis = data_order.get("diagnosis")
    # #a_tip = data_order.get("a_tip")


    problem = data_order.get("problem")
    problem = json.loads(problem) if problem else ""
    problem = " • ".join(problem.copy())

    equipment = data_order.get("equipment")
    equipment = json.loads(equipment) if equipment else ""
    equipment = " • ".join(equipment.copy())

    appearance = data_order.get("appearance")
    appearance = json.loads(appearance) if appearance else ""
    appearance = " • ".join(appearance.copy())

    # GET DATA CLIENT:
    client_uuid = data_order.get("client_id")
    data_client = await get_user_by_user_id(client_uuid)
    client_telegram = data_client.get("username_telegram")
    client_name = data_client.get("real_name") or data_client.get("name")
    client_phone = data_client.get("phone")

    # GET DATA MANAGER:
    created_by_telegram_id = data_order.get("created_by") # telegram id !!
    data_created = await get_user_by_tg(created_by_telegram_id)
    real_name_created = data_created.get("real_name_created") or data_created.get("name")
    created_telegram = data_created.get("username_telegram")
    if created_telegram: created_telegram = "@" + created_telegram

    # GET DATA MASTER:
    uuid_master = data_order.get("master") # UUID
    data_master = await get_user_by_user_id(uuid_master)
    real_name_master = data_master.get("real_name_created") or data_master.get("name")
    master_telegram = data_master.get("username_telegram")
    if master_telegram: master_telegram = "@" + master_telegram

    # COMMENTS:
    comments = data_order.get("comments", []) or []
    if comments: comments = json.loads(comments, object_hook=datetime_parser).copy() # из str -> в Json

    order_data = {
        'order_number': data_order.get("order_number"),
        'order_type': data_order.get("order_type"),
        'status': data_order.get("status"),
        'real_name_client': client_name,
        'client_phone': client_phone,
        'client_telegram': client_telegram,
        'device_type': remove_emojis(data_order.get("device_type")),
        'device_brand': data_order.get("device_brand"),
        'device_model': data_order.get("device_model"),
        'sn_imei': data_order.get("sn_imei"),
        'equipment': equipment,
        'appearance': appearance,
        'real_name_created': real_name_created,
        'created_telegram': created_telegram,
        'created_date': format_date_nice(data_order.get("created_date"), lang),
        'diagnosis_before': format_date_nice(data_order.get("diagnosis_before"), lang),
        'cost_diagnostics': int(data_order.get("cost_diagnostics")),
        'problem': problem,
        'comments': comments,
        'master': data_order.get("master"),
        'diagnosis': data_order.get("diagnosis"),
        'a_tip': data_order.get("a_tip"),
        'real_name_master': real_name_master,
        'master_telegram': master_telegram
    }

    await message.answer(format_order_card(lang, **order_data), parse_mode="HTML")
    if lang == "ru":
        message_text = "Выберите то, что хотите изменить:"

        buttons = [EDIT_ORDER["stat_ru"], EDIT_ORDER["dia_ru"], EDIT_ORDER["add_serv_ru"], EDIT_ORDER["add_part_ru"], EDIT_ORDER["notes_ru"], EDIT_ORDER["clear_ru"], CANCEL["ru"]]
    else:
        message_text = "Select what you want to change:"
        buttons = [EDIT_ORDER["stat"], EDIT_ORDER["dia"], EDIT_ORDER["add_serv"], EDIT_ORDER["add_part"], EDIT_ORDER["notes"], EDIT_ORDER["clear"], CANCEL["en"]]
    await message.answer(message_text, reply_markup = build_keyboard(buttons))

    await state.update_data(id=id, order_number=order_number)
    await state.set_state(Edit.order)







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
    



# # --- DEBUG TEST START ---
# @router.message()
# async def debug_any_message(message: types.Message, state: FSMContext):
#     current_state = await state.get_state()
#     print(f"!!! DEBUG: Роутер edit_order ЖИВ. Текущее состояние: {current_state}")
#     print(f"!!! DEBUG: Ожидаемое состояние: {Edit.order.state}")
# # --- DEBUG TEST END ---