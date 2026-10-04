"""Keyboard navigation; tools are never invoked by this application."""
import argparse
import shlex
from .catalog import CATEGORIES, TOOLS, installed_catalog, INSTALLED_CATEGORY, search
from .storage import Store
from .system import information
from .ui import View

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

    def pick(self, items, page=0):
        start = page * 20
        for i, label in enumerate(items[start:start + 20], start + 1):
            print(f'{i:2}  {label}')
        if len(items) > 20:
            print(f'Page {page + 1}/{(len(items) + 19) // 20} — n : suivante, p : précédente')
        print(' 0  Retour')
        choice = self.view.ask()
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
            print(f'Nom : {tool.name}\nCatégorie : {tool.category}')
            print(f'Statut : {"Installé" if path else "Absent du PATH"}\nChemin : {path or "—"}')
            print(f'Description : {tool.description}')
            if tool.help_args:
                print(f'Aide à consulter manuellement : {shlex.quote(path or tool.command)} {tool.help_args}')
            else:
                print('Aide : consultez la documentation de cet exécutable ; option inconnue.')
            print('Usage : défense et laboratoire expressément autorisé.')
            print(f'Favori : {"Oui" if tool.command in self.store.data["favorites"] else "Non"}')
            print('\n1  Ajouter/retirer des favoris\n0  Retour')
            choice = self.view.ask()
            if choice == '0':
                return
            if choice == '1':
                self.save(lambda: self.store.toggle_favorite(tool.command))

    def tool_list(self, tools, breadcrumb):
        page = 0
        while True:
            visible = [t for t in tools if not self.store.data['installed_only'] or self.paths[t.command]]
            self.view.header(breadcrumb)
            if not visible:
                print('Aucun outil dans cette vue. Vérifiez le filtre dans Paramètres.')
            labels = [f'{t.name} [{"installé" if self.paths[t.command] else "absent"}]'
                      + (' ★' if t.command in self.store.data['favorites'] else '') for t in visible]
            selection = self.pick(labels, page)
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
            categories = CATEGORIES + (INSTALLED_CATEGORY, 'Tous les outils installés')
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

    def run(self):
        try:
            if self.store.warning:
                print(self.store.warning)
                self.view.pause()
            while True:
                self.view.header('Menu principal')
                print('1  Bibliothèque des outils\n2  Catégories\n3  Rechercher un outil\n4  Favoris\n5  Informations système\n6  Paramètres\n0  Quitter')
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
