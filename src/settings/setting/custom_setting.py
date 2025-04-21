from gi.repository import GLib

from .base import BaseSetting
from .widgets import WidgetFactory


import threading
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
        self._async_fetch_value()

    def create_row(self):
        try:
            self.widget = WidgetFactory.create_widget(self)
            if self.widget:
                self.row = self.widget.create_row()
                return self.row
        except Exception as e:
            self.logger.error(f"Error creating row: {str(e)}")
        return None

    def _async_fetch_value(self, force=False):
        def fetch():
            try:
                new_value = self._execute_get_command()
                if force or new_value != self._current_value:
                    GLib.idle_add(self._update_current_value, new_value)
            except Exception as e:
                self.logger.error(f"Error fetching value: {str(e)}")

        if force or self._current_value is None:
            threading.Thread(target=fetch, daemon=True).start()

    def _update_current_value(self, value):
        print("aaaaaaaa" + value)
        if self._current_value != value:
            self._current_value = value
            if self.widget:
                self.widget.update_display()

    def set_value(self, value):
        def async_set():
            try:
                cmd = self._format_command(self.set_command, value)
                self._execute_command(cmd, capture_output=False)
                GLib.idle_add(self._async_fetch_value, True)
            except Exception as e:
                self.logger.error(f"Set value error: {str(e)}")

        threading.Thread(target=async_set, daemon=True).start()

    def get_range(self):
        if not self.get_range_command:
            return None

        try:
            cmd = self._format_command(self.get_range_command)
            output = subprocess.check_output(cmd, shell=True, text=True).strip()
            return ast.literal_eval(output)
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Get range command failed: {e.stderr}")
            return None

    def _execute_command(self, cmd, capture_output=True):
        def async_execute():
            with subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                shell=True,
                bufsize=1,
                universal_newlines=True
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

                while True:
                    line = p.stdout.readline()
                    if not line and p.poll() is not None:
                        break
                    if line:
                        GLib.idle_add(process_line, line)

                if capture_output:
                    GLib.idle_add(lambda: self._process_command_output(''.join(output)))

                stderr = p.stderr.read()
                if stderr:
                    GLib.idle_add(self.logger.error, f"Command error: {stderr}")

        threading.Thread(target=async_execute, daemon=True).start()

    def _process_command_output(self, output):
        self._current_value = output.strip()
        if self.widget:
            self.widget.update_display()

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
        return self._current_value

    def _get_backend_value(self, force=False):
        if force:
            self._async_fetch_value(force=True)
        return self._current_value

    def _set_backend_value(self, value):
        self.set_value(value)

    def _get_backend_range(self):
        return self.get_range()
