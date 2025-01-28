from .base import Backend
from .gsettings import GSettingsBackend
from .file import FileBackend
from .binary import BinaryBackend


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
