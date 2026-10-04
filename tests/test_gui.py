"""Real Tk checks; requires a display or Xvfb."""
import tempfile
import time
import unittest
from unittest.mock import patch
try:
    import tkinter as tk
    from tilex.gui import CatalogGUI
except ImportError:
    tk = None
from tilex.catalog import TOOLS
from tilex.storage import Store

class GuiTests(unittest.TestCase):
    def setUp(self):
        if tk is None:
            self.skipTest('Tkinter unavailable')
        try:
            self.root = tk.Tk()
        except tk.TclError:
            self.skipTest('No graphical display')
        self.directory = tempfile.TemporaryDirectory()
        self.patch_catalog = patch('tilex.gui.installed_catalog', return_value=(TOOLS, {t.command: '/usr/bin/' + t.command for t in TOOLS}))
        self.patch_manual = patch('tilex.gui.read_manual', return_value=('OPTIONS\n       -p PORTS\n              Choisit les ports.\n', 'Manuel de test'))
        self.patch_catalog.start()
        self.patch_manual.start()
        self.app = CatalogGUI(self.root, Store(self.directory.name))
        self.pump(lambda: bool(self.app.tools))

    def tearDown(self):
        if not hasattr(self, 'app'):
            return
        self.app.close()
        self.patch_catalog.stop()
        self.patch_manual.stop()
        self.directory.cleanup()

    def pump(self, condition):
        deadline = time.monotonic() + 5
        while not condition() and time.monotonic() < deadline:
            self.root.update()
            time.sleep(0.02)
        self.assertTrue(condition())

    def test_search_select_copy_favorite_and_manual(self):
        self.app.query.set('nmap')
        self.assertEqual(len(self.app.filtered()), 1)
        tool = self.app.filtered()[0]
        self.app.select(tool)
        self.pump(lambda: bool(self.app.manual_text))
        self.app.copy('nmap -sT -p 80,443 127.0.0.1')
        self.root.update()
        self.assertEqual(self.root.clipboard_get(), 'nmap -sT -p 80,443 127.0.0.1')
        self.app.toggle_favorite()
        self.assertIn('nmap', Store(self.directory.name).data['favorites'])
        self.assertIn('★', self.app.detail.cget('text'))
        self.app.set_mode('Favoris ★')
        self.assertEqual([t.command for t in self.app.filtered()], ['nmap'])
        self.app.show_manual()
        self.root.update()
        windows = [w for w in self.root.winfo_children() if isinstance(w, tk.Toplevel)]
        self.assertEqual(len(windows), 1)

    def test_categories_top_ten_empty_search_and_notes(self):
        self.app.set_category('Bases de données')
        self.assertEqual(self.app.filtered(), [])
        self.app.set_mode('Top 10')
        self.assertEqual(len(self.app.filtered()), 10)
        self.app.query.set('not-a-real-command')
        self.assertEqual(self.app.filtered(), [])
        self.app.store.set('lab_notes', 'Mon appareil : 127.0.0.1')
        self.assertEqual(Store(self.directory.name).data['lab_notes'], 'Mon appareil : 127.0.0.1')
        self.app.laboratory()
        self.root.update()
        windows = [w for w in self.root.winfo_children() if isinstance(w, tk.Toplevel)]
        text = next(w for w in windows[0].winfo_children() if isinstance(w, tk.Text))
        self.assertIn('127.0.0.1', text.get('1.0', 'end'))

if __name__ == '__main__':
    unittest.main()
