#! handlers/statistics.py python3
from logs.set_logger import set_logger
logger = set_logger(name="handlers")
from handlers.common import typing, is_manager, is_super_admin
from database.users import add_user, get_user_by_tg, get_users_by_ids
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
    await typing(message)
    lang = message.from_user.language_code
    input_mes = message.text
    state_data = await state.get_data()
    data_orders = state_data.get("data_orders")
    period = state_data.get("period")
    monthly_data = state_data.get("monthly_data")
    yearly_data = state_data.get("yearly_data")

    text = ""
    if input_mes == UI_TEXTS[lang]['stats_revenue']:
        if period == "year" and monthly_data:
            monthly_result = calc_revenue_monthly(monthly_data)
            text = format_revenue_monthly(lang, monthly_result)
        elif period == "years" and yearly_data:
            yearly_result = calc_revenue_yearly(yearly_data)
            text = format_revenue_yearly(lang, yearly_result)
        else:
            total_payment, total_profit = calc_revenue(data_orders)
            text = format_revenue(lang, total_payment, total_profit)

    elif input_mes == UI_TEXTS[lang]['stats_orders_count']:
        if period == "year" and monthly_data:
            monthly_result = calc_orders_count_monthly(monthly_data)
            text = format_orders_count_monthly(lang, monthly_result)
        elif period == "years" and yearly_data:
            yearly_result = calc_orders_count_yearly(yearly_data)
            text = format_orders_count_yearly(lang, yearly_result)
        else:
            count = calc_orders_count(data_orders)
            text = format_orders_count(lang, count)

    elif input_mes == UI_TEXTS[lang]['stats_payment_methods']:
        stats = calc_payment_methods(data_orders)
        text = format_payment_methods(lang, stats)

    elif input_mes == UI_TEXTS[lang]['stats_by_master']:
        stats = await calc_by_master(data_orders)
        text = format_by_master(lang, stats)

    elif input_mes == UI_TEXTS[lang]['stats_by_device']:
        stats = calc_by_device(data_orders)
        text = format_by_device(lang, stats)

    elif input_mes == UI_TEXTS[lang]['back']:
        await run_statistics(message, state)

    else:
        if lang == "ru":
            await message.answer("🚫 Пожалуйста, выберите пункт из меню.")
        else:
            await message.answer("🚫 Please select an item from the menu.")
        return

    # Экранируем текст, чтобы избежать ошибок с HTML-сущностями
    if not text: return

    import html
    await message.answer(html.escape(text), parse_mode=None)



def calc_revenue(data_orders):
    """Общая сумма оплат и чистая прибыль"""
    total_payment = sum(order['payment_amount'] for order in data_orders)
    total_profit = sum(order['net_profit'] for order in data_orders)
    return total_payment, total_profit

def format_revenue(lang, total_payment, total_profit):
    if lang == "ru":
        return f"💰 Доход: {total_payment:.2f}\n📈 Прибыль: {total_profit:.2f}"
    else:
        return f"💰 Revenue: {total_payment:.2f}\n📈 Profit: {total_profit:.2f}"

def calc_orders_count(data_orders):
    return len(data_orders)

def format_orders_count(lang, count):
    if lang == "ru":
        return f"📦 Количество ремонтов: {count}"
    else:
        return f"📦 Repairs count: {count}"

def calc_payment_methods(data_orders):
    stats = {}
    for order in data_orders:
        method = order['payment_method']
        if method not in stats:
            stats[method] = {'count': 0, 'amount': 0}
        stats[method]['count'] += 1
        stats[method]['amount'] += order['payment_amount']
    return stats

def format_payment_methods(lang, stats):
    if not stats:
        return "Нет данных" if lang == "ru" else "No data"
    method_names = {
        'card': '💳 Карта',
        'cash': '💵 Наличные',
        'crypto': '₿ Крипта',
        'free': '🆓 Без оплаты'
    }
    lines = []
    if lang == "ru":
        lines.append("💳 По способам оплаты:")
        for method, data in stats.items():
            name = method_names.get(method, method)
            lines.append(f"{name}: {data['count']} шт, сумма {data['amount']:.2f}")
    else:
        lines.append("💳 By payment method:")
        for method, data in stats.items():
            name = method_names.get(method, method)
            lines.append(f"{name}: {data['count']} pcs, amount {data['amount']:.2f}")
    return "\n".join(lines)


async def calc_by_master(data_orders):
    master_ids = list({order['master_id'] for order in data_orders if order['master_id']})
    if not master_ids:
        return {}

    users_map = await get_users_by_ids(master_ids)
    name_map = {}
    for user_id, rec in users_map.items():
        name = rec.get('name', '')
        real_name = rec.get('real_name', '')
        full_name = f"{name} {real_name}".strip() or "Unknown"
        name_map[user_id] = full_name
    stats = {}
    for order in data_orders:
        mid = order['master_id']
        if not mid:
            continue
        name = name_map.get(mid, "Unknown")
        if name not in stats:
            stats[name] = {'count': 0, 'amount': 0}
        stats[name]['count'] += 1
        stats[name]['amount'] += order['payment_amount']
    return stats

def format_by_master(lang, stats):
    if not stats:
        return "Нет данных" if lang == "ru" else "No data"
    lines = []
    if lang == "ru":
        lines.append("👨‍🔧 По мастерам:")
        for name, data in stats.items():
            lines.append(f"{name}: {data['count']} ремонтов, сумма {data['amount']:.2f}")
    else:
        lines.append("👨‍🔧 By master:")
        for name, data in stats.items():
            lines.append(f"{name}: {data['count']} repairs, amount {data['amount']:.2f}")
    return "\n".join(lines)


def calc_by_device(data_orders):
    stats = {}
    for order in data_orders:
        device = order.get('device_type', 'unknown')
        if device not in stats:
            stats[device] = {'count': 0, 'amount': 0}
        stats[device]['count'] += 1
        stats[device]['amount'] += order['payment_amount']
    return stats

def format_by_device(lang, stats):
    if not stats:
        return "Нет данных" if lang == "ru" else "No data"
    lines = []
    if lang == "ru":
        lines.append("📱 По устройствам:")
        for device, data in stats.items():
            lines.append(f"{device}: {data['count']} ремонтов, сумма {data['amount']:.2f}")
    else:
        lines.append("📱 By device:")
        for device, data in stats.items():
            lines.append(f"{device}: {data['count']} repairs, amount {data['amount']:.2f}")
    return "\n".join(lines)

# ---------- Функции для месячной разбивки (только для года) ----------

def calc_revenue_monthly(monthly_data):
    """ monthly_data: dict month -> list[orders] """
    result = {}
    for month, orders in monthly_data.items():
        total_payment = sum(o['payment_amount'] for o in orders)
        total_profit = sum(o['net_profit'] for o in orders)
        result[month] = (total_payment, total_profit)
    return result

def format_revenue_monthly(lang, monthly_result):
    months_ru = ['Январь','Февраль','Март','Апрель','Май','Июнь','Июль','Август','Сентябрь','Октябрь','Ноябрь','Декабрь']
    months_en = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
    lines = []
    prev_payment = None
    for month in sorted(monthly_result.keys()):
        payment, profit = monthly_result[month]
        month_name = months_ru[month-1] if lang == 'ru' else months_en[month-1]
        if prev_payment is not None and prev_payment != 0:
            change = ((payment - prev_payment) / prev_payment) * 100
            change_str = f"{change:+.1f}%"
        else:
            change_str = "—"
        lines.append(f"{month_name}: доход {payment:.2f} ({change_str})")
        prev_payment = payment
    # Можно добавить итог за год
    total_payment = sum(p for p,_ in monthly_result.values())
    total_profit = sum(p for _,p in monthly_result.values())
    lines.append(f"\n💰 Итого за год: доход {total_payment:.2f}, прибыль {total_profit:.2f}")
    return "\n".join(lines)

def calc_orders_count_monthly(monthly_data):
    result = {}
    for month, orders in monthly_data.items():
        result[month] = len(orders)
    return result

def format_orders_count_monthly(lang, monthly_result):
    months_ru = ['Январь','Февраль','Март','Апрель','Май','Июнь','Июль','Август','Сентябрь','Октябрь','Ноябрь','Декабрь']
    months_en = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
    lines = []
    prev_count = None
    for month in sorted(monthly_result.keys()):
        count = monthly_result[month]
        month_name = months_ru[month-1] if lang == 'ru' else months_en[month-1]
        if prev_count is not None and prev_count != 0:
            change = ((count - prev_count) / prev_count) * 100
            change_str = f"{change:+.1f}%"
        else:
            change_str = "—"
        lines.append(f"{month_name}: {count} шт ({change_str})")
        prev_count = count
    total = sum(monthly_result.values())
    lines.append(f"\n📦 Всего за год: {total}")
    return "\n".join(lines)



def group_by_year(data_orders):
    """Группирует заказы по году из payment_date"""
    yearly = {}
    for order in data_orders:
        year = order['payment_date'].year
        if year not in yearly:
            yearly[year] = []
        yearly[year].append(order)
    return yearly

def calc_revenue_yearly(yearly_data):
    result = {}
    for year, orders in yearly_data.items():
        total_payment = sum(o['payment_amount'] for o in orders)
        total_profit = sum(o['net_profit'] for o in orders)
        result[year] = (total_payment, total_profit)
    return result

def format_revenue_yearly(lang, yearly_result):
    years = sorted(yearly_result.keys())
    lines = []
    prev_payment = None
    for year in years:
        payment, profit = yearly_result[year]
        if prev_payment is not None and prev_payment != 0:
            change = ((payment - prev_payment) / prev_payment) * 100
            change_str = f"{change:+.1f}%"
        else:
            change_str = "—"
        lines.append(f"{year}: доход {payment:.2f} ({change_str})")
        prev_payment = payment
    total_payment = sum(p for p,_ in yearly_result.values())
    total_profit = sum(p for _,p in yearly_result.values())
    lines.append(f"\n💰 Итого за все годы: доход {total_payment:.2f}, прибыль {total_profit:.2f}")
    return "\n".join(lines)

def calc_orders_count_yearly(yearly_data):
    result = {}
    for year, orders in yearly_data.items():
        result[year] = len(orders)
    return result

def format_orders_count_yearly(lang, yearly_result):
    years = sorted(yearly_result.keys())
    lines = []
    prev_count = None
    for year in years:
        count = yearly_result[year]
        if prev_count is not None and prev_count != 0:
            change = ((count - prev_count) / prev_count) * 100
            change_str = f"{change:+.1f}%"
        else:
            change_str = "—"
        lines.append(f"{year}: {count} шт ({change_str})")
        prev_count = count
    total = sum(yearly_result.values())
    lines.append(f"\n📦 Всего за все годы: {total}")
    return "\n".join(lines)






# GET STATISTICS PERIOD
@router.message(Statistic.period)
async def get_statistics(message: types.Message, state: FSMContext):
    await typing(message)
    lang = message.from_user.language_code
    input_mes = message.text

    if input_mes == UI_TEXTS[lang]["today"]: period = "today"
    elif input_mes == UI_TEXTS[lang]["month"]: period = "month"
    elif input_mes == UI_TEXTS[lang]["year"]: period = "year"
    elif input_mes == UI_TEXTS[lang]["years"]: period = "years"
    else:
        if lang == "ru": await message.answer("🚫 Попробуйте еще раз выбрать пункт из меню")
        else: await message.answer("🚫 Try again to select an item from the menu")
        return

    data_orders = await get_payments(period)
    if not data_orders:
        if lang == "ru": await message.answer("🌀 Нет результатов")
        else: await message.answer("🌀 No results")
        return

    monthly_data = None
    yearly_data = None
    if period == "year":
        monthly_data = {}
        for order in data_orders:
            month = order['payment_date'].month
            if month not in monthly_data:
                monthly_data[month] = []
            monthly_data[month].append(order)
    elif period == "years":
        yearly_data = group_by_year(data_orders)

    await state.update_data(data_orders=data_orders, period=period, 
                            monthly_data=monthly_data, yearly_data=yearly_data)

    buttons = [
        UI_TEXTS[lang]['stats_revenue'],
        UI_TEXTS[lang]['stats_orders_count'],
        UI_TEXTS[lang]['stats_payment_methods'],
        UI_TEXTS[lang]['stats_by_master'],
        UI_TEXTS[lang]['stats_by_device'],
        UI_TEXTS[lang]['back'],
        UI_TEXTS[lang]["cancel"]
    ]

    text = "Выберите фильтр:" if lang == "ru" else "Select a filter:"
    await message.answer(text, reply_markup=build_keyboard(buttons))
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
    await message.answer(text, reply_markup = build_keyboard([
        UI_TEXTS[lang]["today"], 
        UI_TEXTS[lang]["month"], 
        UI_TEXTS[lang]["year"], 
        UI_TEXTS[lang]["years"],
        UI_TEXTS[lang]["cancel"]
        ])) 
    
    await state.set_state(Statistic.period)
