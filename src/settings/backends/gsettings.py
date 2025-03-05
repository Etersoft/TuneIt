from gi.repository import Gio, GLib

from .base import Backend


class GSettingsBackend(Backend):
    def _get_schema(self, schema_name):
        source = Gio.SettingsSchemaSource.get_default()

        if source.lookup(schema_name, True) is None:
            print(f"[ERROR] Scheme {schema_name} is not installed")
            return None

        return Gio.Settings.new(schema_name)

    def get_value(self, key, gtype):
        schema_name, key_name = key.rsplit('.', 1)
        schema = self._get_schema(schema_name)

        if not schema:
            return None

        try:
            value = schema.get_value(key_name)
            return value.unpack()
        except Exception as e:
            print(f"[ERROR] Error when getting the value {key}: {e}")
            return None

    def get_range(self, key, gtype):
        schema_name, key_name = key.rsplit('.', 1)
        schema = self._get_schema(schema_name)

        if not schema:
            return None

        try:
            value = schema.get_range(key_name)
            return value.unpack()[1]
        except Exception as e:
            print(f"[ERROR] Error when getting the range {key}: {e}")
            return None

    def set_value(self, schema_key, value, gtype):
        schema_name, key_name = schema_key.rsplit('.', 1)
        schema = self._get_schema(schema_name)

        if not schema:
            return

        try:
            schema.set_value(key_name, GLib.Variant(gtype, value))
        except Exception as e:
            print(f"[ERROR] Error when setting the value {schema_key}: {e}")
