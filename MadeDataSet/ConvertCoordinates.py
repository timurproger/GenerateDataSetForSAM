from PIL import Image
from matplotlib import pyplot as plt
from shapely.geometry import LineString

from MadeDataSet.TagsOSMEnum import TagsOSMEnum


# Класс конвентирует коордмнаты из планетных в координаты изображения
class ConvertCoordinates():
    def __init__(self, image: str, coordinates_bounding_box: dict) -> None:
        # Обозначаем изображение
        self.img = Image.open(image)
        # Определяем ширену и высоту изображения
        self.w, self.h = self.img.size
        # Определяем координаты рамки в земных коорд
        self.coordinates_bounding_box = coordinates_bounding_box
        # Определяем миниму и максимум для x, y
        self.x_min, self.y_min = self.coordinates_bounding_box['lonLower'], self.coordinates_bounding_box['latLower']
        self.x_max, self.y_max = self.coordinates_bounding_box['lonHigher'], self.coordinates_bounding_box['latHigher']

        # Определяем ширену и длину в земных координатах
        self.w_cord_earth, self.h_cord_earth = self.x_max - self.x_min, self.y_max - self.y_min

        self.scale_w = self.w / self.w_cord_earth
        self.scale_h = self.h / self.h_cord_earth


    #Переводим координаты из земных в коорд изображения
    def MadeCordForImg(self, crd_x: float, crd_y: float) -> list[float]:
        # Определяем разности по формулам для перевода из земных коорд. в коорд. изображения
        delt_x = crd_x - self.x_min
        delt_y = self.y_max - crd_y
        x = delt_x * self.scale_w
        y = delt_y * self.scale_h
        return [x, y]



