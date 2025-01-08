class BaseWidget:
    def __init__(self, setting):
        self.setting = setting

    def create_row(self):
        raise NotImplementedError("Метод create_row должен быть реализован в подклассе")
