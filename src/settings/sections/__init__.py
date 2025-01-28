from ..setting.setting import Setting

from .base_strategy import SectionStrategy
from .classic import ClassicSectionStrategy


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
