#! keyboards/workshop.py python3
from aiogram.utils.keyboard import ReplyKeyboardBuilder, ReplyKeyboardMarkup, KeyboardButton


def build_keyboard(menu: list):
    builder = ReplyKeyboardBuilder()
    for point in menu:
        builder.button(text=point)
    builder.adjust(2)  # автоматически выравниваем
    return builder.as_markup(resize_keyboard=True, one_time_keyboard=False)
    



























    # def reception_menu(self):
    #     return ReplyKeyboardMarkup(
    #         keyboard=[
    #             [KeyboardButton(text="💻 Ноутбук"), KeyboardButton(text="🖥 ПК")],
    #             [KeyboardButton(text="📱 Телефон"), KeyboardButton(text="🖨 Принтер")],
    #             [KeyboardButton(text="✖️ Отмена")]
    #         ],
    #         resize_keyboard=True
    #     )
    