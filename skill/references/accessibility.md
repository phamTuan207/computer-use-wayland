# Native accessibility

Observations include positive native `pressed`, `checked`, `selected` and `expanded` flags when
reported by AT-SPI. Verify the relevant app result with these flags or another independent
app signal before requesting a screenshot. Pinta's toggle tools report `pressed`, for example.
Callbacks can be asynchronous: if the immediate after-snapshot has not updated, re-observe
without replaying input. A missing flag is not a claim of support for that property.


```bash
"$CU" a11y apps
"$CU" a11y observe --pid EXACT_APP_PID
"$CU" a11y observe --pid EXACT_APP_PID --skeleton
"$CU" a11y drill REF --snapshot /path/returned.json
"$CU" a11y act --snapshot /path/returned.json --actions /tmp/actions.json
```

`--skeleton` lists structure, not only actionable nodes: each listed item carries its tree
`path` and `children_count`, and `truncated` marks a subtree larger than the bounds. `drill`
returns a skeleton observation of one element's subtree, using a ref from that snapshot.
Snapshots expire 90 seconds after capture; `drill` and `act` refuse a stale one. Elements may
report `editable` and `disabled`.

Actions: `{"type":"click","ref":"e2"}` or `{"type":"set_text","ref":"e1","text":"Tiếng Việt 🐱"}`. Setter verifies full text but does not log field contents. A native button must expose `click`, `press` or `toggle`; an entry's `activate` is never substituted for a click. Snapshot is bounded to 80 actionable elements, 500 visited nodes, depth 12 and roughly 2 seconds plus outstanding DBus calls. If app absent / tree empty / unsupported, use desktop. Do not change accessibility settings without task-specific need. A11y tree paths are rechecked by name and role; identical replacement widgets cannot be distinguished solely by that check.

`act` shares the session's re-observe gate: after a transient guard refusal, run a fresh
desktop `observe` first. The result reports `completed` and a fresh `after` observation; if
that capture fails, `after_unavailable` and `capture_error` are set and the original error
and count are kept. Never replay uncertain input.
