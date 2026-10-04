"""Curated tool metadata; discovery never executes a tool."""
from dataclasses import dataclass
import shutil
import os
import unicodedata

@dataclass(frozen=True)
class Tool:
    name: str
    category: str
    command: str
    description: str
    help_args: str = '--help'

CATEGORIES = ('Réseau', 'Système', 'Web', 'Analyse réseau', 'Audit sécurité',
              'Audit de mots de passe de laboratoire', 'Forensique', 'Développement')
_DATA = (
    ('ip', 0, 'ip', 'Interfaces, adresses et routes locales.'),
    ('ss', 0, 'ss', 'Sockets et connexions locales.'),
    ('dig', 0, 'dig', 'Diagnostic des résolutions DNS.'),
    ('ping', 0, 'ping', 'Vérification de connectivité autorisée.'),
    ('htop', 1, 'htop', 'Surveillance interactive des processus.'),
    ('systemctl', 1, 'systemctl', 'Inspection et gestion des services locaux.'),
    ('lsblk', 1, 'lsblk', 'Inventaire des périphériques bloc.'),
    ('journalctl', 1, 'journalctl', 'Consultation des journaux système.'),
    ('curl', 2, 'curl', 'Diagnostic HTTP et transferts explicites.'),
    ('wget', 2, 'wget', 'Téléchargement de ressources autorisées.'),
    ('Nikto', 2, 'nikto', 'Audit de configuration web en laboratoire.'),
    ('Wireshark', 3, 'wireshark', 'Analyse graphique de captures autorisées.'),
    ('TShark', 3, 'tshark', 'Analyse de captures réseau en terminal.'),
    ('tcpdump', 3, 'tcpdump', 'Capture réseau sur interfaces autorisées.'),
    ('Nmap', 4, 'nmap', 'Inventaire et audit de services sur périmètre autorisé.'),
    ('Lynis', 4, 'lynis', 'Audit de durcissement du système local.'),
    ('ClamAV', 4, 'clamscan', 'Analyse antivirus de fichiers locaux.'),
    ('John the Ripper', 5, 'john', 'Évaluation de hachages de test appartenant au laboratoire.'),
    ('Hashcat', 5, 'hashcat', 'Évaluation hors ligne de mots de passe de laboratoire.'),
    ('Autopsy', 6, 'autopsy', 'Examen forensique de supports autorisés.'),
    ('Sleuth Kit — fls', 6, 'fls', 'Liste les fichiers dans une image forensique.'),
    ('ExifTool', 6, 'exiftool', 'Inspection de métadonnées de fichiers.'),
    ('file', 6, 'file', 'Identification du type de fichier.'),
    ('Python', 7, 'python3', 'Interpréteur Python.'),
    ('Git', 7, 'git', 'Gestion de versions.'),
    ('GCC', 7, 'gcc', 'Compilation C et C++.'),
    ('Make', 7, 'make', 'Orchestration de constructions locales.'),
)
TOOLS = tuple(Tool(name, CATEGORIES[cat], cmd, desc) for name, cat, cmd, desc in _DATA)

def discover():
    return {tool.command: shutil.which(tool.command) for tool in TOOLS}

def normalize(value):
    return ''.join(c for c in unicodedata.normalize('NFKD', value.casefold())
                   if not unicodedata.combining(c))

def search(query, tools=TOOLS):
    needle = normalize(query.strip())
    return [t for t in tools if needle in normalize(
        f'{t.name} {t.command} {t.category} {t.description}')]


INSTALLED_CATEGORY = 'Autres outils installés'

def installed_catalog():
    """Enumerate executable PATH entries without running any command.

    Known tools retain curated descriptions. Unknown executables get explicit
    generic metadata rather than guessed security categories or help flags.
    """
    known = {tool.command: tool for tool in TOOLS}
    paths = discover()
    extensions = {ext.lower() for ext in os.environ.get(
        'PATHEXT', '.COM;.EXE;.BAT;.CMD').split(';') if ext}
    for directory in os.get_exec_path():
        try:
            with os.scandir(directory or os.curdir) as entries:
                for entry in entries:
                    try:
                        if not entry.is_file() or not os.access(entry.path, os.X_OK):
                            continue
                        name = entry.name
                        if os.name == 'nt' and os.path.splitext(name)[1].lower() not in extensions:
                            continue
                        # which supplies the effective PATH priority and platform rules.
                        resolved = shutil.which(name)
                        if resolved:
                            paths.setdefault(name, resolved)
                    except OSError:
                        continue
        except OSError:
            continue
    additional = [Tool(name, INSTALLED_CATEGORY, name,
                       'Exécutable détecté dans le PATH local. Description non renseignée.', '')
                  for name in paths if paths[name] and name not in known]
    tools = tuple(TOOLS) + tuple(sorted(additional, key=lambda t: t.name.casefold()))
    return tools, paths
