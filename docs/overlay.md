# Central overlay control

## Rule

The computer-use pill ("Computer use active") must ALWAYS show whenever
ANY AI controls the machine, whatever the method: DOM/BiDi, CLI-ified,
shell, computer-use driving, anything. The user must always know an AI
is driving. Before, the pill only showed during a computer-use session
with direct mouse driving, so DOM/CLI/SSH work looked like nothing was
happening.

## Usage

Every agent calls acquire BEFORE it starts controlling, and release when
it is done. The pill shows the controlling agent and method.

```sh
python3 scripts/overlay.py acquire --agent Muse --method BiDi
python3 scripts/overlay.py acquire --agent Codex --method DOM
python3 scripts/overlay.py status
python3 scripts/overlay.py release --agent Muse
python3 scripts/overlay.py release --agent Codex
```

Python agents can use the helper instead:

```python
from overlay import hold
with hold('Muse', 'BiDi'):
    ... # control the browser via BiDi
```

## Reference counting

The pill hides only when ALL holders released. Acquiring twice with the
same agent name updates the method, it never double counts. Holders are
recorded in `~/.cache/agent-computer-use/overlay/holders.json` under a
file lock, so concurrent agents are safe.

`--pid` is optional: when given, a dead pid is pruned automatically.
Always release in a finally block; `overlay.py prune` is not a command,
dead pids are pruned on every status call.

## Session awareness

If a computer-use session is live, its own pill already shows, so the
daemon forwards show/label to the session indicator instead of spawning
a second one. If the session dies while holders remain, the daemon
spawns its own indicator and takes over. A monitor thread polls session
liveness every 2 seconds. If a session starts while the daemon owns the
pill, the daemon hands over to the session.

## Label

The pill text is the latest acquirer's `agent via method`, for example
"Muse via BiDi", max 40 printable ASCII chars. Implemented as a `label`
command in `native/indicator.c` (draw uses a mutable label string) and
passed through `scripts/indicator.py` (socket serve/request). A label
sent while the pill is hidden is stored and drawn on the next show.

## Flicker

The 10 Hz flicker from 20/11 has no in-repo code path that can produce
it during idle driving (redteam worker4). The indicator side fragility
is fixed: `painted()` returns early on idle paints instead of
re-committing full-surface damage (commit f6d73b0), duplicate hide/show
is suppressed, and the native binary reports paint/commit metrics every
second to stderr, so an idle repaint loop is now measurable. If the
pill still flickers, capture the daemon log and count
`surface_commits` per 1 s window while idle: near zero means the
indicator is innocent and the loop lives in the compositor or plugin.
