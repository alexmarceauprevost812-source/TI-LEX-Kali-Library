"""Curated tool metadata; discovery never executes a tool."""
from dataclasses import dataclass
import shutil
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

def search(query):
    needle = normalize(query.strip())
    return [t for t in TOOLS if needle in normalize(
        f'{t.name} {t.command} {t.category} {t.description}')]
