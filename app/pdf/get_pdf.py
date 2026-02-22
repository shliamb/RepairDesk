from logs.set_logger import set_logger
logger = set_logger(name="get_pdf")
from aiogram import types
from aiogram.types import ReplyKeyboardRemove
from database.users import get_user_by_user_id
from database import db
from database.orders import OrderService
from pdf.gen_pdf import BuildPDF


order = OrderService(db)
pdf = BuildPDF()





async def gen_receipt(type_recept: str, order_id: int, lang: str, message: types.Message, data: dict) -> bool:
    """Генерация квитанции"""
    try:
        who_issued = data.get("who_issued")

        # GET DATA ORDER
        order_data = await order.get_order_id(order_id)
        if not order_data: return False
        order_data["lang"] = lang
        order_data["who_issued"] = who_issued

        # GET DATA CLIENT
        client_id = order_data.get("client_id")
        if not client_id: return False
        client_data = await get_user_by_user_id(client_id)
        order_data["phone"] = client_data.get("phone")

        # Build PDF file
        if type_recept == "in":
            path_pdf = pdf.get_order_pdf(order_data)

        elif type_recept == "out":
            path_pdf = pdf.get_order_out_pdf(order_data)

        if not path_pdf:
            if lang == "ru": await message.answer("🚫 При генерации PDF возникла проблема, извините. Попробуйте получить PDF документ снова, войдя в заказ.", reply_markup=ReplyKeyboardRemove())
            else: await message.answer("🚫 There was a problem when generating the PDF, sorry. Try to get the PDF document again by logging in to the order.", reply_markup=ReplyKeyboardRemove())
            return False

        # SEND PDF FILE
        send_text = "📄 Квитанция:" if lang == "ru" else "📄 Receipt:"
        await message.reply_document(
            document=types.input_file.FSInputFile(path_pdf),
            caption=send_text
        )
        return True
    
    except: return False