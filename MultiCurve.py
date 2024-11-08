
#Для отображения нескольких кривых на одном графике из файлов с заголовками approx_strain_rel (для оси  X ) и
#approx_stress_MPa (для оси  Y ), мы можем создать программу, которая позволяет загружать и отображать несколько графиков

### Как использовать:
# - Нажимайте "Загрузить кривую" для добавления каждой новой кривой.
# - После загрузки всех необходимых кривых, нажмите "Отобразить график" для окончательного вывода графика с легендой.
#
# Этот код позволяет одновременно отображать несколько кривых, каждая из которых будет иметь свою подпись в легенде.

#
#
# Для отображения нескольких кривых на одном графике из файлов с заголовками approx_strain_rel (для оси  X )
# и approx_stress_MPa (для оси  Y ), мы можем создать программу, которая позволяет загружать и отображать
# несколько таких файлов.
#
# Имеется возможность удалять отдельные графики из списка загруженных и кнопку для сохранения оставшихся графиков
# в формате книги и графиков Origin Pro. Для этого обновленного кода воспользуемся библиотекой pyorigin для
# экспорта данных в формат Origin, если она у вас доступна. Если нет, экспорт может быть выполнен в CSV-формате,
# который можно импортировать в Origin Pro.
#
#
# 1. Глобальные переменные: curves_data для хранения загруженных данных и file_names для хранения имен файлов.
# 2. Функция load_curve: Загружает файл, добавляет его в глобальный список данных, отображает график и добавляет имя файла в интерфейсный список curve_listbox.
# 3. Функция delete_curve: Удаляет выбранную кривую из глобального списка данных и интерфейса, перерисовывая график с оставшимися кривыми.
# 4. Функция save_to_origin: Создает проект Origin Pro, добавляет каждый файл как отдельный лист и сохраняет его в указанном месте.

### Примечание:
#Исходные данные в каталоге \Искусственный интеллект\Syntx AI\Несколько кривых на одном графике\



import pandas as pd
import matplotlib.pyplot as plt
from tkinter import Tk, filedialog, Button, Listbox, END
import originpro as op

# Глобальные переменные для хранения данных и имен файлов
curves_data = []
file_names = []

def load_curve():
    """Загружает кривую из файла и добавляет её на график."""
    root = Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(defaultextension='.csv', filetypes=[("CSV files", "*.csv")])

    if file_path:
        df = pd.read_csv(file_path)

        if 'approx_strain_rel' in df.columns and 'approx_stress_MPa' in df.columns:
            # Сохранение данных и имени файла
            curves_data.append(df)
            file_names.append(file_path.split('/')[-1])

            # Обновление списка в интерфейсе
            curve_listbox.insert(END, file_names[-1])

            # Отображение графика сразу
            plt.plot(df['approx_strain_rel'], df['approx_stress_MPa'], label=file_names[-1])
            plt.xlabel('approx_strain_rel')
            plt.ylabel('approx_stress_MPa')
            plt.legend()
            plt.grid(True)
            plt.draw()
        else:
            print(f"Файл {file_path} не содержит нужных колонок.")

def delete_curve():
    """Удаляет выбранную кривую из графика и из списка данных."""
    selected_index = curve_listbox.curselection()
    if selected_index:
        index = selected_index[0]
        del curves_data[index]
        del file_names[index]
        curve_listbox.delete(index)

        # Перерисовка графика с оставшимися кривыми
        plt.cla()
        for i, df in enumerate(curves_data):
            plt.plot(df['approx_strain_rel'], df['approx_stress_MPa'], label=file_names[i])
        plt.xlabel('approx_strain_rel')
        plt.ylabel('approx_stress_MPa')
        plt.legend()
        plt.grid(True)
        plt.draw()
    else:
        print("Выберите кривую для удаления.")

def save_to_origin():
    """Сохраняет оставшиеся кривые в проект Origin Pro."""
    try:
        book = op.new_book()
        book.set_name("Сохраненные Кривые")

        for i, df in enumerate(curves_data):
            sheet = book.add_sheet(file_names[i])
            sheet.from_list(0, df['approx_strain_rel'].tolist(), 'approx_strain_rel')
            sheet.from_list(1, df['approx_stress_MPa'].tolist(), 'approx_stress_MPa')
            sheet.plotxy(0, 1, template='line')

        save_path = filedialog.asksaveasfilename(defaultextension='.opj', filetypes=[("Origin Project", "*.opj")])
        if save_path:
            op.save_as(save_path)
            print(f"Проект Origin Pro успешно сохранен как {save_path}")
    except RuntimeError as e:
        print(f"Ошибка при сохранении в Origin Pro: {e}")

def save_to_excel():
    """Сохраняет оставшиеся кривые в файл Excel."""
    save_path = filedialog.asksaveasfilename(defaultextension='.xlsx', filetypes=[("Excel Files", "*.xlsx")])
    if save_path:
        with pd.ExcelWriter(save_path) as writer:
            for i, df in enumerate(curves_data):
                df.to_excel(writer, sheet_name=file_names[i][:31], index=False)  # Ограничение на длину имени листа Excel - 31 символ
        print(f"Данные успешно сохранены в {save_path}")

# Интерфейс
root = Tk()
root.title("Чтение, удаление и сохранение кривых")

# Кнопка загрузки
button_load = Button(root, text="Загрузить кривую", command=load_curve)
button_load.pack(pady=5)

# Список для отображения загруженных файлов
curve_listbox = Listbox(root, selectmode='single')
curve_listbox.pack(pady=5, fill='both')

# Кнопка удаления выбранной кривой
button_delete = Button(root, text="Удалить выбранную кривую", command=delete_curve)
button_delete.pack(pady=5)

# Кнопка сохранения в формат Origin Pro
button_save_origin = Button(root, text="Сохранить в Origin Pro", command=save_to_origin)
button_save_origin.pack(pady=5)

# Кнопка сохранения в формат Excel
button_save_excel = Button(root, text="Сохранить в Excel", command=save_to_excel)
button_save_excel.pack(pady=5)

# Настройка отображения графика
plt.ion()  # Включение интерактивного режима для немедленного отображения

root.mainloop()
