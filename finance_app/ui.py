import tkinter as tk
from tkinter import messagebox
import matplotlib.pyplot as plt
from logic import login, register, set_balance, add_transaction, get_profile_data
from decimal import Decimal
current_user = None

def show_login_window():
    def try_login():
        global current_user
        user = login(email_entry.get(), password_entry.get())
        if user:
            current_user = user
            login_window.destroy()
            show_main_window()
        
    login_window = tk.Tk()
    login_window.title("Вход")
    login_window.geometry("300x200")

    tk.Label(login_window, text="Email: ").pack(pady=5)
    email_entry = tk.Entry(login_window)
    email_entry.pack()

    tk.Label(login_window, text="Password: ").pack(pady=5)
    password_entry = tk.Entry(login_window, show="*")
    password_entry.pack()

    tk.Button(login_window, text="Войти", command=try_login).pack(pady=20)
    tk.Button(login_window, text="Регистрация", command=show_register_window).pack(pady=20)

    
def show_register_window():
    def try_register():
        success, msg = register(
            email_entry.get(),
            password_entry.get(),
            password_confirmed_entry.get(),
            username_entry.get()
        )
        messagebox.showinfo('Результат: ', msg)
        if success:
            register_window.destroy()
    register_window = tk.Tk()
    register_window.title("Регистрация")
    register_window.geometry("300x300")

    tk.Label(register_window, text="Email ").pack(pady=5)
    email_entry = tk.Entry(register_window)
    email_entry.pack()

    tk.Label(register_window, text="Password ").pack(pady=5)
    password_entry = tk.Entry(register_window, show="*")
    password_entry.pack()

    tk.Label(register_window, text="Password Confirm ").pack(pady=5)
    password_confirmed_entry = tk.Entry(register_window, show="*")
    password_confirmed_entry.pack()

    tk.Label(register_window, text="Username ").pack(pady=5)
    username_entry = tk.Entry(register_window)
    username_entry.pack()
    
    tk.Button(register_window, text="Зарегистрироваться", command=try_register).pack(pady=20)

def show_main_window():
    global main_window, balance_field, amount_entry, category_entry, type_var, category_var

    def update_balance():
        global current_user
        try:
            new_balance = float(balance_entry.get())
        except ValueError:
            messagebox.showerror("Ошибка", "Введите корректное число!")
            return
        
        success, msg = set_balance(current_user['id'], new_balance)
        messagebox.showinfo("Результат", msg)
        
        if success:
            # Обновляем баланс в current_user
            current_user['balance'] = new_balance
            
            # Обновляем текстовое поле с балансом
            balance_field.config(text=f"Текущий баланс = {new_balance}")

    def add_trans():
        success, msg = add_transaction(current_user['id'], float(amount_entry.get()), int(category_entry.get()), type_var.get())
        messagebox.showinfo("Результат", msg)
    
    def show_profile():
        data, msg = get_profile_data(current_user['id'])
        if data:
            plt.clf()
            if data["transactions"]:
                dates = [t[1] for t in data['transactions']]
                amounts = [t[0] if t[2] == 'income' else -t[0] for t in data['transactions']]
                plt.plot(dates, amounts, marker='o')
                plt.title("Транзакции")
                plt.xlabel("Дата")
                plt.ylabel("Сумма")
                plt.show()
            else:
                messagebox.showinfo("Информация", "Нет данных о транзакциях.")
        else:
            messagebox.showerror("Ошибка", msg)

    main_window = tk.Tk()
    main_window.title(f"Finance App of {current_user['username']}")
    main_window.geometry("400x500")

    tk.Label(main_window, text="Баланс").pack(pady=5)
    balance_entry = tk.Entry(main_window)
    balance_entry.pack()
    tk.Button(main_window, text="Обновить баланс", command=update_balance).pack(pady=10)

    tk.Label(main_window, text="Сумма транзакции").pack(pady=5)
    amount_entry = tk.Entry(main_window)
    amount_entry.pack()

    tk.Label(main_window, text="ID категории").pack(pady=5)
    category_entry = tk.Entry(main_window)
    category_entry.pack()

    type_var = tk.StringVar(value="expense")
    tk.Radiobutton(main_window, text="Доход", variable=type_var, value="income").pack()
    tk.Radiobutton(main_window, text="Расход", variable=type_var, value="expense").pack()

    tk.Button(main_window, text="Добавить транзакцию", command=add_trans).pack(pady=10)

    balance_field = tk.Label(main_window, text=f"Текущий баланс = {current_user['balance']}")
    balance_field.pack(pady=10)

    tk.Button(main_window, text="Обновить профиль", command=show_profile).pack(pady=10)

    main_window.mainloop()