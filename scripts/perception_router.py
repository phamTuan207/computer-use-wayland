"""P1 DOM/a11y default router (FINAL direction section 1.2 P1, step 5).

One function returns the perception source. Before this module two
perception stacks existed with no routing rule, so work drifted to
the worse one (screenshots, which work everywhere) instead of the
better one (DOM, which needs setup). The router is code, not
convention: a per-target priority table, coverage-based fall-through,
a fail-closed screenshot fallback, and a log line on every decision
so drift back to screenshots is visible instead of silent.

Routing rules (all eight final positions agree on these):

- The router routes on COVERAGE, not just target type. A backend
  returning an empty harvest (zero elements) or a truncated a11y
  tree falls through to the next backend, never proceeds on a
  partial inventory. A probe that raises is treated as an
  unavailable backend, not an error: the router never raises.
- Zen chrome UI routes to screenshots as a DECIDED boundary (P8 is
  CLOSED, BLOCKED: Marionette chrome context is unsupported without
  a Zen restart). No probe result can move a chrome target to DOM.
- Everything else fails closed to the labeled screenshot fallback
  when no backend returns complete coverage.

Target kinds: 'zen-content' (a web page in Zen), 'zen-chrome'
(Zen browser UI), 'chromium-content' (a page in Chromium/Brave via
CDP), 'native-app' (a desktop app via AT-SPI), 'unknown'.

A probe is a callable target -> coverage dict or None. Coverage is
{'elements': int, 'truncated': bool}: complete coverage means at
least one element and not truncated. None means the backend is
unavailable (no session, no port, no tree). The router itself never
opens a browser session: probes are supplied by the caller, so the
router is unit-testable without a live browser.

Every decision emits one JSON log line (event
"perception_routing") through `emit`, defaulting to stderr, and is
also appended to ROUTING_LOG for in-process inspection.
"""
import json
import sys

SOURCES = ('dom-zen', 'dom-chromium', 'a11y', 'screenshot')

# Per-target priority table. Zen chrome UI has exactly one entry:
# the decided P8 boundary, recorded here so no caller can re-open
# it by supplying a different backend order.
_PRIORITY = {
    'zen-content': ('dom-zen', 'screenshot'),
    'zen-chrome': ('screenshot',),
    'chromium-content': ('dom-chromium', 'screenshot'),
    'native-app': ('a11y', 'screenshot'),
    'unknown': ('screenshot',),
}

ROUTING_LOG = []


def _default_emit(record):
    print(json.dumps(record, ensure_ascii=False), file=sys.stderr)


def _coverage_problem(source, coverage):
    """Why a backend's coverage is unusable, or None when complete.

    An empty harvest (zero elements) and a truncated tree are both
    partial inventories: proceeding on either would ground from a
    list the backend itself says is incomplete.
    """
    if coverage is None:
        return 'backend unavailable'
    if not isinstance(coverage, dict):
        return 'coverage is not an object'
    if coverage.get('truncated'):
        return 'truncated inventory'
    elements = coverage.get('elements')
    if not isinstance(elements, int) or isinstance(elements, bool):
        return 'coverage has no element count'
    if elements <= 0:
        return 'empty harvest'
    return None


def route_perception(target, probes=None, emit=None):
    """Route one perception target to its source.

    target is a dict with at least 'kind'. probes maps a source
    name to a callable returning a coverage dict (or None when the
    backend is unavailable). emit receives the decision record;
    the default writes one JSON line to stderr. Returns the
    decision dict: {'source', 'target_kind', 'fell_through':
    [{'source', 'reason'}], 'reason', 'coverage'}. The router
    never raises: any unexpected input fails closed to the
    screenshot fallback with the reason recorded.
    """
    emit = emit or _default_emit
    probes = probes or {}
    kind = target.get('kind') if isinstance(target, dict) else None
    if kind not in _PRIORITY:
        kind = 'unknown'
    fell_through = []
    coverage = None
    source = 'screenshot'
    reason = None
    for candidate in _PRIORITY[kind]:
        if candidate == 'screenshot':
            source = 'screenshot'
            if kind == 'zen-chrome':
                reason = ('decided boundary (P8 CLOSED): Zen chrome UI '
                          'is screenshot-only; the Marionette chrome '
                          'context is unsupported without a Zen restart')
            elif fell_through:
                reason = ('fail-closed fallback: no backend returned '
                          'complete coverage')
            elif kind == 'unknown':
                reason = ('fail-closed fallback: unknown target kind, '
                          'no backend table applies')
            else:
                reason = 'fail-closed fallback'
            break
        probe = probes.get(candidate)
        if probe is None:
            fell_through.append(
                {'source': candidate, 'reason': 'no probe supplied'})
            continue
        try:
            coverage = probe(target)
        except Exception as exc:
            fell_through.append(
                {'source': candidate,
                 'reason': 'probe raised: ' + str(exc)[:200]})
            coverage = None
            continue
        problem = _coverage_problem(candidate, coverage)
        if problem is not None:
            fell_through.append({'source': candidate, 'reason': problem})
            coverage = None
            continue
        source = candidate
        reason = 'complete coverage: %d elements, not truncated' % (
            coverage.get('elements'),)
        break
    decision = {'source': source, 'target_kind': kind,
                'fell_through': fell_through, 'reason': reason,
                'coverage': coverage if source != 'screenshot' else None}
    record = {'event': 'perception_routing',
              'target_kind': kind, 'source': source,
              'fell_through': fell_through, 'reason': reason}
    ROUTING_LOG.append(record)
    emit(record)
    return decision
