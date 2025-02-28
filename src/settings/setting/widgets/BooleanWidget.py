from gi.repository import Adw, Gtk
from .BaseWidget import BaseWidget


class BooleanWidget(BaseWidget):
    def create_row(self):
        self.row = Adw.ActionRow(title=self.setting.name, subtitle=self.setting.help)

        self.switch = Gtk.Switch(
            valign=Gtk.Align.CENTER,
            halign=Gtk.Align.CENTER,
        )
        self.switch.connect("notify::active", self._on_boolean_toggled)

        self.row.set_activatable_widget(self.switch)

        control_box = Gtk.Box(spacing=6, orientation=Gtk.Orientation.HORIZONTAL)
        control_box.append(self.reset_revealer)
        control_box.append(self.switch)

        self.row.add_suffix(control_box)
        self._update_initial_state()
        return self.row

    def _update_initial_state(self):
        current_value = self.setting._get_backend_value()
        is_active = current_value == self.setting.map.get(True)
        self.switch.set_active(is_active)
        self._update_reset_visibility()

    def update_display(self):
        self._update_initial_state()
    
    def _on_boolean_toggled(self, switch, _):
        value = self.setting.map.get(True) if switch.get_active() else self.setting.map.get(False)
        self.setting._set_backend_value(value)

        self._update_reset_visibility()

    def _on_reset_clicked(self, button):
        default_value = self.setting.map.get(self.setting.default)

        self.setting._set_backend_value(default_value)
        self.switch.set_active(self.setting.default)

        self._update_reset_visibility()

    def _update_reset_visibility(self):
        current_value = self.setting._get_backend_value()
        default_value = self.setting.map.get(self.setting.default)

        self.reset_revealer.set_reveal_child(
            current_value != default_value if default_value is not None
            else False
        )
