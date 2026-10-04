# TI-LEX-KALI Library V1

Bibliothèque terminal en français pour Kali Linux : fond noir, menus blancs et logo carré TI-L orange foncé et EX blanc, encadré de barres. Python 3.9+ ; aucune dépendance externe et aucune image nécessaire. Compatible également avec Termux sur Android et Windows natif (outils disponibles selon la plateforme).

## Démarrage

```sh
git clone https://github.com/alexmarceauprevost812-source/TI-LEX-Kali-Library.git
cd TI-LEX-Kali-Library
python3 main.py
# Autre point d'entrée :
python3 -m tilex
```

Aucun privilège root nécessaire. Les couleurs sont activées dans un terminal compatible ANSI et désactivées pour les sorties redirigées, `TERM=dumb`, `NO_COLOR` ou `--no-color`. Un titre compact remplace le grand logo sur les petits terminaux.

## Navigation

Menu : **1 Bibliothèque des outils**, **2 Catégories**, **3 Rechercher un outil**, **4 Favoris**, **5 Informations système**, **6 Paramètres**, **0 Quitter**.

Saisir un numéro puis Entrée ; `0` revient au niveau précédent. Bibliothèque → catégorie → liste → fiche outil. Chaque fiche présente nom, catégorie, statut, chemin détecté, description et commande d'aide à consulter manuellement. `1` dans une fiche ajoute ou retire le favori. Ctrl+C et fin d'entrée quittent proprement.

27 outils disposent de fiches détaillées dans huit catégories : réseau, système, web, analyse réseau, audit sécurité, audit de mots de passe de laboratoire, forensique et développement. La recherche couvre les noms, commandes, catégories et descriptions, sans distinction de casse ou d'accents.

Les statuts reposent uniquement sur `shutil.which` et le `PATH` courant : « absent » signifie introuvable dans ce PATH. Cela ne prouve ni l'absence de tout paquet ni le fonctionnement de l'outil. Le catalogue détaillé est complété automatiquement par les exécutables disponibles dans le PATH. Les alias shell ne sont pas détectés. Paramètres permet d'actualiser la détection et de filtrer les outils installés. La distribution Kali est identifiée via `/etc/os-release`.

## Persistance

Favoris et paramètres : `$XDG_CONFIG_HOME/ti-lex-kali/settings.json`, sinon `~/.config/ti-lex-kali/settings.json`. Écriture atomique ; un fichier illisible produit un avertissement. Un échec d'écriture est signalé et ne modifie pas les préférences en mémoire. Pour isoler une session :

```sh
python3 main.py --config-dir /tmp/ti-lex-demo --no-color
```

Éviter plusieurs sessions modifiant simultanément les mêmes préférences : la dernière sauvegarde prévaut.

## Cadre d'utilisation

Défense, systèmes possédés et laboratoire expressément autorisé. L'application consulte le système local et le PATH ; elle n'exécute aucun outil du catalogue, n'installe rien et ne lance aucun audit réseau. Elle n'automatise ni vol de cookies/identifiants ni accès à des appareils tiers. Les commandes d'aide sont affichées comme référence, à vérifier dans la documentation propre à chaque outil.

## Architecture et vérification

- `main.py`, `tilex/__main__.py` : points d'entrée.
- `tilex/catalog.py` : catalogue, recherche, détection PATH.
- `tilex/app.py`, `tilex/ui.py` : navigation et présentation ANSI/ASCII.
- `tilex/storage.py` : favoris et paramètres JSON.
- `tilex/system.py` : informations locales.
- `tests/test_app.py` : détection, recherche, stockage et parcours du terminal.

```sh
python3 -m compileall -q main.py tilex tests
python3 -m unittest discover -s tests -v
printf '0\n' | python3 main.py --no-color
```

Ces tests n'exécutent aucun outil de cybersécurité. L'identité visuelle utilise un logo TI-LEX en lettres carrées : TI-L orange foncé et EX blanc, encadré de barres en haut de l'écran, avec menus blancs sur fond noir ; aucune ressource graphique n'est requise.

## Copier-coller — Kali Linux / Debian

Installation et lancement (les deux premières commandes peuvent demander votre mot de passe) :

```sh
sudo apt update
sudo apt install -y python3 git
git clone https://github.com/alexmarceauprevost812-source/TI-LEX-Kali-Library.git
cd TI-LEX-Kali-Library
python3 main.py
```

Pour relancer après avoir fermé le terminal, depuis le dossier où vous avez cloné le dépôt :

```sh
cd TI-LEX-Kali-Library
python3 main.py
```

## Copier-coller — Android avec Termux

Utiliser Termux, puis copier-coller :

```sh
pkg update
pkg install -y python git
git clone https://github.com/alexmarceauprevost812-source/TI-LEX-Kali-Library.git
cd TI-LEX-Kali-Library
python main.py
```

Pour relancer :

```sh
cd ~/TI-LEX-Kali-Library
python main.py
```

Termux fonctionne sans root. Ce programme n'installe pas Kali sur Android : il détecte les exécutables disponibles dans Termux. Certains outils du catalogue Kali ne sont pas compatibles avec Android. Les informations système décrivent l'environnement Android/Termux et Kali est indiqué seulement si son identification est réellement présente.

## Copier-coller — Windows PowerShell

Dans PowerShell, installer Python et Git si nécessaire :

```powershell
winget install --id Python.Python.3.13 -e
winget install --id Git.Git -e
```

Fermer puis rouvrir PowerShell pour actualiser le PATH, puis copier-coller :

```powershell
git clone https://github.com/alexmarceauprevost812-source/TI-LEX-Kali-Library.git
cd TI-LEX-Kali-Library
py -3 main.py
```

Pour relancer depuis le dossier parent du dépôt :

```powershell
cd TI-LEX-Kali-Library
py -3 main.py
```

Si `py` n'est pas disponible mais Python est installé, utiliser `python main.py`. Si `winget` est absent, installer Python et Git avec leurs installateurs officiels, puis reprendre les commandes de clonage. Le mode Windows natif détecte les commandes du PATH Windows (`.exe` inclus via `shutil.which`) ; il n'installe pas les outils Linux. Pour utiliser les outils Kali sous Windows, lancer l'application dans une installation Kali sous WSL avec les commandes Linux.

Les préférences Windows utilisent `%APPDATA%\ti-lex-kali\settings.json`. Termux et Linux utilisent les chemins XDG décrits plus haut. Sous Windows, les couleurs sont activées dans Windows Terminal ; dans les consoles non identifiées comme compatibles, la présentation reste en texte simple.

## Mise à jour

Depuis le dossier du dépôt, sur chaque plateforme :

```sh
git pull --ff-only origin main
```

Puis relancer avec `python3 main.py` (Kali), `python main.py` (Termux) ou `py -3 main.py` (Windows).


## Tous les outils déjà installés

Ouvrir **1 Bibliothèque des outils**, puis **10 Tous les outils installés**.
La détection parcourt les dossiers du PATH sans exécuter les outils. Les commandes
connues conservent leur catégorie et leur description ; les autres apparaissent
également dans **9 Autres outils installés**, avec leur chemin et une fiche générique.
Toutes ces commandes sont recherchables et peuvent être ajoutées aux favoris.

Les listes affichent 20 résultats par page : saisir `n` pour la suivante, `p` pour
la précédente, le numéro de l'outil pour sa fiche ou `0` pour revenir.
Après une installation, utiliser **6 Paramètres → 3 Actualiser la détection du PATH**
ou relancer le programme.

Cette vue comprend aussi les commandes générales du système. Elle inventorie les
exécutables accessibles, pas les paquets téléchargés : un fichier non installé,
un alias shell, une application graphique hors PATH ou un programme dans un dossier
absent du PATH ne sera pas détecté. Pour les exécutables sans fiche détaillée,
l'application ne suppose pas qu'une option `--help` existe.
