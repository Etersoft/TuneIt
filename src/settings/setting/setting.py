import threading
import time
from ..searcher import SearcherFactory
from .widgets import WidgetFactory
from ..backends import backend_factory
from ..daemon_client import dclient
from ..tools.gvariant import convert_by_gvariant
from ..widgets.service_dialog import ServiceNotStartedDialog

from gi.repository import GLib
service_stopped = False


class Setting:
    def __init__(self, setting_data, module):
        self._ = module.get_translation

        self.widget = None

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

        self._current_value = None

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
        
        self.update_interval = setting_data.get('update_interval', None)
        if self.update_interval:
            self._start_update_thread()

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
                self.widget = WidgetFactory.create_widget(self)
                return self.widget.create_row() if self.widget else None

            else:
                global service_stopped
                
                if service_stopped is False:
                    from ...main import get_main_window
                    
                    while True:
                        w = get_main_window()
                        if w.get_visible() and w.get_mapped():
                            dialog = ServiceNotStartedDialog()
                            response = dialog.user_question(get_main_window())
                            break

                        time.sleep(0.1)

                    if response == "yes":
                        dialog.service_enable_with_restart()

                    elif response in ("no", "close"):
                        dialog.close()
                        service_stopped = True
                        return None

        self.widget = WidgetFactory.create_widget(self)
        return self.widget.create_row() if self.widget else None

    def _get_selected_row_index(self):
        current_value = self._get_backend_value()
        return list(self.map.values()).index(current_value) if current_value in self.map.values() else 0

    def _get_default_row_index(self):
        return list(self.map.values()).index(self.default) if self.default in self.map.values() else None

    def _get_backend_value(self, force=False):
        if self._current_value is None or force is True:
            backend = self._get_backend()
            value = self.default
            
            if backend:
                value = backend.get_value(self.key, self.gtype) or self.default
                
            self._current_value = value
        return self._current_value

    def _get_backend_range(self):
        backend = self._get_backend()
        if backend:
            return backend.get_range(self.key, self.gtype)

    def _set_backend_value(self, value):
        backend = self._get_backend()
        if backend:
            backend.set_value(self.key, convert_by_gvariant(value, self.gtype), self.gtype)
            self._current_value = value

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

    def _start_update_thread(self):
        def update_loop():
            while True:
                time.sleep(self.update_interval)
                prev_value = self._current_value
                current_value = self._get_backend_value(force=True)
                if current_value != prev_value:
                    GLib.idle_add(self._update_widget)

        thread = threading.Thread(target=update_loop, daemon=True)
        thread.start()

    def _update_widget(self):
        
        if self.widget:
            self.widget.update_display()
        return False
