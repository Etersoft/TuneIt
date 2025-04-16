from .base import BaseSetting
from .widgets import WidgetFactory


import logging
import subprocess
import ast


class CustomSetting(BaseSetting):
    def __init__(self, setting_data, module, section):
        self.section = section

        self.get_command = setting_data.get('get_command')
        self.get_range_command = setting_data.get('get_range_command')
        self.set_command = setting_data.get('set_command')

        super().__init__(setting_data, module)

    def create_row(self):
        try:
            self.widget = WidgetFactory.create_widget(self)
            if self.widget:
                self.row = self.widget.create_row()
                return self.row
        except Exception as e:
            self.logger.error(f"Error creating row: {str(e)}")
        return None

    def get_value(self):
        if self._current_value is None:
            self._current_value = self._execute_get_command()
        return self._current_value

    def set_value(self, value):
        success = self._execute_set_command(value)
        if success:
            self._current_value = value
            self._update_widget()

    def get_range(self):
        return self._execute_get_range_command()

    def _execute_command(self, cmd, capture_output=True):
        with subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            shell=True,
            bufsize=1
        ) as p:
            output = []

            def process_line(line):
                line = line.strip()
                if not line:
                    return
                if line.startswith('CALLBACK:'):
                    self._handle_callback(line)
                elif line.startswith('NOTIFY:'):
                    self._handle_notify(line)
                elif capture_output:
                    output.append(line)

            while p.poll() is None:
                line = p.stdout.readline()
                process_line(line)

            for line in p.stdout.read().splitlines():
                process_line(line)

            stderr = p.stderr.read().strip()

        if p.returncode != 0:
            raise subprocess.CalledProcessError(p.returncode, cmd, stderr=stderr)

        return '\n'.join(output) if capture_output else ''

    def _execute_get_command(self):
        if not self.get_command:
            return self.default

        try:
            cmd = self._format_command(self.get_command)
            output = self._execute_command(cmd)
            return output
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Get command failed: {e.stderr}")
            return self.default

    def _execute_set_command(self, value):
        if not self.set_command:
            return False

        try:
            cmd = self._format_command(self.set_command, value)
            self._execute_command(cmd, capture_output=False)
            return True
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Set command failed: {e.stderr}")
            return False

    def _execute_get_range_command(self):
        if not self.get_range_command:
            return None

        try:
            cmd = self._format_command(self.get_range_command)
            output = self._execute_command(cmd)
            return ast.literal_eval(output)
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Get range command failed: {e.stderr}")
            return None

    def _format_command(self, template, value=None):
        variables = {
            'value': value,
            **self.params,
            **self.section.get_all_values()
        }
        return template.format(**variables)

    def _handle_callback(self, line):
        try:
            _, action, target, value = line.split(':', 3)
            self.section.handle_callback(
                action.strip(),
                target.strip(),
                value.strip()
            )
        except ValueError:
            self.logger.error(f"Invalid callback format: {line}")

    def _handle_notify(self, line):
        self.logger.debug("handled notify")
        try:
            parts = line.split(':', 2)
            parts += [None] * (3 - len(parts))
            _, notification, seconds = parts

            from ...main import get_main_window
            get_main_window().setting_notify(
                self.module.name,
                self._(notification),
                int(seconds) if seconds else None
            )

        except ValueError:
            self.logger.error(f"Invalid notify format: {line}")


    @property
    def current_value(self):
        return self.get_value()

    def _get_backend_value(self):
        return self.get_value()

    def _set_backend_value(self, value):
        self.set_value(value)

    def _get_backend_range(self):
        return self.get_range()
