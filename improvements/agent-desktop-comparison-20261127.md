# Agent-desktop comparison study (clone2, 2026-11-27)

Scope: vercel-labs/agent-desktop (HEAD ce2ddf07, v1.3.1, Rust,
~27,100 lines, 355 commits) against computer-use-wayland
(main, Python, Hyprland/Wayland plus Zen/Firefox). Method: five
parallel research lanes (architecture, observation and element
finding, speed and accuracy, API and error contract, gaps and
what not to copy), one synthesis register, then two debate
rounds: round 1 with three council scorers (value,
feasibility and risk, evidence) plus one red team; round 2
with a convergence council plus a second red team. Every idea
below carries its final verdict from that debate, not just the
lane that proposed it.

Two laws governed the study, set by the owner on 2026-11-27.
Source law: every cited source was actually opened; repo sources
are cited by path and line; anything not opened or not
verifiable is labelled UNVERIFIED and never stated as fact.
Proof law: a claim or proposal counts as proven only if it was
run for real on clone2's machine with measured before and after
numbers; everything else is labelled UNPROVEN, with the pilot
that would prove it named.

One caveat first, because the comparison is not like with
like: agent-desktop is a shipped cross-platform product with
CI, a docs site, and 355 commits; ours is a 10-day-old
single-machine research stack for one user and one laptop.
Rows about CI, distribution, and product breadth are findings
about age and purpose, not about technique, and the debate
records them as deliberate non-goals at our scale, not as
oversights. Where a lane imported one of their measurements
(2.1 ms/node, 2.5-3.5x concurrency, 7x cache, p50/p95 over
31 runs), the debate struck it as justification: Rust async
zbus numbers do not transfer to our Python synchronous D-Bus
under the GIL, and no idea ships on their numbers. Every
idea's savings claim is UNPROVEN until it is re-measured on
our stack, except the one already-banked figure noted in
section 5.

Working papers are local in ~/workspace/agent-desktop-study-out/:
five lane files, synthesis-register.md, debate-council1-value.md,
debate-council2-feasibility.md, debate-council3-evidence.md,
debate-redteam.md, debate-round2-convergence.md, and
debate-round2-redteam.md. Study cost: 12 subagent sessions
(5 lanes, 1 synthesis, 4 debaters in round 1, 2 in round 2)
plus coordinator time. Wall clock and token spend are
UNMEASURED; no timesheet exists.

## Verdict

We are ahead where it matters for our mission, and behind in
discipline. Ahead: real DOM control of Zen (exact rects, field
values, workspace and pinned-tab internals), trusted session
ownership of a live desktop, destination scoping in the RDP
lane, and outcome grading by blind scorers with sealed
evidence. Behind: our error contract is free text, our element
refs are bare sequence numbers with no ambiguity detection,
our observation completeness is one top-level flag, and our
layering and guardrails are convention rather than checked.

The debate converged on 7 whole-ADOPT ideas, 6 split ideas
with an adopt-now half, 5 whole PILOT-FIRST ideas plus 3 pilot
halves, and 3 whole-REJECTED ideas, with 19 rejected forms or
halves in total. The do-first list is section 3. The three
whole rejections are sandbox desktops (I11), MCP catalog
generation (I19), and the cross-lane interaction lease (I20),
each replaced by a small adopted substitute: throwaway
profiles (already built), a drift test, and RDP lock
hardening. All 12 not-recommended entries from the lanes are
upheld, none overturned.

One finding is not an idea at all and is recorded as an open
item in section 6: a personal name sits in two skill files in
the repo, which violates the project's absolute no-personal-info
rule. The name is not reproduced anywhere in this report.

## 1. The comparison, condensed

The full table is 26 dimensions in the synthesis register.
This is the condensed version; each row cites its lane.

| Dimension | agent-desktop | computer-use-wayland (ours) |
|---|---|---|
| Architecture | Strict layered Cargo workspace; core defines a PlatformAdapter trait, platform crates implement it, core never imports a platform crate; CI enforces isolation with a check that plants violations to prove detection (A) | Python multi-lane system orchestrated from scripts/cu.py (2,633 lines); lanes are separate backends (CDP, BiDi, Marionette, RDP, AT-SPI, CLI-Anything); layering is convention, not checked; lanes share helpers through cu.py (A) |
| Process model | One-shot CLI processes; all continuity on disk under ~/.agent-desktop (mode 0700); sessions are namespaces, not connections (D) | Split personality: zen_cli.py one-shot against a long-lived dedicated browser; cu.py holds a live session with a JSON-lines driver, one shared seat, Esc cancel latch; zen_dom.py enforces one global session with a file lock (D) |
| Output contract | One versioned JSON envelope, contract "2.6", drift-tested; exactly one JSON object on stdout, debug to stderr; exit codes 0/1/2 (A, D, E) | No version field anywhere; four implicit contracts; zen_cli.py prints one JSON object per command; cu.py shapes vary by subcommand; rdp_client.py prints JSON for results but plain ERROR: text on stderr; exit codes inconsistent (D) |
| Error taxonomy | Closed set of 17 codes; every error carries suggestion, recovery strategy only when safe, and a retry disposition; agents branch on error.code, never message text (D) | Free-text error strings; zen_cli.py catches exceptions into {"ok": false, "error": str(exc)}; rdp_client.py uses ALL-CAPS prefixes an agent must string-match; some ad-hoc error_code values in cu.py act results (D) |
| Retry disposition | disposition.delivery (unknown / not_delivered / delivery_uncertain / delivered_unverified / delivered_verified) and disposition.retry on every error and action; v2.5 deleted unconditional success flags like clicked (A, C, D) | Retry safety is skill prose ("never replay uncertain input") and per-tool folklore; the tool output itself does not say whether an action landed (C, D) |
| Primary observation | OS accessibility tree only; no OCR, no vision model, no DOM, no pixel matching anywhere (B) | DOM first for the browser (BiDi/Marionette/RDP), AT-SPI for native apps, grim screenshots as universal fallback (B) |
| Web pages | Deliberately not automated ("use agent-browser"); only via the browser's a11y tree (A, B, E) | The main target: real DOM, JS evaluate, exact rects, field values; three protocol lanes plus workspace/folder/pinned-tab internals (B, E) |
| Screenshot capture | PNG; display or X11 window; single-window capture REFUSED on Wayland; fullscreen via xdg portal with a 30 s consent budget, then crop to display; no arbitrary region (B) | grim region/window/monitor capture on Wayland (no consent dialog, real --crop rectangles), logical pixels at scale 1, downscale to 960 px, image_point() maps back; WebDriver screenshot for the browser (B) |
| Element identity / refs | Snapshot-qualified refs @<snapshot_id>:eN, persisted RefMaps (newest 128, capped 1 MB); capture proof (role + native id + stable name/description, never values/bounds); strict re-identification: zero = STALE_REF, two or more = AMBIGUOUS_TARGET; window identity = handle + process-generation token (A, B, C, E) | a11y refs are bare eN sequence numbers, valid only with the snapshot file path; identity is the child-index path + name + role (truncated 120 chars); 90 s TTL; no ambiguity detection; no native id recorded. DOM: no element refs at all, selectors re-issued live. Screenshots: coordinates are the identity (B, E) |
| Completeness accounting | Budget overrun succeeds with complete: false, truncated: true, nodes_observed, per-node subtree_truncated; read failures tri-state Known/Absent/Unknown, never collapsed (B, C) | One top-level truncated flag on a11y observe; skeleton mode has children_count; walk exceptions swallowed bare (except: continue), so a hung app is indistinguishable from an empty one (B) |
| Dense-tree handling | Web-wrapper depth skip (VS Code: 4 to 54-83 ref-able nodes at depth 10); skeleton map then drill-down; find (B, C) | 500-node / 2 s / 80-element caps, depth 12, 100 children per node; no wrapper skip; DOM reads the whole page instead (B, C) |
| Actionability / waits | Pre-dispatch battery (visible, stable, enabled, supported action, policy, editable, hit test over five points) polled up to 5 s auto-wait; occlusion gate three-way; --wait-for / --wait-for-gone post-action waits (default 30 s) (A, C, D) | Desktop lane re-checks geometry/focus before input; a11y act() single-shot with a SENSITIVE check only; RDP lane already polls post-action; no composable wait primitive on the Zen lane (A, B, C, D) |
| Post-action verification | Stateful actions re-read state after delivery; readable contradiction returns ACTION_FAILED with post_action_verification after exactly one attempt; missing evidence alone succeeds as delivered_unverified (C, D) | Verification is model-level re-observation (costs another observation, skipped under time pressure); RDP client and Zen tooling do read-back after write; no tool-level delivered_verified field (C) |
| Batch | One process, ordered JSON array, same dispatch/policy as single commands, one shared deadline, per-entry results with not_started reasons; wait baseline captured BEFORE the preceding action; whole array preflight-validated before entry 1; max 64 entries / 1 MiB input (C, D) | Batching exists inside one call: cu.py act runs up to 32 actions from one observation and returns the final image; browser/a11y act batch known refs; no cross-command batch, no validate-all-first guarantee (C, D) |
| Session model | On-disk container with manifest, snapshot refmaps, append-only JSONL trace segments; session start returns an id but activates nothing; concurrent processes expected; multi-agent --agent-id with per-agent cursors (A, D) | Explicit ownership protocol for the live shared desktop: one session holds the desktop (owner lock), "Computer use active" pill overlay, session-owned cursor lease, physical-Escape cancellation, validated environment tuple, cleanup with restore and recover (A) |
| MCP | Catalog generated from the clap command tree at runtime; every CLI command is a tool; CLI and MCP can never drift (A, D) | scripts/mcp_server.py exposes 8 hand-written Zen-DOM tools with hand-written schemas in a TOOLS list; desktop surface via a separate session MCP; adding a CLI capability does not add an MCP tool (D) |
| Agent docs / discoverability | Skills compiled into the binary, version-matched; help written for agents; docs site serves llms.txt; doc/code drift caught by tests; "a doc that contradicts the code is a defect" (D, E) | Good skill (skill/SKILL.md + 7 reference files) and per-tool docstring manuals, but they live in the repo, are not served by the tools, and are not version-bound; no llms.txt; no drift test between skill text and CLI flags (D) |
| Wayland input | GNOME Mutter private RemoteDesktop D-Bus for keysym injection only; pointer gestures, window control and non-portal screenshots refuse outright on Wayland (A) | Purpose-built Wayland virtual-pointer protocol (drag/wheel/multi-button) and virtual-keyboard protocol with modifier chords and IME/compose handling for Vietnamese text, on Hyprland (A, E) |
| Guardrails | Per-command permission preflight, headless by default with POLICY_DENIED for physical paths, --stdin for secrets, private state root (0700 enforced), Protected Process list, blocked destructive key combos on Linux; NO per-target scoping or allowlist of what may be touched (A, D, E) | Content scope enforced in the tool: RDP tab scope (id + URL pattern, AND semantics), credential-tab denylist ON by default with a logged approval path, single-drive flock, fail-closed profile-marker port-owner check, JSON drive report; zen_cli.py can never attach to the owner's real Zen; cu.py Esc latch; code-exec behind an allowlist plus opt-in (D, E) |

## 2. Final idea table (all 23 ideas)

W = worth 1-5, D = difficulty 1-5, from the council medians
with the adjustments stated in the convergence record. The
binding conditions are part of the idea, not footnotes the
implementer can skip. Round-2 redteam conditions that arrived
after the convergence council are folded in here and marked
(R2).

| ID | Idea (converged form) | Verdict | W | D | Binding conditions | Pilot |
|---|---|---|---|---|---|---|
| I1 | Error codes + disposition + versioned envelope + exit codes, Zen lane first | ADOPT | 5 | 3 | Zen lane first (rdp_client.py first: newest, already JSON, ALL-CAPS prefixes to replace); compat shim for existing consumers; version field + migration notes; cu.py as a sequenced follow-on, never a flag day. C3's correction stands: zen_cli.py already distinguishes parse (2) from runtime (1); only rdp_client.py conflates everything at 2. Benefit magnitude UNPROVEN (no measured retry-error rate); worth 5 is for the verified weakness plus precondition value for I6/I7/I17. (R2) Per-command disposition definitions required first: the F3 pin race and the noSuchActor double-execution do not map cleanly onto five delivery states; a consumer inventory before the shape changes. | None; the Zen lane IS the pilot |
| I2 | Strict ref re-identification, a11y-only scope | PILOT-FIRST | 4 | 4 | Full RefStore version REJECTED: complete-read proof fails on dense apps inside the 500-node / 2 s caps, and more refusals push agents to coordinates. Pilot scope is a11y-only (C3: difficulty 3 for the pilot scope; median 4 is for the wider scope). No benefit claim until the pilot measures it; their changelog anecdotes are not our baseline. (R2) The pilot must be specified before it runs: named apps including a dense one, a pre-stated refusal budget, and per-act cost measurement; a pilot that cannot fail is not an experiment. | Identity-stability probe pass: named app classes (GTK, Qt, Electron); measure the mis-click baseline first, then the refusal rate |
| I3 | Snapshot-qualified refs | ADOPT | 4 | 1 | Additive first: accept qualified refs, warn on bare refs, reject only after a deprecation window; record the snapshot id inside the snapshot file, not only in its filename. (R2) Legacy snapshots without an in-file id are grandfathered, not broken. | None |
| I4 | Batch executor + whole-batch preflight | SPLIT | 3 | 2 | D6 validation half is ALREADY BUILT (C3 stands: cu.py:1472, a11y.py:193), no work. Cross-command executor REJECTED: duplicates the more token-efficient cu.py act model, no measured need. Remaining gap is stale-ref preflight only. Difficulty adjusted 3 to 2: the remaining work is the pilot alone. | Stale-ref preflight pilot: validate refs against a fresh observation before dispatch, on the a11y lane first |
| I5 | Budgeted partial snapshots / skeleton / drill-down / wrapper skip | SPLIT | 4 | 2 / 4 | Accounting half ADOPT now (per-node children_count and cut flags, complete/truncated, skeleton, drill-down; difficulty 2). Walk half PILOT-FIRST (bounded-concurrency GetAll rewrite, difficulty 4); wrapper skip gated to Chromium/Electron provenance only, OFF for native GTK until a census clears it. Their walk numbers (2.1 ms/node, 2.5-3.5x concurrency, 7x cache) do not transfer: Rust async zbus vs our Python synchronous D-Bus under the GIL. (R2) The walk pilot needs a pre-stated success metric; it may return "no win available" and die there. | Walk-cost + wrapper census pilot: measure per-node walk cost on our stack and run the app census before any default is flipped |
| I6 | Post-action verification as a tool duty | PILOT-FIRST | 3 | 2 | NARROWED premise (C3 stands): set_text already verifies (a11y.py:213-214) and act() already re-observes; the RDP "read-back" claim is corrected (navigate re-reads the tab list to re-attach identity, not page state; no verify symbol in rdp_client.py). Remaining gap is click verification plus the disposition field, depending on I1. Worth adjusted 4 to 3: the median 4 scored the broad duty, which no longer exists. Uniform duty REJECTED: doubles observation cost for correlated evidence. (R2) Build opposed until a silent-failure rate for clicks is measured on named apps. | Click verification pilot: one action family (click on a11y act), gated by a measured silent-failure rate for that family |
| I7 | Read-outcome classification | ADOPT (bundled with I1) | 3 | 1 | Ships inside I1, not standalone: vocabulary with no consuming retry loop is shelfware. The disposition field gives the labels a place to live; a retry loop must read them. | None |
| I8 | Perf A/B gate + probe ledger + probes/ | SPLIT | 4 | 2 | Probes/ + ledger habit ADOPT now. Mandatory merge-base A/B gate REJECTED: no CI runner, noisy 1.5-CPU VM, no baseline store; min-of-seven on a noisy VM is not a gate. Advisory on-demand A/B comparison is allowed, non-blocking, with no baseline store until a runner exists. (R2) Ledger rows must cite probe outputs; docs/benchmarks/ exists as a baseline store in shape. | None for the adopted half |
| I9 | Lane interface + capability matrix in doctor | SPLIT | 3 | 2 / 4 | Capability matrix ADOPT now (read-only reporting in doctor, difficulty 2). Unified interface PILOT-FIRST, only after I23 pins behavior, thin adapter over existing entry points only, one lane pair at a time. Big-bang refactor REJECTED. | One-lane-pair interface pilot, after I23, gated also on C1's condition (matrix shows contradictions worth fixing) |
| I10 | Actionability gates + auto-wait | SPLIT | 4 | 2 / 3 | Auto-wait ADOPT now (a11y lane, short cap, poll visible/enabled/stable; matches the RDP lane's existing behaviour; difficulty 2). Full actionability battery PILOT-FIRST only after a hit-test signal is proven on Hyprland; no compositor hit-test primitive exists today. Battery as written REJECTED. | Hit-test signal probe: prove a signal exists (hyprctl stacking, capture-based) and record it in I8's ledger before any battery work |
| I11 | Provider-script sandbox desktops | REJECTED | 2 | 5 | No Linux provider exists; the mission conflict stands (the owner's real Zen session, real tabs, and real logins ARE the workload); the cheap version already exists (throwaway profiles with --marionette and the RDP throwaway profile give a clean browser without a subsystem); a sandbox that looks like the live desktop invites the catastrophic mistake in either direction. C2's time-boxed spike is also not approved: the question it would answer is already answered yes by throwaway profiles. C2 dissents; recorded in section 4 (U1). | None |
| I12 | Append-only trace segments | PILOT-FIRST | 3 | 2 | Form changed by redteam condition: the session-trace subsystem (merge/read commands, new storage contract) is REJECTED. What survives is a one JSONL event-line convention adopted by the noisiest emitters, with grep as the reader. Traces stay local, never committed. Verdict adjusted from ADOPT (C1/C2) to PILOT-FIRST because the remaining form is unproven on any lane. | Event-line convention pilot: drive logs first, one lane, no new commands |
| I13 | Architecture guard | ADOPT | 4 | 1 | Import map defined FIRST: the allowed-import map the check enforces must be written before the check. Machine-value check scoped to a small denylist (profile paths, ports) with an allowlist for fixtures and docs. (R2) The guard must run over skill and docs files too, with the denylist covering personal names: the verified leak in section 6 is in docs, so a code-only guard would pass the repo with both instances in place. | None |
| I14 | Ungate pick4 extents / query / ground + find-style locator | PILOT-FIRST | 4 | 2 | Not a single flip. Re-run the observation timing benches first; ungate query() only; extents stays opt-in until its per-element cost is measured. (R2) Bench must measure coverage too, not only cost (which widget classes silently report no extents); query() and extents-default ungate separately. | Bench re-run + query() ungate experiment |
| I15 | Tri-state reads in AT-SPI walk | SPLIT | 3 | 2 | Root-level incomplete marking ADOPT now (one flag at the walk level). Per-element tri-state REJECTED: output bloat on every observation for a diagnostic nicety. Difficulty adjusted 3 to 2: the adopted half is one flag. | None for the adopted half |
| I16 | Visual debug artifact | SPLIT | 3 | 1 | DOM-rect version ADOPT now (works today, machine-layer only). a11y version PILOT-FIRST after I14 (needs baseline extents). | a11y overlay pilot, gated on I14 |
| I17 | Post-action wait flags for the Zen lane | ADOPT | 4 | 2 | Ships AFTER I1 so the wait-timeout error uses the envelope; the timeout error must preserve the action's own outcome. Write the one-paragraph rule for when to use wait-for vs I6 vs I10. (R2) No default timeout: a 30 s default turns 2 s failures into 30 s failures; fail fast on terminal page states. | None |
| I18 | Tool-served, version-matched guidance | PILOT-FIRST | 3 | 2 | Form changed: embedding/serving guidance is REJECTED (creates a second source of truth). What survives is a version-matched drift check (doctor check that the checked-out skill matches the tool version). FINDING (C3, verified by redteam 2 in a second file): skill/cli-anything/chromium.md:40 contains the user's personal name alongside the endpoint, and skill/cli-anything/zen.md carries machine specifics (ports, profile path, --remote-debugging-port). The scrub list for any served or checked text must cover personal names, not only ports and paths. The name itself is not reproduced anywhere in this report. Remediation is a precondition to revisiting I18, not a follow-on; see section 6. | Drift-check pilot: one CLI, generic text only, scrub list applied |
| I19 | MCP catalog from CLI definitions | REJECTED | 3 | 3 | Generation REJECTED: a shared declarative table to serve 8 tools, no recorded drift incident. KILL discharged only in the sense that the converged form removes the attacked mechanism entirely: no generation. The replacement is a drift test, adopted as a separate small task (worth 3, difficulty 1): assert every zen_dom CLI capability has a corresponding TOOLS entry. | None; the drift test is ADOPT, not a pilot |
| I20 | Interaction lease across input lanes | REJECTED | 3 | 3 | Lease as written REJECTED: a dispatch-only lease does not cover the across-wait race, and one stale lock wedges all input lanes at once. C3's correction stands and weakens the premise: cu.py already holds a global desktop.lock (cu.py:1993-1995); the gap is only that no Zen lane takes it, and no interleaving incident is recorded. KILL discharged only in the sense that the converged form removes the attacked mechanism entirely: no new shared lease file. The replacement is RDP lock hardening (lock-holder identity + stale detection) plus documenting the existing lock map, adopted as a small task (worth 2, difficulty 1). Decided by rule over council dissent (all three councils piloted the lease); see section 4. | None; the substitute is ADOPT, not a pilot |
| I21 | Blocked key-combo list | ADOPT | 4 | 1 | Verify each combo against the actual Hyprland keybindings first; log refusals so a false block is diagnosable. (R2) A conservative subset (VT-switch, SysRq, Ctrl+Alt+Backspace/Delete) can land without the laptop check; the full list waits for the Hyprland binding check, which is a laptop-side step. | None |
| I22 | Secure-field redaction contract | ADOPT | 4 | 2 | NARROWED scope (C3 stands): the a11y half is already safe (describe() collects no field values, a11y.py:80 comment). The gap is DOM/RDP only: DOM evaluate can read input.value; the RDP drive report carries every tab's URL and title. Form is a narrow, honest contract: redact only where the tool controls the bytes, and document in the same breath that evaluate() is out of scope and the agent must not read secure values (skill prose). The full "contract" implying coverage is REJECTED. | None |
| I23 | Conformance contract tests | SPLIT | 4 | 3 | Browser lanes (BiDi, Marionette, RDP) on one fixture page PILOT-FIRST. AT-SPI half REJECTED until a fixture app exists: no native app with a stable a11y tree launches headlessly on this VM today. C3's correction stands: the R3-100 webdriver-disagreement anecdote is UNVERIFIED (the file checked is about port rules) and must not be cited as established; the idea stands on the verified lane divergence. | Browser-lane conformance pilot: one fixture page, two lanes first |

Counts: 7 whole-ADOPT (I1, I3, I7, I13, I17, I21, I22), 6
split with an ADOPT half (I5, I8, I9, I10, I15, I16), 5
whole PILOT-FIRST (I2, I6, I12, I14, I18) plus 3 pilot halves
(I4 stale-ref preflight, I9 interface, I23 browser lanes), 3
whole-REJECTED (I11, I19, I20).

## 3. Do-first list (ordered)

1. **I13** architecture guard (4/1). Mechanical defence of the
   principles; also makes I12's local-only trace rule
   enforceable rather than aspirational. Import map first, and
   the guard covers skill and docs files too (section 6).
2. **I21** blocked key-combo list (4/1). One bad chord can kill
   the owner's session; verify combos against Hyprland first.
3. **I3** snapshot-qualified refs (4/1). Additive first, with a
   deprecation window; id inside the file.
4. **I1** envelope + disposition, Zen lane first (5/3).
   Precondition for I6, I7, I17; compat shim; cu.py later.
5. **I8** probes/ + probe ledger (4/2). The measurement layer
   every other pilot's savings claim depends on; land before
   the I2 and I10 pilots, not after them.
6. **I17** post-action wait flags (4/2). After I1; the skill
   already bans fixed sleeps, so the tool must supply the
   primitive.
7. **I22** secure-field redaction, DOM/RDP only (4/2). A
   password value is one careless evaluate away from a report
   file.
8. **I5** accounting half (4/2). Per-node completeness flags,
   skeleton, drill-down; cheap, ungated.
9. **I10** auto-wait half (4/2). a11y lane, short cap; closes
   the inconsistency with the RDP lane's polling.
10. **I16** DOM-rect debug artifact (3/1). One script over
    existing outputs; machine-layer only.

Next tier, immediately after: I9 capability matrix (read-only,
difficulty 2) and I15 root-level incomplete marking
(difficulty 2). Sequencing constraints: I1 before I6, I7
(bundled), I17; I8 before the I2 and I10 pilots; I14 before the
I16 a11y half; I23 before the I9 interface pilot; I13 early.

## 4. Rejected list (with reasons)

Whole ideas and rejected halves, in the convergence's order.
A rejected idea is not to be revived as "future work" without
new evidence: a Linux provider plus a measured
throwaway-desktop workload (I11), a recorded MCP-drift
incident (I19), a recorded interleaving incident (I20).

- **I11** sandbox desktops (build): no Linux provider exists,
  the mission conflict stands, and throwaway profiles already
  answer the need.
- **I19** MCP catalog generation: 8 tools, no recorded drift
  incident; replaced by a drift test.
- **I20** cross-lane interaction lease as written: dispatch-only
  coverage misses the across-wait race and one stale lock
  wedges all lanes; replaced by RDP lock hardening.
- **I4** cross-command executor: duplicates the more
  token-efficient cu.py act model with no measured need.
- **I5** concurrent-walk rewrite + wrapper-skip-by-default: Rust
  async numbers do not transfer to Python synchronous D-Bus;
  measure and census first.
- **I6** uniform post-action verification duty: doubles
  observation cost for evidence correlated with the failure it
  checks; narrowed to click + disposition.
- **I8** mandatory merge-base A/B gate: no CI runner, noisy VM,
  no baseline store; probes + ledger adopted instead.
- **I9** unified lane interface as a big-bang refactor:
  difficulty-4 rewrite with no conformance harness to catch
  regressions; thin adapter only, after I23.
- **I10** full actionability battery as written: no Hyprland
  hit-test primitive, and the lease blocks the shared seat;
  narrow auto-wait adopted instead.
- **I12** session-trace subsystem (merge/read commands): a
  seventh format with no measured reconstruction need;
  event-line convention piloted instead.
- **I15** per-element tri-state everywhere: output bloat on
  every observation for a diagnostic nicety; root-level marking
  adopted instead.
- **I18** embedding/serving guidance in tools: creates a second
  source of truth; drift check piloted instead.
- **I22** full "contract" implying coverage: evaluate() and
  screenshots are out of scope; narrow honest contract adopted
  instead.
- **I23** AT-SPI half: no fixture app exists that launches
  headlessly on this VM; browser lanes piloted instead.
- **I2** full RefStore version: the complete-read proof fails on
  dense apps inside the current caps; a11y-only pilot instead.
- **I14** single-flip ungate: premature without re-run benches;
  measured experiment instead.
- **I7** standalone: vocabulary with no consuming retry loop is
  shelfware; bundled into I1.
- **I1** all-lane big-bang: breaks every consumer of every CLI's
  output in one change; Zen-first only.
- **I13** as a check without an import map: the boundary it
  checks would be undefined; map first, then the check. (Form
  rejected, not the idea.)

Not-recommended list (register section 4): all 12 entries are
upheld by the debate, none overturned. Mutter RemoteDesktop
input; portal screenshots as a replacement for grim on Hyprland
(E's "gap" is portability, not capability on Hyprland);
their no-web-automation stance (our DOM-first priority stands
unanimously); cross-platform ports; FFI rewrite / in-process
library (C1's qualification: revisit only if Python
control-plane latency becomes the binding constraint on task
time, which no lane's measurements show today); sandbox as
shipped (macOS-only, and its generic variant I11 is now
REJECTED); stateless session replacement (upheld unanimously);
--headed mode flag; dry-run mode (I1 is the cheaper, more
honest substitute); XTest / xdotool-class input (conflicts
with the no-ydotool rule); app-agnostic purity rule imported
wholesale (our Zen specialisation is the opposite by design);
distribution / product machinery wholesale (a deliberate
non-goal at this scale: one user, one laptop, git clone by
design). Full CI likewise: I8 plus I23 are the measurement
layer this project needs, not a CI replica.

## 5. The debate record

Round 1 scored every idea on worth 1-5, difficulty 1-5, and
verdict ADOPT / PILOT-FIRST / REJECT. The three council
scores, medians in the convergence file:

- Council 1 (value): 10 ADOPT, 9 PILOT-FIRST, 2 REJECT (I11,
  I19). Top 5: I1, I8, I13, I21, I3. Bottom 5: I11, I19, I16,
  I9, I15.
- Council 2 (feasibility and risk): 13 ADOPT or adopt-half,
  the rest PILOT-FIRST; no whole REJECT, but I11 allowed only
  as a time-boxed spike with kill criteria. Top 5: I21, I13,
  I3, I1, I17. Bottom 5: I11, I9, I2, I5 full scope, I19.
  Split several ideas into a cheap adopt-now half and a hard
  pilot half (I4, I5, I9, I10).
- Council 3 (evidence): 7 ADOPT, 13 PILOT-FIRST, 1 REJECT
  (I11). No worth-5: no idea carries a measured saving on our
  side. Top 5: I13, I21, I3, I17, I8. Bottom 5: I11, I6, I9,
  I4, I2.
- Redteam 1: 4 SURVIVES (I3, I13, I16, I21), 16 WOUNDED, 3
  KILL (I11, I19, I20). Five most dangerous if adopted as
  written: I11, I9, I20, I5 as written, I2 full RefStore.

Round 2 convergence (council) applied three rules: council
3's evidence corrections stand unless code refutes them (none
was refuted); a redteam KILL stands unless the converged form
removes the attacked mechanism entirely; worth and difficulty
start from the council medians, adjusted only where a
correction or a condition changes the idea itself. Its
dispute settlements: I11 REJECTED including C2's spike (order
reversed: measure a throwaway-desktop workload first, then
discuss a spike); I19 and I20 KILLs discharged only by
removing the attacked mechanism entirely, each replaced by a
small adopted task; I1 ADOPT Zen-first (the Zen lane IS the
pilot, a separate pilot phase adds process without evidence);
I8 split (probes + ledger ADOPT, mandatory gate REJECTED);
I2 PILOT-FIRST a11y-only with benefit UNPROVEN; I5 split
(accounting ADOPT now, walk PILOT); I6 narrowed to click +
disposition; I18 as a drift check with the finding in
section 6.

Round 2 redteam took its best remaining shot at the consensus
and conceded I1 (Zen-first), I21, I8's ledger, and I22, and
conceded the I5 accounting half; it stayed opposed to I13 as
specified (code-only guard, while the verified leak is in
docs), I3 as specified (reject-bare-refs breaks stored
evidence), I17 (no default timeout, no fail-fast, no
sequencing), I14 (bench measures cost, not coverage), I2's
pilot (no spec), and the I5 walk pilot (no success metric).
Its conditions are folded into section 2 as (R2) and are
binding: the I13 guard covers docs, I3 grandfathers legacy
snapshots, I17 carries no default timeout, I14 ungates
query() and extents separately, the I2 pilot is specified
before it runs, and the I6 build waits for a measured
silent-failure rate. It held its KILLs on I11, I19 as
generation, and I20, and accepted the drift test, the RDP
lock hardening, and the I8 advisory pilot as replacements.
It also named nine things a dishonest synthesis would hide;
the checks are, in short: the like-with-like caveat; their
measurements presented as our savings; WOUNDED conditions
demoted to footnotes; the three KILLs laundered into "future
work"; council disagreement averaged into single scores; the
four "already built" premises presented as new builds; the
register corrections; savings stated without evidence status;
and the round-2 conditions dropped from the verdicts. This
report answers each of those checks in place.

What remains UNRESOLVED:

- **U1. I11 spike (C2 dissents).** C2 would allow a time-boxed
  nested-Hyprland spike with kill criteria; C1, C3, and the
  redteam say kill entirely. Needs an owner/coordinator call,
  and the order is reversed: a throwaway-desktop workload of
  substance must be measured first.
- **U2. I1 worth 5 vs 4 (C3 dissents on the number).** C3 caps
  worth at 4 because the benefit magnitude is UNPROVEN (no
  measured retry-error rate); C1/C2 hold 5 for the verified
  weakness plus precondition value. The verdict (ADOPT,
  Zen-first) is agreed; the number is not. Settles when a
  pilot measures the retry-error rate on the Zen lane.
- **U3. I2 refusal-rate budget (no one has named a number).**
  The redteam demands a stated budget, the councils say
  "measure first"; the pilot design must name X before it
  runs.
- **U4. Whether any Python-side walk speedup exists under the
  GIL (redteam vs C2/C3).** C2/C3 price the walk at difficulty
  4 assuming a win exists; the redteam says the cited numbers
  do not transfer. The I8 probe must measure per-node walk
  cost first; the walk pilot may return "no win available" and
  die there.
- **U5. I9 interface trigger (C1 vs redteam).** C1's trigger is
  "only if the matrix shows contradictions worth fixing"; the
  redteam's is "only after I23 pins behavior". The convergence
  applies both gates; whether both must pass or either
  suffices is not settled.

Decided by rule over council dissent (not unresolved, but the
dissent is recorded): I20 (all three councils piloted the
lease; overruled by C3's own evidence correction plus the
redteam KILL; the substitute preserves C2's stale-lease
requirements as design constraints on the RDP lock hardening).
I12 (C1/C2 ADOPT, C3 PILOT; converged to PILOT-FIRST of the
convention form after the redteam KILL removed the subsystem).

## 6. Open finding: personal name in skill files

Council 3 verified, and redteam 2 independently re-verified,
that the user's personal name appears in
skill/cli-anything/chromium.md:40 alongside the endpoint, and
that skill/cli-anything/zen.md:42 carries machine specifics
(ports, profile path, --remote-debugging-port). A second
instance in zen.md was found by the redteam. The name is not
reproduced anywhere in this report or in any debate file, per
the project's absolute privacy rule.

Plainly: the repo is currently in violation of its own
no-personal-info rule, in the exact files I18 proposes to
serve, so I18 would launder an existing violation into tool
output, transcripts, and logs. The scrub list as specified
(ports and paths) would not catch a name, and I13's code-only
guard would not either; both ideas share one blind spot, and
the violation lives in it.

Status: OPEN. Owner: the coordinator (Muse), to fix and to
verify by a census of skill/ and user-facing docs. Remediation
(remove the name from both skill files, census skill/ and
user-facing docs) is a precondition to revisiting I18, not a
follow-on. This study did not edit those files: the fix
belongs to the coordinator's lane, and a parallel edit here
would risk conflicting with it. The I13 guard, when built,
must run over skill and docs files too, with its denylist
covering personal names.

## 7. Evidence corrections applied, and what is still UNPROVEN

Council 3 checked every idea's premise against the code in
~/workspace/computer-use-wayland (main) and
~/workspace/cuw-fixreview (for scripts/zen-rdp/), and the
convergence re-checked the two load-bearing claims. These
corrections stand and are applied throughout this report:

- **I4/D6 premise partly wrong.** Whole-batch validation
  already exists before dispatch (cu.py:1472 before the loop
  at 1477; a11y.py:193). Only stale-ref preflight plus the
  executor are new. The 54x figure is ours and verified
  (docs/clone2-dom-grounding-20261122.md:128) but evidences
  DOM rect round trips, not the executor. It is the one
  measured saving in the whole study.
- **I6 premise partly wrong.** a11y set_text already re-reads
  and fails on mismatch (a11y.py:213-214) and act() already
  returns a full after re-observation (222-227). The real gap
  is click verification plus the disposition field only. RDP
  "read-back" is tab-identity re-attach, not outcome
  verification.
- **I1/D3 sentence wrong for zen_cli.** It distinguishes parse
  (argparse exit 2) from runtime (return 1); only
  rdp_client.py conflates everything at 2.
- **I2 scope problem.** Strict re-identification needs a
  complete window read, but observe() caps at 500 nodes / 2 s
  (a11y.py:83-87), so the full scope depends on I5 walk work
  or refuses constantly on dense apps. Benefit ("largest
  accuracy payoff") is UNPROVEN: no baseline wrong-element
  rate on our side; the twin-control evidence is theirs.
- **I5 transfer risks.** Their 2.1 ms/node and 4 s at 2,000
  nodes cannot occur in our capped walk; wrapper-skip 4 to
  54-83 is their VS Code probe, unmeasured here. Gate it to
  Chromium/Electron provenance pending a census.
- **I20 corrected.** cu.py already holds a global desktop.lock
  (1994-1999); the gap is specifically that zen_cli/zen_dom/
  rdp_client never take it.
- **I22 corrected.** a11y already collects no field values
  (a11y.py:80); the gap is DOM/RDP only.
- **I18 worse than stated.** skill/cli-anything/chromium.md:40
  contains the user's name alongside machine specifics; the
  scrub list must cover personal names. See section 6.
- **I23 anecdote UNVERIFIED.** The R3-100 file checked is
  about port rules, no webdriver disagreement; lane-E-reported
  only. The idea stands on the verified lane divergence.
- **"~691 reports" unpinned.** 324 files on main, 762 entries
  on fix-review.
- **All other benefits UNPROVEN in magnitude.** No idea except
  I4's already-banked 54x carries a measured saving on our
  side. Their walk ledger, wrapper skip, and changelog
  evidence do not transfer as savings.

Next steps, in order: the coordinator decides U1 (I11 spike)
and the owner of the section 6 remediation; the do-first
list in section 3 is the implementation order, with the
sequencing constraints stated there; each pilot names its
measurement before it runs, and a pilot that returns "no win
available" (I5 walk, U4) dies there. No personal information
in this document.
