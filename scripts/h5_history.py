"""H5: drop old screenshots from history, keep only the latest plus text.

Prototype for Track 2 of the computer-use speed program (resume round 2,
19/11). Implements harness-speed-research.md section 2 H5, which refines
algorithm research A7/R7 with the FSP finding: screenshot-only history
does not improve performance; only text-based action history helps.

GATE ANSWER (checked 19/11, before this module was written): the Codex
executor does NOT support pruning old images from history. There is no
harness history builder anywhere in the repo (scripts/cu.py holds zero
occurrences of prompt/history; the history lives in the Codex executor's
own transcript). Pruning is therefore executor-side discipline via this
helper module plus the executor brief, NOT a harness change, and the
relay never sees it, so no relay restart is needed. This was already
proven by the masking prototype (scripts/mask_history.py on branch
speed-swarm-masking, 31/31 tests, live discipline verified: every prompt
carried exactly 2 images). H5 differs from masking in three ways, which
is why it is a separate prototype and not a re-run of masking:

- Keep ONE image, not two: the latest screenshot only (the current
  observation occupies the single slot; history keeps zero full images).
- The text line per old step carries the ACTION TAKEN and the RESULT,
  not just what the screenshot showed. FSP says only text action
  history helps, so the action plus result is the load-bearing text.
- A drop-entirely variant (CU_H5_DROP_TEXT=1) drops old turns with no
  text line at all, to test whether even the text lines cost think.

Design (executor side, local, no broker, no relay, no model call):

- A turn is one loop step the executor already ran:
  {"n": 1, "label": "obs1",
   "observation": {"image": "/path/obs1.png",
                   "description": "one line, what the screenshot showed",
                   "window": "0x..."},
   "reasoning": "...", "action": "...", "result": "..."}
  The description, action and result are written by the executor at
  observe time, in think calls that already read the image. No extra
  call ever writes them. If nothing was recorded, the history line says
  so and never invents content.
- prune_turns: every turn older than the keep window loses its image
  payload and gains one history line,
  "[shot N: <one-line description> | did: <action> | got: <result>]".
  Reasoning and action text stay in full, always.
- build_think_prompt: assembles the prompt for one think call. The
  prompt carries at most keep_full images in total (default 1). The
  current observation is ALWAYS fresh pixels and always occupies one
  slot; pruning applies only to HISTORY, never to the observation the
  model is acting on now. With keep_full=1 the prompt holds the current
  image only; everything older is a text line (or nothing, when
  drop_text is on).
- Flag CU_H5_DROP_OLD_SHOTS=1 turns pruning on. Flag off: apply_h5 and
  build_think_prompt return the input unchanged, byte-identical to
  today (every observation image stays in the prompt).

This module is pure stdlib. It never reads an image, never touches
the desktop, never calls a model, never talks to the broker.

Prior live result this prototype must beat or explain (Phase C masking,
04:19-05:18 19/11, verdict NO WIN provisional): masked (keep 2) slower
on every task, baseline mean wall 105.4s to masked 179.6s (+74.2s);
clean P2-P3 41.8s to 72.7s (+30.9s); broker service identical (2.3s
both arms), whole delta is think; before-act think 22.6s to 47.5s
(+24.9s). Per-step think growth FLAT in both arms; no history-growth
curve existed to cut at this task length (2-6 observations per task).
Confounders: P1 masked unusable (kitty incident), P4 masked session
death plus restart, n=1. H5 tests keep 1 (not 2) and adds a genuinely
multi-step task (M1, about 10 observations) where a growth curve can
actually exist. If H5 also shows no win, the history-pruning line is
closed with two independent negative measurements.
"""

import argparse
import copy
import json
import os
import sys

H5_ENV_VAR = 'CU_H5_DROP_OLD_SHOTS'
H5_KEEP_ENV_VAR = 'CU_H5_KEEP_FULL'
H5_DROP_TEXT_ENV_VAR = 'CU_H5_DROP_TEXT'

# Cap on full images in one think prompt: the current observation plus
# the latest history images. Default 1 (H5: latest screenshot only).
MAX_FULL_SCREENSHOTS = 1

# A history line is short text, never a paragraph.
LINE_MAX_CHARS = 240
FIELD_MAX_CHARS = 120

_TRUTHY = frozenset({'1', 'true', 'yes', 'on'})
_FALSY = frozenset({'0', 'false', 'no', 'off', ''})


def h5_enabled(env=None):
    """True only when the opt-in flag is set. Default OFF."""
    source = os.environ if env is None else env
    value = str(source.get(H5_ENV_VAR, '')).strip().lower()
    return value in _TRUTHY


def h5_keep_full(env=None):
    """Keep-full override from the environment. Default 1.

    Must be 1 or more: the current observation always occupies one
    slot and is never pruned. Raises ValueError on a bad value.
    """
    source = os.environ if env is None else env
    raw = str(source.get(H5_KEEP_ENV_VAR, '')).strip()
    if raw == '':
        return MAX_FULL_SCREENSHOTS
    try:
        value = int(raw)
    except ValueError:
        raise ValueError('CU_H5_KEEP_FULL must be an integer, got %r' % raw)
    if value < 1:
        raise ValueError('CU_H5_KEEP_FULL must be 1 or more, got %d' % value)
    return value


def h5_drop_text(env=None):
    """True only when the drop-entirely variant flag is set."""
    source = os.environ if env is None else env
    value = str(source.get(H5_DROP_TEXT_ENV_VAR, '')).strip().lower()
    return value in _TRUTHY


def _one_line(text, limit=FIELD_MAX_CHARS):
    """Collapse a field to one line, capped, never empty."""
    flat = ' '.join(str(text or '').split())
    if len(flat) > limit:
        flat = flat[:limit].rstrip() + '...'
    return flat


def _turn_number(turn):
    """Step number for a turn, from n, then label digits, else None."""
    if isinstance(turn, dict):
        number = turn.get('n')
        if isinstance(number, int):
            return number
        label = turn.get('label')
        if isinstance(label, str):
            digits = ''.join(ch for ch in label if ch.isdigit())
            if digits:
                return int(digits)
    return None


def _observation_of(turn):
    """Return the observation dict of a turn, or {} when absent."""
    if not isinstance(turn, dict):
        return {}
    observation = turn.get('observation')
    if isinstance(observation, dict):
        return observation
    if isinstance(observation, str):
        return {'description': observation}
    return {}


def _image_of(turn):
    observation = _observation_of(turn)
    image = observation.get('image')
    return image if isinstance(image, str) and image else None


def history_line(turn):
    """One history line for an older turn.

    Format: "[shot N: <one-line description> | did: <action> |
    got: <result>]". The description, action and result are the ones
    recorded at observe time. When nothing was recorded for a field,
    the line says so and never invents content.
    """
    if not isinstance(turn, dict):
        return '[shot ?: (unrecorded turn)]'
    number = _turn_number(turn)
    tag = number if number is not None else '?'
    observation = _observation_of(turn)
    description = (observation.get('description')
                   or observation.get('text_summary')
                   or observation.get('summary') or '')
    if description:
        detail = _one_line(description)
    else:
        window = observation.get('window') or observation.get('address') or ''
        label_text = turn.get('label') or observation.get('label') or ''
        if window and label_text:
            detail = 'observation %s, window %s' % (label_text, window)
        elif window:
            detail = 'window %s' % window
        elif label_text:
            detail = 'observation %s' % label_text
        else:
            detail = '(no description recorded)'
    action = turn.get('action')
    did = _one_line(action) if isinstance(action, str) and action.strip() \
        else '(no action recorded)'
    result = turn.get('result')
    got = _one_line(result) if isinstance(result, str) and result.strip() \
        else '(no result recorded)'
    line = '[shot %s: %s | did: %s | got: %s]' % (tag, detail, did, got)
    if len(line) > LINE_MAX_CHARS:
        line = line[:LINE_MAX_CHARS].rstrip() + '...'
    return line


def count_images(turns):
    """How many turns still carry a full image payload."""
    return sum(1 for turn in (turns or []) if _image_of(turn) is not None)


def prune_turns(turns, *, keep_full=MAX_FULL_SCREENSHOTS, drop_text=False):
    """Prune older observation images in a turn history.

    Returns a NEW list; the input is never mutated. The last
    ``keep_full`` turns keep their image in full; every older turn
    loses its image payload (image becomes None, pruned becomes True)
    and gains its history line, unless drop_text is on, in which case
    the older turn keeps no text line at all. Reasoning and action
    text are kept in full on every turn, pruned or not.
    """
    if keep_full < 0:
        raise ValueError('keep_full must be zero or more')
    items = copy.deepcopy(list(turns or []))
    if keep_full >= len(items):
        return items
    cut = len(items) - keep_full if keep_full else len(items)
    for turn in items[:cut]:
        observation = _observation_of(turn)
        masked = dict(observation)
        masked['image'] = None
        masked['pruned'] = True
        if drop_text:
            masked['history_line'] = None
        else:
            masked['history_line'] = history_line(turn)
        if isinstance(turn, dict):
            turn['observation'] = masked
    return items


def apply_h5(turns, *, env=None, keep_full=None, drop_text=None):
    """Flag-gated pruning.

    Flag on: prune_turns with the keep window (default 1) and the
    drop-text variant. Flag off: return the input UNCHANGED, the very
    same list object, byte-identical to today.
    """
    if not h5_enabled(env):
        return turns
    keep = h5_keep_full(env) if keep_full is None else keep_full
    drop = h5_drop_text(env) if drop_text is None else drop_text
    return prune_turns(turns, keep_full=keep, drop_text=drop)


def build_think_prompt(turns, current_observation, *, env=None,
                       keep_full=None, drop_text=None):
    """Assemble the prompt for one think call.

    Returns a dict with prompt_text, image_paths, pruned_count and
    kept_count. The prompt carries at most ``keep_full`` images in
    total (default 1). The current observation is ALWAYS fresh pixels
    and always occupies one image slot; pruning applies only to
    HISTORY. With keep_full=1 the prompt holds the current image only.
    When the flag is off, every history image stays in the prompt,
    exactly as today.
    """
    keep = h5_keep_full(env) if keep_full is None else keep_full
    if keep < 1:
        raise ValueError('keep_full must be 1 or more, got %r' % (keep,))
    drop = h5_drop_text(env) if drop_text is None else drop_text
    history = list(turns or [])
    enabled = h5_enabled(env)
    current = current_observation if isinstance(current_observation, dict) else {}
    current_image = current.get('image')
    if not isinstance(current_image, str) or not current_image:
        current_image = None

    if enabled:
        # History keeps keep_full - 1 full images: the current
        # observation takes the last slot. keep_full=1 keeps zero
        # history images; the current image is never pruned.
        keep_history = max(keep - 1, 0)
        pruned_history = prune_turns(history, keep_full=keep_history,
                                     drop_text=drop)
        kept_images = [_image_of(turn) for turn in pruned_history]
        kept_images = [path for path in kept_images if path is not None]
    else:
        pruned_history = copy.deepcopy(history)
        kept_images = [_image_of(turn) for turn in pruned_history]
        kept_images = [path for path in kept_images if path is not None]

    image_paths = list(kept_images)
    if current_image is not None:
        image_paths.append(current_image)
    if enabled and len(image_paths) > keep:
        # Defensive cap: never exceed keep_full images even if the
        # caller passed a history that already held too many.
        image_paths = image_paths[-keep:]

    lines = []
    if enabled:
        lines.append('# Think prompt (pruned history, CU_H5_DROP_OLD_SHOTS=1)')
    else:
        lines.append('# Think prompt (full history, H5 off)')
    lines.append('## History (reasoning and actions in full;'
                 ' old screenshots pruned)' if enabled else
                 '## History (reasoning and actions in full)')
    for turn in pruned_history:
        if not isinstance(turn, dict):
            continue
        number = _turn_number(turn)
        tag = '[step %s]' % number if number is not None else '[step ?]'
        reasoning = turn.get('reasoning')
        if isinstance(reasoning, str) and reasoning:
            lines.append('%s reasoning: %s' % (tag, reasoning))
        action = turn.get('action')
        if isinstance(action, str) and action:
            lines.append('%s action: %s' % (tag, action))
        result = turn.get('result')
        if isinstance(result, str) and result:
            lines.append('%s result: %s' % (tag, result))
        observation = _observation_of(turn)
        if observation.get('pruned'):
            line = observation.get('history_line')
            if line:
                lines.append('%s observation: %s' % (tag, line))
            else:
                lines.append('%s observation: (dropped, no text)' % tag)
        elif _image_of(turn) is not None:
            lines.append('%s observation image: %s' % (tag, _image_of(turn)))
        elif observation:
            description = observation.get('description') or ''
            if description:
                lines.append('%s observation: %s' % (tag, _one_line(description)))
    lines.append('## Current observation (fresh, full image)')
    if current_image is not None:
        lines.append('image: %s' % current_image)
        description = current.get('description') or ''
        if description:
            lines.append('description: %s' % _one_line(description))
    else:
        lines.append('(no current image)')
    lines.append('## Images in this prompt (%d max)' % keep)
    for path in image_paths:
        lines.append('- %s' % path)

    pruned_count = sum(
        1 for turn in pruned_history
        if isinstance(turn, dict)
        and _observation_of(turn).get('pruned') is True)
    return {
        'prompt_text': '\n'.join(lines) + '\n',
        'image_paths': image_paths,
        'pruned_count': pruned_count,
        'kept_count': len(image_paths),
    }


def _load_turns(path):
    """Load a history file: a JSON list of turns, or JSONL turns."""
    text = open(path, encoding='utf-8').read()
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        data = None
    if isinstance(data, list):
        return data
    turns = []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        turns.append(json.loads(line))
    if not all(isinstance(turn, dict) for turn in turns):
        raise ValueError('history file must hold a JSON list of turns'
                         ' or one JSON turn per line')
    return turns


def _write_json_600(path, payload):
    """Write JSON with mode 600 (turns carry observation paths)."""
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    try:
        os.write(fd, (json.dumps(payload, ensure_ascii=False, indent=2)
                      + '\n').encode('utf-8'))
    finally:
        os.close(fd)


def _main(argv=None):
    parser = argparse.ArgumentParser(
        description='H5: drop old screenshots from think prompts.')
    sub = parser.add_subparsers(dest='command', required=True)
    prune = sub.add_parser('prune', help='prune older screenshots in a history')
    prune.add_argument('--history', required=True)
    prune.add_argument('--out', required=True)
    prune.add_argument('--keep', type=int, default=None,
                       help='full images to keep (default: 1, or CU_H5_KEEP_FULL)')
    prune.add_argument('--drop-text', action='store_true',
                       help='drop old turns entirely, no text line')
    prompt = sub.add_parser('prompt', help='build one pruned think prompt')
    prompt.add_argument('--history', required=True)
    prompt.add_argument('--current', required=True,
                        help='JSON file with one observation dict')
    prompt.add_argument('--out', required=True)
    prompt.add_argument('--keep', type=int, default=None,
                        help='full images in the prompt (default: 1)')
    prompt.add_argument('--drop-text', action='store_true',
                        help='drop old turns entirely, no text line')
    ns = parser.parse_args(argv)
    keep = ns.keep if ns.keep is not None else h5_keep_full()
    if keep < 1:
        print('h5_history: --keep must be 1 or more', file=sys.stderr)
        return 2
    drop = bool(ns.drop_text) or h5_drop_text()
    try:
        turns = _load_turns(ns.history)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print('h5_history: cannot read history: %s' % exc, file=sys.stderr)
        return 2
    if ns.command == 'prune':
        before = count_images(turns)
        out = apply_h5(turns, keep_full=keep, drop_text=drop)
        after = count_images(out)
        _write_json_600(ns.out, out)
        print('enabled=%s images_before=%d images_after=%d pruned=%d'
              % (h5_enabled(), before, after, before - after))
        return 0
    try:
        current = json.load(open(ns.current, encoding='utf-8'))
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print('h5_history: cannot read current observation: %s' % exc,
              file=sys.stderr)
        return 2
    if not isinstance(current, dict):
        print('h5_history: current observation must be a JSON object',
              file=sys.stderr)
        return 2
    result = build_think_prompt(turns, current, keep_full=keep,
                                drop_text=drop)
    _write_json_600(ns.out, result)
    print('enabled=%s images=%d pruned=%d kept=%d'
          % (h5_enabled(), result['kept_count'],
             result['pruned_count'], result['kept_count']))
    return 0


if __name__ == '__main__':
    raise SystemExit(_main())
