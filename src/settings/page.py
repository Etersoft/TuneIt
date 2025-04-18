import logging
from gi.repository import GLib, Adw

from .widgets.panel_row import TuneItPanelRow


class Page:
    def __init__(self, name, icon=None):
        self.name = name
        self.icon = icon or "preferences-system"  # Значение по умолчанию

        self.logger = logging.getLogger(f"{self.__class__.__name__}[{self.name}]")

        self.sections = []

    def add_section(self, section):
        self.sections.append(section)

    def sort_sections(self):
        self.sections = sorted(self.sections, key=lambda s: s.weight)

    def create_stack_page(self, stack, listbox):
        pref_page = Adw.PreferencesPage()

        not_empty = False

        for section in self.sections:
            preferences_group = section.create_preferences_group()
            if preferences_group:
                pref_page.add(preferences_group)
                not_empty = True
            else:
                self.logger.warn(f"Секция {section.name} не создала виджетов.")

        if not_empty:
            self.update_ui(stack, listbox, pref_page)
        else:
            self.logger.warn(f"the page {self.name} is empty, ignored")

    def update_ui(self, stack, listbox, pref_page):
        stack.add_titled(pref_page, self.name, self.name)

        row = TuneItPanelRow()
        row.props.name = self.name
        row.props.title = self.name
        row.props.icon_name = self.icon
        listbox.append(row)
