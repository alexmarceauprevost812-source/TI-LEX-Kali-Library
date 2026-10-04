"""Tk desktop catalog. All catalog commands are references, never executed."""
import argparse
from concurrent.futures import ThreadPoolExecutor
import queue
import tkinter as tk
from tkinter import messagebox
from .catalog import CATEGORIES, installed_catalog, normalize, top_ten
from .guides import guide
from .icons import find_icon, tool_emoji, refresh
from .manuals import read_manual, options_from_manual
from .storage import Store
from .system import information

BG = '#090d10'
SURFACE = '#121a20'
PANEL = '#182229'
WHITE = '#f2f5f7'
MUTED = '#a4b4c0'
ORANGE = '#d2691e'
BLUE = '#87ceeb'
RED = '#b42323'

class ScrollArea(tk.Frame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, bg=BG, **kwargs)
        self.canvas = tk.Canvas(self, bg=BG, highlightthickness=0)
        bar = tk.Scrollbar(self, command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=bar.set)
        bar.pack(side='right', fill='y')
        self.canvas.pack(side='left', fill='both', expand=True)
        self.body = tk.Frame(self.canvas, bg=BG)
        self.window = self.canvas.create_window((0, 0), window=self.body, anchor='nw')
        self.body.bind('<Configure>', lambda e: self.canvas.configure(scrollregion=self.canvas.bbox('all')))
        self.canvas.bind('<Configure>', lambda e: self.canvas.itemconfigure(self.window, width=e.width))
        self.bind('<Enter>', self._bind_wheel)
        self.bind('<Leave>', self._unbind_wheel)

    def _bind_wheel(self, event):
        self.canvas.bind_all('<MouseWheel>', self._wheel)
        self.canvas.bind_all('<Button-4>', lambda e: self.canvas.yview_scroll(-3, 'units'))
        self.canvas.bind_all('<Button-5>', lambda e: self.canvas.yview_scroll(3, 'units'))

    def _unbind_wheel(self, event):
        for sequence in ('<MouseWheel>', '<Button-4>', '<Button-5>'):
            self.canvas.unbind_all(sequence)

    def _wheel(self, event):
        self.canvas.yview_scroll(-1 if event.delta > 0 else 1, 'units')

class CatalogGUI:
    PAGE_SIZE = 24

    def __init__(self, root, store):
        self.root, self.store = root, store
        self.tools, self.paths = (), {}
        self.selected = None
        self.category = None
        self.mode = 'Bibliothèque'
        self.page = 0
        self.results = queue.Queue()
        self.executor = ThreadPoolExecutor(max_workers=2)
        self.request = 0
        self.closed = False
        root.title('TI-LEX-KALI Library V3')
        root.geometry('1440x860')
        root.minsize(1050, 680)
        root.configure(bg=BG)
        root.protocol('WM_DELETE_WINDOW', self.close)
        self.build()
        self.refresh_catalog()
        self.poll_id = root.after(80, self.poll)
        if store.warning:
            root.after(150, lambda: messagebox.showwarning('Préférences', store.warning, parent=root))

    def label(self, parent, text, fg=WHITE, size=11, **kwargs):
        return tk.Label(parent, text=text, bg=kwargs.pop('bg', BG), fg=fg,
                        font=('DejaVu Sans', size), **kwargs)

    def button(self, parent, text, action, bg=PANEL, fg=WHITE, **kwargs):
        return tk.Button(parent, text=text, command=action, bg=bg, fg=fg,
                         activebackground=BLUE, activeforeground=BG, relief='flat',
                         font=('DejaVu Sans', 10), cursor='hand2', padx=10, pady=7, **kwargs)

    def build(self):
        top = tk.Frame(self.root, bg=SURFACE, padx=15, pady=12)
        top.pack(fill='x')
        brand = tk.Frame(top, bg=SURFACE)
        brand.pack(side='left', padx=(0, 20))
        for text, color in (('TI-L', ORANGE), ('EX', WHITE)):
            self.label(brand, text, color, 25, bg=SURFACE).pack(side='left')
        self.label(brand, '  🐉  V3', ORANGE, 13, bg=SURFACE).pack(side='left')
        self.query = tk.StringVar()
        entry = tk.Entry(top, textvariable=self.query, bg=PANEL, fg=WHITE,
                         insertbackground=WHITE, relief='flat', width=25, font=('DejaVu Sans', 11))
        entry.pack(side='left', padx=10, ipady=10)
        self.query.trace_add('write', lambda *args: self.changed_filter())
        self.label(top, 'Recherche', MUTED, 9, bg=SURFACE).pack(side='left')
        for mode in ('Bibliothèque', 'Top 10', 'Favoris ★'):
            self.button(top, mode, lambda m=mode: self.set_mode(m)).pack(side='left', padx=3)
        self.button(top, 'Laboratoire', self.laboratory).pack(side='left', padx=3)
        self.button(top, 'Actualiser', self.refresh_catalog).pack(side='right')
        body = tk.Frame(self.root, bg=BG)
        body.pack(fill='both', expand=True)
        body.grid_columnconfigure(1, weight=1)
        body.grid_columnconfigure(2, weight=1)
        body.grid_rowconfigure(0, weight=1)
        sidebar = tk.Frame(body, bg=SURFACE, width=225, padx=10, pady=12)
        sidebar.grid(row=0, column=0, sticky='ns')
        self.label(sidebar, '16 CATÉGORIES', size=12, bg=SURFACE).pack(anchor='w', pady=8)
        self.category_buttons = []
        for i, category in enumerate(CATEGORIES, 1):
            row = tk.Frame(sidebar, bg=SURFACE)
            row.pack(fill='x', pady=1)
            self.label(row, f'{i:02}', RED, 10, bg=SURFACE).pack(side='left')
            short = category.split(' — ')[0]
            button = self.button(row, short, lambda c=category: self.set_category(c), bg=SURFACE, anchor='w')
            button.pack(side='left', fill='x', expand=True)
            self.category_buttons.append((category, button))
        self.button(sidebar, 'Tous les outils', lambda: self.set_category(None)).pack(fill='x', pady=8)
        self.only_installed = tk.BooleanVar(value=store_value(self.store, 'installed_only', False))
        tk.Checkbutton(sidebar, text='Installés seulement', variable=self.only_installed,
                       command=self.toggle_filter, bg=SURFACE, fg=WHITE, selectcolor=PANEL,
                       activebackground=SURFACE, activeforeground=WHITE).pack(anchor='w')
        center = tk.Frame(body, bg=BG, padx=15, pady=12)
        center.grid(row=0, column=1, sticky='nsew')
        self.heading = self.label(center, 'Vos outils', size=21)
        self.heading.pack(anchor='w')
        self.status = self.label(center, 'Chargement des outils locaux…', MUTED, 10)
        self.status.pack(anchor='w', pady=8)
        self.cards = ScrollArea(center)
        self.cards.pack(fill='both', expand=True)
        navigation = tk.Frame(center, bg=BG)
        navigation.pack(fill='x', pady=8)
        self.button(navigation, '← Précédent', lambda: self.move_page(-1)).pack(side='left')
        self.page_label = self.label(navigation, 'Page 1')
        self.page_label.pack(side='left', padx=12)
        self.button(navigation, 'Suivant →', lambda: self.move_page(1)).pack(side='right')
        right = tk.Frame(body, bg=SURFACE, padx=18, pady=18)
        right.grid(row=0, column=2, sticky='nsew')
        self.detail = self.label(right, 'Choisissez un outil', BLUE, 22, bg=SURFACE, anchor='w')
        self.detail.pack(fill='x')
        self.detail_info = self.label(right, 'Les commandes et leur guide apparaîtront ici.', MUTED, 10,
                                     bg=SURFACE, wraplength=430, justify='left', anchor='w')
        self.detail_info.pack(fill='x', pady=12)
        actions = tk.Frame(right, bg=SURFACE)
        actions.pack(fill='x', pady=6)
        self.favorite_button = self.button(actions, '☆ Favori', self.toggle_favorite)
        self.favorite_button.pack(side='left')
        self.button(actions, 'Manuel complet', self.show_manual).pack(side='left', padx=5)
        self.commands = ScrollArea(right)
        self.commands.pack(fill='both', expand=True)
        self.label(right, 'LAB — appareils personnels et laboratoires autorisés', ORANGE, 9,
                   bg=SURFACE, wraplength=430).pack(pady=(12, 0))
        self.footer = self.label(self.root, 'Aucune commande du catalogue n’est exécutée.', MUTED, 9)
        self.footer.pack(fill='x', pady=5)

    def submit(self, kind, task, token=0):
        future = self.executor.submit(task)
        def finished(result):
            try:
                value = result.result()
                self.results.put((kind, token, value, None))
            except Exception as exc:
                self.results.put((kind, token, None, str(exc)))
        future.add_done_callback(finished)

    def refresh_catalog(self):
        self.status.configure(text='Détection des outils…')
        refresh()
        read_manual.cache_clear()
        self.submit('catalog', installed_catalog)

    def poll(self):
        if self.closed:
            return
        while not self.results.empty():
            kind, token, value, error = self.results.get_nowait()
            if error:
                self.footer.configure(text='Lecture impossible : ' + error)
            elif kind == 'catalog':
                self.tools, self.paths = value
                self.page = 0
                if self.selected:
                    self.selected = next((t for t in self.tools if t.command == self.selected.command), None)
                self.render_cards()
                if self.selected:
                    self.select(self.selected)
            elif kind == 'manual' and token == self.request:
                text, message = value
                self.manual_text = text
                self.render_commands(list(guide(self.selected.command)) + [
                    ('Option : ' + option, description) for option, description in options_from_manual(text)])
                self.footer.configure(text=message)
        self.poll_id = self.root.after(80, self.poll)

    def filtered(self):
        tools = top_ten(self.tools) if self.mode == 'Top 10' else self.tools
        if self.mode == 'Favoris ★':
            tools = [t for t in tools if t.command in self.store.data['favorites']]
        return [t for t in tools if (not self.category or t.category == self.category)
                and (not self.only_installed.get() or self.paths.get(t.command))
                and normalize(self.query.get()) in normalize(f'{t.name} {t.command} {t.category} {t.description}')]

    def changed_filter(self):
        self.page = 0
        self.render_cards()

    def set_mode(self, mode):
        self.mode, self.category = mode, None
        self.changed_filter()

    def set_category(self, category):
        self.mode, self.category = 'Bibliothèque', category
        self.changed_filter()

    def toggle_filter(self):
        try:
            self.store.set('installed_only', self.only_installed.get())
        except OSError as exc:
            messagebox.showerror('Préférences', str(exc), parent=self.root)
        self.changed_filter()

    def move_page(self, delta):
        pages = max(1, (len(self.filtered()) + self.PAGE_SIZE - 1) // self.PAGE_SIZE)
        self.page = min(max(0, self.page + delta), pages - 1)
        self.render_cards()

    def render_cards(self):
        for child in self.cards.body.winfo_children():
            child.destroy()
        tools = self.filtered()
        pages = max(1, (len(tools) + self.PAGE_SIZE - 1) // self.PAGE_SIZE)
        self.page = min(self.page, pages - 1)
        self.heading.configure(text=self.category or self.mode)
        self.status.configure(text=f'{len(tools)} outils — {sum(bool(self.paths.get(t.command)) for t in tools)} installés')
        self.page_label.configure(text=f'{self.page + 1} / {pages}')
        for category, button in self.category_buttons:
            button.configure(bg=BLUE if category == self.category else SURFACE,
                             fg=BG if category == self.category else WHITE)
        for column in range(2):
            self.cards.body.grid_columnconfigure(column, weight=1)
        for index, tool in enumerate(tools[self.page * self.PAGE_SIZE:(self.page + 1) * self.PAGE_SIZE]):
            selected = self.selected and tool.command == self.selected.command
            card = tk.Frame(self.cards.body, bg=PANEL, highlightthickness=2,
                            highlightbackground=BLUE if selected else SURFACE, padx=12, pady=12)
            card.grid(row=index // 2, column=index % 2, sticky='nsew', padx=5, pady=5)
            favorite = ' ★' if tool.command in self.store.data['favorites'] else ''
            image = self.load_icon(tool)
            icon = self.label(card, tool_emoji(tool), BLUE, 24, bg=PANEL)
            if image:
                icon.configure(image=image, text='')
                icon.image = image
            icon.pack(anchor='w')
            self.label(card, tool.name + favorite, BLUE if selected else WHITE, 14, bg=PANEL,
                       wraplength=220, justify='left').pack(anchor='w', pady=5)
            self.label(card, ('Installé' if self.paths.get(tool.command) else 'Absent du PATH') + '  · LAB',
                       MUTED, 9, bg=PANEL).pack(anchor='w')
            self.label(card, tool.description, MUTED, 10, bg=PANEL, wraplength=220,
                       justify='left').pack(anchor='w', pady=8)
            self.button(card, 'Ouvrir le guide →', lambda t=tool: self.select(t)).pack(fill='x')
            card.bind('<Button-1>', lambda e, t=tool: self.select(t))
            for child in card.winfo_children():
                if not isinstance(child, tk.Button):
                    child.bind('<Button-1>', lambda e, t=tool: self.select(t))
        if not tools:
            self.label(self.cards.body, 'Aucun outil dans cette vue.', MUTED).pack(pady=20)
        self.cards.canvas.yview_moveto(0)

    def load_icon(self, tool):
        path = find_icon(tool.command)
        if not path or path.suffix.lower() not in ('.png', '.gif'):
            return None
        try:
            image = tk.PhotoImage(file=str(path))
            factor = max(1, (max(image.width(), image.height()) + 55) // 56)
            return image.subsample(factor)
        except tk.TclError:
            return None

    def select(self, tool):
        self.selected = tool
        self.request += 1
        self.manual_text = ''
        self.update_detail()
        self.render_cards()
        self.render_commands(guide(tool.command))
        self.footer.configure(text='Lecture du manuel local…')
        self.submit('manual', lambda: read_manual(tool.command, self.store.directory / 'manuals'), self.request)

    def update_detail(self):
        if not self.selected:
            return
        tool = self.selected
        star = ' ★' if tool.command in self.store.data['favorites'] else ''
        self.detail.configure(text=tool.name + star + ' ' + tool_emoji(tool))
        self.detail_info.configure(text=f'{tool.category}\n{self.paths.get(tool.command) or "Absent du PATH"}\n{tool.description}')
        self.favorite_button.configure(text='★ Retirer' if star else '☆ Favori')

    def toggle_favorite(self):
        if not self.selected:
            return
        try:
            self.store.toggle_favorite(self.selected.command)
        except OSError as exc:
            messagebox.showerror('Favoris', str(exc), parent=self.root)
        self.update_detail()
        self.render_cards()

    def render_commands(self, entries):
        for child in self.commands.body.winfo_children():
            child.destroy()
        for command, explanation in entries:
            row = tk.Frame(self.commands.body, bg=PANEL, padx=10, pady=10)
            row.pack(fill='x', pady=4)
            # Wrapping is visual only: the clipboard keeps the exact command.
            row.grid_columnconfigure(0, weight=1)
            row.grid_columnconfigure(1, weight=1)
            self.label(row, command, BLUE, 10, bg=PANEL, wraplength=190,
                       justify='left', anchor='nw').grid(row=0, column=0, sticky='nw', padx=(0, 12))
            self.label(row, explanation, WHITE, 10, bg=PANEL, wraplength=210,
                       justify='left', anchor='nw').grid(row=0, column=1, sticky='nw')
            if not command.startswith(('Option :', 'Cible :', 'Résultat :')):
                self.button(row, 'Copier', lambda c=command: self.copy(c), bg=ORANGE).grid(row=1, column=0, sticky='w', pady=(8, 0))
        self.commands.canvas.yview_moveto(0)

    def copy(self, command):
        self.root.clipboard_clear()
        self.root.clipboard_append(command)
        self.footer.configure(text='Commande copiée. Rien n’a été exécuté.')

    def show_manual(self):
        if not self.selected:
            return
        window = tk.Toplevel(self.root)
        window.title('Manuel — ' + self.selected.name)
        window.geometry('900x650')
        text = tk.Text(window, bg=BG, fg=WHITE, wrap='word', padx=15, pady=15)
        scrollbar = tk.Scrollbar(window, command=text.yview)
        text.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side='right', fill='y')
        text.pack(fill='both', expand=True)
        text.insert('1.0', self.manual_text or 'Manuel indisponible ou encore en cours de chargement.')
        text.configure(state='disabled')

    def laboratory(self):
        window = tk.Toplevel(self.root)
        window.title('Laboratoire — notes personnelles')
        window.geometry('760x560')
        window.configure(bg=BG)
        self.label(window, 'Mon laboratoire', ORANGE, 20).pack(pady=12)
        self.label(window, '\n'.join(f'{k} : {v}' for k, v in information().items()), MUTED,
                   justify='left').pack(anchor='w', padx=20)
        self.label(window, 'Notes : appareils, IP / MAC et objectifs autorisés', size=12).pack(pady=10)
        text = tk.Text(window, bg=PANEL, fg=WHITE, insertbackground=WHITE, wrap='word')
        text.pack(fill='both', expand=True, padx=20)
        text.insert('1.0', self.store.data.get('lab_notes', ''))
        def save():
            try:
                self.store.set('lab_notes', text.get('1.0', 'end-1c'))
                self.footer.configure(text='Notes du laboratoire enregistrées.')
                window.destroy()
            except OSError as exc:
                messagebox.showerror('Notes', str(exc), parent=window)
        self.button(window, 'Enregistrer les notes', save, bg=ORANGE).pack(pady=12)
        self.label(window, 'IP et MAC ne prouvent pas la propriété ou l’autorisation.', MUTED, 9).pack(pady=5)

    def close(self):
        self.closed = True
        self.root.after_cancel(self.poll_id)
        self.executor.shutdown(wait=False, cancel_futures=True)
        self.root.destroy()


def store_value(store, key, default):
    return store.data.get(key, default)


def main(argv=None):
    parser = argparse.ArgumentParser(description='TI-LEX-KALI Library V3 — interface graphique')
    parser.add_argument('--config-dir', help='Dossier des préférences, favoris, notes et manuels')
    args = parser.parse_args(argv)
    try:
        root = tk.Tk()
    except tk.TclError:
        print('Écran graphique indisponible. Lancez depuis votre bureau Kali/Windows, ou configurez Termux:X11. Le terminal reste accessible avec main.py.')
        return 1
    CatalogGUI(root, Store(args.config_dir))
    root.mainloop()
    return 0
