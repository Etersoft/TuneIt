import os

import yaml

def get_local_share_directory():
    home_directory = os.path.expanduser("~")
    local_share_directory = os.path.join(home_directory, ".local", "share", "tuneit")
    return local_share_directory


def load_modules():
    modules = []
    local_share_directory = get_local_share_directory()
    
    modules_directory = os.path.join(local_share_directory, "modules")
    if not os.path.exists(modules_directory):
        print(f"Директория {modules_directory} не существует")
        return modules
    
    modules = load_yaml_files_from_directory(modules_directory)
    return modules

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
            categories_dict[category_name]['sections'].extend(
                category_data['sections'])

    return list(categories_dict.values())
