import webbrowser
from gi.repository import Adw, Gtk, Gdk

@Gtk.Template(resource_path='/ru.ximperlinux.TuneIt/settings/widgets/error_dialog.ui')
class TuneItErrorDialog(Adw.AlertDialog):

    __gtype_name__ = "TuneItErrorDialog"
    textbuffer = Gtk.Template.Child()
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.connect('response', self.on_response)

    def on_response(self, _, response):
        if response == 'copy':
            self.on_copy()

    def on_copy(self):
        self.copy_error()
        webbrowser.open("https://t.me/tuneit")

    def copy_error(self):
        display = Gdk.Display.get_default()
        clipboard = display.get_clipboard()
        clipboard.set(self.textbuffer.get_text(
            self.textbuffer.get_start_iter(),
            self.textbuffer.get_end_iter(),
            False
        ))
