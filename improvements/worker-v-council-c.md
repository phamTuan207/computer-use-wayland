# Council Member C verdict: Fix 4 (ActiveByDefault=True) and audit of Worker T diagnosis
# Council C, 21/11/2026. All times wall-clock Asia/Ho_Chi_Minh.
# Session started 17:24:02 +07. Live checks 17:24-17:27 +07 (about 4 minutes elapsed).
# Scope: ONLY Fix 4 and the soundness of T's diagnosis. Fix 1 is already applied and not revisited.
# Rules followed: read-only on the laptop, no config change, no service restart, no ydotool, no em dash or en dash anywhere.

## Verdicts (up front)

- Fix 4 (ActiveByDefault=True): REJECT as a fix for the reported symptom.
  Revisit only as a separate, narrow experiment if a distinct symptom is reported
  ("IM inactive in the first field after login"), and only then as a bounded trial
  paired with ShareInputState=Program plus terminal and sudo-password regression checks.
  Confidence: high (about 80 percent).
- T's diagnosis: SOUND WITH GAPS.
  The core findings reproduce and survive independent re-checking. The gaps are real
  but do not overturn the root causes. Confidence: high (about 85 percent).

## Fix 4: what was verified live

### 1. Current config value, confirmed read-only
- `~/.config/fcitx5/config` read live 17:24 +07: `[Behavior] ActiveByDefault=False`.
  The file contains only that one Behavior key plus TriggerKeys (Zenkaku_Hankaku, Hangul).
- `~/.config/fcitx5/profile` read live: group Default, items keyboard-us + ngosen,
  DefaultIM=ngosen.
- `fcitx5-remote -n` at 17:24:26 +07 returned `ngosen`, rc 0. Current state is ngosen, active.
- Omarchy ships the same value as its template: `/usr/share/omarchy/config/fcitx5/config`
  also has `[Behavior] ActiveByDefault=False`. So False is the shipped Omarchy default,
  not a user deviation.

### 2. What ActiveByDefault actually changes: NOT established from a primary source
- Secondary docs agree on the slogan ("input method starts in active state") but
  disagree or stay vague on the scope:
  - NixOS wiki: "Without Active By Default set to True, fcitx5 needs to be manually
    activated by pressing the hotkey etc. after the initial launch." That reads as
    initial-launch / first-context scope, not per-tab.
  - An Omarchy Chinese-environment skill doc (same stack, Arch + Hyprland + fcitx5):
    "Missing ActiveByDefault starts apps in Inactive mode." That reads as per-app scope.
- I could not verify the compiled-in default for ShareInputState from any source
  available to me, and that default decides the question:
  - If ShareInputState is All (shared global state), ActiveByDefault only sets the
    initial state at daemon start, and every later context inherits the global state.
  - If ShareInputState is No (per-context), every new context starts per ActiveByDefault.
- Decisive local fact: neither the user config nor the Omarchy template sets
  ShareInputState, resetStateWhenFocusIn, or AllowInputMethodForPassword anywhere
  (grep over `~/.config/fcitx5/` returned no matches; `/etc/xdg/fcitx5/` has no such file).
  So Fix 4's mechanism on THIS machine depends on an unverified compiled-in default.
  T never established it either. A fix whose mechanism cannot be stated from the
  machine's own config is not ready to implement.

### 3. T's own refutation already answers Fix 4's test in Zen
- T proved live (16:44:08-16:44:35): a new Zen tab does NOT reset the reported IM,
  ngosen stayed ngosen across tab A to tab B.
- T's proposed Fix 4 verification test is "type Telex in 5 fresh Zen tabs with no
  toggle, 5/5 must compose." That test would ALREADY PASS today, because new tabs
  already inherit ngosen active. A test that passes with the fix off cannot verify
  the fix. The test is non-discriminating and must be replaced (see the valid test below).
- Therefore Fix 4 treats a mechanism T himself refuted for the reported symptom.
  The reported failures were a stall (5 wtype hangs, 16:42:27-16:45:12) and async Super I
  lag (21s), neither of which ActiveByDefault touches.

### 4. The user-annoyance risk is real, and larger than T stated
Daily typing surfaces, evidenced live from the laptop process list at 17:25:08 +07:
Zen (`zen-bin --remote-debugging-port=9222 --marionette`), kitty terminal (herdr/jarvis
session), Brave and Chromium, opencode. No editor process was running at that moment,
so I make no claim about editor behavior.

(a) Terminal bleed is documented on this exact stack. The Omarchy Chinese-environment
skill doc states: "Terminal defaults to Chinese: Opening a new terminal window inherits
Chinese mode from the browser, requiring manual Shift switching before running commands."
Its recipe pairs ActiveByDefault=True with ShareInputState=Program precisely to contain
that bleed. The engine differs there (Rime vs ngosen) but the bleed mechanism is
framework-level, not engine-level. With ActiveByDefault=True and the current unset
(sharing-unknown) config, a fresh kitty window can open with ngosen active, and the
user must toggle before typing commands.

(b) Telex corruption surface in the terminal, predicted from ngosen's own config
(`~/.config/fcitx5/conf/ngosen.conf`, read live):
- VietnameseOn=True, so when ngosen is the current IM every keystroke is Telex-composed.
- DdFreeStyle=True, with the in-file comment "Allow dd To Produce d When Auto Restore
  Invalid Words Is On". So `dd` becomes d even with auto-restore on. Everyday hits:
  the `dd` command itself, `git add` (add contains dd), `adduser`, `address`.
- Doubled vowels: `oo` becomes o, `ee` becomes e, `aa` becomes a. Everyday hits:
  `root` becomes rot, `free` becomes fre, `sleep` becomes slep, `screen` becomes scren,
  `google` becomes gogle, `book`, `tool`, `docker` is hit differently (see below).
- Tone keys after vowels (s/f/r/x/j): `docker` becomes docke (e + r is a tone),
  `bash` becomes bah (a + s), `status` becomes status with u + s toned.
  (Diacritics shown simplified; the point is the ASCII command is corrupted.)
- Mitigation exists but is conditional: AutoNonVnRestore=True restores words that are
  not valid Vietnamese, typically at a word boundary. That rescues many cases once a
  space is typed, but not mid-word Tab completion, not Enter pressed mid-word, and
  never the dd case, which DdFreeStyle explicitly exempts. I did NOT live-test typing
  in the user's terminal (read-only rule), so I state this as predicted from the
  engine config and Telex rules, not as a measured rate. A measured rate needs the
  bounded trial below, in a scratch terminal, not the user's working one.
- Net quantification: the corruption surface covers a large share of everyday shell
  words (any doubled vowel, any dd, any vowel followed by s/f/r/x/j), the auto-restore
  mitigation is partial and boundary-triggered, and a corrupted command fails silently
  or, worse, runs as a different command. That is a daily annoyance, not an edge case.

(c) The password-field reassurance is overstated. T claims "fcitx5 already steps aside
in password fields, so that specific risk is low." Two problems:
- The laptop config sets no AllowInputMethodForPassword, so the claim rests on an
  unverified compiled-in default, not on this machine's config. The only local support
  is a code comment in indicator.py ("steps aside in password fields"), which describes
  GUI password fields with an input-purpose hint.
- Terminal password prompts have no input-purpose channel at all. A `sudo` password
  typed in kitty is plain terminal input to fcitx5; nothing tells the IM it is a
  password, so Telex composition applies and the password corrupts invisibly (hidden
  echo, no feedback). The user types sudo passwords daily on this laptop. So the
  password risk is low in Zen web forms and high in the terminal, and Fix 4 makes the
  terminal case more likely by starting more contexts active.

(d) ngosen has no per-engine activation override that would contain this.
ngosen.conf has no per-context or per-app activation setting; VietnameseOn=True is
global to the engine. Two interacting settings matter:
- RetypeAfterSwitch=True ("Retype text typed before switching on"): text typed while
  the IM was off gets retyped through Telex after a switch-on, which can compound the
  garbling T observed after the stall ("chaof banjhào bạn xin chaoào").
- FreeMarking=True and ModernStyle=True widen which sequences compose.
Nothing in ngosen.conf limits Telex to Zen or to Vietnamese text.

### 5. Fix 4 verdict: REJECT (for the reported symptom)
Strongest 3 reasons:
1. It treats a mechanism T refuted. New Zen tabs already keep ngosen active, so
   ActiveByDefault=True cannot fix "typing breaks in Zen tabs". The diagnosed causes
   are the stall and the async Super I loss, which Fix 4 does not touch.
2. Its acceptance test is non-discriminating. The 5-fresh-tabs test would pass 5/5
   today with the fix off, so it cannot prove the fix works.
3. The downside is documented and daily. Terminal bleed is a known Omarchy + fcitx5
   annoyance (new terminal inherits the active IM), Telex corrupts a large class of
   everyday shell words (dd, doubled vowels, vowel + tone key), DdFreeStyle=True
   explicitly exempts dd from auto-restore, and terminal sudo passwords have no
   password-purpose protection, so they can corrupt invisibly.

Conditions for any revisit (not an endorsement, a gate):
- Only if a DISTINCT symptom is reported, namely "IM inactive in the first field
  after login/reboot, needs a toggle", separate from the stall and Super I issues.
- First establish the ShareInputState compiled-in default (from fcitx5 upstream source
  or configtool) and state Fix 4's exact scope in writing.
- Trial it paired with ShareInputState=Program (the Omarchy Chinese-environment recipe
  for containing bleed), with an instant rollback (set False, restart fcitx5) and a
  named owner.
- A valid verification test (replacing T's): (i) after a fresh login, first field in
  Zen composes Telex with no toggle; (ii) open 3 fresh kitty windows and type
  `dd`, `git add`, `free -h`, `root`, `docker ps`, `sudo -n true` text entry
  (scratch, no real password), each must arrive uncorrupted with no toggle, or the
  trial fails; (iii) Super I still flips within 1s in the healthy state.

## Audit of T's diagnosis

### What I independently re-verified (all read-only, 17:24-17:27 +07)
- Config and profile values match T exactly: ActiveByDefault=False, group Default,
  keyboard-us + ngosen, DefaultIM=ngosen, VietnameseOn=True.
- indicator.py source (lines 1-160 and 210-322, read live): the Super I chain,
  pending mechanism, 1000ms dbus timeout in call(), 500ms poll, 50ms pending poll,
  all as T described, with one attribution correction below.
- T's run logs on disk (`~/workspace/worker-t-typing-run.log`,
  `worker-t-typing-run2.log`, `worker-t-typing-run3.log`): timestamps, session ids,
  timeouts, and the garbled value "chaof banjhào bạn xin chaoào" match T's narrative
  exactly. Run 2 session c7fd43f8, run 3 session 6917a8c9, 5 wtype timeouts, cycle 7ms,
  recovery 16:45:21-16:45:23.
- Journal for the stall window 16:42:00-16:46:00 (checked live): user journal at
  priority warning has NO entries in that window; the fcitx5 unit log shows only an
  autosave at 16:47:30 and nothing in 16:40-16:50; the system journal shows only
  Chromium scopes starting (16:42:41, 16:43:09, 16:44:22 twice) and xkbcomp warnings
  at 16:45:19 and 16:45:21. No fcitx5 error, no Hyprland error, no OOM, no kill.
  That is consistent with a silent event-loop stall (no log output is expected) and
  with T's "daemon is not crashing" claim.
- Load: 12 CPUs live (`nproc` = 12). T's "load average 1.78" is therefore about 15
  percent of capacity, not a spike. See gap G4.

### What is sound
- The stall is real and reproduced 5 times in one window, with healthy baselines
  measured the same day (wtype 129ms healthy, Super I about 200ms healthy, 21s stalled).
- Super I is async and can silently lose a switch. The mechanism is real (see the
  attribution correction, which strengthens rather than weakens it).
- The "new tab resets IM" story is correctly refuted for the reported state.
- The lotus-autostart side bug is correctly identified as a silent no-op
  (T tested `-s lotus` at 16:37, IM stayed ngosen). Not re-tested by me; Fix 1 is
  already applied and out of scope.
- The stall trigger is correctly left open as an open item, not guessed.

### Gaps (numbered)
- G1. Marionette exoneration is overstated; the premise is wrong for Marionette.
  T writes "NOT Zen, NOT Marionette/BiDi (no BiDi session was active during the
  hangs...)". BiDi and Marionette are different protocols. T's own run logs show a
  Marionette session WAS active during both stall runs: run 2 session c7fd43f8
  created 16:42:26, exactly 1 second before the first hang at 16:42:27, and run 3
  session 6917a8c9 created 16:44:07, during the stall. So "no session was active"
  is true only for BiDi, not for Marionette. Two observations cut the other way and
  keep the exoneration plausible but not proven: run 1 (16:41:27) created and deleted
  a Marionette session with no stall, so session creation alone does not cause stalls;
  and the stall ENDED 16:45:21-16:45:23 while run 3's session was still alive
  (deleted 16:45:23), so a live Marionette session does not sustain the stall.
  The honest statement is: Marionette is not proven as trigger or sustainer, but the
  onset in run 2 coincides with T's own session creation plus tab focus, and the
  flags-vs-session distinction matters. The "indirect correlation" claim (agent-driven
  context churn makes the user hit the stall more often) survives, but it should be
  stated as the best available explanation, not as a proven exoneration of Marionette.
  Also, the flags themselves (--remote-debugging-port, --marionette) have no input
  path: Marionette is a remote control protocol for JS and UI (Firefox source docs),
  and Gecko IME state is managed per focused element by IMEStateManager, not by the
  debugging server. No source links remote debugging to IME handling. That part of
  T's claim stands; the live-session part does not.
- G2. Pending-clear attribution is imprecise (mechanism stands, and is slightly worse).
  T writes "in indicator.py refresh(), if the fcitx5 dbus call fails or times out
  (1000ms timeout in call()), the code catches GLib.Error and CLEARS pending silently."
  In fact refresh() itself (lines 108-133) has no try/except. The clearing happens in
  the two callers: watch()'s nested refresh() (lines 225-231: on GLib.Error,
  pending = "" AND last = "") and command() (lines 301-302: on GLib.Error and others,
  pending = ""). Because refresh() calls snapshot() and SetCurrentIM() unwrapped, ANY
  dbus error in either clears the pending choice. Worse than T stated: the code
  comment at line 248-249 says "A failed read of a running service is retried",
  but only the poll is retried (after 2000ms); the pending choice itself is dropped,
  not retried. And if SetCurrentIM succeeds but the follow-up snapshot fails, pending
  is cleared even though the switch landed, and last is wiped too, so the widget loses
  track of the state. Fix 2 (retry pending instead of clearing it) is therefore the
  right target, and its motivation is stronger than T wrote.
- G3. Two live suspects in the stall window were missed or under-checked.
  (a) Chromium scopes: T cites only 16:44:22. The journal also shows scopes starting
  16:42:41 and 16:43:09. The 16:42:41 scope starts 14 seconds AFTER stall onset
  (16:42:27), so it cannot be the onset trigger, but a Chromium launch during the
  stall could have prolonged it, and T never addressed the earlier scopes.
  (b) xkbcomp keymap recompiles at 16:45:19 AND 16:45:21: T dismisses these as routine
  (80 that day). Two recompiles bracketing the exact recovery second (system wtype
  succeeded at 16:45:21) is at least a timestamp worth correlating, not just noise:
  a keymap recompile is what happens when a virtual keyboard is created or recreated,
  which is exactly the wtype path that was hanging. Not a cause claim, an open
  correlation Fix 5's monitor should capture (log xkbcomp events alongside stalls).
- G4. "System load spike" as a stall candidate is weak as stated. T cites load average
  1.78 at 16:49. The laptop has 12 CPUs (verified live with nproc). Load 1.78 on
  12 cores is about 15 percent, essentially idle. A load spike cannot be a serious
  candidate on that number; if load is pursued, Fix 5 should log per-core load and
  per-process CPU at stall time, not a bare load average.
- G5. Per-context activation (H2) rests on an unverified default, as in Fix 4 section 2.
  T refuted the new-tab reset for the reported state, which is correct, but the
  residual claim ("ActiveByDefault=False remains a real footgun for per-context
  activation") assumes new contexts start inactive. That depends on the unset
  ShareInputState default, which T never established. If the default is shared state,
  there is no per-context footgun in Zen at all.

### Diagnosis judgment: SOUND WITH GAPS
Strongest 3 reasons for sound:
1. The core reproduction is timestamped, repeated 5 times, and independently
   re-verified from T's on-disk logs: the stall, the 21s Super I lag against a
   200ms healthy baseline, and the garbled late-delivered keystrokes are all real.
2. The mechanism for "Super I does not register" is confirmed in source: async
   queueing through Quickshell IPC plus indicator.py pending, with silent clearing
   on any dbus error (G2 corrects the attribution but strengthens the mechanism).
3. The negative claims that matter were checked, not assumed: fcitx5 journal is clean
   with no crash or restart, indicator.py PID 3444 stayed alive through the stall,
   and the journal window I re-checked live shows no fcitx5 or Hyprland errors.

Gaps G1-G5 (listed above) do not overturn the root causes. They change what is proven
about Marionette, the exact pending-clear site, the stall-trigger candidate list, and
the Fix 4 mechanism. Fix 2 remains the highest-value fix; Fix 5 (logging-only stall
monitor) is the only way to close the open trigger item, and it should also log
Marionette session lifetimes, Chromium scope starts, xkbcomp events, and per-core load.

## What I did not do (per the brief)
- No file edited on the laptop, no fcitx5 config change, no service restart.
- No typing test in any live app or terminal (read-only). Telex corruption figures
  above are predicted from ngosen.conf and Telex rules, not measured.
- No live-browser work. Docs were checked by web search and page fetch only.

## Sources
- Live laptop, read-only via ~/workspace/ssh-laptop.sh, 21/11/2026 17:24-17:27 +07:
  ~/.config/fcitx5/config, ~/.config/fcitx5/profile, ~/.config/fcitx5/conf/ngosen.conf,
  /usr/share/omarchy/config/fcitx5/config, /usr/share/omarchy/default/input-methods/indicator.py
  (lines 1-160, 210-322), fcitx5-remote -n (ngosen, rc 0, 17:24:26 +07),
  journalctl 16:42:00-16:46:00, nproc (12), ps (Zen, kitty, Brave, Chromium, opencode),
  ~/workspace/worker-t-typing-run*.log.
- Worker T: improvements/worker-t-vietnamese-typing-diagnosis.md and
  improvements/worker-t-vietnamese-typing-log.md, commit 029cb9b.
- Docs: NixOS wiki Fcitx5 ("Without Active By Default set to True, fcitx5 needs to be
  manually activated ... after the initial launch"); Omarchy Chinese-environment skill
  doc (tomturing/omarchy-cn, "Terminal defaults to Chinese: Opening a new terminal
  window inherits Chinese mode from the browser"); Firefox source docs, IME handling
  guide and Marionette overview (Marionette is a remote protocol for JS/UI;
  IME state is per focused element via IMEStateManager).
