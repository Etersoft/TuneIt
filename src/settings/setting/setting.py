from gi.repository import GLib

import threading
from .base import BaseSetting
from .widgets import WidgetFactory
from ..backends import backend_factory
from ..daemon_client import dclient
from ..tools.gvariant import convert_by_gvariant
from ..widgets.service_dialog import ServiceNotStartedDialog

service_stopped = False


class Setting(BaseSetting):
    def __init__(self, setting_data, module):
        self.backend = setting_data.get('backend')
        self.key = setting_data.get('key')

        super().__init__(setting_data, module)
        self._async_fetch_value()

    def create_row(self):
        if self.root is True:
            self.logger.info("Root is true")
            if dclient is not None:
                self.widget = WidgetFactory.create_widget(self)
                return self.widget.create_row() if self.widget else None

            else:
                global service_stopped

                if service_stopped is False:
                    from ...main import get_main_window
                    dialog = ServiceNotStartedDialog()

                    dialog.present(get_main_window())

                    service_stopped = True
                    return None

        self.widget = WidgetFactory.create_widget(self)
        return self.widget.create_row() if self.widget else None

    def _async_fetch_value(self, force=False):
        def fetch():
            backend = self._get_backend()
            value = self.default
            if backend:
                try:
                    value = backend.get_value(self.key, self.gtype) or self.default
                except Exception as e:
                    self.logger.error(f"Error fetching value: {str(e)}")
            GLib.idle_add(self._update_current_value, value)

        if self._current_value is None or force:
            threading.Thread(target=fetch, daemon=True).start()

    def _update_current_value(self, value):
        if self._current_value != value:
            self._current_value = value
            if self.widget:
                self.widget.update_display()

    def _get_backend_value(self, force=False):
        if force:
            self._async_fetch_value(force=True)
        return self._current_value

    def _get_backend_range(self):
        backend = self._get_backend()
        if backend:
            return backend.get_range(self.key, self.gtype)

    def _set_backend_value(self, value):
        self.logger.info(f"SET VALUE {value}")
        def set_val():
            backend = self._get_backend()
            if backend:
                try:
                    backend.set_value(self.key, value, self.gtype)
                    GLib.idle_add(self._update_current_value, value)
                except Exception as e:
                    self.logger.error(f"Error setting value: {str(e)}")
        threading.Thread(target=set_val, daemon=True).start()

    def _get_backend(self):
        if self.root is True:
            backend = dclient
            backend.set_backend_name(self.backend)
            backend.set_backend_params(self.params)
        else:
            backend = backend_factory.get_backend(self.backend, self.params)
        if not backend:
            self.logger.error(f"Backend {self.backend} not registered.")
        return backend
