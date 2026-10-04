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

    def test_icon_matching_render_failure_and_preview(self):
        from tilex import icons
        from tilex.catalog import Tool
        tool = Tool('Nmap', 'Audit sécurité', 'nmap', 'Test')
        icons.refresh()
        with patch('tilex.icons.icon_index', return_value={'kali-nmap': Path('/tmp/nmap.svg')}):
            self.assertEqual(icons.find_icon('nmap'), Path('/tmp/nmap.svg'))
        with patch('tilex.icons.shutil.which', return_value='/usr/bin/chafa'), patch('tilex.icons.subprocess.run', side_effect=subprocess.TimeoutExpired('chafa', 3)):
            self.assertEqual(icons.render_icon(Path('/tmp/nmap.svg')), ())
        with patch('tilex.icons.find_icon', return_value=None):
            self.assertIn('Icône locale indisponible', icons.panel(tool, False))
        with tempfile.TemporaryDirectory() as config:
            app = Application(Store(config))
            with patch('builtins.input', return_value='v2'), patch('sys.stdout', new_callable=io.StringIO):
                self.assertEqual(app.pick(['Nmap', 'Git'], preview=tool), 'v2')
        icons.refresh()

    def test_side_panel_layout(self):
        from tilex.ui import View
        with tempfile.TemporaryDirectory() as config:
            view = View(Store(config))
            with patch('sys.stdout', new_callable=io.StringIO) as output, patch('tilex.ui.sys.stdout.isatty', return_value=True), patch('tilex.ui.shutil.get_terminal_size', return_value=os.terminal_size((100, 40))):
                view.columns(['Menu', '0 Retour'], ['Nmap', '[image]'])
                self.assertIn('  | Nmap', output.getvalue())
                self.assertIn('  | [image]', output.getvalue())
            with patch('sys.stdout', new_callable=io.StringIO) as output:
                view.columns(['Menu'], ['Image'])
                self.assertEqual(output.getvalue(), 'Menu\n')

    def test_guides_cover_catalog_and_explain_nmap(self):
        from tilex.guides import GUIDES, guide
        self.assertEqual(set(GUIDES), {t.command for t in TOOLS})
        self.assertTrue(any('nmap -sT -p 80,443 127.0.0.1' == command for command, _ in guide('nmap')))
        self.assertIn('manuel local', guide('unknown-command')[0][1])

    def test_manual_reader_and_option_extraction(self):
        from tilex.manuals import read_manual, options_from_manual, clean
        sample = 'OPTIONS\n       -p PORTS\n              Choisit les ports.\n              Liste ou plage.\n       --help  Affiche l’aide.\nFIN\n'
        options = options_from_manual(sample)
        self.assertEqual(options[0], ('-p PORTS', 'Choisit les ports. Liste ou plage.'))
        self.assertEqual(options[1], ('--help', 'Affiche l’aide.'))
        self.assertEqual(clean('X\bX'), 'X')
        read_manual.cache_clear()
        with patch('tilex.manuals.shutil.which', return_value='/usr/bin/man'), patch('tilex.manuals.subprocess.run', return_value=subprocess.CompletedProcess([], 0, sample, '')) as run:
            text, _ = read_manual('nmap')
            self.assertEqual(text, sample)
            self.assertEqual(run.call_args.args[0][0], '/usr/bin/man')
            self.assertEqual(run.call_args.args[0][-2:], ['--', 'nmap'])
            self.assertNotIn('shell', run.call_args.kwargs)
        read_manual.cache_clear()
        with patch('tilex.manuals.shutil.which', return_value=None):
            self.assertEqual(read_manual('tool')[0], '')
        read_manual.cache_clear()

    def test_guide_and_manual_navigation(self):
        from tilex.catalog import Tool
        tool = Tool('Nmap', 'Audit sécurité', 'nmap', 'Test')
        with tempfile.TemporaryDirectory() as config:
            app = Application(Store(config))
            with patch('builtins.input', side_effect=['n', 'p', '0']), patch('sys.stdout', new_callable=io.StringIO) as output:
                app.tool_guide(tool)
                self.assertIn('Option : -p 80,443', output.getvalue())
            with patch('tilex.app.read_manual', return_value=('OPTIONS\n       -p PORTS\n              Choisit les ports.\n', 'Manuel local')), patch('builtins.input', side_effect=['n', '0']), patch('sys.stdout', new_callable=io.StringIO) as output:
                app.tool_manual(tool)
                self.assertIn('Choisit les ports.', output.getvalue())

    def test_sixteen_categories_and_explicit_classification(self):
        from tilex.catalog import CATEGORIES, category_for
        self.assertEqual(len(CATEGORIES), 16)
        self.assertEqual(len(set(CATEGORIES)), 16)
        for command, index in (('nmap', 4), ('clamscan', 9), ('journalctl', 11),
                               ('iw', 2), ('sqlite3', 13), ('rsync', 14), ('git', 12)):
            self.assertEqual(category_for(command), CATEGORIES[index])
        self.assertEqual(category_for('not-nmap-or-git'), CATEGORIES[15])
        self.assertTrue(all(tool.category in CATEGORIES for tool in TOOLS))

    def test_classified_extra_installed_tool(self):
        with tempfile.TemporaryDirectory() as folder:
            executable = Path(folder) / ('sqlite3.exe' if os.name == 'nt' else 'sqlite3')
            executable.write_text('test')
            executable.chmod(0o755)
            with patch.dict(os.environ, {'PATH': folder}):
                tools, paths = installed_catalog()
            tool = next(t for t in tools if t.command == executable.name)
            self.assertEqual(tool.category, 'Bases de données')
            self.assertEqual(paths[tool.command], str(executable))

    def test_command_sidebar_pages_preserve_entries(self):
        from tilex.sidebar import command_panel
        from tilex.catalog import Tool
        tool = Tool('Test', 'Système', 'test', 'Test')
        entries = tuple((f'test --option{i}', f'explication{i}') for i in range(7))
        with patch('tilex.sidebar.command_entries', return_value=(entries, 'Manuel local')):
            seen = []
            for page in range(4):
                rows, pages = command_panel(tool, page)
                self.assertEqual(pages, 4)
                seen.extend(rows)
            text = '\n'.join(seen)
            for command, explanation in entries:
                self.assertIn(command, text)
                self.assertIn(explanation, text)
        with tempfile.TemporaryDirectory() as config:
            app = Application(Store(config))
            with patch('tilex.app.command_panel', return_value=(['Test', 'test --help'], 1)), patch('builtins.input', return_value='c'), patch('sys.stdout', new_callable=io.StringIO) as output:
                self.assertEqual(app.pick(['Test'], preview=tool), 'c')
                self.assertIn('test --help', output.getvalue())

    def test_custom_manual_and_termux_reader(self):
        from tilex.manuals import read_manual
        read_manual.cache_clear()
        with tempfile.TemporaryDirectory() as folder:
            Path(folder, 'example.exe.txt').write_text('OPTIONS\n  --help\n      Affiche l’aide.\n', encoding='utf-8')
            text, message = read_manual('example.exe', folder)
            self.assertIn('Affiche l’aide.', text)
            self.assertIn('personnalisée', message)
            with patch.dict(os.environ, {'PREFIX': '/data/data/com.termux/files/usr'}), patch('tilex.manuals.shutil.which', return_value='/termux/man'), patch('tilex.manuals.subprocess.run', return_value=subprocess.CompletedProcess([], 0, 'MANUAL', '')) as run:
                read_manual('example', folder)
                self.assertEqual(run.call_args.args[0], ['/termux/man', 'example'])
        read_manual.cache_clear()

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
            self.assertIn('Bibliothèque → Réseau et connexions → ip', process.stdout)
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
