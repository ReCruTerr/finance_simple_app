import psycopg2
from psycopg2 import Error

DB_CONFIG = {
    'dbname': 'finance_app',
    'user': 'postgres',
    'password': 'finance_app_pass',  # Замените на свой
    'host': 'localhost',
    'port': '5432'
}
def get_connection():
    try:
        connection = psycopg2.connect(**DB_CONFIG)
        return connection
    except Error as e:
        print(f"Ошибка подключения к базе данных: {e}")
        return None

def init_db():
    connection = get_connection()
    if not connection:
        return
    
    try:
        cursor = connection.cursor()
        
        # Таблица пользователей
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                email VARCHAR(255) UNIQUE NOT NULL,
                password VARCHAR(255) NOT NULL,
                username VARCHAR(100) NOT NULL,
                balance DECIMAL(10, 2) DEFAULT 0.00
            );
        """)
        
        # Таблица категорий
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS categories (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                is_default BOOLEAN DEFAULT FALSE
            );
        """)
        
        # Таблица транзакций
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                amount DECIMAL(10, 2) NOT NULL,
                category_id INTEGER REFERENCES categories(id) ON DELETE SET NULL,
                transaction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                type VARCHAR(10) CHECK (type IN ('income', 'expense'))
            );
        """)
        
        # Таблица целей бюджета
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS budget_goals (
                id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                amount DECIMAL(10, 2) NOT NULL,
                category_id INTEGER REFERENCES categories(id) ON DELETE SET NULL,
                start_date DATE NOT NULL,
                end_date DATE NOT NULL
            );
        """)
        
        # Добавление предустановленных категорий
        cursor.execute("""
            INSERT INTO categories (name, is_default) 
            VALUES 
                ('Еда', TRUE),
                ('Транспорт', TRUE),
                ('Развлечения', TRUE)
            ON CONFLICT DO NOTHING;
        """)
        
        connection.commit()
        print("База данных успешно инициализирована.")
    
    except Error as e:
        print(f"Ошибка при создании таблиц: {e}")
    finally:
        cursor.close()
        connection.close()  