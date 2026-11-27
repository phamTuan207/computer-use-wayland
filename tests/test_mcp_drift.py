"""MCP drift test (agent-desktop comparison I19 substitute).

I19 rejected generating the MCP catalog from CLI definitions; the
adopted substitute is this drift test. It statically enumerates
three surfaces and fails when they drift apart:

- scripts/cu.py: the argparse subcommands (the CLI surface).
- scripts/mcp_bridge.py: the MCP tool (computer_use_session), its
  operation enum, the request command allowlist, the image_policy
  enum, and the session spawn argv.
- scripts/session_driver.py: the relay command allowlist and its
  image_policy values.

Every cu.py subcommand must be classified below as bridge-reachable,
driver-only, lifecycle (spawn/finish plumbing), or deliberately not
exposed over MCP. A new CLI command fails this test until someone
classifies it, which is the point: adding a CLI capability must be a
conscious MCP decision, not silent drift.

Static analysis only (ast, stdlib): no imports of the modules under
test, no GUI, no processes. Hermetic by construction.

Run: python3 -m unittest tests.test_mcp_drift
"""
import ast
import unittest
from pathlib import Path

TREE_ROOT = Path(__file__).resolve().parent.parent
CU_PATH = TREE_ROOT / "scripts" / "cu.py"
BRIDGE_PATH = TREE_ROOT / "scripts" / "mcp_bridge.py"
DRIVER_PATH = TREE_ROOT / "scripts" / "session_driver.py"

# Commands the driver relay accepts but the MCP bridge deliberately
# does not forward. code-exec runs an allowlisted program; it stays
# off the MCP surface until someone decides otherwise here.
DRIVER_ONLY = {"code-exec"}

# cu.py subcommands deliberately not exposed over MCP at all:
# session lifecycle is owned by the bridge start/finish operations,
# act-now is a direct-pointer fallback lane, cli is a local registry
# browser. None of these may become bridge-reachable by accident.
NOT_EXPOSED = {"stop", "recover", "cancel", "resume", "act-now", "cli"}

# cu.py subcommands the bridge uses as plumbing, not via request:
# start spawns [CU, "session", "--", CU, "session-driver"] and
# finish sends ["finish"] through the driver.
LIFECYCLE = {"session", "session-driver", "finish"}


def _str_consts(node):
    """String constants of a List/Tuple/Set node, else None."""
    if not isinstance(node, (ast.List, ast.Tuple, ast.Set)):
        return None
    values = []
    for elt in node.elts:
        if not (isinstance(elt, ast.Constant) and isinstance(elt.value, str)):
            return None
        values.append(elt.value)
    return values


def _parse(path):
    return ast.parse(path.read_text(encoding="utf-8"), filename=str(path))


def cu_top_level_commands(tree):
    """First-arg literals of sub.add_parser(...) calls in cu.py main."""
    commands = set()
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        if (isinstance(func, ast.Attribute) and func.attr == "add_parser"
                and isinstance(func.value, ast.Name) and func.value.id == "sub"
                and node.args and isinstance(node.args[0], ast.Constant)
                and isinstance(node.args[0].value, str)):
            commands.add(node.args[0].value)
    return commands


def command_allowlists(tree):
    """Collections of string constants that look like a command allowlist.

    A command allowlist is a set/tuple/list of strings containing both
    'observe' and 'act'. Exactly one must exist per file; ambiguity is
    itself drift, so callers assert the count.
    """
    found = []
    for node in ast.walk(tree):
        values = _str_consts(node)
        if values and "observe" in values and "act" in values:
            found.append(set(values))
    return found


def schema_enum(tree, key):
    """The enum list of the inputSchema property named `key`."""
    for node in ast.walk(tree):
        if not isinstance(node, ast.Dict):
            continue
        for k, v in zip(node.keys, node.values):
            if (isinstance(k, ast.Constant) and k.value == key
                    and isinstance(v, ast.Dict)):
                for kk, vv in zip(v.keys, v.values):
                    if isinstance(kk, ast.Constant) and kk.value == "enum":
                        return _str_consts(vv)
    return None


def handled_operations(tree):
    """String literals compared against the `operation` variable."""
    ops = set()
    for node in ast.walk(tree):
        if not isinstance(node, ast.Compare):
            continue
        if not (isinstance(node.left, ast.Name) and node.left.id == "operation"):
            continue
        for comp in node.comparators:
            if isinstance(comp, ast.Constant) and isinstance(comp.value, str):
                ops.add(comp.value)
    return ops


def accepted_image_policies(tree):
    """String collections containing both 'auto' and 'always'."""
    found = []
    for node in ast.walk(tree):
        values = _str_consts(node)
        if values and set(values) == {"auto", "always"}:
            found.append(set(values))
    return found


def spawn_argv_commands(tree):
    """Command literals in the bridge Popen argv for the session driver."""
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        if not (isinstance(func, ast.Attribute) and func.attr == "Popen"):
            continue
        if not node.args:
            continue
        argv = node.args[0]
        if not isinstance(argv, ast.List):
            continue
        literals = [e.value for e in argv.elts
                    if isinstance(e, ast.Constant) and isinstance(e.value, str)]
        if "session-driver" in literals:
            return [x for x in literals if x != "--"]
    return None


def has_assignment(tree, name):
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == name:
                    return True
    return False


class McpDriftTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cu_tree = _parse(CU_PATH)
        cls.bridge_tree = _parse(BRIDGE_PATH)
        cls.driver_tree = _parse(DRIVER_PATH)
        cls.cu_commands = cu_top_level_commands(cls.cu_tree)
        bridge_lists = command_allowlists(cls.bridge_tree)
        driver_lists = command_allowlists(cls.driver_tree)
        assert len(bridge_lists) == 1, (
            "expected exactly one command allowlist in mcp_bridge.py, "
            "found %d" % len(bridge_lists))
        assert len(driver_lists) == 1, (
            "expected exactly one command allowlist in session_driver.py, "
            "found %d" % len(driver_lists))
        cls.bridge_commands = bridge_lists[0]
        cls.driver_commands = driver_lists[0]

    def test_cu_surface_found(self):
        self.assertGreaterEqual(len(self.cu_commands), 10,
                                "cu.py subcommand extraction looks broken")

    def test_bridge_commands_exist_in_cu(self):
        missing = self.bridge_commands - self.cu_commands
        self.assertEqual(missing, set(),
                         "MCP bridge forwards commands cu.py does not "
                         "define (renamed or removed?): %s" % sorted(missing))

    def test_driver_commands_exist_in_cu(self):
        missing = self.driver_commands - self.cu_commands
        self.assertEqual(missing, set(),
                         "session driver relays commands cu.py does not "
                         "define (renamed or removed?): %s" % sorted(missing))

    def test_bridge_driver_allowlist_parity(self):
        self.assertEqual(self.driver_commands - self.bridge_commands,
                         DRIVER_ONLY,
                         "driver-only commands changed; update DRIVER_ONLY "
                         "in this test deliberately")
        self.assertEqual(self.bridge_commands - self.driver_commands, set(),
                         "bridge forwards commands the driver will refuse")

    def test_every_cu_command_is_classified(self):
        classified = (self.bridge_commands | DRIVER_ONLY | LIFECYCLE
                      | NOT_EXPOSED)
        unclassified = self.cu_commands - classified
        self.assertEqual(unclassified, set(),
                         "new cu.py commands need an MCP decision: add "
                         "to the bridge allowlist, DRIVER_ONLY, or "
                         "NOT_EXPOSED in this test: %s" % sorted(unclassified))
        stale = classified - self.cu_commands
        self.assertEqual(stale, set(),
                         "classified commands no longer exist in cu.py: "
                         "%s" % sorted(stale))

    def test_not_exposed_stays_unexposed(self):
        self.assertEqual(NOT_EXPOSED & self.bridge_commands, set())
        self.assertEqual(NOT_EXPOSED & self.driver_commands, set())

    def test_spawn_argv_commands_exist(self):
        spawn = spawn_argv_commands(self.bridge_tree)
        self.assertIsNotNone(spawn, "session spawn argv not found in bridge")
        missing = set(spawn) - self.cu_commands
        self.assertEqual(missing, set(),
                         "bridge spawns cu.py commands that do not exist: "
                         "%s" % sorted(missing))
        self.assertEqual(set(spawn), {"session", "session-driver"})

    def test_finish_is_a_cu_command(self):
        self.assertIn("finish", self.cu_commands)

    def test_operation_enum_matches_handlers(self):
        enum = schema_enum(self.bridge_tree, "operation")
        self.assertIsNotNone(enum, "operation enum not found in bridge schema")
        handled = handled_operations(self.bridge_tree)
        self.assertEqual(set(enum), handled,
                         "MCP operation enum drifts from tool_call handlers")

    def test_image_policy_parity(self):
        enum = schema_enum(self.bridge_tree, "image_policy")
        self.assertIsNotNone(enum, "image_policy enum not found in bridge schema")
        bridge_values = accepted_image_policies(self.bridge_tree)
        driver_values = accepted_image_policies(self.driver_tree)
        self.assertTrue(bridge_values, "no image_policy validation in bridge")
        self.assertTrue(driver_values, "no image_policy validation in driver")
        for values in bridge_values + driver_values:
            self.assertEqual(values, set(enum),
                             "image_policy values drift across bridge/driver")

    def test_session_keys_shared(self):
        # mcp_bridge reads cu.SESSION_KEYS for the GUI environment; a
        # rename in cu.py would break the bridge at import time.
        self.assertTrue(has_assignment(self.cu_tree, "SESSION_KEYS"),
                        "cu.py no longer defines SESSION_KEYS")


if __name__ == "__main__":
    unittest.main()
