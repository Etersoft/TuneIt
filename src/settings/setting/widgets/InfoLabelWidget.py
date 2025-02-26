from gi.repository import Adw, Gtk, GLib
from .BaseWidget import BaseWidget


class InfoLabelWidget(BaseWidget):
    def create_row(self):
        self.row = Adw.ActionRow(title=self.setting.name, subtitle=self.setting.help)

        self.label = Gtk.Label(
            valign=Gtk.Align.CENTER,
            halign=Gtk.Align.CENTER,
        )
        self.label.add_css_class("dim-label")

        control_box = Gtk.Box(spacing=6, orientation=Gtk.Orientation.HORIZONTAL)
        control_box.append(self.label)

        self.row.add_suffix(control_box)
        self._update_initial_state()
        return self.row

    def _update_initial_state(self):
        current_value = self.setting._get_backend_value()
        print(current_value)
        self.label.set_label(current_value)

    def update_display(self):
        self._update_initial_state()
