from MadeDataSet.CreateDirectory import CreateDirectory
from MadeDataSet.GenerateImageLabel import GenerateImageLabel
from MadeDataSet.TagsOSMEnum import TagsOSMEnum
from MadeDataSet.СreateMask import CreateMask
from MadeDataSet.BasicParameters import BasicParameters as BsPrm

# Здесь мы обрезаем большую карту на маленькие кусочки
class DivisionOnImgFragment():
    def __init__(self, coordinates_ur: dict) -> None:
        self.coordinates_ur = coordinates_ur
        self.height = self.coordinates_ur['latHigher'] - self.coordinates_ur['latLower']
        self.width = self.coordinates_ur['lonHigher'] - self.coordinates_ur['lonLower']

        #CreateDirectory().CheckCreareDirOther()

    # Обрабатываем маленький фрагмент карты
    def Fragment(self,
                 path_img: str,
                 path_mask: str,
                 path_json: str,
                 coordinates_bounding_box: dict) -> None:

        id_img = 1
        # Список тегов
        list_tags = [TagsOSMEnum.HIGHWAY,
                     TagsOSMEnum.WATERWAY,
                     TagsOSMEnum.RAILWAY,
                     TagsOSMEnum.LANDUSE,
                     TagsOSMEnum.NATURAL]

        # Подключаемся к классу Который генерирует изображение и получает полигоны каждого объекта
        generate_image_label = GenerateImageLabel(coordinates_bounding_box, list_tags)
        # качаем фотку
        generate_image_label.DownloadImage(path_img)

        (polygon_dict,
         way_dictionary_names,
         bounding_box_polygon_obj,
         way_dictionary_tags) = generate_image_label.MadePolygonsFromWays()

        # создаем маски для объектов
        create_mask = CreateMask(coordinates_bounding_box, path_img, path_mask, path_json, id_img)
        create_mask.Create(polygon_dict, way_dictionary_names, way_dictionary_tags)


    # Запуск обрезки карты на маленькие кусочки
    def Start(self,
              name_folder_img: str,
              name_folder_masks: str,
              name_folder_json: str) -> None:
        count_w = int(self.width // 0.05)
        count_h = int(self.height // 0.02)
        count = 0
        print(count_w, count_h)

        for w in range(count_w - 1):
            w_lower = self.coordinates_ur['lonLower'] + w * 0.04
            w_upper = self.coordinates_ur['lonLower'] + (w + 1) * 0.04

            for h in range(count_h - 1):
                count += 1
                path_img = f'{name_folder_img}/{BsPrm.NAME_IMAGE_BASE}_{count}.png'
                path_json = f'{name_folder_json}/{BsPrm.NAME_IMAGE_BASE}_{count}.json'
                path_mask = f'{name_folder_masks}/{BsPrm.NAME_FOLDER_MASK}_{count}/'

                crtdir = CreateDirectory()
                crtdir.CheckCreareDirectory(path_mask)

                h_lower = self.coordinates_ur['latLower'] + h * 0.02
                h_upper = self.coordinates_ur['latLower'] + (h + 1) * 0.02

                coordinates_bounding_box = {'latLower': h_lower,
                                            'lonLower': w_lower,
                                            'latHigher': h_upper,
                                            'lonHigher': w_upper}

                self.Fragment(path_img, path_mask, path_json, coordinates_bounding_box)


