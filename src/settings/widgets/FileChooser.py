from gi.repository import Adw, Gtk
from gi.repository import Gio
import os

from .BaseWidget import BaseWidget


class FileChooser(BaseWidget):
    def create_row(self):
        self.value_separated = False
        self.multiple_mode = self.setting.map.get('multiple', False)
        self.folder_mode = 'folder' in self.setting.map.get('extensions', [])

        row = Adw.ActionRow(
            title=self.setting.name,
            subtitle=self.setting.help,
            subtitle_selectable=True
        )

        control_box = Gtk.Box(
            spacing=6,
            margin_end=12,
            halign=Gtk.Align.END
        )
        control_box.append(self.reset_revealer)

        if not self.multiple_mode and not self.folder_mode:
            self.entry = Gtk.Entry(
                placeholder_text="Enter path or click to browse",
                hexpand=True,
                valign=Gtk.Align.CENTER,
                halign=Gtk.Align.END,
            )
            self.entry.connect("changed", self._on_entry_changed)
            control_box.append(self.entry)
        else:
            self.info_label = Gtk.Label(
                label="No selection" if self.folder_mode else "No files selected",
                valign=Gtk.Align.CENTER,
                css_classes=["dim-label"]
            )
            control_box.append(self.info_label)

        self.select_button = Gtk.Button.new_from_icon_name(
            icon_name="folder-open-symbolic"
        )
        self.select_button.set_valign(Gtk.Align.CENTER)

        self.select_button.connect("clicked", self._on_button_clicked)
        control_box.append(self.select_button)

        row.add_suffix(control_box)

        self._update_display()

        self._update_reset_visibility()

        return row

    def _on_reset_clicked(self, button):
        default_value = self.setting.default

        if default_value is not None:
            if isinstance(default_value, str) and default_value.startswith("file://"):
                default_value = default_value[7:]

            self.setting._set_backend_value(default_value)

            self._update_display()

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

    def _update_display(self):
        current = self.setting._get_backend_value()

        self._update_reset_visibility()

        if current and isinstance(current, str) and current.startswith("file://"):
            current = current[7:]
            self.value_separated = True

        if self.folder_mode:
            self._update_folder_display(current)
        elif self.multiple_mode:
            self._update_multiple_files_display(current)
        else:
            self._update_single_file_display(current)

    def _on_button_clicked(self, button):
        dialog = Gtk.FileDialog()

        # Настройка фильтров
        if not self.folder_mode and 'extensions' in self.setting.map:
            filters = self._create_file_filters()
            if filters.get_n_items() > 0:
                dialog.set_filters(filters)
                dialog.set_default_filter(filters.get_item(0))

        # Установка начальной директории
        current = self.setting._get_backend_value()

        if current:
            try:
                current = os.path.expanduser(current)
                current = os.path.expandvars(current)

                current_file = Gio.File.new_for_path(current)
                parent = current_file.get_parent() if not self.folder_mode else current_file
                dialog.set_initial_folder(parent)
            except Exception as e:
                print(f"Error setting initial folder: {e}")

        # Выбор метода открытия
        try:
            if self.folder_mode:
                dialog.select_folder(
                    parent=button.get_root(),
                    callback=self._on_folder_selected
                )
            elif self.multiple_mode:
                dialog.open_multiple(
                    parent=button.get_root(),
                    callback=self._on_files_selected
                )
            else:
                dialog.open(
                    parent=button.get_root(),
                    callback=self._on_file_selected
                )
        except Exception as e:
            print(f"File dialog error: {e}")

    def _create_file_filters(self):
        filters = Gio.ListStore.new(Gtk.FileFilter)
        patterns = [p for p in self.setting.map.get('extensions', []) if p != 'folder']

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

                self._update_display()
        except Exception as e:
            print(f"File selection error: {e}")

    def _on_files_selected(self, dialog, result):
        try:
            file_list = dialog.open_multiple_finish(result)
            if file_list:
                paths = [f.get_path() for f in file_list]
                self.setting._set_backend_value(paths)
                self._update_display()
        except Exception as e:
            print(f"Multiple files selection error: {e}")

    def _on_folder_selected(self, dialog, result):
        try:
            folder = dialog.select_folder_finish(result)
            if folder:
                self.setting._set_backend_value(folder.get_path())
                self._update_display()
        except Exception as e:
            print(f"Folder selection error: {e}")

    def _update_folder_display(self, current):
        if current:
            folder = Gio.File.new_for_path(current)
            self.info_label.set_label(folder.get_basename() or current)
        else:
            self.info_label.set_label("No folder selected")

    def _update_multiple_files_display(self, current):
        count = len(current) if current else 0
        self.info_label.set_label(f"{count} files selected" if count else "No files selected")

    def _update_single_file_display(self, current):
        self.entry.set_text(current or "")
        if current:
            file = Gio.File.new_for_path(current)
            self.entry.set_tooltip_text(file.get_parse_name())
        else:
            self.entry.set_tooltip_text(None)

    def _on_entry_changed(self, entry):
        if not self.folder_mode and not self.multiple_mode:
            path = entry.get_text().strip()
            self.setting._set_backend_value(path)

            self._update_reset_visibility()