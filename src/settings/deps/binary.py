from .base import DependencyChecker


class BinaryChecker(DependencyChecker):
    def check(self, expected_value, is_conflict=False):
        from shutil import which

        binary_path = which(expected_value)

        if isinstance(expected_value, (str, bytes)):
            expected_values = (expected_value,)
        else:
            expected_values = tuple(expected_value)

        if is_conflict:
            success = binary_path is None
        else:
            success = binary_path is not None

        return {
            'success': success,
            'actual': binary_path,
            'expected': expected_values
        }
