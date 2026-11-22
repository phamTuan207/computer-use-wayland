#!/usr/bin/env python3
"""S2 flip live-run harness, v2 (step 6 of the FINAL direction).

Runs the clone-chat-send class live, one code-exec program per send
(CU_CODE_EXEC=1), act-now/stepwise as fallback only on program
failure. Endpoints are named per browser (P3 port split, P2 persistent port
2026-11-22): Brave/clone1 on http://127.0.0.1:9224, Chromium/clone2
on http://127.0.0.1:9223. Never assume port 9223 is Brave.

Transport split, and why there are two session shapes:
- Routing (tabs, observe) and the code-exec send run through the
  broker (one session per run, mux SSH, short calls). The send is a
  broker `request` with args ['code-exec', '--endpoint', endpoint,
  '--program', '-', '--intent', intent] and the program as stdin,
  exactly the envelope the one-shot used, delivered by shelling
  the broker CLI directly (session_remote.py subcommands start,
  request, result, finish). The harness never calls the
  session_remote.py Python functions _client_start,
  _client_start_with_wait, or _client_finish, and broker_start
  has no busy-wait: it runs the start subcommand once, fail
  fast (no --wait). The driver runs the program only when the relay env
  carries CU_CODE_EXEC=1: the driver inherits the relay process
  env, so a live run needs the relay drop-in flag (coord-click-6
  F3: flags.conf with CU_CODE_EXEC=1, verified in the relay
  process env). A broker send that returns the disabled envelope
  fails loudly with outcome error and does NOT fall back
  automatically; rerun with --transport oneshot as the documented
  recovery path.
- The one-shot session-driver (CU_CODE_EXEC=1 on its own command
  line) stays as fallback and recovery only. Automatic fallback
  happens only when the broker send was proven never accepted:
  the request was refused before dispatch and a result probe
  for that sequence answers not_found, so no broker record
  exists for it. A broker result failure leaves the outcome
  unknown, so no fallback runs there. Use --transport oneshot to force the one-shot path
  for a whole run (recovery, or a relay without the flag).

Per browser the flow is:
  broker tabs -> broker observe (coverage probe) -> P1
  route_perception (gates the send on complete DOM coverage; a
  screenshot decision aborts the send, fail closed) -> broker
  code-exec send program (set_value for Brave, fill for Chromium
  by default, Enter, trailing assert) ->
  independent V12 verify (fresh DOM read, not the program asserting
  its own success) -> P9 viewport capture (direct CDP screenshot,
  no workspace switch, reviewed by a human before the run scores).

Model calls in the loop: zero. The program is written once before
run 1 and reused unchanged across all runs; the machine loop makes
no vision call and no per-action model call. The P9 review is the
only vision read, and it is unscored human evidence (plus the hard
condition: a DOM-vs-render mismatch fails the run).

Wall time per run is t0 (harness start) to both V12 verifies done,
including all transport. The P9 capture and review happen after the
scored wall stops; the run is scored only after the P9 review passes.

SSH uses the S0 mux wrapper (scripts/ssh-laptop-mux.sh): the first
call creates the master (~3.3s), later calls reuse it (~1s). A dead
master costs one slow call and self-heals via ControlMaster=auto.

Usage (from the VM):
  python3 scripts/s2_flip_live.py --run 1 --workdir improvements/s2-flip-runs
  python3 scripts/s2_flip_live.py --run 1 --dry-run --workdir /tmp/s2-dry
  python3 scripts/s2_flip_live.py --run 1 --browser chromium --workdir ...

Exit 0 when the run JSON was written (even if a send failed; failure
is data in the JSON, not a harness crash). Exit 2 on harness error.
"""
import argparse
import base64
from contextlib import contextmanager
import json
import os
import re
import shlex
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from perception_router import route_perception  # noqa: E402

REPO = Path(__file__).resolve().parents[1]
SSH = str(REPO / 'scripts' / 'ssh-laptop-mux.sh')
LAPTOP_CU = '/home/james/computer-use-wayland/scripts/cu.py'
LAPTOP_REMOTE = '/home/james/computer-use-wayland/scripts/session_remote.py'
LAPTOP_V12 = '/tmp/s2-v12.mjs'
LAPTOP_P9 = '/tmp/s2-p9.mjs'
LAPTOP_SEED = '/tmp/s2-seed.mjs'
LAPTOP_ACTIVATE = '/tmp/c5-activate.mjs'
LAPTOP_COUNT = '/tmp/c5-count.mjs'

# Pill hold for the live send (W-PILLCDP, rule 18:30 2026-11-22): the
# overlay pill on the laptop, driven over SSH with the repo's
# scripts/overlay.py. Distinct agent 'S2-flip' so this release can
# never drop another agent's holder.
LAPTOP_OVERLAY = '/home/james/computer-use-wayland/scripts/overlay.py'
PILL_AGENT = 'S2-flip'
PILL_METHOD = 'CDP'

BROWSERS = {
    'brave': {'endpoint': 'http://127.0.0.1:9224', 'label': 'clone1'},
    'chromium': {'endpoint': 'http://127.0.0.1:9223', 'label': 'clone2'},
}

BUBBLE_ASSERT_SELECTOR = '[role="log"] > [data-message-item]:last-child'
# Composer grounding roles. The harvest (cdp.mjs) uses the raw tag name
# as the role, so <input type="text"> arrives as role "input", not
# "textbox". The grounding must accept it: the held-out fixture's
# #msg-input is a text input, and the textarea/textbox-only predicate
# missed it (held-out run 90, "composer not found in snapshot").
# W-ARIA adds the ARIA text-entry roles: the harvest maps an explicit
# role attribute verbatim, so role="searchbox" and role="combobox"
# arrive as such (GAP B), and a contenteditable field harvests as
# "textbox" (GAP A, normalized in cdp.mjs). set_value/focus still fail
# loudly on a non-editable field, so a mis-grounded non-text input
# cannot send silently.
COMPOSER_ROLES = ('textarea', 'textbox', 'input', 'searchbox', 'combobox')
PROGRAM_WALL_SECONDS = 20
V12_TIMEOUT_MS = 10000


def build_program(target_id, message):
    """The fill send program, parameterized only by target and message.

    The fill fallback program for Chromium only:
    build_program_set_value is the default (b1) program for Brave,
    not a general default, and this builder remains only as the
    fallback for Chromium when chromium_set_value is off and
    program_variant is not set_value. It grounds the
    composer from a fresh DOM snapshot, fills it with real input
    (click plus focus check plus insertText plus read-back, inside
    cdp.mjs fill), sends with Enter, and ends with the trailing
    assert (the V12 gate in program form, P5). The assert_state on
    the dom_act result makes a failed send fail the envelope; the
    harness still runs its own independent V12 after.
    P2 (step 7) requires every action to carry scope +
    observation_id bound to this snapshot: scope is the target id,
    observation_id is snap["snapshot"].
    """
    return (
        'snap = dom_observe(' + json.dumps(target_id) + ')\n'
        'comp = None\n'
        'for e in snap["elements"]:\n'
        '    if e["role"] in ' + repr(COMPOSER_ROLES) + ' and e["name"] == "Message":\n'
        '        comp = e["ref"]\n'
        '        break\n'
        'assert_state(comp is not None, "composer not found in snapshot")\n'
        'res = dom_act(snap, [\n'
        '    {"type": "fill", "ref": comp, "text": ' + json.dumps(message)
        + ', "scope": ' + json.dumps(target_id)
        + ', "observation_id": snap["snapshot"]},\n'
        '    {"type": "key", "keys": ["Enter"], "scope": ' + json.dumps(target_id)
        + ', "observation_id": snap["snapshot"]},\n'
        '    {"type": "assert", "selector": '
        + json.dumps(BUBBLE_ASSERT_SELECTOR)
        + ', "text": ' + json.dumps(message) + ', "timeout_ms": 3000'
        + ', "scope": ' + json.dumps(target_id)
        + ', "observation_id": snap["snapshot"]},\n'
        '])\n'
        'print("dom_act ok", res.get("ok"), "completed", res.get("completed"), '
        '"ms", res.get("execution_ms"), "error", res.get("error"))\n'
        'assert_state(res.get("ok") is True, "dom_act failed")\n'
    )


def build_program_set_value(target_id, message):
    """The input-free send program (C5-B1), LANDED shape: 4 actions.

    Grounds the composer from a fresh DOM snapshot, sets its value
    with the native setter plus read-back (inside cdp.mjs
    set_value, zero Input calls), focuses it with the landed
    focus action (cdp.mjs focus, activeElement proof, zero Input
    calls), sends with CDP key Enter (the landed key(), no code
    field; see the F7 decision in the step-9 log, section 2), and
    ends with the trailing bubble assert (the V12 gate in program
    form, P5). No value assert after the Enter: the composer is
    empty once the message is sent. No /tmp helper remains in
    this path. P2 stamps (scope + observation_id) on all 4
    actions, same as build_program. The focus action uses the
    same composer ref as set_value.
    """
    return (
        'snap = dom_observe(' + json.dumps(target_id) + ')\n'
        'comp = None\n'
        'for e in snap["elements"]:\n'
        '    if e["role"] in ' + repr(COMPOSER_ROLES) + ' and e["name"] == "Message":\n'
        '        comp = e["ref"]\n'
        '        break\n'
        'assert_state(comp is not None, "composer not found in snapshot")\n'
        'res = dom_act(snap, [\n'
        '    {"type": "set_value", "ref": comp, "text": ' + json.dumps(message)
        + ', "scope": ' + json.dumps(target_id)
        + ', "observation_id": snap["snapshot"]},\n'
        '    {"type": "focus", "ref": comp, "scope": ' + json.dumps(target_id)
        + ', "observation_id": snap["snapshot"]},\n'
        '    {"type": "key", "keys": ["Enter"], "scope": ' + json.dumps(target_id)
        + ', "observation_id": snap["snapshot"]},\n'
        '    {"type": "assert", "selector": '
        + json.dumps(BUBBLE_ASSERT_SELECTOR)
        + ', "text": ' + json.dumps(message) + ', "timeout_ms": 3000'
        + ', "scope": ' + json.dumps(target_id)
        + ', "observation_id": snap["snapshot"]},\n'
        '])\n'
        'print("dom_act ok", res.get("ok"), "completed", res.get("completed"), '
        '"ms", res.get("execution_ms"), "error", res.get("error"))\n'
        'assert_state(res.get("ok") is True, "dom_act failed")\n'
    )


def message_for(run, browser, prefix='S2-FLIP'):
    """Short, unique, clearly marked test message for one send."""
    return '%s-R%d-%s-IGNORE-TEST' % (prefix, run, browser.upper())


class _BrokerSendNotAccepted(RuntimeError):
    """The broker refused or never ran a send request (pre-dispatch).

    Raised only when the broker `request` call itself failed or the
    broker answered with something other than accepted. That alone
    does NOT prove the driver never saw the program: the same
    failure string also occurs when the channel dies after the
    broker accepted the request. _code_exec_send must probe the
    broker result for the sequence before any fallback runs, and
    only falls back when the probe answers not_found. A failure
    of the `result` call is NOT this error: the outcome is unknown
    there and no fallback may run.
    """


class _BrokerSendConsumed(RuntimeError):
    """A post-accept send failure: the broker consumed sequence seq.

    The broker accepted the request, so its next expected sequence
    is seq plus 1. Carries broker_next_seq so the caller threads
    the sequence correctly instead of reusing the consumed one.
    Raised for result-call failures and for result statuses other
    than completed (running, failed, unknown), for a replay of a
    failed or unknown record, for a disabled envelope, and when
    the pre-fallback probe finds a broker record for the sequence.
    """

    def __init__(self, message, seq):
        super().__init__(message)
        self.broker_next_seq = seq + 1



class Harness:
    def __init__(self, workdir, run_no, dry_run=False, activate=False,
                 message_prefix='S2-FLIP', program_variant='fill',
                 chromium_set_value=False, transport='broker'):
        # Validate before mkdir: a bad program_variant must not
        # create a workdir before it raises.
        if program_variant not in ('fill', 'set_value'):
            raise ValueError(
                'program_variant must be fill or set_value, got %r'
                % (program_variant,))
        if transport not in ('broker', 'oneshot'):
            raise ValueError(
                'transport must be broker or oneshot, got %r'
                % (transport,))
        self.transport = transport
        self.workdir = Path(workdir)
        self.workdir.mkdir(parents=True, exist_ok=True)
        self.run_no = run_no
        self.dry_run = dry_run
        self.activate = activate
        self.message_prefix = message_prefix
        self.program_variant = program_variant
        # Work 1, 2026-11-22: Brave uses (b1), so it uses the
        # set_value shape unconditionally. Chromium uses the (b1)
        # set_value shape only when chromium_set_value is set.
        # --set-value still forces set_value on every browser.
        self.chromium_set_value = chromium_set_value
        self.spans = []
        self.ssh_calls = []
        self.log_lines = []
        # Sleeper pid of the current pill hold, set by cdp_pill_hold
        # for the duration of the hold (None outside a hold). Lets
        # send_browser re-check the exact holder key before the
        # visible step (H1, Redteam amend2).
        self._pill_sleep_pid = None

    def variant_for(self, browser):
        """Send program variant for one browser: 'fill' or 'set_value'.

        Brave returns set_value unconditionally in variant_for, not
        only by default. Chromium returns set_value only when
        chromium_set_value is set, or when the global program_variant
        is set_value.
        """
        browser = str(browser).strip().lower()
        if browser not in ('brave', 'chromium'):
            raise ValueError('unknown browser %r' % (browser,))
        if self.program_variant == 'set_value':
            return 'set_value'
        # Work 1, 2026-11-22: Brave uses (b1), so it returns
        # set_value unconditionally. Chromium uses set_value only when
        # chromium_set_value is set; otherwise it keeps fill.
        if browser == 'brave':
            return 'set_value'
        if browser == 'chromium' and self.chromium_set_value:
            return 'set_value'
        return 'fill'

    def program_variant_label(self, browsers):
        """Label for the browsers actually run, e.g. brave=set_value.

        Only the browsers in the given list appear in the label, so
        a Chromium-only run does not record a Brave variant.
        Browser names are normalized (strip, lower) and deduplicated
        in order, so ' Brave ' and a repeated browser cannot write
        a wrong label.
        """
        seen = []
        for b in browsers:
            norm = str(b).strip().lower()
            if norm not in seen:
                seen.append(norm)
        return ','.join('%s=%s' % (b, self.variant_for(b))
                        for b in seen)

    def delayed_targets(self, results, browsers):
        """Set_value browsers with a target id and a message.

        A send was attempted for these browsers (sent,
        failed-unverified, error, or already-sent), so the delayed
        recount applies. A browser that aborted-routing has a
        target id but no message, so it is left out. Chromium fill
        never uses set_value, so it is left out too.
        Browser names are normalized (strip, lower) and deduplicated
        in order, like program_variant_label, so ' Brave ' and a
        repeated browser cannot write a wrong list.
        """
        targets = []
        seen = set()
        for browser in browsers:
            norm = str(browser).strip().lower()
            if norm in seen:
                continue
            seen.add(norm)
            if self.variant_for(norm) != 'set_value':
                continue
            entry = ((results or {}).get('browsers') or {}).get(norm) or {}
            target_id = entry.get('target_id')
            message = entry.get('message')
            if target_id and message:
                targets.append((norm, target_id, message))
        return targets

    def note(self, text):
        self.log_lines.append(text)
        print(text, flush=True)

    def ssh(self, remote_cmd, label, timeout=120, input_text=None):
        """One mux SSH call. Returns (rc, stdout, stderr, wall_ms)."""
        start = time.monotonic()
        proc = subprocess.run([SSH, remote_cmd], capture_output=True,
                              text=True, timeout=timeout,
                              input=input_text)
        wall_ms = (time.monotonic() - start) * 1000.0
        self.ssh_calls.append({'label': label, 'wall_ms': round(wall_ms, 1),
                               'rc': proc.returncode})
        return proc.returncode, proc.stdout, proc.stderr, wall_ms

    def mux_baseline(self):
        """Mean wall of two trivial SSH calls: the per-call transport cost."""
        walls = []
        for _ in range(2):
            _rc, _out, _err, wall = self.ssh('true', 'mux-probe')
            walls.append(wall)
        return sum(walls) / len(walls)

    def broker(self, lease, seq, args, stdin='', image_policy='auto',
               timeout=120):
        """One driver command through the broker: request + result.

        Returns (request_wall_ms, result_wall_ms, response_dict). The
        envelope travels in a heredoc in the same SSH call as the
        request command, so no scp per command.
        """
        envelope = json.dumps({'args': args, 'stdin': stdin,
                               'image_policy': image_policy},
                              ensure_ascii=False, separators=(',', ':'))
        env_path = '/tmp/s2-flip-env-%d.json' % seq
        remote = (
            'umask 077; cat > ' + env_path + " <<'S2EOF'\n" + envelope + '\nS2EOF\n'
            'python3 ' + LAPTOP_REMOTE + ' request --lease-file ' + lease
            + ' --sequence %d --request %s' % (seq, env_path))
        rc, out, err, req_wall = self.ssh(remote, 'broker-request-%d' % seq,
                                          timeout=timeout)
        if rc != 0:
            raise RuntimeError('broker request failed rc=%d: %s %s'
                               % (rc, out.strip()[:300], err.strip()[:300]))
        accepted = json.loads(out)
        if accepted.get('ok') is not True:
            raise RuntimeError('broker request not accepted: %s' % out[:300])
        status = accepted.get('status')
        if status == 'accepted':
            pass  # fresh accept: fetch the result below
        elif status in ('completed', 'failed', 'running', 'unknown'):
            # Replay of a recorded response: the broker already ran
            # this sequence (same sequence, same digest) and answers
            # with the recorded status instead of 'accepted'. No
            # result fetch is needed; the recorded response travels
            # in this body. broker_code_exec decides what each
            # status means.
            return req_wall, 0.0, accepted
        else:
            raise RuntimeError('broker request not accepted: %s' % out[:300])
        rc, out, err, res_wall = self.ssh(
            'python3 ' + LAPTOP_REMOTE + ' result --lease-file ' + lease
            + ' --sequence %d' % seq, 'broker-result-%d' % seq, timeout=timeout)
        if rc != 0:
            raise RuntimeError('broker result failed rc=%d: %s %s'
                               % (rc, out.strip()[:300], err.strip()[:300]))
        return req_wall, res_wall, json.loads(out)

    def driver_result(self, response):
        """Unwrap a broker result response to the cu.main() result dict."""
        inner = response.get('response') or {}
        if 'result' in inner:
            return inner.get('result')
        return inner

    def broker_start(self, lease, owner):
        rc, out, err, wall = self.ssh(
            'python3 ' + LAPTOP_REMOTE + ' start --owner ' + owner
            + ' --lease-file ' + lease, 'broker-start')
        if rc != 0:
            raise RuntimeError('broker start failed rc=%d: %s %s'
                               % (rc, out.strip()[:300], err.strip()[:300]))
        started = json.loads(out)
        if started.get('ok') is not True:
            raise RuntimeError('broker start not ok: %s' % out[:300])
        self.spans.append({'phase': 'broker-start', 'wall_ms': round(wall, 1),
                           'laptop_ms': None})
        return started

    def broker_finish(self, lease):
        rc, out, err, wall = self.ssh(
            'python3 ' + LAPTOP_REMOTE + ' finish --lease-file ' + lease,
            'broker-finish')
        self.spans.append({'phase': 'broker-finish', 'wall_ms': round(wall, 1),
                           'laptop_ms': None})
        try:
            return json.loads(out)
        except ValueError:
            return {'ok': rc == 0, 'raw': out[:300]}

    def broker_code_exec(self, lease, seq, endpoint, program, intent):
        """One code-exec send through the broker client (A5 migrate).

        Same envelope the one-shot used: args ['code-exec',
        '--endpoint', endpoint, '--program', '-', '--intent', intent]
        with the program as stdin, delivered as one broker request
        plus one result fetch. 'code-exec' is on the broker allowlist
        (session_remote.py COMMANDS) and the driver unwraps the
        result the same way the one-shot did (driver_result), so the
        returned envelope has the same shape (ok, api_calls,
        elapsed_ms, error, error_type, log). Returns (wall_ms,
        envelope, next_seq). Raises _BrokerSendNotAccepted when the
        request was refused before dispatch (the caller must still
        probe before falling back; see _code_exec_send). Raises
        _BrokerSendConsumed (a RuntimeError carrying
        broker_next_seq seq plus 1) when the result call fails or
        the broker reports a status other than completed
        (running, failed, unknown): the request was accepted, so
        the sequence is consumed and no fallback may run. A
        replay with status completed returns its recorded
        envelope; a replay with any other status raises the same
        _BrokerSendConsumed. The driver runs the program only
        when the relay env carries CU_CODE_EXEC=1; a disabled
        envelope is returned, not raised, and the caller must
        refuse the fallback for it.
        """
        try:
            req_w, res_w, resp = self.broker(
                lease, seq,
                ['code-exec', '--endpoint', endpoint, '--program', '-',
                 '--intent', intent],
                stdin=program, timeout=120)
        except RuntimeError as exc:
            if (str(exc).startswith('broker request failed')
                    or str(exc).startswith('broker request not accepted')):
                raise _BrokerSendNotAccepted(str(exc)) from exc
            # Any other broker failure escapes after the request was
            # accepted (the result fetch failed): the sequence is
            # consumed, so the caller must advance past it.
            raise _BrokerSendConsumed(str(exc), seq) from exc
        status = resp.get('status')
        if status == 'completed':
            envelope = self.driver_result(resp)
            wall_ms = req_w + res_w
            self.spans.append({'phase': 'act-broker-code-exec',
                               'wall_ms': round(wall_ms, 1),
                               'laptop_ms': (envelope.get('elapsed_ms')
                                             if isinstance(envelope, dict)
                                             else None)})
            return wall_ms, envelope, seq + 1
        if status == 'unknown':
            raise _BrokerSendConsumed(
                'broker code-exec result unknown for sequence %d: %s'
                % (seq, str(resp)[:300]), seq)
        if status == 'running':
            raise _BrokerSendConsumed(
                'broker code-exec result still running for sequence '
                '%d after the result wait: %s' % (seq, str(resp)[:300]),
                seq)
        if status == 'failed':
            raise _BrokerSendConsumed(
                'broker code-exec result failed for sequence %d: %s'
                % (seq, str(resp)[:300]), seq)
        raise _BrokerSendConsumed(
            'broker code-exec unexpected result status for sequence '
            '%d: %s' % (seq, str(resp)[:300]), seq)

    def _probe_request_record(self, lease, seq):
        """Ask the broker what it knows about one sequence.

        Runs `result --sequence N` once and returns (kind,
        status). kind 'record' means the broker holds a record
        for the sequence (status completed, failed, running, or
        unknown, or an expired answer, which also proves the
        sequence was consumed before). kind 'not_found' means the
        broker knows no such request: the request was never
        accepted. kind 'unavailable' means the probe itself could
        not get an answer (broker down, lease bad, unparseable
        output): the outcome is unknown, not proof of anything.
        A running record makes the result call wait up to the
        broker REQUEST_TIMEOUT (120s) before answering, so this
        probe can take that long; that wait is the price of
        knowing instead of guessing.
        """
        try:
            rc, out, err, _wall = self.ssh(
                'python3 ' + LAPTOP_REMOTE + ' result --lease-file '
                + lease + ' --sequence %d' % seq,
                'broker-result-probe-%d' % seq, timeout=130)
        except Exception:
            return ('unavailable', None)
        text = ((out or '') + (err or '')).strip()
        if rc == 0:
            try:
                body = json.loads(out)
            except ValueError:
                return ('unavailable', None)
            status = body.get('status')
            if body.get('ok') is True and status in (
                    'completed', 'failed', 'running', 'unknown'):
                return ('record', status)
            return ('unavailable', None)
        if 'not_found' in text:
            return ('not_found', None)
        if 'expired' in text:
            return ('record', 'expired')
        return ('unavailable', None)

    def _code_exec_send(self, lease, seq, endpoint, program, intent,
                        before_fallback=None):
        """Send one program by the configured transport.

        Returns (wall_ms, envelope, next_seq, transport). Default
        transport is broker (lease given). One-shot runs when the
        transport is forced to oneshot, or when no broker lease
        exists (legacy callers and unit tests with no session).
        Automatic one-shot fallback runs ONLY after two gates
        pass, in order. First, the result probe: on a
        pre-dispatch broker refusal (_BrokerSendNotAccepted),
        _probe_request_record(lease, seq) must answer
        'not_found', proving the broker holds no record for the
        sequence. A record, an expired answer, or an unanswerable
        probe all refuse the fallback: the send outcome is
        unknown there, so the operator decides with a fresh run
        number instead. 'broker_unavailable' in the request error
        is NOT accepted as proof on its own: the broker client
        maps any socket OSError, including a receive failure
        after the request was transmitted, to that name. Second,
        the recount: before_fallback, when given, re-runs
        count_check for this message and refuses the fallback
        when the count is not 0 (the broker attempt may already
        have sent it) or when the count itself errors. The
        recount runs for both variants, so a Chromium fill send,
        which has no pre-send count, still gets one count before
        any fallback send. A broker result failure, an unknown,
        running, or failed result, or a disabled envelope (relay
        lacks CU_CODE_EXEC=1) raises with no fallback: the flag
        is a relay precondition, and silently routing around it
        would hide it; rerun with --transport oneshot instead.
        A forced oneshot transport is not a fallback, so no
        recount runs there; it relies on the operator's fresh
        run number (never reuse a run number) plus the set_value
        pre-send count, which runs before this call.
        """
        if lease is None or self.transport == 'oneshot':
            wall_ms, envelope = self.oneshot_code_exec(
                endpoint, program, intent)
            return wall_ms, envelope, seq, 'oneshot'
        try:
            wall_ms, envelope, next_seq = self.broker_code_exec(
                lease, seq, endpoint, program, intent)
        except _BrokerSendNotAccepted as exc:
            kind, status = self._probe_request_record(lease, seq)
            if kind == 'record':
                raise _BrokerSendConsumed(
                    'broker code-exec not accepted (%s) but the '
                    'result probe for sequence %d found a broker '
                    'record (status %s), so the send outcome is '
                    'unknown; one-shot fallback NOT taken '
                    'automatically, retry with a fresh run number '
                    'after checking the message count'
                    % (str(exc)[:200], seq, status), seq) from exc
            if kind != 'not_found':
                # The probe could not answer (broker down, lease
                # bad): consumption is unproven either way, so the
                # sequence is kept and the run records an unknown
                # outcome instead of falling back blind.
                raise RuntimeError(
                    'broker code-exec not accepted (%s) and the '
                    'result probe for sequence %d answered %s, so '
                    'the send outcome is unknown; one-shot '
                    'fallback NOT taken automatically, retry with '
                    'a fresh run number after checking the message '
                    'count'
                    % (str(exc)[:200], seq, kind)) from exc
            if before_fallback is not None:
                before_fallback()
            self.note('broker code-exec not accepted (%s); '
                      'one-shot fallback, probe found no record '
                      'for sequence %d'
                      % (str(exc)[:200], seq))
            wall_ms, envelope = self.oneshot_code_exec(
                endpoint, program, intent)
            return wall_ms, envelope, seq, 'broker-fallback-oneshot'
        if (isinstance(envelope, dict)
                and envelope.get('error_type') == 'disabled'):
            raise _BrokerSendConsumed(
                'broker code-exec disabled: relay lacks CU_CODE_EXEC=1; '
                'one-shot fallback NOT taken automatically, rerun with '
                '--transport oneshot as the documented recovery path',
                seq)
        return wall_ms, envelope, next_seq, 'broker'

    def oneshot_code_exec(self, endpoint, program, intent):
        """One code-exec send as a one-shot session-driver.

        FALLBACK AND RECOVERY PATH, kept by the A5 gate: the broker
        is the default send path, and this stays for the automatic
        pre-dispatch fallback in _code_exec_send and for manual
        recovery (--transport oneshot, or the relay restart drill).
        CU_CODE_EXEC=1 is set on this command line only: the flag is
        on for exactly this class's sends, nowhere else. The session
        ends when the JSONL stdin closes. Returns (wall_ms, envelope).
        """
        line = json.dumps({'args': ['code-exec', '--endpoint', endpoint,
                                    '--program', '-', '--intent', intent],
                           'stdin': program, 'image_policy': 'auto'},
                          ensure_ascii=False, separators=(',', ':')) + '\n'
        remote = ('CU_CODE_EXEC=1 python3 %s session -- python3 %s session-driver'
                  % (LAPTOP_CU, LAPTOP_CU))
        start = time.monotonic()
        rc, out, err, wall = self.ssh(remote, 'oneshot-code-exec',
                                      timeout=90, input_text=line)
        wall_ms = (time.monotonic() - start) * 1000.0
        envelope = None
        for raw in out.splitlines():
            try:
                obj = json.loads(raw)
            except ValueError:
                continue
            if isinstance(obj, dict) and 'result' in obj:
                envelope = obj['result']
        if envelope is None:
            raise RuntimeError(
                'one-shot code-exec returned no driver result: rc=%d '
                'stdout=%s stderr=%s' % (rc, out.strip()[-300:],
                                         err.strip()[-300:]))
        return wall_ms, envelope

    def v12_check(self, endpoint, target_id, message):
        """Independent V12: fresh DOM read over CDP, not the program.

        Returns {found, role, side, text_len, ms, error}. Polls up to
        V12_TIMEOUT_MS for a [data-message-item] whose text contains
        the message. Read-only: Runtime.evaluate, no input.
        """
        start = time.monotonic()
        rc, out, err, wall = self.ssh(
            'node %s %s %s %s %d' % (LAPTOP_V12, endpoint, target_id,
                                    shlex.quote(message), V12_TIMEOUT_MS),
            'v12-check', timeout=60)
        wall_ms = (time.monotonic() - start) * 1000.0
        if rc != 0:
            return {'found': False, 'error': 'v12 script rc=%d: %s'
                    % (rc, (out + err).strip()[:300]), 'ms': round(wall_ms, 1)}
        try:
            found = json.loads(out.strip().splitlines()[-1])
        except (ValueError, IndexError):
            return {'found': False, 'error': 'v12 script bad output: %s'
                    % out.strip()[:300], 'ms': round(wall_ms, 1)}
        found['ms'] = round(wall_ms, 1)
        return found

    def p9_capture(self, endpoint, target_id, png_path):
        """P9 viewport screenshot via direct CDP (no session, no
        workspace switch). Returns (wall_ms, ok). The PNG is saved
        on the VM for human review."""
        start = time.monotonic()
        rc, out, err, wall = self.ssh(
            'node %s %s %s' % (LAPTOP_P9, endpoint, target_id),
            'p9-capture', timeout=60)
        wall_ms = (time.monotonic() - start) * 1000.0
        if rc != 0:
            return wall_ms, False
        b64 = out.strip().splitlines()[-1].strip()
        try:
            png_path.write_bytes(base64.b64decode(b64))
        except Exception:
            return wall_ms, False
        return wall_ms, True

    def route_browser(self, lease, seq, browser, target_id=None):
        """Broker tabs + observe + P1 routing for one browser.

        Returns (result_dict, next_seq). When target_id is given
        (dry run), the observe runs against that tab instead of
        looking the muse.ai tab up.
        """
        cfg = BROWSERS[browser]
        endpoint = cfg['endpoint']
        out = {'browser': browser, 'label': cfg['label'],
               'endpoint': endpoint}
        try:
            if target_id is None:
                req_w, res_w, resp = self.broker(
                    lease, seq, ['browser', 'tabs', '--endpoint', endpoint])
                seq += 1
                tabs = self.driver_result(resp)
                if not isinstance(tabs, list):
                    raise RuntimeError('tabs did not return a list: %s'
                                       % str(tabs)[:300])
                muse_tabs = [t for t in tabs
                             if (t.get('url') or '').startswith('https://muse.ai/')]
                if len(muse_tabs) != 1:
                    raise RuntimeError('expected exactly one muse.ai tab, got %d'
                                       % len(muse_tabs))
                target_id = muse_tabs[0]['id']
                out['tab_title'] = muse_tabs[0].get('title')
                self.spans.append({'phase': 'tabs-' + browser,
                                   'wall_ms': round(req_w + res_w, 1),
                                   'laptop_ms': None})
            out['target_id'] = target_id
            req_w, res_w, resp = self.broker(
                lease, seq, ['browser', 'observe', '--endpoint', endpoint,
                             '--target', target_id])
            seq += 1
            snap = self.driver_result(resp)
            if not isinstance(snap, dict) or snap.get('ok') is False:
                raise RuntimeError('observe failed: %s' % str(snap)[:300])
            coverage = {'elements': len(snap.get('elements') or []),
                        'truncated': bool(snap.get('truncated'))}
            out['observe'] = {'elements': coverage['elements'],
                              'truncated': coverage['truncated'],
                              'wall_ms': round(req_w + res_w, 1)}
            # C5-B1: the live thread grows past the 80-element snapshot
            # cap (each test send plus the agent's reply adds message
            # items), so the inventory truncates and the P1 gate fails
            # closed even though the send target is grounded. When the
            # inventory is truncated BUT the composer is present in the
            # snapshot, the send may proceed under a recorded relaxed
            # gate: the send program re-grounds the composer from its
            # own snapshot and asserts it exists, so the target is
            # proven covered either way. Without this the measurement
            # cannot run on a live thread at all.
            out['observe']['composer_present'] = any(
                isinstance(e, dict)
                and e.get('role') in COMPOSER_ROLES
                and e.get('name') == 'Message'
                for e in (snap.get('elements') or []))
            self.spans.append({'phase': 'observe-' + browser,
                               'wall_ms': round(req_w + res_w, 1),
                               'laptop_ms': None})
            routing = []
            decision = route_perception(
                {'kind': 'chromium-content'},
                probes={'dom-chromium': lambda target: coverage},
                emit=routing.append)
            out['routing'] = decision
            for record in routing:
                self.note('perception_routing ' + json.dumps(record, ensure_ascii=False))
            if decision['source'] != 'dom-chromium':
                if coverage['truncated'] and out['observe']['composer_present']:
                    out['routing_relaxed'] = True
                    out['routing'] = {
                        'source': 'dom-chromium',
                        'target_kind': 'chromium-content',
                        'fell_through': decision.get('fell_through', []),
                        'reason': ('relaxed gate: truncated inventory '
                                   '(%d elements), send target covered'
                                   % coverage['elements']),
                        'coverage': coverage}
                    self.note('routing relaxed: truncated inventory, '
                              'composer present in snapshot')
                    out['outcome'] = 'routed'
                else:
                    out['outcome'] = 'aborted-routing'
                    out['error'] = ('router fell through to %s: %s'
                                    % (decision['source'], decision['reason']))
            else:
                out['outcome'] = 'routed'
            return out, seq
        except Exception as exc:
            out['outcome'] = 'error'
            out['error'] = str(exc)[:400]
            return out, seq

    def activate_browser(self, endpoint, target_id):
        """C5-A1 pre-step: Target.activateTarget + Page.bringToFront.

        CDP-only, no workspace switch, no screen change. Runs as a
        separate node helper (/tmp/c5-activate.mjs) before the send
        program. Returns the helper's JSON dict. A failed activation
        does NOT abort the send: the send result itself is the
        measurement, and the activation dict records what happened.
        """
        start = time.monotonic()
        rc, out, err, wall = self.ssh(
            'node %s %s %s' % (LAPTOP_ACTIVATE, endpoint, target_id),
            'activate', timeout=60)
        wall_ms = (time.monotonic() - start) * 1000.0
        try:
            result = json.loads(out.strip().splitlines()[-1])
        except (ValueError, IndexError):
            result = {'ok': False, 'error': 'activate script bad output: %s'
                      % out.strip()[:300]}
        result['ms'] = round(wall_ms, 1)
        result['rc'] = rc
        self.spans.append({'phase': 'activate',
                           'wall_ms': round(wall_ms, 1), 'laptop_ms': None})
        return result

    def count_check(self, endpoint, target_id, message):
        """C5 double-send guard: count bubbles containing the message.

        Single read-only Runtime.evaluate via /tmp/c5-count.mjs.
        Returns {count, items} (count -1 on error). Pre-send the
        count must be 0; post-send it must be 1.
        """
        rc, out, err, wall = self.ssh(
            'node %s %s %s %s' % (LAPTOP_COUNT, endpoint, target_id,
                                 shlex.quote(message)),
            'count-check', timeout=60)
        try:
            result = json.loads(out.strip().splitlines()[-1])
        except (ValueError, IndexError):
            result = {'count': -1,
                      'error': 'count script bad output: %s' % out.strip()[:300]}
        result['ms'] = round(wall, 1)
        return result

    # Laptop sleeper for the pill holder pid (H1 bare-bare): a detached
    # `sleep` on the laptop, alive for one send step, whose pid keys
    # this run's holder. The pid must be a laptop pid of a process
    # alive for the hold: this harness runs on the VM, so its own pid
    # does not exist on the laptop and the daemon would prune the
    # holder within one monitor tick (~2s). Verified 20:38 +07: VM pid
    # 93722 absent on the laptop, prune drops a holder whose pid is
    # dead. The sleeper lives 600s, covers one send step, and if the
    # harness dies the daemon prunes the holder when the sleeper
    # expires. A nohup sleep execs directly (no fork), so $! is the
    # sleep pid itself, and with stdin/stdout/stderr redirected it
    # survives the SSH session end.
    PILL_SLEEP_SECONDS = 600

    def pill_acquire_cmd(self):
        """SSH command that raises the pill on the laptop.

        Starts the laptop sleeper, acquires with its pid, echoes the
        pid as PILL_SLEEP_PID= for the release call, kills the sleeper
        inline when the acquire fails, and preserves the acquire rc
        as the call rc (the trailing echo must not mask a failure).
        """
        return ('nohup sleep %d >/dev/null 2>&1 < /dev/null & SLEEP_PID=$!; '
                'python3 %s acquire --agent %s --method %s --pid $SLEEP_PID; '
                'ACQ_RC=$?; echo PILL_SLEEP_PID=$SLEEP_PID; '
                '[ $ACQ_RC -ne 0 ] && kill $SLEEP_PID 2>/dev/null; '
                'exit $ACQ_RC'
                % (self.PILL_SLEEP_SECONDS, LAPTOP_OVERLAY,
                   PILL_AGENT, PILL_METHOD))

    def pill_release_cmd(self, pid):
        """SSH command that drops this harness's pill holder.

        Takes the sleeper pid from the matching acquire (parsed from
        PILL_SLEEP_PID=). The release passes the same --pid so exactly
        this run's key is removed, then kills the sleeper. The pid
        is required: there is no pid-less release anymore, because a
        pid-less release only removes the bare key, which could be
        another run's live bare holder (the bare-bare hazard, H2
        Redteam amend2), while leaving this run's pid-keyed holder
        behind. When the pid cannot be parsed, cdp_pill_hold
        releases nothing and the daemon prunes the holder when the
        sleeper expires.
        """
        return ('python3 %s release --agent %s --method %s --pid %d; '
                'kill %d 2>/dev/null || true'
                % (LAPTOP_OVERLAY, PILL_AGENT, PILL_METHOD, pid, pid))

    @contextmanager
    def cdp_pill_hold(self):
        """Best-effort pill hold around one browser-control step.

        Acquires the overlay pill on the laptop before the step and
        releases it after. Best effort only: the hard gate is the
        cdp.mjs hook (fail closed), so a failed acquire here only
        warns and the send itself still cannot run invisibly. Yields
        True when the pill was acquired, False otherwise; a failed
        acquire skips the release (nothing was held). A failed release
        is noted, never raised: the holder is pid-keyed by the laptop
        sleeper pid, so the daemon prunes it when the sleeper expires
        (600s), and a stale S2-flip holder keeps the pill up until
        the next release or daemon restart, which is visible, not
        invisible. When the acquire succeeds but the sleeper pid
        cannot be parsed from its output, NO release runs: a
        pid-less release could delete another run's live bare holder
        (the bare-bare hazard, H2 Redteam amend2) while leaving this
        run's pid-keyed holder behind, so the holder is left to
        prune when the sleeper expires. The parsed sleeper pid is
        kept on self._pill_sleep_pid for the duration of the hold
        so send_browser can re-check the exact holder key before
        the visible step (H1).
        """
        held = False
        sleep_pid = None
        self._pill_sleep_pid = None
        try:
            rc, out, err, _wall = self.ssh(
                self.pill_acquire_cmd(), 'pill-acquire', timeout=60)
            held = rc == 0
            if held:
                match = re.search(r'PILL_SLEEP_PID=(\d+)', out)
                if match:
                    sleep_pid = int(match.group(1))
                    self._pill_sleep_pid = sleep_pid
                else:
                    self.note('pill acquire ok but no PILL_SLEEP_PID in '
                              'output; release skipped, no pid-less '
                              'fallback (it could delete another run\'s '
                              'bare holder); the daemon prunes this '
                              'holder when the sleeper expires: %s'
                              % out.strip()[:200])
            if not held:
                self.note('pill acquire failed (best effort, send gate '
                          'still applies): rc=%d %s'
                          % (rc, (out + err).strip()[:200]))
        except Exception as exc:
            self.note('pill acquire failed (best effort, send gate still '
                      'applies): %s' % str(exc)[:200])
        try:
            yield held
        finally:
            if held and sleep_pid is not None:
                try:
                    self.ssh(self.pill_release_cmd(sleep_pid), 'pill-release',
                             timeout=60)
                except Exception as exc:
                    self.note('pill release failed (ignored): %s'
                              % str(exc)[:200])
            self._pill_sleep_pid = None

    def pill_holder_alive(self, sleep_pid):
        """Re-check this run's pill holder is still present (H1).

        Runs overlay.py status on the laptop (read-only; cmd_status
        prunes dead holders first, so a dead sleeper's key is gone
        by the time the holders are reported) and checks the exact
        key S2-flip:<sleep_pid> is in holders. Returns False when
        the key is absent, when no pid is known (sleep_pid None:
        the key cannot be identified, so it cannot be confirmed),
        or when the check itself fails. Fail closed: an unconfirmed
        holder aborts the send in send_browser.
        """
        if sleep_pid is None:
            return False
        try:
            rc, out, err, _wall = self.ssh(
                'python3 %s status' % LAPTOP_OVERLAY, 'pill-status',
                timeout=60)
            if rc != 0:
                return False
            holders = (json.loads(out.strip()).get('holders') or {})
            return ('%s:%d' % (PILL_AGENT, sleep_pid)) in holders
        except Exception:
            return False

    def send_browser(self, browser, target_id, message, lease=None, seq=None):
        """Broker code-exec send + independent V12 for one browser.

        lease and seq carry the live broker session: with a lease the
        send goes through the broker by default (see
        _code_exec_send); without one (legacy callers, unit tests)
        it uses the one-shot path. The pill is held for the whole
        send (W-PILLCDP): the activate step, the program, and the
        V12 read. Best effort (see cdp_pill_hold); the cdp.mjs hook
        is the fail-closed gate for the actual input. Before the
        first visible step (activate), the holder is re-checked: if
        the sleeper died after the acquire and the daemon pruned the
        holder, the send aborts with outcome aborted-pill-lost and
        no visible action runs (H1, Redteam amend2). A failed
        acquire still runs the body (best effort, unchanged): the
        re-check only applies when the acquire reported held.
        """
        t_send = time.monotonic()
        with self.cdp_pill_hold() as held:
            if held and not self.pill_holder_alive(self._pill_sleep_pid):
                cfg = BROWSERS[browser]
                self.note('pill holder lost between acquire and '
                          'activate; aborting send before any visible '
                          'action')
                return {'browser': browser, 'label': cfg['label'],
                        'endpoint': cfg['endpoint'], 'message': message,
                        'model_calls': 0, 'target_id': target_id,
                        'program_variant': self.variant_for(browser),
                        'outcome': 'aborted-pill-lost',
                        'error': 'S2-flip pill holder gone before activate',
                        'wall_ms': round((time.monotonic() - t_send) * 1000.0, 1)}
            return self._send_browser_inner(browser, target_id, message,
                                            lease=lease, seq=seq)

    def _send_browser_inner(self, browser, target_id, message,
                            lease=None, seq=None):
        """Broker code-exec send + independent V12 for one browser.

        lease and seq carry the live broker session; the returned
        dict carries broker_next_seq (the sequence after this send)
        when a lease was given, so run() can thread the sequence
        across browsers. Without a lease the send uses the one-shot
        path and broker_next_seq is absent.
        """
        cfg = BROWSERS[browser]
        endpoint = cfg['endpoint']
        variant = self.variant_for(browser)
        out = {'browser': browser, 'label': cfg['label'],
               'endpoint': endpoint, 'message': message, 'model_calls': 0,
               'target_id': target_id,
               'program_variant': variant}
        t_send = time.monotonic()
        try:
            if self.activate:
                out['activation'] = self.activate_browser(endpoint, target_id)
            if variant == 'set_value':
                # Mandatory pre-send already-sent check (CB-2 double-send
                # guard): a retry must never run when the message is
                # already in the thread. Unique message per run, so any
                # count above 0 aborts the send. already-sent is a
                # valid outcome, not an error: do not rerun the same
                # run number, retry with a new run number instead.
                out['pre_count'] = self.count_check(endpoint, target_id, message)
                if out['pre_count'].get('count', -1) > 0:
                    out['outcome'] = 'already-sent'
                    out['wall_ms'] = round((time.monotonic() - t_send) * 1000.0, 1)
                    return out
                program = build_program_set_value(target_id, message)
            else:
                program = build_program(target_id, message)
            def _recount_before_fallback():
                # Second double-send gate, run immediately before
                # any automatic one-shot fallback (both variants:
                # fill has no pre-send count, so this is its only
                # count). The pre-send count ran before the broker
                # attempt; the broker attempt may have sent the
                # message since, so only a fresh count proves the
                # thread does not already hold it. Fail closed: a
                # count above 0, or a count error (-1), refuses
                # the fallback.
                recount = self.count_check(endpoint, target_id, message)
                count = recount.get('count', -1)
                if count != 0:
                    raise RuntimeError(
                        'one-shot fallback refused: message already '
                        'present or uncountable (count %s)' % (count,))

            wall_ms, envelope, next_seq, transport = self._code_exec_send(
                lease, seq, endpoint, program,
                'S2 flip run %d %s' % (self.run_no, browser),
                before_fallback=_recount_before_fallback)
            if lease is not None:
                out['broker_next_seq'] = next_seq
            completed = None
            if isinstance(envelope, dict):
                for line in envelope.get('log') or []:
                    m = re.search(r'dom_act ok (\S+) completed (\d+)', line)
                    if m:
                        completed = int(m.group(2))
            out['program'] = {
                'ok': envelope.get('ok') if isinstance(envelope, dict) else None,
                'api_calls': envelope.get('api_calls') if isinstance(envelope, dict) else None,
                'elapsed_ms': envelope.get('elapsed_ms') if isinstance(envelope, dict) else None,
                'error': envelope.get('error') if isinstance(envelope, dict) else None,
                'error_type': envelope.get('error_type') if isinstance(envelope, dict) else None,
                'log': envelope.get('log') if isinstance(envelope, dict) else None,
                'wall_ms': round(wall_ms, 1),
                'transport': transport,
            }
            self.spans.append({'phase': 'act-' + browser,
                               'wall_ms': round(wall_ms, 1),
                               'laptop_ms': out['program']['elapsed_ms']})
            if variant == 'set_value':
                # Landed 4-action program: CB-1 is input_sent =
                # set_value, focus and Enter all ran (completed >= 3),
                # target_received = set_value read-back done
                # (completed >= 1), verified = V12 found. No helper
                # remains in this path.
                out['cb1'] = {
                    'input_sent': bool(completed is not None and completed >= 3),
                    'target_received': bool(completed is not None and completed >= 1),
                    'verified': None,
                    'completed': completed,
                }
            else:
                out['cb1'] = {
                    'input_sent': bool(completed is not None and completed >= 2),
                    'target_received': bool(completed is not None and completed >= 1),
                    'verified': None,
                    'completed': completed,
                }
            v12 = self.v12_check(endpoint, target_id, message)
            out['v12'] = v12
            out['cb1']['verified'] = bool(v12.get('found'))
            self.spans.append({'phase': 'verify-' + browser,
                               'wall_ms': v12.get('ms'),
                               'laptop_ms': v12.get('ms')})
            out['wall_ms'] = round((time.monotonic() - t_send) * 1000.0, 1)
            out['outcome'] = 'sent' if v12.get('found') else 'failed-unverified'
            return out
        except Exception as exc:
            out['outcome'] = 'error'
            out['error'] = str(exc)[:400]
            out['wall_ms'] = round((time.monotonic() - t_send) * 1000.0, 1)
            if lease is not None and 'broker_next_seq' not in out:
                # Sequence after a failed send. A post-accept
                # failure (result failure, unknown, running, or
                # failed status, disabled envelope, probe-found
                # record) consumed the sequence: the broker next
                # is seq plus 1, carried on the exception, so the
                # next browser does not reuse it and hit a
                # conflict. A pre-dispatch fallback returns
                # through the success path above with seq
                # unchanged, so this branch keeps seq. A failure
                # after a successful send (for example a V12
                # error) already recorded broker_next_seq above;
                # the 'not in out' guard keeps that value instead
                # of overwriting it with seq.
                out['broker_next_seq'] = getattr(
                    exc, 'broker_next_seq', seq)
            return out

    def seed_scratch(self, browser):
        """Create a scratch tab with a fake composer + thread (dry run).

        Returns the tab id. The page mimics the live shape: a textarea
        with aria-label Message, a [role=log] thread, Enter appends a
        [data-message-item] with the typed text.
        """
        endpoint = BROWSERS[browser]['endpoint']
        rc, out, err, wall = self.ssh(
            'node %s %s' % (LAPTOP_SEED, endpoint), 'seed-scratch', timeout=60)
        if rc != 0:
            raise RuntimeError('seed failed rc=%d: %s' % (rc, (out + err)[:300]))
        tab_id = out.strip().splitlines()[-1].strip()
        if not tab_id:
            raise RuntimeError('seed returned no tab id')
        self.spans.append({'phase': 'setup-' + browser,
                           'wall_ms': round(wall, 1), 'laptop_ms': None})
        return tab_id

    def close_scratch(self, browser, target_id):
        endpoint = BROWSERS[browser]['endpoint']
        self.ssh('curl -s %s/json/close/%s >/dev/null'
                 % (endpoint, target_id), 'close-scratch', timeout=30)

    def run(self, browsers):
        t0 = time.monotonic()
        mux = self.mux_baseline()
        lease = '/home/james/.cache/agent-computer-use/s2-flip-run%d.lease' % self.run_no
        owner = 's2-flip-run%d' % self.run_no
        # The label is computed before the try block on purpose: an
        # unknown browser raises ValueError fail-closed after the mux
        # baseline probe, before any send runs and before any result
        # file is written.
        results = {'run': self.run_no, 'dry_run': self.dry_run,
                   'activate': self.activate,
                   'message_prefix': self.message_prefix,
                   'program_variant': self.program_variant_label(browsers),
                   'transport': self.transport,
                   'chromium_set_value': self.chromium_set_value,
                   'mux_baseline_ms': round(mux, 1), 'browsers': {}}
        scratch = {}
        try:
            if self.dry_run:
                for browser in browsers:
                    # The scratch tab is a browser-control step too:
                    # hold the pill while it is created (W-PILLCDP).
                    with self.cdp_pill_hold():
                        scratch[browser] = self.seed_scratch(browser)
            # A stale lease from a crashed run blocks start (O_EXCL);
            # remove it first. The lease is per-run-number, so this
            # never touches another run's live lease.
            _rc, _out, _err, lease_wall = self.ssh(
                'rm -f ' + lease, 'lease-cleanup', timeout=30)
            self.spans.append({'phase': 'setup-lease',
                               'wall_ms': round(lease_wall, 1),
                               'laptop_ms': None})
            self.broker_start(lease, owner)
            seq = 1
            routed = {}
            try:
                for browser in browsers:
                    target = scratch.get(browser)
                    res, seq = self.route_browser(lease, seq, browser, target)
                    results['browsers'][browser] = res
                    if res.get('outcome') == 'routed':
                        routed[browser] = res['target_id']
                    else:
                        self.note('run %d %s outcome %s: %s'
                                  % (self.run_no, browser, res.get('outcome'),
                                     res.get('error', '')))
                # Sends run INSIDE the broker session (A5 migrate):
                # the broker send is one request on this lease, so it
                # must happen before broker_finish, not after it.
                # The sequence threads across browsers: each send
                # consumes one sequence number.
                for browser in browsers:
                    if browser not in routed:
                        continue
                    message = message_for(self.run_no, browser,
                                          self.message_prefix)
                    res = self.send_browser(browser, routed[browser],
                                            message, lease=lease, seq=seq)
                    seq = res.get('broker_next_seq', seq)
                    results['browsers'][browser].update(res)
                    if res.get('outcome') in ('error', 'failed-unverified'):
                        self.note('run %d %s outcome %s: %s'
                                  % (self.run_no, browser, res.get('outcome'),
                                     res.get('error', '')))
            finally:
                try:
                    self.broker_finish(lease)
                except Exception as exc:
                    self.note('broker finish failed (ignored): %s' % exc)
            # Scored wall stops here: both V12 verifies are done.
            results['wall_ms'] = round((time.monotonic() - t0) * 1000.0, 1)
        finally:
            # Delayed double-send guard for the set_value variant:
            # 10s after the scored wall stops, recount the message.
            # Exactly 1 means no late duplicate arrived. Only the
            # browsers that actually used set_value are recounted.
            # Sleep only when at least one set_value browser has a
            # target_id and a message, that is, a send was attempted
            # (sent, failed-unverified, error, or already-sent).
            # When every browser aborted-routing, no send ran, so
            # no sleep and no delayed count are recorded.
            # already-sent is a valid outcome, not an error: do not
            # rerun the same run number. A retry must use a new run
            # number with a fresh unique message. Brave fill is no
            # longer reachable by any flag; rollback is revert commit.
            # A missing delayed_count key means no send was attempted,
            # not a logging error.
            delayed_targets = self.delayed_targets(results, browsers)
            if delayed_targets:
                results['delayed_count'] = {}
                time.sleep(10)
                for browser, target_id, message in delayed_targets:
                    try:
                        results['delayed_count'][browser] = self.count_check(
                            BROWSERS[browser]['endpoint'], target_id, message)
                    except Exception as exc:
                        results['delayed_count'][browser] = {
                            'count': -1, 'error': str(exc)[:300]}
            # P9 captures AFTER the scored wall stops: one viewport
            # screenshot per browser through direct CDP. The run is
            # scored only after a human reviews these.
            results['p9'] = {}
            for browser in browsers:
                target_id = (results['browsers'].get(browser) or {}).get('target_id')
                if not target_id:
                    continue
                png_path = self.workdir / ('p9-run%d-%s.png'
                                           % (self.run_no, browser))
                try:
                    p9_wall, p9_ok = self.p9_capture(
                        BROWSERS[browser]['endpoint'], target_id, png_path)
                    results['p9'][browser] = {
                        'ok': p9_ok, 'png': str(png_path),
                        'wall_ms': round(p9_wall, 1)}
                except Exception as exc:
                    results['p9'][browser] = {'ok': False,
                                              'error': str(exc)[:300]}
            for browser, target in scratch.items():
                try:
                    with self.cdp_pill_hold():
                        self.close_scratch(browser, target)
                except Exception as exc:
                    self.note('scratch close failed (ignored): %s' % exc)
        results['spans'] = self.spans
        results['ssh_calls'] = self.ssh_calls
        # Phase split. Model is 0 (no model call in the loop). Every
        # span's wall is split into transport (mux hops, measured per
        # run) and laptop work (the remainder, or the payload timing
        # when the payload carries one, e.g. code-exec elapsed_ms).
        # Residual is whatever the split does not attribute; it must
        # stay small, and a large residual means misattribution.
        phases = {'observe': 0.0, 'act': 0.0, 'verify': 0.0, 'broker': 0.0,
                  'setup': 0.0}
        transport = 0.0
        for span in self.spans:
            kind = span['phase'].split('-')[0]
            wall = span['wall_ms'] or 0.0
            if kind in ('observe', 'tabs'):
                laptop = max(0.0, wall - 2 * mux)
                phases['observe'] += laptop
                transport += wall - laptop
            elif kind == 'act':
                laptop = span.get('laptop_ms') or 0.0
                phases['act'] += laptop
                transport += max(0.0, wall - laptop)
            elif kind == 'verify':
                laptop = max(0.0, wall - mux)
                phases['verify'] += laptop
                transport += wall - laptop
            elif kind in ('broker', 'setup', 'activate'):
                laptop = max(0.0, wall - mux)
                phases['setup' if kind in ('activate',) else kind] += laptop
                transport += wall - laptop
        transport += 2 * mux  # the two mux-baseline probes
        accounted = transport + sum(phases.values())
        results['phase_split_ms'] = {
            'model': 0,
            'ssh': round(transport, 1),
            'broker': round(phases['broker'], 1),
            'observe': round(phases['observe'], 1),
            'act': round(phases['act'], 1),
            'verify': round(phases['verify'], 1),
            'setup': round(phases['setup'], 1),
            'residual': round(max(0.0, results['wall_ms'] - accounted), 1),
        }
        results['model_calls'] = 0
        return results


def main(argv=None):
    ap = argparse.ArgumentParser(description='S2 flip live-run harness')
    ap.add_argument('--run', type=int, required=True)
    ap.add_argument('--browser', choices=['brave', 'chromium', 'both'],
                    default='both')
    ap.add_argument('--dry-run', action='store_true')
    ap.add_argument('--activate', action='store_true',
                    help='C5-A1: Target.activateTarget + Page.bringToFront '
                         'before each send (CDP-only, no screen change)')
    ap.add_argument('--message-prefix', default='S2-FLIP',
                    help='prefix for the unique test message per send')
    ap.add_argument('--set-value', action='store_true',
                    help='C5-B1: landed set_value program (no mouse: '
                         'set_value + focus + key Enter + assert) '
                         'forces set_value on Chromium; Brave already '
                         'uses set_value')
    ap.add_argument('--chromium-set-value', action='store_true',
                    help='C5-S2-REOPEN: landed set_value program on '
                         'Chromium only; Brave already uses set_value')
    ap.add_argument('--transport', choices=['broker', 'oneshot'],
                    default='broker',
                    help='send transport (A5 migrate): broker is the '
                         'default; oneshot forces the one-shot '
                         'session-driver fallback/recovery path for '
                         'the whole run')
    ap.add_argument('--workdir', required=True)
    args = ap.parse_args(argv)
    browsers = ['brave', 'chromium'] if args.browser == 'both' else [args.browser]
    harness = Harness(args.workdir, args.run, dry_run=args.dry_run,
                      activate=args.activate,
                      message_prefix=args.message_prefix,
                      program_variant='set_value' if args.set_value else 'fill',
                      chromium_set_value=args.chromium_set_value,
                      transport=args.transport)
    results = harness.run(browsers)
    out_path = Path(args.workdir) / ('run-%d.json' % args.run)
    out_path.write_text(json.dumps(results, indent=2, ensure_ascii=False) + '\n')
    print(json.dumps({'run': args.run, 'wall_ms': results.get('wall_ms'),
                      'outcomes': {b: r.get('outcome')
                                   for b, r in results.get('browsers', {}).items()},
                      'json': str(out_path)}, ensure_ascii=False))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
