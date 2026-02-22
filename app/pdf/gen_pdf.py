#! app/pdf/gen_pdf,py
# pip install fpdf2
from fpdf import FPDF
from datetime import datetime
from logs.set_logger import set_logger
logger = set_logger(name="pdf")
from utils.formatters import remove_emojis, format_phone, format_date_nice
from config import CONDITIONS, CONDITIONS_OF_ISSUE, ADRES, SITE, CURRENCY
import json






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
        self.add_conditions_out()
        self.add_signature_out()


    def get_order_out_pdf(self, data_pdf: dict) -> str:
        """ Главный метод генерируем квитанцию выдачи устройства"""
        self._get_self_data_out(data_pdf)
        
        # КЛЮЧЕВОЕ ИСПРАВЛЕНИЕ: Создаем PDF здесь, перед началом работы с документом
        self._init_pdf_engine() 
        
        # Рисуем контент
        self._draw_receipt_body_out()
        
        # Сохраняем и закрываем
        return self.save_file_pdf()



