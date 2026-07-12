#! app/handlers/actions_order.py
from handlers.common import typing, is_manager
from logs.set_logger import set_logger
logger = set_logger(name="handlers")
from utils.formatters import safe_int, safe_decimal, safe_float
from database.users import get_user_by_user_id, get_user_by_tg, edit_client
from database.finstat import add_stat
from pdf.get_pdf import gen_receipt
from utils.parse import is_number
from aiogram import Router, types, F
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from database.orders import OrderService
from datetime import datetime
from config import UI_TEXTS, CURRENCY, ADMIN_ID, GET_FEEDBACK
from keyboards.workshop import build_keyboard
from handlers.workshop import workshop_panel
from database import db
from telethoner import mytelethon


router = Router()
order = OrderService(db)



class Action(StatesGroup):
    pay_method = State()
    receipt = State()



# # CANCEL STATE & KEYBOARD TO ALL HANDLERS !!!
# @router.message((F.text == UI_TEXTS["en"]["cancel"]) | (F.text == UI_TEXTS["ru"]["cancel"]))
# async def cancel(message: types.Message, state: FSMContext): 
#     """ Отмена / Cancelled """
#     await typing(message)
#     lang = message.from_user.language_code
#     await state.clear()
#     if lang == "ru": await message.answer("🚫 Отменено", reply_markup=ReplyKeyboardRemove())
#     else: await message.answer("🚫 Cancelled", reply_markup=ReplyKeyboardRemove())


# CANCEL STATE & KEYBOARD TO ALL HANDLERS !!!
@router.message((F.text == UI_TEXTS["en"]["cancel"]) | (F.text == UI_TEXTS["ru"]["cancel"]))
async def cancel(message: types.Message, state: FSMContext): 
    """ Отмена / Cancelled """
    await state.clear() # Очищаем состояние (если нужно при отмене)
    # Опционально: пишем, что действие отменено
    lang = message.from_user.language_code
    if lang == "ru": await message.answer("Действие отменено. Возвращаем вас в мастерскую...")
    else: await message.answer("Action canceled. Returning you to the workshop...")
    # Вызываем логику воркшопа, передавая текущие message и state
    await workshop_panel(message, state)





# START PAYD ORDER:
@router.message(Action.pay_method)
async def choosing_payment_method(message: types.Message, state: FSMContext):
    """ Выбор способа оплаты и все остальное..  """
    await typing(message)
    lang = message.from_user.language_code
    user_id = message.from_user.id
    input_text = message.text
    state_data = await state.get_data()

    metod_pay, amount, take, a_tip, order_id, status_order = state_data.get("metod_pay"), state_data.get("amount"), state_data.get("take"), state_data.get("a_tip"), state_data.get("id"), state_data.get("status")

    if metod_pay is None:
        if input_text == UI_TEXTS[lang]["no_payment"]:
            status_order = "issued_not_paid"
            metod_pay = "no_payment"
            amount = 0
            take = True
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
    completion_date = data_order.get("completion_date")
    if not status_order: status_order = data_order.get("status")
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

    # GET DATA FIN STATISTIC:
    data_user_issued = await get_user_by_tg(user_id)
    who_issued = data_user_issued.get("user_id")
    uuid_master = data_order.get("master")
    if not uuid_master:
        data_admin = await get_user_by_tg(ADMIN_ID)
        uuid_master = data_admin.get("user_id") # UUID MASTER

    fin_data = {
        "order_id": order_id,
        "client_id": client_id,
        "master_id": uuid_master,
        "payment_amount": safe_decimal(amount),
        "net_profit": safe_decimal(data_order.get("net_profit")),
        "payment_method": metod_pay,
        "payment_date": datetime.now(),
        "order_created_date": data_order.get("created_date"),
        "order_completed_date": completion_date or datetime.now(),
        "who_issued": who_issued,
        "device_type": data_order.get("device_type"),
        "device_model": data_order.get("device_model"),
        "repair_type": data_order.get("order_type")
    }

    # GET STATUS ORDER:
    if status_order == "issued":
        if lang == "ru": await message.answer("🚫 Заказ уже выдан", reply_markup=ReplyKeyboardRemove())
        else: await message.answer("🚫 The order has already been issued", reply_markup=ReplyKeyboardRemove())
        await state.clear()
        return

    elif status_order not in ("issued_not_paid", "cancelled", "unsuccessful_repair", "paid_not_issued"):
        if not take and metod_pay != UI_TEXTS[lang]["no_payment"] and amount != 0:
            status_order = "paid_not_issued"

        elif take and metod_pay != UI_TEXTS[lang]["no_payment"] and amount != 0:
            status_order = "issued"

    updata_order = {
        "id": order_id,
        "status": status_order,
        "master": uuid_master,
    }
    if not completion_date: updata_order["completion_date"] = datetime.now()

    # СДАЧА КЛИЕНТУ:
    total = None
    cost_repair = data_order.get("cost_repair") or 0
    cost_of_parts = data_order.get("cost_of_parts") or  0

    if status_order != "issued_not_paid":
        total = float(amount) - (float(cost_repair) + float(cost_of_parts) - float(data_order.get("cost_prepayment") or 0))

        if total < 0:
            if lang == "ru": await message.answer(f"🚫 Для оплаты не хватает {abs(total)} {CURRENCY}, попробуйте еще раз", reply_markup=ReplyKeyboardRemove())
            else: await message.answer(f"🚫 There is not enough money for payment {abs(total)} {CURRENCY}, please try again", reply_markup=ReplyKeyboardRemove())
            await state.clear()
            return 


    # UPDATE FIN STATISTIC:
    if not await add_stat(fin_data):
        if lang == "ru": await message.answer("🚫 Ошибка в обновлении финансовой транзакции")
        else: await message.answer("🚫 An error in updating a financial transaction")
        await state.clear()
        return

    # UPDATE ORDER:
    if not await order.edit_order(updata_order):
        if lang == "ru": await message.answer("🚫 Ошибка в обновлении данных заказа")
        else: await message.answer("🚫 Error in updating order data")
        await state.clear()
        return

    # UPDATE CLIENT DATA:
    if not await edit_client(updata_client):
        if lang == "ru": await message.answer("🚫 Ошибка в обновлении данных клиента")
        else: await message.answer("🚫 Error in updating client data")
        await state.clear()
        return

    if lang == "ru":
        text_over = "👍 Изменения сохранены"
        if total: text_over += f", сдача: {total} {CURRENCY}" 
    else:
        text_over = "👍 The changes are saved"
        if total: text_over += f", surplus: {total} {CURRENCY}" 

    await message.answer(text_over, reply_markup=ReplyKeyboardRemove())
    await state.update_data(id=None, metod_pay=None, amount=None, take=None, a_tip=None)
    await state.clear()



# GET PDF RECEIPT:
@router.message(Action.receipt)
async def get_choice_recept(message: types.Message, state: FSMContext):
    """ Генерация в зависимости от выбора  """
    await typing(message)
    lang = message.from_user.language_code
    user_id = message.from_user.id
    input_text = message.text
    state_data = await state.get_data()
    order_id = state_data.get("id")
    data = {}


    if input_text == UI_TEXTS[lang]["receipt_in"]:
        await gen_receipt("in", order_id, lang, message, data)

    if input_text == UI_TEXTS[lang]["receipt_out"]:
        data_user = await get_user_by_tg(user_id)
        who_issued = data_user.get("real_name") or data_user.get("name")
        data["who_issued"] = who_issued
        await gen_receipt("out", order_id, lang, message, data)



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
        if lang == "ru": text = "📄 Вариант документа:"
        else: text = "📄 Document option:"
        buttons = [UI_TEXTS[lang]["receipt_in"], UI_TEXTS[lang]["receipt_out"], UI_TEXTS[lang]["cancel"]] # UI_TEXTS[lang]["back"]
        await message.answer(text, reply_markup = build_keyboard(buttons))
        await state.set_state(Action.receipt)
        return
    
    elif action == "delet":
        if user_id != ADMIN_ID:
            if lang == "ru": await message.answer("🚫 У вас нет доступа. Обратитесь к супер администратору")
            else: await message.answer("🚫 You don't have access. Contact the super administrator")
            return

        result = await order.delete_order_cascade(order_id)
        if not result:
            if lang == "ru": await message.answer(" Ошибка в удалении заказа")
            else: await message.answer("🚫 Error in deleting an order")
            return
        else:
            if lang == "ru": await message.answer("👍 Заказ и его финансовые операции удалены", reply_markup=ReplyKeyboardRemove())
            else: await message.answer("👍 The order and its financial transactions have been deleted", reply_markup=ReplyKeyboardRemove())
            return

    elif action == "payd":
        # await state.update_data(order_id=order_id) Уже есть внутри id = order_id
        if lang == "ru": message_text = "💰 Выберите способ оплаты:"
        else: message_text = "💰 Select payment method:"
        buttons = [UI_TEXTS[lang]["card"], UI_TEXTS[lang]["cash"], UI_TEXTS[lang]["crypto"], UI_TEXTS[lang]["no_payment"],  UI_TEXTS[lang]["cancel"]]
        await message.answer(message_text, reply_markup = build_keyboard(buttons))
        await state.set_state(Action.pay_method)
        return

    elif action == "feedback":
        # Получаем данные заказа и клиента
        data_order = await order.get_order_id(order_id)
        client_id = data_order.get("client_id") # UUID клиента в вашей БД

        client_data = await get_user_by_user_id(client_id)
        username_telegram = client_data.get("username_telegram") # @username клиента
        
        # Безопасное получение telegram ID (чтобы не упасть в ошибку, если там None)
        tg_id_raw = data_order.get("user_telegram")
        user_telegram = int(tg_id_raw) if tg_id_raw and str(tg_id_raw).isdigit() else None

        # Если нет вообще никаких контактов для связи
        if not username_telegram and not user_telegram:
            if lang == "ru": 
                message_text = "❌ У клиента не указаны Telegram данные (ID или Юзернейм)."
            else: 
                message_text = "❌ Client has no Telegram data provided (ID or Username)."
            await message.answer(message_text)
            return

        # Формируем текст сообщения СЛУШАТЕЛЮ (клиенту) в зависимости от языка
        client_message = GET_FEEDBACK[lang]

        # Отправляем через Telethon (метод вернет int-ID при успехе или str-ошибку при неудаче)
        result = await mytelethon.send_message(
            message_text=client_message, 
            telegram_id=user_telegram, 
            username=username_telegram
        )

        # Если вернулся ID (число), значит отправка прошла успешно
        if isinstance(result, int):
            if lang == "ru":
                answer_message = "✅ Сообщение успешно отправлено. Telegram ID клиента сохранен/обновлен."
            else:
                answer_message = "✅ Message sent successfully. Client Telegram ID saved/updated."

            # Обновляем ID клиента в базе данных, если его там не было или он изменился
            new_data_client = {"user_id": client_id, "user_telegram": result}
            if not await edit_client(new_data_client):
                if lang == "ru":
                    await message.answer("⚠️ Ошибка при сохранении Telegram ID в базу данных.")
                else:
                    await message.answer("⚠️ Error saving Telegram ID to the database.")
                return
        else:
            # Если вернулась строка — это текст ошибки из Telethon (уже локализованный там)
            answer_message = str(result)

        # Отвечаем мастеру в боте о результате операции
        await message.answer(answer_message)
        return