from gi.repository import Adw
from ..setting.setting import Setting

from .base import BaseSection

class ClassicSection(BaseSection):
    def __init__(self, section_data, module):
        super().__init__(section_data, module)
        self.settings = [Setting(s, module) for s in section_data.get('settings', [])]
        self.module = module

        self.module.add_section(self)

    def create_preferences_group(self):
        group = Adw.PreferencesGroup(title=self.name, description=self.module.name)
        not_empty = False

        for setting in self.settings:
            row = setting.create_row()
            if row:
                print(f"Adding a row for setting: {setting.name}")
                group.add(row)
                not_empty = True
            else:
                print(f"Failed to create a row for setting: {setting.name}")
        if not_empty:
            return group
        else:
            return None
