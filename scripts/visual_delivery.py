"""Session-local delivery hints; exact visual duplicates never imply app success."""
import hashlib
import io
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
            image_bytes = Path(path).read_bytes()
            if (meta.get('image_format')!='JPEG' or meta.get('image_bytes')!=len(image_bytes) or
                    meta.get('image_sha256')!=hashlib.sha256(image_bytes).hexdigest()):
                raise ValueError('returned image does not match its observation identity')
            from PIL import Image
            with Image.open(io.BytesIO(image_bytes)) as decoded:
                decoded.load()
                if decoded.format!='JPEG' or list(decoded.size)!=meta['image_size']:
                    raise ValueError('returned image dimensions do not match its observation identity')
            frame = [meta[k] for k in ('scope', 'window', 'monitor', 'region', 'image_size',
                                      'monitor_box', 'monitor_scale', 'monitor_transform')
                     if k != 'window' or meta['scope'] == 'window']
            if meta['scope'] == 'window':frame.append(meta['window_bounds'])
            key = (meta['image_sha256'], json.dumps(frame))
        except (OSError, ValueError, KeyError, TypeError):
            self.clear()
            return {**required, 'reason': 'visual identity unavailable'}
        old = self.previous
        if old and old[0] == key and Path(old[1]).exists():
            return {'status': 'unchanged', 'path': path, 'same_as': old[1],
                    'reason': 'exact JPEG and coordinate frame match; not proof of app success'}
        self.previous = (key, path)
        return {**required, 'reason': 'first or changed visual frame'}
