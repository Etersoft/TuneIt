from .BooleanWidget import BooleanWidget
from .ChoiceWidget import ChoiceWidget
from .EntryWidget import EntryWidget

class WidgetFactory:
    widget_map = {
        'choice': ChoiceWidget,
        'boolean': BooleanWidget,
        'entry': EntryWidget
    }

    @staticmethod
    def create_widget(setting):
        widget_class = WidgetFactory.widget_map.get(setting.type)
        if widget_class:
            return widget_class(setting)
        else:
            print(f"Неизвестный тип виджета: {setting.type}")
            return None
