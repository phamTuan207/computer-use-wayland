import ctypes.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import cursor_theme
import cursor_session


class CursorTheme(unittest.TestCase):
    def test_required_snapshot_records_exact_original_gtk_state(self):
        with tempfile.TemporaryDirectory() as tmp:
            profile=Path(tmp)/'profile.json'
            profile.write_text(json.dumps(dict(theme='cu-agent-v1',size=32,restore_theme='default',restore_size=24)))
            with patch.object(cursor_theme,'PROFILE',profile),patch.object(cursor_theme,'command',side_effect=['',"'Adwaita'",'24']) as command:
                saved=cursor_theme.snapshot({})
        self.assertEqual(saved['gtk_theme'],'Adwaita')
        self.assertEqual(saved['gtk_size'],24)
        self.assertEqual(saved['hypr_theme'],'default')
        probe=command.call_args_list[0].args
        self.assertIn(cursor_theme.THEME_CHECK_CODE,probe)
        self.assertEqual(probe[-2:],('cu-agent-v1','32'))

    def test_missing_profile_raises_before_desktop_calls(self):
        with patch.object(cursor_theme.Path,'is_file',return_value=False),patch.object(cursor_theme,'command') as command:
            with self.assertRaisesRegex(RuntimeError,'profile required'):cursor_theme.snapshot({})
            command.assert_not_called()

    def test_oversized_profile_rejected_before_desktop_calls(self):
        with tempfile.TemporaryDirectory() as tmp:
            profile=Path(tmp)/'profile.json'
            profile.write_bytes(b'{"theme":"x",' + b' '*4096 + b'}')
            with patch.object(cursor_theme,'PROFILE',profile),patch.object(cursor_theme,'command') as command:
                with self.assertRaisesRegex(ValueError,'exceeds 4096'):cursor_theme.snapshot({})
                command.assert_not_called()

    def test_unloadable_asset_refuses_before_gtk_queries(self):
        with tempfile.TemporaryDirectory() as tmp:
            profile=self._profile(tmp)
            with patch.object(cursor_theme,'PROFILE',profile), \
                 patch.object(cursor_theme,'command',side_effect=subprocess.CalledProcessError(1,['probe'])) as command:
                with self.assertRaises(subprocess.CalledProcessError):cursor_theme.snapshot({})
                command.assert_called_once()

    def test_dot_and_dotdot_theme_names_rejected(self):
        for bad in ('.','..'):
            with self.subTest(bad=bad),patch.object(cursor_theme,'Guard') as guard:
                with self.assertRaises(ValueError):cursor_theme.apply({},bad,32,'a'*32)
                guard.assert_not_called()

    def test_invalid_theme_rejected_before_side_effects(self):
        with patch.object(cursor_theme,'Guard') as guard:
            with self.assertRaises(ValueError):cursor_theme.apply({},'bad theme; injected',32,'a'*32)
            guard.assert_not_called()

    def test_apply_requires_a_session_token(self):
        with self.assertRaises(ValueError):
            cursor_theme.apply({'XDG_RUNTIME_DIR':'/run/user/1000'},'cu-agent-v1',32)

    def test_apply_hands_validated_values_to_the_lease(self):
        env={'XDG_RUNTIME_DIR':'/run/user/1000'}
        with patch.object(cursor_theme,'Guard',return_value='lease') as guard:
            self.assertEqual(cursor_theme.apply(env,'cu-agent-v1',32,'a'*32),'lease')
            guard.assert_called_once_with(env,'cu-agent-v1',32,'a'*32)

    def test_restore_keeps_distinct_gtk_and_compositor_values(self):
        saved=dict(gtk_theme='Adwaita',gtk_size=24,hypr_theme='default',hypr_size=32)
        with patch.object(cursor_theme,'command',return_value='ok') as command:
            cursor_theme.restore({},saved)
        self.assertEqual(command.call_args_list[0].args[-1],'Adwaita')
        self.assertEqual(command.call_args.args,({},'hyprctl','setcursor','default','32'))

    def test_failed_guardian_restore_preserves_snapshot(self):
        import cancel_hotkey
        with tempfile.TemporaryDirectory() as tmp:
            state=Path(tmp);snapshot=state/'session.json'
            snapshot.write_text(json.dumps(dict(version=4,token='a'*32,cursor={})))
            with patch.object(cursor_session,'SNAPSHOT',snapshot),patch.object(cursor_session,'STATE',state), \
                 patch.object(cancel_hotkey,'hotkey_off'),patch.object(cursor_theme,'restore',side_effect=RuntimeError('injected')):
                self.assertFalse(cursor_session.restore({}))
            self.assertTrue(snapshot.exists())

    def _profile(self,tmp,**extra):
        profile=Path(tmp)/'profile.json'
        data=dict(theme='cu-agent-v1',size=32,restore_theme='Manual-base',restore_size=32)
        data.update(extra)
        profile.write_text(json.dumps(data))
        return profile

    def test_declared_compositor_restore_stays_distinct_from_actual_gtk(self):
        with tempfile.TemporaryDirectory() as tmp:
            profile=self._profile(tmp,restore_theme='Manual-base',restore_size=32)
            with patch.object(cursor_theme,'PROFILE',profile),patch.object(cursor_theme,'command',side_effect=['',"'GTK-base'",'24']):
                saved=cursor_theme.snapshot({})
        self.assertEqual((saved['gtk_theme'],saved['gtk_size']),('GTK-base',24))
        self.assertEqual((saved['hypr_theme'],saved['hypr_size']),('Manual-base',32))

    def test_missing_restore_fields_refuse_before_desktop_queries(self):
        with tempfile.TemporaryDirectory() as tmp:
            profile=self._profile(tmp)
            profile.write_text(json.dumps({'theme':'cu-agent-v1','size':34}))
            with patch.object(cursor_theme,'PROFILE',profile),patch.object(cursor_theme,'command') as command:
                with self.assertRaises(KeyError):cursor_theme.snapshot({})
                command.assert_not_called()

    def test_gtk_guessing_policy_is_refused_before_desktop_queries(self):
        with tempfile.TemporaryDirectory() as tmp:
            profile=self._profile(tmp,restore_mode='gtk')
            with patch.object(cursor_theme,'PROFILE',profile),patch.object(cursor_theme,'command') as command:
                with self.assertRaisesRegex(ValueError,'unknown restore_mode'):
                    cursor_theme.snapshot({})
                command.assert_not_called()

    def test_unknown_restore_mode_is_refused_before_queries(self):
        with tempfile.TemporaryDirectory() as tmp:
            profile=self._profile(tmp,restore_mode='guess')
            with patch.object(cursor_theme,'PROFILE',profile),patch.object(cursor_theme,'command') as command:
                with self.assertRaisesRegex(ValueError,'unknown restore_mode'):
                    cursor_theme.snapshot({'HYPRLAND_INSTANCE_SIGNATURE':'fresh-login'})
                command.assert_not_called()

    def test_agent_theme_is_validated_before_any_instance_check(self):
        with tempfile.TemporaryDirectory() as tmp:
            profile=self._profile(tmp,theme='bad theme; injected')
            with patch.object(cursor_theme,'PROFILE',profile),patch.object(cursor_theme,'command') as command:
                with self.assertRaises(ValueError):
                    cursor_theme.snapshot({'HYPRLAND_INSTANCE_SIGNATURE':'fresh-login'})
                command.assert_not_called()

    def test_invalid_gtk_values_refuse_before_apply(self):
        with tempfile.TemporaryDirectory() as tmp:
            profile=self._profile(tmp)
            env={'HYPRLAND_INSTANCE_SIGNATURE':'fresh-login'}
            with patch.object(cursor_theme,'PROFILE',profile),patch.object(cursor_theme,'command',side_effect=['',"'ok'",'24']):
                saved=cursor_theme.snapshot(env)
        with patch.object(cursor_theme,'Guard',return_value='lease') as guard:
            cursor_theme.apply({},'cu-agent-v1',saved['agent_size'],'a'*32)
            guard.assert_called_once()


class SearchRoots(unittest.TestCase):
    """The Xcursor search path, read from the library rather than assumed."""

    def test_it_runs_one_static_ctypes_probe_with_the_supplied_env(self):
        env={'XCURSOR_PATH':'/override','PATH':'/usr/bin'}
        with patch.object(cursor_theme,'command',return_value='/usr/share/icons') as command:
            roots=cursor_theme.search_roots(env)
        command.assert_called_once_with(env, sys.executable, '-c',
                                        cursor_theme.SEARCH_ROOTS_CODE)
        code=cursor_theme.SEARCH_ROOTS_CODE
        self.assertIn("ctypes.CDLL('libXcursor.so.1')", code)
        self.assertIn('XcursorLibraryPath.restype = ctypes.c_char_p', code)
        self.assertIn('.decode()', code)
        self.assertEqual(roots, [Path('/usr/share/icons')])

    def test_the_environment_override_and_tilde_are_expanded(self):
        with tempfile.TemporaryDirectory() as home, patch.dict(os.environ, {'HOME': home}), \
             patch.object(cursor_theme,'command',return_value='~/.local/share/icons:/tmp/x:'):
            roots=cursor_theme.search_roots({})
        self.assertEqual(roots, [Path(home).resolve()/'.local/share/icons', Path('/tmp/x')])
        self.assertTrue(all(root.is_absolute() for root in roots))

    def test_empty_and_blank_components_are_dropped(self):
        for raw, expected in (('', []), (':', []), ('/a::/b', [Path('/a'), Path('/b')])):
            with self.subTest(raw=raw), patch.object(cursor_theme,'command',return_value=raw):
                self.assertEqual(cursor_theme.search_roots({}), expected)

    def test_a_missing_library_fails_loudly(self):
        with patch.object(cursor_theme,'command',
                          side_effect=subprocess.CalledProcessError(1, 'probe')):
            with self.assertRaises(subprocess.CalledProcessError):
                cursor_theme.search_roots({})

    @unittest.skipUnless(ctypes.util.find_library('Xcursor'),
                         'libXcursor.so.1 is not installed here')
    def test_real_probe_reports_absolute_paths_without_a_display(self):
        env=dict(os.environ)
        env.pop('XCURSOR_PATH', None)
        env.pop('DISPLAY', None)
        env.pop('WAYLAND_DISPLAY', None)
        roots=cursor_theme.search_roots(env)
        self.assertIsInstance(roots, list)
        self.assertTrue(roots, 'a compiled Xcursor default is always reported')
        self.assertTrue(all(root.is_absolute() for root in roots))


class GuardProtocol(unittest.TestCase):
    """check_guard, guard_reply, token-bound restore and the socket lease."""

    def test_guard_reply_accepts_exact_confirmation(self):
        reply=cursor_theme.guard_reply('{"ok":true,"schema":1,"token":"%s"}' % ('a'*32),token='a'*32)
        self.assertTrue(reply['ok'])

    def test_guard_reply_rejects_oversize_shape_mismatch_and_wrong_token(self):
        good='{"ok":true,"schema":1,"token":"%s"}' % ('a'*32)
        with self.assertRaisesRegex(RuntimeError,'exceeds 4096'):
            cursor_theme.guard_reply(' '*(4097-len(good))+good,token='a'*32)
        for raw in ('[]',
                    '{"ok":false,"schema":1,"token":"%s"}' % ('a'*32),
                    '{"ok":true,"schema":2,"token":"%s"}' % ('a'*32),
                    '{"ok":true,"schema":"1","token":"%s"}' % ('a'*32),
                    '{"ok":true,"schema":1,"token":"%s"}' % ('b'*32)):
            with self.subTest(raw=raw[:40]):
                with self.assertRaisesRegex(RuntimeError,'did not confirm'):
                    cursor_theme.guard_reply(raw,token='a'*32)

    def test_check_guard_requires_idle_backend(self):
        with patch.object(cursor_theme,'command',return_value='{"ok":true,"schema":1,"active":false,"token":""}'):
            cursor_theme.check_guard({})
        for payload in ('{"ok":true,"schema":1,"active":true,"token":""}',
                        '{"ok":true,"schema":1,"active":false,"token":"%s"}' % ('a'*32),
                        '{"ok":true,"schema":2,"active":false,"token":""}'):
            with self.subTest(payload=payload[:40]),patch.object(cursor_theme,'command',return_value=payload):
                with self.assertRaises(RuntimeError):cursor_theme.check_guard({})

    def test_restore_with_guard_token_releases_exact_token(self):
        token='c'*32
        with patch.object(cursor_theme,'command',return_value='{"ok":true,"schema":1,"released":"%s"}' % token) as command:
            self.assertIsNone(cursor_theme.restore({}, {'guard_token':token}))
        self.assertEqual(command.call_args.args,({},'hyprctl','cu-cursor','release',token))

    def test_restore_with_bad_guard_token_or_refused_release_fails(self):
        with patch.object(cursor_theme,'command') as command:
            with self.assertRaises(ValueError):
                cursor_theme.restore({}, {'guard_token':'not-hex'})
            command.assert_not_called()
        for payload in ('{"ok":false,"schema":1,"released":"%s"}' % ('d'*32),
                        '{"ok":true,"schema":1,"released":"%s"}' % ('e'*32)):
            with self.subTest(payload=payload[:40]),patch.object(cursor_theme,'command',return_value=payload):
                with self.assertRaises(RuntimeError):
                    cursor_theme.restore({}, {'guard_token':'d'*32})

    def _runtime(self, tmp, mode=0o700):
        runtime=Path(tmp)/'run'
        guarddir=runtime/'agent-computer-use'
        guarddir.mkdir(parents=True)
        guarddir.chmod(mode)
        return {'XDG_RUNTIME_DIR':str(runtime)}, guarddir/'cursor-guard.sock'

    def _serve_once(self, sock, script):
        import socket as netsocket
        listener=netsocket.socket(netsocket.AF_UNIX,netsocket.SOCK_STREAM)
        listener.bind(str(sock));listener.listen(1);listener.settimeout(10)
        outcome={}
        def run():
            try:
                conn,_=listener.accept()
                with conn:
                    outcome['result']=script(conn)
            except BaseException as exc:outcome['error']=exc
            finally:listener.close()
        import threading
        worker=threading.Thread(target=run,daemon=True);worker.start()
        return worker,outcome

    def _read_line(self, conn, outcome_key='request'):
        data=bytearray()
        while b'\n' not in data:
            part=conn.recv(4096)
            if not part:break
            data.extend(part)
        return data

    def test_lease_handshake_confirms_token_then_eof_closes(self):
        import socket as netsocket
        token='f'*32
        with tempfile.TemporaryDirectory() as tmp:
            env,sock=self._runtime(tmp)
            seen={}
            def script(conn):
                seen['request']=json.loads(self._read_line(conn).decode())
                conn.sendall((json.dumps({'ok':True,'schema':1,'token':token})+'\n').encode())
                rest=conn.recv(16)
                seen['eof']=rest
                return True
            worker,outcome=self._serve_once(sock,script)
            guard=cursor_theme.Guard(env,'cu-agent-test',32,token)
            self.assertEqual(seen['request'],{'schema':1,'theme':'cu-agent-test','size':32,'token':token})
            guard.close()
            worker.join(timeout=10)
            self.assertTrue(outcome.get('result'))
            self.assertEqual(seen['eof'],b'')

    def test_command_hides_then_shows_with_state_acks(self):
        token='a'*32
        with tempfile.TemporaryDirectory() as tmp:
            env,sock=self._runtime(tmp)
            seen=[]
            def script(conn):
                seen.append(json.loads(self._read_line(conn).decode()))
                conn.sendall((json.dumps({'ok':True,'schema':1,'token':token})+'\n').encode())
                for state in ('hidden','visible'):
                    request=json.loads(self._read_line(conn).decode())
                    seen.append(request)
                    conn.sendall((json.dumps({'ok':True,'schema':1,'token':token,'state':state})+'\n').encode())
                seen.append(conn.recv(16))
                return True
            worker,outcome=self._serve_once(sock,script)
            guard=cursor_theme.Guard(env,'cu-agent-test',32,token)
            guard.command('hide')
            guard.command('show')
            guard.close()
            worker.join(timeout=10)
            self.assertTrue(outcome.get('result'))
            self.assertEqual(seen[0],{'schema':1,'theme':'cu-agent-test','size':32,'token':token})
            self.assertEqual(seen[1],{'op':'hide','token':token})
            self.assertEqual(seen[2],{'op':'show','token':token})
            self.assertEqual(seen[3],b'')

    def test_command_rejects_invalid_op_before_any_io(self):
        token='a'*32
        with tempfile.TemporaryDirectory() as tmp:
            env,sock=self._runtime(tmp)
            seen=[]
            def script(conn):
                seen.append(json.loads(self._read_line(conn).decode()))
                conn.sendall((json.dumps({'ok':True,'schema':1,'token':token})+'\n').encode())
                conn.settimeout(0.5)
                try:seen.append(conn.recv(64))
                except Exception as exc:seen.append(exc)
                return True
            worker,outcome=self._serve_once(sock,script)
            guard=cursor_theme.Guard(env,'cu-agent-test',32,token)
            with self.assertRaises(ValueError):
                guard.command('blink')
            guard.close()
            worker.join(timeout=10)
            self.assertTrue(outcome.get('result'))
            self.assertEqual(len(seen),2)
            self.assertEqual(seen[1],b'')

    def test_command_responses_are_bounded_framed_and_token_checked(self):
        token='a'*32
        good={'ok':True,'schema':1,'token':token,'state':'hidden'}
        cases={
            'wrong-state':dict(good,state='visible'),
            'wrong-token':dict(good,token='b'*32),
            'missing-state':{'ok':True,'schema':1,'token':token},
            'not-ok':dict(good,ok=False),
            'bad-schema':dict(good,schema=2),
            'two-frames':None,
            'oversize':None,
            'garbage':None,
        }
        payloads={
            'two-frames':(json.dumps(good)+'\n'+json.dumps(good)+'\n').encode(),
            'oversize':b'x'*5000,
            'garbage':b'not json\n',
        }
        for label,reply in cases.items():
            with self.subTest(label=label),tempfile.TemporaryDirectory() as tmp:
                env,sock=self._runtime(tmp)
                def script(conn,reply=reply,label=label):
                    self._read_line(conn)
                    conn.sendall((json.dumps({'ok':True,'schema':1,'token':token})+'\n').encode())
                    self._read_line(conn)
                    conn.sendall(payloads.get(label,(json.dumps(reply)+'\n').encode()))
                    conn.recv(16)
                    return True
                worker,_=self._serve_once(sock,script)
                guard=cursor_theme.Guard(env,'cu-agent-test',32,token)
                try:
                    # Malformed JSON surfaces the decoder's ValueError; every
                    # other bad ack surfaces RuntimeError. Either fails closed.
                    with self.assertRaises((RuntimeError,ValueError)):
                        guard.command('hide')
                finally:
                    guard.close()
                worker.join(timeout=10)

    def test_clean_eof_reports_before_acknowledgement(self):
        token='a'*32
        with tempfile.TemporaryDirectory() as tmp:
            env,sock=self._runtime(tmp)
            def script(conn):
                self._read_line(conn)
                conn.sendall((json.dumps({'ok':True,'schema':1,'token':token})+'\n').encode())
                self._read_line(conn)
                conn.close()
                return True
            worker,_=self._serve_once(sock,script)
            guard=cursor_theme.Guard(env,'cu-agent-test',32,token)
            try:
                with self.assertRaisesRegex(RuntimeError,'before acknowledgement'):
                    guard.command('hide')
            finally:
                guard.close()
            worker.join(timeout=10)
    def test_wrong_token_oversize_framing_and_drop_all_fail_closed(self):
        token='a'*32
        cases={
            'wrong-token':lambda conn:conn.sendall((json.dumps({'ok':True,'schema':1,'token':'b'*32})+'\n').encode()) or conn.recv(16),
            'two-frames':lambda conn:conn.sendall((json.dumps({'ok':True,'schema':1,'token':token})+'\n'+'extra\n').encode()) or conn.recv(16),
            'oversize':lambda conn:conn.sendall(b'x'*5000) or conn.recv(16),
        }
        for label,script in cases.items():
            with self.subTest(label=label),tempfile.TemporaryDirectory() as tmp:
                env,sock=self._runtime(tmp)
                worker,_=self._serve_once(sock,script)
                with self.assertRaises(RuntimeError):
                    cursor_theme.Guard(env,'cu-agent-test',32,token)
                worker.join(timeout=10)
        with tempfile.TemporaryDirectory() as tmp:
            env,sock=self._runtime(tmp)
            def drop(conn):conn.close()
            worker,_=self._serve_once(sock,drop)
            # Clean EOF or RST: either way no lease starts.
            with self.assertRaises((RuntimeError,ConnectionResetError)):
                cursor_theme.Guard(env,'cu-agent-test',32,token)
            worker.join(timeout=10)

    def test_private_directory_and_socket_are_required(self):
        with tempfile.TemporaryDirectory() as tmp:
            env,_=self._runtime(tmp,mode=0o755)
            with self.assertRaisesRegex(RuntimeError,'not private'):
                cursor_theme.Guard(env,'cu-agent-test',32,'a'*32)
        with tempfile.TemporaryDirectory() as tmp:
            env,sock=self._runtime(tmp)
            sock.write_bytes(b'not a socket')
            with self.assertRaisesRegex(RuntimeError,'not a private socket'):
                cursor_theme.Guard(env,'cu-agent-test',32,'a'*32)
            sock.unlink();sock.symlink_to('/tmp')
            with self.assertRaisesRegex(RuntimeError,'not a private socket'):
                cursor_theme.Guard(env,'cu-agent-test',32,'a'*32)
        with tempfile.TemporaryDirectory() as tmp:
            # No socket file at all: lstat fails, so no lease can start.
            env,sock=self._runtime(tmp)
            sock.unlink(missing_ok=True)
            with self.assertRaises(OSError):
                cursor_theme.Guard(env,'cu-agent-test',32,'a'*32)
        for env in ({}, {'XDG_RUNTIME_DIR':'relative/path'}):
            with self.subTest(env=env),self.assertRaisesRegex(RuntimeError,'XDG_RUNTIME_DIR'):
                cursor_theme.Guard(env,'cu-agent-test',32,'a'*32)
        with tempfile.TemporaryDirectory() as tmp:
            env,_=self._runtime(tmp)
            with self.assertRaises(ValueError):
                cursor_theme.Guard(env,'cu-agent-test',32,'short')


if __name__ == '__main__':
    unittest.main()
