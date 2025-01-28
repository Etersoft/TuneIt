import ast
import os
import subprocess

from .base import Backend


class BinaryBackend(Backend):
    def __init__(self, params=None):
        super().__init__(params)
        self.binary_path = os.path.join(
            self.params.get('module_path'),
            self.params.get('binary_path')
        )

        self.binary_name = self.params.get('binary_name')

    def _run_binary(self, command, *args):
        try:
            full_command = (
                [self.binary_path + self.binary_name, command]
                + [x for x in args if x is not None]
            )

            result = subprocess.run(full_command, capture_output=True, text=True, check=True)

            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            print(f"[ERROR] Ошибка при выполнении команды {command}: {e}")
            return None

    def get_value(self, key, gtype):
        print(f"[DEBUG] Получение значения: key={key}, gtype={gtype}")

        result = self._run_binary('get_value', key)

        if result:
            try:
                return ast.literal_eval(result)
            except (ValueError, SyntaxError) as e:
                print(f"[ERROR] Ошибка при преобразовании результата {result}: {e}")
                return result
        return None

    def get_range(self, key, gtype):
        print(f"[DEBUG] Получение диапазона: key={key}, gtype={gtype}")

        result = self._run_binary('get_range', key)

        if not result:
            print(f"[ERROR] Пустой результат или ошибка при выполнении команды get_range для ключа {key}")
            return None

        try:
            parsed_result = ast.literal_eval(result)
            return parsed_result
        except (ValueError, SyntaxError) as e:
            print(f"[ERROR] Ошибка при преобразовании результата {result} для ключа {key}: {e}")
            return None

    def set_value(self, key, value, gtype):
        print(f"[DEBUG] Установка значения: key={key}, value={value}, gtype={gtype}")

        result = self._run_binary('set_value', key, str(value))

        if result:
            try:
                return ast.literal_eval(result)
            except (ValueError, SyntaxError) as e:
                print(f"[ERROR] Ошибка при преобразовании результата {result}: {e}")
        return None
