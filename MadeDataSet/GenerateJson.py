import json

import cv2
import numpy as np
from PIL import Image
from pycocotools import mask


# Генерируем Json файл по 1 изображению со всеми масками

class GenerateJson():
    def __init__(self, path_json: str, id_img: id) -> None:
        self.path_json = path_json
        self.annotation = []
        self.id_img = id_img

    # Функция все собирает и передает на сохранение json
    def Generate(self, img_path: str, list_img: dict) -> None:
        img = Image.open(img_path)
        count = 0

        for id, image_array in list_img.items():
            count += 1
            # Находим границы объекта на изображении
            bbox = self.FindBBox(image_array)
            # Переводим маску в coco RLE формат
            segmentation = self.ImageInToCocoRLE(image_array)
            # Находим площадь сегмента
            area = self.MaskArea(image_array)
            if (bbox != None):
                self.annotation.append(self.Annotation(count, bbox, area, segmentation))

        print(self.annotation)
        self.SaveJson(img, img_path)

    # Функция находит ограничивающую рамку
    def FindBBox(self, image_array: np.array) -> list[int]:
        contours, _ = cv2.findContours(image_array, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        # Найдите bounding box для самого большого контура
        if contours:
            x, y, w, h = cv2.boundingRect(contours[0])
            print("Bounding box:", x, y, w, h)
            return [x, y, w, h]

        else:
            return None


    # Изображение переводится в coco RLE формат
    def ImageInToCocoRLE(self, image_array: np.array) -> dict:
        rle = mask.encode(np.asfortranarray(np.array(image_array)))
        print(rle['counts'], rle['counts'].decode('ascii'))
        rle['counts'] = rle['counts'].decode()
        print(rle)
        return rle

    # Функция находит на основе маски площадь
    def MaskArea(self, image_array: np.array) -> int:
        area = cv2.countNonZero(image_array)
        return area

    # Функция собирает анотацию в словарь
    def Annotation(self,
                   id_annotation: int,
                   bbox: list,
                   area: int,
                   segmentation: dict) -> dict:

        data_annotation = {
            "id": id_annotation,              # Annotation id
            "segmentation": segmentation,             # Mask saved in COCO RLE format.
            "bbox": bbox,     # The box around the mask, in XYWH format
            "area": area,              # The area in pixels of the mask
            "predicted_iou": None,            # The model's own prediction of the mask's quality
            "stability_score": None,            # A measure of the mask's quality
            "crop_box": None,     # The crop of the image used to generate the mask, in XYWH format
            "point_coords": [self.FindCenter(bbox)]        # The point coordinates input to the model to generate the mask
        }
        return data_annotation

    # Функция находит ценрт рамки
    def FindCenter(self, bbox: list) -> list[int]:
        x, y = bbox[0]+bbox[2]//2, bbox[1]+bbox[3]//2
        return [x, y]

    # Функция собирает информацию о основном изображении
    def ImageInfo(self, id_img: int, img: Image, img_path: str) -> dict:

        data_img_info = {
            "image_id": id_img,  # Image id
            "width": img.size[0],  # Image width
            "height": img.size[1],  # Image height
            "file_name": img_path,  # Image filename
        }
        return data_img_info

    # Функция сохраняет все в json файл
    def SaveJson(self, img: Image, img_path: str) -> None:

        data = {"image": self.ImageInfo(self.id_img, img, img_path),
                "annotations": self.annotation}

        with open(self.path_json, "w") as f:
            json.dump(data, f, indent=4)