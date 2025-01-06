# Внимание при вводе данных:
# Максимальное значение деформации в мм;
# Значения силы в кN
# Максимальное значение (предел прочности) в Н/mm квадратный, т.е. МПа
# Lmax - удлинение в %
#
#
#
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from pathlib import Path
import os

# Инициализируем глобальные переменные
strain = None
load = None
selected_points = []

# Функция для загрузки данных из файла с проверкой на наличие нужных столбцов
def load_data(filepath):
    data = pd.read_csv(filepath)
    if 'strain' not in data.columns or 'load' not in data.columns:
        raise ValueError("Файл должен содержать колонки 'strain' и 'load'.")
    return data['strain'].values, data['load'].values

# Функция для расчёта напряжения
def calculate_stress(load, A):
    load_N = load * 1e3  # перевод нагрузки из кН в Н
    A_m2 = A * 1e6      # перевод площади из мм² в м²
    stress_MPa = load_N /A_m2 / 1e6  # перевод в МПа
    return stress_MPa

# Функция для преобразования деформации в относительные единицы
def convert_strain(strain, H):
    return strain / H / 10  # преобразование деформации

# Функция для выбора точек на графике
def select_points(event):
    global selected_points
    if event.xdata is not None and event.ydata is not None:
        ix, iy = event.xdata, event.ydata  # Получаем координаты клика
        selected_points.append((ix, iy))   # Добавляем точку в список выбранных точек
        print(f"Выбрана точка: {ix}, {iy}")
        ax.plot(ix, iy, 'ro')  # Отмечаем точку на графике
        ax.annotate(f'({ix:.2f}, {iy:.2f})', (ix, iy), fontsize=9, color='red')
        fig.canvas.draw()

# Функция для аппроксимации кривой
def approximate_curve(strain, stress, threshold_percentage):
    approx_strain, approx_stress = [], []
    max_index = np.argmax(stress)
    i = 0

    while i < len(stress) - 1:
        start_point = i
        approx_strain.append(strain[start_point])
        approx_stress.append(stress[start_point])

        while i + 2 < len(stress):
            if stress[start_point] != 0:  # Проверяем, что напряжение не равно нулю
                relative_difference = abs(stress[i + 2] - stress[start_point]) / stress[start_point]
            else:
                relative_difference = float('inf')  # Если напряжение равно нулю, избегаем деления на ноль

            if relative_difference <= threshold_percentage:
                i += 2
            else:
                break

        if start_point < max_index <= i:
            approx_strain.append(strain[max_index])
            approx_stress.append(stress[max_index])
            i = max_index

        approx_strain.append(strain[i])
        approx_stress.append(stress[i])
        i += 1

    if approx_strain[-1] != strain[-1]:
        approx_strain.append(strain[-1])
        approx_stress.append(stress[-1])

    return np.array(approx_strain), np.array(approx_stress)

# Функция для расчёта тангенциального модуля отрезка
def calculate_youngs_modulus(approx_strain, approx_stress):
    youngs_moduli = []
    for i in range(1, len(approx_strain)):
        delta_stress = approx_stress[i] - approx_stress[i - 1]
        delta_strain = approx_strain[i] - approx_strain[i - 1]
        if delta_strain != 0:
            youngs_moduli.append(delta_stress / delta_strain)
        else:
            youngs_moduli.append(None)
    return youngs_moduli

# Функция для сохранения данных
def save_data(data_dict, folder_path, save_csv, save_xlsx, save_opju):
    folder_path = Path(folder_path)
    folder_path.mkdir(exist_ok=True)

    if save_csv:
        for name, df in data_dict.items():
            safe_name = "".join([c if c.isalnum() or c in (' ', '_') else '_' for c in name])
            df.to_csv(folder_path / f"{safe_name}.csv", index=False)

    if save_xlsx:
        with pd.ExcelWriter(folder_path / 'data.xlsx') as writer:
            for name, df in data_dict.items():
                sheet_name = name[:31]
                df.to_excel(writer, sheet_name=sheet_name, index=False)

    if save_opju:
        try:
            import originpro as op
            opproj = op.new()
            for name, df in data_dict.items():
                book = op.new_book()
                sheet = book[0]
                sheet.from_df(df)
            opproj.save(folder_path / 'data.opju')
        except ImportError:
            messagebox.showerror("Ошибка", "Не удалось импортировать OriginPro.")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при сохранении в Origin Pro: {e}")

# Функция для построения графика
def plot_approximated_curve(strain, stress, approx_strain, approx_stress, youngs_moduli, show_youngs_modulus, show_segments_in_legend, show_original=True):
    global fig, ax
    fig, ax = plt.subplots(figsize=(10, 6))

    if show_original:
        ax.plot(strain, stress, label="Оригинальная кривая", linestyle='-', marker='o')

    colors = plt.cm.tab10(np.linspace(0, 1, len(approx_strain) - 1))
    for i in range(1, len(approx_strain)):
        label = f"Участок {i}" if show_segments_in_legend else "Аппроксимация" if i == 1 else None
        ax.plot(approx_strain[i-1:i+1], approx_stress[i-1:i+1], color=colors[i-1], linestyle='-', marker='x', label=label)

        if show_youngs_modulus and youngs_moduli[i - 1] is not None:
            mid_strain = (approx_strain[i] + approx_strain[i - 1]) / 2
            mid_stress = (approx_stress[i] + approx_stress[i - 1]) / 2
            ax.annotate(f"E = {youngs_moduli[i - 1]:.2e} Па", (mid_strain, mid_stress), fontsize=8, ha='center')

    ax.set_xlabel("Относительная деформация (мм/мм)")
    ax.set_ylabel("Напряжение (МПа)")
    ax.set_title("Аппроксимация кривой напряжение-деформация с модулем Юнга")
    ax.grid(True)

    handles, labels = ax.get_legend_handles_labels()
    unique = dict(zip(labels, handles))
    plt.legend(unique.values(), unique.keys())
    fig.canvas.mpl_connect('button_press_event', select_points)
    plt.show()

# Функция для открытия файла
def open_file():
    global strain, load
    filepath = filedialog.askopenfilename(title="Выберите CSV файл", filetypes=(("CSV files", "*.csv"), ("all files", "*.*")))
    if filepath:
        file_label.config(text=f"Файл: {filepath}")
        try:
            strain, load = load_data(filepath)
            print(f"Данные загружены: strain={strain[:5]}, load={load[:5]}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при загрузке файла: {e}")

# Функция для построения графика
def plot_graph():
    global strain, load
    try:
        if strain is None or load is None:
            raise ValueError("Данные не загружены. Пожалуйста, выберите файл.")

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
            "Аппроксимированные данные": pd.DataFrame({"strain": strain, "stress": stress}),
            "Модуль Юнга": pd.DataFrame({"strain": approx_strain[1:], "youngs_modulus": youngs_moduli}),
        }
        save_data(data_dict, folder_path, save_csv.get(), save_xlsx.get(), save_opju.get())

        plot_approximated_curve(strain_rel, stress, approx_strain, approx_stress, youngs_moduli,
                                show_youngs_modulus.get(), show_segments_in_legend.get(), show_original.get())
    except ValueError as e:
        messagebox.showerror("Ошибка", f"Проверьте ввод параметров. Ошибка: {e}")
    except Exception as e:
        messagebox.showerror("Ошибка", f"Произошла ошибка: {e}")

#Создание GUI
root = tk.Tk()
root.title ("Аппроксимация кривой напряжение-деформация")
file_label = tk.Label(root, text="Выберите CSV файл", padx=20, pady=10)
file_label.grid(row=0, column=0, columnspan=3)

open_button = tk.Button(root, text="Откройте файл", command=open_file)
open_button.grid(row=1, column=0, columnspan=3, pady=10)

tk.Label(root, text="Площадь поперечного сечения (mm²)").grid(row=2, column=0, padx=10, pady=5)
entry_area = tk.Entry(root)
entry_area.grid(row=2, column=1, padx=10, pady=5)
entry_area.insert(0, "10")

tk.Label(root, text="Высота образца (мм)").grid(row=3, column=0, padx=10, pady=5)
entry_height = tk.Entry(root)
entry_height.grid(row=3, column=1, padx=10, pady=5)
entry_height.insert(0, "50")

tk.Label(root, text="Порог аппрохимации").grid(row=4, column=0, padx=10, pady=5)
entry_threshold = tk.Entry(root)
entry_threshold.grid(row=4, column=1, padx=10, pady=5)
entry_threshold.insert(0, "0.05")

show_original = tk.IntVar(value=1)
tk.Checkbutton(root, text="Оригинальная кривая", variable=show_original).grid(row=6, column=0, padx=10, pady=5)

show_youngs_modulus = tk.IntVar(value=1)
tk.Checkbutton(root, text="Показать модуль", variable=show_youngs_modulus).grid(row=6, column=1, padx=10, pady=5)

show_segments_in_legend = tk.IntVar(value=0)
tk.Checkbutton(root, text="Показать сегменты в легенде", variable=show_segments_in_legend).grid(row=7, column=0, columnspan=2, padx=10, pady=5)

save_csv = tk.IntVar(value=1)
tk.Checkbutton(root, text="Сохранить в формате CSV", variable=save_csv).grid(row=8, column=0, padx=10, pady=5)

save_xlsx = tk.IntVar(value=1)
tk.Checkbutton(root, text="Сохранить в формате XLSX", variable=save_xlsx).grid(row=8, column=1, padx=10, pady=5)

save_opju = tk.IntVar(value=0)
tk.Checkbutton(root, text="Сохранить в формате OPJU", variable=save_opju).grid(row=8, column=0, padx=10, pady=5)

plot_button = tk.Button(root, text="Построить кривую", command=plot_graph)
plot_button.grid(row=9, column=0, columnspan=3, pady=10)

# import tkinter as tk
# from tkinter import ttk





# import tkinter as tk
# from tkinter import ttk
# from tkinter import filedialog
#
# def create_tooltip(widget, text):
#     tooltip = tk.Toplevel(widget)
#     tooltip.withdraw()
#     tooltip.overrideredirect(True)
#     tooltip_label = ttk.Label(tooltip, text=text, relief='solid', background='lightyellow', padding=(5, 3))
#     tooltip_label.pack()
#
#     def show_tooltip(event):
#         tooltip.geometry(f"+{event.x_root + 20}+{event.y_root + 10}")
#         tooltip.deiconify()
#
#     def hide_tooltip(event):
#         tooltip.withdraw()
#
#     widget.bind("<Enter>", show_tooltip)
#     widget.bind("<Leave>", hide_tooltip)
#
# def open_file():
#     try:
#         filename = filedialog.askopenfilename(
#             title="Откройте файл CSV",
#             filetypes=[("CSV файлы", "*.csv"), ("Все файлы", "*.*")]
#         )
#         if filename:
#             print(f"Файл открыт: {filename}")
#         else:
#             print("Файл не выбран.")
#     except Exception as e:
#         print(f"Произошла ошибка при открытии файла: {e}")
#
# def plot_graph():
#     print("Построение графика...")
#
# root = tk.Tk()
# root.title("Интерфейс с подсказками")
#
# # Метка для выбора файла
# file_label = tk.Label(root, text="Выберите CSV файл", padx=20, pady=10)
# file_label.grid(row=0, column=0, columnspan=3)
# create_tooltip(file_label, "Здесь выберите файл в формате CSV.")
#
# # Кнопка для открытия файла
# open_button = tk.Button(root, text="Откройте файл", command=open_file)
# open_button.grid(row=1, column=0, columnspan=3, pady=10)
# create_tooltip(open_button, "Нажмите, чтобы открыть файл.")
#
# # Поля ввода с поясняющими метками
# entry_area_label = tk.Label(root, text="Площадь поперечного сечения (mm²)")
# entry_area_label.grid(row=2, column=0, padx=10, pady=5)
# entry_area = tk.Entry(root)
# entry_area.grid(row=2, column=1, padx=10, pady=5)
# entry_area.insert(0, "10")
# create_tooltip(entry_area, "Введите площадь поперечного сечения образца.")
#
# entry_height_label = tk.Label(root, text="Высота образца (мм)")
# entry_height_label.grid(row=3, column=0, padx=10, pady=5)
# entry_height = tk.Entry(root)
# entry_height.grid(row=3, column=1, padx=10, pady=5)
# entry_height.insert(0, "50")
# create_tooltip(entry_height, "Введите высоту образца.")
#
# entry_threshold_label = tk.Label(root, text="Порог аппроксимации")
# entry_threshold_label.grid(row=4, column=0, padx=10, pady=5)
# entry_threshold = tk.Entry(root)
# entry_threshold.grid(row=4, column=1, padx=10, pady=5)
# entry_threshold.insert(0, "0.05")
# create_tooltip(entry_threshold, "Установите порог аппроксимации для кривой.")
#
# # Чек-боксы
# show_original = tk.IntVar(value=1)
# original_check = tk.Checkbutton(root, text="Оригинальная кривая", variable=show_original)
# original_check.grid(row=6, column=0, padx=10, pady=5)
# create_tooltip(original_check, "Показать оригинальную кривую на графике.")
#
# show_youngs_modulus = tk.IntVar(value=1)
# youngs_modulus_check = tk.Checkbutton(root, text="Показать модуль", variable=show_youngs_modulus)
# youngs_modulus_check.grid(row=6, column=1, padx=10, pady=5)
# create_tooltip(youngs_modulus_check, "Показать модуль упругости на графике.")
#
# show_segments_in_legend = tk.IntVar(value=0)
# segments_in_legend_check = tk.Checkbutton(root, text="Показать сегменты в легенде", variable=show_segments_in_legend)
# segments_in_legend_check.grid(row=7, column=0, columnspan=2, padx=10, pady=5)
# create_tooltip(segments_in_legend_check, "Показать сегменты аппроксимации")

root.mainloop()