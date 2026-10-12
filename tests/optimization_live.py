#!/usr/bin/env python3
"""Real GTK tasks with reset/verifier. Reports contain synthetic data only.

Launches one CLI-owned session; --cli selects the engine and its fixture root.
No account activity, settings changes or automatic input retry.
"""
import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import select
import signal
import statistics
import subprocess
import sys
import tempfile
import time


def summary(values):
    ordered = sorted(values)
    return {'samples': len(values), 'median_ms': round(statistics.median(values), 3),
            'p95_ms': round(ordered[math.ceil(.95 * len(values)) - 1], 3)}


def verified(case, state, expected):
    if case.startswith('type') or case == 'chord':
        return state.get('text') == expected
    if case == 'click':
        return state.get('clicks') == 1
    if case == 'scroll':
        # Direction-only task: Wayland wheel units are not CSS/GTK pixels.
        return state.get('scroll', 0) > 0
    if case == 'drag':
        pos = state.get('drag', [])
        return len(pos) == 2 and abs(pos[0] - 140) <= 3 and abs(pos[1] - 60) <= 3
    raise ValueError('unknown task')


def run(args):
    root = args.cli.resolve().parents[1]
    sys.path.insert(0, str(root / 'scripts'))
    import cu
    cu.require_session()
    env = cu.environment()
    env.pop('GTK_IM_MODULE', None)
    previous = cu.hypr(env, 'activewindow').get('address')
    # Select an unused workspace, rather than moving real applications.
    used = {w['id'] for w in cu.hypr(env, 'workspaces')}
    workspace = next(i for i in range(101, 201) if i not in used)
    original_workspace = json.loads(cu.run(['hyprctl', '-j', 'activeworkspace'], env))['id']
    rows, driver, fixture = [], None, None
    report = {'kind': 'real_gtk_fixture', 'samples': rows, 'ok': False,
              'settings': {'samples': args.samples, 'cases': args.cases, 'no_after': args.no_after},
              'engine_sha256': hashlib.sha256(args.cli.resolve().read_bytes()).hexdigest()}

    def save_report():
        args.report.parent.mkdir(parents=True, exist_ok=True)
        temporary = None
        try:
            with tempfile.NamedTemporaryFile(mode='w', dir=args.report.parent,
                                             prefix='.report-', delete=False) as stream:
                temporary = Path(stream.name)
                json.dump(report, stream, indent=2)
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(temporary, args.report)
        finally:
            if temporary is not None:
                temporary.unlink(missing_ok=True)

    def wait_for(fn, timeout=3):
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            cu.check_cancel()
            result = fn()
            if result:
                return result
            time.sleep(.005)
        raise RuntimeError('fixture verification timeout')

    def receive():
        deadline = time.monotonic() + 15
        while time.monotonic() < deadline:
            cu.check_cancel()
            if select.select([driver.stdout], [], [], .04)[0]:
                line = driver.stdout.readline(65537)
                if not line.endswith('\n') or len(line) > 65536:
                    raise RuntimeError('relay framing failed')
                return json.loads(line)
        raise RuntimeError('relay timeout')

    def command(argv, data=''):
        cu.check_cancel()
        driver.stdin.write(json.dumps({'args': argv, 'stdin': data}, ensure_ascii=False) + '\n')
        driver.stdin.flush()
        reply = receive()
        if reply.get('returncode') != 0 or reply.get('result', {}).get('ok') is False:
            raise RuntimeError('CLI refused fixture action')
        return reply['result']

    def stop(process):
        if process is None:
            return
        if process.poll() is None:
            process.terminate()
            try:
                process.wait(timeout=3)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=3)
        for stream in (process.stdin, process.stdout, process.stderr):
            if stream:
                stream.close()

    with tempfile.TemporaryDirectory(prefix='cu-optimization-') as folder:
        state_path = Path(folder) / 'state.json'
        def state():
            try:
                return json.loads(state_path.read_text())
            except (OSError, ValueError):
                return {}
        address = None
        try:
            cu.run(['hyprctl', 'dispatch', f'hl.dsp.focus({{ workspace = "{workspace}" }})'], env)
            wait_for(lambda: json.loads(cu.run(['hyprctl', '-j', 'activeworkspace'], env))['id'] == workspace)
            fixture = subprocess.Popen([sys.executable, str(root / 'tests/optimization_fixture.py'),
                                        str(state_path)], env=env, stdin=subprocess.PIPE,
                                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, text=True)
            def find():
                matches = [w for w in cu.hypr(env, 'clients') if w.get('pid') == fixture.pid]
                return matches[0] if len(matches) == 1 and state().get('layout') else None
            window = wait_for(find, 8)
            address = window['address']
            cu.focus(env, address)
            cu.wait_cancelable(.3)  # setup animation, outside task timing
            driver = subprocess.Popen([sys.executable, str(args.cli.resolve()), 'session-driver'],
                                      env=env, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                      stderr=subprocess.DEVNULL, text=True, bufsize=1)
            if receive().get('driver') != 'ready':
                raise RuntimeError('relay not ready')
            for index in range(args.samples):
                for case in args.cases:
                    nonce = f'{index}:{case}'
                    initial = 'abcdef' if case == 'chord' else ''
                    fixture.stdin.write(json.dumps({'nonce': nonce, 'text': initial}) + '\n')
                    fixture.stdin.flush()
                    wait_for(lambda: state().get('nonce') == nonce and state().get('text') == initial)
                    observed = command(['observe', '--window', address, '--max-width', '1280'])
                    meta = json.loads(Path(observed['observation']).read_text())
                    layout = state()['layout']
                    def point(name, x=.5, y=.5):
                        bx, by, bw, bh = layout[name]
                        return [(bx + bw*x)*meta['image_size'][0]/meta['region'][2],
                                (by + bh*y)*meta['image_size'][1]/meta['region'][3]]
                    expected = None
                    if case.startswith('type'):
                        size = int(case[4:])
                        expected = ('abc Việt 123 ' * ((size // 13) + 2))[:size]
                        actions = [{'type': 'type', 'text': expected}]
                    elif case == 'chord':
                        expected = 'abcde'
                        actions = [{'type': 'key', 'keys': ['Ctrl', 'a']},
                                   {'type': 'type', 'text': expected}]
                    elif case == 'drag':
                        cx, cy, _, _ = layout['canvas']
                        scale = meta['image_size'][0] / meta['region'][2]
                        actions = [{'type': 'drag', 'from': [(cx+130)*scale, (cy+60)*scale],
                                    'to': [(cx+170)*scale, (cy+80)*scale], 'ms': 150}]
                    else:
                        x, y = point('button' if case == 'click' else 'scrollbox')
                        actions = [{'type': case, 'x': x, 'y': y}]
                        if case == 'scroll':
                            actions[0]['dy'] = 30
                    argv = ['act', '--observation', observed['observation'], '--actions', '-']
                    if args.no_after:
                        argv.append('--no-after')
                    row = {'case': case, 'index': index, 'ok': False}
                    rows.append(row)
                    save_report()  # A killed driver must not leave a prior successful report.
                    started = time.perf_counter()
                    result = command(argv, json.dumps(actions, ensure_ascii=False))
                    response_ms = (time.perf_counter() - started)*1000
                    wait_for(lambda: verified(case, state(), expected))
                    row.update(ok=True, total_ms=(time.perf_counter()-started)*1000,
                               response_ms=response_ms, execution_ms=result['execution_ms'])
                    save_report()
            driver.stdin.write('{"args":["finish"]}\n')
            driver.stdin.flush()
            if receive().get('driver') != 'finished':
                raise RuntimeError('relay did not finish')
            driver.stdin.close()
            if driver.wait(timeout=3) != 0:
                raise RuntimeError('relay failed at finish')
            report['tasks_ok'] = True
        finally:
            cleanup_errors = []
            for process in (driver, fixture):
                try:
                    stop(process)
                except Exception:
                    cleanup_errors.append('owned child cleanup failed')
            report['cleanup'] = {'children_reaped': not cleanup_errors, 'focus_preserved': False}
            # Cancellation is never cleared. Restore only our owned workspace choice.
            try:
                cu.check_cancel()
                active = json.loads(cu.run(['hyprctl', '-j', 'activeworkspace'], env))['id']
                if active == workspace:
                    cu.run(['hyprctl', 'dispatch',
                            f'hl.dsp.focus({{ workspace = "{original_workspace}" }})'], env)
                    if previous and any(w.get('address') == previous for w in cu.hypr(env, 'clients')):
                        cu.focus(env, previous)
                    wait_for(lambda: json.loads(cu.run(['hyprctl', '-j', 'activeworkspace'], env))['id']
                             == original_workspace)
                report['cleanup']['focus_preserved'] = True
            finally:
                report['ok'] = bool(report.get('tasks_ok') and all(report['cleanup'].values()))
                report['summary'] = {case: summary([r['total_ms'] for r in rows
                                                     if r['case'] == case and r['ok']])
                                     for case in args.cases
                                     if any(r['case'] == case and r['ok'] for r in rows)}
                save_report()
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cli', type=Path, default=Path(__file__).resolve().parents[1]/'scripts/cu.py')
    parser.add_argument('--report', type=Path, required=True)
    parser.add_argument('--samples', type=int, default=3)
    parser.add_argument('--cases', nargs='+', choices=['type32', 'type481', 'chord', 'click', 'scroll', 'drag'],
                        default=['type32', 'type481', 'chord', 'click', 'scroll', 'drag'])
    parser.add_argument('--no-after', action='store_true')
    parser.add_argument('--inside', action='store_true', help=argparse.SUPPRESS)
    args = parser.parse_args()
    if not 1 <= args.samples <= 30:
        parser.error('samples must be 1..30')
    if not args.inside:
        if os.environ.get('CU_SESSION_TOKEN'):
            parser.error('launch outside a session; the harness owns exactly one session')
        return subprocess.run([sys.executable, str(args.cli.resolve()), 'session', '--',
                               sys.executable, str(Path(__file__).resolve()), *sys.argv[1:], '--inside']).returncode
    def interrupted(_signum, _frame):
        # Unwind fixture cleanup/report on guardian cancellation; never resume input.
        raise KeyboardInterrupt('fixture interrupted')
    for sig in (signal.SIGTERM, signal.SIGHUP):
        signal.signal(sig, interrupted)
    try:
        report = run(args)
    except Exception:
        print(json.dumps({'ok': False, 'fixture_failed': True}), flush=True)
        raise
    print(json.dumps({'ok': report['ok'], 'kind': report['kind'], 'summary': report['summary']}), flush=True)
    return 0 if report['ok'] else 1


if __name__ == '__main__':
    sys.exit(main())
