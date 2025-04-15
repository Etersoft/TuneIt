import logging


class Backend:
    def __init__(self, params=None):
        # Параметры, передаваемые при инициализации
        self.params = params or {}
        self.logger = logging.getLogger(f"{self.__class__.__name__}")

    def get_value(self, key, gtype):
        raise NotImplementedError("Метод get_value должен быть реализован")

    def get_range(self, key, gtype):
        raise NotImplementedError("Метод get_range должен быть реализован")

    def set_value(self, key, value, gtype):
        raise NotImplementedError("Метод set_value должен быть реализован")
