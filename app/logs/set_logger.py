import logging
from config import TIME_CORRECTION, LOG_TO_FILE, PATH_LOGS
from pathlib import Path
from logging.handlers import RotatingFileHandler
import datetime



class TimezoneFormatter(logging.Formatter):
    """Форматтер с коррекцией времени"""
    def __init__(self, timezone_hours: int = 0, **kwargs):
        super().__init__(**kwargs)
        self.timezone_offset = datetime.timedelta(hours=timezone_hours)
    
    def formatTime(self, record, datefmt=None):
        dt = datetime.datetime.fromtimestamp(record.created, tz=datetime.timezone.utc)
        dt_local = dt + self.timezone_offset
        return dt_local.strftime(datefmt or '%Y-%m-%d %H:%M:%S')



def set_logger(
        name: str,
        log_to_file: bool = LOG_TO_FILE,
        timezone_hours: int = TIME_CORRECTION,
        log_dir: str = PATH_LOGS,
        level = logging.INFO,
        max_size_mb: int = 10
    ) -> logging.Logger:
    """Настройка логгера с коррекцией времени"""
    
    # Если не пишем в файл - включаем стандартные логи aiogram
    if not log_to_file:
        logging.getLogger("aiogram").setLevel(logging.INFO)
        return logging
    
    # Создаем директорию для логов
    log_path = Path(log_dir) / f"{name}.log"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Создаем логгер
    logger = logging.getLogger(name)
    logger.handlers.clear()
    logger.setLevel(level)
    
    # Файловый обработчик с ротацией
    file_handler = RotatingFileHandler(
        filename=str(log_path),
        maxBytes=max_size_mb * 1024 * 1024,
        backupCount=5,
        encoding='utf-8'
    )
    
    # Форматтер с коррекцией времени
    formatter = TimezoneFormatter(
        timezone_hours=timezone_hours,
        fmt='%(asctime)s [%(name)s] %(levelname)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(formatter)
    
    logger.addHandler(file_handler)
    return logger


























# import logging
# from config import TIME_CORRECTION, LOG_TO_FILE, PATH_LOGS
# # import os
# from pathlib import Path
# from typing import Optional, Dict
# from logging.handlers import RotatingFileHandler
# import threading
# import datetime

# # Глобальная блокировка для thread-safety
# _logger_lock = threading.Lock()
# _configured_loggers: Dict[str, logging.Logger] = {}
# _uvicorn_disabled = False


# class TimezoneFormatter(logging.Formatter):
#     """Форматтер с поддержкой временных зон"""

#     def __init__(self, *args, timezone_offset_hours: int = 0, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.timezone_offset = datetime.timedelta(hours=timezone_offset_hours)

#     def formatTime(self, record, datefmt=None):
#         # Получаем UTC время из record.created
#         dt = datetime.datetime.fromtimestamp(record.created, tz=datetime.timezone.utc)
#         # Применяем смещение
#         dt_local = dt + self.timezone_offset
#         # Форматируем
#         if datefmt:
#             return dt_local.strftime(datefmt)
#         else:
#             return dt_local.strftime('%Y-%m-%d %H:%M:%S')




# def set_logger(
#         name: str,
#         log_file: str = None,
#         level: int = logging.INFO,
#         format_string: str = '%(asctime)s [%(name)s] %(levelname)s: %(message)s',
#         max_bytes: int = 10 * 1024 * 1024,  # 10MB
#         backup_count: int = 5,
#         encoding: str = 'utf-8',
#         disable_uvicorn: bool = True,
#         timezone_offset_hours: int = TIME_CORRECTION  # Смещение в часах (например, +3 для MSK)
#     ) -> logging.Logger:
#     """
#     Настройка логгера с ротацией файлов и поддержкой временных зон.

#     Args:
#         timezone_offset_hours: Смещение времени в часах относительно UTC
#                               (например, 3 для MSK, -5 для EST)
#     """

#     log_file = f"{PATH_LOGS}{name}.log"

#     if not LOG_TO_FILE:
#         logging.getLogger("aiogram").setLevel(logging.INFO)
#         return logging


#     with _logger_lock:
#         # Проверяем cache
#         cache_key = f"{name}:{log_file}:{timezone_offset_hours}"
#         if cache_key in _configured_loggers:
#             return _configured_loggers[cache_key]

#         logger = logging.getLogger(name)

#         # Сбрасываем существующие хендлеры
#         logger.handlers.clear()
#         logger.setLevel(level)
#         logger.propagate = False

#         # Отключаем uvicorn один раз глобально
#         global _uvicorn_disabled
#         if disable_uvicorn and not _uvicorn_disabled:
#             _disable_uvicorn_logs()
#             _uvicorn_disabled = True

#         try:
#             # Создаем директорию
#             log_path = Path(log_file)
#             log_path.parent.mkdir(parents=True, exist_ok=True)

#             # Проверяем права на запись
#             if not _check_write_permissions(log_path.parent):
#                 raise OSError(f"Нет прав на запись в директорию: {log_path.parent}")

#             # Создаем хендлер с ротацией
#             file_handler = RotatingFileHandler(
#                 filename=str(log_path),
#                 maxBytes=max_bytes,
#                 backupCount=backup_count,
#                 encoding=encoding,
#                 delay=True
#             )

#             # Настраиваем форматтер с временной зоной
#             formatter = TimezoneFormatter(
#                 fmt=format_string,
#                 datefmt='%Y-%m-%d %H:%M:%S',
#                 timezone_offset_hours=timezone_offset_hours
#             )
#             file_handler.setFormatter(formatter)

#             # Добавляем хендлер
#             logger.addHandler(file_handler)

#             # Сохраняем в cache
#             _configured_loggers[cache_key] = logger

#             # Логируем успешную инициализацию
#             logger.info(
#                 f"Logger '{name}' initialized with UTC{timezone_offset_hours:+d} timezone. Log file: {log_file}")

#             return logger

#         except Exception as e:
#             # В случае ошибки создаем консольный логгер
#             console_handler = logging.StreamHandler()
#             console_formatter = TimezoneFormatter(
#                 format_string,
#                 timezone_offset_hours=timezone_offset_hours
#             )
#             console_handler.setFormatter(console_formatter)
#             logger.addHandler(console_handler)
#             logger.error(f"Failed to setup file logging for '{name}': {e}")
#             return logger


# def _disable_uvicorn_logs():
#     """Отключает стандартные uvicorn логи"""
#     uvicorn_loggers = ["uvicorn", "uvicorn.access", "uvicorn.error"]
#     for logger_name in uvicorn_loggers:
#         uvicorn_logger = logging.getLogger(logger_name)
#         uvicorn_logger.handlers.clear()
#         uvicorn_logger.propagate = False


# def _check_write_permissions(directory: Path) -> bool:
#     """Проверяет права на запись в директорию"""
#     try:
#         test_file = directory / ".write_test"
#         test_file.touch()
#         test_file.unlink()
#         return True
#     except (OSError, PermissionError):
#         return False
    








# def get_logger(name: str) -> Optional[logging.Logger]:
#     """Получить уже настроенный логгер по имени"""
#     with _logger_lock:
#         for key, logger in _configured_loggers.items():
#             if key.startswith(f"{name}:"):
#                 return logger
#     return None


# def list_configured_loggers() -> Dict[str, str]:
#     """Возвращает список всех настроенных логгеров"""
#     with _logger_lock:
#         return {
#             logger_name.split(':')[0]: logger_name.split(':')[1]
#             for logger_name in _configured_loggers.keys()
#         }


# def cleanup_loggers():
#     """Очищает все настроенные логгеры"""
#     with _logger_lock:
#         for logger in _configured_loggers.values():
#             for handler in logger.handlers:
#                 handler.close()
#             logger.handlers.clear()
#         _configured_loggers.clear()
#         global _uvicorn_disabled
#         _uvicorn_disabled = False


# # Контекстный менеджер для временного логгера
# class TemporaryLogger:
#     def __init__(self, name: str, log_file: str, **kwargs):
#         self.name = name
#         self.log_file = log_file
#         self.kwargs = kwargs
#         self.logger = None

#     def __enter__(self):
#         self.logger = set_logger(self.name, self.log_file, **self.kwargs)
#         return self.logger

#     def __exit__(self, exc_type, exc_val, exc_tb):
#         if self.logger:
#             for handler in self.logger.handlers:
#                 handler.close()
#             self.logger.handlers.clear()