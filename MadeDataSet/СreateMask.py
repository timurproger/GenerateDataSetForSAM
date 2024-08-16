import cv2
import numpy as np
from PIL import Image, ImageDraw
from matplotlib import pyplot as plt
from matplotlib.axis import Axis
from shapely import LineString, Polygon

from MadeDataSet.BasicParameters import BasicParameters
from MadeDataSet.ConvertCoordinates import ConvertCoordinates
from MadeDataSet.GenerateJson import GenerateJson


# Класс создания масок для изображения
class CreateMask():
    def __init__(self,
                 coordinates_bounding_box: dict,
                 path_img: str,
                 path_masks: str,
                 path_json: str,
                 id_img: int) -> None:

        # объявление переменных
        self.id_img = id_img
        self.coordinates_bounding_box = coordinates_bounding_box
        self.path_img = path_img
        self.path_masks = path_masks
        self.path_json = path_json

        self.name_mask = BasicParameters.NAME_MASKS_BASE

    # Строим польгон
    def PlotPolygon(self, polygon: Polygon, ax: Axis, color: str) -> None:
        x, y = polygon.exterior.xy
        ax.fill(x, y, fc=color, alpha=1)

    # Строим линию
    def PlotLine(self, line: LineString, ax: Axis, color: str) -> None:
        x, y = line.buffer(4).exterior.xy
        ax.fill(x, y, fc=color, alpha=1)

    # Сохраняем маску
    def SaveMask(self, name: str) -> np.array:
        name_img_to_save = f'{self.path_masks}{self.name_mask}_{name}.png'

        # Сохраняем только изображение внутри области графика
        plt.savefig(name_img_to_save, bbox_inches='tight', pad_inches=0, dpi=150)
        mask_rgb = np.array(Image.open(name_img_to_save))
        mask_binary = (np.sum(mask_rgb, axis=2) > 128 * 3).astype(np.uint8) * 255

        return mask_binary

    # Сохраняем оригенальную фотографию в измененном формате
    def SaveOriginalImg(self) -> None:
        fig, ax = plt.subplots()
        ax.axis('off')
        # Добавляем изображения
        ax.imshow(Image.open(self.path_img))
        plt.savefig(self.path_img, bbox_inches='tight', pad_inches=0, dpi=150)


    #  Строим маску для каждого типа на изображении
    def PlotingOnMap(self,
                     new_cords_polygon: dict,
                     way_dictionary_tags: dict,
                     way_dictionary_names: dict) -> dict:

        img = Image.open(self.path_img)
        w, h = img.size
        # Получаем все уникальные имена обектов
        list_names = self.ListNames(way_dictionary_names)
        print(list_names)
        #list_names.remove('wood')

        white_canvas = Image.new("RGB", (w+10, h+10), 'black')

        img_list = {}

        # Перебираем полигоны и строим их
        for id, polygon in new_cords_polygon.items():
                # Строим фигуру для отрисовки маски каждого объекта
                fig, ax = plt.subplots()
                # Добавляем изображения
                ax.imshow(white_canvas)

                tag = way_dictionary_tags[id]
                name = way_dictionary_names[id]

                # Определяем название объекта и естьли в нем специальный атрибут inner
                print('name', name)
                if('way' in tag.lower()):
                    self.PlotLine(LineString(polygon[:-1]), ax, 'white')
                else:
                    self.PlotPolygon(Polygon(polygon), ax, 'white')

                # Обрезаем маску
                ax.set_xlim(0, w)
                ax.set_ylim(h, 0)
                ax.axis('off')
                # Сохраняем маску
                image_array = self.SaveMask(f'{name}_{id}')
                img_list[id] = image_array

                plt.close('all')

        return img_list

    # Получаем уникальный список тегов
    def ListNames(self, way_dictionary_names: dict) -> list[str]:
        list_names = [i.split('*')[0] for i in set(way_dictionary_names.values())]
        return list_names

    # Проверяем объект входит или нет в рамки изображения
    def CheckMask(self, polygon: Polygon) -> bool:
        img = Image.open(self.path_img)
        w, h = img.size
        x_mas, y_mas = polygon.exterior.xy
        for x, y in zip(x_mas, y_mas):
            if(x > 0 and y > 0 and x < w and y < h):
                return True
        else:
            return False


    # Основная функциа которая све собирает и отправляет в генератор json файла
    def Create(self,
               polygon_dict: dict,
               way_dictionary_names: dict,
               way_dictionary_tags: dict) -> None:

        # Подключаемся к классу для перевода координат
        conv = ConvertCoordinates(self.path_img, self.coordinates_bounding_box)
        new_cords_polygon = {}

        # Переводим координаты земли в координаты изображения
        for id, polygon in polygon_dict.items():
            cord = polygon.exterior.coords
            name = way_dictionary_names[id]

            print(name, id)
            new_polygon = [tuple(conv.MadeCordForImg(i[0], i[1])) for i in list(cord)]
            if(self.CheckMask(Polygon(new_polygon))):
                new_cords_polygon[id] = new_polygon


        list_img = self.PlotingOnMap(new_cords_polygon, way_dictionary_tags, way_dictionary_names)
        # Создаем Json файл
        self.SaveOriginalImg()
        generateJson = GenerateJson(self.path_json, self.id_img)
        generateJson.Generate(self.path_img, list_img)
