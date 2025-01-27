from gi.repository import Adw, Gtk

import os
import gettext
import locale

from .backends import backend_factory
from .daemon_client import dclient

from .tools.yml_tools import load_modules
from .tools.gvariant import convert_by_gvariant
from .widgets import WidgetFactory
from .widgets.panel_row import TuneItPanelRow

from .widgets.service_dialog import ServiceNotStartedDialog

dialog_presented = False

class Setting:
    def __init__(self, setting_data, module):
        self._ = module.get_translation

        self.name = self._(setting_data['name'])

        self.root = setting_data.get('root', False)

        self.backend = setting_data.get('backend')

        self.params = {
            **setting_data.get('params', {}),
            'module_path': module.path
        }

        self.type = setting_data['type']

        self.help = setting_data.get('help', None)
        if self.help is not None:
            self.help = self._(self.help)

        self.key = setting_data.get('key')
        self.default = setting_data.get('default')
        self.gtype = setting_data.get('gtype', [])

        self.map = setting_data.get('map')
        if self.map is None:
            self.map = self._default_map()

        if isinstance(self.map, dict) and self.type == 'choice':
            self.map = {
                self._(key) if isinstance(key, str) else key: value
                for key, value in self.map.items()
            }

        if len(self.gtype) > 2:
            self.gtype = self.gtype[0]
        else:
            self.gtype = self.gtype

    def _default_map(self):
        if self.type == 'boolean':
            # Дефолтная карта для булевых настроек
            return {True: True, False: False}
        if self.type == 'choice':
            # Дефолтная карта для выборов
            map = {}
            range = self._get_backend_range()

            if range is None:
                return {}

            for var in range:
                print(var)
                map[var[0].upper() + var[1:]] = var
            return map
        if self.type == 'number':
            map = {}
            range = self._get_backend_range()

            if range is None:
                return {}

            map["upper"] = range[1]
            map["lower"] = range[0]

            # Кол-во после запятой
            map["digits"] = len(str(range[0]).split('.')[-1]) if '.' in str(range[0]) else 0
            # Минимальное число с этим количеством
            map["step"] = 10 ** -map["digits"] if map["digits"] > 0 else 0
            return map
        return {}

    def create_row(self):
        if self.root is True:
            print("Root is true")
            if dclient is not None:
                widget = WidgetFactory.create_widget(self)
                return widget.create_row() if widget else None
            else:
                global dialog_presented
                if dialog_presented is False:
                    from ..main import get_main_window

                    dialog = ServiceNotStartedDialog()
                    dialog.present(get_main_window())

                    dialog_presented = True
                return None


        widget = WidgetFactory.create_widget(self)
        return widget.create_row() if widget else None

    def _get_selected_row_index(self):
        current_value = self._get_backend_value()
        return list(self.map.values()).index(current_value) if current_value in self.map.values() else 0

    def _get_default_row_index(self):
        return list(self.map.values()).index(self.default) if self.default in self.map.values() else None

    def _get_backend_value(self):
        value = None

        backend = self._get_backend()

        if backend:
            value = backend.get_value(self.key, self.gtype)
        if value is None:
            value = self.default
        return value

    def _get_backend_range(self):
        backend = self._get_backend()
        if backend:
            return backend.get_range(self.key, self.gtype)

    def _set_backend_value(self, value):
        backend = self._get_backend()
        if backend:
            backend.set_value(self.key, convert_by_gvariant(value, self.gtype), self.gtype)

    def _get_backend(self):
        if self.root is True:
            backend = dclient
            backend.set_backend_name(self.backend)
            backend.set_backend_params(self.params)
        else:
            backend = backend_factory.get_backend(self.backend, self.params)

        if not backend:
            print(f"Бекенд {self.backend} не зарегистрирован.")
        return backend

class Module:
    def __init__(self, module_data):
        self.name = module_data['name']
        self.weight = module_data.get('weight', 0)
        self.path = module_data.get("module_path")
        print(self.path)
        self.pages = {
            page['name']: page for page in module_data.get('pages', [])
        }
        self.sections = []
        self.system_lang_code = self.get_system_language()

    def add_section(self, section):
        self.sections.append(section)

    def get_sorted_sections(self):
        return sorted(self.sections, key=lambda s: s.weight)

    @staticmethod
    def get_system_language():
        lang, _ = locale.getdefaultlocale()
        return lang.split('_')[0] if lang else 'en'

    def get_translation(self, text, lang_code=None):
        if text.startswith('_'):
            text = text[1:]

        locales_path = os.path.join(self.path, "locale")

        if os.path.exists(locales_path):
            text = gettext.translation(
                domain='messages',
                localedir=locales_path,
                fallback=True
            ).gettext(text)
        return text


class Section:
    def __init__(self, section_data, strategy, module):
        self.name = module.get_translation(section_data['name'])
        self.weight = section_data.get('weight', 0)
        self.page = section_data.get('page')
        self.settings = [Setting(s, module) for s in section_data.get('settings', [])]
        self.strategy = strategy
        self.module = module

        self.module.add_section(self)

    def create_preferences_group(self):
        return self.strategy.create_preferences_group(self)


class SectionStrategy:
    def create_preferences_group(self, section):
        raise NotImplementedError("Метод create_preferences_group должен быть реализован")


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

    def create_section(self, section_data, module):
        section_type = section_data.get('type', 'classic')

        strategy = self.strategies.get(section_type)
        if not strategy:
            raise ValueError(f"Неизвестный тип секции: {section_type}")
        return Section(section_data, strategy, module)


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

def init_settings_stack(stack, listbox, split_view):
    yaml_data = load_modules()
    section_factory = SectionFactory()
    modules_dict = {}
    pages_dict = {}

    if stack.get_pages():
        print("Clear pages...")
        listbox.remove_all()
        for page in stack.get_pages():
            stack.remove(page)
    else:
        print("First init...")

    for module_data in yaml_data:
        module = Module(module_data)
        modules_dict[module.name] = module

        for section_data in module_data.get('sections', []):
            page_name = module.get_translation(section_data.get('page', 'Default'))
            module_page_name = section_data.get('page', 'Default')
            print(module_page_name)

            if page_name not in pages_dict:

                page_info = (
                    module.pages.get(f"_{module_page_name}", {})
                    or module.pages.get(module_page_name, {})
                )

                page = Page(
                    name=page_name,
                    icon=page_info.get('icon'),
                )
                pages_dict[page_name] = page

            section = section_factory.create_section(section_data, module)
            pages_dict[page_name].add_section(section)

    pages = list(pages_dict.values())
    for page in pages:
        page.sort_sections()

    pages = sorted(pages, key=lambda p: p.name)

    for page in pages:
        page.create_stack_page(stack, listbox)

    if not stack:
        print("Ошибка: settings_pagestack не найден.")

    def on_row_selected(listbox, row):
        if row:
            page_id = row.props.name
            print(f"Selected page: {page_id}")

            visible_child = stack.get_child_by_name(page_id)
            if visible_child:
                stack.set_visible_child(visible_child)
                split_view.set_show_content(True)

    listbox.connect("row-selected", on_row_selected)
