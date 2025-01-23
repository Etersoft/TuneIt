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

        title_label = Gtk.Label(
            label=self.setting.name,
            halign=Gtk.Align.START
        )
        title_label.add_css_class("heading")

        content_box.append(title_label)

        if self.setting.help:
            subtitle_label = Gtk.Label(
                label=self.setting.help,
                halign=Gtk.Align.START,
                wrap=True,
                margin_bottom=4
            )
            subtitle_label.add_css_class("caption")
            subtitle_label.add_css_class("dim-label")

            content_box.append(subtitle_label)

        radio_container = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=4
        )

        content_box.append(radio_container)

        current_value = self.setting._get_backend_value()
        group = None

        # Создаем радио-кнопки
        for label, value in self.setting.map.items():
            radio = Gtk.CheckButton(
                label=label,
                halign=Gtk.Align.START,
            )
            radio.set_active(value == current_value)

            if group:
                radio.set_group(group)
            else:
                group = radio

            radio.connect("toggled", self._on_toggle, value)
            radio_container.append(radio)

        return main_box

    def _on_toggle(self, button, value):
        if button.get_active():
            self.setting._set_backend_value(value)

