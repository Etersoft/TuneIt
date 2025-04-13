from gi.repository import GLib, Adw, Gtk

@Gtk.Template(resource_path='/ru.ximperlinux.TuneIt/settings/widgets/deps_alert_dialog.ui')
class TuneItDepsAlertDialog(Adw.AlertDialog):
    __gtype_name__ = "TuneItDepsAlertDialog"
    deps_message_textbuffer = Gtk.Template.Child()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.callback = None

    def ask_user(self, window, callback):
        self.callback = callback
        self.present(window)
        self.connect('response', self.on_response)

    def on_response(self, dialog, response):
        if self.callback:
            self.callback(response)
