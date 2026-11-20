# Held-out DOM grounding protocol

## Offline generator and run

The generator in `tests/heldout_dom_cases.mjs` creates 12 cases from an
unsigned 32-bit seed. Each case varies a synthetic application label, control
names, visible rectangles, DOM order, and action sequence. The task plan carries
only target names and sequence. The adapter must resolve each target from a
fresh DOM observation by unique role and name; generated coordinates are used
only to lay out the fake DOM.

Run one seed with:

```sh
CU_HELDOUT_SEED=314159265 python3 -m unittest discover -s tests -p 'test_cdp_snapshot.py' -v
CU_HELDOUT_SEED=314159265 node tests/cdp_snapshot.mjs
```

The Python test runs the production CDP adapter against its fake CDP transport,
checks each click separately, writes and verifies per-attempt JSONL, and asserts
the hit-rate counters. The Node command prints the case count, observation
count, hit rate, and synthetic per-click timing. Its batch timing includes the
final assertion and is divided by click count. Use another seed for an
independent deterministic sample. The same seed must reproduce the same cases;
a different seed must change them.

## Interpreting results

This offline suite checks that DOM grounding follows newly generated role/name
targets across varied layouts and sequences. Its adapter and harness timings
are synthetic. They do not measure real browser latency, screenshot/mouse speed,
desktop pointer accuracy, or real-app hit rate. Do not present them as live
accuracy evidence.

## Independent live run still owed

A fresh independent agent should run the offline command with a seed not used in
the run log, then validate the same method on a genuinely new browser app or
content set when a live-browser run is authorized. For that live run, record the
app and viewport geometry, define targets from the new UI at runtime, resolve
each target by observed role/name, batch only known actions, and append every
click outcome to JSONL. Compare DOM and screenshot/mouse on the same cases and
report hit rate plus elapsed time per action. Do not reuse target coordinates
from earlier cases. Record live and synthetic results separately.
