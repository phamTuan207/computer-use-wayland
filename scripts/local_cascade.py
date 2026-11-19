#!/usr/bin/env python3
"""Local small-model cascade for routine loop steps (Track 2, Rank 1 / M4).

Prototype for Pham Tuan's computer-use speed program. A small local text
model (Qwen2.5-3B-Instruct, 4-bit, served by llama-server on the laptop
GPU) handles the routine, checkable steps: windows listing, first observe
verification, and finish confirmation. Luna 6 Max handles only the hard
steps: act composition and genuine ambiguity or recovery.

Opt-in only: every rule in this module is inert unless the environment
variable CU_LOCAL_CASCADE is set to ``1``. Default is OFF, so the baseline
loop is byte-identical when the flag is unset.

This is NOT Pick 2. Pick 2 failed because it used a fresh REMOTE codex exec
per routine decision (about 22s wall, about 18k uncached tokens, 1 of 2
wrong). A LOCAL small model is a different route: no network round trip,
no fresh session, about 2.8s per call measured for UI-TARS-2B-SFT on this
laptop, used here only as a local-call latency reference.

Escalation is deterministic, never a judgment call by the small model.
A routine answer is used only when ALL of these hold:
- the transport returned valid JSON matching the step schema,
- the reported confidence is at or above CONFIDENCE_THRESHOLD (0.70),
- the deterministic postcondition passes:
  - windows: the returned address exists in the clients list given,
  - verify/finish: a pass=true answer cites evidence that appears
    verbatim (whitespace-normalised) in the observation text,
- the call finished inside REQUEST_TIMEOUT_S.
Anything else returns escalate=true with a machine-readable reason, and
the executor falls back to a Luna think call for that step. Act
composition is NEVER routed to the small model.

Transport: plain stdlib urllib POST to the llama-server /completion
endpoint. The server owns the model file and the GPU; this module owns
only prompts, validation, and escalation. No broker, no desktop, no
model calls at import time.

No em dash or en dash in this file.
"""

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

FLAG_ENV = 'CU_LOCAL_CASCADE'
SERVER_ENV = 'CU_CASCADE_SERVER'
DEFAULT_SERVER = 'http://127.0.0.1:8088'

# Deterministic escalation threshold. A routine answer below this
# confidence is not used, whatever the model says about itself.
CONFIDENCE_THRESHOLD = 0.70

# A bounded routine decision is a short JSON object, so it never needs
# a long answer. The cap is enforced on the server call, not by the model.
MAX_OUTPUT_TOKENS = 256

# A local call should take about 3s. A hung server must escalate, never
# hang the loop.
REQUEST_TIMEOUT_S = 30

# Routine verify inputs are short command outputs. Truncate so a huge
# observation cannot blow up the local prompt.
MAX_OBSERVATION_CHARS = 4000
MAX_CLIENTS = 64

WINDOWS_SCHEMA = {
    "type": "object",
    "properties": {
        "address": {"type": ["string", "null"]},
        "confidence": {"type": "number"},
    },
    "required": ["address", "confidence"],
    "additionalProperties": False,
}

VERIFY_SCHEMA = {
    "type": "object",
    "properties": {
        "pass": {"type": "boolean"},
        "evidence": {"type": "string"},
        "confidence": {"type": "number"},
    },
    "required": ["pass", "evidence", "confidence"],
    "additionalProperties": False,
}


def enabled():
    """True only when CU_LOCAL_CASCADE is exactly '1'."""
    return os.environ.get(FLAG_ENV) == '1'


def server_url():
    """llama-server base URL, overridable for tests and the gate."""
    return os.environ.get(SERVER_ENV, DEFAULT_SERVER).rstrip('/')


def _chat_prompt(system, user):
    """Plain Qwen2.5 chat-format prompt, no tokenizer dependency."""
    return (
        "<|im_start|>system\n" + system + "<|im_end|>\n"
        "<|im_start|>user\n" + user + "<|im_end|>\n"
        "<|im_start|>assistant\n"
    )


def build_windows_prompt(clients, goal):
    """Prompt for the windows-listing routine step.

    clients is a list of dicts with at least address, class, title,
    workspace, focused. The model must return exactly one address from
    the list, or null when no listed window matches the goal.
    """
    lines = []
    for client in clients[:MAX_CLIENTS]:
        lines.append(
            "address={address} class={klass} title={title} "
            "workspace={workspace} focused={focused}".format(
                address=client.get('address', '?'),
                klass=client.get('class', '?'),
                title=(client.get('title', '?') or '?')[:120],
                workspace=client.get('workspace', {}).get('name', '?')
                if isinstance(client.get('workspace'), dict)
                else client.get('workspace', '?'),
                focused=client.get('focused', False),
            )
        )
    system = (
        "You pick one window from the list. Reply with JSON only, "
        "exactly {\"address\": \"<address>\", \"confidence\": <0 to 1>}. "
        "Use the address exactly as listed. Use null for address when "
        "no listed window matches the goal. Confidence is your "
        "certainty that the picked window is the right one."
    )
    user = "Goal: {goal}\nWindows:\n{windows}".format(
        goal=goal, windows="\n".join(lines) if lines else "(no windows)")
    return _chat_prompt(system, user)


def build_verify_prompt(observation, condition):
    """Prompt for the verify routine step.

    The model judges whether the condition holds in the observation and
    must cite the exact line that proves it. The citation is checked
    verbatim by validate_verify, so a hallucinated citation escalates.
    """
    system = (
        "You judge one condition against the observation text. Reply "
        "with JSON only, exactly {\"pass\": true or false, "
        "\"evidence\": \"<exact line from the observation>\", "
        "\"confidence\": <0 to 1>}. Evidence must be copied exactly "
        "from the observation, not paraphrased. When the condition "
        "fails, evidence is the exact line that shows the real value. "
        "Use an empty evidence string only when no line is relevant."
    )
    user = "Condition: {condition}\nObservation:\n{observation}".format(
        condition=condition,
        observation=observation[:MAX_OBSERVATION_CHARS])
    return _chat_prompt(system, user)


def build_finish_prompt(final_text, goal):
    """Prompt for the finish-confirmation routine step.

    Same shape as verify: the goal is done only when the final state
    text proves it, with a verbatim citation.
    """
    system = (
        "You judge whether the goal is DONE from the final state text. "
        "Reply with JSON only, exactly {\"pass\": true or false, "
        "\"evidence\": \"<exact line from the final state>\", "
        "\"confidence\": <0 to 1>}. Evidence must be copied exactly "
        "from the final state, not paraphrased. Pass true only when "
        "the text proves the goal is complete."
    )
    user = "Goal: {goal}\nFinal state:\n{state}".format(
        goal=goal, state=final_text[:MAX_OBSERVATION_CHARS])
    return _chat_prompt(system, user)


def _http_complete(server, prompt, schema):
    """One llama-server /completion call. Returns the parsed JSON dict.

    Raises on transport failure, non-200 status, or bad JSON, so the
    caller can escalate deterministically.
    """
    body = json.dumps({
        "prompt": prompt,
        "json_schema": schema,
        "n_predict": MAX_OUTPUT_TOKENS,
        "temperature": 0,
        "stop": ["<|im_end|>", "<|endoftext|>"],
    }).encode('utf-8')
    request = urllib.request.Request(
        server + '/completion', data=body,
        headers={'Content-Type': 'application/json'}, method='POST')
    try:
        with urllib.request.urlopen(request, timeout=REQUEST_TIMEOUT_S) as resp:
            payload = json.loads(resp.read().decode('utf-8'))
    except urllib.error.HTTPError as exc:
        raise RuntimeError('server HTTP %s' % exc.code) from exc
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        raise RuntimeError('transport failed: %s' % exc) from exc
    content = payload.get('content', '')
    if not content:
        raise RuntimeError('empty completion')
    try:
        return json.loads(content)
    except json.JSONDecodeError as exc:
        raise RuntimeError('bad JSON: %s' % exc) from exc


def complete(prompt, schema, transport=None):
    """Run one routine completion.

    transport, when given, is a callable (prompt, schema) -> dict used
    by tests instead of the HTTP call. Returns (result, latency_ms,
    error). result is None when error is set.
    """
    started = time.monotonic()
    try:
        if transport is not None:
            result = transport(prompt, schema)
        else:
            result = _http_complete(server_url(), prompt, schema)
    except Exception as exc:  # noqa: BLE001 - any failure escalates
        return None, (time.monotonic() - started) * 1000.0, str(exc)
    if not isinstance(result, dict):
        return None, (time.monotonic() - started) * 1000.0, 'not an object'
    return result, (time.monotonic() - started) * 1000.0, None


def _norm(text):
    """Whitespace-normalised text for verbatim evidence matching."""
    return ' '.join(str(text).split())


def _confidence_ok(result):
    """Confidence must be a number at or above the threshold."""
    confidence = result.get('confidence')
    if isinstance(confidence, bool) or not isinstance(confidence, (int, float)):
        return False, 'confidence missing or not a number'
    if confidence < CONFIDENCE_THRESHOLD:
        return False, 'confidence %.2f below %.2f' % (
            confidence, CONFIDENCE_THRESHOLD)
    return True, ''


def _escalate(step, reason, latency_ms):
    return {
        'step': step, 'escalate': True, 'reason': reason,
        'latency_ms': round(latency_ms, 1),
    }


def validate_window_choice(result, clients):
    """Deterministic postcondition for the windows step.

    Returns (ok, reason). The address must exist in the clients list,
    or be null (which is a valid 'no match' answer that still needs
    confidence at threshold to be used).
    """
    ok, reason = _confidence_ok(result)
    if not ok:
        return False, reason
    known = {str(c.get('address')) for c in clients}
    address = result.get('address')
    if address is None:
        return True, ''
    if str(address) not in known:
        return False, 'address %s not in window list' % address
    return True, ''


def validate_verify(result, observation):
    """Deterministic postcondition for the verify/finish steps.

    Returns (ok, reason). A pass=true answer must cite evidence that
    appears verbatim in the observation. A pass=false answer must cite
    the line showing the real value, unless no line is relevant.
    """
    ok, reason = _confidence_ok(result)
    if not ok:
        return False, reason
    if not isinstance(result.get('pass'), bool):
        return False, 'pass missing or not a boolean'
    evidence = result.get('evidence')
    if not isinstance(evidence, str):
        return False, 'evidence missing or not a string'
    if result['pass'] and not _norm(evidence):
        return False, 'pass=true without evidence'
    if _norm(evidence) and _norm(evidence) not in _norm(observation):
        return False, 'evidence not verbatim in observation'
    return True, ''


def pick_window(clients, goal, transport=None):
    """Routine windows step via the local model, with escalation.

    Returns a dict with step, address (or None), confidence, escalate,
    reason, latency_ms. escalate=true means the executor must fall back
    to a Luna think call for this step.
    """
    prompt = build_windows_prompt(clients, goal)
    result, latency_ms, error = complete(prompt, WINDOWS_SCHEMA, transport)
    if error is not None:
        return _escalate('windows', error, latency_ms)
    ok, reason = validate_window_choice(result, clients)
    if not ok:
        return _escalate('windows', reason, latency_ms)
    return {
        'step': 'windows', 'address': result.get('address'),
        'confidence': result.get('confidence'), 'escalate': False,
        'reason': '', 'latency_ms': round(latency_ms, 1),
    }


def verify_condition(observation, condition, transport=None):
    """Routine verify step via the local model, with escalation."""
    prompt = build_verify_prompt(observation, condition)
    result, latency_ms, error = complete(prompt, VERIFY_SCHEMA, transport)
    if error is not None:
        return _escalate('verify', error, latency_ms)
    ok, reason = validate_verify(result, observation)
    if not ok:
        return _escalate('verify', reason, latency_ms)
    return {
        'step': 'verify', 'pass': result['pass'],
        'evidence': result.get('evidence', ''),
        'confidence': result.get('confidence'), 'escalate': False,
        'reason': '', 'latency_ms': round(latency_ms, 1),
    }


def confirm_finish(final_text, goal, transport=None):
    """Routine finish-confirmation step via the local model."""
    prompt = build_finish_prompt(final_text, goal)
    result, latency_ms, error = complete(prompt, VERIFY_SCHEMA, transport)
    if error is not None:
        return _escalate('finish', error, latency_ms)
    ok, reason = validate_verify(result, final_text)
    if not ok:
        return _escalate('finish', reason, latency_ms)
    return {
        'step': 'finish', 'pass': result['pass'],
        'evidence': result.get('evidence', ''),
        'confidence': result.get('confidence'), 'escalate': False,
        'reason': '', 'latency_ms': round(latency_ms, 1),
    }


def _read_input(path):
    if path == '-':
        return sys.stdin.read()
    return Path(path).read_text(encoding='utf-8')


def main(argv=None):
    """CLI: windows | verify | finish | health. Prints one JSON object.

    Exit 0 on every handled outcome, including escalate=true. Exit 2
    on CLI usage errors. The executor reads stdout JSON only.
    """
    parser = argparse.ArgumentParser(
        prog='local_cascade',
        description='Route a routine loop step to the local small model.')
    sub = parser.add_subparsers(dest='command', required=True)
    p_win = sub.add_parser('windows', help='pick one window from a list')
    p_win.add_argument('--clients', required=True,
                       help='hyprctl clients JSON file, or - for stdin')
    p_win.add_argument('--goal', required=True)
    p_ver = sub.add_parser('verify', help='judge a condition on text')
    p_ver.add_argument('--observation', required=True,
                       help='observation text file, or - for stdin')
    p_ver.add_argument('--condition', required=True)
    p_fin = sub.add_parser('finish', help='confirm the goal is done')
    p_fin.add_argument('--final-state', required=True,
                       help='final state text file, or - for stdin')
    p_fin.add_argument('--goal', required=True)
    sub.add_parser('health', help='check the local server answers')
    args = parser.parse_args(argv)
    if not enabled():
        print(json.dumps({
            'escalate': True,
            'reason': 'CU_LOCAL_CASCADE is not 1 (cascade disabled)',
        }))
        return 0
    if args.command == 'health':
        try:
            with urllib.request.urlopen(
                    server_url() + '/health',
                    timeout=REQUEST_TIMEOUT_S) as resp:
                body = json.loads(resp.read().decode('utf-8'))
            print(json.dumps({'ok': True, 'health': body}))
        except Exception as exc:  # noqa: BLE001 - health reports, not raises
            print(json.dumps({'ok': False, 'error': str(exc)}))
        return 0
    if args.command == 'windows':
        clients = json.loads(_read_input(args.clients))
        print(json.dumps(pick_window(clients, args.goal)))
        return 0
    if args.command == 'verify':
        observation = _read_input(args.observation)
        print(json.dumps(verify_condition(observation, args.condition)))
        return 0
    if args.command == 'finish':
        final_text = _read_input(args.final_state)
        print(json.dumps(confirm_finish(final_text, args.goal)))
        return 0
    parser.error('unknown command')
    return 2


if __name__ == '__main__':
    raise SystemExit(main())
