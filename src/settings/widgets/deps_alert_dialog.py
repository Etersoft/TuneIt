from gi.repository import GObject, Adw, Gtk
from time import sleep

@Gtk.Template(resource_path='/ru.ximperlinux.TuneIt/settings/widgets/deps_alert_dialog.ui')
class TuneItDepsAlertDialog(Adw.AlertDialog):

    __gtype_name__ = "TuneItDepsAlertDialog"
    deps_message_textbuffer = Gtk.Template.Child()

    response = ""

    def user_question(self, window):
        self.present(window)
        
        def on_response(dialog, response):
            self.response = response

        self.connect('response', on_response)
        
        while True:
            if self.response != "":
                return self.response
            else:
                sleep(0.1)
                continue
