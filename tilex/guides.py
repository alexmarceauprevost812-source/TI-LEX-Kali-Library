"""French read-only reference examples. No command execution."""
import shlex

# Complete commands are shown separately from option fragments.
GUIDES = {
    'nmap': (
        ('nmap -sT -p 80,443 127.0.0.1', 'Examine les ports TCP 80 et 443 de votre propre ordinateur.'),
        ('nmap -sT -sV -p 80,443 127.0.0.1', 'Essaie aussi de reconnaître les services et leur version sur ces ports locaux.'),
        ('nmap -sT -p 1-1024 127.0.0.1', 'Examine la plage de ports TCP 1 à 1024 sur votre ordinateur.'),
        ('nmap --help', 'Affiche le résumé des options de Nmap.'),
        ('Option : -p 80,443', 'Choisit uniquement les ports indiqués ; -p seul est incomplet.'),
        ('Option : -p 1-1024', 'Choisit une plage de ports, de 1 à 1024 inclus.'),
        ('Option : -sT', 'Utilise des connexions TCP classiques ; ne nécessite pas root pour ce scan.'),
        ('Option : -sV', 'Envoie des sondes pour identifier les services et leurs versions.'),
        ('Cible : 127.0.0.1', 'Adresse de boucle locale : votre ordinateur, pas un appareil tiers.'),
        ('Résultat : open / closed / filtered', 'Ouvert : service accessible ; fermé : pas de service ; filtré : réponse insuffisante à cause du filtrage.'),
    ),
    'ip': (('ip address show', 'Affiche les interfaces et leurs adresses locales.'), ('ip route show', 'Affiche la table de routage locale.')),
    'ss': (('ss -tuln', 'Liste les sockets TCP/UDP en écoute ; -n affiche ports et adresses numériques.'),),
    'dig': (('dig localhost', 'Interroge le résolveur DNS configuré pour le nom localhost.'),),
    'ping': (('ping -c 4 127.0.0.1', 'Envoie quatre requêtes ICMP à votre propre ordinateur ; -c limite le nombre.'),),
    'htop': (('htop', 'Ouvre le moniteur interactif des processus ; q permet de quitter.'),),
    'systemctl': (('systemctl --no-pager --type=service --state=running', 'Liste les services actifs, sans ouvrir de pager.'),),
    'lsblk': (('lsblk -f', 'Affiche les disques, partitions et informations de systèmes de fichiers.'),),
    'journalctl': (('journalctl -n 50 --no-pager', 'Affiche les 50 dernières entrées de journal accessibles à votre utilisateur.'),),
    'curl': (('curl -I http://127.0.0.1:8000/', 'Demande les en-têtes HTTP de votre serveur local sur le port 8000 ; -I utilise HEAD.'),),
    'wget': (('wget --spider http://127.0.0.1:8000/', 'Vérifie une ressource du serveur local sans télécharger son contenu.'),),
    'nikto': (('nikto -h http://127.0.0.1:8000/', 'Audite votre serveur web de laboratoire local ; -h indique la cible. Produit des requêtes HTTP.'),),
    'wireshark': (('wireshark -r capture-labo.pcap', 'Ouvre une capture de laboratoire existante ; -r lit le fichier sans démarrer de capture.'),),
    'tshark': (('tshark -r capture-labo.pcap -c 10', 'Affiche les dix premiers paquets du fichier ; -r lit, -c limite le nombre.'),),
    'tcpdump': (('tcpdump -nn -r capture-labo.pcap -c 10', 'Lit dix paquets du fichier ; -nn évite la résolution des noms et des ports.'),),
    'lynis': (('lynis show version', 'Affiche la version de Lynis sans lancer un audit.'),),
    'clamscan': (('clamscan fichier-labo.txt', 'Analyse ce fichier local ; ne demande ni suppression ni déplacement.'),),
    'john': (('john --list=formats', 'Liste les formats de hachages pris en charge par John Jumbo ; ne lance pas de récupération de mot de passe.'),),
    'hashcat': (('hashcat --help', 'Affiche les modes et options ; aucun audit de mot de passe n’est lancé.'),),
    'autopsy': (('man autopsy', 'Ouvre le manuel local, s’il est installé. Le lancement dépend de la version d’Autopsy.'),),
    'fls': (('fls image-labo.dd', 'Liste les entrées du système de fichiers de cette image autorisée ; une image partitionnée peut nécessiter un décalage -o.'),),
    'exiftool': (('exiftool photo-labo.jpg', 'Lit les métadonnées de la photo sans les modifier.'),),
    'file': (('file fichier-labo.txt', 'Identifie le type du fichier à partir de son contenu.'),),
    'python3': (('python3 --version', 'Affiche la version de Python.'), ('python3 -m py_compile main.py', 'Vérifie la syntaxe sans lancer main.py ; crée un cache de compilation.')),
    'git': (('git status', 'Affiche l’état du dépôt courant sans modifier les fichiers.'), ('git log -5 --oneline', 'Affiche les cinq derniers commits sous forme compacte.')),
    'gcc': (('gcc --version', 'Affiche la version du compilateur.'), ('gcc -fsyntax-only exemple.c', 'Vérifie la syntaxe du fichier C sans produire de programme.')),
    'make': (('make --help', 'Affiche l’aide. Une compilation normale dépend du Makefile du projet.'),),
}

NMAP_SOURCES = (
    'https://nmap.org/book/man-port-specification.html',
    'https://nmap.org/book/man-version-detection.html',
    'https://nmap.org/book/man-port-scanning-techniques.html',
)

def guide(command):
    if command in GUIDES:
        return GUIDES[command]
    return ((f'man -- {shlex.quote(command)}',
             'Consulte le manuel local si man et cette page sont disponibles. Aucun guide spécifique n’est encore rédigé pour cet outil.'),)

NOTES = ('LAB : utilisez ces exemples uniquement sur vos appareils ou avec une autorisation explicite.',
         'IP et MAC identifient une interface ; elles ne confirment pas la propriété ou l’autorisation.',
         'Sur Kali, ip address show affiche vos IP et ip link show affiche les MAC de vos interfaces locales.',
         'Pour un autre de vos appareils, vérifiez ses adresses dans ses paramètres réseau. Une MAC peut changer et n’est pas visible au-delà du réseau local.',
         'Référence à copier manuellement : aucune commande n’est exécutée ici.',
         'Les noms fichier-labo.txt, capture-labo.pcap, image-labo.dd et exemple.c sont à remplacer par vos fichiers existants.',
         'Les exemples réseau ciblent seulement 127.0.0.1. Un serveur local doit être démarré pour les exemples web.',
         'Les options peuvent varier selon la version et la plateforme ; vérifiez l’aide locale.')
