# Chromium

```bash
CU=computer-use
"$CU" browser start
"$CU" browser tabs
"$CU" browser observe --target EXACT_TAB_ID
"$CU" browser act --target EXACT_TAB_ID --snapshot ID_FROM_OBSERVE --actions /tmp/actions.json
```

`start` reuses a loopback CDP endpoint if available; otherwise opens Chromium with a dedicated persistent profile at `~/.local/share/agent-computer-use/browser-profile`. No `--no-sandbox` or wildcard remote origin. This profile has its own logins. Do not assume it is the user's other browser session. `--endpoint http://127.0.0.1:PORT` selects another locally exposed CDP endpoint. Standalone CLI commands open one CDP connection per command; inside a session relay the worker reuses a connection only while endpoint, tab and page URL are unchanged and the transport is healthy, and any failure disposes it.

`observe` returns up to 80 interactive elements with short names and refs, visible controls first. All form values and editable contents are redacted; checked state remains available. Screenshots and page labels may still contain private data. Use `--max-elements 16` on observe/act when a smaller output is sufficient (range 1..80, default 80); increase it if the target is absent, never guess a ref. Long page contents and base64 screenshots are not printed. Add `--image` when needed; an image file path is returned. DOM operation is top-document only, excludes canvas internals and does not enumerate shadow roots.

Browser actions:

```json
[
 {"type":"fill","ref":"e1","text":"Tiếng Việt 🐱"},
 {"type":"click","ref":"e2"},
 {"type":"assert","selector":"#status","text":"Saved","timeout_ms":1000}
]
```

`click`, `fill`, `assert`: use a ref or an exact single-match CSS `selector`. `fill` uses trusted input and verifies the resulting value. `assert` accepts `text` (substring), `value` (exact), `checked` (boolean), or defaults to nonzero element width; timeout max 3000 ms. `key`: `keys` array (`Ctrl`, `Alt`, `Shift`, `Meta`, `Enter`, `Tab`, `Escape`, arrows, editing keys, one character). `scroll`: `dy`, optional `dx`,`x`,`y` in viewport CSS pixels. `wait`: `ms` max 2000. Navigation ends the old snapshot; snapshots also expire 90 seconds after capture, and further input is refused until you observe again. Result includes a fresh `after` snapshot.

`set_value` also takes one `ref` or exact `selector` plus `text`. Prefer it for
text-like inputs (`text`, `search`, `tel`, `url`, `email`) and textareas: it
avoids focus-dependent typing, uses the native value setter and verifies the
value, but dispatches synthetic, untrusted `input`/`change` events. Follow it
with an assertion on the app's result. On failure the result may carry
`mutation_may_have_occurred: true` (a partial change may have landed): inspect
state, never replay. Use `fill` when trusted keyboard events are required and the
target is controlled.
See [field routing evidence](../../docs/optimization-experiments.md#browser-field-assignment-with-routing-faults).

Snapshots list interactive controls, not arbitrary status messages. A successful
`act` and its `after` alone do not prove that Save succeeded. Use a known app-result
assert; if the result is not yet understood, request `--image` and inspect it.
Do not invent a status selector or expected message to avoid that check.

When the next targets and success condition are known, keep `fill`, `click` and
the result `assert` in one `act`, as above. A fixed `wait` cannot establish that
the application finished. Use an exact `value` assertion for field contents and
a specific result condition for an action; the default width assertion only
checks element presence. Split at unknown layout changes or navigation, and stop
after failure without replaying input. This recipe reduces request roundtrips;
it does not change the input backend or prove model-token savings. Reproduction
and limitations: [task experiments](../../docs/optimization-experiments.md).

### Scope the observation: `browser observe --scope`

Opt-in, one read, never sticky:

```bash
"$CU" browser observe --target EXACT_TAB_ID --scope '#task'
```

`--scope` is valid on `observe` only. The value is a CSS selector that must match
exactly one top-document element; it must be non-empty and at most 1024 UTF-16
units. The selector is resolved read-only before the snapshot is replaced, so a
failed match leaves the previous snapshot id and refs usable — there is no
fallback to the whole page.

The result enumerates only the interactive descendants of that root, plus the root
itself when it is interactive. Iframes inside the scope are counted but not
traversed. `scoped: true` in the result marks it; `title` and `url` remain whole
page metadata. `--image` still captures the full viewport.

Scope is **not** an input, security or privacy boundary: existing selectors can
address anything on the page, and every action guard is unchanged. This is worth
using when the page carries many irrelevant controls, because the observation is
what you have to read.

### Scope the successful after-snapshot

When the next browser step is still in one panel, ask `act` for its new refs there:

```bash
"$CU" browser act --target EXACT_TAB_ID --snapshot ID_FROM_OBSERVE \
  --actions /tmp/actions.json --after-scope '#task'
```

This scopes only a **successful** `act` after-snapshot. A failed action keeps a
whole-page diagnostic. If the panel is gone or no longer unique after the action,
the result says `after_unavailable`; observe again before further input. The
default `act` still returns the whole page. `--after-scope` cannot combine with
`--no-after`; use `--no-after` when a final assert already proves completion and
no next refs are needed. `--image` still captures the full viewport.

### Skip the final snapshot: `browser act --no-after`

Opt-in. The same recipe, with the result `assert` last:

```bash
"$CU" browser act --target EXACT_TAB_ID --snapshot ID_FROM_OBSERVE \
  --actions /tmp/actions.json --no-after
```

On a successful `act` the result carries `after_skipped: true` and no `after`
snapshot, so the response is much smaller. An execution failure still attempts a
diagnostic `after` snapshot (or sets `after_unavailable`) and never sets
`after_skipped`; preflight failures happen before input. Omitting the flag keeps
today's behaviour.

Because that assert is now the only evidence of success, the last action must
be an `assert` with a condition it really evaluates. `assert` resolves one
predicate in `value` > `text` > `checked` order and ignores the rest, so:

- `value`: a string; `""` is allowed and means "the field is empty".
- `text`: a non-empty string. An empty `text` proves nothing.
- `checked`: a boolean.
- none of these — the default nonzero-width check — is refused.

`--no-after` is rejected on `observe`, `tabs` and `start`, cannot be combined
with `--image`, and is refused before any network or input effect if the final
action is `wait`, `click` or `fill`, or if `actions` is empty.

There is no automatic observation, retry or replay. If the layout or the page
changes after the assert, the previous snapshot is spent: run `observe` again
before any further input. Split at unknown layout changes and navigation as
usual. This reduces response size; it is not a claim about billed model tokens.
