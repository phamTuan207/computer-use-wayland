# Realistic hard tests by clone2, batch 3

Ten hard realistic browser tasks, reassigned to clone2 after
another worker failed twice to deliver them. Each test has 15 to
40 steps, a fully offline HTML fixture, a spec file, and a checker
that verifies real DOM state in a real browser through Selenium.
No simulated DOM anywhere in this suite.

Layout:

- fixtures/, one offline HTML app per test, no network, no CDN.
- specs/, one markdown spec per test, steps, expected results,
  and the measured timing from the verification run.
- tests/, one Selenium test per spec, built on harness.py.
- harness.py, shared browser launch, step timing and checks.
- run_all.py, runs every test in its own subprocess and reports
  a suite summary with wall clock and elapsed totals.

Run everything, with a Python that has selenium installed:

    python3 tests/realistic/clone2-batch3/run_all.py --out /tmp/b3.json

Run one test:

    python3 tests/realistic/clone2-batch3/tests/test01_pdf_form_fill.py

Environment: FIREFOX_BINARY and GECKODRIVER pick the browser and
driver, the same suite runs against Zen on the laptop by pointing
FIREFOX_BINARY at the Zen binary. BATCH3_HEADED=1 runs headed.

| Test | Topic |
| --- | --- |
| test01 | PDF form fill, validate, submit |
| test02 | Video player, play, pause, seek, volume, subtitle, playlist |
| test03 | Keyboard only navigation, full flow, no mouse |
| test04 | Drag and drop kanban, state saved |
| test05 | Canvas drawing, colors, undo, save image |
| test06 | Chat app, send, receive, typing indicator, search |
| test07 | Map directions, transport modes, time estimates |
| test08 | Shopping cart checkout, discount code, payment form |
| test09 | Code review diff, per line comments, approve, request changes |
| test10 | Data dashboard, table, filter, sort, export CSV |
