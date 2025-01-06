#Пояснение к коду:
#Выбор файла:

#Используется библиотека Tkinter для создания графического интерфейса, который позволяет пользователю выбрать файл изображения.
#Выбор области (ROI):

#Используется функция cv2.selectROI из OpenCV для интерактивного выбора области на изображении.
#Обработка изображения:

#Применяется преобразование Кэнни для выделения границ в выбранной области.
#Применяется преобразование Хафа для выделения линий.
#Построение розы ветров:

#Извлекаются данные о направлении линий и строится роза ветров с использованием Matplotlib.
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
def plot_rose_diagram(angles):
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

    # Извлечение данных о направлении линий
    angles = []
    if lines is not None:
        for line in lines:
            rho, theta = line[0]
            angles.append(theta)

    # Построение розы ветров
    if angles:
        plot_rose_diagram(angles)
    else:
        print("Линии не обнаружены")

if __name__ == "__main__":
    main()
