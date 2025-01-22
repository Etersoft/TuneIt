import os

import yaml

def get_local_module_directory():
    home_directory = os.path.expanduser("~")
    return os.path.join(home_directory, ".local", "share", "tuneit", "modules")

def get_module_directory():
    return "/usr/share/tuneit/modules"

def load_modules():
    modules = []
    local_modules_directory = get_local_module_directory()
    global_modules_directory = get_module_directory()

    all_modules = set(os.listdir(global_modules_directory))

    for module_name in os.listdir(local_modules_directory):
        module_path = os.path.join(local_modules_directory, module_name)
        if os.path.isdir(module_path):
            modules += load_yaml_files_from_directory(module_path)
            all_modules.discard(module_name)

    for module_name in all_modules:
        module_path = os.path.join(global_modules_directory, module_name)
        if os.path.isdir(module_path):
            modules += load_yaml_files_from_directory(module_path)

    return modules

def load_yaml_files_from_directory(directory):
    yaml_data = []
    for file in os.listdir(directory):
        if file.endswith(".yml") or file.endswith(".yaml"):
            file_path = os.path.join(directory, file)
            with open(file_path, 'r', encoding='utf-8') as f:
                try:
                    data = yaml.safe_load(f)
                    if data:
                        for item in data:
                            item['module_path'] = directory
                        yaml_data.extend(data)
                except yaml.YAMLError as e:
                    print(f"Ошибка при чтении файла {file_path}: {e}")
    return yaml_data
