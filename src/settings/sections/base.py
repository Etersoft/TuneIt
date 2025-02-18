class BaseSection():
     def __init__(self, section_data, module):
        self.name = module.get_translation(section_data['name'])
        self.weight = section_data.get('weight', 0)
        self.page = section_data.get('page')
        