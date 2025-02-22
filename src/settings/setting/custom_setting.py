from ..searcher import SearcherFactory
from .widgets import WidgetFactory


import logging
import subprocess


class CustomSetting:
    def __init__(self, setting_data, module, section):
        self._ = module.get_translation
        self.module = module
        self.section = section
        self.logger = logging.getLogger(f"CommandSetting[{setting_data['name']}]")

        self.name = self._(setting_data['name'])
        self.orig_name = setting_data['name']

        self.type = setting_data['type']
        self.default = setting_data.get('default', '')
        self.help = self._(setting_data.get('help', ''))
        self._current_value = None

        self.get_command = setting_data.get('get_command')
        self.set_command = setting_data.get('set_command')

        self.gtype = setting_data.get('gtype', 's')

        if len(self.gtype) > 2:
            self.gtype = self.gtype[0]
        else:
            self.gtype = self.gtype

        self.search_target = setting_data.get('search_target')

        self.params = {
            **setting_data.get('params', {}),
            'module_path': module.path
        }

        self.widget = None
        self.row = None

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
        try:
            self.widget = WidgetFactory.create_widget(self)
            if self.widget:
                self.row = self.widget.create_row()
                return self.row
        except Exception as e:
            self.logger.error(f"Error creating row: {str(e)}")
        return None

    def get_value(self):
        if self._current_value is None:
            self._current_value = self._execute_get_command()
        return self._current_value

    def set_value(self, value):
        success = self._execute_set_command(value)
        if success:
            self._current_value = value
            self._update_widget()

    def _get_selected_row_index(self):
        current_value = self._get_backend_value()
        return list(self.map.values()).index(current_value) if current_value in self.map.values() else 0

    def _get_default_row_index(self):
        return list(self.map.values()).index(self.default) if self.default in self.map.values() else None

    def _execute_get_command(self):
        if not self.get_command:
            return self.default

        try:
            cmd = self._format_command(self.get_command)
            result = subprocess.run(
                cmd,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                shell=True
            )
            return self._process_output(result.stdout)
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Get command failed: {e.stderr}")
            return self.default

    def _execute_set_command(self, value):
        if not self.set_command:
            return False

        try:
            cmd = self._format_command(self.set_command, value)
            result = subprocess.run(
                cmd,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                shell=True
            )

            self._process_output(result.stdout)
            return True
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Set command failed: {e.stderr}")
            return False

    def _format_command(self, template, value=None):
        variables = {
            'value': value,
            **self.params,
            **self.section.get_all_values()
        }
        return template.format(**variables)

    def _process_output(self, output):
        lines = []
        for line in output.split('\n'):
            line = line.strip()
            if line.startswith('CALLBACK:'):
                self._handle_callback(line)
            else:
                lines.append(line)
        return '\n'.join(lines).strip()

    def _handle_callback(self, line):
        try:
            _, action, target, value = line.split(':', 3)
            self.section.handle_callback(
                action.strip(),
                target.strip(),
                value.strip()
            )
        except ValueError:
            self.logger.error(f"Invalid callback format: {line}")

    def _update_widget(self):
        if self.widget:
            self.widget.update_display()

    @property
    def current_value(self):
        return self.get_value()

    def _get_backend_value(self):
        return self.get_value()

    def _set_backend_value(self, value):
        self.set_value(value)