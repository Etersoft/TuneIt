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

from gi.repository import Adw, Gtk

from .settings import init_settings_stack

@Gtk.Template(resource_path='/ru/ximperlinux/TuteIt/window.ui')
class TuneitWindow(Adw.ApplicationWindow):
    __gtype_name__ = 'TuneitWindow'

    settings_pagestack = Gtk.Template.Child()
    settings_listbox = Gtk.Template.Child()
    settings_split_view = Gtk.Template.Child()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        init_settings_stack(self.settings_pagestack, self.settings_listbox, self.settings_split_view)
