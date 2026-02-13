from config import USER_DB, PASSWORD_DB, DB_NAME, HOST
import psycopg2
from logs.set_logger import set_logger
logger = set_logger(name="db")




# Create TABLES:
def create_tables_in_db():
    connection, cursor = False, False

    try:
        # Connect to db:
        connection = psycopg2.connect(host=HOST, database=DB_NAME, user=USER_DB, password=PASSWORD_DB)

        cursor = connection.cursor()

        # Create table:
        create_table_users = '''
        CREATE TABLE IF NOT EXISTS users (
            user_id UUID PRIMARY KEY,                                                           -- UUID value

            user_glotmax VARCHAR(50) UNIQUE,                                                    -- MAX ебать его в рот..
            user_whatsapp VARCHAR(50) UNIQUE,                                                   -- WatsApp земля ему пухом..
            user_telegram BIGINT UNIQUE,                                                        -- Telegram id
            username_telegram VARCHAR(50) UNIQUE,                                               -- Telegram Username @name
            
            phone VARCHAR(20) UNIQUE,
            email VARCHAR(100) UNIQUE,
            name VARCHAR(50) NOT NULL,

            a_tip DECIMAL(10, 2),                                                               -- Чаевые от клиента сумма за все время
            total_spent DECIMAL(10, 2),                                                         -- Потратил клиент на ремонты за все время
            repair_count_total INT,                                                             -- Колличество ремонтов/обращений за все время
            
            real_name VARCHAR(50),                                                              -- Админ добавляет менеджеров и устанавливаем им реальные имена для доков
            description_user VARCHAR,                                                           -- Описание пользователя, для внутреннего использования
            source VARCHAR(200),                                                                -- Источник рекламы
            block BOOLEAN DEFAULT FALSE,                                                        -- Блок для пид..ов
            hum_quality VARCHAR(50),                                                            -- Бывает полезно, когда повторные обращения - экономит время и нервы   
            
            last_visit TIMESTAMP,                                                               -- Последнее посещение
            time_reg TIMESTAMP,                                                                 -- Время регистрации
            time_zone VARCHAR(10),                                                              -- Не используется
            language VARCHAR(10),                                                               -- Не используется
            parametrs JSONB,                                                                    -- На будующее, пока хз

            is_admin BOOLEAN DEFAULT FALSE,
            is_manager BOOLEAN DEFAULT FALSE,
            is_master BOOLEAN DEFAULT FALSE,

            remind JSONB                                                                        -- Напоминалка, позже можно замутить..
        );
        '''
        # Executing an SQL query:
        cursor.execute(create_table_users)


        create_table_orders = '''
        CREATE TABLE IF NOT EXISTS orders (
            id SERIAL PRIMARY KEY,                                                              -- Serial номер внутренний, на всякий
            order_number VARCHAR(20) UNIQUE NOT NULL,                                           -- красивый (R-2024-0001)
            
            location VARCHAR(50),                                                               -- Локация на будущее
            
            sn_imei VARCHAR(50),
            status VARCHAR(50),                                                                 -- Статус заказа (новый, в работе, готов..)
            order_type VARCHAR(50),                                                             -- Тип заказа (Платный, гарантийный)
            device_type VARCHAR(50),                                                            -- Тип устройства (принтер, телефон)
            device_brand VARCHAR(50),                                                           -- Бренд устройства (Asus, Apple)
            device_model VARCHAR(100),                                                          -- Модель устройства (iPhone 16)
            equipment VARCHAR(100),                                                             -- Комплектация устройства (Зарядка)
            
            problem TEXT,                                                                       -- Описание проблемы
            appearance VARCHAR(100),                                                            -- Внешний вид устройства
            created_date TIMESTAMP,                                                             -- Дата приема устройства
            completion_date TIMESTAMP,                                                          -- Дата выполнения заказа
            diagnosis_before TIMESTAMP,                                                         -- Дата ожидания примерной готовности диагностики
            
            diagnosis TEXT,                                                                     -- Текст диагностики
            cost_diagnostics DECIMAL(10, 2),                                                    -- Стоимость диагностики

            services TEXT,                                                                      -- Услуга - цена - гарантия
            cost_repair DECIMAL(10, 2),                                                         -- Общая стоимость ремонта/работ
            date_of_issue TIMESTAMP,                                                            -- Дата выдачи

            parts TEXT,                                                                         -- Запчасти - цена - гарантия
            cost_of_parts DECIMAL(10, 2),                                                       -- Общая стоимость запчастей
            cost_price DECIMAL(10, 2),                                                          -- Закупочная цена запчастей
            
            prepayment TEXT,                                                                    -- Предоплата клиента
            cost_prepayment DECIMAL(10, 2),                                                     -- Общая стоимость предоплаты
            
            net_profit DECIMAL(10, 2),                                                          -- Чистая прибыль с заказа
            tips DECIMAL(10, 2),                                                                -- Чаевые клиента
            
            path_photo VARCHAR(100),                                                            -- Путь к фотографиям устройства
            
            client_id UUID NOT NULL,                                                            -- user_id клиента заказа в UUID
            real_name_client VARCHAR(50),                                                       -- Реальное имя клиента для документов (для уменьшения обращений к базе)
            
            created_by BIGINT NOT NULL,                                                         -- Оформил менеджер с телеграмм id
            real_name_created VARCHAR(50),                                                      -- Реальное имя принимающего для документов (для уменьшения обращений к базе) 
            
            master UUID,                                                                        -- user_id мастера в UUID                                                
            
            edit_history JSONB,                                                                 -- Позже можно цепочку изменнений вносить, кто и когда менял
            
            comments TEXT,                                                                      -- Комментарии по ремонту
            time_spent_on_repairs FLOAT,                                                        -- Примерное время затраченное мастером на ремонт (позже можно будет определять самый выгодный вид ремонта)

            FOREIGN KEY (client_id) REFERENCES users(user_id)
        );
            CREATE INDEX IF NOT EXISTS idx_orders_client_id ON orders(client_id);
            CREATE INDEX IF NOT EXISTS idx_orders_status ON orders(status);
            CREATE INDEX IF NOT EXISTS idx_order_number ON orders(order_number);
            CREATE INDEX IF NOT EXISTS idx_orders_serial ON orders(sn_imei);
        '''
        cursor.execute(create_table_orders)


        create_table_fin_stats = '''
        CREATE TABLE IF NOT EXISTS fin_stats (
            payment_id SERIAL PRIMARY KEY,
            order_id INTEGER REFERENCES orders(id),                                             -- Порядковый id заказа
            client_id UUID REFERENCES users(user_id),                                           -- UUID клиента
            master_id UUID REFERENCES users(user_id),                                           -- UUID мастера
            
            payment_amount DECIMAL(10,2) NOT NULL,                                              -- Сумма оплаты (полная)
            net_profit DECIMAL(10,2) NOT NULL,                                                  -- Чистая* прибыль с ремонта (ремонт - запчасти)
            payment_method VARCHAR(20) NOT NULL,                                                -- Способ оплаты 'card', 'cash', 'crypto', 'free'
            
            payment_date TIMESTAMP DEFAULT NOW(),                                               -- Когда оплатили
            order_created_date TIMESTAMP,                                                       -- Когда создан заказ (дублируем для аналитики)
            order_completed_date TIMESTAMP,                                                     -- Когда завершён
            who_issued UUID REFERENCES users(user_id),                                          -- Кто принял оплату или выдал устройство клиенту
            
            device_type VARCHAR(50),                                                            -- Тип устройства (phone/laptop)
            device_model VARCHAR(100),                                                          -- Модель
            repair_type VARCHAR(50)

        );

        CREATE INDEX idx_fin_stats_payment_date ON fin_stats(payment_date);

        '''
        cursor.execute(create_table_fin_stats)



        # Saving changes:
        connection.commit()
        logger.info("Adding tables is done!")
        print("Adding tables is done!")
        return True

    except Exception as error:
        logger.error(f"Error Create Tables in DB: {error}")
        print("Error Create Tables in DB:", error)
        return False

    finally:

        # Closing the cursor and database connection
        if cursor:
            cursor.close()

        if connection:
            connection.close()

# create_tables_in_db()


# VARCHAR(n) - строковый тип данных ограничение n, TEXT - строковый тип данных ограничение в 1Гб.
# iuser_id INTEGER SERIAL PRIMARY KEY , тут SERIAL - означает, что каждый последующее число в строке будет само увеличиваться..
# Если ячейка является первичным ключем, то она автоматически добавленна в индекс, CONSTRAINT unique_user_id UNIQUE (user_id)  -- Создание уникального ограничения также создает индекс
# INTEGER  BIGINT block BOOLEAN NOT NULL DEFAULT FALSE  INTEGER  VARCHAR(100) NOT NULL UNIQUE UNIQUE
# time_zone TIMESTAMP DEFAULT CURRENT_TIMESTAMP
# UNIQUE - автоматом индексируются
# INDEX idx_name (name)  -- Создание обычного индекса на колонке name