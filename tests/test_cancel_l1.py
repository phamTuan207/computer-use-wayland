"""L1: self-describing cancellation latch — GUI-free unit tests.

Every GUI-reaching command (hyprctl eval/devices, cursor guard, indicator,
request_stop) is mocked; only real file operations under a temp state folder
are exercised. The legacy 'cancelled by user' message prefix and the latch
path (STATE/'cancelled') must stay unchanged; all new behaviour is additive.
"""
import errno
import io
import json
import os
from pathlib import Path
import shlex
import stat
import subprocess
import sys
import tempfile
import threading
import time
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import cancel_hotkey
import cu
import cursor_session as session


class CancelLatchL1(unittest.TestCase):
    def setUp(self):
        tmp=tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.folder=Path(tmp.name)
        self.state=self.folder/'cache'/'agent-computer-use'
        self.state.mkdir(parents=True)
        self.latch=self.state/'cancelled'

    def read_latch(self):
        return json.loads(self.latch.read_text())


def unescape_lua_string(code):
    """Extract the command passed to hl.dsp.exec_cmd from a generated Lua binding."""
    start=code.index('exec_cmd("')+len('exec_cmd("')
    parts=[]
    i=start
    while i<len(code):
        ch=code[i]
        if ch=='\\':
            nxt=code[i+1]
            if nxt=='"':parts.append(34);i+=2
            elif nxt=='\\':parts.append(92);i+=2
            else:parts.append(int(code[i+1:i+4]));i+=4
        elif ch=='"':break
        else:
            parts.extend(ch.encode('utf-8'));i+=1
    return bytes(parts).decode('utf-8')


class TestLatchMetadata(CancelLatchL1):
    def test_absent_latch_reports_not_cancelled_without_metadata(self):
        status=cancel_hotkey.cancellation_status(self.latch)
        self.assertEqual(status,{'cancelled':False})
        self.assertNotIn('cancellation',status)
        self.assertFalse(cancel_hotkey.latch_present(self.latch))

    def test_latch_present_fails_closed_on_unreadable_state(self):
        self.assertFalse(cancel_hotkey.latch_present(self.latch))          # missing only
        for error in (PermissionError(13,'denied'),OSError(5,'i/o error')):
            with self.subTest(error=type(error).__name__):
                with patch.object(cancel_hotkey.os,'lstat',side_effect=error):
                    self.assertTrue(cancel_hotkey.latch_present(self.latch))  # fail closed
        with patch.object(cancel_hotkey.os,'lstat',side_effect=FileNotFoundError(2,'missing')):
            self.assertFalse(cancel_hotkey.latch_present(self.latch))

    def test_dangling_symlink_latch_is_present_and_cancelled(self):
        os.symlink(self.folder/'gone-target',self.latch)
        self.assertTrue(cancel_hotkey.latch_present(self.latch))  # no-follow presence
        status=cancel_hotkey.cancellation_status(self.latch)
        self.assertTrue(status['cancelled'])              # entry exists: fail-closed
        detail=status['cancellation']
        self.assertEqual(detail['source'],'legacy latch; origin unknown')
        self.assertEqual(detail['clear_with'],'computer-use resume')
        self.assertIn('continue',detail['instruction'])
        self.assertIsNotNone(detail['set_at'])            # link mtime fallback
        message=cancel_hotkey.cancellation_message(self.latch)
        self.assertTrue(message.startswith('cancelled by user'))
        self.assertIn('computer-use resume',message)

    def test_active_latch_records_timestamp_pid_source_and_guidance(self):
        before=time.time()
        cancel_hotkey.latch(path=self.latch,source='cli')
        after=time.time()
        raw=self.read_latch()
        self.assertIsInstance(raw['set_at'],float)
        self.assertGreaterEqual(raw['set_at'],before-1)
        self.assertLessEqual(raw['set_at'],after+1)
        self.assertEqual(raw['pid'],os.getpid())
        self.assertEqual(raw['source'],'cli')
        status=cancel_hotkey.cancellation_status(self.latch)
        self.assertTrue(status['cancelled'])
        detail=status['cancellation']
        self.assertAlmostEqual(detail['set_at'],raw['set_at'],places=6)
        self.assertEqual(detail['pid'],os.getpid())
        self.assertEqual(detail['source'],'cli')
        self.assertEqual(detail['clear_with'],'computer-use resume')
        self.assertIn('continue',detail['instruction'])
        self.assertTrue(self.latch.exists())  # reporting never auto-resumes

    def test_session_token_captured_and_malformed_session_json_tolerated(self):
        (self.state/'session.json').write_text(json.dumps({'token':'a'*32}))
        cancel_hotkey.latch(path=self.latch,source='physical-escape')
        self.assertEqual(self.read_latch()['session_token'],'a'*32)
        for broken in ('not json','[]','{"token":4}'):
            with self.subTest(broken=broken):
                (self.state/'session.json').write_text(broken)
                cancel_hotkey.latch(path=self.latch,source='physical-escape')
                self.assertIsNone(self.read_latch()['session_token'])

    def test_latch_mode_is_exactly_0600_regardless_of_umask(self):
        cancel_hotkey.latch(path=self.latch,source='cli')
        self.assertEqual(self.latch.stat().st_mode & 0o777,0o600)
        fresh=self.state/'cancelled-fresh'
        old=os.umask(0o777)
        try:
            cancel_hotkey.latch(path=fresh,source='cli')  # creation under hostile umask
        finally:
            os.umask(old)
        self.assertEqual(fresh.stat().st_mode & 0o777,0o600)

    def test_legacy_text_latch_uses_mtime_and_unknown_source(self):
        stamp=time.time()-3600
        self.latch.write_text('cancelled by user\n')
        os.utime(self.latch,(stamp,stamp))
        status=cancel_hotkey.cancellation_status(self.latch)
        self.assertTrue(status['cancelled'])
        detail=status['cancellation']
        self.assertEqual(detail['source'],'legacy latch; origin unknown')
        self.assertAlmostEqual(detail['set_at'],stamp,places=3)
        self.assertEqual(detail['clear_with'],'computer-use resume')
        self.assertIn('continue',detail['instruction'])
        self.assertTrue(self.latch.exists())  # still latched, never auto-resumed

    def test_malformed_and_unreadable_metadata_still_cancelled_with_guidance(self):
        payloads=('{broken','{"set_at": 12.5, "source": "cl','{"set_at": 12.5,','[1,2]','"text"',
                  json.dumps({'set_at':'nope','source':42}),json.dumps({'set_at':True,'source':''}))
        for payload in payloads:
            with self.subTest(payload=payload):
                self.latch.write_text(payload)
                status=cancel_hotkey.cancellation_status(self.latch)
                self.assertTrue(status['cancelled'])
                detail=status['cancellation']
                self.assertEqual(detail['source'],'legacy latch; origin unknown')
                self.assertEqual(detail['clear_with'],'computer-use resume')
                self.assertIn('continue',detail['instruction'])
                message=cancel_hotkey.cancellation_message(self.latch)
                self.assertTrue(message.startswith('cancelled by user'))
                self.assertIn('computer-use resume',message)
        self.latch.write_text(json.dumps({'set_at':1.0,'source':'cli'}))
        with patch.object(cancel_hotkey.os,'open',side_effect=OSError(13,'permission denied')):
            status=cancel_hotkey.cancellation_status(self.latch)
        self.assertTrue(status['cancelled'])
        self.assertEqual(status['cancellation']['clear_with'],'computer-use resume')

    def test_non_finite_timestamps_fall_back_to_mtime_and_strict_json(self):
        stamp=time.time()-120
        for literal in ('NaN','Infinity','-Infinity','1e999',str(10**400)):
            with self.subTest(literal=literal):
                self.latch.write_text('{"set_at": '+literal+', "source": "cli"}')
                os.utime(self.latch,(stamp,stamp))
                status=cancel_hotkey.cancellation_status(self.latch)
                self.assertTrue(status['cancelled'])
                self.assertAlmostEqual(status['cancellation']['set_at'],stamp,places=3)
                self.assertEqual(status['cancellation']['source'],'cli')
                encoded=json.dumps(status,allow_nan=False)  # strict JSON must hold
                self.assertIn('clear_with',encoded)


class TestCancellationMessage(CancelLatchL1):
    def test_message_keeps_prefix_and_appends_timestamp_source_guidance(self):
        cancel_hotkey.latch(path=self.latch,source='physical-escape')
        message=cancel_hotkey.cancellation_message(self.latch)
        self.assertTrue(message.startswith('cancelled by user'))
        self.assertIn('stop this task',message)
        self.assertIn('computer-use resume',message)
        self.assertIn('source=physical-escape',message)
        self.assertIn(f"set_at={self.read_latch()['set_at']}",message)

    def test_legacy_latch_message_keeps_prefix_and_explains(self):
        self.latch.write_text('cancelled by user\n')
        message=cancel_hotkey.cancellation_message(self.latch)
        self.assertTrue(message.startswith('cancelled by user'))
        self.assertIn('computer-use resume',message)
        self.assertIn('legacy latch',message)

    def test_cu_check_cancel_keeps_prefix_and_reports_metadata(self):
        with patch.dict(os.environ,{'CU_SESSION_TOKEN':''}), \
                patch.object(cu,'STATE',self.state),patch.object(cu,'CANCEL',self.latch):
            self.latch.write_text('cancelled by user\n')
            with self.assertRaisesRegex(RuntimeError,'^cancelled by user'):
                cu.check_cancel()
            cancel_hotkey.latch(path=self.latch,source='cli')
            with self.assertRaisesRegex(RuntimeError,'^cancelled by user') as caught:
                cu.check_cancel()
        self.assertIn('source=cli',str(caught.exception))
        self.assertIn('computer-use resume',str(caught.exception))

    def test_cu_check_cancel_treats_dangling_symlink_as_cancelled(self):
        os.symlink(self.folder/'gone-target',self.latch)
        with patch.dict(os.environ,{'CU_SESSION_TOKEN':''}), \
                patch.object(cu,'STATE',self.state),patch.object(cu,'CANCEL',self.latch):
            with self.assertRaisesRegex(RuntimeError,'^cancelled by user'):
                cu.check_cancel()


class TestFdOwnershipAndPaths(CancelLatchL1):
    def test_latch_refuses_symlink_and_leaves_target_unchanged(self):
        target=self.folder/'victim'
        target.write_text('keep')
        self.latch.symlink_to(target)
        with self.assertRaises(OSError):
            cancel_hotkey.latch(path=self.latch,source='cli')
        self.assertEqual(target.read_text(),'keep')       # symlink target untouched
        self.assertTrue(self.latch.is_symlink())          # latch path itself unchanged

    def test_fifo_latch_reports_cancelled_without_blocking(self):
        os.mkfifo(self.latch,0o600)
        status=cancel_hotkey.cancellation_status(self.latch)
        self.assertTrue(status['cancelled'])              # no hang: O_NONBLOCK + fstat guard
        detail=status['cancellation']
        self.assertEqual(detail['source'],'legacy latch; origin unknown')
        self.assertEqual(detail['clear_with'],'computer-use resume')
        self.assertIn('continue',detail['instruction'])
        self.assertIsNotNone(detail['set_at'])

    def test_latch_write_refuses_fifo_without_blocking(self):
        os.mkfifo(self.latch,0o600)
        with self.assertRaises(OSError):                  # ENXIO: no reader, never blocks
            cancel_hotkey.latch(path=self.latch,source='cli')
        self.assertTrue(self.latch.is_fifo())             # target left untouched

    def test_fstat_rejection_happens_before_any_mutation(self):
        self.latch.write_text('previous latch')  # owned regular fixture with old content
        class FakeEntry:
            st_mode=stat.S_IFIFO                 # pretend the opened fd is a FIFO
        with patch.object(cancel_hotkey.os,'fstat',return_value=FakeEntry) as fstat_mock, \
                patch.object(cancel_hotkey.os,'fchmod') as fchmod_mock, \
                patch.object(cancel_hotkey.os,'ftruncate') as ftruncate_mock, \
                patch.object(cancel_hotkey.os,'fdopen') as fdopen_mock:
            with self.assertRaises(OSError) as caught:
                cancel_hotkey.latch(path=self.latch,source='cli')
        self.assertEqual(caught.exception.errno,errno.ENOTSUP)
        self.assertIn('not a regular file',str(caught.exception))
        fstat_mock.assert_called_once()          # decision made at the fstat branch
        fchmod_mock.assert_not_called()          # no mode mutation
        ftruncate_mock.assert_not_called()       # no truncation
        fdopen_mock.assert_not_called()          # no stream, no write
        self.assertEqual(self.latch.read_text(),'previous latch')  # content untouched

    def test_latch_write_refuses_fifo_with_reader_before_mutation(self):
        os.mkfifo(self.latch,0o600)
        chunks=[]
        def reader():
            with open(self.latch,'rb') as stream:  # parks in open() until a writer pairs
                chunks.append(stream.read())
        thread=threading.Thread(target=reader,daemon=True)
        thread.start()
        try:
            for _ in range(100):                   # wait until the reader is parked
                try:
                    cancel_hotkey.latch(path=self.latch,source='cli')
                    self.fail('latch onto a FIFO must be refused')
                except OSError as exc:
                    if exc.errno==errno.ENXIO:     # reader not parked yet: retry
                        time.sleep(.02)
                        continue
                    self.assertEqual(exc.errno,errno.ENOTSUP)  # refused at fstat, not open
                    break
            else:
                self.fail('writer never got past open() within the retry budget')
        finally:
            thread.join(timeout=5)
        self.assertEqual(chunks,[b''])             # zero bytes written into the FIFO
        self.assertTrue(self.latch.is_fifo())      # target untouched

    def test_fifo_session_json_is_ignored_without_blocking(self):
        os.mkfifo(self.state/'session.json',0o600)
        cancel_hotkey.latch(path=self.latch,source='cli')  # must not block on the FIFO
        self.assertEqual(self.read_latch()['source'],'cli')
        self.assertIsNone(self.read_latch()['session_token'])

    def test_fd_handed_to_stream_exactly_once(self):
        real_fdopen,real_close=os.fdopen,os.close
        opened,closed=[],[]
        def spy_fdopen(fd,*a,**k):
            opened.append(fd)
            return real_fdopen(fd,*a,**k)
        def spy_close(fd):
            closed.append(fd)
            return real_close(fd)
        with patch.object(cancel_hotkey.os,'fdopen',side_effect=spy_fdopen), \
                patch.object(cancel_hotkey.os,'close',side_effect=spy_close):
            cancel_hotkey.latch(path=self.latch,source='cli')
        self.assertEqual(len(opened),1)
        self.assertEqual(closed,[])  # success path: the stream alone owns the fd
        with patch.object(cancel_hotkey.os,'fdopen',side_effect=OSError(9,'bad descriptor')), \
                patch.object(cancel_hotkey.os,'close',side_effect=spy_close) as close_mock:
            with self.assertRaises(OSError):
                cancel_hotkey.latch(path=self.latch,source='cli')
        close_mock.assert_called_once()  # failure path closes the bare fd once
        self.assertTrue(self.latch.exists())  # stream wrote the latch before closing

    def test_latch_path_and_hotkey_command_unchanged(self):
        self.assertEqual(cancel_hotkey.CANCEL,cancel_hotkey.STATE/'cancelled')
        self.assertEqual(cancel_hotkey.HOTKEY,'agentComputerUseEscapeBind')
        def fake_run(argv,**kwargs):
            if '-j' in argv:
                return subprocess.CompletedProcess([],0,json.dumps({'keyboards':[{'name':'test-keyboard'}]}),'')
            return subprocess.CompletedProcess([],0,'ok','')
        code={}
        def fake_eval(eval_code):
            code['value']=eval_code
            return subprocess.CompletedProcess([],0,'ok','')
        with patch.object(cancel_hotkey.subprocess,'run',side_effect=fake_run), \
                patch.object(cancel_hotkey,'hypr_eval',side_effect=fake_eval), \
                patch.object(cancel_hotkey,'STATE',self.state):
            cancel_hotkey.hotkey_on()
        # Verify the invocation actually generated, not a mirrored default.
        command=unescape_lua_string(code['value'])
        argv=shlex.split(command)
        self.assertEqual(argv,['env','XDG_CACHE_HOME='+str(self.state.parent),sys.executable,
                               str(Path(cancel_hotkey.__file__).resolve()),'cancel',
                               '--source','physical-escape'])


class TestSourceAttribution(CancelLatchL1):
    def test_two_invocations_produce_different_sources(self):
        cancel_hotkey.latch(path=self.latch,source='physical-escape')
        hotkey_source=cancel_hotkey.cancellation_status(self.latch)['cancellation']['source']
        cancel_hotkey.latch(path=self.latch,source='cli')
        cli_source=cancel_hotkey.cancellation_status(self.latch)['cancellation']['source']
        self.assertEqual(hotkey_source,'physical-escape')
        self.assertEqual(cli_source,'cli')
        self.assertNotEqual(hotkey_source,cli_source)

    def test_cancel_command_defaults_to_cli_and_honours_source_flag(self):
        for argv,expected in ((['cancel'],'cli'),(['cancel','--source','physical-escape'],'physical-escape'),
                              (['cancel','--source','cli'],'cli')):
            with self.subTest(argv=argv):
                self.latch.unlink(missing_ok=True)
                with patch.object(cancel_hotkey,'STATE',self.state), \
                        patch.object(cancel_hotkey,'CANCEL',self.latch), \
                        patch.object(session,'request_stop') as stop, \
                        patch.object(sys,'argv',['cancel_hotkey.py',*argv]):
                    self.assertEqual(cancel_hotkey.main(),0)
                stop.assert_called_once()  # guardian stop responsibility unchanged
                self.assertEqual(self.read_latch()['source'],expected)

    def test_cu_cancel_command_latches_cli_source(self):
        with patch.object(cu,'STATE',self.state),patch.object(cu,'CANCEL',self.latch), \
                patch.object(session,'request_stop') as stop, \
                patch.object(sys,'argv',['cu.py','cancel']):
            self.assertEqual(cu.main(),0)
        stop.assert_called_once()
        self.assertEqual(self.read_latch()['source'],'cli')
        status=cancel_hotkey.cancellation_status(self.latch)
        self.assertTrue(status['cancelled'])
        self.assertEqual(status['cancellation']['clear_with'],'computer-use resume')


class TestPublicCliShape(CancelLatchL1):
    def test_status_keeps_legacy_shape_and_adds_metadata_only_when_cancelled(self):
        buffer=io.StringIO()
        with patch.object(cu,'CANCEL',self.latch), \
                patch.object(sys,'argv',['cu.py','status']),patch.object(sys,'stdout',buffer):
            self.assertEqual(cu.main(),0)
        self.assertEqual(json.loads(buffer.getvalue()),{'ok':True,'cancelled':False})
        cancel_hotkey.latch(path=self.latch,source='cli')
        buffer=io.StringIO()
        with patch.object(cu,'CANCEL',self.latch), \
                patch.object(sys,'argv',['cu.py','status']),patch.object(sys,'stdout',buffer):
            self.assertEqual(cu.main(),0)
        result=json.loads(buffer.getvalue())
        self.assertTrue(result['ok'])                       # existing field
        self.assertTrue(result['cancelled'])                # existing field
        self.assertEqual(result['cancellation']['source'],'cli')          # additive
        self.assertEqual(result['cancellation']['clear_with'],'computer-use resume')

    def test_missing_metadata_does_not_suppress_guidance(self):
        self.latch.write_text('legacy')
        status=cancel_hotkey.cancellation_status(self.latch)
        self.assertTrue(status['cancelled'])
        self.assertEqual(status['cancellation']['clear_with'],'computer-use resume')
        self.assertTrue(status['cancellation']['instruction'])
        self.assertIn('computer-use resume',cancel_hotkey.cancellation_message(self.latch))

    def test_status_output_is_strict_json_even_with_poisoned_metadata(self):
        self.latch.write_text('{"set_at": NaN, "pid": Infinity, "source": "cli"}')
        buffer=io.StringIO()
        with patch.object(cu,'CANCEL',self.latch), \
                patch.object(sys,'argv',['cu.py','status']),patch.object(sys,'stdout',buffer):
            self.assertEqual(cu.main(),0)
        output=buffer.getvalue()
        result=json.loads(output)
        json.dumps(result,allow_nan=False)  # strict: no NaN/Infinity anywhere
        self.assertNotIn('NaN',output)
        self.assertNotIn('Infinity',output)
        self.assertTrue(result['cancelled'])
        self.assertEqual(result['cancellation']['source'],'cli')


class TestStartupRefusal(CancelLatchL1):
    def test_guardian_startup_refusal_explains_and_reports_metadata(self):
        def metadata_latch():
            self.latch.write_text(json.dumps({'set_at':time.time()-30,'source':'cli'}))
        def legacy_latch():
            self.latch.write_text('legacy text')
            os.utime(self.latch,(time.time()-60,)*2)
        def dangling_latch():
            os.symlink(self.folder/'gone-target',self.latch)
        cases=(('metadata latch',metadata_latch,True),
               ('legacy latch',legacy_latch,False),
               ('dangling symlink latch',dangling_latch,False))
        for label,setup,expect_cli in cases:
            with self.subTest(case=label):
                if self.latch.is_symlink() or self.latch.exists():self.latch.unlink()
                setup()
                with patch.object(session,'owner_lock'), \
                        patch.object(session,'SNAPSHOT',self.folder/'absent-session.json'), \
                        patch.object(session,'STATE',self.state), \
                        patch.object(session,'CANCEL',self.latch), \
                        patch.object(session.signal,'signal'), \
                        patch.object(cancel_hotkey,'hotkey_off') as off:
                    with self.assertRaisesRegex(RuntimeError,'^cancelled by user') as caught:
                        session.guardian({},-1,'f'*32)
                message=str(caught.exception)
                self.assertIn('computer-use resume',message)
                self.assertIn('set_at=',message)
                if expect_cli:self.assertIn('source=cli',message)
                else:self.assertIn('legacy latch',message)
                off.assert_not_called()  # refusal raises before the try/finally cleanup

    def test_guardian_refusal_fails_closed_on_unreadable_lstat(self):
        # Same contract as latch_present: an unreadable latch state must refuse
        # startup (cancelled), never look 'ready'.
        with patch.object(session,'owner_lock'), \
                patch.object(session,'SNAPSHOT',self.folder/'absent-session.json'), \
                patch.object(session,'STATE',self.state), \
                patch.object(session,'CANCEL',self.folder/'unreadable-latch'), \
                patch.object(session.signal,'signal'), \
                patch.object(cancel_hotkey,'hotkey_off') as off, \
                patch.object(cancel_hotkey.os,'lstat',side_effect=PermissionError(13,'denied')):
            with self.assertRaisesRegex(RuntimeError,'^cancelled by user') as caught:
                session.guardian({},-1,'f'*32)
        message=str(caught.exception)
        self.assertIn('computer-use resume',message)
        self.assertIn('legacy latch',message)
        off.assert_not_called()


class TestDeepCorruptMetadata(CancelLatchL1):
    """P2 reviewer findings A (RecursionError) and B (lone UTF-16 surrogates):
    corrupt/deep metadata must fail closed yet stay reportable, and every
    metadata string must survive a REAL strict UTF-8 encoder/CLI stdout."""

    def test_deep_session_json_64K_never_blocks_physical_cancel(self):
        # 64 KiB of '[' fits the latch read limit and once raised RecursionError
        # inside latch(), crashing python cancel_hotkey.py cancel BEFORE the
        # latch write and request_stop (physical cancel prevented).
        (self.state/'session.json').write_text('['*65536)
        cancel_hotkey.latch(path=self.latch,source='physical-escape')  # must not raise
        detail=self.read_latch()
        self.assertIsNone(detail['session_token'])
        self.assertEqual(detail['source'],'physical-escape')
        self.assertTrue(cancel_hotkey.latch_present(self.latch))

    def test_deep_latch_metadata_still_reports_latched_with_guidance(self):
        self.latch.write_text('['*65536)
        status=cancel_hotkey.cancellation_status(self.latch)
        self.assertTrue(status['cancelled'])
        detail=status['cancellation']
        self.assertEqual(detail['source'],'legacy latch; origin unknown')
        self.assertEqual(detail['clear_with'],'computer-use resume')
        self.assertIn('continue',detail['instruction'])
        self.assertIn('cancelled by user',
                      cancel_hotkey.cancellation_message(self.latch))
        json.dumps(status,ensure_ascii=False).encode('utf-8')  # real utf8 output

    def test_lone_utf16_surrogate_metadata_stays_utf8_safe(self):
        self.latch.write_text('{"session_token":"sk-\\ud800-ok","source":"cli"}')
        detail=cancel_hotkey.cancellation_status(self.latch)['cancellation']
        self.assertEqual(detail['session_token'],'sk-?-ok')
        self.assertEqual(detail['source'],'cli')
        # StringIO/round-trip tests miss this: assert the REAL utf-8 encoder.
        json.dumps(detail,ensure_ascii=False).encode('utf-8')
        cancel_hotkey.cancellation_message(self.latch).encode('utf-8')

    def test_surrogate_session_token_round_trip_stays_utf8_safe(self):
        (self.state/'session.json').write_text('{"token":"\\ud800tok"}')
        cancel_hotkey.latch(path=self.latch,source='cli')
        self.latch.read_text(encoding='utf-8')  # ASCII-safe latch write
        detail=cancel_hotkey.cancellation_status(self.latch)['cancellation']
        json.dumps(detail,ensure_ascii=False).encode('utf-8')  # real utf8 output


if __name__=='__main__':
    unittest.main()
