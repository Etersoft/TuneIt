from gi.repository import Gio, GLib

class Backend:
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
            return value.unpack()
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


class BackendFactory:
    def __init__(self):
        self.backends = {
            'gsettings': GSettingsBackend(),
        }

    def get_backend(self, name):
        return self.backends.get(name)


backend_factory = BackendFactory()
