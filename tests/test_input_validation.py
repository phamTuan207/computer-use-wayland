"""Offline validation, process, and browser-profile regressions. No GUI, no live fixture."""
import importlib.util
import io
import json
from pathlib import Path
import subprocess
import sys
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
_spec = importlib.util.spec_from_file_location('cu', ROOT / 'scripts/cu.py')
cu = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(cu)


class RunCancelableBaseException(unittest.TestCase):
    """KeyboardInterrupt/SystemExit must still reap the owned child, then re-raise."""

    class _Child:
        def __init__(self, interrupted=True):
            self.terminated = self.killed = self.reaped = False
            self.pid = 4242
            self._interrupted = interrupted

        def poll(self):
            return None

        def terminate(self):
            self.terminated = True

        def kill(self):
            self.killed = True

        def communicate(self, input=None, timeout=None):
            if self._interrupted and not self.terminated:
                raise KeyboardInterrupt('during communicate')
            self.reaped = True
            return ('', '')

    def _drive(self, error):
        child = self._Child()

        def communicate(input=None, timeout=None):
            if not child.terminated:
                raise error          # cancelled while the child is still running
            child.reaped = True
            return ('', '')
        child.communicate = communicate
        with mock.patch.object(cu.subprocess, 'Popen', return_value=child):
            with self.assertRaises(type(error)):
                cu.run_cancelable(['node', 'adapter.mjs'], input='{}')
        return child

    def test_keyboard_interrupt_terminates_reaps_and_propagates(self):
        for error in (KeyboardInterrupt(), SystemExit(1)):
            with self.subTest(error=type(error).__name__):
                child = self._drive(error)
                self.assertTrue(child.terminated, 'child was not terminated')
                self.assertTrue(child.reaped, 'child was not reaped')

    def test_cleanup_failure_still_escalates_to_kill(self):
        child = self._Child()
        child.terminate = mock.Mock(side_effect=OSError('terminate failed'))
        with mock.patch.object(cu.subprocess, 'Popen', return_value=child):
            with self.assertRaises(KeyboardInterrupt):
                cu.run_cancelable(['node', 'adapter.mjs'], input='{}')
        self.assertTrue(child.killed, 'kill escalation was skipped')


class RealChildCleanup(unittest.TestCase):
    def test_interrupt_reaps_the_owned_sleep_subprocess(self):
        original=cu.subprocess.Popen;children=[]
        def spawn(*args,**kwargs):
            child=original(*args,**kwargs);children.append(child);return child
        try:
            with mock.patch.object(cu.subprocess,'Popen',side_effect=spawn), \
                 mock.patch.object(cu,'check_cancel',side_effect=[None,KeyboardInterrupt('owned child')]):
                with self.assertRaisesRegex(KeyboardInterrupt,'owned child'):
                    cu.run_cancelable([sys.executable,'-c','import time; time.sleep(30)'])
            self.assertIsNotNone(children[0].poll())
            self.assertIsNotNone(children[0].returncode)
        finally:
            for child in children:
                if child.poll() is None:child.kill();child.wait(timeout=2)


class JsonReadLimit(unittest.TestCase):
    """Untrusted JSON is capped at 8 MiB before the whole input is buffered."""

    def test_exact_limit_is_accepted_and_one_byte_over_is_refused(self):
        head, tail = '{"k":"', '"}'
        body = cu.JSON_LIMIT - len(head) - len(tail)
        at_limit = head + 'x' * body + tail
        self.assertEqual(len(at_limit), cu.JSON_LIMIT)
        self.assertEqual(cu.read_json(io.StringIO(at_limit)), {'k': 'x' * body})
        with self.assertRaisesRegex(ValueError, 'exceeds 8 MiB'):
            cu.read_json(io.StringIO(at_limit + 'y'))

    def test_binary_stream_and_non_ascii_are_counted_in_bytes(self):
        with self.assertRaisesRegex(ValueError, 'exceeds 8 MiB'):
            cu.read_json(io.BytesIO(b'{"k":"' + 'é'.encode() * (5 * 1024 * 1024) + b'"}'))

    def test_a_file_is_not_fully_read_to_detect_an_oversized_payload(self):
        class Counting(io.StringIO):
            def __init__(self, data):
                super().__init__(data)
                self.served = 0

            def read(self, size=-1):
                self.served += len(self.getvalue()) if size < 0 else size
                return super().read(size)

        import tempfile
        big = 'x' * (9 * 1024 * 1024)
        with tempfile.NamedTemporaryFile('w', suffix='.json', delete=False) as handle:
            handle.write(big)
            path = Path(handle.name)
        try:
            counter = Counting(big)
            with mock.patch.object(cu, 'open', return_value=counter, create=True):
                with self.assertRaisesRegex(ValueError, 'exceeds 8 MiB'):
                    cu.read_json_file(path)
            self.assertLess(counter.served, len(big), 'the whole file was buffered first')
        finally:
            path.unlink()

    def test_text_unicode_is_limited_before_the_whole_stream_is_read(self):
        class Counting(io.StringIO):
            served=0
            def read(self,size=-1):
                chunk=super().read(size);self.served+=len(chunk.encode('utf-8'));return chunk
        for character in ('é','🙂'):
            payload='{"k":"'+character*(5*1024*1024)+'"}'
            stream=Counting(payload)
            with self.assertRaisesRegex(ValueError,'exceeds 8 MiB'):cu.read_json(stream)
            self.assertLess(stream.served,len(payload.encode('utf-8')))
        wrapper=io.TextIOWrapper(io.BytesIO(b'{"k":"'+b'\xc3\xa9'*(5*1024*1024)+b'"}'),encoding='utf-8')
        with self.assertRaisesRegex(ValueError,'exceeds 8 MiB'):cu.read_json(wrapper)

    def test_empty_input_is_refused(self):
        with self.assertRaisesRegex(ValueError, 'empty JSON input'):
            cu.read_json(io.StringIO(''))


class SessionDriverLimit(unittest.TestCase):
    def test_an_over_long_request_line_is_refused_before_json_parse(self):
        import session_driver
        stream = io.StringIO('{"args":["act"]}\n')
        self.assertEqual([line for line in session_driver.request_lines(stream)],
                         ['{"args":["act"]}\n'])
        with self.assertRaisesRegex(ValueError, 'exceeds 8 MiB'):
            list(session_driver.request_lines(io.StringIO('{' + 'x' * (8 * 1024 * 1024) + '\n')))


    def test_unicode_driver_stops_before_execute_and_preserves_partial_final_line(self):
        import session_driver
        payload=json.dumps({'args':['status'],'padding':'é'*(5*1024*1024)},ensure_ascii=False)+'\n'
        class Counting(io.StringIO):
            served=0
            def readline(self,size=-1):
                chunk=super().readline(size);self.served+=len(chunk.encode('utf-8'));return chunk
        stream=Counting(payload)
        with mock.patch.object(session_driver,'execute') as execute:
            with self.assertRaisesRegex(ValueError,'exceeds 8 MiB'):
                session_driver.relay_commands(stream,io.StringIO())
            execute.assert_not_called()
        self.assertLess(stream.served,len(payload.encode('utf-8')))
        for stream in (io.StringIO('é\n🙂'),io.BytesIO('é\n🙂'.encode())):
            self.assertEqual(list(session_driver.request_lines(stream)),['é\n','🙂'])


class BrowserStartLifecycle(unittest.TestCase):
    """Only a process this call started is terminated; the log is private at creation."""

    def test_existing_log_is_private_before_spawn_and_closed_on_spawn_error(self):
        import os
        import tempfile
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);state=root/'state';state.mkdir()
            log=state/'browser.log';log.touch();log.chmod(0o644)
            handles=[]
            def spawn(*args,**kwargs):
                handles.append(kwargs['stdout'])
                self.assertEqual(os.fstat(handles[-1].fileno()).st_mode & 0o777,0o600)
                raise OSError('spawn failed')
            with mock.patch.object(cu,'ROOT',root),mock.patch.object(cu,'STATE',state), \
                 mock.patch('urllib.request.urlopen',side_effect=OSError('offline')), \
                 mock.patch.object(cu.subprocess,'Popen',side_effect=spawn):
                with self.assertRaisesRegex(OSError,'spawn failed'):cu.browser_start({},'http://localhost:9222')
            self.assertTrue(handles[0].closed)

    def test_cancel_reaps_owned_process_and_reuse_starts_nothing(self):
        import tempfile
        child=mock.Mock()
        child.wait.side_effect=[subprocess.TimeoutExpired('chromium',3),0]
        with tempfile.TemporaryDirectory() as temp, \
             mock.patch.object(cu,'ROOT',Path(temp)),mock.patch.object(cu,'STATE',Path(temp)/'state'), \
             mock.patch('urllib.request.urlopen',side_effect=OSError('offline')), \
             mock.patch.object(cu.subprocess,'Popen',return_value=child), \
             mock.patch.object(cu,'check_cancel',side_effect=KeyboardInterrupt('cancel')):
            with self.assertRaises(KeyboardInterrupt):cu.browser_start({},'http://localhost:9222')
        child.terminate.assert_called_once();child.kill.assert_called_once()
        self.assertEqual(child.wait.call_count,2)
        with mock.patch('urllib.request.urlopen',return_value=io.StringIO('{}')), \
             mock.patch.object(cu.subprocess,'Popen') as spawn:
            self.assertTrue(cu.browser_start({},'http://localhost:9222')['reused'])
            spawn.assert_not_called()

    def test_existing_profile_dir_is_brought_to_0700_before_spawn(self):
        import os
        import stat
        import tempfile
        for mode in (0o755, 0o777):
            with self.subTest(mode=oct(mode)):
                with tempfile.TemporaryDirectory() as temp:
                    root = Path(temp)
                    profile = root/'browser-profile'
                    profile.mkdir(mode=mode)
                    seen = {}

                    def spawn(*args, **kwargs):
                        seen['mode'] = stat.S_IMODE(os.stat(profile).st_mode)
                        child = mock.Mock()
                        child.pid = 4242
                        return child

                    with mock.patch.object(cu, 'ROOT', root), \
                         mock.patch.object(cu, 'STATE', root/'state'), \
                         mock.patch('urllib.request.urlopen',
                                    side_effect=[OSError('offline'), io.StringIO('{}')]), \
                         mock.patch.object(cu.subprocess, 'Popen', side_effect=spawn):
                        cu.browser_start({}, 'http://localhost:9222')
                    self.assertEqual(seen['mode'], 0o700,
                                     'the directory itself is 0700 before Chromium starts')
                    self.assertEqual(stat.S_IMODE(os.stat(profile).st_mode), 0o700)

    def test_new_profile_dir_is_created_0700(self):
        import os
        import stat
        import tempfile
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            child = mock.Mock()
            child.pid = 4242
            with mock.patch.object(cu, 'ROOT', root), \
                 mock.patch.object(cu, 'STATE', root/'state'), \
                 mock.patch('urllib.request.urlopen',
                            side_effect=[OSError('offline'), io.StringIO('{}')]), \
                 mock.patch.object(cu.subprocess, 'Popen', return_value=child):
                cu.browser_start({}, 'http://localhost:9222')
            self.assertEqual(stat.S_IMODE(os.stat(root/'browser-profile').st_mode), 0o700)

    def test_bad_profile_inode_never_spawns(self):
        import os
        import tempfile
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            target = root/'elsewhere'
            target.mkdir()
            profile = root/'browser-profile'
            # Symlink refuses with a fixed helpful error, never raw ELOOP/ENOTDIR.
            if profile.is_symlink() or profile.is_file():
                profile.unlink()
            elif profile.is_dir():
                profile.rmdir()
            profile.symlink_to(target, target_is_directory=True)
            with mock.patch.object(cu, 'ROOT', root), \
                 mock.patch.object(cu, 'STATE', root/'state'), \
                 mock.patch('urllib.request.urlopen', side_effect=OSError('offline')), \
                 mock.patch.object(cu.subprocess, 'Popen') as spawn:
                with self.assertRaisesRegex(RuntimeError, 'must not be a symlink'):
                    cu.browser_start({}, 'http://localhost:9222')
            spawn.assert_not_called()
            self.assertTrue(target.is_dir(), 'no arbitrary target was touched')
            # An ordinary file still refuses without spawning.
            profile.unlink()
            profile.write_text('x')
            with mock.patch.object(cu, 'ROOT', root), \
                 mock.patch.object(cu, 'STATE', root/'state'), \
                 mock.patch('urllib.request.urlopen', side_effect=OSError('offline')), \
                 mock.patch.object(cu.subprocess, 'Popen') as spawn:
                with self.assertRaises(OSError):
                    cu.browser_start({}, 'http://localhost:9222')
            spawn.assert_not_called()
            self.assertTrue(target.is_dir(), 'no arbitrary target was touched')

    def test_foreign_owned_profile_never_spawns(self):
        import tempfile
        foreign = mock.Mock()
        foreign.st_uid = 424242
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root/'browser-profile').mkdir()
            with mock.patch.object(cu, 'ROOT', root), \
                 mock.patch.object(cu, 'STATE', root/'state'), \
                 mock.patch('urllib.request.urlopen', side_effect=OSError('offline')), \
                 mock.patch.object(cu.os, 'fstat', return_value=foreign), \
                 mock.patch.object(cu.subprocess, 'Popen') as spawn:
                with self.assertRaisesRegex(RuntimeError, 'not owned'):
                    cu.browser_start({}, 'http://localhost:9222')
            spawn.assert_not_called()

    def test_profile_open_or_chmod_failure_never_spawns(self):
        import os
        import tempfile
        for point, error in (('open', OSError('open down')), ('chmod', OSError('chmod down'))):
            with self.subTest(point=point):
                with tempfile.TemporaryDirectory() as temp:
                    root = Path(temp)
                    (root/'browser-profile').mkdir()
                    before = set(os.listdir('/proc/self/fd'))
                    if point == 'open':
                        patcher = mock.patch.object(cu.os, 'open', side_effect=error)
                    else:
                        patcher = mock.patch.object(cu.os, 'fchmod', side_effect=error)
                    with mock.patch.object(cu, 'ROOT', root), \
                         mock.patch.object(cu, 'STATE', root/'state'), \
                         mock.patch('urllib.request.urlopen', side_effect=OSError('offline')), \
                         patcher, \
                         mock.patch.object(cu.subprocess, 'Popen') as spawn:
                        with self.assertRaises(OSError):
                            cu.browser_start({}, 'http://localhost:9222')
                    spawn.assert_not_called()
                    self.assertEqual(set(os.listdir('/proc/self/fd')) - before, set(),
                                     'no file descriptor leaked')

    def test_reused_endpoint_never_touches_the_profile(self):
        import tempfile
        opened = []

        def spy_open(path, *args, **kwargs):
            opened.append(str(path))
            raise AssertionError('profile must not be touched on reuse')

        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            with mock.patch.object(cu, 'ROOT', root), \
                 mock.patch.object(cu, 'STATE', root/'state'), \
                 mock.patch('urllib.request.urlopen', return_value=io.StringIO('{}')), \
                 mock.patch.object(cu.os, 'open', side_effect=spy_open), \
                 mock.patch.object(cu.subprocess, 'Popen') as spawn:
                self.assertTrue(cu.browser_start({}, 'http://localhost:9222')['reused'])
            spawn.assert_not_called()
            self.assertEqual(opened, [])
            self.assertFalse((root/'browser-profile').exists())

    def test_bad_port_is_refused_with_a_clear_error(self):
        for endpoint in ('http://localhost:notaport', 'http://127.0.0.1:99999'):
            with self.subTest(endpoint=endpoint):
                with self.assertRaises(ValueError):
                    cu.browser_start({}, endpoint)


class BrowserCliEnvelope(unittest.TestCase):
    def test_capture_failure_preserves_structured_action_result_and_stops_session(self):
        import contextlib
        envelope={'ok':False,'completed':1,'execution_ms':12,'error':'mutation failed',
                  'capture_error':'screenshot failed','mutation_may_have_occurred':True}
        with mock.patch.object(cu,'require_session'),mock.patch.object(cu,'check_cancel'), \
             mock.patch.object(cu,'locked',return_value=contextlib.nullcontext()), \
             mock.patch.object(cu,'stop_session_on_error') as stop, \
             mock.patch.object(cu,'run_cancelable',return_value=json.dumps(envelope)) as adapter, \
             mock.patch.object(sys,'argv',['cu','browser','act','--snapshot','s','--target','t','--actions','-','--image']), \
             mock.patch.object(sys,'stdin',io.StringIO('[{"type":"wait","ms":0}]')), \
             contextlib.redirect_stdout(io.StringIO()) as output:
            self.assertEqual(cu.main(),1)
        self.assertEqual(json.loads(output.getvalue()),envelope)
        adapter.assert_called_once();stop.assert_called_once()


if __name__ == '__main__':
    unittest.main()
