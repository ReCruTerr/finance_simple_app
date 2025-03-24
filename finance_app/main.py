from db import init_db
from ui import show_login_window, show_register_window
import tkinter as tk
def show_start_window():
    def open_login():
        start_window.destroy()
        show_login_window()
    def open_register():
        start_window.destroy()
        show_register_window()

    start_window = tk.Tk()
    start_window.title("Finance App")
    start_window.geometry("200x150")

    tk.Label(start_window, text="Добро пожаловать!").pack(pady=10)
    tk.Button(start_window, text="Войти", command=open_login).pack(pady=10)
    tk.Button(start_window, text="Регистрация", command=open_register).pack(pady=10)
    
    start_window.mainloop()

show_start_window()