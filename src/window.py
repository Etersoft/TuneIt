# window.py
#
# Copyright 2024 Etersoft
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# SPDX-License-Identifier: GPL-3.0-or-later

import threading, traceback
from gi.repository import GObject, Adw, Gtk, GLib

from .settings.main import init_settings_stack

from .settings.widgets.error_dialog import TuneItErrorDialog

@Gtk.Template(resource_path='/ru.ximperlinux.TuneIt/window.ui')
class TuneitWindow(Adw.ApplicationWindow):
    __gtype_name__ = 'TuneitWindow'


    settings_toast_overlay = Gtk.Template.Child()

    settings_pagestack = Gtk.Template.Child()
    settings_listbox = Gtk.Template.Child()
    settings_split_view = Gtk.Template.Child()

    @GObject.Signal
    def settings_page_update(self):
        pass

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.error_dialog = TuneItErrorDialog()

        self.connect('settings_page_update', self.update_settings_page)

        if tuneit_config.IS_DEVEL:
            print("!!! DEVEL BUILD")
            self.add_css_class("devel")

        self.update_settings_page()

    def update_settings_page(self):
        thread = threading.Thread(target=self._update_settings_page)
        thread.daemon = True
        thread.start()

    def _update_settings_page(self, *args):
        """
        Можно вызвать вот так, благодаря сигналу:
        self.settings_pagestack.get_root().emit("settings_page_update")
        """
        self.setting_notify("Tune It", "Init settings...")
        try:
            init_settings_stack(
                self.settings_pagestack,
                self.settings_listbox,
                self.settings_split_view,
            )
            self.setting_notify("Tune It", "Settings are initialized!")

        except Exception as e:
            self.error(traceback.format_exc())

    def error(self, error):
        print(error)

        self.error_dialog.textbuffer.set_text(str(error))
        GLib.idle_add(self.error_dialog.present, self)

    def setting_notify(self, module_name: str, notify: str, seconds: int = 5) -> None:
        seconds = 5 if seconds is None else seconds

        GLib.idle_add(self.settings_toast_overlay.dismiss_all)

        toast = Adw.Toast(
            title=f"{module_name}: {notify}",
            timeout=seconds,
        )
        GLib.idle_add(self.settings_toast_overlay.add_toast, toast)