from gi.repository import GObject, Adw, Gtk


@Gtk.Template(resource_path='/ru.ximperlinux.TuneIt/settings/widgets/panel_row.ui')
class TuneItPanelRow(Adw.PreferencesRow):
    __gtype_name__ = "TuneItPanelRow"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @GObject.Property(type=str, default="")
    def icon_name(self):
        return self._icon_name

    @icon_name.setter
    def icon_name(self, icon_name):
        self._icon_name = icon_name

    @GObject.Property(type=str, default="")
    def subtitle(self):
        return self._subtitle

    @subtitle.setter
    def subtitle(self, subtitle):
        self._subtitle = subtitle
