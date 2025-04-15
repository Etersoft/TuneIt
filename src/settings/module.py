import gettext
import locale
import logging
import os


class Module:
    def __init__(self, module_data):
        self.name = module_data['name']

        self.logger = logging.getLogger(f"{self.__class__.__name__}[{self.name}]")


        self.weight = module_data.get('weight', 0)
        self.path = module_data.get("module_path")
        self.logger.debug(self.path)
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
