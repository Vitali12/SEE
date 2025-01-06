#Подсчет количества линий:

#В функции main добавлен список line_counts, который содержит количество линий для каждого направления. В данном случае каждая линия считается один раз.
#Отображение количества линий на роза-диаграмме:

#В функции plot_rose_diagram добавлен код для отображения количества линий на диаграмме. Используется метод ax.annotate для добавления аннотаций к каждому сектору диаграммы.
#Этот код позволяет пользователю выбрать файл изображения, интерактивно выбрать область на изображении, подсчитать количество линий в этой области и отобразить их на роза-диаграмме.

import cv2
import numpy as np
import matplotlib.pyplot as plt
from tkinter import Tk, filedialog

# Функция для выбора файла через графический интерфейс
def select_file():
    root = Tk()
    root.withdraw()  # Скрыть основное окно Tkinter
    file_path = filedialog.askopenfilename(title="Выберите файл изображения", filetypes=[("Image files", "*.jpg;*.jpeg;*.png;*.bmp;*.tiff")])
    root.destroy()
    return file_path

# Функция для выбора области на изображении
def select_roi(image):
    roi = cv2.selectROI("Select ROI", image, fromCenter=False, showCrosshair=True)
    cv2.destroyWindow("Select ROI")
    return roi

# Функция для построения розы ветров
def plot_rose_diagram(angles, line_counts):
    plt.figure(figsize=(8, 8))
    ax = plt.subplot(111, projection='polar')
    ax.set_theta_zero_location('N')
    ax.set_theta_direction(-1)

    # Создание гистограммы направлений
    num_bins = 36
    counts, bin_edges = np.histogram(angles, bins=num_bins, range=(0, 2 * np.pi))
    bin_centers = 0.5 * (bin_edges[:-1] + bin_edges[1:])

    # Построение розы ветров
    bars = ax.bar(bin_centers, counts, width=2 * np.pi / num_bins, bottom=0.0)

    # Настройка осей
    ax.set_xticks(np.pi / 180. * np.linspace(0,  360, 8, endpoint=False))
    ax.set_xticklabels(['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW'])

    # Добавление количества линий на диаграмму
    for bar, count in zip(bars, line_counts):
        height = bar.get_height()
        ax.annotate('{}'.format(count),
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3),  # 3 points vertical offset
                    textcoords="offset points",
                    ha='center', va='bottom')

    plt.show()

# Основная функция
def main():
    # Выбор файла изображения
    file_path = select_file()
    if not file_path:
        print("Файл не выбран")
        return

    # Чтение изображения
    image = cv2.imread(file_path, cv2.IMREAD_GRAYSCALE)
    if image is None:
        print("Ошибка загрузки изображения")
        return

    # Выбор области на изображении
    roi = select_roi(image)
    x, y, w, h = roi
    roi_image = image[y:y+h, x:x+w]

    # Применение преобразования Кэнни для выделения границ
    edges = cv2.Canny(roi_image, 50, 150, apertureSize=3)

    # Применение преобразования Хафа для выделения линий
    lines = cv2.HoughLines(edges, 1, np.pi / 180, 50)

    # Извлечение данных о направлении линий и подсчет количества линий
    angles = []
    line_counts = []
    if lines is not None:
        for line in lines:
            rho, theta = line[0]
            angles.append(theta)
            line_counts.append(1)  # Каждая линия считается один раз

    # Построение розы ветров
    if angles:
        plot_rose_diagram(angles, line_counts)
    else:
        print("Линии не обнаружены")

if __name__ == "__main__":
    main()
