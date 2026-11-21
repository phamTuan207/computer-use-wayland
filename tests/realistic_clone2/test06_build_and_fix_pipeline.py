#!/usr/bin/env python3
"""Test 06, terminal and editor: make a broken build green.

Context: a tiny project builds by concatenating its source modules
into one bundle and syntax checking it, driven by build.sh. The
build is broken two ways: the main module was saved under a typo
file name, mian.py instead of main.py, and inside it there is a
syntax error, one closing parenthesis too many. The task is the
terminal loop an agent runs daily: run the build, read the error,
fix the cause, rebuild, repeat, then run the bundle and check its
output.

Pass: build.sh exits 0 and prints BUILD_OK, the bundle exists, and
running it prints the expected line.
Fail: build still red, or the bundle output is wrong.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from common import Case, run_cmd

BUILD = """#!/bin/sh
set -e
cat src/greet.py src/mathx.py src/main.py > dist/bundle.py
python3 -m py_compile dist/bundle.py
echo BUILD_OK
"""

GREET = 'def greet(name):\n    return "hello " + name\n'
MATHX = "def double(x):\n    return x * 2\n"
MAIN_BROKEN = (
    'if __name__ == "__main__":\n'
    '    print(greet("team"), double(21)))\n'
)


def main():
    case = Case("test06", "make a broken build green",
                "terminal and editor")
    ws = case.ws
    with case.phase("setup_fixture"):
        (ws / "src").mkdir()
        (ws / "dist").mkdir()
        (ws / "build.sh").write_text(BUILD, encoding="utf-8")
        (ws / "src" / "greet.py").write_text(GREET, encoding="utf-8")
        (ws / "src" / "mathx.py").write_text(MATHX, encoding="utf-8")
        (ws / "src" / "mian.py").write_text(MAIN_BROKEN, encoding="utf-8")

    with case.phase("run_build_expect_failure"):
        first = run_cmd(["sh", "build.sh"], cwd=ws)
        case.check("build_fails_before_fix", first["exit"] != 0,
                   f"exit={first['exit']} err={first['stderr'][:120]}")

    with case.phase("fix_one_rename_module"):
        listing = sorted(p.name for p in (ws / "src").iterdir())
        case.check("misnamed_module_found", "mian.py" in listing,
                   f"src={listing}")
        (ws / "src" / "mian.py").rename(ws / "src" / "main.py")
        second = run_cmd(["sh", "build.sh"], cwd=ws)
        case.check("build_now_fails_on_syntax", second["exit"] != 0,
                   f"exit={second['exit']} err={second['stderr'][:120]}")

    with case.phase("fix_two_syntax_error"):
        main_path = ws / "src" / "main.py"
        text = main_path.read_text(encoding="utf-8")
        case.check("extra_paren_present", "double(21)))" in text)
        main_path.write_text(text.replace("double(21)))", "double(21))"),
                             encoding="utf-8")

    with case.phase("rebuild_and_run_bundle"):
        third = run_cmd(["sh", "build.sh"], cwd=ws)
        case.check("build_passes_after_fixes",
                   third["exit"] == 0 and "BUILD_OK" in third["stdout"],
                   f"exit={third['exit']} out={third['stdout'][:80]}")
        bundle = run_cmd([sys.executable, "dist/bundle.py"], cwd=ws)
        case.check("bundle_output_correct",
                   bundle["stdout"].strip() == "hello team 42",
                   repr(bundle["stdout"]))

    return case.finish()


if __name__ == "__main__":
    sys.exit(main())
