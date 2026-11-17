#!/usr/bin/env python3
"""Run the checked tc02-v1 plan through the local broker."""
import argparse
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import time


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PLAN = ROOT / 'scripts' / 'plans' / 'tc02-v1.json'
DEFAULT_SCHEMA = ROOT / 'scripts' / 'plans' / 'tc02.schema.json'
DEFAULT_RUNS = Path('/tmp/opt-impl-step1-runs')
DEFAULT_TRACE = Path('/tmp/opencode/multipage-l3/tc02-t3/evidence')
TZ = timezone(timedelta(hours=7))
T0 = datetime(2026, 11, 17, 10, 26, tzinfo=TZ)
REQUEST_TIMEOUT = 120
SAFE_RUN_ID = re.compile(r'[A-Za-z0-9_.-]{1,80}\Z')
GUI_ENV_KEYS = {
    'XDG_RUNTIME_DIR', 'WAYLAND_DISPLAY', 'DISPLAY',
    'HYPRLAND_INSTANCE_SIGNATURE', 'DBUS_SESSION_BUS_ADDRESS',
    'XDG_CURRENT_DESKTOP', 'XDG_SESSION_DESKTOP', 'XDG_SESSION_TYPE',
    'XDG_SEAT', 'XDG_VTNR', 'USER', 'HOME', 'LOGNAME', 'PATH',
    'GDK_BACKEND', 'QT_QPA_PLATFORM', 'ELECTRON_OZONE_PLATFORM_HINT',
    'MOZ_ENABLE_WAYLAND',
}
ALLOWED_BACKGROUND_CLASSES = frozenset({'zen'})
SPECIAL_WORKSPACE_PREFIX = 'special:'


class Escalate(RuntimeError):
    def __init__(self, step, checkpoint, reason, *, hygiene=False):
        self.step = step
        self.checkpoint = checkpoint
        self.reason = str(reason)
        self.hygiene = hygiene
        super().__init__(self.reason)


def wall_now():
    return datetime.now(TZ)


def wall_text():
    return wall_now().strftime('%Y-%m-%d %H:%M:%S %z')


def elapsed_s():
    return (wall_now() - T0).total_seconds()


def load_json(path):
    try:
        return json.loads(Path(path).read_text(encoding='utf-8'))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ValueError(f'cannot load JSON {path}: {exc}') from exc


def validate_plan(plan, schema):
    if not isinstance(schema, dict) or schema.get('$schema') != 'https://json-schema.org/draft/2020-12/schema':
        raise ValueError('plan schema must declare JSON Schema draft 2020-12')
    if not isinstance(plan, dict) or plan.get('schema_version') != 1 or plan.get('procedure') != 'tc02-v1':
        raise ValueError('plan identity must be schema version 1, tc02-v1')
    task = plan.get('task')
    if not isinstance(task, dict):
        raise ValueError('plan task must be an object')
    expected = task.get('text')
    if (not isinstance(expected, str) or len(expected.encode('utf-8')) != task.get('expected_bytes') or
            hashlib.sha256(expected.encode('utf-8')).hexdigest() != task.get('expected_sha256')):
        raise ValueError('plan text, byte count, and SHA-256 disagree')
    if (expected != 'Tối nay ôn cấu trúc dữ liệu lúc 20:30.\n' or
            task.get('filename') != 'on-tap.txt' or task.get('expected_bytes') != 50 or
            task.get('expected_sha256') != '8da1f5624c1b482bcdfae9d7c6883fdc52313dbe4120c2d1df2623ec5bcb9772'):
        raise ValueError('plan task differs from the byte-exact tc02 case')
    if not task.get('filename') or '/' in task['filename'] or '\\' in task['filename']:
        raise ValueError('plan filename must be a single safe path component')
    pre = plan.get('preconditions')
    if not isinstance(pre, dict) or pre.get('observation_max_age_s') != 90:
        raise ValueError('plan must keep the 90-second observation limit')
    if pre.get('editor_geometry', {}).get('size') != [901, 1176]:
        raise ValueError('validated editor geometry must be 901x1176')
    tuning = plan.get('wait_tuning', {})
    if not 0 <= tuning.get('selected_wait_ms', -1) <= 2000:
        raise ValueError('S2 wait must be between 0 and 2000 ms')
    checkpoint_sample = tuning.get('checkpoint_sample')
    checkpoint_strings = ('definition', 'measures', 'not_for')
    if (not isinstance(checkpoint_sample, dict) or
            any(not isinstance(checkpoint_sample.get(key), str) or
                not checkpoint_sample[key].strip() for key in checkpoint_strings) or
            any(type(checkpoint_sample.get(key)) is not int or checkpoint_sample[key] < 10
                for key in ('target_samples', 'minimum_samples'))):
        raise ValueError('S2 checkpoint sample definition and minimum counts are required')
    menu_open_latency = tuning.get('menu_open_latency')
    if (not isinstance(menu_open_latency, dict) or
            any(not isinstance(menu_open_latency.get(key), str) or
                not menu_open_latency[key].strip()
                for key in ('happy_path', 'point_sample_source'))):
        raise ValueError('S2 menu-open latency source and happy-path evidence are required')
    samples = tuning.get('historical_samples_ms')
    if (not isinstance(samples, list) or
            any(type(value) is not int or value < 0 for value in samples) or
            len(samples) != tuning.get('historical_valid_samples')):
        raise ValueError('S2 historical sample list and valid-sample count disagree')
    if samples:
        p95_index = (95 * len(samples) + 99) // 100 - 1
        measured_p95 = sorted(samples)[p95_index]
        if measured_p95 != tuning.get('historical_p95_upper_bound_ms'):
            raise ValueError('S2 p95 upper bound does not match the recorded sample list')
        expected_wait = min(tuning.get('cap_ms', 2000), measured_p95 + tuning.get('margin_ms', 0))
        if tuning.get('selected_wait_ms') != expected_wait:
            raise ValueError('S2 wait must equal measured p95 plus its margin, capped at 2000 ms')
    if (len(samples) < tuning.get('minimum_samples', 10) and
            'provisional' not in tuning.get('status', '').casefold()):
        raise ValueError('S2 wait must be marked provisional until the minimum sample count is met')
    coords = plan.get('coordinates')
    if not isinstance(coords, dict) or not coords:
        raise ValueError('plan must declare coordinates')
    for name, coordinate in coords.items():
        if (not isinstance(name, str) or not isinstance(coordinate, dict) or
                coordinate.get('anchor') != 'window_top_left' or
                coordinate.get('bounds_assertion') != 'inside_current_image_and_window'):
            raise ValueError(f'{name}: every coordinate needs an anchor and bounds assertion')
        offset = coordinate.get('offset')
        if (not isinstance(offset, list) or len(offset) != 2 or
                any(type(value) is not int for value in offset)):
            raise ValueError(f'{name}: coordinate offset must be two integers')
    required_coordinates = {
        'banner_close': [888, 45], 'editor_body': [200, 100],
        'file_menu': [57, 14], 'save_as_row': [95, 365],
        'name_field': [430, 22], 'save_button': [825, 22],
    }
    if {name: item.get('offset') for name, item in coords.items()} != required_coordinates:
        raise ValueError('plan coordinates differ from the reviewed tc02-v1 anchors')
    steps = plan.get('steps')
    ids = [step.get('id') for step in steps] if isinstance(steps, list) else []
    if ids != ['P0', 'P1', 'G0', 'S1', 'S2', 'S3', 'S4', 'S5', 'S6']:
        raise ValueError('tc02-v1 steps must be P0, P1, G0, S1, S2, S3, S4, S5, S6')
    expected_requests = {
        'P1': ['start'], 'G0': ['windows', 'observe'], 'S1': ['act'],
        'S2': ['act', 'windows'], 'S3': ['observe'], 'S4': ['act'],
        'S5': ['act', 'windows'], 'S6': ['observe', 'finish'],
    }
    for step in steps:
        if step.get('request_sequence', []) != expected_requests.get(step['id'], []):
            raise ValueError(f"{step['id']}: request sequence differs from the checked procedure")
        batch = step.get('batch', [])
        if not isinstance(batch, list) or len(batch) > 8:
            raise ValueError(f"{step['id']}: batch exceeds the soft cap of 8 actions")
        if step.get('kind') == 'act' and not batch:
            raise ValueError(f"{step['id']}: act step must contain a batch")
        for action in batch:
            if action.get('type') == 'click' and action.get('point') not in coords:
                raise ValueError(f"{step['id']}: click references an unknown coordinate")
            if action.get('type') == 'wait' and not 0 <= action.get('ms', -1) <= 2000:
                raise ValueError(f"{step['id']}: wait exceeds the broker limit")
    expected_batches = {
        'S1': [
            {'type': 'click', 'point': 'banner_close'},
            {'type': 'click', 'point': 'editor_body'},
            {'type': 'type', 'text': expected},
        ],
        'S2': [
            {'type': 'click', 'point': 'file_menu'},
            {'type': 'wait', 'ms': plan['wait_tuning']['selected_wait_ms']},
            {'type': 'click', 'point': 'save_as_row'},
        ],
        'S4': [
            {'type': 'click', 'point': 'name_field'},
            {'type': 'key', 'keys': ['CTRL', 'A']},
            {'type': 'type', 'text': '${output_path}'},
        ],
        'S5': [{'type': 'click', 'point': 'save_button'}],
    }
    for step_id, batch in expected_batches.items():
        if steps[ids.index(step_id)].get('batch') != batch:
            raise ValueError(f'{step_id}: action batch differs from the reviewed tc02-v1 sequence')
    if steps[4].get('batch', [None, None])[1] != {
            'type': 'wait', 'ms': plan['wait_tuning']['selected_wait_ms']}:
        raise ValueError('S2 batch wait and selected tuning value disagree')
    if steps[4].get('expected_terminal_window') != 'unbound' or not steps[4].get('no_after'):
        raise ValueError('S2 must declare an unbound successor and skip its after-capture')
    if steps[7].get('expected_terminal_window') != 'saved_editor' or not steps[7].get('no_after'):
        raise ValueError('S5 must bind the expected editor and skip the dialog after-capture')
    if not isinstance(plan.get('branches'), dict) or not plan['branches']:
        raise ValueError('plan must declare named recovery branches')
    return True


def gui_environment():
    donors = []
    for entry in Path('/proc').iterdir():
        if not entry.name.isdigit():
            continue
        try:
            if entry.joinpath('comm').read_text().strip() == 'quickshell':
                donors.append(entry)
        except OSError:
            pass
    if not donors:
        raise RuntimeError('no live quickshell process can provide the desktop environment')
    result = dict(os.environ)
    for item in donors[0].joinpath('environ').read_bytes().split(b'\0'):
        if b'=' not in item:
            continue
        key, value = item.split(b'=', 1)
        name = key.decode('ascii', 'ignore')
        if name in GUI_ENV_KEYS:
            result[name] = value.decode(errors='surrogateescape')
    result.pop('GTK_IM_MODULE', None)
    if not result.get('HYPRLAND_INSTANCE_SIGNATURE') or not result.get('WAYLAND_DISPLAY'):
        raise RuntimeError('desktop environment donor lacks Hyprland or Wayland identity')
    return result


def hypr_query(env, query):
    proc = subprocess.run(['hyprctl', '-j', query], env=env,
                          capture_output=True, text=True, timeout=5)
    if proc.returncode:
        raise RuntimeError(f'hyprctl {query} failed: {proc.stderr.strip()[:300]}')
    try:
        return json.loads(proc.stdout)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f'hyprctl {query} returned invalid JSON') from exc


def process_inventory():
    imv = []
    code = 0
    counts = {}
    for entry in Path('/proc').iterdir():
        if not entry.name.isdigit():
            continue
        try:
            pid = int(entry.name)
            comm = entry.joinpath('comm').read_text().strip()
            cmdline = entry.joinpath('cmdline').read_bytes().replace(b'\0', b' ').decode(errors='replace').strip()
        except OSError:
            continue
        counts[comm] = counts.get(comm, 0) + 1
        if comm.lower().startswith('imv'):
            imv.append({'pid': pid, 'comm': comm, 'cmdline': cmdline[:500]})
        if comm == 'code':
            code += 1
    return {'process_counts_by_name': dict(sorted(counts.items())),
            'imv_processes': imv, 'code_process_count': code}


def window_line(window):
    line = {'address': window.get('address'), 'class': window.get('class'),
            'title': window.get('title'), 'at': window.get('at'),
            'size': window.get('size')}
    workspace = window.get('workspace')
    if isinstance(workspace, dict) and 'name' in workspace:
        line['workspace'] = workspace['name']
    elif 'workspace' in window:
        line['workspace'] = workspace
    return line


def same_window_identity(actual, expected):
    return (actual.get('address') == expected.get('address') and
            actual.get('class') == expected.get('class') and
            actual.get('title') == expected.get('title'))


class Tc02Controller:
    def __init__(self, plan, run_id, output_root, *, trace_dir=None, live=False):
        self.plan = plan
        self.run_id = run_id
        self.run_dir = Path(output_root).expanduser().resolve() / run_id
        self.live = live
        self.trace_dir = Path(trace_dir) if trace_dir else None
        self.dispatch_mono = time.monotonic()
        self.step = 'P0'
        self.current_step = None
        self.current_checkpoint = 'plan-loaded'
        self.gui_env = None
        self.log_path = self.run_dir / 'executor-log.jsonl'
        self.summary_path = self.run_dir / 'run-summary.json'
        self.packet_path = self.run_dir / 'L2-packet.json'
        self.history = []
        self.s2_samples = []
        self.last_windows = []
        self.last_active_window = None
        self.last_observation = None
        self.last_image = None
        self.current_batch_size = 0
        self.current_batch_completed = 0
        self.completed_actions = 0
        self.lease_path = None
        self.editor = None
        self.dialog = None
        self.editor_observation = None
        self.dialog_observation = None
        self.generation = None
        self.broker_generation = None
        self.sequence = 1
        self.session_started = False
        self.session_finished = False
        self.process = None
        self.known_background = []
        self.metrics = {
            'task_requests': 0,
            'driver_requests': 0,
            'windows_requests': 0,
            'logical_acts': 0,
            'images_delivered': 0,
            'delivered_image_bytes': 0,
            'result_calls': 0,
            'result_poll_sleep_s': 0.0,
            'result_poll_waste_s': 0.0,
            'authenticated_status_polls': 0,
            'refusals': 0,
            'session_deaths': 0,
            'retries': 0,
            'model_round_trips': 0,
            'step_spans_s': {},
        }

    def emit(self, event, **data):
        row = {'wall': wall_text(), 'elapsed_from_T0_s': round(elapsed_s(), 3),
               'monotonic': time.monotonic(), 'event': event, **data}
        self.history.append(row)
        self.run_dir.mkdir(parents=True, exist_ok=True, mode=0o700)
        fd = os.open(self.log_path, os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o600)
        try:
            os.write(fd, (json.dumps(row, ensure_ascii=False, separators=(',', ':')) + '\n').encode())
        finally:
            os.close(fd)
        print(json.dumps(row, ensure_ascii=False, separators=(',', ':')), flush=True)

    @contextmanager
    def span(self, step):
        self.step = step
        self.current_step = next((item for item in self.plan['steps'] if item['id'] == step), None)
        start = time.monotonic()
        self.emit('step-start', step=step)
        try:
            yield
        finally:
            duration = time.monotonic() - start
            self.metrics['step_spans_s'][step] = round(duration, 4)
            self.emit('step-span', step=step, duration_s=round(duration, 4))

    def run_remote(self, *args, timeout=60, check=True):
        command = [sys.executable, str(ROOT / 'scripts' / 'session_remote.py'), *map(str, args)]
        start = time.monotonic()
        proc = subprocess.run(command, capture_output=True, text=True, timeout=timeout,
                              env=os.environ.copy())
        duration = time.monotonic() - start
        try:
            value = json.loads(proc.stdout)
        except json.JSONDecodeError:
            value = None
        self.emit('broker-cli', command=args[0] if args else '', returncode=proc.returncode,
                  duration_s=round(duration, 4))
        if check and proc.returncode:
            detail = value if isinstance(value, dict) else proc.stdout[:400] + proc.stderr[:400]
            raise Escalate(self.step, self.current_checkpoint, f'session_remote {args[0]} failed: {detail}')
        return value, proc

    def run_gui_json(self, command, *, timeout=10):
        proc = subprocess.run(command, env=self.gui_env, capture_output=True, text=True,
                              timeout=timeout)
        if proc.returncode:
            raise Escalate(self.step, self.current_checkpoint,
                           f'{Path(command[0]).name} failed: {proc.stderr.strip()[:300]}')
        return json.loads(proc.stdout)

    def current_clients(self):
        return [window_line(row) for row in hypr_query(self.gui_env, 'clients')]

    def update_windows(self, windows):
        if not isinstance(windows, list) or any(not isinstance(row, dict) for row in windows):
            raise Escalate(self.step, self.current_checkpoint, 'windows response is not a list')
        self.last_windows = [window_line(row) for row in windows]
        self.last_active_window = hypr_query(self.gui_env, 'activewindow').get('address')

    def note_image(self, observation, label):
        if not isinstance(observation, dict) or not observation.get('id'):
            return
        self.last_observation = observation
        self.last_image = {'id': observation.get('id'), 'sha256': observation.get('image_sha256'),
                           'path': observation.get('image')}
        self.metrics['images_delivered'] += 1
        byte_count = observation.get('image_bytes')
        image_path = observation.get('image')
        if isinstance(image_path, str) and Path(image_path).is_file():
            image_path = Path(image_path)
            byte_count = image_path.stat().st_size
            evidence = self.run_dir / 'evidence'
            evidence.mkdir(parents=True, exist_ok=True, mode=0o700)
            shutil.copy2(image_path, evidence / f'{label}-{observation["id"]}.png')
        self.metrics['delivered_image_bytes'] += int(byte_count or 0)
        self.emit('image-delivered', step=self.step, label=label,
                  observation_id=observation.get('id'), bytes=int(byte_count or 0),
                  sha256=observation.get('image_sha256'))

    def _driver_body(self, outer, name, action_count=0):
        if not isinstance(outer, dict) or outer.get('status') not in ('completed', 'failed', 'unknown'):
            raise Escalate(self.step, self.current_checkpoint,
                           f'{name}: long-poll did not return a terminal request result')
        envelope = outer.get('response')
        if not isinstance(envelope, dict):
            raise Escalate(self.step, self.current_checkpoint, f'{name}: broker omitted the response envelope')
        body = envelope.get('result')
        if not isinstance(body, (dict, list)):
            raise Escalate(self.step, self.current_checkpoint, f'{name}: driver response is malformed')
        if isinstance(body, dict):
            self.current_batch_completed = int(body.get('completed', 0) or 0)
            self.completed_actions += self.current_batch_completed
            capture_done = (body.get('capture_error') and
                            type(body.get('completed')) is int and
                            body.get('completed') == action_count and action_count > 0)
            if body.get('ok') is False and not capture_done:
                self.metrics['refusals'] += 1
            if envelope.get('session_continues') is False:
                self.metrics['session_deaths'] += 1
        return body, envelope

    def broker_driver(self, name, args, *, stdin='', action_count=0, prebuilt=None):
        req_dir = self.run_dir / 'requests'
        req_dir.mkdir(parents=True, exist_ok=True, mode=0o700)
        seq = self.sequence
        request = prebuilt or {'args': list(args), 'stdin': stdin,
                               'image_policy': self.plan['parameters']['image_policy']}
        request_path = req_dir / f'{seq:03d}-{name}.json'
        if request_path.exists():
            if prebuilt is None or load_json(request_path) != request:
                raise Escalate(self.step, self.current_checkpoint,
                               f'{name}: request path already exists with different content')
        else:
            fd = os.open(request_path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
            try:
                os.write(fd, (json.dumps(request, ensure_ascii=False, separators=(',', ':')) + '\n').encode())
            finally:
                os.close(fd)
        start = time.monotonic()
        accepted, _ = self.run_remote('request', '--lease-file', self.lease_path,
                                      '--sequence', seq, '--request', request_path,
                                      timeout=35, check=False)
        if not isinstance(accepted, dict) or accepted.get('ok') is not True or accepted.get('status') != 'accepted':
            raise Escalate(self.step, self.current_checkpoint,
                           f'{name}: request was not accepted: {accepted}')
        self.sequence += 1
        self.metrics['driver_requests'] += 1
        self.metrics['task_requests'] += 1
        self.metrics['windows_requests'] += int(bool(args) and args[0] == 'windows')
        self.metrics['logical_acts'] += int(args and args[0] == 'act')
        self.current_batch_size = action_count
        self.current_batch_completed = 0
        self.metrics['result_calls'] += 1
        result, _ = self.run_remote('result', '--lease-file', self.lease_path,
                                    '--sequence', seq,
                                    timeout=self.plan['parameters']['result_timeout_s'],
                                    check=False)
        wait_s = time.monotonic() - start
        self.emit('result-long-poll', name=name, sequence=seq, result_calls=1,
                  fixed_poll_sleep_s=0.0, extra_result_calls=0,
                  poll_waste_s=0.0, receipt_wait_s=round(wait_s, 4))
        body, envelope = self._driver_body(result, name, action_count)
        self.emit('request-complete', name=name, sequence=seq,
                  status=result.get('status') if isinstance(result, dict) else None,
                  completed=body.get('completed') if isinstance(body, dict) else None,
                  ok=body.get('ok') if isinstance(body, dict) else None,
                  session_continues=envelope.get('session_continues'))
        if result.get('status') != 'completed':
            raise Escalate(self.step, self.current_checkpoint,
                           f'{name}: request ended as {result.get("status")}')
        if isinstance(body, dict):
            after = body.get('after')
            if isinstance(after, dict):
                self.note_image(after, name)
        return body, envelope

    def auth_status(self):
        value, _ = self.run_remote('status', '--lease-file', self.lease_path,
                                   timeout=10, check=False)
        self.metrics['authenticated_status_polls'] += 1
        return value

    def output_path(self):
        return self.run_dir / 'output' / self.plan['task']['filename']

    def _ensure_clean_broker(self):
        status, _ = self.run_remote('status', timeout=5, check=False)
        if not isinstance(status, dict) or status.get('ok') is not True:
            raise Escalate('P0', 'broker-clean', f'public broker status unavailable: {status}', hygiene=True)
        clean = (
            status.get('state') in ('idle', 'finished') and
            status.get('driver') in ('idle', 'stopped') and
            status.get('guardian') in ('idle', 'clean') and
            status.get('active_sequence') is None and
            status.get('error') is None and
            status.get('recovery') in (None, 'none') and
            status.get('cancelled') is False
        )
        if not clean:
            raise Escalate('P0', 'broker-clean', f'broker is not clean: {status}', hygiene=True)
        self.broker_generation = status.get('broker_generation')
        self.broker_status = status
        self.emit('broker-preflight', state=status.get('state'), driver=status.get('driver'),
                  guardian=status.get('guardian'), generation=self.broker_generation)

    def _check_desktop_hygiene(self):
        try:
            self.gui_env = gui_environment()
            windows = self.current_clients()
            active = hypr_query(self.gui_env, 'activewindow').get('address')
            processes = process_inventory()
        except Exception as exc:
            raise Escalate('P0', 'desktop-hygiene', f'read-only desktop inventory failed: {exc}', hygiene=True)
        self.last_windows = windows
        self.last_active_window = active
        anr = [row for row in windows if re.search(r'application not responding|not responding',
                                                   str(row.get('title', '')), re.I)]
        allow_listed = []
        for row in windows:
            reasons = []
            if str(row.get('class') or '').lower() in ALLOWED_BACKGROUND_CLASSES:
                reasons.append('zen-class')
            workspace = row.get('workspace')
            if isinstance(workspace, str) and workspace.startswith(SPECIAL_WORKSPACE_PREFIX):
                reasons.append('special-workspace')
            if reasons:
                if not any(same_window_identity(row, known) for known in self.known_background):
                    self.known_background.append(row)
                allow_listed.append({'window': row, 'reasons': reasons})
        allowed = list(self.known_background)
        unexpected = [row for row in windows
                      if not any(same_window_identity(row, known) for known in allowed)]
        evidence = {'windows': windows, 'active_window': active,
                    'processes': processes, 'anr_windows': anr,
                    'allow_listed_windows': allow_listed,
                    'unexpected_windows': unexpected}
        self.emit('desktop-hygiene', **evidence)
        if processes['imv_processes'] or anr or unexpected:
            reason = ('blocked on desktop hygiene: ' +
                      json.dumps({'imv': processes['imv_processes'], 'anr': anr,
                                  'unexpected': unexpected}, ensure_ascii=False))
            raise Escalate('P0', 'desktop-hygiene', reason, hygiene=True)
        blank_matches = [row for row in windows
                         if row.get('class') == 'com.microsoft.VSCode' and
                         'blank.txt' in (row.get('title') or '')]
        if blank_matches:
            raise Escalate('P0', 'exactly-one-target-window',
                           'a blank.txt VS Code window already exists; refusing to guess ownership', hygiene=True)
        return windows

    def preflight(self):
        self.run_dir.mkdir(parents=True, exist_ok=False, mode=0o700)
        os.chmod(self.run_dir, 0o700)
        self._ensure_clean_broker()
        self._write_private_json(self.run_dir / 'broker-preflight.json', self.broker_status)
        windows = self._check_desktop_hygiene()
        output = self.output_path()
        if output.exists():
            raise Escalate('P0', 'output-absent', f'output path already exists: {output}', hygiene=True)
        self.emit('live-launch', procedure=self.plan['procedure'], run_id=self.run_id,
                  repo_head=self.git_head(), initial_window_count=len(windows))

    @staticmethod
    def _write_private_json(path, value):
        path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        try:
            os.write(fd, (json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode())
        finally:
            os.close(fd)

    @staticmethod
    def git_head():
        try:
            return subprocess.run(['git', '-C', str(ROOT), 'rev-parse', 'HEAD'],
                                  capture_output=True, text=True, timeout=3, check=True).stdout.strip()
        except Exception:
            return None

    def _launch_test_window(self):
        input_dir = self.run_dir / 'input'
        profile = self.run_dir / 'vscode-profile'
        extensions = self.run_dir / 'vscode-extensions'
        output_dir = self.run_dir / 'output'
        for path in (input_dir, profile / 'User', extensions, output_dir):
            path.mkdir(parents=True, exist_ok=True, mode=0o700)
            os.chmod(path, 0o700)
        blank = input_dir / 'blank.txt'
        fd = os.open(blank, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        os.close(fd)
        settings = profile / 'User' / 'settings.json'
        self._write_private_json(settings, {
            'window.menuBarVisibility': 'classic',
            'window.restoreWindows': 'none',
            'workbench.startupEditor': 'none',
            'security.workspace.trust.enabled': False,
        })
        code = shutil.which('code')
        if not code:
            raise Escalate('P0', 'vscode-launch', 'VS Code CLI is unavailable')
        before = {row.get('address') for row in self.current_clients()}
        self.process = subprocess.Popen(
            [code, '--new-window', '--disable-extensions', '--skip-welcome',
             '--disable-workspace-trust', f'--user-data-dir={profile}',
             f'--extensions-dir={extensions}', '--ozone-platform=wayland',
             '--force-device-scale-factor=1', '--window-size=901,1176', str(blank)],
            env=self.gui_env, stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
        self.emit('vscode-launched', pid=self.process.pid, blank_file=str(blank),
                  profile=str(profile))
        deadline = time.monotonic() + 60
        while time.monotonic() < deadline:
            windows = self.current_clients()
            new = [row for row in windows
                   if row.get('address') not in before and
                   row.get('class') == 'com.microsoft.VSCode' and
                   'blank.txt' in (row.get('title') or '')]
            if len(new) > 1:
                raise Escalate('P0', 'exactly-one-target-window',
                               'more than one new blank.txt VS Code window appeared')
            if len(new) == 1:
                self.editor = new[0]
                expected_set = list(self.known_background) + [self.editor]
                unexpected = [row for row in windows
                              if not any(same_window_identity(row, expected)
                                         for expected in expected_set)]
                if unexpected:
                    raise Escalate('P0', 'no-unexpected-surfaces',
                                   f'unexpected surface appeared during P0: {unexpected}')
                self._assert_geometry(self.editor, 'editor')
                self.emit('vscode-window-mapped', **self.editor)
                return
            time.sleep(.25)
        raise Escalate('P0', 'vscode-window-mapped', 'no new blank.txt window appeared in 60 seconds')

    def _assert_geometry(self, window, which):
        spec = self.plan['preconditions']['editor_geometry' if which == 'editor' else 'dialog_geometry']
        expected = spec['size']
        actual = window.get('size')
        tolerance = spec['tolerance_px']
        if (not isinstance(actual, list) or len(actual) != 2 or
                any(abs(a - e) > tolerance for a, e in zip(actual, expected))):
            raise Escalate(self.step, f'{which}-geometry',
                           f'{which} geometry {actual} is outside {expected} ±{tolerance}px')

    def start_session(self):
        # Construct the first request before start so the ready session has no planning gap.
        self.first_request = {'args': ['windows'], 'stdin': '',
                              'image_policy': self.plan['parameters']['image_policy']}
        req_dir = self.run_dir / 'requests'
        req_dir.mkdir(parents=True, exist_ok=True, mode=0o700)
        self.first_request_path = req_dir / '001-G0-windows.json'
        self._write_private_json(self.first_request_path, self.first_request)
        self.lease_path = self.run_dir / 'session.lease'
        owner = f'tc02-v1-{self.run_id}'[:80]
        self.execution_start = time.monotonic()
        response, _ = self.run_remote('start', '--owner', owner, '--lease-file', self.lease_path,
                                      timeout=35, check=False)
        self.metrics['task_requests'] += 1
        if not isinstance(response, dict) or response.get('ok') is not True:
            raise Escalate('P1', 'session-start', f'broker rejected start: {response}')
        self.generation = response.get('generation')
        self.session_started = True
        deadline = time.monotonic() + 25
        ready = None
        while time.monotonic() < deadline:
            status = self.auth_status()
            if (isinstance(status, dict) and status.get('state') == 'running' and
                    status.get('driver') == 'ready' and status.get('guardian') == 'active'):
                ready = status
                break
            time.sleep(.5)
        if not isinstance(ready, dict):
            raise Escalate('P1', 'session-ready', 'session did not become running/ready/active in 25 seconds')
        if (ready.get('generation') != self.generation or
                ready.get('broker_generation') != self.broker_generation):
            raise Escalate('P1', 'same-generation', 'session or broker generation changed during readiness')
        self.sequence = ready.get('next_sequence', 1)
        self.emit('session-ready', owner=owner, generation=self.generation,
                  broker_generation=self.broker_generation,
                  readiness_s=round(time.monotonic() - self.execution_start, 4),
                  next_sequence=self.sequence)

    def _observe(self, name, address, max_width):
        body, _ = self.broker_driver(name, ['observe', '--window', address,
                                            '--max-width', str(max_width)])
        if not isinstance(body, dict) or body.get('ok') is not True:
            raise Escalate(self.step, self.current_checkpoint, f'{name}: observe failed: {body}')
        self.note_image(body, name)
        self._remember_observation(body)
        return body

    def _remember_observation(self, observation):
        self.last_observation = observation
        self.last_image = {'id': observation.get('id'), 'sha256': observation.get('image_sha256'),
                           'path': observation.get('image')}

    def _windows(self, name, *, prebuilt=None):
        body, _ = self.broker_driver(name, ['windows'], prebuilt=prebuilt)
        if not isinstance(body, list):
            raise Escalate(self.step, self.current_checkpoint, f'{name}: windows response is malformed')
        self.update_windows(body)
        self.emit('windows-list', name=name, windows=self.last_windows,
                  active_window=self.last_active_window)
        return body

    def _expected_window_set(self, additions):
        expected = list(self.known_background)
        for item in additions:
            if item is not None:
                expected.append(window_line(item))
        return expected

    def _assert_no_unexpected_windows(self, windows, additions):
        expected = self._expected_window_set(additions)
        unexpected = [window_line(row) for row in windows
                      if not any(same_window_identity(window_line(row), allowed)
                                 for allowed in expected)]
        if unexpected:
            raise Escalate(self.step, self.current_checkpoint,
                           f'unexpected window or dialog appeared: {unexpected}')

    def _assert_window(self, windows, address, *, cls=None, title_contains=None):
        matches = [row for row in windows if row.get('address') == address]
        if len(matches) != 1:
            raise Escalate(self.step, self.current_checkpoint,
                           f'expected exactly one window at {address}; found {len(matches)}')
        row = matches[0]
        if cls and row.get('class') != cls:
            raise Escalate(self.step, self.current_checkpoint,
                           f'window {address} class changed to {row.get("class")}')
        if title_contains and title_contains not in (row.get('title') or ''):
            raise Escalate(self.step, self.current_checkpoint,
                           f'window {address} title does not contain {title_contains!r}')
        return row

    def _observation_age(self, observation):
        mono = observation.get('capture_started_monotonic')
        if not isinstance(mono, (int, float)):
            return None
        return max(0.0, time.monotonic() - mono)

    def _assert_fresh(self, observation):
        age = self._observation_age(observation)
        if age is None or age >= self.plan['preconditions']['observation_max_age_s']:
            raise Escalate(self.step, self.current_checkpoint,
                           f'observation is missing a monotonic timestamp or is too old: {age}')

    def _check_after_image(self, before, after, *, changed=False):
        self._assert_fresh(after)
        keys = ('window', 'window_bounds', 'monitor', 'monitor_box',
                'monitor_scale', 'monitor_transform', 'capture_compositor')
        differences = [key for key in keys if before.get(key) != after.get(key)]
        if differences:
            raise Escalate(self.step, self.current_checkpoint,
                           f'after-image changed its coordinate identity: {differences}')
        if changed and after.get('pixel_sha256') == before.get('pixel_sha256'):
            raise Escalate(self.step, self.current_checkpoint,
                           'expected editor change is absent from the full-frame after-image')

    def _resolve_action(self, action, observation):
        result = dict(action)
        point = result.pop('point', None)
        if point:
            coordinate = self.plan['coordinates'][point]
            if coordinate['anchor'] != 'window_top_left':
                raise Escalate(self.step, self.current_checkpoint, f'{point}: unsupported anchor')
            x, y = coordinate['offset']
            image_width, image_height = observation.get('image_size', [0, 0])
            wx, wy, ww, wh = observation.get('window_bounds', [0, 0, 0, 0])
            rx, ry, rw, rh = observation.get('region', [0, 0, 0, 0])
            sx = rw / image_width if image_width else 0
            sy = rh / image_height if image_height else 0
            gx, gy = rx + x * sx, ry + y * sy
            if (not image_width or not image_height or x < 0 or y < 0 or
                    x >= image_width or y >= image_height or
                    gx < wx or gy < wy or gx >= wx + ww or gy >= wy + wh):
                raise Escalate(self.step, f'bounds:{point}',
                               f'{point}={x},{y} is outside the current image or window')
            result['x'], result['y'] = x, y
        text = result.get('text')
        if isinstance(text, str) and text == '${output_path}':
            result['text'] = str(self.output_path())
        return result

    def _menu_bar_visible(self, observation):
        image = observation.get('image')
        if not isinstance(image, str) or not Path(image).is_file():
            raise Escalate('G0', 'menu-bar-presence', 'grounding image file is unavailable')
        tesseract = shutil.which('tesseract')
        if not tesseract:
            raise Escalate('G0', 'menu-bar-presence', 'tesseract is unavailable; refusing to assume a menu bar')
        proc = subprocess.run([tesseract, image, 'stdout', '--psm', '6'],
                              capture_output=True, text=True, timeout=10)
        text = proc.stdout.casefold()
        missing = [token for token in self.plan['preconditions']['menu_bar_ocr_tokens']
                   if token.casefold() not in text]
        self.emit('menu-bar-presence', engine='tesseract-full-frame',
                  tokens=self.plan['preconditions']['menu_bar_ocr_tokens'],
                  missing=missing, text_excerpt=' '.join(proc.stdout.split())[:300])
        if proc.returncode or missing:
            raise Escalate('G0', 'menu-bar-presence',
                           f'menu bar OCR check failed; missing labels: {missing}')

    def _partial_reobserve(self, target_address):
        packet_evidence = {'partial_batch': {'completed': self.current_batch_completed,
                                             'batch_size': self.current_batch_size}}
        try:
            windows = self._windows('partial-windows')
            target = next((row for row in windows if row.get('address') == target_address), None)
            if target is not None:
                observation = self._observe('partial-fresh-observe', target_address, 1600)
                packet_evidence['partial_batch']['fresh_observation_id'] = observation.get('id')
        except Exception as exc:
            packet_evidence['partial_batch']['reobserve_error'] = str(exc)
        return packet_evidence

    def _act(self, step, observation, target_window, *, after_window=None,
             after_bounds=None):
        self._assert_fresh(observation)
        resolved = [self._resolve_action(action, observation) for action in step['batch']]
        self.current_batch_size = len(resolved)
        self.current_batch_completed = 0
        self.current_checkpoint = step['checkpoint']
        args = ['act', '--observation', observation['observation'], '--actions', '-']
        if step.get('no_after'):
            args.append('--no-after')
        expected = step.get('expected_terminal_window', 'same')
        if expected == 'saved_editor':
            expected = after_window
            if not isinstance(expected, str):
                raise Escalate(step['id'], step['checkpoint'], 'saved editor address is not bound')
        if expected != 'same':
            args.extend(['--expected-terminal-window', expected])
            if expected != 'unbound' and expected != 'none' and after_bounds:
                args.extend(['--expected-terminal-bounds', *map(str, after_bounds)])
        stdin = json.dumps(resolved, ensure_ascii=False, separators=(',', ':'))
        body, envelope = self.broker_driver(step['id'], args, stdin=stdin,
                                            action_count=len(resolved))
        if not isinstance(body, dict):
            raise Escalate(step['id'], step['checkpoint'], 'act response is not an object')
        if step['id'] == 'S2':
            self.emit('s2-act-timing', execution_ms=body.get('execution_ms'),
                      after_capture_ms=body.get('after_capture_ms'),
                      after_skipped=body.get('after_skipped'),
                      completed=body.get('completed'), ok=body.get('ok'))
        if body.get('ok') is True:
            if body.get('completed') != len(resolved):
                evidence = self._partial_reobserve(target_window)
                raise Escalate(step['id'], step['checkpoint'],
                               f'partial batch completed {body.get("completed")} of {len(resolved)}',
                               hygiene=False)
            if isinstance(body.get('after'), dict):
                self._check_after_image(observation, body['after'], changed=step['id'] == 'S1')
            return body
        if (body.get('capture_error') and type(body.get('completed')) is int and
                body.get('completed') == len(resolved)):
            self.emit('action-done-evidence-missing', step=step['id'],
                      completed=body.get('completed'), capture_error=body.get('capture_error'),
                      transition=body.get('transition'))
            return body
        if body.get('completed', 0) < len(resolved):
            evidence = self._partial_reobserve(target_window)
            raise Escalate(step['id'], step['checkpoint'],
                           f'partial or refused batch; {evidence}')
        raise Escalate(step['id'], step['checkpoint'],
                       f'act returned ok:false without the completed capture-error recovery case: {body}')

    def record_s2_sample(self, *, act_done_mono, windows_done_mono, dialog):
        # Act timing ratchets with the wait; checkpoint latency measures dialog appearance, not menu rendering.
        span_s = windows_done_mono - act_done_mono
        if span_s < 0:
            raise ValueError('S2 checkpoint sample span cannot be negative')
        sample_ms = round(span_s * 1000, 3)
        wait_ms = self.plan['wait_tuning']['selected_wait_ms']
        dialog_address = dialog['address']
        self.emit(
            's2-sample', sample_ms=sample_ms,
            definition='Monotonic milliseconds from the return of the S2 act result to the return of the S2 windows result that first lists the Save As dialog.',
            wait_ms=wait_ms,
            menu_open_latency_ms={
                'censored': True,
                'upper_bound_ms': wait_ms,
                'evidence': 'Save As dialog appeared after the row click, so the menu was open when the row was clicked',
            },
            dialog_address=dialog_address, dialog=dialog)
        self.s2_samples.append({
            'sample_ms': sample_ms,
            'wait_ms': wait_ms,
            'menu_open_latency_censored_upper_bound_ms': wait_ms,
            'dialog_address': dialog_address,
        })

    def _geometry_matches_observation(self, observation, window):
        bounds = observation.get('window_bounds')
        size = window.get('size')
        return isinstance(bounds, list) and isinstance(size, list) and bounds[2:] == size

    def run_live(self):
        if not self.live:
            raise ValueError('live run requires --live')
        self.preflight()
        with self.span('P0'):
            self.current_checkpoint = 'one-test-owned-vscode-window'
            self._launch_test_window()
        with self.span('P1'):
            self.current_checkpoint = 'session-running-ready-active'
            self.start_session()
        with self.span('G0'):
            self.current_checkpoint = 'grounding-window-and-menu-bar'
            self._windows('G0-windows', prebuilt=self.first_request)
            self.editor = self._assert_window(self.last_windows, self.editor['address'],
                                              cls='com.microsoft.VSCode', title_contains='blank.txt')
            self._assert_no_unexpected_windows(self.last_windows, [self.editor])
            if self.last_active_window != self.editor['address']:
                raise Escalate('G0', 'active-target-window',
                               f'editor is not active: {self.last_active_window}')
            observation = self._observe('G0-observe', self.editor['address'], 1600)
            self._assert_geometry(self.editor, 'editor')
            if not self._geometry_matches_observation(observation, self.editor):
                raise Escalate('G0', 'coordinate-geometry', 'grounding observation and window bounds differ')
            self._menu_bar_visible(observation)
            for coordinate in self.plan['coordinates']:
                self._resolve_action({'type': 'click', 'point': coordinate}, observation)
            self.editor_observation = observation
        with self.span('S1'):
            step = self.plan['steps'][3]
            body = self._act(step, self.editor_observation, self.editor['address'])
            if body.get('completed') != len(step['batch']) or not body.get('after'):
                raise Escalate('S1', step['checkpoint'], 'S1 did not produce its required full-batch after-image')
            self.editor_observation = body['after']
        with self.span('S2'):
            step = self.plan['steps'][4]
            body = self._act(step, self.editor_observation, self.editor['address'])
            t_act_done = time.monotonic()
            if body.get('completed') != len(step['batch']):
                raise Escalate('S2', step['checkpoint'], 'S2 action count is incomplete')
            windows = self._windows('S2-windows')
            t_windows_done = time.monotonic()
            dialogs = [row for row in windows if row.get('class') == 'xdg-desktop-portal-gtk' and
                       row.get('title') == 'Save As']
            if len(dialogs) != 1:
                raise Escalate('S2', step['checkpoint'],
                               f'expected one Save As dialog, found {len(dialogs)}')
            self.dialog = window_line(dialogs[0])
            self.record_s2_sample(act_done_mono=t_act_done,
                                  windows_done_mono=t_windows_done,
                                  dialog=self.dialog)
            self._assert_no_unexpected_windows(windows, [self.editor, self.dialog])
            self._assert_geometry(self.dialog, 'dialog')
            if self.last_active_window != self.dialog['address']:
                raise Escalate('S2', 'dialog-active', 'Save As dialog did not become active')
        with self.span('S3'):
            step = self.plan['steps'][5]
            self.current_checkpoint = step['checkpoint']
            self.dialog_observation = self._observe('S3-observe-dialog', self.dialog['address'],
                                                    step['max_width'])
            if not self._geometry_matches_observation(self.dialog_observation, self.dialog):
                raise Escalate('S3', step['checkpoint'], 'dialog observation bounds do not match the live window')
            for coordinate in ('name_field', 'save_button'):
                self._resolve_action({'type': 'click', 'point': coordinate}, self.dialog_observation)
        with self.span('S4'):
            step = self.plan['steps'][6]
            body = self._act(step, self.dialog_observation, self.dialog['address'])
            if body.get('completed') != len(step['batch']) or not body.get('after'):
                raise Escalate('S4', step['checkpoint'], 'S4 did not complete the path-entry batch')
            self.dialog_observation = body['after']
        with self.span('S5'):
            step = self.plan['steps'][7]
            body = self._act(step, self.dialog_observation, self.dialog['address'],
                             after_window=self.editor['address'], after_bounds=self.editor['at'] + self.editor['size'])
            if body.get('completed') != len(step['batch']):
                raise Escalate('S5', step['checkpoint'], 'Save action did not complete')
            if body.get('ok') is False and not body.get('capture_error'):
                raise Escalate('S5', step['checkpoint'], 'Save act failed without a recoverable missing capture')
            windows = self._windows('S5-windows')
            dialog_still_open = any(row.get('address') == self.dialog['address'] for row in windows)
            if dialog_still_open:
                raise Escalate('S5', 'dialog-close-transaction', 'Save As dialog is still present; Save will not be repeated')
            editor = self._assert_window(windows, self.editor['address'],
                                         cls='com.microsoft.VSCode')
            self._assert_no_unexpected_windows(windows, [editor])
            self.saved_title = editor.get('title') or ''
            if self.last_active_window != self.editor['address']:
                raise Escalate('S5', 'successor-active', 'saved editor successor is not active')
            self.emit('save-transition-windows', action_completed=True,
                      old_surface_gone=True, successor=self.editor['address'],
                      title=self.saved_title, envelope_transition=body.get('transition'))
        with self.span('S6'):
            step = self.plan['steps'][8]
            self.current_checkpoint = step['checkpoint']
            final_observation = self._observe('S6-final-editor', self.editor['address'],
                                              step['max_width'])
            self._assert_window(self.last_windows, self.editor['address'], cls='com.microsoft.VSCode')
            if not self._geometry_matches_observation(final_observation, self.editor):
                raise Escalate('S6', step['checkpoint'], 'successor observation does not match editor geometry')
            self.emit('transition-verified', action_completed=True, old_surface_gone=True,
                      successor=self.editor['address'], successor_verified=True,
                      final_observation=final_observation.get('id'))
            if self.plan['task']['filename'] not in self.saved_title:
                raise Escalate('S6', 'saved-editor-title',
                               f'editor title did not change to {self.plan["task"]["filename"]!r}: {self.saved_title!r}')
            self.emit('saved-title-verified', title=self.saved_title)
            output = self.output_path()
            if not output.is_file():
                raise Escalate('S6', 'read-only-byte-verification', 'saved output file is absent')
            contents = output.read_bytes()
            digest = hashlib.sha256(contents).hexdigest()
            exact = (len(contents) == self.plan['task']['expected_bytes'] and
                     digest == self.plan['task']['expected_sha256'] and
                     contents == self.plan['task']['text'].encode('utf-8'))
            self.emit('read-only-byte-verification', exact=exact, bytes=len(contents), sha256=digest)
            if not exact:
                raise Escalate('S6', 'read-only-byte-verification',
                               f'byte mismatch: {len(contents)} bytes, SHA-256 {digest}')
            finish, _ = self.run_remote('finish', '--lease-file', self.lease_path,
                                        timeout=135, check=False)
            self.metrics['task_requests'] += 1
            self.session_finished = bool(isinstance(finish, dict) and finish.get('ok') is True and
                                         finish.get('status') == 'finished' and
                                         finish.get('driver') == 'stopped' and
                                         finish.get('guardian') == 'clean')
            self.emit('finish-record', result=finish)
            if not self.session_finished:
                self.metrics['session_deaths'] += 1
                raise Escalate('S6', 'clean-finish', f'finish did not return finished/stopped/clean: {finish}')
        self.known_background.append(window_line(self.editor))
        return self._summary('PASS')

    def _cleanup_finish(self):
        if not self.session_started or self.session_finished:
            return None
        try:
            result, _ = self.run_remote('finish', '--lease-file', self.lease_path,
                                        timeout=135, check=False)
            self.session_finished = bool(isinstance(result, dict) and result.get('status') == 'finished')
            self.metrics['task_requests'] += 1
            self.emit('escalation-cleanup-finish', result=result)
            return result
        except Exception as exc:
            self.emit('escalation-cleanup-finish-error', error=str(exc))
            return None

    def _l2_packet(self, failure, extra=None):
        age = self._observation_age(self.last_observation) if self.last_observation else None
        branches = (self.current_step or {}).get('branches', ['stop-and-report'])
        return {
            'destination': 'VM supervisor (L2 packet; no local model call)',
            'procedure': self.plan['procedure'],
            'step': failure.step,
            'failed_checkpoint': failure.checkpoint,
            'state': {
                'windows': self.last_windows,
                'active_window': self.last_active_window,
                'last_observation': self.last_observation.get('id') if self.last_observation else None,
                'observation_age_s': round(age, 3) if age is not None else None,
            },
            'last_image': self.last_image,
            'completed': {
                'current_batch': f'{self.current_batch_completed} of {self.current_batch_size}',
                'total_actions': self.completed_actions,
            },
            'branches': branches,
            'history': self.history[-80:],
            'reason': failure.reason,
            'blocked_on_desktop_hygiene': failure.hygiene,
            'extra': extra or {},
        }

    def _summary(self, status, *, failure=None):
        end_to_end = time.monotonic() - self.dispatch_mono
        execution = (time.monotonic() - self.execution_start
                     if hasattr(self, 'execution_start') else None)
        summary = {
            'status': status,
            'procedure': self.plan['procedure'],
            'run_id': self.run_id,
            'repo_head': self.git_head(),
            'execution_s': round(execution, 4) if execution is not None else None,
            'end_to_end_s': round(end_to_end, 4),
            'metrics': self.metrics,
            's2_samples': list(self.s2_samples),
            'generation': self.generation,
            'broker_generation': self.broker_generation,
            'output_path': str(self.output_path()),
            'failure': failure.reason if failure else None,
            'L2_packet': str(self.packet_path) if failure else None,
        }
        self._write_private_json(self.summary_path, summary)
        self.emit('run-summary', **summary)
        return summary

    def escalate(self, failure, extra=None):
        self._cleanup_finish()
        packet = self._l2_packet(failure, extra)
        self._write_private_json(self.packet_path, packet)
        self.emit('ESCALATED', L2_packet=packet)
        self._summary('ESCALATED', failure=failure)
        return 2


def canonical_action(action):
    value = dict(action)
    if value.get('type') == 'type' and isinstance(value.get('text'), str):
        text = value['text']
        if text == '${output_path}' or text.endswith('/on-tap.txt'):
            value['text'] = '<output>/on-tap.txt'
    return value


def dry_run(plan, trace_dir):
    expected_requests = ['start', 'windows', 'observe', 'act', 'act', 'windows',
                         'observe', 'act', 'act', 'windows', 'observe', 'finish']
    plan_requests = []
    for step in plan['steps']:
        plan_requests.extend(step.get('request_sequence', []))
    if plan_requests != expected_requests:
        raise ValueError(f'plan request sequence differs from tc02-v1: {plan_requests}')
    plan_actions = []
    for step in plan['steps']:
        for action in step.get('batch', []):
            if action.get('type') != 'wait':
                resolved = dict(action)
                point = resolved.pop('point', None)
                if point:
                    resolved['x'], resolved['y'] = plan['coordinates'][point]['offset']
                plan_actions.append(canonical_action(resolved))
    trace_actions = []
    trace_act_requests = 0
    if trace_dir and Path(trace_dir).is_dir():
        records = []
        for path in Path(trace_dir).glob('*-record.json'):
            try:
                record = load_json(path)
            except ValueError:
                continue
            request = record.get('request', {})
            if request.get('args', [])[:1] != ['act']:
                continue
            records.append(record)
        records.sort(key=lambda item: item.get('sequence', 0))
        for record in records:
            request = record.get('request', {})
            try:
                actions = json.loads(request.get('stdin', '[]'))
            except (TypeError, json.JSONDecodeError):
                continue
            trace_act_requests += 1
            trace_actions.extend(canonical_action(action) for action in actions)
        verification = load_json(Path(trace_dir) / 'byte-exact-read-back.json')
        expected_hash = plan['task']['expected_sha256']
        if (not verification.get('exact') or verification.get('actual_bytes') != 50 or
                verification.get('actual') != plan['task']['text']):
            raise ValueError('t3 evidence does not prove the plan text byte-exactly')
        if hashlib.sha256(verification['actual'].encode()).hexdigest() != expected_hash:
            raise ValueError('t3 evidence SHA-256 does not match the plan')
        if plan_actions != trace_actions:
            raise ValueError('plan actions do not match the ordered brokered actions in the t3 trace')
        source = str(trace_dir)
    else:
        source = 'opt-batch-research.md tc02 procedure (trace directory unavailable)'
        if len(plan_actions) != 9:
            raise ValueError('plan does not contain the nine grounded non-wait tc02 actions')
    result = {
        'status': 'PASS',
        'procedure': plan['procedure'],
        'trace_source': source,
        'logical_request_sequence': plan_requests,
        'logical_request_count': len(plan_requests),
        'optimized_act_requests': sum(1 for step in plan['steps'] if step.get('kind') == 'act'),
        'baseline_t3_act_requests': trace_act_requests,
        'semantic_action_order_matches_t3': bool(trace_actions) and plan_actions == trace_actions,
        'model_round_trips': 0,
        'live_desktop_touched': False,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--plan', type=Path, default=DEFAULT_PLAN)
    parser.add_argument('--schema', type=Path, default=DEFAULT_SCHEMA)
    parser.add_argument('--dry-run', action='store_true', help='compare the plan with retained tc02-t3 evidence only')
    parser.add_argument('--trace-dir', type=Path, default=DEFAULT_TRACE)
    parser.add_argument('--live', action='store_true', help='run the GUI plan through the real local broker')
    parser.add_argument('--run-id', default=None)
    parser.add_argument('--output-root', type=Path, default=DEFAULT_RUNS)
    args = parser.parse_args(argv)
    if args.live == args.dry_run:
        parser.error('choose exactly one of --live or --dry-run')
    try:
        plan = load_json(args.plan)
        schema = load_json(args.schema)
        validate_plan(plan, schema)
        if args.dry_run:
            return dry_run(plan, args.trace_dir)
        run_id = args.run_id or wall_now().strftime('tc02-%Y%m%d-%H%M%S')
        if not SAFE_RUN_ID.fullmatch(run_id):
            parser.error('--run-id may contain only letters, numbers, dot, underscore, and hyphen')
        controller = Tc02Controller(plan, run_id, args.output_root, live=True)
        try:
            controller.run_live()
            return 0
        except Escalate as failure:
            return controller.escalate(failure)
        except Exception as exc:
            failure = Escalate(controller.step, controller.current_checkpoint,
                               f'unexpected controller failure: {type(exc).__name__}: {exc}')
            return controller.escalate(failure)
    except (OSError, ValueError) as exc:
        print(f'PLAN-ERROR: {exc}', file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
