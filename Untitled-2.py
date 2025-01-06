import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os

def open_file():
    file_path = filedialog.askopenfilename(title="Выберите CSV файл", filetypes=[("CSV файлы", "*.csv")])
    if file_path:
        try:
            data = pd.read_csv(file_path)
            return data
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при загрузке файла: {e}")
            return None
    return None

def calculate_stress(load, area):
    return load / area

def convert_strain(strain, height):
    return strain / height

def approximate_curve(strain, stress, threshold_percentage):
    # Пример аппроксимации
    return strain, stress

def calculate_youngs_modulus(strain, stress):
    # Пример расчета модуля Юнга
    return np.gradient(stress, strain)

def save_data(data_dict, folder_path, save_csv, save_xlsx, save_opju):
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    for key, df in data_dict.items():
        if save_csv:
            df.to_csv(os.path.join(folder_path, f"{key}.csv"), index=False)
        if save_xlsx:
            df.to_excel(os.path.join(folder_path, f"{key}.xlsx"), index=False)
        # Добавьте сохранение в формате opju, если необходимо

def plot_approximated_curve(strain, stress, approx_strain, approx_stress, youngs_moduli, show_youngs_modulus, show_segments_in_legend, show_original):
    plt.figure(figsize=(10, 6))
    if show_original:
        plt.plot(strain, stress, label="Оригинальные данные")
    plt.plot(approx_strain, approx_stress, label="Аппроксимированные данные")
    if show_youngs_modulus:
        plt.plot(approx_strain[1:], youngs_moduli, label="Модуль Юнга")
    plt.xlabel("Деформация")
    plt.ylabel("Напряжение")
    plt.legend()
    plt.grid(True)
    plt.show()

def process_data():
    try:
        data = open_file()
        if data is None:
            return

        load = data['load'].values
        strain = data['strain'].values

        A = float(entry_area.get())
        H = float(entry_height.get())
        threshold = float(entry_threshold.get())

        if A <= 0 or H <= 0:
            raise ValueError("Площадь поперечного сечения и высота образца должны быть положительными числами.")

        stress = calculate_stress(load, A)
        strain_rel = convert_strain(strain, H)
        approx_strain, approx_stress = approximate_curve(strain_rel, stress, threshold_percentage=threshold)
        youngs_moduli = calculate_youngs_modulus(approx_strain, approx_stress)

        folder_path = os.path.join(os.getcwd(), 'output_data')
        data_dict = {
            "Оригинальные данные": pd.DataFrame({"strain": strain_rel, "stress": stress}),
            "Аппроксимированные данные": pd.DataFrame({"strain": approx_strain, "stress": approx_stress}),
            "Модуль Юнга": pd.DataFrame({"strain": approx_strain[1:], "youngs_modulus": youngs_moduli}),
        }
        save_data(data_dict, folder_path, save_csv.get(), save_xlsx.get(), save_opju.get())

        plot_approximated_curve(strain_rel, stress, approx_strain, approx_stress, youngs_moduli,
                                show_youngs_modulus.get(), show_segments_in_legend.get(), show_original.get())
    except ValueError as e:
        messagebox.showerror("Ошибка", f"Проверьте ввод параметров. Ошибка: {e}")
    except Exception as e:
        messagebox.showerror("Ошибка", f"Произошла ошибка: {e}")

# Создание GUI
root = tk.Tk()
root.title("Аппроксимация кривой напряжение-деформация")
file_label = tk.Label(root, text="Выберите CSV файл", padx=20, pady=10)
file_label.grid(row=0, column=0, columnspan=3)

open_button = tk.Button(root, text="Откройте файл", command=process_data)
open_button.grid(row=1, column=0, columnspan=3, pady=10)

tk.Label(root, text="Площадь поперечного сечения (mm²)").grid(row=2, column=0, padx=10, pady=5)
entry_area = tk.Entry(root)
entry_area.grid(row=2, column=1, padx=10, pady=5)
entry_area.insert(0, "10")

tk.Label(root, text="Высота образца (mm)").grid(row=3, column=0, padx=10, pady=5)
entry_height = tk.Entry(root)
entry_height.grid(row=3, column=1, padx=10, pady=5)
entry_height.insert(0, "50")

tk.Label(root, text="Порог аппроксимации (%)").grid(row=4, column=0, padx=10, pady=5)
entry_threshold = tk.Entry(root)
entry_threshold.grid(row=4, column=1, padx=10, pady=5)
entry_threshold.insert(0, "5")

save_csv = tk.BooleanVar()
tk.Checkbutton(root, text="Сохранить в CSV", variable=save_csv).grid(row=5, column=0, padx=10, pady=5)

save_xlsx = tk.BooleanVar()
tk.Checkbutton(root, text="Сохранить в XLSX", variable=save_xlsx).grid(row=5, column=1, padx=10, pady=5)

save_opju = tk.BooleanVar()
tk.Checkbutton(root, text="Сохранить в OPJU", variable=save_opju).grid(row=5, column=2, padx=10, pady=5)

show_youngs_modulus = tk.BooleanVar()
tk.Checkbutton(root, text="Показать модуль Юнга", variable=show_youngs_modulus).grid(row=6, column=0, padx=10, pady=5)

show_segments_in_legend = tk.BooleanVar()
tk.Checkbutton(root, text="Показать сегменты в легенде", variable=show_segments_in_legend).grid(row=6, column=1, padx=10, pady=5)

show_original = tk.BooleanVar()
tk.Checkbutton(root, text="Показать оригинальные данные", variable=show_original).grid(row=6, column=2, padx=10, pady=5)

root.mainloop()