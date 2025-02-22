from gi.repository import Gtk

class BaseWidget:
    def __init__(self, setting):
        self.setting = setting

        self.reset_button = Gtk.Button(
            icon_name="edit-undo-symbolic",
            valign=Gtk.Align.CENTER,
            halign=Gtk.Align.CENTER,
            tooltip_text=_("Restore Default")
        )
        self.reset_button.add_css_class('flat')

        self.reset_button.connect("clicked", self._on_reset_clicked)

        self.reset_revealer = Gtk.Revealer(
            transition_type=Gtk.RevealerTransitionType.CROSSFADE,
            transition_duration=150,
            child=self.reset_button,
            reveal_child=False,
            halign=Gtk.Align.END
        )
    def update_display(self):
        raise NotImplementedError("update_display method should be implemented in the subclass")

    def set_visible(self, visible: bool):
        self.row.set_visible(visible)
        
    def set_enabled(self, enabled: bool):
        self.row.set_sensitive(enabled)

    def create_row(self):
        raise NotImplementedError("create_row method should be implemented in the subclass")

    def _on_reset_clicked(self, button):
        raise NotImplementedError("_on_reset_clicked method should be implemented in the subclass")
