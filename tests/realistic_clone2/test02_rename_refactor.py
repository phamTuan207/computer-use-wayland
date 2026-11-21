#!/usr/bin/env python3
"""Test 02, code editing: rename a function across a whole project.

Context: a five file mini project exposes compute_total in a core
module, imported and called from three other modules, re-exported
from the package init, and mentioned in the README. The task is to
rename it to calculate_total everywhere code references it, keep the
README accurate, and prove the project still runs with the same
output.

Pass: no code file contains the old name, the project entry point
prints the expected total, and a fresh import of the new name works.
Fail: any stale reference, or the output changed.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from common import Case, run_cmd

FILES = {
    "shop/__init__.py": "from .core import compute_total\n",
    "shop/core.py": (
        "def compute_total(items):\n"
        "    return round(sum(i['price'] * i['qty'] for i in items), 2)\n"
    ),
    "shop/cart.py": (
        "from .core import compute_total\n\n"
        "def checkout(items):\n"
        "    return compute_total(items)\n"
    ),
    "shop/report.py": (
        "import shop\n\n"
        "def daily(items):\n"
        "    return shop.compute_total(items)\n"
    ),
    "main.py": (
        "from shop.cart import checkout\n"
        "from shop.report import daily\n"
        "items = [{'price': 10.0, 'qty': 2}, {'price': 3.5, 'qty': 4}]\n"
        "print(checkout(items))\n"
        "print(daily(items))\n"
    ),
    "README.md": "Billing uses compute_total from shop.core.\n",
}
EXPECTED_OUTPUT = "34.0\n34.0\n"


def main():
    case = Case("test02", "rename a function across a whole project",
                "code editing")
    ws = case.ws
    with case.phase("setup_fixture"):
        for rel, content in FILES.items():
            path = ws / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
        before = run_cmd([sys.executable, "main.py"], cwd=ws)
        case.check("project_runs_before", before["stdout"] == EXPECTED_OUTPUT,
                   repr(before["stdout"]))

    with case.phase("rename_everywhere"):
        for path in ws.rglob("*"):
            if path.is_file() and path.suffix in (".py", ".md"):
                text = path.read_text(encoding="utf-8")
                if "compute_total" in text:
                    path.write_text(text.replace("compute_total",
                                                 "calculate_total"),
                                    encoding="utf-8")

    with case.phase("verify_no_stale_references"):
        stale = [str(p.relative_to(ws)) for p in ws.rglob("*.py")
                 if "compute_total" in p.read_text(encoding="utf-8")]
        case.check("no_old_name_in_code", stale == [], f"stale={stale}")
        readme = (ws / "README.md").read_text(encoding="utf-8")
        case.check("readme_updated",
                   "calculate_total" in readme and "compute_total" not in readme)

    with case.phase("verify_behaviour_unchanged"):
        after = run_cmd([sys.executable, "main.py"], cwd=ws)
        case.check("same_output_after", after["stdout"] == EXPECTED_OUTPUT,
                   repr(after["stdout"]))
        probe = run_cmd([sys.executable, "-c",
                         "from shop import calculate_total; "
                         "print(calculate_total([{'price': 2, 'qty': 3}]))"],
                        cwd=ws)
        case.check("new_name_importable", probe["stdout"].strip() == "6",
                   probe["stdout"].strip())

    return case.finish()


if __name__ == "__main__":
    sys.exit(main())
