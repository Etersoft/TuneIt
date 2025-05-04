from gi.repository import Adw, Gtk, Gdk
from gi.repository import Gio
import os

from .BaseWidget import BaseWidget


class AvatarWidget(BaseWidget):
    def create_row(self):

        row = Adw.PreferencesRow(
            activatable=False,
            focusable=False
        )

        control_box = Gtk.Box(
            spacing=6,
            orientation=Gtk.Orientation.HORIZONTAL,
            halign=Gtk.Align.CENTER,
            hexpand=True,
            margin_top=12,
            margin_bottom=12,
        )
        
        self.avatar = Adw.Avatar(
            size=128,
            text=None
        )
        
        self.change_button = Gtk.Button(
            icon_name="edit-symbolic",
            valign=Gtk.Align.END,
            halign=Gtk.Align.END,
            margin_bottom=4,
            margin_end=4,
            tooltip_text="Change your avatar"
        )
        self.change_button.get_style_context().add_class("circular")
        self.change_button.get_style_context().add_class("secondary")
        self.change_button.connect("clicked", self._on_change_clicked)
        
        self.reset_button = Gtk.Button(
            icon_name="user-trash-symbolic",
            valign=Gtk.Align.START,
            halign=Gtk.Align.END,
            margin_top=4,
            margin_end=4,
            tooltip_text="Reset the avatar"
        )
        self.reset_button.get_style_context().add_class("circular")
        self.reset_button.get_style_context().add_class("destructive-action")
        self.reset_button.connect("clicked", self._on_reset_clicked)

        self.reset_revealer = Gtk.Revealer(
            transition_type=Gtk.RevealerTransitionType.CROSSFADE,
            transition_duration=150,
            child=self.reset_button,
            reveal_child=False,
            valign=Gtk.Align.START,
            halign=Gtk.Align.END
        )
        
        overlay = Gtk.Overlay()
        overlay.set_child(self.avatar)
        overlay.add_overlay(self.reset_revealer)
        overlay.add_overlay(self.change_button)
        
        control_box.append(overlay)
        row.set_child(control_box)
        
        self.update_display()
        self._update_reset_visibility()

        return row

    def update_display(self):
        current = self.setting._get_backend_value()

        if current and isinstance(current, str) and current.startswith("file://"):
            current = current[7:]
            self.value_separated = True

        if current and os.path.exists(current):
            file = Gio.File.new_for_path(current)
            
            try:
                texture = Gdk.Texture.new_from_file(file)
                self.avatar.set_custom_image(texture)
            except Exception as e:
                self.avatar.set_custom_image(None)
        else:
            self.avatar.set_custom_image(None)

        self._update_reset_visibility()

    def _on_reset_clicked(self, button):
        default_value = self.setting.default

        if default_value is not None:
            if isinstance(default_value, str) and default_value.startswith("file://"):
                default_value = default_value[7:]

            self.setting._set_backend_value(default_value)

            self.update_display()

            self._update_reset_visibility()

    def _update_reset_visibility(self):
        current_value = self.setting._get_backend_value()
        default_value = self.setting.default


        if isinstance(current_value, str) and current_value.startswith("file://"):
            current_value = current_value[7:]

        if current_value:
            current_value = os.path.expanduser(current_value)
            current_value = os.path.expandvars(current_value)

        if default_value:
            default_value = os.path.expanduser(default_value)
            default_value = os.path.expandvars(default_value)

        self.reset_revealer.set_reveal_child(
            current_value != default_value if default_value is not None
            else False
        )

    def _on_change_clicked(self, button):
        dialog = Gtk.FileDialog()

        # Настройка фильтров
        if 'extensions' in self.setting.map:
            filters = self._create_file_filters()
            if filters.get_n_items() > 0:
                dialog.set_filters(filters)
                dialog.set_default_filter(filters.get_item(0))

        try:
            dialog.open(
                parent=button.get_root(),
                callback=self._on_file_selected
            )
        except Exception as e:
            self.logger.error(f"File dialog error: {e}")

    def _create_file_filters(self):
        filters = Gio.ListStore.new(Gtk.FileFilter)
        patterns = [p for p in self.setting.map.get('extensions', [])]

        if patterns:
            file_filter = Gtk.FileFilter()
            file_filter.set_name("Supported files")
            for pattern in patterns:
                if pattern.startswith('.'):
                    file_filter.add_suffix(pattern[1:])
                else:
                    file_filter.add_pattern(pattern)
            filters.append(file_filter)

        return filters

    def _on_file_selected(self, dialog, result):
        try:
            file = dialog.open_finish(result)
            if file:
                self.setting._set_backend_value(file.get_path())

                self.update_display()
        except Exception as e:
            self.logger.error(f"File selection error: {e}")
