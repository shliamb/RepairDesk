#! app/pdf/gen_pdf,py
# pip install fpdf2
from fpdf import FPDF
from datetime import datetime
from logs.set_logger import set_logger
logger = set_logger(name="pdf")
from config import CONDITIONS, ADRES, SITE, CURRENCY
import json



def remove_emojis(text: str) -> str:
    """Удаляет эмодзи (простая версия)"""
    import re
    return re.sub(r'[^\w\s,.!?;:()\-@#%&*+=/\\|"\'<>$€£¥₹₽]', '', str(text))




class BuildPDF():
    """ Генерация PDF файла """
    def __init__(self):
        self.pdf = FPDF()
        self.pdf.add_page()
        self.pdf.set_margins(10, 10, 10)
        self.pdf.set_auto_page_break(True, 10)
        self.width = self.pdf.w  # 210
        self.height = self.pdf.h  # 297
        # Шрифты
        self.pdf.add_font('DejaVu', '', 'app/pdf/font/DejaVuSans.ttf') # DejaVuSans-ExtraLight.ttf
        self.pdf.add_font('DejaVu', 'B', 'app/pdf/font/DejaVuSans-Bold.ttf')
        self.pdf.add_font('DejaVu', 'I', 'app/pdf/font/DejaVuSans-Oblique.ttf')
        self.pdf.add_font('DejaVu', 'BI', 'app/pdf/font/DejaVuSans-BoldOblique.ttf')
        self.pdf.set_font('DejaVu', '', 10)
        #
        self.logo_path = "app/pdf/img/logo.jpeg"
        self.path_save_pdf = "./app/pdf/out_files"
        self.conditions = CONDITIONS
        self.currency = CURRENCY
        self.adres = ADRES
        self.site = SITE
        



    def _get_self_data(self, data_pdf: dict) -> None:
        """ Извлекаю данные для оформления """
        if not data_pdf:
            logger.error("Пустой data_pdf: dict")
            return
        
        # Автоматом, но у меня как всегда - грабли 
        # for key, value in data_pdf.items():
        #     setattr(self, key, value)

        self.lang = data_pdf.get("lang", "en")
        self.order_number = data_pdf.get("order_number")
        self.sn_imei = data_pdf.get("sn_imei")
        self.order_type = data_pdf.get("order_type")
        self.device_type = remove_emojis(data_pdf.get("device_type")) if data_pdf.get("device_type") else None
        self.device_brand = data_pdf.get("device_brand")
        self.device_model = data_pdf.get("device_model")
        self.equipment = json.loads(data_pdf.get("equipment")) if data_pdf.get("equipment") else None
        self.problem = json.loads(data_pdf.get("problem")) if data_pdf.get("problem") else None
        self.appearance = json.loads(data_pdf.get("appearance")) if data_pdf.get("appearance") else None
        self.created_date = data_pdf.get("created_date")
        self.diagnosis_before = data_pdf.get("diagnosis_before")
        self.cost_diagnostics = data_pdf.get("cost_diagnostics")
        self.path_photo = data_pdf.get("path_photo")
        #self.client_id = data_pdf.get("client_id")
        self.name_client = data_pdf.get("name")
        self.phone_client = data_pdf.get("phone")
        #self.created_by = data_pdf.get("created_by")
        self.created_by = 'Шаошников А.В.'



        self.equipment = ", ".join(self.equipment.copy())
        self.appearance = ", ".join(self.appearance.copy())
        self.problem = ", ".join(self.problem.copy())

        self.order_data_ru = ({
            'Клиент': self.name_client,
            'Телефон': self.phone_client,
            'Марка/модель': f'{self.device_type} {self.device_brand} ({self.device_model})',
            'SN/imei': self.sn_imei,
            'Комплектация': self.equipment,
            'Внешний вид': self.appearance,
            'Причина обращения': self.problem,
            'Стоимость диагностики': f'{self.cost_diagnostics} {self.currency}',
            'Примерная дата готовности диагностики': self.diagnosis_before
        }).copy()
        self.order_data_en = ({
            'Name': self.name_client,
            'Phone': self.phone_client,
            'Brand/Model': f'{self.device_type} {self.device_brand} ({self.device_model})',
            'SN/imei': self.sn_imei,
            'Equipment': self.equipment,
            'Device appearance': self.appearance,
            'Problems': self.problem,
            'The cost of diagnosis': f'{self.cost_diagnostics} {self.currency}',
            'Approximate date when the diagnosis is ready': self.diagnosis_before
        }).copy()
        

    @staticmethod
    def _get_date() -> datetime:
        """ Текущая дата и время """
        return datetime.now().strftime("%d.%m.%Y")


    def save_file_pdf(self) -> str:
        """Сохраняю в файл pdf с путем"""
        name = self.order_number
        path = self.path_save_pdf
        full_path = f"{path}/{name}.pdf" if path else f"{name}.pdf"
        self.pdf.output(full_path)
        return full_path

    
    def add_header(self) -> None:
        """Добавляем заголовок"""
        current_y = self.pdf.get_y()
        self.pdf.image(self.logo_path, x=10, y=current_y, w=15)
        self.pdf.set_font('DejaVu', '', 10)
        self.pdf.set_x(25)  # Отступ 30мм слева
        self.pdf.cell(0, 10, self.adres)
        self.pdf.ln(3)
        self.pdf.set_x(25)
        self.pdf.set_font('DejaVu', 'B', 10)
        self.pdf.cell(0, 15, self.site)
        self.pdf.ln(7)
        self.pdf.set_font('DejaVu', 'BI', 14)
        title_order_num = f'Квитанция {self.order_number}' if self.lang == 'ru' else f'Receipt {self.order_number}'
        number_width = self.pdf.get_string_width(title_order_num)
        self.pdf.cell(number_width, 15, title_order_num)
        start_value_x = self.pdf.get_x()
        #self.pdf.set_x(85)
        self.pdf.set_font('DejaVu', 'I', 10)
        self.pdf.cell(0, 16, f' от {self._get_date()}')
        self.pdf.set_x(start_value_x)
        self.pdf.ln(12)
        self.pdf.line(10, self.pdf.get_y(), 200, self.pdf.get_y())  # Линия от x=10 до x=200
        self.pdf.ln(2)


    def add_order_data(self) -> None:
        """ Данные заказа """

        if self.lang == "ru": order_data = self.order_data_ru
        else: order_data = self.order_data_en

        for key, value in order_data.items():
            # Тоочная ширина текста
            self.pdf.set_font('DejaVu', 'B', 9)
            key_width = self.pdf.get_string_width(f'{key}: ')
            
            self.pdf.cell(key_width, 3, f'{key}: ')
            
            # Текущая позиция X
            start_value_x = self.pdf.get_x()
            
            self.pdf.set_font('DejaVu', '', 9)
            if not value: value = ' — '
            self.pdf.multi_cell(0, 3, f'{value}')
            
            # Для следующей строки вернулись на ту же стартовую позицию
            self.pdf.set_x(start_value_x)
            self.pdf.ln(1)
        
        self.pdf.ln(2)


    def add_conditions(self) -> None:
        """Добавляем условия """
        self.pdf.set_font('DejaVu', 'I', 7)
        if self.lang == "ru": self.pdf.multi_cell(190, 3, self.conditions["ru"])
        else: self.pdf.multi_cell(190, 3, self.conditions["en"])
        self.pdf.ln(1)


    def add_signature(self):
        """ Добавление место подписей """
        self.pdf.set_font('DejaVu', '', 10)
        if self.lang == "ru": self.pdf.cell(70, 6, f'Принял: ___________ / {self.created_by}')
        else: self.pdf.cell(70, 6, f'Has accepted: ___________ / {self.created_by}')
        self.pdf.set_x(140)
        self.pdf.cell(50, 6, f'__________ / {self.name_client}')
        self.pdf.ln(3)
        self.pdf.set_font('DejaVu', '', 7)
        self.pdf.set_x(140)
        if self.lang == "ru": self.pdf.cell(50, 10, 'с условиями ознакомлен и согласен')
        else: self.pdf.cell(50, 10, 'I have read and agree to the terms and conditions')
        self.pdf.ln(20)


    def get_order_pdf(self, data_pdf: dict)-> None:
        """ Генерация pdf """
        self._get_self_data(data_pdf)
        self.add_header()
        self.add_order_data()
        self.add_conditions()
        self.add_signature()
        self.add_header()
        self.add_order_data()
        self.add_conditions()
        self.add_signature()
        return self.save_file_pdf()




# data_pdf = {}
# pdf = BuildPDF()
# pdf.get_order_pdf(data_pdf)











# from fpdf import FPDF

# pdf = FPDF()          # 1. Создаем пустой PDF
# pdf.add_page()        # 2. Добавляем страницу

# # 3. Шрифты (должны быть в папке)
# pdf.add_font('Font', '', 'arial.ttf', uni=True)
# pdf.set_font('Font', '', 12)  # шрифт, стиль, размер

# # 4. Основные команды:
# pdf.cell(ширина, высота, 'текст')    # Ячейка с текстом (одна строка)
# pdf.ln(10)                           # Перенос строки (10мм вниз)
# pdf.multi_cell(ширина, высота, 'длинный текст')  # Многострочный текст

# # 5. Координаты и позиция:
# pdf.set_xy(50, 100)   # Установить позицию (X=50, Y=100)
# pdf.get_x()           # Текущая позиция X
# pdf.get_y()           # Текущая позиция Y

# # 6. Линии:
# pdf.line(x1, y1, x2, y2)     # Линия от (x1,y1) до (x2,y2)
# pdf.rect(x, y, width, height)  # Прямоугольник

# # 7. Изображения:
# pdf.image('photo.jpg', x=10, y=10, w=50)  # w=ширина, h=высота

# # 8. Сохранение:
# pdf.output('файл.pdf')





# from fpdf import FPDF

# pdf = FPDF()
# pdf.add_page()

# # Шрифт
# pdf.add_font('Arial', '', 'arial.ttf', uni=True)
# pdf.set_font('Arial', '', 12)

# # Заголовок
# pdf.cell(0, 10, 'Мой заголовок', ln=True)  # ln=True - перенос строки

# # Текст с отступом
# pdf.ln(5)  # Отступ 5мм
# pdf.cell(50, 8, 'Имя:')  # Ячейка шириной 50мм
# pdf.cell(0, 8, 'Иван')   # Продолжение в той же строке
# pdf.ln(10)

# # Многострочный текст (автоперенос)
# pdf.multi_cell(0, 8, 'Длинный текст который сам перенесется на новые строки если не влезет')

# # Горизонтальная линия
# pdf.ln(10)
# pdf.line(10, pdf.get_y(), 200, pdf.get_y())  # Линия от x=10 до x=200

# # Картинка
# pdf.image('logo.png', x=10, y=pdf.get_y()+5, w=30)

# # Сохраняем
# pdf.output('документ.pdf')



# # Добавляешь 2 версии шрифта:
# pdf.add_font('DejaVu', '', 'DejaVuSans.ttf')      # Обычный
# pdf.add_font('DejaVu', 'B', 'DejaVuSans-Bold.ttf') # Жирный

# # Переключаешься:
# pdf.set_font('DejaVu', '', 12)   # Обычный
# pdf.cell(0, 10, 'Обычный текст')

# pdf.set_font('DejaVu', 'B', 12)  # Жирный
# pdf.cell(0, 10, 'Жирный текст')





# '' - обычный (Regular)

# 'B' - жирный (Bold) - нужен отдельный файл .ttf

# 'I' - курсив (Italic) - нужен отдельный файл

# 'BI' - жирный курсив (Bold Italic) - нужен отдельный файл






# # Добавление всех стилей (если файлы есть):
# pdf.add_font('DejaVu', '', 'DejaVuSans.ttf')
# pdf.add_font('DejaVu', 'B', 'DejaVuSans-Bold.ttf')
# pdf.add_font('DejaVu', 'I', 'DejaVuSans-Oblique.ttf')
# pdf.add_font('DejaVu', 'BI', 'DejaVuSans-BoldOblique.ttf')

# # Использование:
# pdf.set_font('DejaVu', '', 12)
# pdf.cell(0, 10, 'Обычный')

# pdf.set_font('DejaVu', 'B', 12)
# pdf.cell(0, 10, 'Жирный')

# pdf.set_font('DejaVu', 'I', 12)  
# pdf.cell(0, 10, 'Курсив')

# pdf.set_font('DejaVu', 'BI', 12)
# pdf.cell(0, 10, 'Жирный курсив')






























# # Создаем PDF
# pdf = FPDF()
# pdf.add_page()

# # Добавляем шрифты
# pdf.add_font('DejaVu', '', 'app/pdf/DejaVuSans.ttf', uni=True)
# pdf.set_font('DejaVu', '', 10)

# # 1. Добавляем дату вверху
# current_date = datetime.now().strftime("%d/%m/%y, %I:%M %p")
# pdf.cell(0, 5, current_date)
# pdf.ln(5)

# # 2. Данные мастерской
# pdf.cell(0, 5, 'Москва, 3-я Парковая, дом 38, +7 (999) 832-99-34 с 10 до 20 каждый день')
# pdf.ln(5)
# pdf.cell(0, 5, 'www.1Rmaster.ru')
# pdf.ln(10)

# # 3. Заголовок квитанции
# pdf.set_font('DejaVu', '', 14)
# pdf.cell(0, 8, 'Квитанция A1457 от 12.01.2026')
# pdf.ln(10)

# # 4. Данные клиента
# pdf.set_font('DejaVu', '', 10)
# data = [
#     'Клиент: Игорь Бобров',
#     'Телефон:',
#     'Марка/модель: Asus',
#     'Комплектация: Устройство, TUF Gaming B760m-plus wifi d4, 4 * 8, гб, i5-13600kf, i5-14600kf',
#     'Внешний вид: царапины, потертости',
#     'Причина обращения со слов заказчика:',
#     'Стоимость диагностики: 0,00',
#     'Примерная дата готовности диагностики: 13.01.2026 14:29'
# ]

# for line in data:
#     pdf.cell(0, 6, line)
#     pdf.ln(6)

# pdf.ln(10)

# # 5. Условия (одним текстом)
# pdf.set_font('DejaVu', '', 9)
# conditions = """1. Устройство принимается в мастерскую на диагностику/ремонт для определения примерных сроков, стоимости и возможности проведения ремонта заявленной клиентом неисправности.
# 2. При диагностике или ремонте устройства его необходимо вскрыть, что влечёт за собой потерю заводской гарантии, прошу это учитывать и самостоятельно проверять наличие гарантии от производителя.
# 3. Заказчик принимает на себя риск возможной полной или частичной утраты работоспособности устройства в процессе ремонта, в случае грубых нарушений пользователем условий эксплуатации, наличие следов попадания токопроводящей жидкости (коррозии), либо механических повреждений.
# 4. Условия хранения клиентских устройств: Максимальный срок гарантийного или платного ремонта составляет 45 дней. Срок ремонта может быть увеличен при отсутствии запчастей. 2. С момента оповещения клиента о готовности или не возможности ремонта Клиент обязуется забрать изделие в течение 30 календарных дней. По истечении 30-дневного срока бесплатного хранения за дальнейшее хранение Исполнителем взимается плата в размере 100 рублей в сутки. 3. Стороны договорились, что при неисполнении Клиентом своей обязанности забрать изделие из ремонта, по истечении двух месяцев с момента начала платного хранения, оборудование становится невостребованным Клиентом. Клиент, тем самым, отказывается от своего права на данное оборудование, и Исполнитель имеет право реализовать данное имущество в счет возмещения убытков за ремонт и хранение изделия.
# 5. Аппарат выдается при предъявлении «Квитанции о приеме». В случае утери квитанции выдача устройства может быть произведена при предъявлении документа, удостоверяющего личность на имя заказчика.
# Заказчик ознакомлен и согласен с вышеперечисленными условиями и обработкой персональных данных, указанных в настоящей квитанции, а также несёт ответственность за их достоверность. Заказчик подтверждает, что является законным владельцем устройства."""

# # Разбиваем текст на абзацы и добавляем
# paragraphs = conditions.split('\n')
# for para in paragraphs:
#     pdf.multi_cell(0, 4, para)
#     pdf.ln(3)

# pdf.ln(10)

# # 6. Подписи
# pdf.set_font('DejaVu', '', 10)
# pdf.cell(0, 6, 'Принял: / / Петров А.В./')
# pdf.ln(8)
# pdf.cell(0, 6, 'с условиями ознакомлен и согласен')
# pdf.ln(8)
# pdf.cell(0, 6, 'A1457 A1457')

# # Сохраняем
# pdf.output('Квитанция_ремонт_исправлено.pdf')
# print('PDF создан: Квитанция_ремонт_исправлено.pdf')




















# from fpdf import FPDF
# from datetime import datetime

# # Создаем класс для квитанции
# class RepairReceiptPDF(FPDF):
#     def __init__(self):
#         super().__init__()
#         self.add_page()
        
#         # Регистрируем шрифт
#         self.add_font('DejaVu', '', 'app/pdf/DejaVuSans.ttf', uni=True)
#         self.add_font('DejaVu', 'B', 'app/pdf/DejaVuSans-Bold.ttf', uni=True)  # Добавь эту строку
#         self.set_font('DejaVu', '', 10)
    
#     def add_header(self, workshop_info, website, current_date):
#         """Добавляем заголовок"""
#         self.set_font('DejaVu', '', 9)
#         self.cell(190, 5, current_date)
#         self.ln(5)
#         self.cell(190, 5, workshop_info)
#         self.ln(5)
#         self.cell(190, 5, website)
#         self.ln(10)

    
#     def add_receipt_info(self, receipt_num, date):
#         """Информация о квитанции"""
#         self.set_font('DejaVu', 'B', 12)
#         self.cell(0, 8, f'Квитанция {receipt_num} от {date}', ln=True)
#         self.set_font('DejaVu', '', 10)
#         self.ln(5)
    
#     def add_client_info(self, client_name, phone, brand, equipment, appearance, reason, cost, ready_date):
#         """Информация о клиенте и устройстве"""
#         fields = [
#             f'Клиент: {client_name}',
#             f'Телефон: {phone}',
#             f'Марка/модель: {brand}',
#             f'Комплектация: {equipment}',
#             f'Внешний вид: {appearance}',
#             f'Причина обращения со слов заказчика: {reason}',
#             f'Стоимость диагностики: {cost}',
#             f'Примерная дата готовности диагностики: {ready_date}'
#         ]
        
#         for field in fields:
#             self.cell(0, 6, field, ln=True)
        
#         self.ln(5)
    
#     def add_conditions(self):
#         """Добавляем условия"""
#         conditions = [
#             "1. Устройство принимается в мастерскую на диагностику/ремонт для определения примерных сроков,",
#             "стоимости и возможности проведения ремонта заявленной клиентом неисправности.",
#             "2. При диагностике или ремонте устройства его необходимо вскрыть, что влечёт за собой потерю",
#             "заводской гарантии, прошу это учитывать и самостоятельно проверять наличие гарантии от производителя.",
#             "3. Заказчик принимает на себя риск возможной полной или частичной утраты работоспособности",
#             "устройства в процессе ремонта, в случае грубых нарушений пользователем условий эксплуатации,",
#             "наличие следов попадания токопроводящей жидкости (коррозии), либо механических повреждений.",
#             "4. Условия хранения клиентских устройств: Максимальный срок гарантийного или платного ремонта",
#             "составляет 45 дней. Срок ремонта может быть увеличен при отсутствии запчастей. 2. С момента",
#             "оповещения клиента о готовности или не возможности ремонта Клиент обязуется забрать изделие",
#             "в течение 30 календарных дней. По истечении 30-дневного срока бесплатного хранения за",
#             "дальнейшее хранение Исполнителем взимается плата в размере 100 рублей в сутки. 3. Стороны",
#             "договорились, что при неисполнении Клиентом своей обязанности забрать изделие из ремонта,",
#             "по истечении двух месяцев с момента начала платного хранения, оборудование становится",
#             "невостребованным Клиентом. Клиент, тем самым, отказывается от своего права на данное",
#             "оборудование, и Исполнитель имеет право реализовать данное имущество в счет возмещения",
#             "убытков за ремонт и хранение изделия.",
#             "5. Аппарат выдается при предъявлении «Квитанции о приеме». В случае утери квитанции выдача",
#             "устройства может быть произведена при предъявлении документа, удостоверяющего личность",
#             "на имя заказчика.",
#             "Заказчик ознакомлен и согласен с вышеперечисленными условиями и обработкой персональных",
#             "данных, указанных в настоящей квитанции, а также несёт ответственность за их достоверность.",
#             "Заказчик подтверждает, что является законным владельцем устройства."
#         ]
        
#         self.set_font('DejaVu', '', 9)
#         for line in conditions:
#             self.multi_cell(190, 4, line)
        
#         self.ln(5)
    
#     def add_signatures(self, accepted_by, receipt_num):
#         """Добавляем подписи"""
#         self.set_font('DejaVu', '', 10)
#         self.cell(0, 6, f'Принял: / / {accepted_by}/', ln=True)
#         self.cell(0, 6, 'с условиями ознакомлен и согласен', ln=True)
#         self.ln(2)
#         self.cell(0, 6, f'{receipt_num} {receipt_num}', ln=True)

# # Создаем квитанцию
# def create_receipt():
#     # Твои данные
#     data = {
#         'workshop_info': 'Москва, 3-я Парковая, дом 38, +7 (999) 832-99-34 с 10 до 20 каждый день',
#         'website': 'www.1Rmaster.ru',
#         'receipt_num': 'A1457',
#         'client_name': 'Игорь Бородин',
#         'phone': '',
#         'brand': 'Asus',
#         'equipment': 'Устройство, @library, TUF Gaming B760m-plus wifi d4, 4 * 8, гб, i5-13600kf, i5-14600kf',
#         'appearance': 'царапины, потертости',
#         'reason': '',
#         'cost': '0,00',
#         'ready_date': '13.01.2026 14:29',
#         'accepted_by': 'Шапошников А.В.'
#     }
    
#     # Создаем PDF
#     pdf = RepairReceiptPDF()
    
#     # Добавляем контент
#     current_date = datetime.now().strftime("%d/%m/%y, %I:%M %p")
#     receipt_date = datetime.now().strftime("%d.%m.%Y")
    
#     pdf.add_header(data['workshop_info'], data['website'], current_date)
#     pdf.add_receipt_info(data['receipt_num'], receipt_date)
#     pdf.add_client_info(
#         data['client_name'], data['phone'], data['brand'], 
#         data['equipment'], data['appearance'], data['reason'], 
#         data['cost'], data['ready_date']
#     )
#     pdf.add_conditions()
#     pdf.add_signatures(data['accepted_by'], data['receipt_num'])
    
#     # Сохраняем
#     output_file = 'Квитанция_ремонт.pdf'
#     pdf.output(output_file)
#     print(f'Квитанция создана: {output_file}')

# # Запускаем
# if __name__ == "__main__":
#     create_receipt()































# from reportlab.lib.pagesizes import A4
# from reportlab.pdfgen import canvas
# from reportlab.pdfbase import pdfmetrics
# from reportlab.pdfbase.ttfonts import TTFont
# from datetime import datetime
# import os

# def generate_pdf_receipt(client_data, output_file="Квитанция_ремонт.pdf"):
#     """
#     Генерирует PDF-квитанцию о приеме устройства в ремонт
#     """
    
#     # Регистрируем шрифт для поддержки кириллицы
#     try:
#         # Попробуем использовать стандартный шрифт
#         from reportlab.pdfbase.ttfonts import TTFont
#         # Если есть шрифт Arial, используем его
#         pdfmetrics.registerFont(TTFont('ArialUni', 'arial.ttf'))
#         font_name = 'ArialUni'
#     except:
#         # Или используем встроенный шрифт
#         from reportlab.pdfbase import pdfmetrics
#         from reportlab.pdfbase.ttfonts import TTFont
#         font_name = 'Helvetica'
    
#     # Текущая дата
#     current_date = datetime.now().strftime("%d/%m/%y, %I:%M %p")
#     receipt_date = datetime.now().strftime("%d.%m.%Y")
    
#     # Данные по умолчанию
#     default_data = {
#         "receipt_number": "A1457",
#         "date": receipt_date,
#         "client_name": "Иван Иванов",
#         "phone": "+7 (999) 123-45-67",
#         "brand_model": "Asus TUF Gaming",
#         "equipment": "Устройство, зарядное устройство",
#         "appearance": "царапины, потертости",
#         "reason": "Не включается",
#         "diagnostic_cost": "0,00",
#         "diagnostic_date": "15.01.2026 14:29",
#         "workshop_name": "Москва, 3-я Парковая, дом 38, +7 (999) 832-99-34 с 10 до 20 каждый день",
#         "website": "www.1Rmaster.ru",
#         "accepted_by": "Петров П.П.",
#         "client_signature": client_data.get("client_name", "Иван Иванов")
#     }
    
#     # Объединяем данные
#     data = {**default_data, **client_data}
    
#     # Создаем PDF
#     c = canvas.Canvas(output_file, pagesize=A4)
#     width, height = A4
    
#     # Начальная позиция
#     y_position = height - 50
    
#     # Функция для добавления текста
#     def add_text(text, x, y, size=10, bold=False):
#         c.setFont(font_name + ("-Bold" if bold else ""), size)
#         c.drawString(x, y, text)
    
#     # Заголовок
#     add_text(current_date, 50, y_position, 10)
#     y_position -= 20
    
#     add_text(data['workshop_name'], 50, y_position, 10)
#     y_position -= 15
    
#     add_text(data['website'], 50, y_position, 10)
#     y_position -= 30
    
#     # Номер квитанции
#     add_text(f"Квитанция {data['receipt_number']} от {data['date']}", 50, y_position, 12, True)
#     y_position -= 30
    
#     # Данные клиента
#     add_text(f"Клиент: {data['client_name']}", 50, y_position, 10)
#     y_position -= 20
    
#     add_text(f"Телефон: {data['phone']}", 50, y_position, 10)
#     y_position -= 20
    
#     add_text(f"Марка/модель: {data['brand_model']}", 50, y_position, 10)
#     y_position -= 20
    
#     add_text(f"Комплектация: {data['equipment']}", 50, y_position, 10)
#     y_position -= 20
    
#     add_text(f"Внешний вид: {data['appearance']}", 50, y_position, 10)
#     y_position -= 20
    
#     add_text(f"Причина обращения: {data['reason']}", 50, y_position, 10)
#     y_position -= 20
    
#     add_text(f"Стоимость диагностики: {data['diagnostic_cost']}", 50, y_position, 10)
#     y_position -= 20
    
#     add_text(f"Примерная дата готовности диагностики: {data['diagnostic_date']}", 50, y_position, 10)
#     y_position -= 30
    
#     # Условия
#     conditions = [
#         "1. Устройство принимается в мастерскую на диагностику/ремонт для определения",
#         "примерных сроков, стоимости и возможности проведения ремонта заявленной",
#         "клиентом неисправности.",
#         "2. При диагностике или ремонте устройства его необходимо вскрыть, что влечёт",
#         "за собой потерю заводской гарантии, прошу это учитывать и самостоятельно",
#         "проверять наличие гарантии от производителя.",
#         "3. Заказчик принимает на себя риск возможной полной или частичной утраты",
#         "работоспособности устройства в процессе ремонта, в случае грубых нарушений",
#         "пользователем условий эксплуатации, наличие следов попадания токопроводящей",
#         "жидкости (коррозии), либо механических повреждений.",
#         "4. Условия хранения клиентских устройств: Максимальный срок гарантийного",
#         "или платного ремонта составляет 45 дней. Срок ремонта может быть увеличен",
#         "при отсутствии запчастей. 2. С момента оповещения клиента о готовности",
#         "или не возможности ремонта Клиент обязуется забрать изделие в течение 30",
#         "календарных дней. По истечении 30-дневного срока бесплатного хранения",
#         "за дальнейшее хранение Исполнителем взимается плата в размере 100 рублей",
#         "в сутки. 3. Стороны договорились, что при неисполнении Клиентом своей",
#         "обязанности забрать изделие из ремонта, по истечении двух месяцев с момента",
#         "начала платного хранения, оборудование становится невостребованным",
#         "Клиентом. Клиент, тем самым, отказывается от своего права на данное",
#         "оборудование, и Исполнитель имеет право реализовать данное имущество",
#         "в счет возмещения убытков за ремонт и хранение изделия.",
#         "5. Аппарат выдается при предъявлении «Квитанции о приеме». В случае утери",
#         "квитанции выдача устройства может быть произведена при предъявлении",
#         "документа, удостоверяющего личность на имя заказчика.",
#         "Заказчик ознакомлен и согласен с вышеперечисленными условиями и обработкой",
#         "персональных данных, указанных в настоящей квитанции, а также несёт",
#         "ответственность за их достоверность. Заказчик подтверждает, что является",
#         "законным владельцем устройства."
#     ]
    
#     for condition in conditions:
#         add_text(condition, 50, y_position, 9)
#         y_position -= 15
    
#     y_position -= 20
    
#     # Подписи
#     add_text(f"Принял: / / {data['accepted_by']}/", 50, y_position, 10)
#     y_position -= 20
    
#     add_text("с условиями ознакомлен и согласен", 50, y_position, 10)
#     y_position -= 20
    
#     add_text(f"{data['receipt_number']} {data['receipt_number']}", 50, y_position, 10)
    
#     # Сохраняем PDF
#     c.save()
#     print(f"PDF квитанция сохранена в файл: {output_file}")
#     print(f"Файл находится в: {os.path.abspath(output_file)}")

# # Пример использования
# if __name__ == "__main__":
#     # Введите ваши данные
#     my_data = {
#         "client_name": "Ваше Имя Фамилия",
#         "phone": "Ваш телефон",
#         "brand_model": "Марка и модель устройства",
#         "equipment": "Что сдаете в ремонт",
#         "appearance": "Состояние устройства",
#         "reason": "Причина обращения",
#         "diagnostic_date": "дата готовности диагностики",
#         "receipt_number": "номер квитанции",
#     }
    
#     generate_pdf_receipt(my_data)