"""Small ANSI terminal view with a plain-text fallback."""
import os
import sys
import shutil
import textwrap
import re

ORANGE = '\033[38;2;210;105;30m'
WHITE = '\033[97m'
SKY_BLUE = '\033[38;2;135;206;235m'
DARK_RED = '\033[38;2;180;35;35m'
BAR = '=' * 48
LOGO_ROWS = (
    ('███████ ██       ██     ', '███████ ██   ██'),
    ('   ██   ██       ██     ', '██       ██ ██ '),
    ('   ██   ██ █████ ██     ', '█████     ███  '),
    ('   ██   ██       ██     ', '██       ██ ██ '),
    ('   ██   ██       ███████', '███████ ██   ██'),
)

def logo(colored=False, compact=False):
    orange, white = (ORANGE, WHITE) if colored else ('', '')
    if compact:
        return f'{white}| {orange}TI-L{white}EX | TI-LEX-KALI / LIBRARY V1 |'
    lines = [white + BAR]
    for left, right in LOGO_ROWS:
        lines.append(f'{white}|  {orange}{left} {white}{right}    |')
    lines.append(f'{white}|            {orange}TI-L{white}EX-KALI · LIBRARY V1           |')
    lines.append(white + BAR)
    return '\n'.join(lines)

LOGO = logo()

class View:
    def __init__(self, store):
        self.store = store

    @property
    def color(self):
        return self.store.data['color'] and sys.stdout.isatty() and 'NO_COLOR' not in os.environ and os.environ.get('TERM') != 'dumb' and (os.name != 'nt' or 'WT_SESSION' in os.environ)

    def header(self, breadcrumb):
        if self.color:
            print('\033[0m\033[2J\033[H\033[97m\033[40m', end='')
        compact = sys.stdout.isatty() and shutil.get_terminal_size(fallback=(80, 24)).columns < 48
        print(logo(self.color, compact))
        print(breadcrumb)
        print('─' * 60)

    def numbered(self, line, selected=False):
        if self.color:
            body_color = SKY_BLUE if selected else WHITE
            colored = re.sub(r'^(\s*)(\d+)(?=\s)',
                          lambda match: match[1] + DARK_RED + match[2] + body_color,
                          line, count=1)
            return body_color + colored + WHITE
        return line

    def columns(self, left, right=(), show_below=False, selected_index=None):
        width = shutil.get_terminal_size(fallback=(80, 24)).columns
        if not sys.stdout.isatty() or width < 90 or not right:
            for index, line in enumerate(left):
                print(self.numbered(line, index == selected_index))
            if show_below and right:
                print('\nCOMMANDES DE L’OUTIL APERÇU')
                for line in right:
                    print(line)
            return
        left_width = width - 30
        rows = []
        for index, line in enumerate(left):
            rows.extend((part, index == selected_index) for part in (textwrap.wrap(line, width=left_width, replace_whitespace=False) or ['']))
        for index in range(max(len(rows), len(right))):
            text, selected = rows[index] if index < len(rows) else ('', False)
            image = right[index] if index < len(right) else ''
            # Chafa emits color codes; count only visible characters and cap width.
            count = 0
            clipped = ''
            for part in re.findall(r'\x1b\[[0-9;]*m|[^\x1b]', image):
                if part.startswith('\x1b'):
                    clipped += part
                elif count < 26:
                    clipped += part
                    count += 1
            reset = WHITE + '\033[40m' if self.color else ''
            print(self.numbered(text.ljust(left_width), selected) + '  | ' + clipped + reset)

    def guide_table(self, examples):
        width = shutil.get_terminal_size(fallback=(80, 24)).columns
        if width < 80:
            for command, explanation in examples:
                print(command)
                print('  → ' + explanation)
            return
        command_width = min(48, max(30, width // 2 - 3))
        explanation_width = max(20, width - command_width - 3)
        print('COMMANDE / OPTION'.ljust(command_width) + ' | EXPLICATION EN FRANÇAIS')
        for command, explanation in examples:
            left = textwrap.wrap(command, width=command_width) or ['']
            right = textwrap.wrap(explanation, width=explanation_width) or ['']
            for index in range(max(len(left), len(right))):
                print((left[index] if index < len(left) else '').ljust(command_width)
                      + ' | ' + (right[index] if index < len(right) else ''))
            print('')

    def ask(self, prompt='Choix'):
        return input(f'TI-LEX-KALI > {prompt} : ').strip()

    def pause(self):
        self.ask('Entrée pour revenir')

    def reset(self):
        if sys.stdout.isatty():
            print('\033[0m', end='', flush=True)
