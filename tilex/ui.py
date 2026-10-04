"""Small ANSI terminal view with a plain-text fallback."""
import os
import sys
import shutil

LOGO = '''================================================
|  ███████ ██       ██      ███████ ██   ██    |
|     ██   ██       ██      ██       ██ ██     |
|     ██   ██ █████ ██      █████     ███      |
|     ██   ██       ██      ██       ██ ██     |
|     ██   ██       ███████ ███████ ██   ██    |
|            TI-LEX-KALI · LIBRARY V1           |
================================================'''

class View:
    def __init__(self, store):
        self.store = store

    @property
    def color(self):
        return self.store.data['color'] and sys.stdout.isatty() and 'NO_COLOR' not in os.environ and os.environ.get('TERM') != 'dumb' and (os.name != 'nt' or 'WT_SESSION' in os.environ)

    def header(self, breadcrumb):
        if self.color:
            print('\033[0m\033[2J\033[H\033[97m\033[40m', end='')
        if self.color:
            print('\033[91m', end='')
        print(LOGO if not sys.stdout.isatty() or shutil.get_terminal_size(fallback=(80, 24)).columns >= 48 else '| TI-LEX | TI-LEX-KALI / LIBRARY V1 |')
        if self.color:
            print('\033[97m', end='')
        print(breadcrumb)
        print('─' * 60)

    def ask(self, prompt='Choix'):
        return input(f'TI-LEX-KALI > {prompt} : ').strip()

    def pause(self):
        self.ask('Entrée pour revenir')

    def reset(self):
        if sys.stdout.isatty():
            print('\033[0m', end='', flush=True)
