import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
import numpy as np

# Функция для загрузки CSV файла
def load_csv_file(file_path):
    try:
        data = pd.read_csv(file_path)
        strain = data['strain'].values
        stress = data['stress'].values
        return strain, stress
    except Exception as e:
        messagebox.showerror("Ошибка", f"Ошибка при загрузке файла: {e}")
        return None, None

# Функция для подгонки данных и построения графика
def fit_and_plot():
    file_path = 'd:/projects/see/experimental_data/stress_strain_data.csv'
    strain, stress = load_csv_file(file_path)
    if strain is None or stress is None:
        return

    # Определяем функцию подгонки
    def model_func(x, param3, param4):
        param1 = 200
        param2 = 7
        return param1 * (x / param2) * np.exp(1/param3) * (1 - (x**param3 / param2**param3)**param4)

    # Начальные значения для param3 и param4
    initial_guess = [1, 1]

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

        # Выводим оптимальные значения параметров
        print(f"Оптимальные значения параметров: param3={popt[0]:.2f}, param4={popt[1]:.2f}")

    except Exception as e:
        messagebox.showerror("Ошибка", f"Ошибка при подгонке данных: {e}")

# Создание интерфейса с помощью tkinter
root = tk.Tk()
root.title("Анализ данных и подгонка кривой")

# Кнопка для выполнения подгонки и построения графика
fit_button = tk.Button(root, text="Fit and Plot", command=fit_and_plot)
fit_button.grid(row=0, column=0, padx=5, pady=5)

root.mainloop()