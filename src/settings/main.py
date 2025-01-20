from gi.repository import Adw, Gtk

from .backends import backend_factory
from .daemon_client import dclient

from .tools.yml_tools import load_modules, merge_categories_by_name
from .tools.gvariant import convert_by_gvariant
from .widgets import WidgetFactory
from .widgets.panel_row import TuneItPanelRow

from .widgets.service_dialog import ServiceNotStartedDialog

dialog_presented = False

class Setting:
    def __init__(self, setting_data):
        self.name = setting_data['name']
        self.root = setting_data.get('root', False)
        self.backend = setting_data.get('backend')
        self.params = setting_data.get('params', {})
        self.type = setting_data['type']
        self.help = setting_data.get('help', "")
        self.key = setting_data.get('key')
        self.default = setting_data.get('default')
        self.gtype = setting_data.get('gtype', [])
        self.map = setting_data.get('map')
        if self.map is None:
            self.map = self._default_map()
        self.data = setting_data.get('data', {})

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

        not_empty = False

        for section in self.sections:
            preferences_group = section.create_preferences_group()
            if preferences_group:
                pref_page.add(preferences_group)
                not_empty = True
            else:
                print(f"Секция {section.name} не создала виджетов.")

        if not_empty:
            stack_page = stack.add_child(box)
            stack_page.set_title(self.name)
            stack_page.set_name(self.name)
        else:
            print(f"the category {self.name} is empty, ignored")


def init_settings_stack(stack, listbox, split_view):
    yaml_data = load_modules()
    merged_data = merge_categories_by_name(yaml_data)
    section_factory = SectionFactory()

    if stack.get_pages():
        print("Clear pages...")
        listbox.remove_all()
        for page in stack.get_pages():
            stack.remove(page)
    else:
        print("First init...")

    categories = [Category(c, section_factory) for c in merged_data]

    for category in categories:
        category.create_stack_page(stack)
    if not stack:
        print("Ошибка: settings_pagestack не найден.")

    def populate_listbox_from_stack():
        pages = stack.get_pages()
        for i in range(pages.get_n_items()):
            page = pages.get_item(i)

            row = TuneItPanelRow()
            row.set_name(page.get_name())
            row.set_title(page.get_title())
            row.icon_name = "preferences-system"

            listbox.append(row)

    def on_row_selected(listbox, row):
        if row:
            page_id = row.get_name()
            print(f"Selected page: {page_id}")

            visible_child = stack.get_child_by_name(page_id)
            if visible_child:
                stack.set_visible_child(visible_child)
                split_view.set_show_content(True)

    listbox.connect("row-selected", on_row_selected)
    populate_listbox_from_stack()
