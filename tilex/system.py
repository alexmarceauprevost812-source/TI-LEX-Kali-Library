"""Read-only host identification, without external commands."""
import platform
from pathlib import Path

def information():
    release = {}
    try:
        for line in Path('/etc/os-release').read_text(encoding='utf-8').splitlines():
            if '=' in line:
                key, value = line.split('=', 1)
                release[key] = value.strip('"\'')
    except OSError:
        pass
    return {
        'Distribution': release.get('PRETTY_NAME', platform.system()),
        'Kali détecté': 'Oui' if release.get('ID', '').lower() == 'kali' else 'Non',
        'Noyau': platform.release(),
        'Architecture': platform.machine(),
        'Python': platform.python_version(),
    }
