from .BooleanWidget import BooleanWidget
from .ChoiceWidget import ChoiceWidget
from .RadioChoiceWidget import RadioChoiceWidget
from .EntryWidget import EntryWidget
from .NumStepper import NumStepper


class WidgetFactory:
    widget_map = {
        'choice': ChoiceWidget,
        'radiochoice': RadioChoiceWidget,
        'boolean': BooleanWidget,
        'entry': EntryWidget,
        'number': NumStepper,
    }

    @staticmethod
    def create_widget(setting):
        widget_class = WidgetFactory.widget_map.get(setting.type)
        if widget_class:
            return widget_class(setting)
        else:
            print(f"Неизвестный тип виджета: {setting.type}")
            return None
