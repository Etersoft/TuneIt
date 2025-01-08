import os

import yaml


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
