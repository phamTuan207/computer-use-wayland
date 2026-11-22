#!/usr/bin/env python3
"""Held-out fixture run for C5-STEP9: the landed (b1) program against the
two-vision benchmark fixture (tests/two_vision_fixture.html, batch 8,
locked by the C4 bench manifest). The fixture is a task this worker did
not design: a fake clone thread with #msg-input (aria-label Message),
Enter appends a .bubble, window.__bubblePresent(text) verifies it.

Runs on the VM like scripts/s2_flip_live.py and reuses its transport:
Harness.broker (step-8 broker) for tabs + observe, and
Harness.oneshot_code_exec for the program. The (b1) program is the
landed 4-action shape (set_value, focus, key Enter, assert) with the
bubble assert selector swapped to the fixture's '#thread
.bubble:last-child' (the live-thread selector does not exist on the
fixture). Verification is the fixture's own __bubblePresent /
__sentBubbles, NOT the muse-specific V12/count helpers.

Also covers the step-9 gate's no-double-send-on-retry item: after the
send, a retry attempt runs the pre-send bubble check, finds the message
already present, and refuses to send (outcome 'already-sent'); the
bubble count stays 1. A 10s delayed recount closes the run.
"""
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'scripts'))
import s2_flip_live  # noqa: E402

FIXTURE_URL = ('file:///home/james/computer-use-wayland/tests/'
               'two_vision_fixture.html?clone=1')
FIXTURE_SHA = ('147494cda4c6ae24a51ced03ccdfb3fc5a79a1bbab56dcdfc5afb4f72fba6'
               'cbf')
RUN_NO = 91
MESSAGE = 'C5-HELDOUT-R91-CHROMIUM-IGNORE-TEST'
WORKDIR = Path('/tmp/c5-heldout-91')
LAPTOP_SEED = '/home/james/c5-step9-run/c5-fixture-seed.mjs'
LAPTOP_EVAL = '/home/james/c5-step9-run/c5-eval.mjs'


def main():
    t0 = time.monotonic()
    # The fixture's bubble selector, not the live thread's.
    s2_flip_live.BUBBLE_ASSERT_SELECTOR = '#thread .bubble:last-child'
    h = s2_flip_live.Harness(str(WORKDIR), RUN_NO, chromium_set_value=True,
                             message_prefix='C5-HELDOUT')
    endpoint = s2_flip_live.BROWSERS['chromium']['endpoint']
    results = {'run': RUN_NO, 'fixture': FIXTURE_URL,
               'fixture_sha256': FIXTURE_SHA, 'message': MESSAGE,
               'model_calls': 0, 'program_variant': 'set_value'}
    try:
        rc, out, err, _wall = h.ssh(
            'node %s %s %s' % (LAPTOP_SEED, endpoint, FIXTURE_URL),
            'seed-fixture', timeout=90)
        if rc != 0:
            raise RuntimeError('fixture seed failed rc=%d: %s' % (rc, (out + err)[:300]))
        tab_id = out.strip().splitlines()[-1].strip()
        results['target_id'] = tab_id
        lease = '/home/james/.cache/agent-computer-use/c5-heldout-91.lease'
        owner = 'c5-heldout-91'
        h.ssh('rm -f ' + lease, 'lease-cleanup', timeout=30)
        h.broker_start(lease, owner)
        try:
            res, _seq = h.route_browser(lease, 1, 'chromium', tab_id)
        finally:
            h.broker_finish(lease)
        results['observe'] = res
        if res.get('outcome') != 'routed':
            raise RuntimeError('route failed: %s' % res.get('error'))

        def ev(expr):
            rc2, out2, err2, _w = h.ssh(
                'node %s %s %s %s' % (LAPTOP_EVAL, endpoint, tab_id,
                                      __import__('shlex').quote(expr)),
                'eval', timeout=60)
            if rc2 != 0:
                raise RuntimeError('eval failed rc=%d: %s' % (rc2, (out2 + err2)[:300]))
            return json.loads(out2.strip().splitlines()[-1])

        results['pre'] = {
            'bubble_present': ev("window.__bubblePresent(%s)" % json.dumps(MESSAGE)),
            'bubbles': ev('window.__sentBubbles()'),
            'input_events': ev('window.__inputEvents'),
        }
        if results['pre']['bubble_present']:
            raise RuntimeError('pre-check: message already present')
        program = s2_flip_live.build_program_set_value(tab_id, MESSAGE)
        wall_ms, envelope = h.oneshot_code_exec(
            endpoint, program, 'c5-heldout-91-chromium')
        results['program'] = {
            'ok': envelope.get('ok'), 'elapsed_ms': envelope.get('elapsed_ms'),
            'error': envelope.get('error'), 'log': envelope.get('log'),
            'wall_ms': round(wall_ms, 1),
        }
        completed = None
        for line in envelope.get('log') or []:
            m = __import__('re').search(r'dom_act ok (\S+) completed (\d+)', line)
            if m:
                completed = int(m.group(2))
        results['program']['completed'] = completed
        results['post'] = {
            'bubble_present': ev("window.__bubblePresent(%s)" % json.dumps(MESSAGE)),
            'bubbles': ev('window.__sentBubbles()'),
            'input_value': ev("document.getElementById('msg-input').value"),
            'input_events': ev('window.__inputEvents'),
        }
        # No-double-send on retry: the pre-send check finds the message
        # already present and refuses to re-run the program.
        retry_pre = ev("window.__bubblePresent(%s)" % json.dumps(MESSAGE))
        results['retry'] = {'pre_present': retry_pre,
                            'outcome': 'already-sent' if retry_pre else 'would-send'}
        if retry_pre:
            results['retry']['bubbles_after_refusal'] = ev('window.__sentBubbles()')
        time.sleep(10)
        results['delayed'] = {
            'bubbles': ev('window.__sentBubbles()'),
            'count': ev("window.__sentBubbles().filter(b => b === %s).length"
                        % json.dumps(MESSAGE)),
        }
        png = WORKDIR / 'p9-run90-chromium.png'
        p9_wall, p9_ok = h.p9_capture(endpoint, tab_id, png)
        results['p9'] = {'ok': p9_ok, 'png': str(png), 'wall_ms': round(p9_wall, 1)}
        sent = (results['program'].get('ok') is True
                and results['program'].get('completed') == 4
                and results['post']['bubble_present'] is True
                and results['post']['bubbles'] == [MESSAGE]
                and results['retry']['outcome'] == 'already-sent'
                and results['delayed']['count'] == 1)
        results['outcome'] = 'sent' if sent else 'failed-unverified'
    except Exception as exc:  # noqa: BLE001 - record and re-raise for the log
        results['outcome'] = 'error'
        results['error'] = str(exc)[:400]
    finally:
        try:
            h.close_scratch('chromium', results.get('target_id', ''))
        except Exception:  # noqa: BLE001 - close is best-effort
            pass
    results['wall_ms'] = round((time.monotonic() - t0) * 1000.0, 1)
    WORKDIR.mkdir(parents=True, exist_ok=True)
    (WORKDIR / 'run-90.json').write_text(json.dumps(results, indent=2))
    print(json.dumps(results, indent=2))
    return 0 if results['outcome'] == 'sent' else 1


if __name__ == '__main__':
    raise SystemExit(main())
