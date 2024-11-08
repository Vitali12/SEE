#Добавим третью таблицу, содержащую столбцы strain и youngs_modulus.
#Мы объединим её с уже существующей таблицей по значению strain, аналогично
#тому, как это было сделано с ко-лонкой stress из второй таблицы.

#Вот обновленный код, который добавляет данные из третьей таблицы:
   
#Три кривые.py
### Что добавлено:
#1. Третья таблица: Теперь код загружает третью таблицу, которая содержит колонки strain и youngs_modulus.
#2. Объединение с третьей таблицей: Мы объединяем таблицы по колонке strain, добавляя колон-ку youngs_modulus в итоговую таблицу.
#3. Сохранение итоговой таблицы: Как и раньше, программа сохраняет итоговую таблицу в CSV файл.

### Итоговая таблица будет содержать:
#- strain: значения из первой таблицы.
#- stress_1: значения из первой таблицы.
#- stress_2: значения из второй таблицы (если значение strain совпадает).
#- youngs_modulus: значения из третьей таблицы (если значение strain совпадает).
# ИСХОДНЫЕ ДАННЫЕ В КАТАЛОГЕ: ИСКУССТВЕННЫЙ ИНТЕЛЛЕКТ\Syntx AI\Объединение оригинальной и аппроксимированной кривой\
import pandas as pd
import tkinter as tk
from tkinter import filedialog, messagebox

# Функция для загрузки CSV файла
def load_csv_file():
    file_path = filedialog.askopenfilename(title="Выберите файл CSV", filetypes=[("CSV файлы", "*.csv")])
    if file_path:
        try:
            data = pd.read_csv(file_path)
            return data
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при загрузке файла: {e}")
            return None
    return None

# Функция для синхронизации данных по strain и создания итоговой таблицы
def synchronize_data():
    # Загружаем первую таблицу
    data1 = load_csv_file()
    if data1 is None:
        return

    # Загружаем вторую таблицу
    data2 = load_csv_file()
    if data2 is None:
        return

    # Загружаем третью таблицу
    data3 = load_csv_file()
    if data3 is None:
        return

    try:
        # Объединяем данные первой и второй таблицы по strain
        merged_data = pd.merge(data1, data2[['strain', 'stress']], on='strain', how='left', suffixes=('_1', '_2'))

        # Объединяем получившуюся таблицу с третьей таблицей по strain
        final_data = pd.merge(merged_data, data3[['strain', 'youngs_modulus']], on='strain', how='left')

        # Сохраняем результат в новую таблицу
        save_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV файлы", "*.csv")])
        if save_path:
            final_data.to_csv(save_path, index=False)
            messagebox.showinfo("Успех", "Итоговая таблица успешно сохранена!")
        else:
            messagebox.showwarning("Отмена", "Сохранение отменено.")

    except Exception as e:
        messagebox.showerror("Ошибка", f"Ошибка при обработке данных: {e}")

# Создание интерфейса с помощью tkinter
root = tk.Tk()
root.title("Синхронизация данных")

# Кнопка для загрузки таблиц и синхронизации данных
sync_button = tk.Button(root, text="Загрузить таблицы и синхронизировать данные", command=synchronize_data)
sync_button.pack(padx=20, pady=20)

# Запуск основного цикла Tkinter
root.mainloop()
