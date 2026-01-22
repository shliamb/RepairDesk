#! app/utils/serialize.py
from logs.set_logger import set_logger
logger = set_logger(name="serialize")
from datetime import datetime
from decimal import Decimal, InvalidOperation
from uuid import UUID
import re




def json_serializer(obj):
    """Сериализатор"""
    if isinstance(obj, Decimal):
        return str(obj)  # или float(obj) если допустимо
    
    elif isinstance(obj, datetime):
        return obj.isoformat()
    
    elif isinstance(obj, UUID):
        return str(obj)
    
    elif hasattr(obj, '__dict__'):  # Обрабатываем объекты с атрибутами
        return obj.__dict__
    
    raise TypeError(f"Type {type(obj)} not serializable")






def json_decoder(value):
    """Сериализатор"""
    if not isinstance(value, str):
        return value
    
    # UUID (проверяем формат, а не содержание строки)
    if re.fullmatch(r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}', value, re.IGNORECASE):
        try:
            return UUID(value)
        except (ValueError, AttributeError) as e:
            logger.warning(f"Failed to parse UUID for key '{value}': {e}")
            return value
    
    # Datetime (ISO 8601)
    if 'T' in value or re.match(r'\d{4}-\d{2}-\d{2}', value):
        try:
            return datetime.fromisoformat(value)
        except ValueError as e:
            logger.warning(f"Failed to parse datetime for key '{value}': {e}")
            return value
    
    # Числа (int/bigint/float/decimal)
    if re.fullmatch(r'-?\d+(?:\.\d+)?(?:[eE][+-]?\d+)?', value):
        try:
            # Если есть точка или экспонента -> Decimal, иначе int (поддержка BIGINT)
            if '.' in value or 'e' in value.lower():
                return Decimal(value)
            else:
                return int(value)
        except (InvalidOperation, ValueError) as e:
            logger.warning(f"Failed to parse number for key '{value}': {e}")
            return value




def custom_json_decoder(dct: dict):
    """Декодирует JSON с поддержкой Decimal, datetime, UUID, BIGINT, JSONB"""
    for key, value in dct.items():
        if not isinstance(value, str):
            continue
        
        # UUID (проверяем формат, а не содержание строки)
        if re.fullmatch(r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}', value, re.IGNORECASE):
            try:
                dct[key] = UUID(value)
                continue
            except (ValueError, AttributeError) as e:
                logger.warning(f"Failed to parse UUID for key '{key}': {e}")
        
        # Datetime (ISO 8601)
        if 'T' in value or re.match(r'\d{4}-\d{2}-\d{2}', value):
            try:
                dct[key] = datetime.fromisoformat(value)
                continue
            except ValueError as e:
                logger.warning(f"Failed to parse datetime for key '{key}': {e}")
        
        # Числа (int/bigint/float/decimal)
        if re.fullmatch(r'-?\d+(?:\.\d+)?(?:[eE][+-]?\d+)?', value):
            try:
                # Если есть точка или экспонента -> Decimal, иначе int (поддержка BIGINT)
                if '.' in value or 'e' in value.lower():
                    dct[key] = Decimal(value)
                else:
                    dct[key] = int(value)
                continue
            except (InvalidOperation, ValueError) as e:
                logger.warning(f"Failed to parse number for key '{key}': {e}")
    
    return dct







# def datetime_parser(dct):
#     """ На всякий.. Парсер для JSON, преобразует строки в datetime"""
#     for key, value in dct.items():
#         if isinstance(value, str):
#             try:
#                 # Пробуем распарсить как datetime
#                 dct[key] = datetime.fromisoformat(value)
#             except (ValueError, AttributeError):
#                 pass
#     return dct



# def custom_json_decoder(dct):
#     """Сериализатор декодер """
#     for key, value in dct.items():
#         if isinstance(value, str):

#             if re.fullmatch(r'-?\d+(?:\.\d+)?', value):
#                 try:
#                     dct[key] = Decimal(value)
#                 except:
#                     print("Error custom_json_decoder -> Decimal")

#             elif 'T' in value:
#                 try:
#                     dct[key] = datetime.fromisoformat(value)
#                 except:
#                     print("Error custom_json_decoder -> datetime")

#             elif 'uuid' in value:
#                 try:
#                     dct[key] = UUID(value)
#                 except:
#                     print("Error custom_json_decoder -> uuid")

#     return dct
