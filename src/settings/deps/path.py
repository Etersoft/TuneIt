from .base import DependencyChecker


class PathChecker(DependencyChecker):
    def check(self, expected_value, is_conflict=False):
        from os import path

        file_path = path.expanduser(expected_value)
        file_path = path.expandvars(file_path)

        file_exists = path.exists(file_path)

        if isinstance(expected_value, (str, bytes)):
            expected_values = (expected_value,)
        else:
            expected_values = tuple(expected_value)

        if is_conflict:
            success = not file_exists
        else:
            success = file_exists

        return {
            'success': success,
            'actual': file_path,
            'expected': expected_values,
            'exists': file_exists
        }
