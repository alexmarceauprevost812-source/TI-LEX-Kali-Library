"""Local installed icons; optional Chafa rendering, never network downloads."""
from functools import lru_cache
import os
from pathlib import Path
import re
import shutil
import subprocess

ALIASES = {'python3': ('python', 'python3'), 'tshark': ('wireshark',),
           'clamscan': ('clamav',), 'fls': ('sleuthkit',), 'gcc': ('gcc', 'c')}
SUFFIXES = ('.png', '.svg', '.xpm', '.jpg', '.jpeg', '.webp')

@lru_cache(maxsize=1)
def icon_index():
    roots = [Path('/usr/share/icons'), Path('/usr/share/pixmaps'),
             Path.home() / '.local/share/icons']
    index = {}
    for root in roots:
        if not root.is_dir():
            continue
        for directory, _, files in os.walk(root):
            for name in sorted(files):
                path = Path(directory) / name
                if path.suffix.lower() in SUFFIXES:
                    index.setdefault(path.stem.casefold(), path)
    return index

@lru_cache(maxsize=512)
def find_icon(command):
    index = icon_index()
    names = (command.casefold(),) + ALIASES.get(command.casefold(), ())
    for name in names:
        for candidate in ('kali-' + name, name):
            if candidate in index:
                return index[candidate]
    return None

@lru_cache(maxsize=128)
def render_icon(path):
    renderer = shutil.which('chafa')
    if not renderer:
        return ()
    try:
        result = subprocess.run(
            [renderer, '--format=symbols', '--symbols=block', '--size=24x10',
             '--colors=full', '--animate=off', '--', str(path)],
            capture_output=True, text=True, timeout=3, check=True)
        # Only retain SGR color escapes; discard cursor movement and OSC sequences.
        rows = []
        for line in result.stdout.splitlines()[:10]:
            line = re.sub(r'\x1b\][^\x07]*(?:\x07|\x1b\\)', '', line)
            line = re.sub(r'\x1b\[(?![0-9;]*m)[0-?]*[ -/]*[@-~]', '', line)
            rows.append(line)
        return tuple(rows)
    except (OSError, subprocess.SubprocessError, UnicodeError):
        return ()

def panel(tool, colored):
    path = find_icon(tool.command)
    rendered = render_icon(path) if colored and path else ()
    title = tool.name[:24]
    if rendered:
        return [title, *rendered, 'Icône installée sur Kali']
    label = tool.command[:20].center(22)
    return [title, '+----------------------+', '|                      |',
            '|' + label + '|', '|                      |', '+----------------------+',
            'Icône locale indisponible' if not path else 'Image : installer chafa']

def refresh():
    icon_index.cache_clear()
    find_icon.cache_clear()
    render_icon.cache_clear()
