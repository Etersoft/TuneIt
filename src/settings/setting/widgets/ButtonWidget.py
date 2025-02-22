from gi.repository import Adw, Gtk
from .BaseWidget import BaseWidget


class ButtonWidget(BaseWidget):
    def create_row(self):
        self.row = Adw.ButtonRow(
            title=self.setting.name,
            subtitle=self.setting.help,
        )
        
        self.row.connect("activated", self._on_button_clicked)

        self.row.add_suffix(self.button)

        return self.row

    def _on_button_clicked(self, button):
        self.setting._set_backend_value(True)