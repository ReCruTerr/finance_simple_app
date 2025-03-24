import bcrypt
from db import get_connection
from decimal import Decimal
def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

def check_password(password, hashed_password):
    try:
        # Если хеш в шестнадцатеричном формате, декодируем его
        if isinstance(hashed_password, str) and hashed_password.startswith(r"\x"):
            hex_hash_cleaned = hashed_password.replace(r"\x", "")
            hashed_password_bytes = bytes.fromhex(hex_hash_cleaned)
            hashed_password = hashed_password_bytes.decode('utf-8')

        # Проверяем пароль
        if isinstance(password, str):
            password = password.encode('utf-8')
        if isinstance(hashed_password, str):
            hashed_password = hashed_password.encode('utf-8')
        return bcrypt.checkpw(password, hashed_password)
    except Exception as e:
        print(f"Ошибка проверки пароля: {e}")
        return False

def register(email, password, password_confirmed, username):
    if password != password_confirmed:
        return False, "Пароли не совпадают!"
    connection = get_connection()
    if not connection:
        return False, "Ошибка подключения к базе!"
    try:
        cursor = connection.cursor()
        hashed_password = hash_password(password)
        cursor.execute("""
        INSERT INTO users(email, password, username)
        VALUES (%s, %s, %s)
""", (email, hashed_password, username))
        connection.commit()
        return True, "Регистрация успешна!"
    except Exception as exc:
        return False, f"Ошибка регистрации:{exc}"
    finally:
        cursor.close()
        connection.close()
    
def login(email, password):
    connection = get_connection()
    if not connection:
        return False, "Ошибка соединения"
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT id, password, username, balance FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()

        if user and check_password(password, user[1]):
            return {'id': user[0], 'username': user[2], 'balance': user[3]}
        else:
            return None, "Неверный email или пароль!"
    except Exception as ex:
        return None, f"Ошибка входа:{ex}"
    finally:
        cursor.close()
        connection.close()
    
def set_balance(user_id, balance):
    connection = get_connection()
    if not connection:
        return False, "Ошибка соединения"
    try:
        cursor = connection.cursor()
        cursor.execute(" UPDATE users SET balance = %s WHERE id = %s ", (balance,user_id))
        connection.commit()
        return True, f"Баланс изменен на {balance}"

    except Exception as exc:
        return False, f"Ошибка при изменении баланса! {exc}"
    finally:
        cursor.close()
        connection.close()



def add_transaction(user_id, amount, category_id, type_):
    if type_ not in ['income', 'expense']:
        return False, "Неверный тип транзакции!"
    
    connection = get_connection()
    if not connection:
        return False, "Ошибка соединения"
    
    try:
        cursor = connection.cursor()
        
        # Вставляем новую транзакцию
        cursor.execute("""
        INSERT INTO transactions(user_id, amount, category_id, type)
        VALUES (%s, %s, %s, %s)
        """, (user_id, amount, category_id, type_))
        
        # Получаем текущий баланс пользователя
        cursor.execute("SELECT balance FROM users WHERE id = %s", (user_id,))
        current_balance = cursor.fetchone()[0]
        
        # Преобразуем current_balance в float, если это decimal.Decimal
        if isinstance(current_balance, Decimal):
            current_balance = float(current_balance)
        
        # Вычисляем новый баланс
        new_balance = 0
        if type_ == 'income':
            new_balance = current_balance + amount
        elif type_ == 'expense':
            if current_balance < amount:
                return False, "Недостаточно средств для расхода!"
            new_balance = current_balance - amount
        
        # Обновляем баланс пользователя
        cursor.execute("UPDATE users SET balance = %s WHERE id = %s", (new_balance, user_id))
        
        # Фиксируем изменения
        connection.commit()
        return True, f"Транзакция добавлена. Новый баланс = {new_balance}"
    
    except Exception as exc:
        # Откатываем изменения в случае ошибки
        connection.rollback()
        return False, f"Ошибка: {exc}"
    
    finally:
        # Закрываем соединение и курсор
        if cursor:
            cursor.close()
        if connection:
            connection.close()

def get_profile_data(user_id):
    connection = get_connection()
    if not(connection):
        return None, "Ошибка соединения!"
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT balance FROM users WHERE id = %s",(user_id,))
        user = cursor.fetchone()
        if not user:
            return None, "Пользователь не найден"
        balance = user[0]
        
        cursor.execute("""\
            SELECT amount,transaction_date, type FROM transactions WHERE user_id = %s ORDER BY transaction_date DESC LIMIT 10
            """,(user_id,))
        transactions = cursor.fetchall()

        cursor.execute("""
            SELECT c.name, SUM(t.amount) as total FROM transactions t JOIN categories c ON t.category_id = c.id
            WHERE t.user_id = %s AND t.type = 'expense' GROUP BY c.name ORDER BY total DESC LIMIT 3
""",(user_id,))
        top_categories = cursor.fetchall()

        return {
            'balance':balance,
            'transactions': transactions,
            'top_categories':top_categories
        }, "Данные профиля получены!"
    except Exception as exc:
        return None, f"Ошибка {exc}"

    finally:    
        cursor.close()
        connection.close()