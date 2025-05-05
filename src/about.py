# about.py
#
# Copyright 2025 Etersoft
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

from gi.repository import Adw

developers = [
    "Roman Alifanov https://gitlab.eterfund.ru/ximper",
    "Anton Palgunov https://gitlab.eterfund.ru/Toxblh",
    "Kirill Unitsaev https://gitlab.eterfund.ru/fiersik",
    "Vladimir Vaskov <rirusha@altlinux.org>"
]

def build_about_dialog() -> Adw.AboutDialog:
    about = Adw.AboutDialog(
        application_name='tuneit',
        application_icon='ru.ximperlinux.TuneIt',
        developer_name='Etersoft',
        version=tuneit_config.VERSION,
        developers=developers,
        copyright='© 2024-2025 Etersoft'
    )

    # Translators: Replace "translator-credits" with your name/username, and optionally an email or URL.
    about.set_translator_credits(_('translator-credits'))
    return about
