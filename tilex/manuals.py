"""Read installed man pages, never invoke catalog tools or guessed help flags."""
from functools import lru_cache
import os
import re
import shutil
import subprocess


def clean(text):
    # man may emit overstrikes for bold/underline.
    while '\b' in text:
        updated = re.sub(r'.\x08', '', text)
        if updated == text:
            break
        text = updated
    text = re.sub(r'\x1b\[[0-?]*[ -/]*[@-~]', '', text)
    return ''.join(c for c in text if c in '\n\t' or ord(c) >= 32).replace('−', '-').replace('‐', '-')

@lru_cache(maxsize=64)
def read_manual(command):
    reader = shutil.which('man')
    if not reader:
        return '', 'Lecteur man absent. Sur Kali : sudo apt install man-db manpages-fr'
    if not command or '/' in command or '\\' in command or any(ord(c) < 32 for c in command):
        return '', 'Nom de commande non pris en charge par le lecteur de manuel.'
    env = dict(os.environ, MANPAGER='cat', PAGER='cat', MANOPT='', MANWIDTH='140',
               MAN_KEEP_FORMATTING='0', GROFF_NO_SGR='1')
    try:
        result = subprocess.run([reader, '-P', 'cat', '-L', 'fr', '-S', '1:8:6', '--', command],
                                capture_output=True, text=True, errors='replace',
                                timeout=10, env=env)
    except (OSError, subprocess.SubprocessError):
        return '', 'Lecture du manuel impossible ou délai dépassé.'
    if result.returncode or not result.stdout.strip():
        return '', 'Aucun manuel local disponible pour cet outil.'
    return clean(result.stdout), 'Manuel local : français si disponible, sinon langue d’origine.'


def options_from_manual(text):
    """Best-effort extraction of option headings and following paragraphs.

    Formatting varies between man pages; full text stays available separately.
    """
    result = []
    current = None
    descriptions = []
    indent = 0
    def finish():
        if current:
            result.append((current, ' '.join(descriptions).strip() or 'Description non extraite ; consulter le manuel complet.'))
    for line in text.splitlines():
        stripped = line.strip()
        leading = len(line) - len(line.lstrip())
        if re.match(r'^--?[A-Za-z0-9?][^\n]*', stripped) and (current is None or leading <= indent):
            finish()
            parts = re.split(r'\s{2,}', stripped, maxsplit=1)
            current = parts[0]
            descriptions = parts[1:] if len(parts) > 1 else []
            indent = leading
        elif current and stripped:
            if leading > indent:
                descriptions.append(stripped)
            else:
                finish()
                current = None
                descriptions = []
    finish()
    return tuple(dict.fromkeys(result))
