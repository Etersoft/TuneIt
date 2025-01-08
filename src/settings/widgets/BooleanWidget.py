from gi.repository import Adw
from .BaseWidget import BaseWidget

class BooleanWidget(BaseWidget):
    def create_row(self):
        row = Adw.SwitchRow(title=self.setting.name, subtitle=self.setting.help)
        current_value = self.setting._get_backend_value()
        row.set_active(current_value == self.setting.map.get(True))
        row.connect("notify::active", self._on_boolean_toggled)
        return row

    def _on_boolean_toggled(self, switch, _):
        value = self.setting.map.get(True) if switch.get_active() else self.setting.map.get(False)
        self.setting._set_backend_value(value)
