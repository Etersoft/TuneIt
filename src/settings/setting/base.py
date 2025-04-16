import logging
import threading
import time
from ..searcher import SearcherFactory

from gi.repository import GLib

class BaseSetting:
    def __init__(self, setting_data, module):
        self._ = module.get_translation

        self.module = module

        self.name = self._(setting_data['name'])
        self.orig_name = setting_data['name']

        self.logger = logging.getLogger(f"{self.__class__.__name__}[{self.name}]")

        self.widget = None

        self.root = setting_data.get('root', False)

        self.params = {
            **setting_data.get('params', {}),
            'module_path': module.path
        }

        self.type = setting_data['type']

        self.help = setting_data.get('help', None)
        if self.help is not None:
            self.help = self._(self.help)

        self.default = setting_data.get('default')
        self.gtype = setting_data.get('gtype', [])

        self._current_value = None

        self.search_target = setting_data.get('search_target', None)

        self.map = setting_data.get('map')

        self.prepare_map()

        self.update_interval = setting_data.get('update_interval', None)

        if self.update_interval:
            self._start_update_thread()


    def prepare_map(self):
        if self.map is None:
            if self.search_target is not None:
                self.map = SearcherFactory.create(self.search_target).search()
            else:
                self.map = self._default_map()

        if isinstance(self.map, list) and 'choice' in self.type:
            self.map = {
                item.title(): item for item in self.map
                if item is not None
            }

            if not self.map:
                self.logger.warning(f"Warning: 'map' is empty for setting {self.name}. Check data source.")


        if isinstance(self.map, dict) and 'choice' in self.type:
            self.map = {
                self._(key) if isinstance(key, str) else key: value
                for key, value in self.map.items()
            }
            if not self.map:
                self.logger.warning(f"Warning: 'map' is empty for setting {self.name}. Check data source.")


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
                self.logger.debug(var)
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

    def _get_selected_row_index(self):
        current_value = self._get_backend_value()
        return list(self.map.values()).index(current_value) if current_value in self.map.values() else 0

    def _get_default_row_index(self):
        return list(self.map.values()).index(self.default) if self.default in self.map.values() else None

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
