"""Validated, atomic per-user settings and favorites."""
import json
import os
from pathlib import Path
import tempfile

class Store:
    def __init__(self, directory=None):
        self.directory = Path(directory) if directory else Path(
            os.environ.get('XDG_CONFIG_HOME') or (os.environ.get('APPDATA') if os.name == 'nt' else None) or Path.home() / '.config') / 'ti-lex-kali'
        self.path = self.directory / 'settings.json'
        self.data = {'favorites': [], 'color': True, 'installed_only': False}
        self.warning = None
        try:
            raw = json.loads(self.path.read_text(encoding='utf-8'))
            if not isinstance(raw, dict):
                raise ValueError('Objet JSON attendu')
            favorites = raw.get('favorites', [])
            if not isinstance(favorites, list) or any(not isinstance(x, str) for x in favorites):
                raise ValueError('Favoris invalides')
            self.data['favorites'] = sorted(set(favorites))
            for key in ('color', 'installed_only'):
                if key in raw and not isinstance(raw[key], bool):
                    raise ValueError('Paramètre invalide')
                self.data[key] = raw.get(key, self.data[key])
        except FileNotFoundError:
            pass
        except (OSError, ValueError) as exc:
            self.warning = f'Configuration illisible : {exc}. Valeurs par défaut utilisées.'
            self.data = {'favorites': [], 'color': True, 'installed_only': False}

    def set(self, key, value):
        updated = dict(self.data, **{key: value})
        self.directory.mkdir(parents=True, exist_ok=True)
        temporary = None
        try:
            with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8',
                                             dir=self.directory, delete=False) as handle:
                temporary = Path(handle.name)
                json.dump(updated, handle, ensure_ascii=False, indent=2)
                handle.write('\n')
            temporary.replace(self.path)
            self.data = updated
        finally:
            if temporary is not None:
                temporary.unlink(missing_ok=True)

    def toggle_favorite(self, command):
        favorites = set(self.data['favorites'])
        if command in favorites:
            favorites.remove(command)
        else:
            favorites.add(command)
        self.set('favorites', sorted(favorites))
