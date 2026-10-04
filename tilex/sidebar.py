"""Paginated command reference next to the tool list."""
import textwrap
from .guides import guide
from .manuals import read_manual, options_from_manual


def command_entries(command, manual_directory=None):
    text, message = read_manual(command, manual_directory)
    entries = list(guide(command))
    entries.extend(('Option : ' + option, description)
                   for option, description in options_from_manual(text))
    return tuple(entries), message


def command_panel(tool, page=0, manual_directory=None):
    entries, message = command_entries(tool.command, manual_directory)
    pages = max(1, (len(entries) + 1) // 2)
    page = min(max(0, page), pages - 1)
    rows = textwrap.wrap(tool.name + ' — COMMANDES', width=26)
    rows.append(f'Page {page + 1}/{pages}')
    for command, explanation in entries[page * 2:page * 2 + 2]:
        rows.append('')
        rows.extend(textwrap.wrap(command, width=26))
        rows.extend(textwrap.wrap('→ ' + explanation, width=26))
    rows.append('')
    rows.extend(textwrap.wrap(message, width=26))
    rows.extend(['c : commandes suivantes', 'd : commandes précédentes'])
    return rows, pages
