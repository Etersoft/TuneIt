# window.py
#
# Copyright 2024 Etersoft
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

import yaml
import os
from gi.repository import Adw, Gtk, Gio, GLib


class Backend:
    def get_value(self, key, gtype):
        raise NotImplementedError("Метод get_value должен быть реализован")

    def set_value(self, key, value, gtype):
        raise NotImplementedError("Метод set_value должен быть реализован")


class GSettingsBackend(Backend):
    def get_value(self, key, gtype):
        schema_name, key_name = key.rsplit('.', 1)
        schema = Gio.Settings.new(schema_name)

        print(f"[DEBUG] Получение значения: schema={schema_name}, key={key_name}, gtype={gtype}")
        try:
            value = schema.get_value(key_name)
            return value.unpack()
        except Exception as e:
            print(f"[ERROR] Ошибка при получении значения {key}: {e}")
            return None

    def set_value(self, schema_key, value, gtype):
        schema_name, key_name = schema_key.rsplit('.', 1)
        schema = Gio.Settings.new(schema_name)

        print(f"[DEBUG] Установка значения: schema={schema_name}, key={key_name}, value={value}, gtype={gtype}")
        try:
            schema.set_value(key_name, GLib.Variant(gtype, value))
        except Exception as e:
            print(f"[ERROR] Ошибка при установке значения {schema_key}: {e}")

class BackendFactory:
    def __init__(self):
        self.backends = {}

    def register_backend(self, name, backend):
        self.backends[name] = backend

    def get_backend(self, name):
        return self.backends.get(name)


backend_factory = BackendFactory()
backend_factory.register_backend('gsettings', GSettingsBackend())


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
        if self.type == 'choice':
            return self._create_choice_row()
        elif self.type == 'boolean':
            return self._create_boolean_row()
        elif self.type == 'entry':
            return self._create_entry_row()
        else:
            print(f"Неизвестный тип настройки: {self.type}")
            return None

    def _create_choice_row(self):
        row = Adw.ComboRow(title=self.name, subtitle=self.help)
        row.set_model(Gtk.StringList.new(list(self.map.keys())))
        row.set_selected(self._get_selected_row_index())
        row.connect("notify::selected", self._on_choice_changed)
        return row

    def _create_boolean_row(self):
        if not self.map:
            print(f"[WARNING] Используется дефолтная карта для {self.name}")
            self.map = self._default_map()

        row = Adw.SwitchRow(title=self.name, subtitle=self.help)
        current_value = self._get_backend_value()
        print(f"[DEBUG] Текущее значение для {self.key}: {current_value}")
        row.set_active(current_value == self.map.get(True))
        row.connect("notify::active", self._on_boolean_toggled)
        return row

    def _create_entry_row(self):
        row = Adw.EntryRow(title=self.name)
        row.set_show_apply_button(True)
        row.set_text(self._get_backend_value())
        row.connect("apply", self._on_text_changed)
        return row

    def _on_choice_changed(self, combo_row, _):
        selected_value = list(self.map.values())[combo_row.get_selected()]
        self._set_backend_value(selected_value)

    def _on_boolean_toggled(self, switch, _):
        if not self.map:
            print(f"[WARNING] Карта пуста для {self.key}, используется дефолтная.")
            self.map = self._default_map()

        value = self.map.get(True) if switch.get_active() else self.map.get(False)
        if value is None:
            print(f"[ERROR] Некорректная карта для ключа {self.key}: {self.map}")
        else:
            print(f"[DEBUG] Установка значения для {self.key}: {value}")
            self._set_backend_value(value)

    def _on_text_changed(self, entry_row):
        self._set_backend_value(entry_row.get_text())

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


class Section:
    def __init__(self, section_data, strategy: SectionStrategy):
        self.name = section_data['name']
        self.weight = section_data.get('weight', 0)
        self.settings = [Setting(s) for s in section_data.get('settings', [])]
        self.strategy = strategy

    def create_preferences_group(self):
        return self.strategy.create_preferences_group(self)


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


def load_yaml_files_from_directory(directory):
    yaml_data = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".yml") or file.endswith(".yaml"):
                file_path = os.path.join(root, file)
                with open(file_path, 'r', encoding='utf-8') as f:
                    try:
                        data = yaml.safe_load(f)
                        if data:
                            yaml_data.extend(data)
                    except yaml.YAMLError as e:
                        print(f"Ошибка при чтении файла {file_path}: {e}")
    return yaml_data


def merge_categories_by_name(categories_data):
    categories_dict = {}
    for category_data in categories_data:
        category_name = category_data['name']
        if category_name not in categories_dict:
            categories_dict[category_name] = category_data
        else:
            categories_dict[category_name]['sections'].extend(category_data['sections'])

    return list(categories_dict.values())


@Gtk.Template(resource_path='/ru/ximperlinux/TuteIt/window.ui')
class TuneitWindow(Adw.ApplicationWindow):
    __gtype_name__ = 'TuneitWindow'

    main_pagestack = Gtk.Template.Child()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        yaml_files_directory = "/usr/share/ximper-tuneit/modules"  # Укажите путь к папке с YAML файлами
        yaml_data = load_yaml_files_from_directory(yaml_files_directory)

        merged_data = merge_categories_by_name(yaml_data)
        section_factory = SectionFactory()
        self.categories = [Category(c, section_factory) for c in merged_data]

        for category in self.categories:
            category.create_stack_page(self.main_pagestack)

        if not self.main_pagestack:
            print("Ошибка: main_pagestack не найден.")

