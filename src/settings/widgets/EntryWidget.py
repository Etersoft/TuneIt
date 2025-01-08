from gi.repository import Adw
from .BaseWidget import BaseWidget

class EntryWidget(BaseWidget):
    def create_row(self):
        row = Adw.EntryRow(title=self.setting.name)
        row.set_show_apply_button(True)
        row.set_text(self.setting._get_backend_value())
        row.connect("apply", self._on_text_changed)
        return row

    def _on_text_changed(self, entry_row):
        self.setting._set_backend_value(entry_row.get_text())
