import logging
from gi.repository import Adw
from ..setting.setting import Setting

from .base import BaseSection

class ClassicSection(BaseSection):
    def __init__(self, section_data, module):
        super().__init__(section_data, module)
        self.logger = logging.getLogger(f"{self.__class__.__name__}[{self.name}]")
        self.settings = [Setting(s, module) for s in section_data.get('settings', [])]
        self.settings = sorted(self.settings, key=lambda s: s.weight, reverse=True)
        self.module = module

        self.module.add_section(self)

    def create_preferences_group(self):
        group = Adw.PreferencesGroup(title=self.name, description=self.module.name)
        not_empty = False

        for setting in self.settings:
            row = setting.create_row()
            if row:
                self.logger.debug(f"Adding a row for setting: {setting.name}")
                group.add(row)
                not_empty = True
            else:
                self.logger.debug(f"Failed to create a row for setting: {setting.name}")
        if not_empty:
            return group
        else:
            return None
