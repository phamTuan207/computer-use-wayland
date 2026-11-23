#!/usr/bin/env python3
"""Opt-in bare/stale broker proof. This never performs GUI input."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import secrets
import shutil
import signal
import socket
import stat
import subprocess
import sys
import tempfile
import time
import uuid

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / 'scripts'
sys.path.insert(0, str(SCRIPTS))
import cu
import session_remote

SESSION_KEYS = set('XDG_RUNTIME_DIR WAYLAND_DISPLAY DISPLAY HYPRLAND_INSTANCE_SIGNATURE '
                   'DBUS_SESSION_BUS_ADDRESS XDG_CURRENT_DESKTOP XDG_SESSION_DESKTOP '
                   'XDG_SESSION_TYPE XDG_SEAT XDG_VTNR USER HOME LOGNAME PATH GDK_BACKEND '
                   'QT_QPA_PLATFORM ELECTRON_OZONE_PLATFORM_HINT MOZ_ENABLE_WAYLAND'.split())
IDENTITY_KEYS = {'USER', 'HOME', 'LOGNAME', 'PATH'}
ROUTING_KEYS = SESSION_KEYS - IDENTITY_KEYS
DONOR_ORDER = ('quickshell', 'waybar', 'kitty', 'Hyprland')
TOKEN_RE = re.compile(r'[0-9a-f]{32}\Z')


class ProofBlocked(RuntimeError):
    pass


def _decode_env(raw):
    values = {}
    token_present = False
    token_valid = False
    gtk_present = False
    for item in raw.decode('utf-8', 'surrogateescape').split('\0'):
        key, separator, value = item.partition('=')
        if not separator:
            continue
        if key in SESSION_KEYS:
            values[key] = value
        elif key == 'CU_SESSION_TOKEN':
            token_present = bool(value)
            token_valid = bool(TOKEN_RE.fullmatch(value))
        elif key == 'GTK_IM_MODULE':
            gtk_present = True
    return values, token_present, token_valid, gtk_present


def _process_env(pid):
    try:
        folder = Path('/proc', str(pid))
        info = folder.stat()
        if info.st_uid != os.geteuid():
            return None
        return _decode_env((folder / 'environ').read_bytes())
    except (OSError, UnicodeError, ValueError):
        return None


def _read_donor(pid):
    try:
        folder = Path('/proc', str(pid))
        info = folder.stat()
        if info.st_uid != os.geteuid():
            return None
        raw = {}
        for item in (folder / 'environ').read_bytes().decode(
                'utf-8', 'surrogateescape').split('\0'):
            key, separator, value = item.partition('=')
            if separator and key in SESSION_KEYS:
                raw[key] = value
        return raw
    except (OSError, UnicodeError, ValueError):
        return None


def _host_quickshell(pid):
    try:
        return b'/usr/share/omarchy/shell' in Path('/proc', str(pid), 'cmdline').read_bytes()
    except OSError:
        return False


def find_verified_host_donor():
    by_tuple = {}
    for name in DONOR_ORDER:
        try:
            result = subprocess.run(['pgrep', '-x', name], capture_output=True,
                                    text=True, timeout=2, check=False)
        except (OSError, subprocess.SubprocessError):
            continue
        for pid in result.stdout.split() if result.returncode == 0 else ():
            if not pid.isdigit():
                continue
            try:
                if Path('/proc', pid).stat().st_uid != os.geteuid():
                    continue
            except OSError:
                continue
            if name == 'quickshell' and not _host_quickshell(pid):
                continue
            donor = _read_donor(pid)
            if not donor:
                continue
            runtime = donor.get('XDG_RUNTIME_DIR')
            if not runtime or not cu._private_runtime(runtime):
                continue
            try:
                values = cu._validate_session_tuple(donor)
            except (OSError, RuntimeError, TypeError, ValueError):
                continue
            key = tuple(values[field] for field in (
                'XDG_RUNTIME_DIR', 'WAYLAND_DISPLAY', 'HYPRLAND_INSTANCE_SIGNATURE'))
            if key not in by_tuple:
                by_tuple[key] = dict(donor)
                continue
            selected = by_tuple[key]
            if (selected.get('XDG_SEAT') and donor.get('XDG_SEAT') and
                    selected['XDG_SEAT'] != donor['XDG_SEAT']):
                continue
            for field, value in donor.items():
                if field in SESSION_KEYS and value and not selected.get(field):
                    selected[field] = value
    if len(by_tuple) != 1:
        if len(by_tuple) > 1:
            raise ProofBlocked('multiple_verified_host_sessions')
        raise ProofBlocked('no_verified_host_donor')
    expected = next(iter(by_tuple.values()))
    missing = sorted(key for key in SESSION_KEYS if not expected.get(key))
    if missing:
        raise ProofBlocked('full_key_proof_blocked_missing=' + ','.join(missing))
    try:
        cu._validate_session_tuple(expected)
    except Exception as error:
        raise ProofBlocked('host_donor_tuple_validation_failed') from error
    return expected


def _client_environment():
    home = os.environ.get('HOME') or str(Path.home())
    return {'HOME': home, 'USER': os.environ.get('USER', 'testuser'),
            'LOGNAME': os.environ.get('LOGNAME', os.environ.get('USER', 'testuser')),
            'PATH': '/usr/bin:/bin', 'PYTHONDONTWRITEBYTECODE': '1'}


def _check_installed_broker(client_env):
    try:
        result = subprocess.run([sys.executable, '-B', str(SCRIPTS / 'session_remote.py'),
                                 'status'], env=client_env, capture_output=True,
                                text=True, timeout=5, check=False)
        status = json.loads(result.stdout) if result.returncode == 0 else None
    except (OSError, subprocess.SubprocessError, json.JSONDecodeError):
        status = None
    if not isinstance(status, dict) or not status.get('ok') or status.get('broker') != 'running':
        raise ProofBlocked('installed_broker_status_unavailable')
    if (status.get('state') != 'idle' or status.get('owner') is not None or
            status.get('cancelled') is not False or
            status.get('cancellation_state') != 'clear' or
            status.get('recovery') != 'none'):
        raise ProofBlocked('installed_broker_not_idle_or_safety_gate_active')
    try:
        if session_remote._cancelled(session_remote.CANCEL):
            raise ProofBlocked('shared_cancellation_latch_is_set')
        if session_remote._read_snapshot(session_remote.SNAPSHOT) is not None:
            raise ProofBlocked('shared_session_snapshot_requires_recovery')
    except session_remote.BrokerError as error:
        raise ProofBlocked('shared_session_state_unavailable') from error


def _check_readiness(donor):
    try:
        session_remote.native_readiness(donor)
    except session_remote.BrokerError as error:
        stage = error.stage or 'readiness'
        diagnostic = error.diagnostic or 'native_unavailable'
        raise ProofBlocked(f'native_readiness_blocked_stage={stage}_diagnostic={diagnostic}') from error
    except Exception as error:
        raise ProofBlocked('native_readiness_blocked_stage=readiness_diagnostic=unknown') from error


def _secure_test_root():
    parent = Path('/tmp/opencode')
    try:
        parent.mkdir(mode=0o700, parents=True, exist_ok=True)
        info = parent.lstat()
    except OSError as error:
        raise ProofBlocked('private_test_directory_unavailable') from error
    if (not stat.S_ISDIR(info.st_mode) or info.st_uid != os.geteuid()):
        raise ProofBlocked('private_test_directory_not_owned')
    return Path(tempfile.mkdtemp(prefix='envsteal-', dir=parent))


def _broker_environment(case, donor):
    environment = _client_environment()
    if case == 'stale':
        environment.update({key: donor[key] for key in
                            ('XDG_RUNTIME_DIR', 'WAYLAND_DISPLAY', 'DISPLAY')
                            if donor.get(key)})
        while True:
            stale = 'envsteal-stale-' + uuid.uuid4().hex
            if not (Path(donor['XDG_RUNTIME_DIR']) / 'hypr' / stale).exists():
                break
        environment['HYPRLAND_INSTANCE_SIGNATURE'] = stale
    return environment


def _proof_request(expected_hash):
    parent, child = socket.socketpair(socket.AF_UNIX, socket.SOCK_STREAM)
    parent.settimeout(5)
    parent.sendall(json.dumps({'channel': 'envsteal-proof-v1',
                               'expected_cu_sha256': expected_hash},
                              separators=(',', ':')).encode())
    return parent, child


def _start_test_broker(test_dir, environment, expected_hash):
    path = test_dir / 'relay.sock'
    parent, child = _proof_request(expected_hash)
    command = [sys.executable, '-B', str(SCRIPTS / 'session_remote.py'), 'serve',
               '--socket', str(path), '--envsteal-test-proof-fd', str(child.fileno())]
    try:
        process = subprocess.Popen(command, env=environment, stdin=subprocess.DEVNULL,
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                   close_fds=True, pass_fds=(child.fileno(),))
    except OSError as error:
        parent.close()
        child.close()
        raise ProofBlocked('test_owned_broker_did_not_start') from error
    child.close()
    try:
        response = bytearray()
        while b'\n' not in response and len(response) <= 2048:
            chunk = parent.recv(2049 - len(response))
            if not chunk:
                break
            response.extend(chunk)
        proof = json.loads(bytes(response).decode('utf-8'))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        if process.poll() is None:
            process.send_signal(signal.SIGTERM)
        try:
            process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            pass
        parent.close()
        raise ProofBlocked('test_owned_broker_source_proof_failed') from error
    finally:
        parent.close()
    if (not isinstance(proof, dict) or proof.get('ok') is not True or
            proof.get('cu_path') != str(SCRIPTS / 'cu.py') or
            proof.get('cu_sha256') != expected_hash or
            proof.get('session_remote_path') != str(SCRIPTS / 'session_remote.py')):
        if process.poll() is None:
            process.send_signal(signal.SIGTERM)
            try:
                process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                pass
        raise ProofBlocked('test_owned_broker_source_assertion_mismatch')
    try:
        _wait_for_status(path, lambda value: value.get('state') == 'idle' and
                         value.get('owner') is None and value.get('cancelled') is False and
                         value.get('recovery') == 'none', process, deadline=15)
    except Exception as error:
        if process.poll() is None:
            process.send_signal(signal.SIGTERM)
            try:
                code = process.wait(timeout=15)
            except subprocess.TimeoutExpired as cleanup_error:
                raise ProofBlocked('test_owned_broker_idle_start_cleanup_timeout') from cleanup_error
            if code != 0:
                raise ProofBlocked('test_owned_broker_idle_start_exit_not_zero') from error
        raise ProofBlocked('test_owned_broker_did_not_become_idle') from error
    return process, path, proof


def _status(path, timeout=3):
    return session_remote._exchange({'command': 'status'}, path=path, timeout=timeout)


def _wait_for_status(path, predicate, process, deadline=25):
    until = time.monotonic() + deadline
    while time.monotonic() < until:
        if process is not None and process.poll() is not None:
            raise RuntimeError('test_owned_broker_exited_before_ready')
        try:
            value = _status(path, timeout=2)
        except session_remote.BrokerError:
            time.sleep(0.1)
            continue
        if predicate(value):
            return value
        time.sleep(0.1)
    raise RuntimeError('bounded_wait_for_broker_state_expired')


def _proc_parent_and_argv(pid):
    try:
        raw = Path('/proc', str(pid), 'stat').read_text()
        tail = raw[raw.rfind(')') + 2:].split()
        parent = int(tail[1])
        argv = [part.decode('utf-8', 'surrogateescape') for part in
                Path('/proc', str(pid), 'cmdline').read_bytes().split(b'\0') if part]
        return parent, argv
    except (OSError, ValueError):
        return None


def _driver_descendant(broker_pid):
    children = {}
    try:
        entries = list(Path('/proc').iterdir())
    except OSError:
        return None
    for entry in entries:
        if not entry.name.isdigit():
            continue
        row = _proc_parent_and_argv(entry.name)
        if row:
            children.setdefault(row[0], []).append((int(entry.name), row[1]))
    pending = [broker_pid]
    descendants = set()
    while pending:
        parent = pending.pop()
        for pid, argv in children.get(parent, ()):
            if pid in descendants:
                continue
            descendants.add(pid)
            pending.append(pid)
            if (len(argv) >= 3 and argv[1] == str(SCRIPTS / 'cu.py') and
                    argv[2] == 'session-driver'):
                try:
                    if Path('/proc', str(pid)).stat().st_uid == os.geteuid():
                        return pid
                except OSError:
                    pass
    return None


def _lease_fields(lease):
    return {'owner': lease['owner'], 'generation': lease['generation'],
            'lease_secret': lease['lease_secret']}


def _finish_owned_lease(path, lease):
    if lease is None:
        return None
    finish = {'command': 'finish', **_lease_fields(lease)}
    response = _exchange_with_timeout(finish, path, timeout=5)
    if not response.get('ok'):
        raise RuntimeError('owned_lease_finish_was_refused')
    final = _wait_for_status(path, lambda value: value.get('state') == 'finished' and
                             value.get('driver') == 'stopped' and
                             value.get('guardian') == 'clean', None)
    if final.get('cancelled') is not False or final.get('cancellation_state') != 'clear':
        raise RuntimeError('cancellation_state_changed_during_test_owned_cleanup')
    if session_remote._read_snapshot(session_remote.SNAPSHOT) is not None:
        raise RuntimeError('owned_lease_left_retained_session_snapshot')
    return final


def _exchange_with_timeout(value, path, timeout):
    return session_remote._exchange(value, path=path, timeout=timeout)


def _cycle(case, index, process, path, donor, inherited_count):
    lease = None
    record = {'case': case, 'cycle': index,
              'inherited_gui_key_count': inherited_count}
    try:
        initial = _status(path)
        idle = (initial.get('state') == 'idle' and initial.get('owner') is None and
                initial.get('driver') == 'idle' and initial.get('guardian') == 'idle')
        finished = (initial.get('state') == 'finished' and
                    initial.get('driver') == 'stopped' and
                    initial.get('guardian') == 'clean')
        if (not (idle or finished) or initial.get('cancelled') is not False or
                initial.get('cancellation_state') != 'clear' or
                initial.get('recovery') != 'none'):
            raise RuntimeError('test_owned_broker_not_idle_before_cycle')

        start_id = session_remote._new_start_id()
        owner = 'envsteal-live-' + uuid.uuid4().hex[:10]
        lease_secret = secrets.token_hex(32)
        command = {'command': 'start', 'owner': owner, 'start_id': start_id,
                   'lease_secret': lease_secret,
                   'broker_generation': initial['broker_generation']}
        started = _exchange_with_timeout(command, path, timeout=5)
        if not started.get('ok'):
            raise RuntimeError('test_owned_start_refused_' + str(started.get('stage',
                                                                            started.get('error', 'unknown')))
                               + '_' + str(started.get('diagnostic', '')))
        lease = {'owner': owner, 'start_id': start_id, 'lease_secret': lease_secret,
                 'broker_generation': initial['broker_generation'],
                 'generation': started['generation']}

        status = _wait_for_status(path, lambda value: value.get('state') == 'running' and
                                  value.get('driver') == 'ready' and
                                  value.get('guardian') == 'active', process)
        if status.get('generation') != lease['generation'] or status.get('owner') != owner:
            raise RuntimeError('test_owned_task_identity_mismatch')
        record['running_driver_guardian'] = True

        driver_pid = _driver_descendant(process.pid)
        if driver_pid is None:
            until = time.monotonic() + 5
            while driver_pid is None and time.monotonic() < until:
                driver_pid = _driver_descendant(process.pid)
                time.sleep(0.05)
        if driver_pid is None:
            raise RuntimeError('test_owned_session_driver_descendant_not_found')
        driver_environment = _process_env(driver_pid)
        if driver_environment is None:
            raise RuntimeError('test_owned_session_driver_environment_unreadable')
        driver_values, token_present, token_valid, gtk_present = driver_environment
        if not token_present or not token_valid:
            # The value itself stays private; validate only that the token exists
            # and has the broker's fixed token shape without returning it.
            raise RuntimeError('test_owned_driver_token_missing')
        if gtk_present:
            raise RuntimeError('GTK_IM_MODULE_reached_session_driver')
        missing = sorted(key for key in SESSION_KEYS if not driver_values.get(key))
        if missing:
            raise RuntimeError('driver_full_key_proof_missing=' + ','.join(missing))
        mismatch = sorted(key for key in SESSION_KEYS if driver_values.get(key) != donor.get(key))
        if mismatch:
            raise RuntimeError('driver_key_comparison_failed=' + ','.join(mismatch))
        cu._validate_session_tuple(driver_values)
        if (driver_values['XDG_RUNTIME_DIR'] != donor['XDG_RUNTIME_DIR'] or
                driver_values['WAYLAND_DISPLAY'] != donor['WAYLAND_DISPLAY'] or
                driver_values['HYPRLAND_INSTANCE_SIGNATURE'] != donor['HYPRLAND_INSTANCE_SIGNATURE']):
            raise RuntimeError('driver_tuple_does_not_match_current_donor')
        record.update({'driver_key_count': len(driver_values), 'key_comparison': True,
                       'tuple_validation': True, 'gtk_im_module_absent': True,
                       'driver_token_present': True})

        request = {'command': 'request', **_lease_fields(lease), 'sequence': 1,
                   'request': {'args': ['doctor'], 'stdin': '', 'image_policy': 'always'}}
        accepted = _exchange_with_timeout(request, path, timeout=5)
        if not accepted.get('ok') or accepted.get('status') != 'accepted':
            raise RuntimeError('read_only_doctor_request_was_not_accepted')
        until = time.monotonic() + 20
        result = None
        while time.monotonic() < until:
            result = _exchange_with_timeout(
                {'command': 'result', **_lease_fields(lease), 'sequence': 1}, path, timeout=5)
            if result.get('status') == 'completed':
                break
            if result.get('status') in ('failed', 'unknown'):
                break
            time.sleep(0.1)
        response = result.get('response') if isinstance(result, dict) else None
        doctor = response.get('result') if isinstance(response, dict) else None
        if (not isinstance(response, dict) or response.get('returncode') != 0 or
                response.get('session_continues') is not True or
                not isinstance(doctor, dict) or doctor.get('session') is not True or
                not isinstance(doctor.get('monitors'), list) or not doctor['monitors']):
            raise RuntimeError('read_only_doctor_proof_failed')
        record['doctor'] = {'returncode': 0, 'session_continues': True,
                            'session': True, 'monitors_nonempty': True,
                            'monitor_count': len(doctor['monitors'])}
        return record, lease
    finally:
        if lease is not None:
            final = _finish_owned_lease(path, lease)
            record['clean_finish'] = bool(final)


def _terminate_test_broker(process, path):
    status = _status(path)
    if (status.get('state') not in ('idle', 'finished') or
            status.get('driver') not in ('idle', 'stopped') or
            status.get('guardian') not in ('idle', 'clean') or
            status.get('recovery') != 'none' or status.get('cancelled') is not False):
        raise RuntimeError('test_owned_broker_not_idle_after_owned_cleanup')
    if session_remote._read_snapshot(session_remote.SNAPSHOT) is not None:
        raise RuntimeError('retained_snapshot_before_test_broker_shutdown')
    process.send_signal(signal.SIGTERM)
    try:
        code = process.wait(timeout=15)
    except subprocess.TimeoutExpired as error:
        raise RuntimeError('test_owned_broker_did_not_exit_after_SIGTERM') from error
    if code != 0:
        raise RuntimeError('test_owned_broker_exit_code_not_zero')
    return code


def run_case(case, repeat):
    if os.environ.get('CU_SESSION_TOKEN'):
        raise ProofBlocked('inherited_CU_SESSION_TOKEN_refused')
    client_env = _client_environment()
    if session_remote.STATE.resolve() != (Path(client_env['HOME']) / '.cache' / 'agent-computer-use').resolve():
        raise ProofBlocked('normal_shared_state_root_unavailable')
    if 'XDG_CACHE_HOME' in os.environ:
        raise ProofBlocked('XDG_CACHE_HOME_would_change_shared_state_root')
    donor = find_verified_host_donor()
    _check_installed_broker(client_env)
    _check_readiness(donor)

    test_dir = _secure_test_root()
    process = None
    broker_path = test_dir / 'relay.sock'
    success = False
    evidence = {'case': case, 'repeat': repeat, 'cycles': []}
    try:
        environment = _broker_environment(case, donor)
        gui_values = {key: environment[key] for key in SESSION_KEYS if key in environment}
        inherited_count = len(gui_values)
        process, broker_path, source_proof = _start_test_broker(
            test_dir, environment, hashlib.sha256((SCRIPTS / 'cu.py').read_bytes()).hexdigest())
        broker_environment_evidence = _process_env(process.pid)
        if broker_environment_evidence is None:
            raise RuntimeError('test_owned_broker_environment_unreadable')
        broker_values, broker_token, _broker_token_valid, broker_gtk = broker_environment_evidence
        if broker_token or broker_gtk:
            raise RuntimeError('test_owned_broker_inherited_session_token_or_gtk')
        actual_count = len(broker_values)
        if actual_count != inherited_count:
            raise RuntimeError('test_owned_broker_allowlist_count_mismatch')
        inherited_count = actual_count
        if case == 'bare' and ROUTING_KEYS.intersection(broker_values):
            raise RuntimeError('bare_test_broker_inherited_gui_routing_variables')
        if case == 'stale':
            if (broker_values.get('XDG_RUNTIME_DIR') != donor['XDG_RUNTIME_DIR'] or
                    broker_values.get('WAYLAND_DISPLAY') != donor['WAYLAND_DISPLAY'] or
                    not broker_values.get('HYPRLAND_INSTANCE_SIGNATURE') or
                    broker_values['HYPRLAND_INSTANCE_SIGNATURE'] == donor['HYPRLAND_INSTANCE_SIGNATURE']):
                raise RuntimeError('stale_test_broker_hints_not_installed')
            stale_ipc = (Path(broker_values['XDG_RUNTIME_DIR']) / 'hypr' /
                         broker_values['HYPRLAND_INSTANCE_SIGNATURE'] / '.socket.sock')
            if stale_ipc.exists():
                raise RuntimeError('stale_signature_was_not_guaranteed_nonexistent')
        if source_proof['cu_sha256'] != hashlib.sha256((SCRIPTS / 'cu.py').read_bytes()).hexdigest():
            raise RuntimeError('test_owned_broker_source_hash_changed')
        evidence.update({'inherited_gui_key_count': inherited_count,
                         'broker_source_assertion': True,
                         'broker_cu_path_match': source_proof['cu_path'] == str(SCRIPTS / 'cu.py'),
                         'broker_session_remote_path_match':
                             source_proof['session_remote_path'] == str(SCRIPTS / 'session_remote.py'),
                         'broker_repo_cu_sha256': source_proof['cu_sha256'],
                         'broker_repo_cu_hash': True})

        for index in range(1, repeat + 1):
            _check_installed_broker(client_env)
            cycle, _lease = _cycle(case, index, process, broker_path,
                                   donor, inherited_count)
            if case == 'stale':
                cycle['stale_recovered_to_current_tuple'] = True
            evidence['cycles'].append(cycle)
        exit_code = _terminate_test_broker(process, broker_path)
        process = None
        evidence['test_broker_exit_code'] = exit_code
        evidence['driver_key_count'] = 18
        evidence['key_comparison'] = all(row.get('key_comparison') for row in evidence['cycles'])
        evidence['tuple_validation'] = all(row.get('tuple_validation') for row in evidence['cycles'])
        evidence['readiness_and_doctor'] = all(
            row.get('running_driver_guardian') and row.get('doctor', {}).get('returncode') == 0
            for row in evidence['cycles'])
        evidence['clean_finish'] = all(row.get('clean_finish') for row in evidence['cycles'])
        evidence['ok'] = all((evidence['broker_source_assertion'], evidence['broker_repo_cu_hash'],
                              evidence['key_comparison'], evidence['tuple_validation'],
                              evidence['readiness_and_doctor'], evidence['clean_finish'],
                              exit_code == 0))
        if not evidence['ok']:
            raise RuntimeError('one_or_more_envsteal_proofs_failed')
        success = True
        return evidence
    finally:
        if process is not None:
            try:
                status = _status(broker_path)
            except Exception:
                status = {}
            if (status.get('state') in ('idle', 'finished') and
                    status.get('recovery') == 'none' and
                    not session_remote._lexists(session_remote.SNAPSHOT)):
                try:
                    _terminate_test_broker(process, broker_path)
                except Exception:
                    pass
        if success:
            shutil.rmtree(test_dir)
        else:
            print(json.dumps({'case': case, 'blocked_or_failed': True,
                              'evidence_directory': str(test_dir)}, separators=(',', ':')),
                  file=sys.stderr, flush=True)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', choices=('bare', 'stale'), required=True)
    parser.add_argument('--repeat', type=int, default=2)
    args = parser.parse_args(argv)
    if args.repeat < 1 or args.repeat > 4:
        parser.error('--repeat must be between 1 and 4')
    try:
        proof = run_case(args.case, args.repeat)
    except ProofBlocked as error:
        print(json.dumps({'case': args.case, 'repeat': args.repeat,
                          'blocked': str(error)}, separators=(',', ':')))
        return 2
    except Exception as error:
        print(json.dumps({'case': args.case, 'repeat': args.repeat,
                          'ok': False, 'error': str(error)}, separators=(',', ':')))
        return 1
    print(json.dumps(proof, separators=(',', ':')))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
