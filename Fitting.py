import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
import tkinter as tk
from tkinter import filedialog, messagebox

# Функция для загрузки CSV файла
def load_csv_file():
    file_path = filedialog.askopenfilename(title="Выберите файл CSV", filetypes=[("CSV файлы", "*.csv")])
    if file_path:
        try:
            data = pd.read_csv(file_path)
            strain = data['strain'].values
            stress = data['stress'].values
            return strain, stress
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при загрузке файла: {e}")
            return None, None
    return None, None

# Функция для получения параметров из таблицы
def get_params():
    params = []
    for entry in param_entries:
        try:
            params.append(float(entry.get()))
        except ValueError:
            params.append(1)  # Используем 1 по умолчанию, если не введено значение
    return params

# Функция для подгонки данных и построения графика
def fit_and_plot():
    strain, stress = load_csv_file()
    if strain is None or stress is None:
        return

    # Получаем функцию подгонки из текстового поля
    fit_func_str = fit_func_entry.get()

    # Определяем функцию подгонки
    def model_func(x, *params):
        # Замена param1, param2 и т.д. на их фактические значения
        local_fit_func_str = fit_func_str
        for i, param in enumerate(params):
            local_fit_func_str = local_fit_func_str.replace(f'param{i+1}', str(param))
        return eval(local_fit_func_str)

    # Получаем параметры, введенные пользователем
    initial_guess = get_params()

    # Выполняем подгонку с помощью curve_fit
    try:
        popt, pcov = curve_fit(model_func, strain, stress, p0=initial_guess)

        # Строим график
        strain_fit = np.linspace(min(strain), max(strain), 100)
        stress_fit = model_func(strain_fit, *popt)

        # График экспериментальных данных и подгонки
        plt.figure(figsize=(8, 6))
        plt.plot(strain, stress, 'bo', label="Experimental data")
        plt.plot(strain_fit, stress_fit, 'r-', label=f"Fitted curve")
        plt.xlabel("Strain")
        plt.ylabel("Stress")
        plt.title("Fitting Experimental Data")
        plt.legend()
        plt.grid(True)
        plt.show()

        # Выводим результат в виде формулы
        fitting_formula = fit_func_str
        for i, param in enumerate(popt):
            fitting_formula = fitting_formula.replace(f'param{i+1}', f'{param:.2e}')
        print(f"Подогнанная формула: {fitting_formula}")

    except Exception as e:
        messagebox.showerror("Ошибка", f"Ошибка при подгонке данных: {e}")

# Создание интерфейса с помощью tkinter
root = tk.Tk()
root.title("Анализ данных и подгонка кривой")

# Поле для ввода функции подгонки
tk.Label(root, text="Введите функцию подгонки (используйте param1, param2,... для параметров)").pack(padx=10, pady=5)
fit_func_entry = tk.Entry(root, width=50)
fit_func_entry.pack(padx=10, pady=5)
fit_func_entry.insert(0, "param1 * ((x / param2) * np.exp(1 - (x / param2)**param3))")  # Пример функции

# Таблица для ввода параметров
param_entries = []
for i in range(5):  # Допустим, у нас 5 параметров
    frame = tk.Frame(root)
    frame.pack(padx=10, pady=5)
    tk.Label(frame, text=f"param{i+1}:").pack(side=tk.LEFT)
    entry = tk.Entry(frame, width=10)
    entry.pack(side=tk.LEFT)
    entry.insert(0, "1")  # Начальное значение
    param_entries.append(entry)

# Кнопка для запуска подгонки
fit_button = tk.Button(root, text="Загрузить CSV и выполнить подгонку", command=fit_and_plot)
fit_button.pack(padx=20, pady=20)

# Запуск основного цикла Tkinter
root.mainloop()
