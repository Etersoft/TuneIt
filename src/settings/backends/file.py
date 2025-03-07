import os
import re

from .base import Backend


class FileBackend(Backend):
    def __init__(self, params=None):
        super().__init__(params)
        self.file_path = os.path.expanduser(params.get('file_path'))
        self.file_path = os.path.expandvars(self.file_path)

        self.lines = []
        self.vars = {}
        self._parse_file()

    def _parse_file(self):
        if os.path.exists(self.file_path):
            with open(self.file_path, 'r') as f:
                self.lines = f.readlines()

        for line_num, line in enumerate(self.lines):
            self._parse_line(line_num, line)

    def _parse_line(self, line_num, line):
        line = line.rstrip('\n')
        parsed = {
            'raw': line,
            'active': True,
            'var_name': None,
            'value': None,
            'comment': '',
            'style': {}
        }

        if re.match(r'^\s*#', line):
            parsed['active'] = False
            line = re.sub(r'^\s*#', '', line, count=1)

        var_match = re.match(
            r'^\s*([A-Za-z_][A-Za-z0-9_]*)\s*([=])\s*(.*?)(\s*(#.*)?)$',
            line
        )

        if var_match:
            parsed['var_name'] = var_match.group(1)
            parsed['value'] = self._parse_value(var_match.group(3))
            parsed['comment'] = var_match.group(4) or ''

            value_part = var_match.group(3)
            parsed['style'] = {
                'space_before': ' ' if ' ' in var_match.group(0).split('=')[0][-1:] else '',
                'space_after': ' ' if ' ' in var_match.group(0).split('=')[1][:1] else '',

                'quote': self._detect_quote(var_match.group(3)),
                'commented': not parsed['active']
            }

            if parsed['var_name'] not in self.vars:
                self.vars[parsed['var_name']] = []
            self.vars[parsed['var_name']].append((line_num, parsed))

    @staticmethod
    def _parse_value(value_str):
        value_str = value_str.strip()

        for quote in ['"', "'"]:

            if value_str.startswith(quote) and value_str.endswith(quote):
                return value_str[1:-1]

        return value_str

    @staticmethod
    def _detect_quote(value_str):
        value_str = value_str.strip()

        if value_str.startswith('"') and value_str.endswith('"'):
            return '"'
        if value_str.startswith("'") and value_str.endswith("'"):
            return "'"

        return ''

    def _get_style_template(self):
        if not self.vars:
            return {
                'space_before': '',
                'space_after': ' ',
                'quote': '"',
                'commented': False
            }

        last_var = next(reversed(self.vars.values()))[-1][1]

        return last_var['style']

    @staticmethod
    def _build_line(key, value, style):
        quote = style['quote']
        value_str = f"{quote}{value}{quote}" if quote else str(value)

        return (
            f"{key}{style['space_before']}="
            f"{style['space_after']}{value_str}"
        )

    def _save_file(self):
        with open(self.file_path, 'w') as f:
            f.writelines(self.lines)

    def get_value(self, key, gtype):
        entries = self.vars.get(key, [])

        for entry in reversed(entries):
            return entry[1]['value']

        return None

    def set_value(self, key, value, gtype):
        entries = self.vars.get(key, [])
        style = self._get_style_template()

        key = os.path.expanduser(key)
        key = os.path.expandvars(key)

        if entries:
            line_num, last_entry = entries[-1]
            style = last_entry['style']
            line = self._build_line(key, value, style)

            self.lines[line_num] = line + '\n'

            if last_entry['style']['commented']:
                self.lines[line_num] = self.lines[line_num].lstrip('#')
        else:
            line = self._build_line(key, value, style)
            self.lines.append(line + '\n')

        self._save_file()
