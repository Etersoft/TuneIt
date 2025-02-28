from gi.repository import Adw, Gtk
from .BaseWidget import BaseWidget

class InfoDictWidget(BaseWidget):
    def create_row(self):
        main_box = Adw.PreferencesRow()
        main_box.set_activatable(False)
        
        content_box = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            margin_top=8,
            margin_bottom=8,
            margin_start=12,
            margin_end=12
        )
        main_box.set_child(content_box)

        title_label = Gtk.Label(
            label=self.setting.name,
            halign=Gtk.Align.START,
            margin_bottom=6
        )
        content_box.append(title_label)

        if self.setting.help:
            subtitle_label = Gtk.Label(
                label=self.setting.help,
                halign=Gtk.Align.START,
                wrap=True,
                margin_bottom=8
            )
            subtitle_label.add_css_class("dim-label")
            content_box.append(subtitle_label)

        self.main_list = Gtk.ListBox()
        self.main_list.set_selection_mode(Gtk.SelectionMode.NONE)
        self.main_list.add_css_class('boxed-list')
        content_box.append(self.main_list)
        
        self._update_initial_state()
        return main_box

    def _create_value_label(self, value, level):
        label = Gtk.Label(
            label=str(value),
            halign=Gtk.Align.END,
            hexpand=True,
            margin_start=12,
            margin_end=12 * level
        )
        label.add_css_class('dim-label')
        return label

    def _render_value(self, value, container, level=0):
        if isinstance(value, dict):
            self._render_dict(value, container, level)
        elif isinstance(value, (list, tuple)):
            self._render_list(value, container, level)
        else:
            container.append(self._create_value_label(value, level))

    def _render_dict(self, data, parent_container, level):
        for key, value in data.items():
            row = Adw.ActionRow()
            row.set_title(key)
            row.set_activatable(False)
            
            if isinstance(value, (dict, list, tuple)):
                value_widget = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
                self._render_value(value, value_widget, level + 1)
            else:
                value_widget = self._create_value_label(value, level)
            
            row.add_suffix(value_widget)
            parent_container.append(row)

    def _render_list(self, data, parent_container, level):
        for item in data:
            row = Adw.ActionRow()
            row.set_title("•")
            row.set_activatable(False)
            
            if isinstance(item, (dict, list, tuple)):
                value_widget = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
                self._render_value(item, value_widget, level + 1)
            else:
                value_widget = self._create_value_label(item, level)
            
            row.add_suffix(value_widget)
            parent_container.append(row)

    def _update_initial_state(self):
        current_value = self.setting._get_backend_value() or {}
        while child := self.main_list.get_first_child():
            self.main_list.remove(child)
        self._render_value(current_value, self.main_list, 0)

    def update_display(self):
        self._update_initial_state()
