"""Real-implementation run of the rewritten Y1b probes (Phase B gate).

Runs the probe file's OUTER program strings UNCHANGED against the REAL
run_snippet implementation (fixture manifests built at runtime, with
api_sha256 computed from the current code_exec.py bytes), plus the
attack-stub comparison from the probe file to show the discrimination.
The 1e-R and 4a-R2 probes run directly against the real modules.

Exit 0 only when 1e-R, 4a-R2, 10b-R and 10f-R all pass on the real build.
The old 10b/10f outer programs are run as controls and must show the
documented behavior (first-call wall error / snippet-only trace trip).
"""
import json
import pathlib
import sys
import tempfile
import time

REPO = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / 'scripts'))
sys.path.insert(0, str(REPO / 'tests'))

import code_exec  # noqa: E402
import y1b_probes_rewritten as probes  # noqa: E402
from test_code_exec import FakeBackend  # noqa: E402
from test_snippets import _make_root  # noqa: E402


def _real_session(backend, root, wall=2, max_api_calls=32):
    return code_exec.CodeExecSession(
        backend, state_dir=tempfile.mkdtemp(),
        session_token='0123456789abcdef' * 2,
        snippet_root=root, wall_seconds=wall, max_api_calls=max_api_calls)


def check_10b_real():
    """10b-R shapes A and B against the real run_snippet."""
    out = {}
    # Shape A: outer burns 1.5s, snippet does 1.0s, wall 2s. Shared
    # deadline refuses; a fresh deadline would run it.
    root_a = _make_root([{'name': 'slow-act', 'source': probes.SNIPPET_SLOW2}])
    session = _real_session(probes.SleepingBackend(), root_a, wall=2)
    real_a = session.run(probes.OUTER_10B_A)
    attack = probes.Stub('attack')
    attack.snippet_sources['slow-act'] = probes.SNIPPET_SLOW2
    attack_a = attack.run_outer(probes.OUTER_10B_A)
    shape_a = (real_a['ok'] is False and 'wall-clock' in real_a['error']
               and attack_a['ok'] is True)
    out['A'] = {'real': real_a, 'attack': attack_a, 'pass': shape_a}
    # Shape B: try/except around the first call, so the second call runs.
    # Shared deadline: the second call adds ~0 observes in ~0s. Fresh
    # deadline (attack): a full second set, 8 observes total in ~4s.
    root_b = _make_root([{'name': 'slow-act', 'source': probes.SNIPPET_SLOW6}])
    backend = probes.SleepingBackend()
    session = _real_session(backend, root_b, wall=2)
    started = time.monotonic()
    real_b = session.run(probes.OUTER_10B_B)
    elapsed_b = time.monotonic() - started
    attack = probes.Stub('attack')
    attack.snippet_sources['slow-act'] = probes.SNIPPET_SLOW6
    attack_b = attack.run_outer(probes.OUTER_10B_B)
    shape_b = (real_b['ok'] is False and 'wall-clock' in real_b['error']
               and backend.observe_calls <= 5 and elapsed_b < 3.0
               and attack_b['observes'] >= 8 and attack_b['elapsed'] >= 3.5)
    out['B'] = {'real': real_b, 'real_observes': backend.observe_calls,
                'real_elapsed': round(elapsed_b, 2), 'attack': attack_b,
                'pass': shape_b}
    return {'probe': '10b-R', 'pass': bool(shape_a and shape_b),
            'detail': [('shape A discriminates (real refuses, attack runs)',
                        shape_a),
                       ('shape B discriminates (real <=5 obs <3s, '
                        'attack 8 obs >=3.5s)', shape_b)],
            'evidence': [json.dumps(out, default=str)[:1200]]}


def check_10f_real():
    """10f-R against the real run_snippet."""
    root = _make_root([{'name': 'many-lines', 'source': probes.SNIPPET_MANY}])
    session = _real_session(FakeBackend(), root, wall=30)
    real = session.run(probes.OUTER_10F)
    attack = probes.Stub('attack', wall=30)
    attack.snippet_sources['many-lines'] = probes.SNIPPET_MANY
    attack_out = attack.run_outer(probes.OUTER_10F)
    passed = (real['ok'] is False
              and 'trace step budget exceeded' in real['error']
              and attack_out['ok'] is True)
    return {'probe': '10f-R', 'pass': passed,
            'detail': [('real refuses on shared trace counter, attack runs',
                        passed)],
            'evidence': [json.dumps({'real': real, 'attack': attack_out},
                                    default=str)[:800]]}


def check_old_controls_real():
    """Old 10b/10f outer programs against the real implementation."""
    root_b = _make_root([{'name': 'slow-act', 'source': probes.SNIPPET_SLOW6}])
    backend = probes.SleepingBackend()
    session = _real_session(backend, root_b, wall=2)
    started = time.monotonic()
    old_b = session.run(probes.OUTER_10B_OLD)
    elapsed_b = time.monotonic() - started
    root_f = _make_root([{'name': 'many-lines',
                          'source': probes.SNIPPET_MANY_OLD}])
    session = _real_session(FakeBackend(), root_f, wall=30)
    old_f = session.run(probes.OUTER_10F_OLD)
    return {'probe': 'OLD-controls-real', 'pass': True,
            'detail': [('old 10b: wall error on first call, second never '
                        'runs (observes=%d, elapsed=%.2fs)'
                        % (backend.observe_calls, elapsed_b),
                        old_b['ok'] is False
                        and 'wall-clock' in old_b['error']
                        and backend.observe_calls <= 5),
                       ('old 10f: snippet alone trips the trace cap',
                        old_f['ok'] is False
                        and 'trace step budget exceeded' in old_f['error'])],
            'evidence': [json.dumps({'old_10b': old_b, 'old_10f': old_f},
                                    default=str)[:800]]}


def main():
    results = []
    results.append(probes.probe_1e_rewritten(probes.codemode, probes.code_exec))
    results.append(probes.probe_4a_rewritten(probes.codemode, probes.code_exec))
    results.append(check_10b_real())
    results.append(check_10f_real())
    results.append(check_old_controls_real())
    for r in results:
        print('=' * 70)
        print(r['probe'], 'PASS' if r['pass'] else 'FAIL')
        for d in r.get('detail', []):
            print('  ', d[0], '=>', d[1])
        for e in r.get('evidence', []):
            print('   evidence:', e)
    gate = [r for r in results
            if r['probe'] in ('1e-R', '4a-R2', '10b-R', '10f-R')]
    ok = all(r['pass'] for r in gate) and len(gate) == 4
    print('=' * 70)
    print('G-Y1B real-implementation gate:', 'PASS' if ok else 'FAIL',
          '(%d/4)' % sum(1 for r in gate if r['pass']))
    return 0 if ok else 1


if __name__ == '__main__':
    raise SystemExit(main())
