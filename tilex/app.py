"""Keyboard navigation; tools are never invoked by this application."""
import argparse
import shlex
from .catalog import CATEGORIES, TOOLS, installed_catalog, INSTALLED_CATEGORY, search
from .storage import Store
from .system import information
from .ui import View
from .icons import panel, refresh
from .guides import guide, NOTES, NMAP_SOURCES
from .manuals import read_manual, options_from_manual

class Application:
    def __init__(self, store):
        self.store = store
        self.view = View(store)
        self.tools, self.paths = installed_catalog()

    def save(self, operation):
        try:
            operation()
        except OSError as exc:
            print(f'Enregistrement impossible : {exc}')
            self.view.pause()

    def pick(self, items, page=0, preview=None):
        start = page * 20
        rows = [f'{i:2}  {label}' for i, label in enumerate(items[start:start + 20], start + 1)]
        self.view.columns(rows, panel(preview, self.view.color) if preview else ())
        if preview:
            print('v + numéro : aperçu à droite (exemple : v2)')
        if len(items) > 20:
            print(f'Page {page + 1}/{(len(items) + 19) // 20} — n : suivante, p : précédente')
        print(self.view.numbered(' 0  Retour'))
        choice = self.view.ask()
        if choice.startswith('v') and choice[1:].isdecimal() and 1 <= int(choice[1:]) <= len(items):
            return choice
        if choice in ('n', 'p'):
            return choice
        if choice == '0':
            return None
        if choice.isdecimal() and 1 <= int(choice) <= len(items):
            return int(choice) - 1
        print('Choix invalide.')
        self.view.pause()
        return -1

    def tool_card(self, tool):
        while True:
            self.view.header(f'Bibliothèque → {tool.category} → {tool.name}')
            path = self.paths[tool.command]
            details = [f'Nom : {tool.name}', f'Catégorie : {tool.category}',
                       f'Statut : {"Installé" if path else "Absent du PATH"}',
                       f'Chemin : {path or "—"}', f'Description : {tool.description}']
            if tool.help_args:
                details.append(f'Aide à consulter manuellement : {shlex.quote(path or tool.command)} {tool.help_args}')
            else:
                details.append('Aide : consultez la documentation ; option inconnue.')
            details.extend(['Usage : défense et laboratoire expressément autorisé.',
                            f'Favori : {"Oui" if tool.command in self.store.data["favorites"] else "Non"}',
                            '', '1  Ajouter/retirer des favoris', '2  Commandes et guide en français', '3  Toutes les options documentées', '4  Manuel complet', '0  Retour'])
            self.view.columns(details, panel(tool, self.view.color))
            choice = self.view.ask()
            if choice == '0':
                return
            if choice == '1':
                self.save(lambda: self.store.toggle_favorite(tool.command))
            elif choice == '2':
                self.tool_guide(tool)
            elif choice in ('3', '4'):
                self.tool_manual(tool, full=choice == '4')

    def tool_guide(self, tool):
        examples = guide(tool.command)
        page = 0
        while True:
            self.view.header(f'{tool.name} → Commandes et guide en français')
            if not self.paths[tool.command]:
                print('Outil absent du PATH : les exemples ne fonctionneront pas avant installation.')
            rows = examples[page * 5:page * 5 + 5]
            self.view.guide_table(rows)
            print('')
            for note in NOTES:
                print(note)
            if tool.command == 'nmap':
                print('Documentation : ' + ' | '.join(NMAP_SOURCES))
            print(f'Page {page + 1}/{(len(examples) + 4) // 5} — n : suivante, p : précédente, 0 : retour')
            choice = self.view.ask()
            if choice == '0':
                return
            if choice in ('n', 'p'):
                page = min(max(0, page + (1 if choice == 'n' else -1)), (len(examples) - 1) // 5)

    def tool_manual(self, tool, full=False):
        print('Chargement du manuel local…')
        text, message = read_manual(tool.command)
        options = options_from_manual(text)
        content = text.splitlines() if full else options
        page_size = 18 if full else 4
        page = 0
        while True:
            self.view.header(f'{tool.name} → {"Manuel complet" if full else "Options documentées"}')
            print(message)
            if not content:
                print('Aucune option extraite. Choisir 4 dans la fiche pour le manuel complet.' if text else 'Documentation manquante ; aucun outil n’a été exécuté pour deviner ses options.')
            if full:
                for line in content[page * page_size:(page + 1) * page_size]:
                    print(line)
            else:
                self.view.guide_table(content[page * page_size:(page + 1) * page_size])
                print('Options extraites du manuel : elles ne constituent pas des commandes complètes.')
                print('Extraction indicative ; le manuel complet fait référence et contient aussi les sous-commandes.')
            pages = max(1, (len(content) + page_size - 1) // page_size)
            print(f'Page {page + 1}/{pages} — n : suivante, p : précédente, 0 : retour')
            choice = self.view.ask()
            if choice == '0':
                return
            if choice in ('n', 'p'):
                page = min(max(0, page + (1 if choice == 'n' else -1)), pages - 1)

    def tool_list(self, tools, breadcrumb):
        page = 0
        preview_command = None
        while True:
            visible = [t for t in tools if not self.store.data['installed_only'] or self.paths[t.command]]
            self.view.header(breadcrumb)
            if not visible:
                print('Aucun outil dans cette vue. Vérifiez le filtre dans Paramètres.')
            labels = [f'{t.name} [{"installé" if self.paths[t.command] else "absent"}]'
                      + (' ★' if t.command in self.store.data['favorites'] else '') for t in visible]
            preview = next((t for t in visible if t.command == preview_command), visible[page * 20] if visible else None)
            selection = self.pick(labels, page, preview)
            if isinstance(selection, str) and selection.startswith('v'):
                preview_command = visible[int(selection[1:]) - 1].command
                continue
            if selection in ('n', 'p'):
                page = min(max(0, page + (1 if selection == 'n' else -1)), max(0, (len(labels) - 1) // 20))
                continue
            if selection is None:
                return
            if selection >= 0:
                self.tool_card(visible[selection])

    def categories(self, root):
        while True:
            self.view.header(f'{root} → Catégories')
            categories = CATEGORIES + ('Tous les outils installés',)
            selection = self.pick([f'{cat} ({sum(bool(self.paths[t.command]) for t in self.tools if t.category == cat)} installés)'
                                   for cat in categories[:-1]] + [f'Tous les outils installés ({sum(bool(p) for p in self.paths.values())})'])
            if selection is None:
                return
            if isinstance(selection, int) and selection >= 0:
                category = categories[selection]
                self.tool_list([t for t in self.tools if (self.paths[t.command] if category == 'Tous les outils installés' else t.category == category)], f'{root} → {category}')

    def settings(self):
        while True:
            self.view.header('Paramètres')
            print(f'Configuration : {self.store.path}')
            print(f'1  Couleurs : {self.store.data["color"]}')
            print(f'2  Afficher seulement les outils installés : {self.store.data["installed_only"]}')
            print('3  Actualiser la détection du PATH\n0  Retour')
            choice = self.view.ask()
            if choice == '0':
                return
            key = {'1': 'color', '2': 'installed_only'}.get(choice)
            if key:
                self.save(lambda: self.store.set(key, not self.store.data[key]))
            elif choice == '3':
                self.tools, self.paths = installed_catalog()
                refresh()
                read_manual.cache_clear()

    def run(self):
        try:
            if self.store.warning:
                print(self.store.warning)
                self.view.pause()
            while True:
                self.view.header('Menu principal')
                self.view.columns(['1  Bibliothèque des outils', '2  Catégories', '3  Rechercher un outil', '4  Favoris', '5  Informations système', '6  Paramètres', '0  Quitter'])
                choice = self.view.ask()
                if choice == '0':
                    break
                if choice in ('1', '2'):
                    self.categories('Bibliothèque' if choice == '1' else 'Catégories')
                elif choice == '3':
                    self.tool_list(search(self.view.ask('Recherche'), self.tools), 'Recherche → Résultats')
                elif choice == '4':
                    self.tool_list([t for t in self.tools if t.command in self.store.data['favorites']], 'Favoris')
                elif choice == '5':
                    self.view.header('Informations système')
                    for key, value in information().items():
                        print(f'{key} : {value}')
                    print(f'Outils détectés : {sum(bool(p) for p in self.paths.values())}/{len(self.tools)}')
                    self.view.pause()
                elif choice == '6':
                    self.settings()
                else:
                    print('Choix invalide.')
                    self.view.pause()
        except (EOFError, KeyboardInterrupt):
            print('\nSession terminée.')
        finally:
            self.view.reset()
        return 0

def main(argv=None):
    parser = argparse.ArgumentParser(description='TI-LEX-KALI Library : inventaire local défensif.')
    parser.add_argument('--config-dir', help='Dossier alternatif pour les préférences et favoris')
    parser.add_argument('--no-color', action='store_true', help='Désactiver les couleurs pour cette session')
    args = parser.parse_args(argv)
    store = Store(args.config_dir)
    if args.no_color:
        store.data['color'] = False
    return Application(store).run()
