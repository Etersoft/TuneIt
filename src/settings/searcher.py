import os
import fnmatch

from .backends import FileBackend


class Searcher:
    def __init__(self, search_paths, exclude_paths, exclude_names, recursive):
        self.search_paths = [
            os.path.expanduser(os.path.expandvars(path))
            for path in search_paths
        ]

        self.exclude_paths = [
            os.path.expanduser(os.path.expandvars(path))
            for path in exclude_paths
        ]

        self.exclude_names = exclude_names
        self.recursive = recursive

    def is_excluded(self, path):
        abs_path = os.path.abspath(path)

        for excluded in self.exclude_paths:
            abs_excluded = os.path.abspath(excluded)
            if abs_path == abs_excluded or abs_path.startswith(abs_excluded + os.sep):
                return True

        path_parts = os.path.normpath(abs_path).split(os.sep)
        if any(part in self.exclude_names for part in path_parts):
            return True

        return False


class DirSearcher(Searcher):
    def search(self):
        result = []
        for base_path in self.search_paths:
            if not os.path.isdir(base_path) or self.is_excluded(base_path):
                continue

            if self.recursive:
                for root, dirs, _ in os.walk(base_path):
                    dirs[:] = [d for d in dirs if not self.is_excluded(os.path.join(root, d))]

                    if self.is_excluded(root):
                        continue

                    result.append(root)
            else:
                try:
                    result.extend([
                        os.path.join(base_path, d)
                        for d in os.listdir(base_path)
                        if os.path.isdir(os.path.join(base_path, d))
                           and not self.is_excluded(os.path.join(base_path, d))
                    ])
                except PermissionError:
                    pass
        return result


class FileSearcher(Searcher):
    def __init__(self, search_paths, exclude_paths, exclude_names, recursive, pattern):
        super().__init__(search_paths, exclude_paths, exclude_names, recursive)
        self.pattern = pattern

    def search(self):
        result = []
        for base_path in self.search_paths:
            if not os.path.exists(base_path):
                continue

            if self.recursive and os.path.isdir(base_path):
                for root, dirs, files in os.walk(base_path):
                    dirs[:] = [d for d in dirs if not self.is_excluded(os.path.join(root, d))]

                    if self.is_excluded(root):
                        continue

                    result.extend([
                        os.path.join(root, f)
                        for f in files
                        if fnmatch.fnmatch(f, self.pattern)
                           and not self.is_excluded(os.path.join(root, f))
                    ])
            else:
                if os.path.isfile(base_path):
                    filename = os.path.basename(base_path)
                    if fnmatch.fnmatch(filename, self.pattern) and not self.is_excluded(base_path):
                        result.append(base_path)
                else:
                    try:
                        result.extend([
                            os.path.join(base_path, f)
                            for f in os.listdir(base_path)
                            if os.path.isfile(os.path.join(base_path, f))
                               and fnmatch.fnmatch(f, self.pattern)
                               and not self.is_excluded(os.path.join(base_path, f))
                        ])
                    except PermissionError:
                        pass
        return result


class ValueInFileSearcher(Searcher):
    def __init__(self, search_paths, exclude_paths, exclude_names, recursive,
                 file_pattern, key, exclude_neighbor_files=None):
        super().__init__(search_paths, exclude_paths, exclude_names, recursive)

        self.file_pattern = file_pattern
        self.key = key
        self.exclude_neighbor_files = exclude_neighbor_files or []

    def has_exclude_neighbor(self, file_path):
        dir_path = os.path.dirname(file_path)

        return any(
            os.path.exists(os.path.join(dir_path, neighbor))
            for neighbor in self.exclude_neighbor_files
        )

    def search(self):
        result = []

        file_searcher = FileSearcher(
            self.search_paths,
            self.exclude_paths,
            self.exclude_names,
            self.recursive,
            self.file_pattern
        )

        for file_path in file_searcher.search():
            try:
                if self.exclude_neighbor_files and self.has_exclude_neighbor(file_path):
                    continue

                result.append(FileBackend(params={'file_path': file_path}).get_value(self.key, 's'))

            except Exception as e:
                print(f"Error processing {file_path}: {str(e)}")
                continue

        return result


class SearcherFactory:
    _searchers = {
        'dir': DirSearcher,
        'file': FileSearcher,
        'value_in_file': ValueInFileSearcher
    }

    @classmethod
    def create(cls, config):
        searcher_type = config['type']
        params = {
            'search_paths': config['search_paths'],
            'exclude_paths': config.get('exclude_paths', []),
            'exclude_names': config.get('exclude_names', []),
            'recursive': config.get('recursive', True)
        }

        if searcher_type == 'file':
            params['pattern'] = config['pattern']
        elif searcher_type == 'value_in_file':
            params['file_pattern'] = config['file_pattern']
            params['key'] = config['key']
            params['exclude_neighbor_files'] = config.get('exclude_neighbor_files', [])

        return cls._searchers[searcher_type](**params)
