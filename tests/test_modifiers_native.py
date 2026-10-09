"""Self-contained regression suite for native/modifiers virtual keyboard helper.

Uses an isolated TemporaryDirectory in setUpClass to generate protocol glue
and compile a temporary test binary. Never pollutes repo build artifacts or races
other test suites.
"""
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
XML = ROOT / 'native/keyboard.xml'
SRC = ROOT / 'native/modifiers.c'


class ModifiersNativeSelfContainedTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmpdir = tempfile.TemporaryDirectory()
        cls.tmppath = Path(cls.tmpdir.name)
        cls.proto_h = cls.tmppath / 'keyboard-protocol.h'
        cls.proto_c = cls.tmppath / 'keyboard-protocol.c'
        cls.binary = cls.tmppath / 'modifiers_test_bin'

        # 1. Generate client-header and private-code into temporary directory
        res_h = subprocess.run(
            ['wayland-scanner', 'client-header', str(XML), str(cls.proto_h)],
            capture_output=True, text=True
        )
        if res_h.returncode != 0:
            raise RuntimeError(f"wayland-scanner header failed:\n{res_h.stderr}")

        res_c = subprocess.run(
            ['wayland-scanner', 'private-code', str(XML), str(cls.proto_c)],
            capture_output=True, text=True
        )
        if res_c.returncode != 0:
            raise RuntimeError(f"wayland-scanner code failed:\n{res_c.stderr}")

        # 2. Strict compile into temporary directory
        cmd = [
            'cc', '-Wall', '-Wextra', '-Werror', '-O2',
            f'-I{cls.tmppath}',
            '-o', str(cls.binary),
            str(SRC), str(cls.proto_c),
            '-lwayland-client', '-lxkbcommon'
        ]
        proc = subprocess.run(cmd, capture_output=True, text=True)
        if proc.returncode != 0:
            raise RuntimeError(f"Compilation failed:\n{proc.stderr}")

    @classmethod
    def tearDownClass(cls):
        cls.tmpdir.cleanup()

    def test_01_binary_built_and_executable(self):
        """Verify the binary was built cleanly and is executable."""
        self.assertTrue(self.binary.is_file())
        self.assertTrue(os.access(self.binary, os.X_OK))

    def test_02_missing_wayland_exits_2(self):
        """When Wayland display is unavailable, process exits with code 2."""
        env = os.environ.copy()
        env['WAYLAND_DISPLAY'] = 'nonexistent_display_fixture_12345'
        proc = subprocess.run(
            [str(self.binary)],
            env=env,
            capture_output=True,
            text=True,
            timeout=5
        )
        self.assertEqual(proc.returncode, 2)
        self.assertIn('Wayland unavailable', proc.stderr)

    def test_03_protocol_xml_interfaces(self):
        """Verify XML contains the required interfaces for virtual keyboard protocol."""
        content = XML.read_text()
        self.assertIn('name="zwp_virtual_keyboard_v1"', content)
        self.assertIn('name="zwp_virtual_keyboard_manager_v1"', content)
        self.assertIn('name="keymap"', content)
        self.assertIn('name="modifiers"', content)


    def test_04_altgr_binding_is_mod5_level3(self):
        """Measured proof that AltGr (mask 128) is a real Mod5/Level3 binding.

        A Mod5 index alone does not prove AltGr works. This compiles a C probe
        against the pinned us+lv3:ralt_switch keymap and asserts that RALT carries
        ISO_Level3_Shift, that xkb_state_update_mask(128) makes Mod5 active (and
        mask 0 makes it inactive), and that every modifier index the helper uses
        matches (Shift 0, Control 2, Mod1 3, Mod4 6, Mod5 7).
        """
        probe_src = self.tmppath / 'xkb_binding_probe.c'
        probe_bin = self.tmppath / 'xkb_binding_probe'
        probe_src.write_text(r"""
#include <stdio.h>
#include <xkbcommon/xkbcommon.h>
int main(void) {
    struct xkb_context *ctx = xkb_context_new(XKB_CONTEXT_NO_FLAGS);
    if (!ctx) { printf("ctx_fail\n"); return 1; }
    struct xkb_rule_names names = {
        .rules = "evdev", .model = "pc105", .layout = "us",
        .variant = "", .options = "lv3:ralt_switch"
    };
    struct xkb_keymap *km = xkb_keymap_new_from_names(
        ctx, &names, XKB_KEYMAP_COMPILE_NO_FLAGS);
    if (!km) { printf("keymap_fail\n"); return 1; }
    const char *names_out[] = {"Shift", "Lock", "Control", "Mod1",
                               "Mod2", "Mod3", "Mod4", "Mod5"};
    for (unsigned i = 0; i < sizeof(names_out) / sizeof(names_out[0]); i++) {
        xkb_mod_index_t idx = xkb_keymap_mod_get_index(km, names_out[i]);
        printf("%s=%d\n", names_out[i], (int)idx);
    }
    xkb_keycode_t ralt = xkb_keymap_key_by_name(km, "RALT");
    printf("RALT=%u\n", (unsigned)ralt);
    int level3 = 0;
    if (ralt != XKB_KEYCODE_INVALID) {
        const xkb_keysym_t *syms = NULL;
        int n = xkb_keymap_key_get_syms_by_level(km, ralt, 0, 0, &syms);
        for (int i = 0; i < n; i++) {
            if (syms[i] == XKB_KEY_ISO_Level3_Shift) level3 = 1;
        }
    }
    printf("RALT_is_level3=%d\n", level3);
    xkb_mod_index_t m5 = xkb_keymap_mod_get_index(km, "Mod5");
    struct xkb_state *state = xkb_state_new(km);
    xkb_state_update_mask(state, 128, 0, 0, 0, 0, 0);
    printf("mask128_active=%d\n",
           xkb_state_mod_index_is_active(state, m5, XKB_STATE_MODS_EFFECTIVE));
    xkb_state_update_mask(state, 0, 0, 0, 0, 0, 0);
    printf("mask0_active=%d\n",
           xkb_state_mod_index_is_active(state, m5, XKB_STATE_MODS_EFFECTIVE));
    xkb_state_unref(state);
    xkb_keymap_unref(km);
    xkb_context_unref(ctx);
    return 0;
}
""")
        res = subprocess.run(
            ['cc', '-Wall', '-Wextra', '-Werror', '-O2', '-o', str(probe_bin),
             str(probe_src), '-lxkbcommon'],
            capture_output=True, text=True
        )
        self.assertEqual(res.returncode, 0, msg=f"probe compile failed:\n{res.stderr}")

        run = subprocess.run([str(probe_bin)], capture_output=True, text=True, timeout=5)
        self.assertEqual(run.returncode, 0, msg=f"probe run failed:\n{run.stderr}")
        out = run.stdout
        self.assertNotIn('RALT=4294967295', out, msg="RALT keycode is missing")
        for expected in ('Shift=0', 'Control=2', 'Mod1=3', 'Mod4=6', 'Mod5=7',
                         'RALT_is_level3=1', 'mask128_active=1', 'mask0_active=0'):
            self.assertIn(expected, out, msg=f"{expected} not in probe output:\n{out}")

    def test_05_allowed_mods_constant_in_source(self):
        """ALLOWED_MODS in modifiers.c must be 205 (Shift1+Ctrl4+Alt8+Super64+AltGr128)."""
        content = SRC.read_text()
        self.assertIn('ALLOWED_MODS (1U | 4U | 8U | 64U | 128U)', content,
                      msg="ALLOWED_MODS definition must include AltGr bit 128")
        # Verify the lv3:ralt_switch option is pinned in source
        self.assertIn('lv3:ralt_switch', content,
                      msg="options must contain lv3:ralt_switch for AltGr to work")
        # Verify the unsafe fallback keymap was removed
        self.assertNotIn('struct xkb_rule_names fallback', content,
                         msg="fallback keymap block must be removed after A6 fix")


if __name__ == '__main__':
    unittest.main()
