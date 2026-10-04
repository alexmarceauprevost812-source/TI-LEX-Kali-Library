"""Small ANSI terminal view with a plain-text fallback."""
import os
import sys
import shutil

LOGO = r'''
 _______ ___       ___     _______ __   __       ___   _ _______ ___     ___
|       |   |     |   |   |       |  |_|  |     |   | | |   _   |   |   |   |
|_     _|   |_____|   |   |    ___|       |_____|   |_| |  |_|  |   |   |   |
  |   | |   |_____|   |   |   |___|       |_____|      _|       |   |   |   |
  |   | |   |     |   |___|    ___|  ___  |     |     |_|   _   |   |___|   |
  |___| |___|     |_______|_______|__| |__|     |___| |_|__| |__|_______|___|
   ░▒▓ TI-LEX-KALI · LIBRARY V1 ▓▒░
'''

class View:
    def __init__(self, store):
        self.store = store

    @property
    def color(self):
        return self.store.data['color'] and sys.stdout.isatty() and 'NO_COLOR' not in os.environ and os.environ.get('TERM') != 'dumb' and (os.name != 'nt' or 'WT_SESSION' in os.environ)

    def header(self, breadcrumb):
        if self.color:
            print('\033[0m\033[2J\033[H\033[38;2;190;255;0m\033[40m', end='')
        print(LOGO if self.color or not sys.stdout.isatty() or shutil.get_terminal_size(fallback=(80, 24)).columns >= 80 else '\nTI-LEX-KALI / LIBRARY V1')
        print(breadcrumb)
        print('─' * 60)

    def ask(self, prompt='Choix'):
        return input(f'TI-LEX-KALI > {prompt} : ').strip()

    def pause(self):
        self.ask('Entrée pour revenir')

    def reset(self):
        if sys.stdout.isatty():
            print('\033[0m', end='', flush=True)
