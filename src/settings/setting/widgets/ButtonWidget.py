from gi.repository import Adw, Gtk
from .BaseWidget import BaseWidget


class ButtonWidget(BaseWidget):
    def create_row(self):
        self.row = Adw.ButtonRow(
            title=self.setting.name,
        )

        self.row.connect("activated", self._on_button_clicked)

        return self.row

    def _on_button_clicked(self, button):
        self.setting._set_backend_value(True)

    def update_display(self):
        pass
