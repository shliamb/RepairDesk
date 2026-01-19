#! app/utils/serialize.py
from datetime import datetime
from decimal import Decimal
import re


def json_serializer(obj):
    """Сериализатор для Decimal и datetime"""
    if isinstance(obj, Decimal):
        return str(obj)  # или float(obj) если допустимо
    elif isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f"Type {type(obj)} not serializable")


def custom_json_decoder(dct):
    for key, value in dct.items():
        if isinstance(value, str):
            # Для чисел (целых и дробных)
            if re.fullmatch(r'-?\d+(?:\.\d+)?', value):
                try:
                    dct[key] = Decimal(value)
                except:
                    pass
            # Для дат
            elif 'T' in value:
                try:
                    dct[key] = datetime.fromisoformat(value)
                except:
                    pass
    return dct


def datetime_parser(dct):
    """ На всякий.. Парсер для JSON, преобразует строки в datetime"""
    for key, value in dct.items():
        if isinstance(value, str):
            try:
                # Пробуем распарсить как datetime
                dct[key] = datetime.fromisoformat(value)
            except (ValueError, AttributeError):
                pass
    return dct
