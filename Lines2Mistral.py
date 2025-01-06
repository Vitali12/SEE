from osgeo import gdal
import cv2
import numpy as np
import matplotlib.pyplot as plt

# Загрузка изображения
image = cv2.imread('e:/Morphometry_Python/Lines.png', cv2.IMREAD_GRAYSCALE)

# Применение преобразования Кэнни для выделения границ
edges = cv2.Canny(image, 50, 150, apertureSize=3)

# Применение преобразования Хафа для выделения линий
lines = cv2.HoughLines(edges, 1, np.pi / 180, 200)

# Извлечение данных о направлении и длине линий
angles = []
for line in lines:
    rho, theta = line[0]
    angles.append(theta)

# Построение розы ветров
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
# Сохранение графика в файл
plt.savefig('e:/Morphometry_Python/wind_rose.png')
plt.show()