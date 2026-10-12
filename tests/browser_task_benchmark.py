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

PAGE = b'''<!doctype html><meta charset="utf-8">
<input id="name"><button id="save">Save fixture</button><p id="status">Ready</p>
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
</script>'''


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


def finish_report(report, path, cleanup):
    report['cleanup_ok'] = False
    try:
        cleanup()
    finally:
        report['ok'] = bool(report.get('tasks_ok') and report['cleanup_ok'])
        rows = report['samples']
        report['summary'] = {mode: summary([r['total_ms'] for r in rows if r['mode']==mode and r['ok']])
                             for mode in ['split', 'batch'] if any(r['mode']==mode and r['ok'] for r in rows)}
        write_report(report, path)


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
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *_):
            pass
        def do_GET(self):
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(PAGE)
        def do_POST(self):
            size = int(self.headers.get('Content-Length', 0))
            if self.path != '/done' or not 0 < size < 2000:
                self.send_error(400)
                return
            data = json.loads(self.rfile.read(size))
            state['text'] = data.get('text')
            self.send_response(204)
            self.end_headers()
    server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    browser = None
    worker = BrowserWorker()
    rows = []
    report = {'kind': 'real_chromium_fixture', 'phase': 'cold' if args.cold else 'warm',
              'delay_ms': args.delay, 'modes': list(args.modes), 'samples_per_mode': args.samples,
              'provenance': 'source_tree' if root == Path(__file__).resolve().parents[1] else 'external_cli',
              'runtime_sha256': {name: hashlib.sha256((root/'scripts'/name).read_bytes()).hexdigest()
                                 for name in ['cu.py', 'browser_worker.py', 'cdp.mjs']},
              'ok': False, 'samples': rows, 'warmup': []}
    temporary = tempfile.TemporaryDirectory(prefix='cu-task-browser-')
    with temporary as folder:
        try:
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
            base = {'endpoint': endpoint, 'target': target, 'max_elements': 8}
            for i in range(0 if args.cold else -1, args.samples):
                for mode in (args.modes if i%2 == 0 else list(reversed(args.modes))):
                    cu.check_cancel()
                    snapshot = worker.request({**base, 'operation': 'observe'})
                    text = f'Fixture {i} Việt 🐱'
                    state.clear()
                    actions = [{'type': 'fill', 'selector': '#name', 'text': text},
                               {'type': 'click', 'selector': '#save'},
                               {'type': 'assert', 'selector': '#status', 'text': 'Saved '+text,
                                'timeout_ms': 1000}]
                    row = {'mode': mode, 'index': i, 'ok': False, 'calls': 0, 'result_bytes': 0}
                    (rows if i >= 0 else report['warmup']).append(row)
                    write_report(report, args.report)  # Keep an incomplete row if guardian kills cleanup.
                    started = time.perf_counter()
                    groups = [actions] if mode == 'batch' else [actions[:1], actions[1:2],
                              [{'type': 'wait', 'ms': 80}], actions[2:]]
                    for group in groups:
                        result = worker.request({**base, 'operation': 'act',
                                                 'snapshot': snapshot['snapshot'], 'actions': group})
                        row['calls'] += 1
                        row['result_bytes'] += len(json.dumps(result, ensure_ascii=False).encode())
                        if not result.get('ok'):
                            raise RuntimeError('fixture task refused or condition timed out')
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
                attempt('worker_close', worker.close)
                attempt('browser_reap', stop_browser)
                attempt('server_shutdown', server.shutdown)
                attempt('server_close', server.server_close)
                attempt('server_thread_join', lambda: thread.join(timeout=2))
                attempt('workspace_restore', restore)
                if thread.is_alive():
                    errors.append('server_thread_alive')
                attempt('profile_remove', temporary.cleanup)
                report['cleanup_ok'] = not errors
            finish_report(report, args.report, cleanup)
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cli', type=Path, default=Path(__file__).resolve().parents[1]/'scripts/cu.py')
    parser.add_argument('--samples', type=int, default=30)
    parser.add_argument('--delay', type=int, choices=[-1, 0, 16, 50, 100, 250], default=0)
    parser.add_argument('--modes', nargs='+', choices=['split', 'batch'], default=['split', 'batch'])
    parser.add_argument('--cold', action='store_true', help='measure first task without warm-up')
    parser.add_argument('--report', type=Path, required=True)
    parser.add_argument('--inside', action='store_true', help=argparse.SUPPRESS)
    args = parser.parse_args()
    if not 1 <= args.samples <= 30:
        parser.error('samples must be 1..30')
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
