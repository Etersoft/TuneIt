from gi.repository import Adw

from .base_strategy import SectionStrategy


class ClassicSectionStrategy(SectionStrategy):
    def create_preferences_group(self, section):
        group = Adw.PreferencesGroup(title=section.name, description=section.module.name)
        not_empty = False

        for setting in section.settings:
            row = setting.create_row()
            if row:
                print(f"Добавление строки для настройки: {setting.name}")
                group.add(row)
                not_empty = True
            else:
                print(f"Не удалось создать строку для настройки: {setting.name}")
        if not_empty:
            return group
        else:
            return None
