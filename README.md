# TI-LEX-KALI Library V1

Bibliothèque terminal en français pour Kali Linux : fond noir, menus blancs et logo carré TI-L orange foncé et EX blanc, encadré de barres. Python 3.9+ ; aucune dépendance Python externe ; images facultatives avec Chafa. Compatible également avec Termux sur Android et Windows natif (outils disponibles selon la plateforme).

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

27 outils disposent de fiches détaillées dans les 16 catégories du catalogue décrites ci-dessous. La recherche couvre les noms, commandes, catégories et descriptions, sans distinction de casse ou d'accents.

Les statuts reposent uniquement sur `shutil.which` et le `PATH` courant : « absent » signifie introuvable dans ce PATH. Cela ne prouve ni l'absence de tout paquet ni le fonctionnement de l'outil. Le catalogue détaillé est complété automatiquement par les exécutables disponibles dans le PATH. Les alias shell ne sont pas détectés. Paramètres permet d'actualiser la détection et de filtrer les outils installés. La distribution Kali est identifiée via `/etc/os-release`.

## Persistance

Favoris et paramètres : `$XDG_CONFIG_HOME/ti-lex-kali/settings.json`, sinon `~/.config/ti-lex-kali/settings.json`. Écriture atomique ; un fichier illisible produit un avertissement. Un échec d'écriture est signalé et ne modifie pas les préférences en mémoire. Pour isoler une session :

```sh
python3 main.py --config-dir /tmp/ti-lex-demo --no-color
```

Éviter plusieurs sessions modifiant simultanément les mêmes préférences : la dernière sauvegarde prévaut.

## Cadre d'utilisation

Défense, systèmes possédés et laboratoire expressément autorisé. L'application consulte le système local et le PATH ; elle n'exécute aucun outil d'audit du catalogue, n'installe rien et ne lance aucun audit réseau. Elle n'automatise ni vol de cookies/identifiants ni accès à des appareils tiers. Les commandes d'aide sont affichées comme référence, à vérifier dans la documentation propre à chaque outil.

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

Ouvrir **1 Bibliothèque des outils**, puis **17 Tous les outils installés**.
La détection parcourt les dossiers du PATH sans exécuter les outils. Les commandes
connues conservent leur catégorie et leur description ; les autres apparaissent
également dans **16 Autres outils installés**, avec leur chemin et une fiche générique.
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


## Icônes à droite dans le terminal Kali

Pour activer les images, copier-coller :

```sh
sudo apt update
sudo apt install -y chafa
cd ~/TI-LEX-Kali-Library
git pull --ff-only origin main
python3 main.py
```

Agrandir le terminal à **90 colonnes ou plus**. La liste affiche à droite l'icône
locale du premier outil de la page ; saisir `v` suivi du numéro (exemple `v2`)
pour changer l'aperçu. La fiche affiche aussi l'icône à droite de ses informations
et de son menu. Chafa convertit l'image en blocs colorés adaptés au terminal Kali.

Les images viennent des icônes déjà installées dans `/usr/share/icons`,
`/usr/share/pixmaps` et `~/.local/share/icons`, en recherchant le nom de commande
ou `kali-` suivi du nom. Ce sont des icônes locales fournies par les paquets ou
le thème : leur origine officielle n'est pas garantie. Beaucoup de commandes
n'ont pas de logo. Dans ce cas, ou si Chafa est absent, une vignette textuelle
remplace l'image. Aucun téléchargement d'image n'est effectué.

Sous 90 colonnes, en sortie redirigée ou sans couleurs, l'interface garde son
fonctionnement textuel. Chafa est le seul programme externe exécuté pour cette
fonction ; aucun outil d'audit du catalogue n'est lancé. La détection des icônes
est actualisée avec **Paramètres → Actualiser la détection du PATH**.


## Commandes expliquées en français

Dans une fiche outil, choisir **2 Commandes et guide en français**.
Les commandes complètes sont accompagnées de leur explication, à côté dans un
terminal large ou en dessous sur un petit écran. `n` / `p` changent de page,
`0` revient à la fiche. Les 27 outils du catalogue disposent d’exemples rédigés ;
les autres commandes détectées proposent la consultation du manuel local,
sans inventer leurs options.

Exemple Nmap :

```sh
nmap -sT -p 80,443 127.0.0.1
```

`-p 80,443` sélectionne ces deux ports, `-sT` utilise des connexions TCP et
`127.0.0.1` désigne votre ordinateur. Le guide distingue les commandes complètes
des fragments comme `-p`, qui nécessitent une valeur et une cible.
Sources Nmap : https://nmap.org/book/man-port-specification.html et
https://nmap.org/book/man-version-detection.html.

Les exemples ne sont jamais exécutés par l’application. Les fichiers d’exemple
sont à remplacer par vos fichiers de laboratoire ; les exemples web demandent
un serveur local existant. Vérifier les options de la version installée.


## Options de tous les outils : documentation locale

Dans chaque fiche : **3 Toutes les options documentées** affiche les options
extraites du manuel local et leur description à côté ; **4 Manuel complet**
affiche toute la page disponible, y compris les sous-commandes et exemples.
Ces vues fonctionnent pour tout outil détecté qui possède une page man.
`n` / `p` parcourent toutes les pages, sans tronquer la documentation.

Pour ajouter le lecteur et les traductions disponibles sur Kali :

```sh
sudo apt update
sudo apt install -y man-db manpages-fr
```

Les exemples rédigés du menu 2 sont en français. Les menus 3 et 4 demandent un
manuel français, avec repli sur l’original : toutes les pages et toutes les options
ne sont pas traduites. Un outil sans manuel affiche un message explicite.
L'extraction d'options dépend de la mise en forme ; utiliser le manuel complet
pour les options non extraites. Il ne s'agit pas d'une garantie d'exhaustivité
des options d'une version, ni d'une traduction automatique de tous les outils.

Seul `man` est exécuté pour lire la documentation, jamais l'outil sélectionné.
Source du fonctionnement des langues : https://man7.org/linux/man-pages/man1/man.1.html.


## Catalogue en 16 catégories

Dans **Bibliothèque** ou **Catégories**, choisir le numéro :

| Nº | Catégorie |
|---|---|
| 1 | Réseau et connexions |
| 2 | Analyse du trafic réseau |
| 3 | Wi-Fi — laboratoire autorisé |
| 4 | Sites et applications web |
| 5 | Inventaire des ports et services |
| 6 | Audit des vulnérabilités |
| 7 | Mots de passe — laboratoire autorisé |
| 8 | Forensique et preuves numériques |
| 9 | Fichiers et métadonnées |
| 10 | Analyse de logiciels malveillants |
| 11 | Système et performances |
| 12 | Journaux et surveillance |
| 13 | Développement et programmation |
| 14 | Bases de données |
| 15 | Sauvegarde et récupération |
| 16 | Autres outils installés |

**17 Tous les outils installés** donne accès à l'inventaire global.
Le compteur de chaque catégorie indique combien de ses commandes sont installées.
Les commandes reconnues par leur nom exact sont classées automatiquement, y compris
hors des 27 fiches détaillées : par exemple `iw` en Wi-Fi, `sqlite3` en bases de
données et `rsync` en sauvegarde. Les commandes inconnues restent en catégorie 16,
sans classement inventé. Une catégorie peut être vide sur votre machine.

Parcours : **catégorie → outil → fiche avec icône disponible → guide et options**.
La recherche et les favoris restent accessibles depuis le menu principal.

Les numéros de sélection des menus, catégories et outils sont en rouge foncé dans les terminaux avec couleurs ; les noms restent blancs.


## Mention LAB et identification de vos appareils

Chaque outil porte **[LAB]** dans les listes. Cela indique le cadre d’utilisation
sur vos appareils personnels ou un laboratoire expressément autorisé ; ce n’est
ni une certification de sécurité de l’outil ni une confirmation automatique de
la propriété d’une cible. Les fiches et guides rappellent ce cadre.

Sur votre propre Kali, consulter les IP et les MAC locales :

```sh
ip address show
ip link show
```

Pour un autre appareil personnel, relever l’IP et la MAC dans ses paramètres
réseau et vérifier qu’il s’agit bien de l’appareil prévu. Une adresse IP ou MAC
ne prouve pas la propriété ni l’autorisation ; les MAC peuvent être aléatoires
ou modifiées et ne traversent pas les routeurs. Aucun mécanisme de validation
de propriété ou de lancement d’audit n’est ajouté par cette mention.


## Commandes à côté de la liste des outils

Le panneau de droite présente maintenant le nom de l’outil, ses exemples de
commandes et les options extraites de son manuel, avec les descriptions.
Les images restent dans les fiches. **v2** choisit l’aperçu du deuxième outil,
**c** passe à la page de commandes suivante et **d** à la précédente.
Toutes les entrées disponibles se parcourent par pages de deux, sans supprimer
les descriptions longues. **n/p** changent la page des outils, et un numéro
ouvre la fiche. Sur un écran étroit, le panneau apparaît sous la liste.

Ce panneau rassemble les exemples rédigés et les options extraites du manuel
local ; il ne garantit pas toutes les commandes possibles d’un logiciel.
La fiche → **4 Manuel complet** reste la référence pour les sous-commandes et
options que l’extraction n’identifie pas. Les descriptions non traduites restent
dans la langue du manuel. Aucune commande affichée n’est exécutée.


## Panneau des commandes — Android et Windows

Le panneau et les touches **v + numéro**, **c/d**, **n/p** sont également
compatibles avec Termux et Windows. Agrandir la fenêtre à 90 colonnes pour
l’affichage à droite ; sinon les commandes apparaissent sous la liste.
Les exemples Linux ne deviennent pas des commandes Windows natives : ils
nécessitent Kali/WSL ou un outil compatible installé.

### Termux Android : mise à jour

```sh
pkg install -y python git mandoc
cd ~/TI-LEX-Kali-Library
git pull --ff-only origin main
python main.py
```

Les manuels réellement installés sont lus avec le lecteur de Termux. Leur
présence et leur langue dépendent des paquets. Les images restent facultatives.

### Windows PowerShell : mise à jour

Depuis le dossier parent du projet :

```powershell
cd TI-LEX-Kali-Library
git pull --ff-only origin main
py -3 main.py
```

Les guides intégrés fonctionnent sans `man`. Pour les autres outils, ajouter
un fichier d'aide UTF-8 nommé exactement comme la commande détectée, par exemple
`git.exe.txt`, dans `%APPDATA%\ti-lex-kali\manuals`. L'application affiche ce
texte dans le manuel complet et en extrait les options disponibles.
Avec `--config-dir`, utiliser le sous-dossier `manuals` de ce dossier.
Cette documentation personnalisée fonctionne aussi sur Linux et Termux, où
elle est prioritaire sur la page man. Elle n'est pas générée automatiquement.

Exemple de format :

```text
OPTIONS
  --version
      Affiche la version du programme.
  --help
      Affiche l’aide du programme.
```

Utiliser uniquement les options réellement documentées pour cet outil. La
lecture d'un fichier d'aide ne lance pas l'exécutable correspondant.


## Bleu ciel, Top 10 et favoris

L’outil affiché en aperçu avec `v` + numéro est repéré en **bleu ciel** dans la
liste. Le nom dans la fiche est également bleu ciel ; les numéros restent rouge
foncé. En mode sans couleurs, toutes les fonctions restent disponibles.

**7 Top 10 — outils de choix** ouvre une sélection fixe : Nmap, Wireshark,
tcpdump, ip, ss, curl, Lynis, file, Python et Git. Ce sont des raccourcis, pas un
classement de vos usages. Le filtre « outils installés » s’applique aussi ici.

Les favoris portent une **★ immédiatement après leur nom**, dans les listes,
le Top 10 et leur fiche. Dans la fiche, **1** ajoute ou retire le favori ; les
étoiles sont actualisées au retour dans la liste et conservées au redémarrage.


Chaque nom d’outil comporte aussi un emoji correspondant à sa catégorie
(🌐 réseau, 📶 Wi-Fi, 📄 fichiers, 🔧 développement…). Les outils non classés
utilisent **🐉**, le dragon. Ces symboles décoratifs ne sont pas des logos officiels.
Leur rendu dépend des polices emoji de votre terminal ; aucune image à télécharger.
