import os


# Класс по созданию папок и проверкой существуют ли они
class CreateDirectory():
    def __init__(self) -> None:
        pass

    def CheckCreareDirectory(self, path_name: str) -> None:
        if not os.path.isdir(path_name):
            os.mkdir(path_name)


