from gi.repository import Gio, GLib
import json
import yaml
import os
from configparser import ConfigParser


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
        self.file_path = os.path.expanduser(self.params.get('file_path'))
        self.encoding = self.params.get('encoding', 'utf-8')
        self.file_type = self._get_file_type()

    def _get_file_type(self):
        _, ext = os.path.splitext(self.file_path)
        ext = ext.lower()
        if ext == '.json':
            return 'json'
        elif ext in ['.yaml', '.yml']:
            return 'yaml'
        elif ext == '.ini':
            return 'ini'
        elif ext in ['.sh', '.conf']:
            return 'text'
        else:
            return 'text'

    def _read_file(self):
        try:
            with open(self.file_path, 'r', encoding=self.encoding) as file:
                if self.file_type == 'json':
                    return json.load(file)
                elif self.file_type == 'yaml':
                    return yaml.safe_load(file)
                elif self.file_type == 'ini':
                    config = ConfigParser()
                    config.read_file(file)
                    return config
                elif self.file_type == 'text':
                    return self._parse_text_config(file)
                else:
                    raise ValueError(f"Unsupported file type: {self.file_type}")
        except Exception as e:
            print(f"[ERROR] Ошибка при чтении файла {self.file_path}: {e}")
            return None

    def _write_file(self, data):
        try:
            with open(self.file_path, 'r+', encoding=self.encoding) as file:
                if self.file_type == 'json':
                    file.seek(0)
                    json.dump(data, file, indent=4)
                elif self.file_type == 'yaml':
                    file.seek(0)
                    yaml.dump(data, file, default_flow_style=False)
                elif self.file_type == 'ini':
                    file.seek(0)
                    config = ConfigParser()
                    for section, values in data.items():
                        config[section] = values
                    config.write(file)
                elif self.file_type == 'text':
                    self._write_text_config(file, data)
                else:
                    raise ValueError(f"Unsupported file type: {self.file_type}")
        except Exception as e:
            print(f"[ERROR] Ошибка при записи в файл {self.file_path}: {e}")

    def _parse_text_config(self, file):
        config = {}
        for line in file:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if '=' in line:
                key, value = line.split('=', 1)
                config[key.strip()] = value.strip()
        return config

    def _write_text_config(self, file, data):
        existing_lines = file.readlines()
        style = self._detect_text_style(existing_lines)

        file.seek(0)
        file.truncate()

        for line in existing_lines:
            if not line.strip() or line.startswith('#'):
                file.write(line)
            elif '=' in line:
                key, _ = line.split('=', 1)
                if key.strip() in data:
                    if style == 'space_around':
                        file.write(f"{key.strip()} = {data[key.strip()]}\n")
                    elif style == 'no_space':
                        file.write(f"{key.strip()}={data[key.strip()]}\n")
                    else:
                        file.write(f"{key.strip()} = {data[key.strip()]}\n")
                else:
                    file.write(line)

        for key, value in data.items():
            if not any(key.strip() == line.split('=', 1)[0].strip() for line in existing_lines):
                file.write(f"{key} = {value}\n")

    def _detect_text_style(self, lines):
        for line in lines:
            line = line.strip()
            if '=' in line:
                if line.startswith(' ') and line.endswith(' '):
                    return 'space_around'
                elif line.find('=') == len(line.split('=')[0]):
                    return 'no_space'
        return 'space_around'

    def get_value(self, key, gtype):
        data = self._read_file()
        if data is None:
            return None

        if self.file_type in ['json', 'yaml']:
            return data.get(key, None)
        elif self.file_type == 'ini':
            section, key_name = key.split('.', 1)
            if section in data:
                return data[section].get(key_name, None)
        elif self.file_type == 'text':
            return data.get(key, None)
        return None

    def get_range(self, key, gtype):
        data = self._read_file()
        if data is None:
            return None

        if self.file_type in ['json', 'yaml']:
            if isinstance(data.get(key), list):
                return (min(data[key]), max(data[key]))
        elif self.file_type == 'ini':
            pass
        return None

    def set_value(self, key, value, gtype):
        data = self._read_file()
        if data is None:
            return

        if self.file_type in ['json', 'yaml']:
            data[key] = value
        elif self.file_type == 'ini':
            section, key_name = key.split('.', 1)
            if section not in data:
                data[section] = {}
            data[section][key_name] = value
        elif self.file_type == 'text':
            data[key] = value

        self._write_file(data)

class BackendFactory:
    def __init__(self):
        self.backends = {
            'gsettings': GSettingsBackend,
            'file': FileBackend,
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
        }

    def get_backend(self, backend_name, params=None):
        backend_class = self.backends.get(backend_name)
        if backend_class:
            # Передаем параметры в конструктор бэкенда, если они есть
            return backend_class(params) if params else backend_class()
        return None


root_backend_factory = RootBackendFactory()
