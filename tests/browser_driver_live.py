#!/usr/bin/env python3
"""Run only inside computer-use session; isolated Chromium + source relay fixture."""
import json
from pathlib import Path
import select
import statistics
import subprocess
import sys
import tempfile
import time
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import cu


def receive(driver):
    cu.check_cancel()
    if not select.select([driver.stdout], [], [], 10)[0]:
        raise RuntimeError('fixture driver response timed out')
    line = driver.stdout.readline(65537)
    if not line.endswith('\n') or len(line) > 65536:
        raise RuntimeError('fixture driver response framing failed')
    return json.loads(line)


def command(driver, args, data=''):
    cu.check_cancel()
    payload = json.dumps({'args': args, 'stdin': data}, ensure_ascii=False) + '\n'
    if len(payload.encode()) > 1000:
        raise RuntimeError('fixture request exceeds its small-message budget')
    start = time.monotonic()
    driver.stdin.write(payload)
    driver.stdin.flush()
    response = receive(driver)
    elapsed = (time.monotonic() - start) * 1000
    if response.get('returncode') != 0 or 'result' not in response:
        raise RuntimeError('fixture driver command failed')
    result = response['result']
    if isinstance(result, dict) and result.get('ok') is False:
        raise RuntimeError('fixture browser command failed')
    return result, elapsed


def node_identity(driver):
    result = subprocess.run(['pgrep', '-P', str(driver.pid)], capture_output=True,
                            text=True, timeout=2)
    children = result.stdout.split()
    if result.returncode != 0 or len(children) != 1:
        raise RuntimeError('fixture expected exactly one worker child')
    pid = int(children[0])
    if (Path('/proc') / str(pid) / 'exe').resolve().name != 'node':
        raise RuntimeError('fixture child is not Node')
    return pid, process_start(pid)


def process_start(pid):
    try:
        return (Path('/proc') / str(pid) / 'stat').read_text().rsplit(')', 1)[1].split()[19]
    except FileNotFoundError:
        return None


def stop_owned(process):
    if process is None:
        return
    try:
        if process.poll() is None:
            process.terminate()
        try:
            process.wait(timeout=3)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=3)
    finally:
        for stream in (process.stdin, process.stdout, process.stderr):
            if stream is not None and not stream.closed:
                stream.close()


def main():
    if not cu.os.environ.get('CU_SESSION_TOKEN'):
        raise RuntimeError('fixture requires computer-use session')
    cu.check_cancel()
    env = cu.environment()
    original = cu.hypr(env, 'activewindow').get('address')
    endpoint = None
    driver = chromium = None
    with tempfile.TemporaryDirectory(prefix='cu-browser-driver-') as profile:
        try:
            fixture = (ROOT / 'tests/fixture.html').as_uri()
            chromium = subprocess.Popen([
                'chromium', '--user-data-dir=' + profile,
                '--remote-debugging-port=0', '--remote-debugging-address=127.0.0.1',
                '--no-first-run', '--no-default-browser-check',
                '--disable-background-networking', fixture], env=env,
                stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            deadline = time.monotonic() + 10
            target = None
            while time.monotonic() < deadline:
                cu.check_cancel()
                if chromium.poll() is not None:
                    raise RuntimeError('fixture Chromium exited during startup')
                try:
                    port = int((Path(profile) / 'DevToolsActivePort').read_text().splitlines()[0])
                    endpoint = 'http://127.0.0.1:' + str(port)
                    with urllib.request.urlopen(endpoint + '/json/list', timeout=.5) as response:
                        tabs = json.load(response)
                    target = next((tab['id'] for tab in tabs
                                   if tab.get('type') == 'page' and tab.get('url') == fixture), None)
                    if target:
                        break
                except (OSError, ValueError, IndexError):
                    pass
                time.sleep(.05)
            if not target:
                raise RuntimeError('fixture Chromium target did not appear')
            driver = subprocess.Popen([sys.executable, str(ROOT / 'scripts/cu.py'), 'session-driver'],
                                      env=env, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                      stderr=subprocess.DEVNULL, text=True, bufsize=1)
            ready = receive(driver)
            assert ready.get('ok') is True and ready.get('driver') == 'ready'
            base = ['--endpoint', endpoint, '--target', target, '--max-elements', '16']
            observe = ['browser', 'observe', *base]
            snapshot, first_ms = command(driver, observe)
            assert snapshot['elements'] and len(snapshot['elements']) <= 16
            identity = node_identity(driver)
            assert identity[1] is not None
            text = 'Tiếng Việt 🐱'
            actions = [{'type': 'fill', 'selector': '#name', 'text': text},
                       {'type': 'click', 'selector': '#save'},
                       {'type': 'assert', 'selector': '#status', 'text': 'Saved ' + text}]
            acted, act_ms = command(driver, ['browser', 'act', *base,
                                            '--snapshot', snapshot['snapshot'], '--actions', '-'],
                                    json.dumps(actions, ensure_ascii=False))
            assert acted['ok'] is True and acted['completed'] == 3
            assert node_identity(driver) == identity
            captured, image_ms = command(driver, [*observe, '--image'])
            from PIL import Image
            with Image.open(captured['image']) as image:
                image.load()
                assert image.format == 'PNG' and image.width > 0 and image.height > 0
            assert node_identity(driver) == identity
            timings, output_bytes = [], []
            for _ in range(6):
                snapshot, elapsed = command(driver, observe)
                assert snapshot['elements'] and len(snapshot['elements']) <= 16
                assert node_identity(driver) == identity
                timings.append(elapsed)
                output_bytes.append(len(json.dumps(snapshot, ensure_ascii=False).encode()))
            driver.stdin.write('{"args":["finish"]}\n')
            driver.stdin.flush()
            finished = receive(driver)
            assert finished.get('ok') is True and finished.get('driver') == 'finished'
            driver.stdin.close()
            assert driver.wait(timeout=5) == 0
            deadline = time.monotonic() + 2
            while process_start(identity[0]) == identity[1] and time.monotonic() < deadline:
                cu.check_cancel()
                time.sleep(.05)
            assert process_start(identity[0]) != identity[1]
            return {'ok': True, 'unicode_fill_click_assert': True, 'png_readback': True,
                    'one_node_worker': True, 'worker_reaped': True, 'driver_exit_zero': True,
                    'first_observe_ms': round(first_ms, 3), 'act_ms': round(act_ms, 3),
                    'image_ms': round(image_ms, 3), 'repeat_observe_median_ms': round(statistics.median(timings), 3),
                    'repeat_observe_samples': 6, 'mean_output_bytes': round(statistics.mean(output_bytes))}
        finally:
            try:
                stop_owned(driver)
            finally:
                try:
                    stop_owned(chromium)
                finally:
                    if original:
                        try:
                            cu.check_cancel()
                            cu.focus(env, original)
                        except Exception:
                            pass


if __name__ == '__main__':
    try:
        report = main()
    except BaseException:
        print(json.dumps({'ok': False, 'fixture_failed': True}), flush=True)
        sys.exit(1)
    print(json.dumps(report, separators=(',', ':')), flush=True)
