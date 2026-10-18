"""Session-local delivery hints; exact visual duplicates never imply app success."""
import hashlib
import json
from pathlib import Path


class VisualCheckpoint:
    def __init__(self):
        self.previous = None

    def clear(self):
        self.previous = None

    def assess(self, response):
        result = response.get('result')
        if not isinstance(result, dict):
            self.clear()
            return None
        observation = result if 'image' in result else result.get('after')
        if not isinstance(observation, dict) or not observation.get('image'):
            self.clear()
            return None
        path = observation['image']
        required = {'status': 'required', 'path': path}
        if response.get('returncode') or response.get('stderr') or result.get('ok') is False or any(
                result.get(k) for k in ('error', 'capture_error', 'ime_restore_failed', 'after_unavailable')):
            self.clear()
            return {**required, 'reason': 'error or refusal'}
        try:
            meta = json.loads(Path(observation['observation']).read_text())
            if meta['backend'] != 'desktop' or meta['scope'] not in ('window', 'screen') or meta['image'] != path:
                raise ValueError('not a matching desktop observation')
            # Same pixels in another window/crop/monitor are not the same coordinate frame.
            frame = [meta[k] for k in ('scope', 'window', 'monitor', 'region', 'image_size',
                                      'monitor_box', 'monitor_scale', 'monitor_transform')
                     if k != 'window' or meta['scope'] == 'window']
            if meta['scope'] == 'window':frame.append(meta['window_bounds'])
            key = (hashlib.sha256(Path(path).read_bytes()).hexdigest(), json.dumps(frame))
        except (OSError, ValueError, KeyError, TypeError):
            self.clear()
            return {**required, 'reason': 'visual identity unavailable'}
        old = self.previous
        if old and old[0] == key and Path(old[1]).exists():
            return {'status': 'unchanged', 'path': path, 'same_as': old[1],
                    'reason': 'exact PNG and coordinate frame match; not proof of app success'}
        self.previous = (key, path)
        return {**required, 'reason': 'first or changed visual frame'}
