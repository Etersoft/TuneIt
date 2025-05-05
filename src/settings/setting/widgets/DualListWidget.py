from gi.repository import Gtk, Adw, GObject, Gdk
from .BaseWidget import BaseWidget

class AddItemsDialog(Adw.AlertDialog):
    __gtype_name__ = 'AddItemsDialog'

    def __init__(self, available_items, selected_items, **kwargs):
        super().__init__(**kwargs)

        self.set_presentation_mode(Adw.DialogPresentationMode.AUTO)

        self.available_items = available_items
        self.selected_items = selected_items

        self.set_heading("Select Items")
        self.set_size_request(360, 500)

        self.search_entry = Gtk.SearchEntry(placeholder_text=_("Search..."))
        self.search_entry.connect("search-changed", self.on_search_changed)

        self.scrolled_window = Gtk.ScrolledWindow(vexpand=True)
        self.list_box = Gtk.ListBox(
            selection_mode=Gtk.SelectionMode.SINGLE,
            css_classes=["boxed-list"]
        )
        self.list_box.connect("row-activated", self.on_row_activated)
        self.scrolled_window.set_child(self.list_box)

        self.content_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        self.content_box.append(self.search_entry)
        self.content_box.append(self.scrolled_window)
        self.set_extra_child(self.content_box)

        self.add_response("cancel", _("_Cancel"))
        self.add_response("add", _("_Add"))
        self.set_response_appearance("add", Adw.ResponseAppearance.SUGGESTED)

        self.populate_list()

    def on_row_activated(self, list_box, row):
        if row.is_selected():
            list_box.unselect_row(row)
        else:
            list_box.select_row(row)

    def populate_list(self):
        for key in self.available_items:
            if key not in self.selected_items:
                row = Adw.ActionRow(title=self.available_items[key])
                row.key = key
                self.list_box.append(row)

        self.list_box.unselect_all()

    def on_search_changed(self, entry):
        search_text = entry.get_text().lower()
        row = self.list_box.get_first_child()
        while row is not None:
            title = row.get_title().lower()
            row.set_visible(search_text in title)
            row = row.get_next_sibling()

    def get_selected(self):
        return [row.key for row in self.list_box.get_selected_rows()]

class DualListWidget(BaseWidget):
    def __init__(self, setting):
        super().__init__(setting)
        self.pending_changes = None
        self.is_reorder_mode = False

    def create_row(self):
        self.main_row = Adw.PreferencesRow(
            activatable=False
        )
        content_box = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            margin_top=8,
            margin_bottom=8,
            margin_start=12,
            margin_end=12
        )
        self.main_row.set_child(content_box)

        header_box = Gtk.Box(spacing=12, margin_bottom=12)
        content_box.append(header_box)

        title_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, hexpand=True)
        title_label = Gtk.Label(
            label=self.setting.name,
            halign=Gtk.Align.START,
            css_classes=["title-4"]
        )
        title_box.append(title_label)

        if self.setting.help:
            subtitle = Gtk.Label(
                label=self.setting.help,
                halign=Gtk.Align.START,
                wrap=True,
                css_classes=["caption", "dim-label"]
            )
            title_box.append(subtitle)

        header_box.append(title_box)
        header_box.append(self.reset_revealer)

        self.add_btn = Gtk.Button(
            label=_("Add"),
            tooltip_text=_("Add items"),
            hexpand=True,
        )
        self.add_btn.connect("clicked", self.show_dialog)

        self.selected_list = Gtk.ListBox(
            css_classes=["boxed-list"],
            selection_mode=Gtk.SelectionMode.NONE
        )
        content_box.append(self.selected_list)

        self.apply_btn = Gtk.Button(
            label=_("Apply"),
            css_classes=["suggested-action"],
            hexpand=True,
            sensitive=False,
        )
        self.apply_btn.connect("clicked", self.on_apply)

        self.reorder_btn = Gtk.ToggleButton(
            label=_("Edit"),
            tooltip_text=_("Toggle reorder mode"),
            hexpand=True
        )
        self.reorder_btn.connect("toggled", self.toggle_reorder_mode)

        button_box = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL,
            spacing=12,
            margin_top=12,
            hexpand=True
        )
        button_box.append(self.add_btn)
        button_box.append(self.apply_btn)
        button_box.append(self.reorder_btn)
        content_box.append(button_box)

        self.update_display()
        return self.main_row

    def create_item_row(self, key, value):
        if key not in self.setting.map:
            return None

        row = Adw.ActionRow(title=value)
        row.key = key

        suffix_box = Gtk.Box(spacing=6, valign=Gtk.Align.CENTER)
        row.add_suffix(suffix_box)

        delete_btn = Gtk.Button(
            icon_name="user-trash-symbolic",
            valign=Gtk.Align.CENTER,
            css_classes=["flat", "circular", "destructive-action"],
            visible=not self.is_reorder_mode
        )
        delete_btn.connect("clicked", self.on_delete_item, row)
        suffix_box.append(delete_btn)

        order_box = Gtk.Box(spacing=4, visible=self.is_reorder_mode)
        suffix_box.append(order_box)

        up_btn = Gtk.Button(
            icon_name="go-up-symbolic",
            css_classes=["flat", "circular"],
            tooltip_text=_("Move up")
        )
        up_btn.connect("clicked", self.on_move_item, row, -1)
        order_box.append(up_btn)

        down_btn = Gtk.Button(
            icon_name="go-down-symbolic",
            css_classes=["flat", "circular"],
            tooltip_text=_("Move down")
        )
        down_btn.connect("clicked", self.on_move_item, row, 1)
        order_box.append(down_btn)

        if self.is_reorder_mode:
            drag_handle = Gtk.Image(
                icon_name="list-drag-handle-symbolic",
            )
            row.add_prefix(drag_handle)
            self.setup_drag_and_drop(row)

        return row

    def setup_drag_and_drop(self, row):
        drag_source = Gtk.DragSource()
        drag_source.set_actions(Gdk.DragAction.MOVE)
        drag_source.connect("prepare", self.on_drag_prepare, row)
        drag_source.connect("drag-begin", self.on_drag_begin, row)
        drag_source.connect("drag-end", self.on_drag_end, row)
        row.add_controller(drag_source)

        drop_target = Gtk.DropTarget.new(GObject.TYPE_STRING, Gdk.DragAction.MOVE)
        drop_target.connect("drop", self.on_drop, row)
        row.add_controller(drop_target)

    def toggle_reorder_mode(self, button):
        self.is_reorder_mode = button.get_active()
        self.update_display()

    def on_move_item(self, button, row, direction):
        current = self.pending_changes if self.pending_changes is not None else self.setting._get_backend_value()
        if not current:
            return

        try:
            index = current.index(row.key)
            new_index = index + direction

            if 0 <= new_index < len(current):
                current.insert(new_index, current.pop(index))
                self.pending_changes = current
                self.apply_btn.set_sensitive(True)
                self.update_display()
        except ValueError:
            pass

    def on_drag_prepare(self, source, x, y, row):
        value = row.key
        return Gdk.ContentProvider.new_for_value(value)

    def on_drag_begin(self, source, drag, row):
        row.add_css_class("dragging")

    def on_drag_end(self, source, drag, delete_data, row):
        row.remove_css_class("dragging")

    def on_drop(self, target, value, x, y, row):
        current = self.pending_changes if self.pending_changes is not None else self.setting._get_backend_value()
        src_item = value
        dst_item = row.key

        if src_item in current and dst_item in current:
            src_idx = current.index(src_item)
            dst_idx = current.index(dst_item)

            current.insert(dst_idx, current.pop(src_idx))
            self.pending_changes = current
            self.apply_btn.set_sensitive(True)
            self.update_display()
            return True
        return False

    def show_dialog(self, button):
        current = self.setting._get_backend_value()
        if self.pending_changes is not None:
            current = self.pending_changes
        dialog = AddItemsDialog(
            self.setting.map,
            current
        )
        dialog.connect("response", self.on_dialog_response)
        dialog.present(self.main_row.get_root())

    def on_dialog_response(self, dialog, response):
        if response == "add":
            selected = dialog.get_selected()
            current = self.setting._get_backend_value() if self.pending_changes is None else self.pending_changes
            new_pending = list(set(current + selected))
            if new_pending != current:
                self.pending_changes = new_pending
                self.update_display()
                self.apply_btn.set_sensitive(True)

    def on_delete_item(self, button, row):
        current = self.setting._get_backend_value() if self.pending_changes is None else self.pending_changes
        if row.key in current:
            new_pending = [k for k in current if k != row.key]
            if new_pending != current:
                self.pending_changes = new_pending
                self.update_display()
                self.apply_btn.set_sensitive(True)

    def update_display(self):
        current = self.setting._get_backend_value()
        if self.pending_changes is not None:
            current = self.pending_changes
        self.reorder_btn.set_sensitive(len(current) > 0)

        while child := self.selected_list.get_first_child():
            self.selected_list.remove(child)

        for key in current:
            if key in self.setting.map:
                row = self.create_item_row(key, self.setting.map[key])
                if row:
                    self.selected_list.append(row)

        self._update_reset_visibility()

    def on_apply(self, button):
        if self.pending_changes is not None:
            self.logger.info(f"applying: {self.pending_changes}")
            self.setting._set_backend_value(self.pending_changes)
            self.pending_changes = None
            self.update_display()
            self.apply_btn.set_sensitive(False)

            self.is_reorder_mode = False
            self.reorder_btn.set_active(False)

    def _on_reset_clicked(self, button):
        self.setting._set_backend_value(self.setting.default or [])
        self.pending_changes = None
        self.update_display()
        self.apply_btn.set_sensitive(False)

        self.is_reorder_mode = False
        self.reorder_btn.set_active(False)

    def _update_reset_visibility(self):
        current = self.setting._get_backend_value() if self.pending_changes is None else self.pending_changes
        is_default = set(current) == set(self.setting.default or [])
        self.reset_revealer.set_reveal_child(not is_default)
