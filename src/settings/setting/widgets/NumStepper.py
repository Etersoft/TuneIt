from gi.repository import Adw, Gtk
from .BaseWidget import BaseWidget


class NumStepper(BaseWidget):
    def create_row(self):
        map = self.setting.map
        map_keys = list(map.keys())

        row = Adw.ActionRow(
            title=self.setting.name,
            subtitle=self.setting.help,
            activatable=False
        )

        self.spin = Gtk.SpinButton(
            valign=Gtk.Align.CENTER,
            halign=Gtk.Align.CENTER,
        )

        adjustment = Gtk.Adjustment(
            value=self.setting._get_backend_value(),
            lower=map["lower"],
            upper=map["upper"],
            step_increment=map["step"],
        )
        self.spin.set_adjustment(adjustment)

        if "digits" in map_keys:
            self.spin.set_digits(map["digits"])

        control_box = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL,
            spacing=6,
            margin_start=12
        )
        control_box.append(self.reset_revealer)
        control_box.append(self.spin)

        row.add_suffix(control_box)
        self.spin.connect("value-changed", self._on_num_changed)

        self._update_reset_visibility()

        return row

    def update_display(self):
        current_value = self.setting._get_backend_value()
        self.spin.set_value(float(current_value))
        self._update_reset_visibility()

    def _on_num_changed(self, widget):
        selected_value = widget.get_value()

        self.setting._set_backend_value(selected_value)

        self._update_reset_visibility()

    def _on_reset_clicked(self, button):
        default_value = self.setting.default

        if default_value is not None:
            self.setting._set_backend_value(default_value)
            self.spin.set_value(float(default_value))

        self._update_reset_visibility()

    def _update_reset_visibility(self):
        current_value = float(self.setting._get_backend_value())
        default_value = self.setting.default

        self.reset_revealer.set_reveal_child(
            current_value != default_value if default_value is not None
            else False
        )