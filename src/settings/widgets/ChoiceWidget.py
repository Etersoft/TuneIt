from gi.repository import Adw, Gtk
from .BaseWidget import BaseWidget

class ChoiceWidget(BaseWidget):
    def create_row(self):
        row = Adw.ComboRow(title=self.setting.name, subtitle=self.setting.help)
        row.set_model(Gtk.StringList.new(list(self.setting.map.keys())))
        row.set_selected(self.setting._get_selected_row_index())
        row.connect("notify::selected", self._on_choice_changed)
        return row

    def _on_choice_changed(self, combo_row, _):
        selected_value = list(self.setting.map.values())[combo_row.get_selected()]
        self.setting._set_backend_value(selected_value)
