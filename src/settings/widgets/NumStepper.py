from docutils.nodes import subtitle
from gi.repository import Adw, Gtk
from .BaseWidget import BaseWidget

class NumStepper(BaseWidget):
    def create_row(self):
        map = self.setting.map
        map_keys = list(self.setting.map.keys())

        row = Adw.SpinRow(
            title=self.setting.name, subtitle=self.setting.help
        )

        adjustment = Gtk.Adjustment(
            value=self.setting._get_backend_value(),
            lower=map["lower"], upper=map["upper"],
            step_increment=map["step"],
        )
        row.set_adjustment(adjustment)

        if "digits" in map_keys:
            row.set_digits(map["digits"])

        adjustment.connect("value_changed", self._on_num_changed)
        return row

    def _on_num_changed(self, adj):
        selected_value = adj.get_value()
        self.setting._set_backend_value(selected_value)
