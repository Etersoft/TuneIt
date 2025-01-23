from gi.repository import GObject, Adw, Gtk


@Gtk.Template(resource_path='/ru.ximperlinux.TuneIt/settings/widgets/panel_row.ui')
class TuneItPanelRow(Gtk.ListBoxRow):

    __gtype_name__ = "TuneItPanelRow"

    name = GObject.Property(type=str, default='')
    title = GObject.Property(type=str, default='')
    subtitle = GObject.Property(type=str, default='')
    subtitle_visible = GObject.Property(type=bool, default=False)
    icon_name = GObject.Property(type=str, default='')
