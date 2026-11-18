"""Observation masking: keep only the latest screenshots in full.

Standalone prototype for prior-art ranked shortlist item 4 (The
Complexity Trap, Lindenbauer, arXiv 2508.21433, Aug 2025, entry 3.1 in
improvements/speed-prior-art.md). Masking halves cost and matches LLM
summarization on solve rate, with ZERO extra model calls. Observation
tokens are about 84 percent of an average turn (entry 3.1);
screenshot-only history does NOT improve performance, only text
history helps (OSWorld-Human, entry 3.4); long context raises
per-token cost 3.6x to 7x (entry 2.12).

Masking is a RULE (deterministic, local), NOT an LLM summarization.
Do NOT build a summarizer: per 3.1 it costs an extra model call and
is no better than masking on solve rate.

Design (executor side, local, no broker, no relay, no model call):

- A turn is one loop step the executor already ran:
  {"n": 1, "label": "obs1",
   "observation": {"image": "/path/obs1.png",
                   "description": "one line, what the screenshot showed",
                   "window": "0x..."},
   "reasoning": "...", "action": "..."}
  The description is written by the executor at observe time, in the
  same think call that already read the image. No extra call ever
  writes it. If no description was recorded, the mask line falls back
  to the label and window and never invents content.
- mask_turns: the last keep_full history turns keep their image; every
  older turn loses its image payload and gains one mask line,
  "[screenshot N masked: <one-line description>]". Reasoning and
  action text stay in full, always.
- build_think_prompt: assembles the prompt for one think call. The
  prompt carries at most keep_full images in total. The current
  observation is ALWAYS fresh pixels and always occupies one slot;
  masking applies only to HISTORY, never to the observation the model
  is acting on now. With keep_full=2 the prompt holds the current
  image plus the latest 1 history image; everything older is a text
  line.
- Flag CU_MASK_HISTORY=1 turns masking on. Flag off: apply_mask and
  build_think_prompt return the input unchanged, byte-identical to
  today (every observation image stays in the prompt).

This module is pure stdlib. It never reads an image, never touches
the desktop, never calls a model, never talks to the broker.
"""

import argparse
import copy
import json
import os
import sys

MASK_ENV_VAR = 'CU_MASK_HISTORY'

# Cap on full images in one think prompt: the current observation plus
# the latest history images. Default 2 (prior-art 3.1: latest 1 to 2).
MAX_FULL_SCREENSHOTS = 2

# A mask line is one line of text, never a paragraph.
MASK_LINE_MAX_CHARS = 200

_TRUTHY = frozenset({'1', 'true', 'yes', 'on'})
_FALSY = frozenset({'0', 'false', 'no', 'off', ''})


def mask_enabled(env=None):
    """True only when the opt-in flag is set. Default OFF."""
    source = os.environ if env is None else env
    value = str(source.get(MASK_ENV_VAR, '')).strip().lower()
    return value in _TRUTHY


def _one_line(text, limit=MASK_LINE_MAX_CHARS):
    """Collapse a description to one line, capped, never empty."""
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


def mask_line(observation, *, n=None, label=None):
    """One mask line for an older observation.

    Format: "[screenshot N masked: <one-line description>]". The
    description is the one recorded at observe time. When nothing was
    recorded, the line says so and never invents content.
    """
    if not isinstance(observation, dict):
        observation = {}
    number = n
    if number is None:
        number = _turn_number({'n': observation.get('n'),
                               'label': label or observation.get('label')})
    if number is None:
        number = '?'
    description = (observation.get('description')
                   or observation.get('text_summary')
                   or observation.get('summary') or '')
    window = observation.get('window') or observation.get('address') or ''
    label_text = label or observation.get('label') or ''
    if description:
        detail = _one_line(description)
    elif window and label_text:
        detail = 'observation %s, window %s' % (label_text, window)
    elif window:
        detail = 'window %s' % window
    elif label_text:
        detail = 'observation %s' % label_text
    else:
        detail = '(no description recorded)'
    return '[screenshot %s masked: %s]' % (number, detail)


def count_images(turns):
    """How many turns still carry a full image payload."""
    return sum(1 for turn in (turns or []) if _image_of(turn) is not None)


def mask_turns(turns, *, keep_full=MAX_FULL_SCREENSHOTS):
    """Mask older observation images in a turn history.

    Returns a NEW list; the input is never mutated. The last
    ``keep_full`` turns keep their image in full; every older turn
    loses its image payload (image becomes None, masked becomes True)
    and gains its mask line. Reasoning and action text are kept in
    full on every turn, masked or not.
    """
    if keep_full < 0:
        raise ValueError('keep_full must be zero or more')
    items = copy.deepcopy(list(turns or []))
    if keep_full >= len(items):
        return items
    cut = len(items) - keep_full if keep_full else len(items)
    for turn in items[:cut]:
        observation = _observation_of(turn)
        line = mask_line(observation,
                         n=_turn_number(turn),
                         label=turn.get('label') if isinstance(turn, dict) else None)
        masked = dict(observation)
        masked['image'] = None
        masked['masked'] = True
        masked['mask_line'] = line
        if isinstance(turn, dict):
            turn['observation'] = masked
    return items


def apply_mask(turns, *, env=None, keep_full=MAX_FULL_SCREENSHOTS):
    """Flag-gated masking.

    Flag on: mask_turns. Flag off: return the input UNCHANGED, the
    very same list object, byte-identical to today.
    """
    if not mask_enabled(env):
        return turns
    return mask_turns(turns, keep_full=keep_full)


def build_think_prompt(turns, current_observation, *, env=None,
                       keep_full=MAX_FULL_SCREENSHOTS):
    """Assemble the prompt for one think call.

    Returns a dict with prompt_text, image_paths, masked_count and
    kept_count. The prompt carries at most ``keep_full`` images in
    total. The current observation is ALWAYS fresh pixels and always
    occupies one image slot; masking applies only to HISTORY. With
    keep_full=2 the prompt holds the current image plus the latest 1
    history image. When the flag is off, every history image stays in
    the prompt, exactly as today.
    """
    if keep_full < 0:
        raise ValueError('keep_full must be zero or more')
    history = list(turns or [])
    enabled = mask_enabled(env)
    current = current_observation if isinstance(current_observation, dict) else {}
    current_image = current.get('image')
    if not isinstance(current_image, str) or not current_image:
        current_image = None

    if enabled:
        # History keeps keep_full - 1 full images: the current
        # observation takes the last slot. keep_full=0 still keeps
        # the current image; it is never masked.
        keep_history = max(keep_full - 1, 0)
        masked_history = mask_turns(history, keep_full=keep_history)
        kept_images = [_image_of(turn) for turn in masked_history]
        kept_images = [path for path in kept_images if path is not None]
    else:
        masked_history = copy.deepcopy(history)
        kept_images = [_image_of(turn) for turn in masked_history]
        kept_images = [path for path in kept_images if path is not None]

    image_paths = list(kept_images)
    if current_image is not None:
        image_paths.append(current_image)
    if enabled and len(image_paths) > keep_full:
        # Defensive cap: never exceed keep_full images even if the
        # caller passed a history that already held too many.
        image_paths = image_paths[-keep_full:]

    lines = []
    if enabled:
        lines.append('# Think prompt (masked history, CU_MASK_HISTORY=1)')
    else:
        lines.append('# Think prompt (full history, masking off)')
    lines.append('## History (reasoning and actions in full;'
                 ' old screenshots masked)' if enabled else
                 '## History (reasoning and actions in full)')
    for turn in masked_history:
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
        observation = _observation_of(turn)
        if observation.get('masked'):
            lines.append('%s observation: %s'
                         % (tag, observation.get('mask_line', '')))
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
    lines.append('## Images in this prompt (%d max)' % keep_full)
    for path in image_paths:
        lines.append('- %s' % path)

    masked_count = sum(
        1 for turn in masked_history
        if isinstance(turn, dict)
        and _observation_of(turn).get('masked') is True)
    return {
        'prompt_text': '\n'.join(lines) + '\n',
        'image_paths': image_paths,
        'masked_count': masked_count,
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


def _main(argv=None):
    parser = argparse.ArgumentParser(
        description='Observation masking for think prompts.')
    sub = parser.add_subparsers(dest='command', required=True)
    mask = sub.add_parser('mask', help='mask older screenshots in a history')
    mask.add_argument('--history', required=True)
    mask.add_argument('--out', required=True)
    mask.add_argument('--keep', type=int, default=MAX_FULL_SCREENSHOTS)
    prompt = sub.add_parser('prompt', help='build one masked think prompt')
    prompt.add_argument('--history', required=True)
    prompt.add_argument('--current', required=True,
                        help='JSON file with one observation dict')
    prompt.add_argument('--out', required=True)
    prompt.add_argument('--keep', type=int, default=MAX_FULL_SCREENSHOTS)
    ns = parser.parse_args(argv)
    try:
        turns = _load_turns(ns.history)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print('mask_history: cannot read history: %s' % exc, file=sys.stderr)
        return 2
    if ns.command == 'mask':
        before = count_images(turns)
        out = apply_mask(turns, keep_full=ns.keep)
        after = count_images(out)
        with open(ns.out, 'w', encoding='utf-8') as handle:
            json.dump(out, handle, ensure_ascii=False, indent=2)
            handle.write('\n')
        print('enabled=%s images_before=%d images_after=%d masked=%d'
              % (mask_enabled(), before, after, before - after))
        return 0
    try:
        current = json.load(open(ns.current, encoding='utf-8'))
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print('mask_history: cannot read current observation: %s' % exc,
              file=sys.stderr)
        return 2
    if not isinstance(current, dict):
        print('mask_history: current observation must be a JSON object',
              file=sys.stderr)
        return 2
    result = build_think_prompt(turns, current, keep_full=ns.keep)
    with open(ns.out, 'w', encoding='utf-8') as handle:
        json.dump(result, handle, ensure_ascii=False, indent=2)
        handle.write('\n')
    print('enabled=%s images=%d masked=%d kept=%d'
          % (mask_enabled(), result['kept_count'],
             result['masked_count'], result['kept_count']))
    return 0


if __name__ == '__main__':
    raise SystemExit(_main())
