from gi.repository import Adw
from ..setting.custom_setting import CustomSetting

from .base import BaseSection

import logging

class CustomSection(BaseSection):
    settings = []

    def __init__(self, section_data, module):
        super().__init__(section_data, module)
        self.logger = logging.getLogger(f"{self.__class__.__name__}[{self.name}]")
        self.settings = [CustomSetting(s, module, self) for s in section_data.get('settings', [])]
        self.settings_dict = {s.orig_name: s for s in self.settings}
        self.module = module
        self.module.add_section(self)
        
        self._callback_buffer = []

    def create_preferences_group(self):
        group = Adw.PreferencesGroup(title=self.name, description=self.module.name)
        not_empty = False

        for setting in self.settings:
            try:
                row = setting.create_row()
                if row:
                    print(f"Adding a row for setting: {setting.name}")
                    group.add(row)
                    not_empty = True
            except Exception as e:
                self.logger.error(f"Error creating row for {setting.orig_name}: {str(e)}")
        
        self._process_buffered_callbacks()
        
        return group if not_empty else None

    def handle_callback(self, action, target, value):
        self.logger.debug(f"handled callback action={action}, target={target}, value={value}")
        try:
            if target not in self.settings_dict:
                self._callback_buffer.append((action, target, value))
                self.logger.debug(f"Buffering callback for {target}")
                return

            self._apply_callback(action, target, value)
                
        except Exception as e:
            self.logger.error(f"Callback handling error: {str(e)}")

    def _apply_callback(self, action, target, value):
        setting = self.settings_dict[target]
        
        if action == 'set':
            setting.create_row = value
            setting._update_widget()

        elif action == 'set_apply':
            setting.set_value(value)

        elif action == 'visible':
            if setting.row:
                setting.row.set_visible(value.lower() == 'true')
        
        elif action == 'enabled':
            if setting.row:
                setting.row.set_sensitive(value.lower() == 'true')
        else:
            self.logger.warning(f"Unknown callback action: {action}")

    def _process_buffered_callbacks(self):
        while self._callback_buffer:
            action, target, value = self._callback_buffer.pop(0)
            try:
                if target in self.settings_dict:
                    self._apply_callback(action, target, value)
                else:
                    self.logger.warning(f"Unknown target after processing buffer: {target}")
            except Exception as e:
                self.logger.error(f"Error processing buffered callback: {str(e)}")

    def get_all_values(self):
        return {
            setting.orig_name: setting._current_value
            for setting in self.settings
        }
