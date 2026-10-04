import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from tilex.catalog import TOOLS, discover, search, installed_catalog, INSTALLED_CATEGORY
from tilex.storage import Store
from tilex.system import information
from tilex.app import Application

ROOT = Path(__file__).resolve().parents[1]

class LibraryTests(unittest.TestCase):
    def test_real_path_discovery(self):
        with tempfile.TemporaryDirectory() as folder:
            executable = Path(folder) / ('git.exe' if os.name == 'nt' else 'git')
            executable.write_text('test')
            executable.chmod(0o755)
            with patch.dict(os.environ, {'PATH': folder}):
                paths = discover()
            self.assertEqual(paths['git'], str(executable))
            self.assertIsNone(paths['nmap'])

    @unittest.skipIf(os.name == 'nt', 'Unix executable fixtures')
    def test_extra_installed_tools_and_path_priority(self):
        with tempfile.TemporaryDirectory() as first, tempfile.TemporaryDirectory() as second:
            for folder in (first, second):
                executable = Path(folder) / 'local-lab-tool'
                executable.write_text('not executed')
                executable.chmod(0o755)
            (Path(first) / 'not-executable').write_text('data')
            (Path(first) / 'directory').mkdir()
            with patch.dict(os.environ, {'PATH': os.pathsep.join((first, second, '/missing-directory'))}):
                tools, paths = installed_catalog()
            matches = search('local-lab-tool', tools)
            self.assertEqual(len(matches), 1)
            self.assertEqual(matches[0].category, INSTALLED_CATEGORY)
            self.assertEqual(paths['local-lab-tool'], str(Path(first) / 'local-lab-tool'))
            self.assertNotIn('not-executable', paths)
            self.assertNotIn('directory', paths)
            with tempfile.TemporaryDirectory() as config:
                store = Store(config)
                store.toggle_favorite('local-lab-tool')
                self.assertIn(matches[0].command, Store(config).data['favorites'])

    def test_pagination(self):
        with tempfile.TemporaryDirectory() as config:
            app = Application(Store(config))
            with patch('builtins.input', return_value='n'), patch('sys.stdout', new_callable=io.StringIO) as output:
                self.assertEqual(app.pick([str(i) for i in range(45)], 1), 'n')
                self.assertIn('Page 2/3', output.getvalue())
                self.assertIn('21  20', output.getvalue())
                self.assertNotIn('41  40', output.getvalue())

    def test_search_accents_and_case(self):
        self.assertTrue(search('DEVELOPPEMENT'))
        self.assertEqual(search('john THE ripper')[0].command, 'john')
        self.assertEqual(search('nonexistent-tool-xyz'), [])

    def test_persistence_toggle_and_settings(self):
        with tempfile.TemporaryDirectory() as folder:
            store = Store(folder)
            store.toggle_favorite('git')
            store.set('installed_only', True)
            reopened = Store(folder)
            self.assertEqual(reopened.data['favorites'], ['git'])
            self.assertTrue(reopened.data['installed_only'])
            reopened.toggle_favorite('git')
            self.assertEqual(Store(folder).data['favorites'], [])

    def test_invalid_config_recovers(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'settings.json'
            for content in ('{', '[]', '{"favorites": [1]}', '{"color": "yes"}'):
                path.write_text(content)
                store = Store(folder)
                self.assertIsNotNone(store.warning)
                self.assertEqual(store.data['favorites'], [])

    def test_failed_write_keeps_state(self):
        with tempfile.TemporaryDirectory() as folder:
            store = Store(folder)
            with patch('tilex.storage.tempfile.NamedTemporaryFile', side_effect=OSError('read only')):
                with self.assertRaises(OSError):
                    store.toggle_favorite('git')
            self.assertEqual(store.data['favorites'], [])

    def test_full_navigation_and_restart(self):
        with tempfile.TemporaryDirectory() as folder:
            # Invalid selection, library/category/card/favorite, search, favorites,
            # system info, settings/filter/rescan, exit.
            sequence = '999\n\n1\n1\n1\n1\n0\n0\n0\n3\ngit\n1\n0\n0\n4\n0\n5\n\n6\n2\n3\n0\n0\n'
            process = subprocess.run([sys.executable, 'main.py', '--no-color', '--config-dir', folder],
                                     cwd=ROOT, input=sequence, capture_output=True, text=True, timeout=10)
            self.assertEqual(process.returncode, 0, process.stderr)
            self.assertIn('Bibliothèque → Réseau → ip', process.stdout)
            self.assertIn('Chemin :', process.stdout)
            self.assertIn('Kali détecté', process.stdout)
            self.assertNotIn('\033[', process.stdout)
            self.assertIn('ip', Store(folder).data['favorites'])

    def test_entrypoints_eof_and_help(self):
        with tempfile.TemporaryDirectory() as folder:
            for entry in (['main.py'], ['-m', 'tilex']):
                for input_text in ('0\n', ''):
                    result = subprocess.run([sys.executable, *entry, '--config-dir', folder],
                                            cwd=ROOT, input=input_text, capture_output=True, text=True, timeout=10)
                    self.assertEqual(result.returncode, 0, result.stderr)
                    self.assertIn('TI-LEX-KALI', result.stdout)
            result = subprocess.run([sys.executable, 'main.py', '--help'], cwd=ROOT,
                                    capture_output=True, text=True, timeout=10)
            self.assertEqual(result.returncode, 0)

    def test_interrupt_and_missing_release(self):
        with tempfile.TemporaryDirectory() as folder:
            with patch('builtins.input', side_effect=KeyboardInterrupt), patch('sys.stdout', new_callable=io.StringIO):
                self.assertEqual(Application(Store(folder)).run(), 0)
        with patch('tilex.system.Path.read_text', side_effect=FileNotFoundError):
            self.assertEqual(information()['Kali détecté'], 'Non')

if __name__ == '__main__':
    unittest.main()
