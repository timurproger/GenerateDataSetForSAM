import overpy
from PIL import Image

from overpy.exception import OverpassTooManyRequests, OverpassGatewayTimeout
import time

from shapely import simplify
from tqdm import tqdm
import folium
from shapely.geometry import Polygon
import numpy as np

import geopandas as gpd

from shapely.geometry import box
import contextily as ctx
import matplotlib.pyplot as plt

from MadeDataSet.ConvertCoordinates import ConvertCoordinates
from MadeDataSet.RequestsOSM import RequestsOSM

#

class GenerateImageLabel():
    def __init__(self, coordinates_bounding_box, list_tags):
        # Подключаемся к OSM
        self.api = overpy.Overpass()


        self.coordinates_bounding_box = coordinates_bounding_box

        # Переводим координаты в строку для запроса
        self.overpy_bounding_box = f"""({self.coordinates_bounding_box['latLower']},
                                        {self.coordinates_bounding_box['lonLower']},
                                        {self.coordinates_bounding_box['latHigher']},
                                        {self.coordinates_bounding_box['lonHigher']})"""

        # Список тегов по которым будем искать объекты
        self.list_tags = list_tags

    # Фуункция обрабатывает объекты с фнутренними обектами
    def DubleMember(self,
                    result,
                    name_tag: str,
                    way_dictionary_names: dict,
                    way_dictionary_node_list: dict,
                    way_dictionary_tags: dict,
                    requests_texts: RequestsOSM) -> [dict, dict, dict]:

        for relation in result.relations:

            print(relation.tags, relation.id)
            try:
                name = relation.tags[name_tag]
            except:
                name = 'Неизвестно'
            print(name)
            # В каждом обекте перебераем подобъекты (это нужно если есть внутриний объект)
            for member in relation.members:
                # текст запроса для подобъекта
                print('meber:', member, member.role)
                text_way = requests_texts.ReqTextWays(member.ref)
                # запрос
                result_way = self.api.query(text_way)
                print(result_way.get_ways())

                # формирование полигонов
                for way in result_way.get_ways():
                    if (member.role == 'inner'):
                        print(member.role)
                        # Если у нас внутренний полигон то мы к имени добавляем _inner
                        way_dictionary_names[way.id] = f'Неизвестно'
                    else:
                        way_dictionary_names[way.id] = name
                    way_dictionary_tags[way.id] = name_tag
                    way_dictionary_node_list = self.PolygonsInDict(way,
                                                                   way_dictionary_node_list)

        return way_dictionary_names, way_dictionary_node_list, way_dictionary_tags

    #Фуункция обрабатывает объекты в нутри которых нет других объектов
    def Member(self,
               result,
               name_tag: str,
               way_dictionary_names: dict,
               way_dictionary_node_list: dict,
               way_dictionary_tags: dict) -> [dict, dict, dict]:

        # получаем каждый объект в рамках одного тега
        for way in result.get_ways():
            way_dictionary_tags[way.id] = name_tag
            way_dictionary_names[way.id] = way.tags.get(name_tag, 'Неизвестно')
            # формирование полигонов
            way_dictionary_node_list = self.PolygonsInDict(way,
                                                           way_dictionary_node_list)

        return way_dictionary_names, way_dictionary_node_list, way_dictionary_tags



    # Нахождение полигонов в путях (обекты в OSM)
    def MadePolygonsFromWays(self)  -> [dict, dict, np.array]:

        # Получаем класс который создает текстовые запросы
        requests_texts = RequestsOSM()
        # Создание списка результатов запроса
        list_results_requests = []

        # Запросы по разным тегам и формируем список результатов запроса
        for tag in self.list_tags:

            text = requests_texts.QueryTextReq(tag, self.overpy_bounding_box)
            result = self.api.query(text)
            list_results_requests.append(result)

        # Создаем словари для списков узлов по каждому объекту и для названий каждого узла
        way_dictionary_node_list = {}
        way_dictionary_names = {}
        way_dictionary_tags = {}

        # получаем результаты запросов для каждого типа тегов
        for result, name_tag in zip(tqdm(list_results_requests), self.list_tags):

            # получаем обекты
            (way_dictionary_names,
             way_dictionary_node_list,
             way_dictionary_tags) = self.DubleMember(result,
                                                     name_tag,
                                                     way_dictionary_names,
                                                     way_dictionary_node_list,
                                                     way_dictionary_tags,
                                                     requests_texts)
            (way_dictionary_names,
             way_dictionary_node_list,
             way_dictionary_tag) = self.Member(result,
                                               name_tag,
                                               way_dictionary_names,
                                               way_dictionary_node_list,
                                               way_dictionary_tags)




        # Словарь для каждого отдельного польгона
        polygon_dict = {}
        for id, way in way_dictionary_node_list.items():
            polygon_dict[id] = Polygon(np.array(way))

        # Переводим всю нашу область в полигон
        bounding_box_polygon_obj = Polygon(np.array([
            [self.coordinates_bounding_box['lonLower'], self.coordinates_bounding_box['latLower']],
            [self.coordinates_bounding_box['lonLower'], self.coordinates_bounding_box['latHigher']],
            [self.coordinates_bounding_box['lonHigher'], self.coordinates_bounding_box['latHigher']],
            [self.coordinates_bounding_box['lonHigher'], self.coordinates_bounding_box['latLower']]
        ]))

        return polygon_dict, way_dictionary_names, bounding_box_polygon_obj, way_dictionary_tags

        # Нахождение полигонов и сохранении их в словарь
    def PolygonsInDict(self,
                       way,
                       way_dictionary_node_list: dict) -> dict:

        while True:
            try:
                # Получаем список узлов
                nodes = way.get_nodes(resolve_missing=True)
                # Создаем список для узлов по каждому объекту
                list_coordinates_each_node = []
                # идем по узлам
                for node in nodes:
                    # из узлов получаем долготу и широту
                    list_coordinates_each_node.append([float(node.lon), float(node.lat)])

                # В списке узлов должно быть минимум 3 узла
                if len(list_coordinates_each_node) >= 3:
                    # Добавить путь и его узлы в словарь
                    way_dictionary_node_list[way.id] = list_coordinates_each_node
                    # получаем полигон
                    polygon = Polygon(list_coordinates_each_node)
                    # Апроксимируем наш полигон
                    #polygon = simplify(polygon, 0.0001)  # Параметр tolerance определяет точность упрощения
                    # и вписываем в словарь координат
                    way_dictionary_node_list[way.id] = list(polygon.exterior.coords)


            # Обработка разных исключений
            except OverpassTooManyRequests:
                time.sleep(1)
                print('Retrying...')
                continue
            except OverpassGatewayTimeout:
                time.sleep(10)
                print('OverpassGatewayTimeout, retrying...')
                continue
            except Exception as e:
                print(e)
            break

        return way_dictionary_node_list

    # Функция отображает карту со всеми выделенными полигонами
    def ShowMapInWeb(self,
                     polygon_dict: dict,
                     way_dictionary_names: dict,
                     bounding_box_polygon_obj: np.array) -> None:

        #Создаем оснавную карту
        map = folium.Map(location=[(self.coordinates_bounding_box['latLower'] + self.coordinates_bounding_box['latHigher']) / 2,
                                (self.coordinates_bounding_box['lonLower'] + self.coordinates_bounding_box['lonHigher']) / 2],
                         zoom_start=15, tiles='CartoDB positron')

        for id, polygon in polygon_dict.items():
            # Пререводим полигоны в формат GeoJson
            geo_polygons_json = folium.GeoJson(data=gpd.GeoSeries(polygon).to_json(),
                                               style_function=lambda x: {'fillColor': 'red'})
            # Создаем текст для маркера
            popup_text = f"Полигон {way_dictionary_names[id]} - {id}"
            popup = folium.Popup(popup_text)

            # Добавление маркера в центр полигона
            lat_center = np.mean([coord[1] for coord in polygon.exterior.coords])
            lon_center = np.mean([coord[0] for coord in polygon.exterior.coords])

            # Создание маркера с подписями
            marker = folium.Marker([lat_center, lon_center], popup=popup)
            # Добавление маркера на карту
            marker.add_to(map)
            # Добавление полигона на карту
            geo_polygons_json.add_to(map)


        # Добавляем нашу выбраную кординатами облость
        geo_json_box = folium.GeoJson(data=gpd.GeoSeries(bounding_box_polygon_obj).to_json(),
                                      style_function=lambda x: {'fillColor': 'blue'})
        # Добавляем на карту
        geo_json_box.add_to(map)

        # Отображаем карту в браузере
        map.show_in_browser()


    # Сохраняем изображение карты
    def DownloadImage(self, name_img) -> None:
        # нижний левый угол
        xmin, ymin = self.coordinates_bounding_box['lonLower'], self.coordinates_bounding_box['latLower']

        # верхний правый угол
        xmax, ymax = self.coordinates_bounding_box['lonHigher'], self.coordinates_bounding_box['latHigher']

        # Создаем прямоугольник из координат
        bounds_box = box(xmin, ymin, xmax, ymax)

        # Создаем GeoDataFrame
        gdf_map = gpd.GeoDataFrame(index=[0], crs="EPSG:4326", geometry=[bounds_box])

        # Преобразуем координаты в проекцию Меркатора (EPSG:3857)
        gdf = gdf_map.to_crs(epsg=3857)

        # Получаем границы для отображения
        xmin, ymin, xmax, ymax = gdf.total_bounds

        # отображаем карту
        fig, ax = plt.subplots(figsize=(10, 10))
        ax.set_xlim(xmin, xmax)
        ax.set_ylim(ymin, ymax)

        # Убираем оси
        ax.axis('off')

        # Добавляем базовую карту
        ctx.add_basemap(ax, source=ctx.providers.OpenStreetMap.Mapnik, crs=gdf.crs.to_string())

        # Сохраняем карту в файл
        plt.savefig(f'{name_img}', bbox_inches='tight', pad_inches=0, dpi=400)

        # Отображаем карту
        #plt.show()
        plt.clf()


