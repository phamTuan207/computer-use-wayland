"""Benchmark the native pointer ACK round-trip against the mocked harness.

Reuses tests/test_pointer_native.py, so the binary measured is the real
native/pointer.c built against its in-process Wayland mock. This measures the
helper protocol round-trip (write command -> read "ok") only. The mock has no
compositor, so these numbers are NOT desktop/Wayland latency.
"""
import importlib.util
from pathlib import Path
import statistics
import time

HERE = Path(__file__).resolve().parent
ROUNDS = 200

_spec = importlib.util.spec_from_file_location(
    'test_pointer_native', HERE / 'test_pointer_native.py')
harness = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(harness)


def summarize(samples):
    ordered = sorted(samples)
    rank = max(1, min(len(ordered), int(0.95 * len(ordered) + 0.999)))
    return {'n': len(ordered), 'median': statistics.median(ordered),
            'p95': ordered[rank - 1], 'min': ordered[0], 'max': ordered[-1]}


def send(case, process, command):
    process.stdin.write(command)
    process.stdin.flush()
    case.expect_line(process.stdout, b'ok\n')


def measure(case, process, commands, rounds):
    samples = []
    for i in range(rounds):
        command = commands[i % len(commands)]
        began = time.perf_counter_ns()
        send(case, process, command)
        samples.append((time.perf_counter_ns() - began) / 1e6)
    return samples


def main():
    harness.NativePointer.setUpClass()
    case = harness.NativePointer('run')  # helpers only; never executes its tests
    try:
        process = case.start()
        case.hold(process)  # waits for "ready" and warms the button path
        plans = {
            'abs': [b'abs 10 10 1280 800\n'],
            'button': [b'button 1 1\n', b'button 1 0\n'],
            'scroll': [b'scroll 0 15\n'],
        }
        print(f'rounds={ROUNDS} per command; mock Wayland, no desktop latency')
        print(f'{"command":8} {"n":>4} {"median_ms":>10} {"p95_ms":>9} '
              f'{"min_ms":>9} {"max_ms":>9}')
        for name, commands in plans.items():
            for command in commands:  # warm every branch of this plan
                send(case, process, command)
            stats = summarize(measure(case, process, commands, ROUNDS))
            print(f'{name:8} {stats["n"]:>4} {stats["median"]:>10.4f} '
                  f'{stats["p95"]:>9.4f} {stats["min"]:>9.4f} {stats["max"]:>9.4f}')
            assert stats['n'] == ROUNDS and 0 < stats['median'] <= stats['p95']
    finally:
        case.doCleanups()
        harness.NativePointer.doClassCleanups()


if __name__ == '__main__':
    main()
