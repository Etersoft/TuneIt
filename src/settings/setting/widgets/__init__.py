from .BooleanWidget import BooleanWidget
from .ChoiceWidget import ChoiceWidget
from .RadioChoiceWidget import RadioChoiceWidget
from .EntryWidget import EntryWidget
from .NumStepper import NumStepper
from .FileChooser import FileChooser
from .ButtonWidget import ButtonWidget
from .InfoLabelWidget import InfoLabelWidget
from .InfoDictWidget import InfoDictWidget

class WidgetFactory:
    widget_map = {
        'file': FileChooser,
        'choice': ChoiceWidget,
        'choice_radio': RadioChoiceWidget,
        'boolean': BooleanWidget,
        'entry': EntryWidget,
        'number': NumStepper,
        'button': ButtonWidget,
        'info_label': InfoLabelWidget,
        'info_dict': InfoDictWidget,
    }

    @staticmethod
    def create_widget(setting):
        widget_class = WidgetFactory.widget_map.get(setting.type)
        if widget_class:
            return widget_class(setting)
        else:
            print(f"Неизвестный тип виджета: {setting.type}")
            return None
