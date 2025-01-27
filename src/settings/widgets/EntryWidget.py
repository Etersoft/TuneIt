from gi.repository import Gtk, Adw
from .BaseWidget import BaseWidget


class EntryWidget(BaseWidget):
    def create_row(self):
        self.row = Adw.ActionRow(title=self.setting.name)

        self.entry = Gtk.Entry()
        self.entry.set_halign(Gtk.Align.CENTER)

        self.entry.set_text(self.setting._get_backend_value() or "")

        self.entry.connect("activate", self._on_text_changed)


        control_box = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL,
            spacing=6,
            margin_start=12,
            valign=Gtk.Align.CENTER,
            halign=Gtk.Align.CENTER,
        )
        control_box.append(self.reset_revealer)
        control_box.append(self.entry)

        self.row.add_suffix(control_box)

        self._update_reset_visibility()

        return self.row

    def _on_text_changed(self, entry):
        new_value = entry.get_text()

        self.setting._set_backend_value(new_value)

        self._update_reset_visibility()

    def _on_reset_clicked(self, button):
        default_value = self.setting.default

        self.setting._set_backend_value(default_value)
        self.entry.set_text(str(default_value))

        self._update_reset_visibility()

    def _update_reset_visibility(self):
        current_value = self.entry.get_text() or ""
        default_value = self.setting.default

        has_default = self.setting.default is not None
        is_default = current_value == default_value

        self.reset_revealer.set_reveal_child(not is_default and has_default)