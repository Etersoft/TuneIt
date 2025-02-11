from .base import DependencyChecker


class OSReleaseChecker(DependencyChecker):
    def check(self, expected_value='Etersoft Ximper', is_conflict=False):
        from ..backends.file import FileBackend

        actual_name = FileBackend({'file_path': '/etc/os-release'}).get_value('NAME', 's')

        if isinstance(expected_value, (str, bytes)):
            expected_values = (expected_value,)
        else:
            expected_values = tuple(expected_value)

        if is_conflict:
            success = actual_name not in expected_values
        else:
            success = actual_name in expected_values

        return {
            'success': success,
            'actual': actual_name,
            'expected': expected_values
        }
