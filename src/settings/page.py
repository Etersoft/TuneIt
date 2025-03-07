from gi.repository import Adw

from .widgets.panel_row import TuneItPanelRow


class Page:
    def __init__(self, name, icon=None):
        self.name = name
        self.icon = icon or "preferences-system"  # Значение по умолчанию
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
                print(f"Секция {section.name} не создала виджетов.")

        if not_empty:
            stack_page = stack.add_child(pref_page)
            stack_page.set_title(self.name)
            stack_page.set_name(self.name)

            row = TuneItPanelRow()
            row.props.name = self.name
            row.props.title = self.name
            row.props.icon_name = self.icon
            listbox.append(row)
        else:
            print(f"the page {self.name} is empty, ignored")
