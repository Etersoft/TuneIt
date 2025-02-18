from .classic import ClassicSection

class SectionFactory:
    def __init__(self):
        self.sections = {
            'classic': ClassicSection,
        }

    def create_section(self, section_data, module):
        section_type = section_data.get('type', 'classic')

        section = self.sections.get(section_type)
        if not section:
            raise ValueError(f"Unknown type of section: {section_type}")
        return section(section_data, module)