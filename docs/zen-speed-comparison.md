# Zen control speed comparison, all methods, 2026-11-21

By clone2. Every number in this document carries its condition and
its source. Numbers measured by clone2 say so, with the machine,
the browser and the date. Numbers from other sources are labelled
reported or documented and are not re verified here. Nothing is
estimated silently, where no number exists the cell says so.

## 1. Measured here, Marionette against BiDi, same task

Benchmark: tests/zen_speed_benchmark.py, 3 runs per method,
medians below, runs listed in the raw log summary at the end of
this section. Machine: headless Linux VM. Browser: Firefox
160.0.1 as a Zen stand-in, Zen speaks both protocols identically
at this level, real Zen numbers need the laptop run of the same
script. Date: 2026-11-21. Both methods did the same task on the
same pages: session start, list tabs, navigate to a local
fixture, read the heading, put text in the input, click the
button, read the result, navigate to example.com, read the title.

Mechanism note: Marionette steps are WebDriver element commands
through geckodriver, typing is real key events, clicking is a
real element click. BiDi typing and clicking here are DOM
operations inside script.evaluate, set value plus dispatch
events, and call click(). Same outcome, different mechanism,
which is exactly why BiDi type looks so fast, it skips the input
pipeline.

| Step | Marionette median | BiDi median | Faster |
| --- | --- | --- | --- |
| session start | 0.1211 s warm, 2.906 s cold first run | 0.0017 s | BiDi, by a lot |
| list tabs | 0.0021 s | 0.0018 s | tie |
| navigate to local fixture | 0.2053 s | 0.0282 s | BiDi |
| read DOM heading | 0.0754 s | 0.0048 s | BiDi, about 16x |
| type 12 chars | 0.1514 s, real keys | 0.0021 s, DOM set | BiDi, different mechanism |
| click and verify | 0.2907 s | 0.2040 s | both include a fixed 0.2 s settle sleep, raw call about 0.09 s against about 0.004 s |
| navigate example.com | 0.0545 s | 0.0337 s | BiDi, network variance dominates |

Raw runs, seconds. Marionette: session 2.906, 0.1211, 0.0641,
list 0.0021, 0.0029, 0.0018, fixture nav 0.2053, 0.2648, 0.1012,
read 0.0758, 0.0754, 0.0396, type 0.2125, 0.1152, 0.1514, click
0.2962, 0.2773, 0.2907, web nav 0.9986, 0.0545, 0.0425. BiDi:
session 0.0157, 0.0017, 0.0014, list 0.0213, 0.0018, 0.0014,
fixture nav 0.1264, 0.0195, 0.0282, read 0.016, 0.0027, 0.0048,
type 0.003, 0.001, 0.0021, click 0.204, 0.2036, 0.2062, web nav
0.0344, 0.0337, 0.0325.

Reading: a BiDi session over a raw socket is nearly free to open
and its DOM reads are single evaluate round trips at single digit
milliseconds. Marionette pays a real session negotiation, worst
on the cold first run, and every element command is a geckodriver
round trip at tens of milliseconds. For a long task of many small
DOM steps, BiDi wins by an order of magnitude on step latency.
For a short task, both are dominated by browser startup and page
loads, not by protocol steps.

## 2. Measured here, full Selenium runs, batch 1 and batch 2

Same machine and browser as section 1, Selenium plus geckodriver
connect existing, full task runs including browser handling:

| Run | Total | Session create | Read DOM | Type | Click and verify | Second tab web |
| --- | --- | --- | --- | --- | --- | --- |
| batch 1 script, 2026-11-21 morning run 1 | 9.2447 s | 2.8927 s | 0.27 s area | 0.18 s area | 0.09 s | 1.7262 s |
| batch 1 script, morning run 2 | 4.9837 s | 2.7904 s | 0.13 s area | 0.12 s area | 0.09 s | 0.8420 s |
| batch 1 script, re-verified in batch 2 | 5.1791 s | 2.7269 s | 0.2218 s | 0.1779 s | 0.1051 s | 1.2177 s |
| zen live script, launch mode, batch 2 | 8.0402 s | 3.4678 s | 0.0332 s | 0.0569 s | 0.3846 s | 1.6765 s |
| zen live script, attach mode, batch 2 | 4.4301 s | 0.8006 s | 0.0465 s | 0.0616 s | 0.3837 s | 1.5142 s |

Attach mode is the fastest Selenium shape because the browser is
already warm, session create drops from about 3 s to 0.8 s. The
click figures in the zen live rows include the built in settle
waits. Full step logs are in the procedure document for task 5.

## 3. Reported numbers, real Zen on the laptop, not clone2 measured

From the coordinator progress report shown to clone2 on
2026-11-21: a Selenium based process at 0.278 s and a real task
at 0.64 s with 0 misses on real Zen, and a 20 test run on real
Zen by another worker. Condition: real Zen on the user laptop,
post reboot session. These are the fastest Selenium figures in
this document and they are plausible next to section 2, a warm
browser and a small page, but clone2 did not measure them and
cannot reproduce their exact task definition. Label: reported,
unverified by clone2.

The repo own BiDi path, scripts/zen_cli.py against real Zen
1.24.2b, is verified working in the repo records, a dedicated
headless instance answering session and tab commands, but the
repo records no per step timings for it. Label: functional,
no published timings. The benchmark in section 1 is the first
timed BiDi run in this project, on the Firefox stand-in.

## 4. Documented numbers from the other methods

- zen-mcp and zenpilot, from the batch 1 research: both are BiDi
  based, so their step latency should sit in the same class as
  section 1 BiDi, single digit to tens of milliseconds per DOM
  step. Neither project publishes a timing table that clone2
  could verify. Label: documented architecture, no verified
  timings.
- Playwright with Firefox: launch only, no attach, from batch 1.
  No Zen attach path exists, so it has no place in a Zen speed
  table beyond noting its Firefox launch automation is in the
  same WebDriver class as Marionette for step latency. Label:
  documented, not measured here.
- kde-desktop-mcp, from its README, batch 2 research: tool calls
  take milliseconds, one Firefox get_text example goes from
  8.7 ms to 1.1 ms with its 2 s tree cache, an AT-SPI call waits
  at most 2 s, and its own benchmark section states task time is
  dominated by model turns and read size, not call latency.
  Label: documented by the project, not re measured here.
- agent-desktop, from its Linux adapter pull request: one
  snapshot case improved from 2.025 s to 35 to 95 ms during its
  Wayland work. Label: documented by the project.
- linux-use, author reported: walking 28 interactive elements in
  gnome-calculator in 48 ms, about 1.7 ms per element. Label:
  author reported.
- AT-SPI raw, third party Hyprland census: 87 elements walked in
  about 20 ms, 0.22 to 0.24 ms per element for name and role.
  Label: third party measured, cited in the AT-SPI document.
- Screenshot plus pointer, the repo general desktop path: no per
  click timing is published in the repo logs. Its cost shape is
  structural, one capture, one locate step that in this repo is a
  model round trip at seconds scale, one pointer move and click,
  usually one more capture to verify. It is the slowest path per
  action in this comparison and the only one that works on
  canvas and tree less surfaces. Label: qualitative, from the
  repo architecture, no invented number.

## 5. Conclusions, fastest per task type

- Opening a control channel: BiDi over a raw socket, 0.0017 s
  median session, against Marionette 0.8 s warm attach and about
  3 s cold. BiDi wins.
- Listing tabs: tie, both about 0.002 s once connected.
- Reading the DOM: BiDi evaluate, 0.0048 s median, against
  Marionette element reads at 0.03 to 0.27 s depending on the
  run. BiDi wins, about an order of magnitude.
- Typing: BiDi DOM set is fastest at 0.0021 s but is not real
  typing, it sets the value and dispatches events, which some
  apps ignore. For real key events, Marionette send keys at
  about 0.06 to 0.18 s is the measured option. Choose by whether
  the target app trusts DOM set values.
- Clicking: BiDi evaluate click, about 0.004 s raw, against a
  Marionette real click at about 0.09 to 0.11 s raw. BiDi wins on
  speed, Marionette wins on fidelity, it goes through the real
  input and focus path.
- Navigating: close, network and page weight dominate, protocol
  difference is tens of milliseconds.
- Native desktop apps: AT-SPI semantic actions, per element walk
  at sub millisecond to a few milliseconds from the documented
  figures, against seconds for a screenshot plus model locate.
  AT-SPI wins wherever a tree exists.
- Anything with no DOM and no tree, canvas, games, video: the
  screenshot path is the only option, speed is what it is.

Primary and fallback recommendation for Zen: BiDi primary for
DOM work, it is the repo existing direction and now the measured
fastest. Marionette as the attach fallback, it is the only
method that attaches to a user started Zen with -marionette, and
the only one here sending real input events, at a session cost
of about 0.8 s warm. Screenshot plus pointer stays as the
universal fallback for surfaces neither protocol can see. On the
laptop, run tests/zen_speed_benchmark.py against real Zen and
replace the stand-in medians in section 1 with Zen medians, the
script is ready and takes the Zen binary path as an argument.
