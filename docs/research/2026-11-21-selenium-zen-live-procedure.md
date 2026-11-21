# Selenium on real Zen after reboot, full procedure, 2026-11-21

By clone2. Purpose: one repeatable, timed, logged run of Selenium
plus geckodriver against the real Zen on the laptop, in both a
self launched configuration and an attach configuration against
the user already open Zen. Script:
tests/selenium_zen_live.py. Everything in this procedure was
verified on this machine against Firefox 160.0.1 as a stand-in,
measured results in section 5. Zen itself is UNVERIFIED until the
laptop run, there is no Zen binary on the clone2 machine.

## 1. What the script does

One real task, the same in both modes: open the local fixture page
in a new tab, read the DOM, type into the input, click the button,
verify the page changed, open example.com in a second new tab,
verify by title, close only the tabs the script created, switch
back to the original tab, end cleanly. Every step is one JSON line
with wall clock, elapsed seconds, ok flag and detail, printed and
optionally written to a JSONL file with --out.

Modes:

- launch: the script starts the browser itself with -marionette
  and a dedicated throwaway profile, and closes that browser at
  the end. Recommended for the first laptop run, it cannot touch
  the user session at all.
- attach: the script connects to a Zen the user started with
  -marionette. It deletes only the WebDriver session at the end,
  by an HTTP DELETE plus stopping geckodriver, never driver.quit(),
  so the browser and every pre-existing tab stay open.

Tab safety rules, built into the script, not optional: record the
window handles at session start, only close handles created
during the run, switch back to the original handle before
finishing, and verify the handle set at the end equals the
starting set. The attach run in section 5 proves all four.

Timing rules built in: wait 1 second after every page load before
interacting, and set the window size explicitly to 1280x900 at
session start, a zero or tiny viewport makes elements report as
not interactable.

## 2. Prerequisites on the laptop

- Zen installed, binary path known, check with: which zen, or the
  app install path. The script also auto detects common paths,
  and --zen PATH always wins.
- geckodriver on PATH or passed with --geckodriver. Version close
  to the browser, the verified pair here is geckodriver 0.37.1
  with Firefox 160.0.1.
- Python 3 with selenium installed, pip install selenium, the
  verified version here is 4.53.0.
- For attach mode only: no other Marionette session active.
  Marionette allows exactly one session at a time, a leftover
  session from a crashed run blocks new ones, see section 6.

## 3. Run it, launch mode first

From the repo root on the laptop:

    python3 tests/selenium_zen_live.py --mode launch \
        --zen /path/to/zen --geckodriver /path/to/geckodriver \
        --out /tmp/zen-live-launch.jsonl

Expected shape: every step ok true, SUMMARY ok true. Headless is
available with --headless for a smoke run, but the first real run
should be headed, watching the browser proves more than the log.

## 4. Run it, attach mode against the real session

1. Quit Zen fully if it is running without Marionette, a normally
   started Zen has no Marionette listener and cannot be attached
   to after the fact.
2. Start Zen with Marionette. With a dedicated profile, safest:

       zen -marionette -P clone2-test

   The profile folder must exist or be created by the profile
   manager first, a -profile path that does not exist fails with
   Could not find profile folder, measured here. With the user
   default profile instead:

       zen -marionette

   This is the user real session and real tabs. The script tab
   safety rules in section 1 are what make this acceptable, and
   section 5 proves them against a live browser.
3. Open a couple of tabs by hand, so the run proves it preserves
   them.
4. Run the script:

       python3 tests/selenium_zen_live.py --mode attach \
           --zen /path/to/zen --geckodriver /path/to/geckodriver \
           --out /tmp/zen-live-attach.jsonl

5. Confirm the SUMMARY line says ok true and
   browser_alive_after true, and that Zen is still open with the
   hand opened tabs untouched.

## 5. Measured verification on this machine, Firefox stand-in

Environment: headless VM, Firefox 160.0.1, geckodriver 0.37.1,
Selenium 4.53.0, 2026-11-21. These numbers are the script working
end to end, they are not Zen numbers.

Launch mode run, wall clock 2026-11-21T09:36Z area, final clean
run total elapsed 8.0402 s, 12 of 12 steps ok:

- launch browser with Marionette 0.5015 s
- create session, connect existing 3.4678 s, window set to
  1280x900
- open fixture in new tab 1.5584 s, includes the 1 s settle wait
- read DOM 0.0332 s, type 0.0569 s, click and verify 0.3846 s
- second tab example.com 1.6765 s
- close only own tabs 0.1148 s, handle set back to the start set

Attach mode run against a Firefox started by hand with
-marionette, total elapsed 4.4301 s, 13 of 13 steps ok:

- session create only 0.8006 s against the warm browser
- fixture tab 1.2763 s, read DOM 0.0465 s, type 0.0616 s, click
  and verify 0.3837 s, example.com tab 1.5142 s
- close only own tabs 0.0899 s, session deleted by HTTP, status
  200, browser still alive after, marionette port still open,
  the pre-existing tab untouched

The batch 1 script was also re-verified in this batch, as the
task required: tests/selenium_connect_existing.py with
--launch-firefox, wall clock 2026-11-21T09:40:57Z to 09:41:02Z,
all 10 steps ok, total elapsed 5.1791 s, session create 2.7269 s,
list tabs 0.0126 s, read DOM 0.2218 s, type 0.1779 s, click and
verify 0.1051 s, second tab 1.2177 s. One operator note from the
re-verification: without --launch-firefox and with no browser
running, that script session create times out after 60 s, it does
not fail fast. The new script checks the marionette port first in
attach mode and fails in milliseconds instead.

Two findings from the verification runs, both reproduced:

- The example.com served on this network is a 577 byte variant
  with the title but no h1 element, checked with curl as well as
  in the browser. The script therefore verifies the network tab
  by title and URL and reports the h1 when present, instead of
  asserting it. On a normal network the h1 reads Example Domain.
- First runs of the new script failed twice for clone2 mistakes,
  wrong fixture element ids, the fixture uses heading, q, go and
  out, and the h1 assumption above. Both were found by running,
  fixed, and re-run green. The failures are kept in the local run
  logs, they are why this package is verified at all.

## 6. Troubleshooting

- Nothing on marionette port 2828 in attach mode: the browser was
  started without -marionette, or with a profile path that does
  not exist. Restart it with the flag, section 4.
- Session create hangs or is refused: a previous session is still
  held. Marionette allows one session. Delete it with
  curl -X DELETE http://127.0.0.1:4444/session/SESSION_ID when
  the geckodriver port is known, or kill the leftover geckodriver
  process, never the browser, and retry.
- Geckodriver port 4444 already in use: a leftover geckodriver
  from a crashed run. Kill that geckodriver only.
- Element not interactable or zero size errors: the window opened
  at a tiny size. The script sets 1280x900 at session start, if a
  site still misbehaves, raise the settle wait with
  --pause-after-load 2.
- Profile locked or profile in use: the same profile is open in
  another browser instance. Use the dedicated test profile, or
  quit the other instance. Do not delete lock files by hand while
  a browser is running.
- Everything passes except the network tab: check the machine
  network with curl first, the fixture half of the test needs no
  network and separates browser problems from network problems.
- A run died mid task: the script finally block deletes the
  session in attach mode and closes only its own browser in
  launch mode. If a tab from a dead run survives, it is a normal
  browser tab, close it by hand, no state is corrupted.

## 7. Laptop checklist, in order

1. Pull the PR branch, note geckodriver and selenium versions.
2. Launch mode run, headed, watch it, save the JSONL.
3. Attach mode run against a dedicated test profile with two
   hand opened tabs, confirm tabs preserved and browser alive.
4. Attach mode run against the real user profile, same checks.
5. Record in coord: Zen version, both SUMMARY lines, total
   elapsed per mode, and any step that behaved differently from
   the Firefox stand-in numbers in section 5.
