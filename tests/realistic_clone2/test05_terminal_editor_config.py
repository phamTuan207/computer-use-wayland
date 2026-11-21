#!/usr/bin/env python3
"""Test 05, terminal and editor: reconfigure an app from the shell.

Context: a small app reads config.ini and prints its effective
settings as JSON with app.py --check. The task is done the way an
agent at a terminal would do it, with shell tools and a scripted
editor pass, no GUI: change the port to 9090, turn the feature flag
on, raise the worker count to 4, and add a new [cache] section with
ttl 300. Then run the checker the app itself provides.

Pass: app.py --check exits 0 and its JSON equals the expected
effective settings, and the config file still parses as INI.
Fail: any setting off, or the app rejects the config.
"""

import configparser
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from common import Case, run_cmd

APP = '''
import configparser, json, sys
cfg = configparser.ConfigParser()
if not cfg.read("config.ini"):
    print("no config"); sys.exit(2)
out = {
    "port": cfg.getint("server", "port"),
    "feature_x": cfg.getboolean("server", "feature_x"),
    "workers": cfg.getint("server", "workers"),
    "cache_ttl": cfg.getint("cache", "ttl"),
}
print(json.dumps(out, sort_keys=True))
'''

CONFIG = """[server]
port = 8080
feature_x = false
workers = 1
"""

EXPECTED = {"port": 9090, "feature_x": True, "workers": 4, "cache_ttl": 300}


def main():
    case = Case("test05", "reconfigure an app from the terminal",
                "terminal and editor")
    ws = case.ws
    with case.phase("setup_fixture"):
        (ws / "app.py").write_text(APP, encoding="utf-8")
        (ws / "config.ini").write_text(CONFIG, encoding="utf-8")
        before = run_cmd([sys.executable, "app.py"], cwd=ws)
        case.check("app_rejects_incomplete_config_before", before["exit"] != 0,
                   f"exit={before['exit']}")

    with case.phase("edit_config_with_terminal_tools"):
        sed = run_cmd(["sed", "-i",
                       "-e", "s/^port = .*/port = 9090/",
                       "-e", "s/^feature_x = .*/feature_x = true/",
                       "-e", "s/^workers = .*/workers = 4/",
                       "config.ini"], cwd=ws)
        case.check("sed_edits_applied", sed["exit"] == 0, sed["stderr"][:120])
        with open(ws / "config.ini", "a", encoding="utf-8") as fh:
            fh.write("\n[cache]\nttl = 300\n")

    with case.phase("verify_with_the_app_itself"):
        after = run_cmd([sys.executable, "app.py"], cwd=ws)
        case.check("app_check_exits_0", after["exit"] == 0,
                   f"exit={after['exit']} err={after['stderr'][:160]}")
        got = json.loads(after["stdout"]) if after["exit"] == 0 else {}
        case.check("effective_settings_match", got == EXPECTED, f"got={got}")
        parser = configparser.ConfigParser()
        parser.read(ws / "config.ini")
        case.check("config_still_valid_ini",
                   parser.sections() == ["server", "cache"],
                   f"sections={parser.sections()}")

    return case.finish()


if __name__ == "__main__":
    sys.exit(main())
