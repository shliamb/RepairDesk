#! app/pdf/gen_pdf,py
# pip install fpdf2
from fpdf import FPDF
from datetime import datetime
from logs.set_logger import set_logger
logger = set_logger(name="pdf")
from utils.formatters import remove_emojis, format_phone, format_date_nice
from config import CONDITIONS, CONDITIONS_OF_ISSUE, ADRES, SITE, CURRENCY
import json



# Тут надо все переписать, повторения и сдамия!!!!!!


class BuildPDF():
    """ Генерация PDF файла """
    def __init__(self):
        # В __init__ оставляем ТОЛЬКО неизменяемые настройки.
        # Сам объект self.pdf здесь создавать НЕЛЬЗЯ, если класс живет долго.
        self.logo_path = "app/pdf/img/logo.jpeg"
        self.path_save_pdf = "./app/pdf/out_files"
        self.conditions = CONDITIONS
        self.conditions_of_issue = CONDITIONS_OF_ISSUE
        self.currency = CURRENCY
        self.adres = ADRES
        self.site = SITE
        self.pdf = None # Будет создан перед генерацией

    def _init_pdf_engine(self):
        """ Создаем ЧИСТЫЙ экземпляр PDF и шрифты для каждого нового файла """
        self.pdf = FPDF()
        self.pdf.add_page()
        self.pdf.set_margins(10, 10, 10)
        self.pdf.set_auto_page_break(True, 10)
        
        # Шрифты нужно загружать каждый раз для нового экземпляра FPDF
        self.pdf.add_font('DejaVu', '', 'app/pdf/font/DejaVuSans.ttf')
        self.pdf.add_font('DejaVu', 'B', 'app/pdf/font/DejaVuSans-Bold.ttf')
        self.pdf.add_font('DejaVu', 'I', 'app/pdf/font/DejaVuSans-Oblique.ttf')
        self.pdf.add_font('DejaVu', 'BI', 'app/pdf/font/DejaVuSans-BoldOblique.ttf')
        self.pdf.set_font('DejaVu', '', 10)

    def _get_self_data(self, data_pdf: dict) -> None:
        """ Парсинг данных """
        if not data_pdf:
            logger.error("Пустой data_pdf")
            return

        self.lang = data_pdf.get("lang", "en")
        self.order_number = data_pdf.get("order_number")
        self.sn_imei = data_pdf.get("sn_imei")
        self.order_type = data_pdf.get("order_type")
        self.device_type = remove_emojis(data_pdf.get("device_type")) if data_pdf.get("device_type") else ""
        self.device_brand = data_pdf.get("device_brand", "")
        self.device_model = data_pdf.get("device_model", "")

        # Безопасная обработка JSON списков
        self.equipment = self._safe_json_load(data_pdf.get("equipment"))
        self.problem = self._safe_json_load(data_pdf.get("problem"))
        self.appearance = self._safe_json_load(data_pdf.get("appearance"))
        
        # Дата диагностики
        diagnosis_before = data_pdf.get("diagnosis_before")
        self.diagnosis_before = diagnosis_before.strftime("%d.%m.%y %H:%M") if diagnosis_before else "—"

        self.cost_diagnostics = data_pdf.get("cost_diagnostics", "0")
        self.name_client = data_pdf.get("real_name_client", "")
        self.phone_client = data_pdf.get("phone", "")
        self.created_by = data_pdf.get("real_name_created", "")

        # Формирование словарей
        self.order_data_ru = {
            'Клиент': self.name_client,
            'Телефон': format_phone(self.phone_client),
            'Марка/модель': f'{self.device_type} {self.device_brand} ({self.device_model})',
            'SN/imei': self.sn_imei,
            'Комплектация': self.equipment,
            'Внешний вид': self.appearance,
            'Причина обращения': self.problem,
            'Стоимость диагностики': f'{self.cost_diagnostics} {self.currency}',
            'Примерная дата готовности': self.diagnosis_before
        }
        
        self.order_data_en = {
            'Name': self.name_client,
            'Phone': format_phone(self.phone_client),
            'Brand/Model': f'{self.device_type} {self.device_brand} ({self.device_model})',
            'SN/imei': self.sn_imei,
            'Equipment': self.equipment,
            'Device appearance': self.appearance,
            'Problems': self.problem,
            'The cost of diagnosis': f'{self.cost_diagnostics} {self.currency}',
            'Approximate date ready': self.diagnosis_before
        }

    def _safe_json_load(self, json_str):
        """ Вспомогательный метод для безопасного парсинга списков """
        if not json_str:
            return "—"
        try:
            data = json.loads(json_str)
            if isinstance(data, list):
                return ", ".join(data)
            return str(data)
        except Exception:
            return str(json_str)

    @staticmethod
    def _get_date() -> str:
        return datetime.now().strftime("%d.%m.%Y")

    def save_file_pdf(self) -> str:
        name = self.order_number
        full_path = f"{self.path_save_pdf}/{name}.pdf"
        # ЭТО ФИНАЛЬНЫЙ АККОРД. После этого self.pdf МЕРТВ.
        self.pdf.output(full_path)
        return full_path
    
    def add_header(self) -> None:
        current_y = self.pdf.get_y()
        try:
            self.pdf.image(self.logo_path, x=10, y=current_y, w=15)
        except: pass

        self.pdf.set_font('DejaVu', '', 10)
        self.pdf.set_x(25)
        self.pdf.cell(0, 10, self.adres)
        self.pdf.ln(3)
        self.pdf.set_x(25)
        self.pdf.set_font('DejaVu', 'B', 10)
        self.pdf.cell(0, 15, self.site)
        self.pdf.ln(7)
        self.pdf.set_font('DejaVu', 'BI', 14)
        
        title = f'Квитанция {self.order_number}' if self.lang == 'ru' else f'Receipt {self.order_number}'
        self.pdf.cell(self.pdf.get_string_width(title), 15, title)
        
        start_x = self.pdf.get_x()
        self.pdf.set_font('DejaVu', 'I', 10)
        date_txt = f' от {self._get_date()}' if self.lang == 'ru' else f' from {self._get_date()}'
        self.pdf.cell(0, 16, date_txt)
        
        self.pdf.set_x(start_x)
        self.pdf.ln(12)
        self.pdf.line(10, self.pdf.get_y(), 200, self.pdf.get_y())
        self.pdf.ln(2)

    def add_order_data(self) -> None:
        data = self.order_data_ru if self.lang == "ru" else self.order_data_en
        for key, value in data.items():
            self.pdf.set_font('DejaVu', 'B', 9)
            k_txt = f'{key}: '
            self.pdf.cell(self.pdf.get_string_width(k_txt), 3, k_txt)
            
            self.pdf.set_font('DejaVu', '', 9)
            self.pdf.multi_cell(0, 3, str(value) if value else '—')
            self.pdf.ln(1)
        self.pdf.ln(2)

    def add_conditions(self) -> None:
        self.pdf.set_font('DejaVu', 'I', 7)
        txt = self.conditions["ru"] if self.lang == "ru" else self.conditions["en"]
        self.pdf.multi_cell(190, 3, txt)
        self.pdf.ln(1)

    def add_signature(self):
        self.pdf.set_font('DejaVu', '', 10)
        acc_txt = f'Принял: ___________ / {self.created_by}' if self.lang == "ru" else f'Accepted: ___________ / {self.created_by}'
        self.pdf.cell(70, 6, acc_txt)
        
        self.pdf.set_x(140)
        self.pdf.cell(50, 6, f'__________ / {self.name_client}')
        self.pdf.ln(3)
        
        self.pdf.set_font('DejaVu', '', 7)
        self.pdf.set_x(140)
        agr_txt = 'с условиями ознакомлен и согласен' if self.lang == "ru" else 'read and agree to terms'
        self.pdf.cell(50, 10, agr_txt)
        self.pdf.ln(10)

    def _draw_receipt_body(self):
        self.add_header()
        self.add_order_data()
        self.add_conditions()
        self.add_signature()

    def _add_cut_line(self):
        y = self.pdf.get_y()
        self.pdf.set_draw_color(100, 100, 100)
        self.pdf.line(0, y, 210, y)
        self.pdf.set_y(y)
        self.pdf.set_font('DejaVu', 'I', 8)
        self.pdf.cell(0, 4, '- - - Cut here / Линия отреза - - -', align='C')
        self.pdf.ln(5)
        self.pdf.set_draw_color(0)


    def get_order_pdf(self, data_pdf: dict) -> str:
        """ Главный метод генерируем квитанцию приема устройства"""
        self._get_self_data(data_pdf)
        
        # КЛЮЧЕВОЕ ИСПРАВЛЕНИЕ: Создаем PDF здесь, перед началом работы с документом
        self._init_pdf_engine() 
        
        # Рисуем контент
        self._draw_receipt_body()
        self._add_cut_line()
        self._draw_receipt_body()
        
        # Сохраняем и закрываем
        return self.save_file_pdf()
    




    # КВИТАНЦИЯ ВЫДАЧИ УСТРОЙСТВА:


    def _get_self_data_out(self, data_pdf: dict) -> None:
        """ Парсинг данных """
        if not data_pdf:
            logger.error("Пустой data_pdf")
            return

        self.lang = data_pdf.get("lang", "en")
        self.order_number = data_pdf.get("order_number")
        self.sn_imei = data_pdf.get("sn_imei")
        self.order_type = data_pdf.get("order_type")
        self.device_type = remove_emojis(data_pdf.get("device_type")) if data_pdf.get("device_type") else ""
        self.device_brand = data_pdf.get("device_brand", "")
        self.device_model = data_pdf.get("device_model", "")

        # Безопасная обработка JSON списков
        self.equipment = self._safe_json_load(data_pdf.get("equipment"))
        self.problem = self._safe_json_load(data_pdf.get("problem"))
        self.appearance = self._safe_json_load(data_pdf.get("appearance"))

        self.name_client = data_pdf.get("real_name_client", "")
        self.phone_client = data_pdf.get("phone", "")
        self.who_issued = data_pdf.get("who_issued", "")

        # Формирование словарей
        self.order_out_data_ru = {
            'Клиент': self.name_client,
            'Телефон': format_phone(self.phone_client),
            'Марка/модель': f'{self.device_type} {self.device_brand} ({self.device_model})',
            'SN/imei': self.sn_imei,
            'Комплектация': self.equipment,
            'Внешний вид': self.appearance,
            'Причина обращения': self.problem,
        }
        
        self.order_out_data_en = {
            'Name': self.name_client,
            'Phone': format_phone(self.phone_client),
            'Brand/Model': f'{self.device_type} {self.device_brand} ({self.device_model})',
            'SN/imei': self.sn_imei,
            'Equipment': self.equipment,
            'Device appearance': self.appearance,
            'Problems': self.problem,
        }




    def add_header_out(self) -> None:
        current_y = self.pdf.get_y()
        try:
            self.pdf.image(self.logo_path, x=10, y=current_y, w=15)
        except: pass

        self.pdf.set_font('DejaVu', '', 10)
        self.pdf.set_x(25)
        self.pdf.cell(0, 10, self.adres)
        self.pdf.ln(3)
        self.pdf.set_x(25)
        self.pdf.set_font('DejaVu', 'B', 10)
        self.pdf.cell(0, 15, self.site)
        self.pdf.ln(7)
        self.pdf.set_font('DejaVu', 'BI', 14)
        
        title = f'Акт выполненных работ {self.order_number}' if self.lang == 'ru' else f'The act of completed works {self.order_number}'
        self.pdf.cell(self.pdf.get_string_width(title), 15, title)
        
        start_x = self.pdf.get_x()
        self.pdf.set_font('DejaVu', 'I', 10)
        date_txt = f' от {self._get_date()}' if self.lang == 'ru' else f' from {self._get_date()}'
        self.pdf.cell(0, 16, date_txt)
        
        self.pdf.set_x(start_x)
        self.pdf.ln(12)
        self.pdf.line(10, self.pdf.get_y(), 200, self.pdf.get_y())
        self.pdf.ln(2)


    def add_order_data_out(self) -> None:
        data = self.order_out_data_ru if self.lang == "ru" else self.order_out_data_en
        for key, value in data.items():
            self.pdf.set_font('DejaVu', 'B', 9)
            k_txt = f'{key}: '
            self.pdf.cell(self.pdf.get_string_width(k_txt), 3, k_txt)
            
            self.pdf.set_font('DejaVu', '', 9)
            self.pdf.multi_cell(0, 3, str(value) if value else '—')
            self.pdf.ln(1)
        self.pdf.ln(2)


    def add_conditions_out(self) -> None:
        self.pdf.set_font('DejaVu', 'I', 7)
        txt = self.conditions_of_issue["ru"] if self.lang == "ru" else self.conditions_of_issue["en"]
        self.pdf.multi_cell(190, 3, txt)
        self.pdf.ln(1)


    def add_signature_out(self):
        self.pdf.set_font('DejaVu', '', 10)
        acc_txt = f'Выдал: ___________ / {self.who_issued}' if self.lang == "ru" else f'Issued: ___________ / {self.who_issued}'
        self.pdf.cell(70, 6, acc_txt)
        
        self.pdf.set_x(140)
        self.pdf.cell(50, 6, f'__________ / {self.name_client}')
        self.pdf.ln(3)
        
        self.pdf.set_font('DejaVu', '', 7)
        self.pdf.set_x(140)
        agr_txt = 'с условиями ознакомлен и согласен' if self.lang == "ru" else 'read and agree to terms'
        self.pdf.cell(50, 10, agr_txt)
        self.pdf.ln(10)


    def _draw_receipt_body_out(self):
        self.add_header_out()
        self.add_order_data_out()




    def add_services_list(self, services, parts):
        """ Пронумерованный список услуг и запчастей """
        
        # Преобразуем строки в списки
        try:
            services = json.loads(services) if services else []
            parts = json.loads(parts) if parts else []
        except:
            services = []
            parts = []
        
        self.pdf.set_font('DejaVu', '', 9)
        i, j = 1, 1
        sum_serv, sum_part = 0, 0
        
        # Работы
        if services:
            self.pdf.set_font('DejaVu', 'B', 9)
            self.pdf.cell(0, 8, "Работы:", 0, 1, "L")
            self.pdf.set_font('DejaVu', '', 9)
            
            for item in services:
                work = item.get("work", "—")
                pieces = item.get('pieces', '1')
                price = item.get('price', '0')
                warranty = item.get('warranty_period', '0')
                
                text = f"{i}. {work} - {price}{self.currency} - {pieces}шт. - {warranty}мес."
                
                self.pdf.set_x(10)
                self.pdf.multi_cell(0, 5, text)
                
                sum_serv += float(price) * int(pieces)
                i += 1
            
            self.pdf.ln(2)
        
        # Запчасти
        if parts:
            self.pdf.set_font('DejaVu', 'B', 9)
            self.pdf.cell(0, 8, "Запчасти:", 0, 1, "L")
            self.pdf.set_font('DejaVu', '', 9)
            
            for item in parts:
                part = item.get("part", "—")
                pieces = item.get('pieces', '1')
                price = item.get('price', '0')
                warranty = item.get('warranty_period', '0')
                
                text = f"{j}. {part} - {price}{self.currency} - {pieces}шт. - {warranty}мес."
                
                self.pdf.set_x(10)
                self.pdf.multi_cell(0, 5, text)
                
                sum_part += float(price) * int(pieces)
                j += 1
            
            self.pdf.ln(2)
        
        # Итог
        if services or parts:
            self.pdf.ln(3)
            self.pdf.set_font('DejaVu', 'B', 10)
            total = sum_serv + sum_part
            total_str = f"{total:,.2f}".replace(',', ' ').replace('.', ',')
            self.pdf.cell(0, 6, f"ИТОГО: {total_str} {self.currency}", 0, 1)



    def get_order_out_pdf(self, data_pdf: dict) -> str:
        self._get_self_data_out(data_pdf)
        self._init_pdf_engine()

        self._draw_receipt_body_out()

        services = data_pdf.get('services', [])
        parts = data_pdf.get('parts', [])
        if services:
            self.add_services_list(services, parts) 

        self.add_conditions_out()
        self.add_signature_out()

        return self.save_file_pdf()
        








#################################


# from fpdf import FPDF
# from datetime import datetime
# from dataclasses import dataclass, field
# from typing import Dict, List, Optional, Any
# from enum import Enum
# import json

# from logs.set_logger import set_logger
# from utils.formatters import remove_emojis, format_phone
# from config import CONDITIONS, CONDITIONS_OF_ISSUE, ADRES, SITE, CURRENCY

# logger = set_logger(name="pdf")


# class ReceiptType(Enum):
#     INTAKE = "intake"  # Прием
#     ISSUE = "issue"    # Выдача


# @dataclass
# class OrderData:
#     """Данные заказа с валидацией"""
#     lang: str = "en"
#     order_number: str = ""
#     sn_imei: str = ""
#     device_type: str = ""
#     device_brand: str = ""
#     device_model: str = ""
#     equipment: List[str] = field(default_factory=list)
#     problem: List[str] = field(default_factory=list)
#     appearance: List[str] = field(default_factory=list)
#     name_client: str = ""
#     phone_client: str = ""
#     created_by: str = ""
#     who_issued: str = ""
#     diagnosis_before: Optional[datetime] = None
#     cost_diagnostics: str = "0"
#     services: List[Dict] = field(default_factory=list)
#     parts: List[Dict] = field(default_factory=list)
    
#     @classmethod
#     def from_dict(cls, data: Dict[str, Any]) -> "OrderData":
#         """Безопасное создание из словаря"""
#         return cls(
#             lang=data.get("lang", "en"),
#             order_number=data.get("order_number", ""),
#             sn_imei=data.get("sn_imei", ""),
#             device_type=remove_emojis(data.get("device_type", "")),
#             device_brand=data.get("device_brand", ""),
#             device_model=data.get("device_model", ""),
#             equipment=cls._parse_json_list(data.get("equipment")),
#             problem=cls._parse_json_list(data.get("problem")),
#             appearance=cls._parse_json_list(data.get("appearance")),
#             name_client=data.get("real_name_client", ""),
#             phone_client=data.get("phone", ""),
#             created_by=data.get("real_name_created", ""),
#             who_issued=data.get("who_issued", ""),
#             diagnosis_before=data.get("diagnosis_before"),
#             cost_diagnostics=str(data.get("cost_diagnostics", "0")),
#             services=cls._parse_json_list(data.get("services")),
#             parts=cls._parse_json_list(data.get("parts"))
#         )
    
#     @staticmethod
#     def _parse_json_list(value: Any) -> List:
#         """Безопасный парсинг JSON списков"""
#         if not value:
#             return []
#         if isinstance(value, list):
#             return value
#         try:
#             parsed = json.loads(value)
#             return parsed if isinstance(parsed, list) else [str(parsed)]
#         except:
#             return [str(value)]
    
#     def get_device_full_name(self) -> str:
#         """Полное название устройства"""
#         return f"{self.device_type} {self.device_brand} ({self.device_model})".strip()
    
#     def get_formatted_phone(self) -> str:
#         """Отформатированный телефон"""
#         return format_phone(self.phone_client)
    
#     def get_diagnosis_date(self) -> str:
#         """Дата диагностики"""
#         if self.diagnosis_before:
#             return self.diagnosis_before.strftime("%d.%m.%y %H:%M")
#         return "—"


# class PDFBuilder:
#     """Построитель PDF с минимальным состоянием"""
    
#     def __init__(self):
#         self.logo_path = "app/pdf/img/logo.jpeg"
#         self.font_paths = {
#             'regular': 'app/pdf/font/DejaVuSans.ttf',
#             'bold': 'app/pdf/font/DejaVuSans-Bold.ttf',
#             'italic': 'app/pdf/font/DejaVuSans-Oblique.ttf',
#             'bold_italic': 'app/pdf/font/DejaVuSans-BoldOblique.ttf'
#         }
#         self.pdf: Optional[FPDF] = None
        
#     def _create_pdf(self) -> FPDF:
#         """Создает новый экземпляр PDF"""
#         pdf = FPDF()
#         pdf.add_page()
#         pdf.set_margins(10, 10, 10)
#         pdf.set_auto_page_break(True, 10)
        
#         # Добавляем шрифты
#         pdf.add_font('DejaVu', '', self.font_paths['regular'])
#         pdf.add_font('DejaVu', 'B', self.font_paths['bold'])
#         pdf.add_font('DejaVu', 'I', self.font_paths['italic'])
#         pdf.add_font('DejaVu', 'BI', self.font_paths['bold_italic'])
#         pdf.set_font('DejaVu', '', 10)
        
#         return pdf
    
#     def _add_header(self, title: str, date_prefix: str):
#         """Универсальный заголовок"""
#         current_y = self.pdf.get_y()
        
#         # Логотип
#         try:
#             self.pdf.image(self.logo_path, x=10, y=current_y, w=15)
#         except Exception as e:
#             logger.warning(f"Не удалось добавить логотип: {e}")
        
#         # Адрес и сайт
#         self.pdf.set_font('DejaVu', '', 10)
#         self.pdf.set_x(25)
#         self.pdf.cell(0, 10, ADRES)
#         self.pdf.ln(3)
#         self.pdf.set_x(25)
#         self.pdf.set_font('DejaVu', 'B', 10)
#         self.pdf.cell(0, 15, SITE)
#         self.pdf.ln(7)
        
#         # Заголовок с датой
#         self.pdf.set_font('DejaVu', 'BI', 14)
#         self.pdf.cell(self.pdf.get_string_width(title), 15, title)
        
#         start_x = self.pdf.get_x()
#         self.pdf.set_font('DejaVu', 'I', 10)
#         date_txt = f' {date_prefix} {datetime.now().strftime("%d.%m.%Y")}'
#         self.pdf.cell(0, 16, date_txt)
        
#         # Линия
#         self.pdf.set_x(start_x)
#         self.pdf.ln(12)
#         self.pdf.line(10, self.pdf.get_y(), 200, self.pdf.get_y())
#         self.pdf.ln(2)
    
#     def _add_data_section(self, data: Dict[str, str]):
#         """Добавляет секцию с данными"""
#         for key, value in data.items():
#             self.pdf.set_font('DejaVu', 'B', 9)
#             self.pdf.cell(self.pdf.get_string_width(f'{key}: '), 3, f'{key}: ')
            
#             self.pdf.set_font('DejaVu', '', 9)
#             display_value = value if value else '—'
#             if isinstance(display_value, list):
#                 display_value = ', '.join(display_value) if display_value else '—'
#             self.pdf.multi_cell(0, 3, str(display_value))
#             self.pdf.ln(1)
#         self.pdf.ln(2)
    
#     def _add_conditions(self, text: str):
#         """Добавляет условия"""
#         self.pdf.set_font('DejaVu', 'I', 7)
#         self.pdf.multi_cell(190, 3, text)
#         self.pdf.ln(1)
    
#     def _add_signature(self, left_label: str, left_name: str, right_name: str, agreement_text: str):
#         """Универсальная подпись"""
#         self.pdf.set_font('DejaVu', '', 10)
#         self.pdf.cell(70, 6, f'{left_label}: ___________ / {left_name}')
        
#         self.pdf.set_x(140)
#         self.pdf.cell(50, 6, f'__________ / {right_name}')
#         self.pdf.ln(3)
        
#         self.pdf.set_font('DejaVu', '', 7)
#         self.pdf.set_x(140)
#         self.pdf.cell(50, 10, agreement_text)
#         self.pdf.ln(10)
    
#     def _add_cut_line(self):
#         """Линия отреза"""
#         y = self.pdf.get_y()
#         self.pdf.set_draw_color(100, 100, 100)
#         self.pdf.line(0, y, 210, y)
#         self.pdf.set_y(y)
#         self.pdf.set_font('DejaVu', 'I', 8)
#         self.pdf.cell(0, 4, '- - - Cut here / Линия отреза - - -', align='C')
#         self.pdf.ln(5)
#         self.pdf.set_draw_color(0)
    
#     def _add_services_section(self, services: List[Dict], parts: List[Dict], lang: str):
#         """Добавляет секцию услуг и запчастей"""
#         if not services and not parts:
#             return
            
#         self.pdf.set_font('DejaVu', '', 9)
#         total = 0
        
#         # Работы
#         if services:
#             self.pdf.set_font('DejaVu', 'B', 9)
#             header = "Работы:" if lang == "ru" else "Services:"
#             self.pdf.cell(0, 8, header, 0, 1, "L")
#             self.pdf.set_font('DejaVu', '', 9)
                
#             for i, item in enumerate(services, 1):
#                 work = item.get("work", "—")
#                 pieces = int(item.get('pieces', 1))
#                 price = float(item.get('price', 0))
#                 warranty = item.get('warranty_period', '0')
                
#                 text = f"{i}. {work} - {price}{CURRENCY} - {pieces}шт. - {warranty}мес."
#                 self.pdf.set_x(10)
#                 self.pdf.multi_cell(0, 5, text)
#                 total += price * pieces
            
#             self.pdf.ln(2)
        
#         # Запчасти
#         if parts:
#             self.pdf.set_font('DejaVu', 'B', 9)
#             header = "Запчасти:" if lang == "ru" else "Parts:"
#             self.pdf.cell(0, 8, header, 0, 1, "L")
#             self.pdf.set_font('DejaVu', '', 9)
            
#             for i, item in enumerate(parts, 1):
#                 part = item.get("part", "—")
#                 pieces = int(item.get('pieces', 1))
#                 price = float(item.get('price', 0))
#                 warranty = item.get('warranty_period', '0')
                
#                 text = f"{i}. {part} - {price}{CURRENCY} - {pieces}шт. - {warranty}мес."
#                 self.pdf.set_x(10)
#                 self.pdf.multi_cell(0, 5, text)
#                 total += price * pieces
            
#             self.pdf.ln(2)
        
#         # Итого
#         self.pdf.ln(3)
#         self.pdf.set_font('DejaVu', 'B', 10)
#         total_str = f"{total:,.2f}".replace(',', ' ').replace('.', ',')
#         total_label = "ИТОГО:" if lang == "ru" else "TOTAL:"
#         self.pdf.cell(0, 6, f"{total_label} {total_str} {CURRENCY}", 0, 1)
    
#     def build_receipt(self, order: OrderData, receipt_type: ReceiptType, output_path: str) -> str:
#         """Главный метод построения PDF"""
#         self.pdf = self._create_pdf()
        
#         # Локализация
#         is_ru = order.lang == "ru"
        
#         # Заголовок
#         if receipt_type == ReceiptType.INTAKE:
#             title = f'Квитанция {order.order_number}' if is_ru else f'Receipt {order.order_number}'
#         else:
#             title = f'Акт выполненных работ {order.order_number}' if is_ru else f'The act of completed works {order.order_number}'
        
#         date_prefix = "от" if is_ru else "from"
        
#         # Данные для отображения
#         if is_ru:
#             display_data = {
#                 'Клиент': order.name_client,
#                 'Телефон': order.get_formatted_phone(),
#                 'Марка/модель': order.get_device_full_name(),
#                 'SN/imei': order.sn_imei,
#                 'Комплектация': ', '.join(order.equipment) if order.equipment else '—',
#                 'Внешний вид': ', '.join(order.appearance) if order.appearance else '—',
#                 'Причина обращения': ', '.join(order.problem) if order.problem else '—'
#             }
#         else:
#             display_data = {
#                 'Name': order.name_client,
#                 'Phone': order.get_formatted_phone(),
#                 'Brand/Model': order.get_device_full_name(),
#                 'SN/imei': order.sn_imei,
#                 'Equipment': ', '.join(order.equipment) if order.equipment else '—',
#                 'Device appearance': ', '.join(order.appearance) if order.appearance else '—',
#                 'Problems': ', '.join(order.problem) if order.problem else '—'
#             }
        
#         # Добавляем специфичные поля для приема
#         if receipt_type == ReceiptType.INTAKE:
#             if is_ru:
#                 display_data['Стоимость диагностики'] = f'{order.cost_diagnostics} {CURRENCY}'
#                 display_data['Примерная дата готовности'] = order.get_diagnosis_date()
#             else:
#                 display_data['The cost of diagnosis'] = f'{order.cost_diagnostics} {CURRENCY}'
#                 display_data['Approximate date ready'] = order.get_diagnosis_date()








