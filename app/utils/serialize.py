#! app/utils/serialize.py
from datetime import datetime


def json_serializer(obj):
    """ Сериализовывает дату """
    if isinstance(obj, datetime):
        return obj.isoformat()  # "2024-01-15T12:30:45"
    raise TypeError(f"Type {type(obj)} not serializable")


def datetime_parser(dct):
    """Парсер для JSON, преобразует строки в datetime"""
    for key, value in dct.items():
        if isinstance(value, str):
            try:
                # Пробуем распарсить как datetime
                dct[key] = datetime.fromisoformat(value)
            except (ValueError, AttributeError):
                pass
    return dct