from ..searcher import SearcherFactory
from .widgets import WidgetFactory
from ..backends import backend_factory
from ..daemon_client import dclient
from ..tools.gvariant import convert_by_gvariant
from ..widgets.service_dialog import ServiceNotStartedDialog

dialog_presented = False


class Setting:
    def __init__(self, setting_data, module):
        self._ = module.get_translation

        self.name = self._(setting_data['name'])

        self.root = setting_data.get('root', False)

        self.backend = setting_data.get('backend')

        self.params = {
            **setting_data.get('params', {}),
            'module_path': module.path
        }

        self.type = setting_data['type']

        self.help = setting_data.get('help', None)
        if self.help is not None:
            self.help = self._(self.help)

        self.key = setting_data.get('key')
        self.default = setting_data.get('default')
        self.gtype = setting_data.get('gtype', [])

        self.search_target = setting_data.get('search_target', None)

        self.map = setting_data.get('map')
        if self.map is None:
            if self.search_target is not None:
                self.map = SearcherFactory.create(self.search_target).search()
            else:
                self.map = self._default_map()

        if isinstance(self.map, list) and 'choice' in self.type:
            self.map = {
                item.title(): item for item in self.map
            }


        if isinstance(self.map, dict) and 'choice' in self.type:
            self.map = {
                self._(key) if isinstance(key, str) else key: value
                for key, value in self.map.items()
            }

        if len(self.gtype) > 2:
            self.gtype = self.gtype[0]
        else:
            self.gtype = self.gtype

    def _default_map(self):
        if self.type == 'boolean':
            # Дефолтная карта для булевых настроек
            return {True: True, False: False}
        if 'choice' in self.type:
            # Дефолтная карта для выборов
            map = {}
            range = self._get_backend_range()

            if range is None:
                return {}

            for var in range:
                print(var)
                map[var[0].upper() + var[1:]] = var
            return map
        if self.type == 'number':
            map = {}
            range = self._get_backend_range()

            if range is None:
                return {}

            map["upper"] = range[1]
            map["lower"] = range[0]

            # Кол-во после запятой
            map["digits"] = len(str(range[0]).split('.')[-1]) if '.' in str(range[0]) else 0
            # Минимальное число с этим количеством
            map["step"] = 10 ** -map["digits"] if map["digits"] > 0 else 0
            return map
        return {}

    def create_row(self):
        if self.root is True:
            print("Root is true")
            if dclient is not None:
                widget = WidgetFactory.create_widget(self)
                return widget.create_row() if widget else None
            else:
                global dialog_presented
                if dialog_presented is False:
                    from ..main import get_main_window

                    dialog = ServiceNotStartedDialog()
                    dialog.present(get_main_window())

                    dialog_presented = True
                return None

        widget = WidgetFactory.create_widget(self)
        return widget.create_row() if widget else None

    def _get_selected_row_index(self):
        current_value = self._get_backend_value()
        return list(self.map.values()).index(current_value) if current_value in self.map.values() else 0

    def _get_default_row_index(self):
        return list(self.map.values()).index(self.default) if self.default in self.map.values() else None

    def _get_backend_value(self):
        value = None

        backend = self._get_backend()

        if backend:
            value = backend.get_value(self.key, self.gtype)
        if value is None:
            value = self.default
        return value

    def _get_backend_range(self):
        backend = self._get_backend()
        if backend:
            return backend.get_range(self.key, self.gtype)

    def _set_backend_value(self, value):
        backend = self._get_backend()
        if backend:
            backend.set_value(self.key, convert_by_gvariant(value, self.gtype), self.gtype)

    def _get_backend(self):
        if self.root is True:
            backend = dclient
            backend.set_backend_name(self.backend)
            backend.set_backend_params(self.params)
        else:
            backend = backend_factory.get_backend(self.backend, self.params)

        if not backend:
            print(f"Бекенд {self.backend} не зарегистрирован.")
        return backend
