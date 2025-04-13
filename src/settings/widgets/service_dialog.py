import os
import subprocess
import sys
from time import sleep

from gi.repository import GLib, Adw

class ServiceNotStartedDialog(Adw.AlertDialog):

    response = ""

    def __init__(self):
        super().__init__()

        self.sname = 'tuneit-daemon'

        self.set_heading(_("Dbus service is disabled or unresponsive."))
        self.set_body(_("It is needed for modules that require root permissions.\nDo you want to try to turn on the service?\nTune It will restart after enabling the service."))

        self.add_response("yes", _("Yes"))
        self.add_response("no", _("No"))

        self.connect('response', on_response)

    def on_response(self, dialog, response):
        if response == "yes":
            self.service_enable_with_restart()

        elif response in ("no", "close"):
            dialog.close()

    def service_status(self):
        try:
            # Запускаем команду systemctl is-active <service_name>
            result = subprocess.run(
                ['systemctl', 'is-active', self.sname],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )
            # Проверяем статус
            if result.stdout.decode('utf-8').strip() == 'active':
                return True
            else:
                return False
        except Exception as e:
            print(f"An error occurred: {e}")
            return False

    def service_enable(self):
        try:
            subprocess.run(
                ['pkexec', 'systemctl', '--now', 'enable', self.sname],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )
        except Exception as e:
            print(f"An error occurred: {e}")

    def service_enable_with_restart(self):
        self.service_enable()
        self.close()

        os.execv(sys.argv[0], sys.argv)
