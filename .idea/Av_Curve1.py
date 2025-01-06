import tkinter as tk
from tkinter import filedialog
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler
from scipy.optimize import curve_fit
import numpy as np

class FileLoaderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("File Loader")

        self.file_entries = []
        for i in range(5):
            label = tk.Label(root, text=f"File {i+1}:")
            label.grid(row=i, column=0, padx=5, pady=5)
            entry = tk.Entry(root, width=50)
            entry.grid(row=i, column=1, padx=5, pady=5)
            self.file_entries.append(entry)
            button = tk.Button(root, text="Browse", command=lambda i=i: self.load_file(i))
            button.grid(row=i, column=2, padx=5, pady=5)
            plot_button = tk.Button(root, text="Показать график", command=lambda i=i: self.show_plot(i))
            plot_button.grid(row=i, column=3, padx=5, pady=5)

        self.model_label = tk.Label(root, text="Model Formula:")
        self.model_label.grid(row=5, column=0, padx=5, pady=5)
        self.model_entry = tk.Entry(root, width=50)
        self.model_entry.insert(0, "sigma_peak * (epsilon / epsilon_peak) * np.exp(1/n) * (1 - (epsilon**n / epsilon_peak**n)**B)")
        self.model_entry.grid(row=5, column=1, padx=5, pady=5)

        self.param_label = tk.Label(root, text="Initial Parameters (sigma_peak, epsilon_peak, n, B):")
        self.param_label.grid(row=6, column=0, padx=5, pady=5)
        self.param_entry = tk.Entry(root, width=50)
        self.param_entry.insert(0, "1, 1, 1, 1")
        self.param_entry.grid(row=6, column=1, padx=5, pady=5)

        fit_button = tk.Button(root, text="Fit Model", command=self.fit_model)
        fit_button.grid(row=5, column=2, padx=5, pady=5)

        normalize_button = tk.Button(root, text="Normalize Data", command=self.normalize_data)
        normalize_button.grid(row=7, column=1, padx=5, pady=5)

    def load_file(self, index):
        file_path = filedialog.askopenfilename(title="Выберите файл", filetypes=[("CSV файлы", "*.csv")])
        if file_path:
            self.file_entries[index].delete(0, tk.END)
            self.file_entries[index].insert(0, file_path)

    def show_plot(self, index):
        file_path = self.file_entries[index].get()
        if file_path:
            try:
                data = pd.read_csv(file_path)
                if 'load' in data.columns and 'strain' in data.columns:
                    data = data[['load', 'strain']].dropna()  # Удаление пропусков
                    scaler = MinMaxScaler()
                    data[['load', 'strain']] = scaler.fit_transform(data[['load', 'strain']])  # Нормализация
                    plt.plot(data['strain'], data['load'], label=f'File {index+1}')
                    plt.xlabel('Strain')
                    plt.ylabel('Load')
                    plt.title('Load vs Strain')
                    plt.legend()
                    plt.show()
                else:
                    print(f"Файл {file_path} не содержит необходимые колонки 'load' и 'strain'.")
            except Exception as e:
                print(f"Ошибка при обработке файла {file_path}: {e}")

    def normalize_data(self):
        all_data = []
        for entry in self.file_entries:
            file_path = entry.get()
            if file_path:
                try:
                    data = pd.read_csv(file_path)
                    if 'load' in data.columns and 'strain' in data.columns:
                        data = data[['load', 'strain']].dropna()  # Удаление пропусков
                        all_data.append(data)
                    else:
                        print(f"Файл {file_path} не содержит необходимые колонки 'load' и 'strain'.")
                except Exception as e:
                    print(f"Ошибка при обработке файла {file_path}: {e}")

        if all_data:
            plt.figure(figsize=(10, 6))
            for i, data in enumerate(all_data):
                scaler = MinMaxScaler()
                data[['load', 'strain']] = scaler.fit_transform(data[['load', 'strain']])  # Нормализация
                plt.plot(data['strain'], data['load'], label=f'File {i+1}')
            plt.xlabel('Strain')
            plt.ylabel('Load')
            plt.title('Normalized Load vs Strain')
            plt.legend()
            plt.show()

    def fit_model(self):
        model_formula = self.model_entry.get()
        initial_params = [float(p) for p in self.param_entry.get().split(',')]
        if not model_formula:
            print("Введите формулу модели.")
            return

        def model_func(epsilon, sigma_peak, epsilon_peak, n, B):
            return sigma_peak * (epsilon / epsilon_peak) * np.exp(1/n) * (1 - (epsilon**n / epsilon_peak**n)**B)

        all_data = []
        for entry in self.file_entries:
            file_path = entry.get()
            if file_path:
                try:
                    data = pd.read_csv(file_path)
                    if 'load' in data.columns and 'strain' in data.columns:
                        data = data[['load', 'strain']].dropna()  # Удаление пропусков
                        all_data.append(data)
                    else:
                        print(f"Файл {file_path} не содержит необходимые колонки 'load' и 'strain'.")
                except Exception as e:
                    print(f"Ошибка при обработке файла {file_path}: {e}")

        if all_data:
            plt.figure(figsize=(10, 6))
            for i, data in enumerate(all_data):
                x_data = data['strain']
                y_data = data['load']
                try:
                    popt, _ = curve_fit(model_func, x_data, y_data, p0=initial_params)
                    plt.plot(x_data, model_func(x_data, *popt), label=f'Fit {i+1}')
                except Exception as e:
                    print(f"Ошибка при подгонке модели для файла {i+1}: {e}")
            plt.xlabel('Strain')
            plt.ylabel('Load')
            plt.title('Model Fit')
            plt.legend()
            plt.show()

if __name__ == "__main__":
    root = tk.Tk()
    app = FileLoaderApp(root)
    root.mainloop()