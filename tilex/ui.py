"""Small ANSI terminal view with a plain-text fallback."""
import os
import sys
import shutil

ORANGE = '\033[38;2;210;105;30m'
WHITE = '\033[97m'
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

    def ask(self, prompt='Choix'):
        return input(f'TI-LEX-KALI > {prompt} : ').strip()

    def pause(self):
        self.ask('Entrée pour revenir')

    def reset(self):
        if sys.stdout.isatty():
            print('\033[0m', end='', flush=True)
