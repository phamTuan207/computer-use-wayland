"""Plugin inventory gates use fixed fixtures; no compositor is contacted."""
import json
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import indicator
import plugin_inventory

BAR = {'name': 'hyprbars', 'author': 'Vaxry', 'handle': '55ae075ca090',
       'version': '1.0', 'description': 'Window title bars'}
GLASS = {'name': 'hyprglass', 'author': 'hyprnux', 'handle': 'aabbccddeeff',
         'version': indicator.LIQUID_VERSION, 'description': 'Liquid glass'}
GUARD = {'name': 'computer-use-cursor', 'author': 'computer-use-wayland',
         'handle': '112233445566', 'version': '1.0.0',
         'description': 'Session-owned cursor image lease'}


class PluginInventoryTests(unittest.TestCase):
    def test_setup_accepts_empty_or_exact_hyprbars(self):
        self.assertEqual(plugin_inventory.setup_baseline('[]'), [])
        identity=[{'name':'hyprbars','author':'Vaxry','version':'1.0'}]
        self.assertEqual(plugin_inventory.setup_baseline(json.dumps([BAR])), identity)
        self.assertEqual(plugin_inventory.setup_baseline(
            json.dumps([{**BAR,'handle':'559e76cc0020'}])),identity)
        self.assertEqual(plugin_inventory.setup_snapshot([BAR]),[BAR])

    def test_setup_rejects_unknown_duplicate_and_malformed_plugins(self):
        for plugins in ([{**BAR, 'author': 'other'}], [BAR, BAR],
                        [{key: value for key, value in BAR.items() if key != 'handle'}],
                        [{**BAR, 'handle': 'not-hex'}]):
            with self.subTest(plugins=plugins), self.assertRaises(RuntimeError):
                plugin_inventory.setup_baseline(plugins)

    def test_cursor_requires_accepted_glass_and_optional_hyprbars(self):
        self.assertEqual(plugin_inventory.cursor_baseline([GLASS]), [GLASS])
        self.assertEqual(plugin_inventory.cursor_baseline([GLASS, BAR]), [GLASS, BAR])
        for plugins in ([], [{**GLASS, 'version': 'old'}], [GLASS, {**BAR, 'version': '2'}],
                        [GLASS, {**BAR, 'handle': GLASS['handle']}], [GLASS, GUARD]):
            with self.subTest(plugins=plugins), self.assertRaises(RuntimeError):
                plugin_inventory.cursor_baseline(plugins)

    def test_full_snapshot_detects_handle_and_metadata_drift(self):
        with self.assertRaisesRegex(RuntimeError, 'changed'):
            plugin_inventory.assert_glass_added([BAR], [{**BAR, 'handle': 'deadbeef'}, GLASS])
        with self.assertRaisesRegex(RuntimeError, 'changed'):
            plugin_inventory.assert_guard_added([GLASS, BAR], [GLASS, {**BAR, 'version': '2'}, GUARD])

    def test_only_the_expected_cursor_guard_may_be_added(self):
        self.assertEqual(plugin_inventory.assert_guard_added([GLASS], [GLASS, GUARD]),
                         [GLASS, GUARD])
        with self.assertRaisesRegex(RuntimeError, 'accepted plugin'):
            plugin_inventory.assert_guard_added([GLASS], [GLASS, {**GUARD, 'version': '2'}])


if __name__ == '__main__':
    unittest.main()
