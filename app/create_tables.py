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
            user_id VARCHAR PRIMARY KEY,        -- обфусцированный HMAC, вернуть обратно не выйдет
            block BOOLEAN DEFAULT FALSE,
            dialog_agent VARCHAR,               -- Диалог с агентом
            dialog_seo VARCHAR,                 -- Диалог с SEO агентами !!! Пока что не использую, на всякий случай..
            last_visit TIMESTAMP,
            time_zone VARCHAR(10), 
            language VARCHAR(10),
            system_contents JSONB,              -- Разные инструкции для агентов в JSON
            rewrite INT,                        -- Максимально возможное колличество переписывания текста агентом
            format_text VARCHAR(50),
            model VARCHAR(50),
            format_file VARCHAR(50),
            paid INT DEFAULT 0,
            intermediate BOOLEAN,               -- Вывод промежуточных данных, True - выводит
            money FLOAT
        );
        -- CREATE INDEX idx_ai ON users(ai);
        CREATE INDEX IF NOT EXISTS idx_system_contents ON users USING gin (system_contents jsonb_path_ops);
        CREATE INDEX idx_user_user_id ON users(user_id);
        '''
        # Executing an SQL query:
        cursor.execute(create_table_users)

        create_table_statistics = '''
        CREATE TABLE IF NOT EXISTS statistics (
            id SERIAL PRIMARY KEY,
            date TIMESTAMP,
            model VARCHAR(50),
            tokens INTEGER,
            price_1 FLOAT,
            price FLOAT,
            user_id VARCHAR,
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        );
        '''
        cursor.execute(create_table_statistics)

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