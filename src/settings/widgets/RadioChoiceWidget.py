from gi.repository import Gtk, Adw
from .BaseWidget import BaseWidget


class RadioChoiceWidget(BaseWidget):
    def create_row(self):
        main_box = Adw.PreferencesRow()

        content_box = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=6,
            margin_top=8,
            margin_bottom=8,
            margin_start=12,
            margin_end=12
        )
        main_box.set_child(content_box)

        title_horizontal_box = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL,
            hexpand=True,
        )
        content_box.append(title_horizontal_box)

        title_box = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            hexpand=True,
            spacing=1,
        )
        title_horizontal_box.append(title_box)

        title_label = Gtk.Label(
            label=self.setting.name,
            halign=Gtk.Align.START,
        )

        title_box.append(title_label)

        if self.setting.help:
            subtitle_label = Gtk.Label(
                label=self.setting.help,
                halign=Gtk.Align.START,
                wrap=True,
                margin_bottom=4
            )
            subtitle_label.add_css_class("caption")
            subtitle_label.add_css_class("dim-label")

            title_box.append(subtitle_label)

        radio_container = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=8
        )
        content_box.append(radio_container)

        self.radio_buttons = {}
        current_value = self.setting._get_backend_value()
        group = None

        # Создаем радио-кнопки
        for label, value in self.setting.map.items():
            radio = Gtk.CheckButton(
                label=label,
                halign=Gtk.Align.START,
                active=(value == current_value)
            )
            radio.add_css_class('selection-mode')

            if group:
                radio.set_group(group)
            else:
                group = radio

            radio.connect("toggled", self._on_toggle, value)
            radio_container.append(radio)
            self.radio_buttons[value] = radio

        self.reset_revealer.set_halign(Gtk.Align.END)

        title_horizontal_box.append(self.reset_revealer)

        self._update_reset_visibility()

        return main_box

    def _on_toggle(self, button, value):
        if button.get_active():
            self.setting._set_backend_value(value)

            self._update_reset_visibility()

    def _on_reset_clicked(self, button):
        default_value = self.setting.default

        if default_value is not None:
            self.setting._set_backend_value(default_value)

            if default_value in self.radio_buttons:
                self.radio_buttons[default_value].set_active(True)

            self._update_reset_visibility()

    def _update_reset_visibility(self):
        current_value = self.setting._get_backend_value()
        default_value = self.setting.default

        self.reset_revealer.set_reveal_child(
            current_value != default_value if default_value is not None
            else False
        )