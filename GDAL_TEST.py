import cv2
import numpy as np
from osgeo import gdal

# Чтение DEM файла с помощью GDAL
dataset = gdal.Open('path_to_your_dem_file.tif')
if dataset is None:
    print("Ошибка загрузки DEM файла")
else:
    # Получение данных о высоте
    band = dataset.GetRasterBand(1)
    dem_data = band.ReadAsArray()

    # Преобразование данных в формат, подходящий для OpenCV
    dem_image = np.array(dem_data, dtype=np.float32)

    # Нормализация данных для отображения (если необходимо)
    dem_image = cv2.normalize(dem_image, None, 0, 255, cv2.NORM_MINMAX)
    dem_image = np.uint8(dem_image)

    # Создание структурного элемента (kernel)
    kernel = np.ones((5, 5), np.uint8)

    # Применение морфологической операции (например, эрозии)
    eroded_dem = cv2.erode(dem_image, kernel, iterations=1)

    # Отображение результата
    cv2.imshow('Eroded DEM', eroded_dem)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

if __name__ == "__main__":
    import os
    os.system('python /d:/Projects/SEE/GDAL_TEST.py')