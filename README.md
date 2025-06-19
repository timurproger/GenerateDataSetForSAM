# 🗺️ GenerateDataSetForSAM

Этот проект предназначен для генерации датасета с использованием карт OpenStreetMap и автоматическим созданием масок и JSON-аннотаций. Датасет может быть использован для обучения сегментационных моделей, таких как [Segment Anything Model (SAM)](https://github.com/facebookresearch/segment-anything).

---

## 📦 Возможности

* Загрузка карт с OpenStreetMap
* Автоматическое разбиение карт на изображения
* Генерация масок к изображениям
* Сохранение аннотаций в формате JSON

---

## 🚀 Установка

1. **Клонируйте репозиторий:**

   ```bash
   git clone https://github.com/timurproger/GenerateDataSetForSAM.git
   cd GenerateDataSetForSAM
   ```

2. **Создайте и активируйте виртуальное окружение (рекомендуется):**

   * **Windows:**

     ```bash
     python -m venv venv
     venv\Scripts\activate
     ```
   * **MacOS/Linux:**

     ```bash
     python3 -m venv venv
     source venv/bin/activate
     ```

3. **Установите зависимости:**

   ```bash
   pip install -r requirements.txt
   ```

---

## ▶️ Запуск

Для генерации датасета выполните команду:

```bash
python StartGnerateDataSet.py
```

После запуска будет создана папка `dataset/`, в которой содержатся следующие директории:

| Папка    | Содержимое                                                              |
| -------- | ----------------------------------------------------------------------- |
| `image/` | Обработанные и обрезанные изображения с карт OpenStreetMap              |
| `masks/` | Маски, соответствующие каждому изображению                              |
| `jsons/` | JSON-аннотации, содержащие информацию о геометрии и метаданных объектов |

---

## 🧱 Структура проекта

```
GenerateDataSetForSAM/
├── dataset/
│   ├── image/
│   ├── masks/
│   └── jsons/
├── StartGnerateDataSet.py
├── requirements.txt
└── ...
```

---

## 📝 Примечание

Убедитесь, что у вас установлен Python 3.8+ и есть подключение к интернету, так как при генерации используется OpenStreetMap.
