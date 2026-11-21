# Snippets registry

Reusable code-exec programs, taken verbatim from the Pick 1 template
programs P1-P4 in improvements/pick1-program-template.md. Each snippet
has a description, an input, and a sample output. The registry file is
registry.json; the same programs also live as plain .py files here.

Use from Python:

```python
from scripts.codemode_search import list_snippets, get_snippet
list_snippets()            # short list: name, title, description
get_snippet("p1-terminal-df")  # full entry with program and sample output
```

Run a snippet program through scripts/code_exec.py, not by importing
it. Shape for every program: windows -> observe -> act -> observe ->
assert. The observe after act is both the settle interval and the
verify image; never assert directly after act.

Sample outputs were recorded on the VM on 2026-11-21 by running the
underlying shell commands. The df output reflects that machine's
filesystem, not the laptop.
