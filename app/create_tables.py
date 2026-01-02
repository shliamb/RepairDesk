from keys import USER_DB, PASSWORD_DB, DB_NAME
from config import HOST, PATH_LOGS
import psycopg2
from set_logger import setup_logger

logger_db = setup_logger('db', f'{PATH_LOGS}db.log')


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
            user_id UUID PRIMARY KEY UNIQUE NOT NULL,       -- UUID value
            user_glotmax VARCHAR(20) UNIQUE,
            user_whatsapp VARCHAR(20) UNIQUE,
            user_telegram BIGINT UNIQUE,                    -- telegram id
            phone VARCHAR(20) UNIQUE,
            email VARCHAR(20) UNIQUE,
            surname VARCHAR(50),                            -- фамилия
            name VARCHAR(50),
            description_user VARCHAR(200),
            source VARCHAR(200),                            -- источник рекламы
            block BOOLEAN DEFAULT FALSE,                    -- блок пид..ов
            hum_quality VARCHAR(50),          
            last_visit TIMESTAMP,
            time_reg TIMESTAMP,
            time_zone VARCHAR(10), 
            language VARCHAR(10),
            admin BOOLEAN DEFAULT FALSE,
            super_admin BOOLEAN DEFAULT FALSE,
            system JSONB,
            paid INT DEFAULT 0,
        );
        '''
        # Executing an SQL query:
        cursor.execute(create_table_users)

        create_table_orders = '''
        CREATE TABLE IF NOT EXISTS orders (
            id SERIAL PRIMARY KEY,
            date TIMESTAMP,
            model VARCHAR(50),
            tokens INTEGER,
            price_1 FLOAT,
            price FLOAT,
            user_id UUID,
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        );
        '''
        cursor.execute(create_table_orders)

        create_table_methods_pay = '''
        CREATE TABLE IF NOT EXISTS methods_pay (
            id SERIAL PRIMARY KEY,
            date TIMESTAMP,
            counts INT,
            use_sbp_transfer BOOLEAN,
            use_mastercard BOOLEAN,
            use_visa BOOLEAN,
            use_mircard BOOLEAN,
            use_cripto BOOLEAN,
            use_sms BOOLEAN,
            use_stars BOOLEAN,
            use_telegram BOOLEAN,
            use_digital BOOLEAN,
            title_method_pay VARCHAR(50) UNIQUE,
            method_pay_ru TEXT,
            method_pay_en TEXT
        );
        '''
        cursor.execute(create_table_methods_pay)

        create_table_payments = '''
        CREATE TABLE IF NOT EXISTS payments (
            id SERIAL PRIMARY KEY,
            date TIMESTAMP UNIQUE,
            title_method_pay VARCHAR(50),
            sum FLOAT,
            user_id VARCHAR,
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        );
        '''
        cursor.execute(create_table_payments)

        # Saving changes:
        connection.commit()
        logger_db.info("Adding tables is done!")
        print("Adding tables is done!")
        return True

    except Exception as error:
        logger_db.error(f"Error Create Tables in DB: {error}")
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