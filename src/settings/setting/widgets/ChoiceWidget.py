from gi.repository import Adw, Gtk
from .BaseWidget import BaseWidget

class ChoiceWidget(BaseWidget):
    def create_row(self):
        items = list(self.setting.map.keys())

        self.row = Adw.ActionRow(title=self.setting.name, subtitle=self.setting.help)

        self.dropdown = Gtk.DropDown.new_from_strings(items)
        self.dropdown.set_halign(Gtk.Align.CENTER)
        self.dropdown.set_valign(Gtk.Align.CENTER)

        self.handler_id = self.dropdown.connect("notify::selected", self._on_choice_changed)

        self.row.set_activatable_widget(self.dropdown)

        self._update_dropdown_selection()


        control_box = Gtk.Box(spacing=6, orientation=Gtk.Orientation.HORIZONTAL)
        control_box.append(self.reset_revealer)
        control_box.append(self.dropdown)

        self.row.add_suffix(control_box)
        self._update_reset_visibility()
        return self.row

    def update_display(self):
        self._update_dropdown_selection()
        self._update_reset_visibility()

    def _update_dropdown_selection(self):
        current_index = self.setting._get_selected_row_index()

        with self.dropdown.handler_block(self.handler_id):
            self.dropdown.set_selected(current_index)

    def _on_choice_changed(self, dropdown, _):
        selected = dropdown.get_selected()
        if selected < 0 or selected >= len(self.setting.map):
            return

        selected_value = list(self.setting.map.values())[selected]
        self.setting._set_backend_value(selected_value)
        self._update_reset_visibility()

    def _on_reset_clicked(self, button):
        default_value = self.setting._get_default_row_index()

        if default_value is not None:
            with self.dropdown.handler_block(self.handler_id):
                self.dropdown.set_selected(default_value)
            self.setting._set_backend_value(self.setting.default)

        self._update_reset_visibility()

    def _update_reset_visibility(self):
        current_value = self.setting._get_selected_row_index()
        default_value = self.setting._get_default_row_index()

        self.reset_revealer.set_reveal_child(
            current_value != default_value
            if default_value is not None
            else False
        )