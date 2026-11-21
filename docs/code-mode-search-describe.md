# Code Mode search/describe for this repo

Date: 2026-11-21. Implements the two missing pieces from
docs/research/2026-11-21-code-mode-integration.md section 6:
search/describe over the full script catalog, and a snippets registry.

## What was built

- scripts/codemode_search.py: search_ops(query) and describe_op(name)
  over every script in scripts/. The registry is built by scanning
  scripts/ at import, so the count moves as scripts are added: 60 ops
  at the latest measurement (a sibling task added mcp_server.py during
  this work). Each op carries only a short description (first docstring
  or first comment lines, capped at 200 chars), tags, file name and
  size. describe_op adds top-level entry point names and the first 6
  non-empty lines, capped at 800 chars. Total describe output stays
  under 2000 chars. A whole file is never returned.
- snippets/registry.json plus snippets/p1_terminal_df.py,
  p2_terminal_calc.py, p3_terminal_mkdir.py,
  p4_terminal_write_file.py, and snippets/README.md. The four snippets
  are the Pick 1 template programs P1-P4 from
  improvements/pick1-program-template.md, copied verbatim. Each entry
  has a description, an input (terminal title plus typed text), and a
  sample output. Sample outputs were recorded on this VM on 2026-11-21
  by running the underlying shell commands; the df output reflects
  that machine's filesystem. list_snippets() and get_snippet(name) in
  codemode_search.py read the registry.
- tests/test_codemode_search.py: 19 tests.

## How to use

```sh
python3 scripts/codemode_search.py search "dom locate"
python3 scripts/codemode_search.py describe zen_dom
python3 scripts/codemode_search.py tokens "session"
python3 scripts/codemode_search.py list
python3 scripts/codemode_search.py snippet p1-terminal-df
```

Or from Python:

```python
from scripts.codemode_search import search_ops, describe_op, get_snippet
search_ops("session")
describe_op("session_manager")
get_snippet("p3-terminal-mkdir")
```

## Measured results (this VM, 2026-11-21)

Tests: python3 -m unittest tests.test_codemode_search, 19 tests, all
pass. Suite wall clock 1.088 s on the second run (2.317 s on the first
run, including interpreter start). The existing prototype suite still
passes: python3 -m unittest tests.test_codemode, OK.

Token estimates are characters divided by 4, labeled as estimates,
same proxy Worker N used. Before is the full catalog proxy: first 3
lines of every script, 7292 chars, 1823.0 tokens estimate (measured
with 60 ops in the registry). After is the search result JSON for the
query, limit 5:

- "dom locate": after 90.2 tokens estimate, saved 1732.8.
- "session": after 251.0 tokens estimate, saved 1572.0.
- "polygon": after 59.5 tokens estimate, saved 1763.5.

The saving is real but small in absolute terms, matching the
integration doc: the large saving in this repo is model calls, not
tool-definition tokens, and no before/after wall-time numbers for the
Pick 1 measurement exist yet. Do not claim a wall-time saving from
these numbers.

Snippet checks: all four snippet programs pass
scripts/code_exec.py validate_program, and the registry programs match
the .py files byte for byte (checked by a round-trip test).

## Limits, stated plainly

- Descriptions come from file heads, so a script with a missing or
  misleading docstring gets a weak description. The registry is only
  as good as the docstrings.
- Search is keyword scoring (name match beats description match), not
  semantic search. A query with words the scripts never use returns
  nothing.
- Snippets run through scripts/code_exec.py on the laptop only; this
  VM has no terminal window titled speed-pick1-term and no live Zen,
  so no snippet was executed end to end here. The sample outputs are
  the underlying shell commands run directly on this VM, not full
  program runs.
- No wall-time or model-call comparison was run. The Pick 1
  measurement is still paused, as the integration doc records.
