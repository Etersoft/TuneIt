from gi.repository import Adw, Gtk

from .backends import backend_factory
from .tools.yml_tools import load_yaml_files_from_directory, merge_categories_by_name
from .widgets import WidgetFactory


class Setting:
    def __init__(self, setting_data):
        self.name = setting_data['name']
        self.type = setting_data['type']
        self.help = setting_data.get('help', "")
        self.backend = setting_data.get('backend')
        self.key = setting_data.get('key')
        self.default = setting_data.get('default')
        self.map = setting_data.get('map', self._default_map())
        if setting_data.get('gtype'):
            self.gtype = setting_data.get('gtype')[0]
        self.data = setting_data.get('data', {})

    def _default_map(self):
        if self.type == 'boolean':
            # Дефолтная карта для булевых настроек
            return {True: True, False: False}
        return {}

    def create_row(self):
        widget = WidgetFactory.create_widget(self)
        return widget.create_row() if widget else None

    def _get_selected_row_index(self):
        current_value = self._get_backend_value()
        return list(self.map.values()).index(current_value) if current_value in self.map.values() else 0

    def _get_backend_value(self):
        backend = self._get_backend()
        if backend:
            return backend.get_value(self.key, self.gtype)
        return self.default

    def _set_backend_value(self, value):
        backend = self._get_backend()
        if backend:
            backend.set_value(self.key, value, self.gtype)

    def _get_backend(self):
        backend = backend_factory.get_backend(self.backend)
        if not backend:
            print(f"Бекенд {self.backend} не зарегистрирован.")
        return backend


class Section:
    def __init__(self, section_data, strategy):
        self.name = section_data['name']
        self.weight = section_data.get('weight', 0)
        self.settings = [Setting(s) for s in section_data.get('settings', [])]
        self.strategy = strategy

    def create_preferences_group(self):
        return self.strategy.create_preferences_group(self)


class SectionStrategy:
    def create_preferences_group(self, section):
        raise NotImplementedError("Метод create_preferences_group должен быть реализован")


class ClassicSectionStrategy(SectionStrategy):
    def create_preferences_group(self, section):
        group = Adw.PreferencesGroup(title=section.name)
        for setting in section.settings:
            row = setting.create_row()
            if row:
                print(f"Добавление строки для настройки: {setting.name}")
                group.add(row)
            else:
                print(f"Не удалось создать строку для настройки: {setting.name}")
        return group


class NewSectionStrategy(SectionStrategy):
    def create_preferences_group(self, section):
        group = Adw.PreferencesGroup(title=section.name)
        print(f"Создание секции нового типа: {section.name}")
        for setting in section.settings:
            row = setting.create_row()
            group.add(row)
        return group


class SectionFactory:
    def __init__(self):
        self.strategies = {
            'classic': ClassicSectionStrategy(),
        }

    def create_section(self, section_data):
        section_type = section_data.get('type', 'classic')

        strategy = self.strategies.get(section_type)
        if not strategy:
            raise ValueError(f"Неизвестный тип секции: {section_type}")
        return Section(section_data, strategy)


class Category:
    def __init__(self, category_data, section_factory: SectionFactory):
        self.name = category_data['name']
        self.weight = category_data.get('weight', 0)
        self.sections = [section_factory.create_section(s) for s in category_data.get('sections', [])]

    def create_stack_page(self, stack):
        box = Gtk.ScrolledWindow()
        pref_page = Adw.PreferencesPage()
        clamp = Adw.Clamp()
        clamp.set_child(pref_page)
        box.set_child(clamp)

        for section in self.sections:
            preferences_group = section.create_preferences_group()
            if preferences_group:
                pref_page.add(preferences_group)
            else:
                print(f"Секция {section.name} не создала виджетов.")

        stack.add_child(box).set_title(self.name)


def init_settings_stack(stack):
    yaml_files_directory = "/usr/share/ximper-tuneit/modules"  # Укажите путь к папке с YAML файлами
    yaml_data = load_yaml_files_from_directory(yaml_files_directory)
    merged_data = merge_categories_by_name(yaml_data)
    section_factory = SectionFactory()

    categories = [Category(c, section_factory) for c in merged_data]

    for category in categories:
        category.create_stack_page(stack)
    if not stack:
        print("Ошибка: settings_pagestack не найден.")
