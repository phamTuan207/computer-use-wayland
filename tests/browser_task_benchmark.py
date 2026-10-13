#!/usr/bin/env python3
"""Owned Chromium task: existing split/wait route vs existing batch/assert route.

No backend changes. Inert loopback page reports its actual final state to the
fixture server. Output omits paths, IDs, ports and text. Run outside a session.
"""
import argparse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import threading
import time
import urllib.request

from optimization_live import summary

BATCH_MODES = ('batch', 'batch-no-after')

TASK_MODES = ('task-full', 'task-scoped', 'task-after-full', 'task-after-scoped')


PAGE = '''<!doctype html><meta charset="utf-8">
<input id="name"><button id="save">Save fixture</button><p id="status">Ready</p>{controls}
<script>
let generation=0;
document.querySelector('#name').addEventListener('input',()=>{
  generation++; document.querySelector('#status').textContent='Ready';
});
document.querySelector('#save').onclick=()=>{
  const text=document.querySelector('#name').value, own=generation;
  const delay=Number(new URL(location.href).searchParams.get('delay'));
  if(delay<0)return;
  setTimeout(()=>{
    if(own!==generation)return;
    document.querySelector('#status').textContent='Saved '+text;
    requestAnimationFrame(()=>fetch('/done',{method:'POST',body:JSON.stringify({text})}));
  },delay);
};
requestAnimationFrame(()=>fetch('/ready',{method:'POST',body:'{}'}));
</script>'''

TASK_PAGE = PAGE.replace('<input id="name">', '<div id="task"><input id="name" aria-label="Task name">', 1).replace('<p id="status">Ready</p>', '<p id="status">Ready</p></div>', 1)


def page(controls, task=False):
    """One page plus `controls` inert inputs, so the after-snapshot pays real DOM cost.

    The task variant wraps the same targets and the same script in a unique #task
    root, with the irrelevant controls after it, so every target stays in view and
    the scope root matches exactly once.
    """
    template = TASK_PAGE if task else PAGE
    return template.replace('{controls}', '<input disabled aria-hidden="true">'*controls).encode()


def wait_workspace(cu, env, workspace, timeout=3):
    deadline = time.monotonic()+timeout
    while True:
        cu.check_cancel()
        if json.loads(cu.run(['hyprctl', '-j', 'activeworkspace'], env))['id'] == workspace:
            return
        if time.monotonic() >= deadline:
            raise RuntimeError('fixture workspace transition timed out')
        time.sleep(.01)


def write_report(report, path):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode='w', dir=path.parent, prefix='.report-', delete=False) as stream:
            temporary = Path(stream.name)
            json.dump(report, stream, indent=2)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def selected_modes(report):
    """Selected modes, in selection order; rows are the fallback for a bare report."""
    rows = report['samples']
    chosen = report.get('modes')
    if not chosen:
        chosen = list(dict.fromkeys(r['mode'] for r in rows))
    return [m for m in chosen if any(r['mode'] == m and r['ok'] for r in rows)]


def finish_report(report, path, cleanup):
    report['cleanup_ok'] = False
    try:
        cleanup()
    finally:
        report['ok'] = bool(report.get('tasks_ok') and report['cleanup_ok'])
        rows = report['samples']
        report['summary'] = {mode: summary([r['total_ms'] for r in rows if r['mode']==mode and r['ok']])
                             for mode in selected_modes(report)}
        write_report(report, path)


def text_for(nonce, index, mode):
    """Unique per run, sample and mode, so a stale field cannot satisfy the assert."""
    return f'{nonce} {index} {mode} Việt 🐱'


def pick_ref(elements, role, label):
    """Resolve one ref by unique semantic label; a selector would bypass the observe."""
    found = [e['ref'] for e in elements if e['role'] == role and e['name'] == label]
    if len(found) != 1:
        raise RuntimeError(f'ref selection for {label!r} matched {len(found)} controls')
    return found[0]


def task_sample(base, worker, row, mode, text, state, cu):
    """Whole task: fresh observe, act, then independent app verification."""
    state.clear()
    observe_request = {**base, 'operation': 'observe', 'max_elements': 80}
    if mode in ('task-scoped', 'task-after-full', 'task-after-scoped'):
        observe_request['scope'] = '#task'
    started = time.perf_counter()
    snapshot = worker.request(observe_request)
    row['calls'] += 1
    row['result_bytes'] += len(json.dumps(snapshot, ensure_ascii=False).encode())
    row['observe_ms'] = (time.perf_counter()-started)*1000
    name = pick_ref(snapshot['elements'], 'input', 'Task name')
    save = pick_ref(snapshot['elements'], 'button', 'Save fixture')
    actions = [{'type': 'set_value', 'ref': name, 'text': text},
               {'type': 'click', 'ref': save},
               {'type': 'assert', 'selector': '#status', 'text': 'Saved '+text,
                'timeout_ms': 1000}]
    act_request = {**base, 'operation': 'act', 'max_elements': 80,
                   'snapshot': snapshot['snapshot'], 'actions': actions}
    if mode in ('task-full', 'task-scoped'):
        act_request['no_after'] = True
    if mode == 'task-after-scoped':
        act_request['after_scope'] = '#task'
    result = worker.request(act_request)
    response_done = time.perf_counter()
    row['calls'] += 1
    row['result_bytes'] += len(json.dumps(result, ensure_ascii=False).encode())
    if not result.get('ok'):
        row['failure'] = {k: result[k] for k in ('error', 'completed', 'mutation_may_have_occurred') if k in result}
        raise RuntimeError('fixture task refused or condition timed out')
    if mode in ('task-full', 'task-scoped'):
        if result.get('after_skipped') is not True or 'after' in result:
            raise RuntimeError('no_after route did not skip the after-snapshot')
    else:
        after = result.get('after')
        if not isinstance(after, dict) or not after.get('snapshot') or \
                bool(after.get('scoped')) != (mode == 'task-after-scoped'):
            raise RuntimeError('after-snapshot scope differs from requested mode')
        pick_ref(after['elements'], 'input', 'Task name')
        pick_ref(after['elements'], 'button', 'Save fixture')
    deadline = time.monotonic()+1
    while state.get('text') != text and time.monotonic() < deadline:
        cu.check_cancel()
        time.sleep(.005)
    if state.get('text') != text:
        raise RuntimeError('independent app state differs')
    row['ok'] = True
    row['total_ms'] = (time.perf_counter()-started)*1000
    row['act_verify_ms'] = row['total_ms']-row['observe_ms']
    row['response_ms'] = (response_done-started)*1000
    row['execution_ms'] = result['execution_ms']
    row['whole_task_ms'] = row['total_ms']


def run(args):
    root = args.cli.resolve().parents[1]
    sys.path.insert(0, str(root/'scripts'))
    import cu
    from browser_worker import BrowserWorker
    cu.require_session()
    env = cu.environment()
    original = cu.hypr(env, 'activewindow').get('address')
    original_workspace = json.loads(cu.run(['hyprctl', '-j', 'activeworkspace'], env))['id']
    used = {w['id'] for w in cu.hypr(env, 'workspaces')}
    workspace = next(i for i in range(101, 201) if i not in used)
    state = {}
    mode_family = 'task' if set(args.modes) <= set(TASK_MODES) else 'legacy'
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *_):
            pass
        def do_GET(self):
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(page(args.controls, task=mode_family == 'task'))
        def do_POST(self):
            size = int(self.headers.get('Content-Length', 0))
            if self.path not in ('/done', '/ready') or not 0 < size < 2000:
                self.send_error(400)
                return
            data = json.loads(self.rfile.read(size))
            if self.path == '/ready':
                state['ready'] = True
            else:
                state['text'] = data.get('text')
            self.send_response(204)
            self.end_headers()
    server = None
    thread = None
    thread_started = False
    browser = None
    worker = None
    temporary = None
    rows = []
    report = {'kind': 'real_chromium_fixture', 'phase': 'cold' if args.cold else 'warm',
              'delay_ms': args.delay, 'modes': list(args.modes), 'controls': args.controls,
              'samples_per_mode': args.samples,
              'mode_family': mode_family,
              'timing_scope': ('whole task: observe + act + independent app verification; setup outside'
                               if mode_family == 'task'
                               else 'act request plus independent app verification; setup outside'),
              'provenance': 'source_tree' if root == Path(__file__).resolve().parents[1] else 'external_cli',
              'runtime_sha256': {name: hashlib.sha256((root/'scripts'/name).read_bytes()).hexdigest()
                                 for name in ['cu.py', 'browser_worker.py', 'cdp.mjs']},
              'ok': False, 'samples': rows, 'warmup': []}
    try:
        server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        thread_started = True
        worker = BrowserWorker()
        temporary = tempfile.TemporaryDirectory(prefix='cu-task-browser-')
        folder = temporary.name
        cu.run(['hyprctl', 'dispatch', f'hl.dsp.focus({{ workspace = "{workspace}" }})'], env)
        wait_workspace(cu, env, workspace)
        url = f'http://127.0.0.1:{server.server_port}/fixture?delay={args.delay}'
        browser = subprocess.Popen(['chromium', '--user-data-dir='+folder,
                                    '--remote-debugging-port=0', '--remote-debugging-address=127.0.0.1',
                                    '--no-first-run', '--no-default-browser-check',
                                    '--disable-background-networking', url], env=env,
                                   stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        deadline = time.monotonic()+10
        target = endpoint = None
        while time.monotonic() < deadline:
            cu.check_cancel()
            if browser.poll() is not None:
                raise RuntimeError('fixture browser exited')
            try:
                port = int((Path(folder)/'DevToolsActivePort').read_text().splitlines()[0])
                endpoint = 'http://127.0.0.1:'+str(port)
                with urllib.request.urlopen(endpoint+'/json/list', timeout=.5) as response:
                    tabs = json.load(response)
                target = next((tab['id'] for tab in tabs if tab.get('url') == url), None)
                if target:
                    break
            except (OSError, ValueError, IndexError):
                pass
            time.sleep(.05)
        if not target:
            raise RuntimeError('fixture target unavailable')
        # Target discovery can precede the trailing script attaching app handlers.
        deadline = time.monotonic()+5
        while not state.get('ready'):
            cu.check_cancel()
            if time.monotonic() >= deadline:
                raise RuntimeError('fixture app readiness timed out')
            time.sleep(.01)
        base = {'endpoint': endpoint, 'target': target}
        nonce = os.urandom(4).hex()
        for i in range(0 if args.cold else -1, args.samples):
            for mode in (args.modes if i%2 == 0 else list(reversed(args.modes))):
                cu.check_cancel()
                row = {'mode': mode, 'index': i, 'ok': False, 'calls': 0, 'result_bytes': 0,
                       'observe_ms': 0, 'act_verify_ms': 0}
                (rows if i >= 0 else report['warmup']).append(row)
                # Checkpoint before the timer and before the observe, so an abrupt
                # kill still leaves the partial row.
                write_report(report, args.report)
                text = text_for(nonce, i, args.modes.index(mode))
                if mode in TASK_MODES:
                    task_sample(base, worker, row, mode, text, state, cu)
                    write_report(report, args.report)
                    continue
                # Fresh observe per sample: a skipped after-snapshot cannot hand back a
                # new snapshot id, so a route that skips it must never reuse the old one.
                snapshot = worker.request({**base, 'operation': 'observe', 'max_elements': 8})
                state.clear()
                # Both batch routes use set_value, which is focus-independent; split keeps
                # fill, so it stays comparable with its existing history.
                setter = 'set_value' if mode in BATCH_MODES else 'fill'
                actions = [{'type': setter, 'selector': '#name', 'text': text},
                           {'type': 'click', 'selector': '#save'},
                           {'type': 'assert', 'selector': '#status', 'text': 'Saved '+text,
                            'timeout_ms': 1000}]
                started = time.perf_counter()
                groups = [actions] if mode in BATCH_MODES else [actions[:1], actions[1:2],
                          [{'type': 'wait', 'ms': 80}], actions[2:]]
                for group in groups:
                    request = {**base, 'operation': 'act', 'max_elements': 8,
                               'snapshot': snapshot['snapshot'], 'actions': group}
                    if mode == 'batch-no-after':
                        request['no_after'] = True
                    result = worker.request(request)
                    row['calls'] += 1
                    row['result_bytes'] += len(json.dumps(result, ensure_ascii=False).encode())
                    if not result.get('ok'):
                        row['failure'] = {k: result[k] for k in ('error', 'completed', 'mutation_may_have_occurred') if k in result}
                        raise RuntimeError('fixture task refused or condition timed out')
                    if mode == 'batch-no-after':
                        if result.get('after_skipped') is not True or 'after' in result:
                            raise RuntimeError('no_after route did not skip the after-snapshot')
                        continue
                    snapshot = result['after']
                deadline = time.monotonic()+1
                while state.get('text') != text and time.monotonic() < deadline:
                    cu.check_cancel()
                    time.sleep(.005)
                if state.get('text') != text:
                    raise RuntimeError('independent app state differs')
                row.update(ok=True, total_ms=(time.perf_counter()-started)*1000)
                write_report(report, args.report)
        report['tasks_ok'] = True
    finally:
        def cleanup():
            errors = report['cleanup_errors'] = []
            def attempt(label, operation):
                try:
                    operation()
                except BaseException:
                    errors.append(label)
            def stop_browser():
                if browser is not None and browser.poll() is None:
                    browser.terminate()
                    try:
                        browser.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        browser.kill()
                        browser.wait(timeout=3)
            def restore():
                cu.check_cancel()
                active = json.loads(cu.run(['hyprctl', '-j', 'activeworkspace'], env))['id']
                if active == workspace:
                    cu.run(['hyprctl', 'dispatch',
                            f'hl.dsp.focus({{ workspace = "{original_workspace}" }})'], env)
                    if original and any(w.get('address') == original for w in cu.hypr(env, 'clients')):
                        cu.focus(env, original)
                    wait_workspace(cu, env, original_workspace)
            # Each owner is optional: setup can fail before it exists.
            if worker is not None:
                attempt('worker_close', worker.close)
            attempt('browser_reap', stop_browser)
            if thread_started:
                attempt('server_shutdown', server.shutdown)
                attempt('server_thread_join', lambda: thread.join(timeout=2))
            if server is not None:
                attempt('server_close', server.server_close)
            attempt('workspace_restore', restore)
            if thread_started and thread.is_alive():
                errors.append('server_thread_alive')
            if temporary is not None:
                attempt('profile_remove', temporary.cleanup)
            report['cleanup_ok'] = not errors
        finish_report(report, args.report, cleanup)
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cli', type=Path, default=Path(__file__).resolve().parents[1]/'scripts/cu.py')
    parser.add_argument('--samples', type=int, default=30)
    parser.add_argument('--delay', type=int, choices=[-1, 0, 16, 50, 100, 250], default=0)
    parser.add_argument('--modes', nargs='+',
                        choices=['split', 'batch', 'batch-no-after', *TASK_MODES],
                        default=['split', 'batch'])
    parser.add_argument('--controls', type=int, default=0,
                        help='extra inert fixture inputs, 0..1000; makes after-snapshot cost real')
    parser.add_argument('--cold', action='store_true', help='measure first task without warm-up')
    parser.add_argument('--report', type=Path, required=True)
    parser.add_argument('--inside', action='store_true', help=argparse.SUPPRESS)
    args = parser.parse_args()
    if not 1 <= args.samples <= 30:
        parser.error('samples must be 1..30')
    if not 0 <= args.controls <= 1000:
        parser.error('controls must be 0..1000')
    # The families time different work, so mixing them would blend two scopes.
    if len({'legacy' if mode in ('split', 'batch', 'batch-no-after') else 'task'
            for mode in args.modes}) > 1:
        parser.error('do not mix task modes with split/batch/batch-no-after')
    if args.cold and (args.samples != 1 or len(args.modes) != 1):
        parser.error('cold requires --samples 1 and exactly one mode')
    args.report.parent.mkdir(parents=True, exist_ok=True)
    if not args.inside:
        if os.environ.get('CU_SESSION_TOKEN'):
            parser.error('harness owns its session; launch outside one')
        return subprocess.run([sys.executable, str(args.cli.resolve()), 'session', '--',
                               sys.executable, str(Path(__file__).resolve()), *sys.argv[1:], '--inside']).returncode
    import signal
    def interrupted(*_):
        raise KeyboardInterrupt('fixture interrupted')
    for sig in [signal.SIGTERM, signal.SIGHUP]:
        signal.signal(sig, interrupted)
    result = run(args)
    print(json.dumps({'ok': result['ok'], 'kind': result['kind'], 'summary': result['summary']}), flush=True)
    return 0 if result['ok'] else 1


if __name__ == '__main__':
    sys.exit(main())
