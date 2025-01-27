from gi.repository import Gio, GLib
import os, re
import ast, subprocess

class Backend:
    def __init__(self, params=None):
        # Параметры, передаваемые при инициализации
        self.params = params or {}

    def get_value(self, key, gtype):
        raise NotImplementedError("Метод get_value должен быть реализован")

    def get_range(self, key, gtype):
        raise NotImplementedError("Метод get_range должен быть реализован")

    def set_value(self, key, value, gtype):
        raise NotImplementedError("Метод set_value должен быть реализован")


class GSettingsBackend(Backend):
    def get_value(self, key, gtype):
        schema_name, key_name = key.rsplit('.', 1)
        schema = Gio.Settings.new(schema_name)

        print(f"[DEBUG] Получение значения: schema={schema_name}, key={key_name}, gtype={gtype}")
        try:
            value = schema.get_value(key_name)
            return value.unpack()
        except Exception as e:
            print(f"[ERROR] Ошибка при получении значения {key}: {e}")
            return None

    def get_range(self, key, gtype):
        schema_name, key_name = key.rsplit('.', 1)
        schema = Gio.Settings.new(schema_name)

        print(f"[DEBUG] Получение значения: schema={schema_name}, key={key_name}, gtype={gtype}")
        try:
            value = schema.get_range(key_name)
            return value.unpack()[1]
        except Exception as e:
            print(f"[ERROR] Ошибка при получении значения {key}: {e}")
            return None

    def set_value(self, schema_key, value, gtype):
        schema_name, key_name = schema_key.rsplit('.', 1)
        schema = Gio.Settings.new(schema_name)

        print(f"[DEBUG] Установка значения: schema={schema_name}, key={key_name}, value={value}, gtype={gtype}")
        try:
            schema.set_value(key_name, GLib.Variant(gtype, value))
        except Exception as e:
            print(f"[ERROR] Ошибка при установке значения {schema_key}: {e}")

class FileBackend(Backend):
    def __init__(self, params=None):
        super().__init__(params)
        self.file_path = os.path.expanduser(params.get('file_path'))
        self.file_path = os.path.expandvars(self.file_path)

        self.lines = []
        self.vars = {}
        self._parse_file()

    def _parse_file(self):
        if os.path.exists(self.file_path):
            with open(self.file_path, 'r') as f:
                self.lines = f.readlines()

        for line_num, line in enumerate(self.lines):
            self._parse_line(line_num, line)

    def _parse_line(self, line_num, line):
        line = line.rstrip('\n')
        parsed = {
            'raw': line,
            'active': True,
            'var_name': None,
            'value': None,
            'comment': '',
            'style': {}
        }

        if re.match(r'^\s*#', line):
            parsed['active'] = False
            line = re.sub(r'^\s*#', '', line, count=1)

        var_match = re.match(
            r'^\s*([A-Za-z_][A-Za-z0-9_]*)\s*([=])\s*(.*?)(\s*(#.*)?)$',
            line
        )

        if var_match:
            parsed['var_name'] = var_match.group(1)
            parsed['value'] = self._parse_value(var_match.group(3))
            parsed['comment'] = var_match.group(4) or ''

            value_part = var_match.group(3)
            parsed['style'] = {
                'space_before': ' ' if ' ' in var_match.group(0).split('=')[0][-1:] else '',
                'space_after': ' ' if ' ' in var_match.group(0).split('=')[1][:1] else '',

                'quote': self._detect_quote(var_match.group(3)),
                'commented': not parsed['active']
            }

            if parsed['var_name'] not in self.vars:
                self.vars[parsed['var_name']] = []
            self.vars[parsed['var_name']].append((line_num, parsed))

    @staticmethod
    def _parse_value(value_str):
        value_str = value_str.strip()

        for quote in ['"', "'"]:

            if value_str.startswith(quote) and value_str.endswith(quote):
                return value_str[1:-1]

        return value_str

    @staticmethod
    def _detect_quote(value_str):
        value_str = value_str.strip()

        if value_str.startswith('"') and value_str.endswith('"'):
            return '"'
        if value_str.startswith("'") and value_str.endswith("'"):
            return "'"

        return ''

    def _get_style_template(self):
        if not self.vars:
            return {
                'space_before': '',
                'space_after': ' ',
                'quote': '"',
                'commented': False
            }

        last_var = next(reversed(self.vars.values()))[-1][1]

        return last_var['style']

    @staticmethod
    def _build_line(key, value, style):
        quote = style['quote']
        value_str = f"{quote}{value}{quote}" if quote else str(value)

        return (
            f"{key}{style['space_before']}="
            f"{style['space_after']}{value_str}"
        )

    def _save_file(self):
        with open(self.file_path, 'w') as f:
            f.writelines(self.lines)

    def get_value(self, key, gtype):
        entries = self.vars.get(key, [])

        for entry in reversed(entries):
            return entry[1]['value']

        return None

    def set_value(self, key, value, gtype):
        entries = self.vars.get(key, [])
        style = self._get_style_template()

        key = os.path.expanduser(key)
        key = os.path.expandvars(key)

        if entries:
            line_num, last_entry = entries[-1]
            style = last_entry['style']
            line = self._build_line(key, value, style)

            self.lines[line_num] = line + '\n'

            if last_entry['style']['commented']:
                self.lines[line_num] = self.lines[line_num].lstrip('#')
        else:
            line = self._build_line(key, value, style)
            self.lines.append(line + '\n')

        self._save_file()

class BinaryBackend(Backend):
    def __init__(self, params=None):
        super().__init__(params)
        self.binary_path = os.path.join(
            self.params.get('module_path'),
            self.params.get('binary_path')
        )

        self.binary_name = self.params.get('binary_name')

    def _run_binary(self, command, *args):
        try:
            full_command = (
                [self.binary_path + self.binary_name, command]
                + [x for x in args if x is not None]
            )

            result = subprocess.run(full_command, capture_output=True, text=True, check=True)

            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            print(f"[ERROR] Ошибка при выполнении команды {command}: {e}")
            return None

    def get_value(self, key, gtype):
        print(f"[DEBUG] Получение значения: key={key}, gtype={gtype}")

        result = self._run_binary('get_value', key)

        if result:
            try:
                return ast.literal_eval(result)
            except (ValueError, SyntaxError) as e:
                print(f"[ERROR] Ошибка при преобразовании результата {result}: {e}")
                return result
        return None

    def get_range(self, key, gtype):
        print(f"[DEBUG] Получение диапазона: key={key}, gtype={gtype}")

        result = self._run_binary('get_range', key)

        if not result:
            print(f"[ERROR] Пустой результат или ошибка при выполнении команды get_range для ключа {key}")
            return None

        try:
            parsed_result = ast.literal_eval(result)
            return parsed_result
        except (ValueError, SyntaxError) as e:
            print(f"[ERROR] Ошибка при преобразовании результата {result} для ключа {key}: {e}")
            return None

    def set_value(self, key, value, gtype):
        print(f"[DEBUG] Установка значения: key={key}, value={value}, gtype={gtype}")

        result = self._run_binary('set_value', key, str(value))

        if result:
            try:
                return ast.literal_eval(result)
            except (ValueError, SyntaxError) as e:
                print(f"[ERROR] Ошибка при преобразовании результата {result}: {e}")
        return None

class BackendFactory:
    def __init__(self):
        self.backends = {
            'gsettings': GSettingsBackend,
            'file': FileBackend,
            'binary': BinaryBackend,
        }

    def get_backend(self, backend_name, params=None):
        backend_class = self.backends.get(backend_name)
        if backend_class:
            # Передаем параметры в конструктор бэкенда, если они есть
            return backend_class(params) if params else backend_class()
        return None


backend_factory = BackendFactory()

class RootBackendFactory:
    def __init__(self):
        self.backends = {
            'file': FileBackend,
            'binary': BinaryBackend,

        }

    def get_backend(self, backend_name, params=None):
        backend_class = self.backends.get(backend_name)
        if backend_class:
            # Передаем параметры в конструктор бэкенда, если они есть
            return backend_class(params) if params else backend_class()
        return None


root_backend_factory = RootBackendFactory()
