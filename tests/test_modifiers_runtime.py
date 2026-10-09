"""Run real native/modifiers.c against an in-process Wayland mock.

The mock replaces wayland-client only; xkbcommon is the real library, so the
keymap upload path is exercised. No GUI/compositor is touched.
"""
import os
from pathlib import Path
import select
import shutil
import signal
import subprocess
import tempfile
import time
import unittest


HEADER = r'''
#ifndef MOCK_WAYLAND_H
#define MOCK_WAYLAND_H
#include <stdint.h>
struct wl_display; struct wl_registry; struct wl_seat; struct wl_callback;
struct zwp_virtual_keyboard_manager_v1; struct zwp_virtual_keyboard_v1;
struct wl_interface { const char *name; };
extern const struct wl_interface wl_seat_interface;
extern const struct wl_interface zwp_virtual_keyboard_manager_v1_interface;
struct wl_registry_listener {
 void (*global)(void *,struct wl_registry *,uint32_t,const char *,uint32_t);
 void (*global_remove)(void *,struct wl_registry *,uint32_t);
};
struct wl_callback_listener { void (*done)(void *,struct wl_callback *,uint32_t); };
struct wl_display *wl_display_connect(const char *);
struct wl_registry *wl_display_get_registry(struct wl_display *);
int wl_registry_add_listener(struct wl_registry *,const struct wl_registry_listener *,void *);
void *wl_registry_bind(struct wl_registry *,uint32_t,const struct wl_interface *,uint32_t);
struct wl_callback *wl_display_sync(struct wl_display *);
int wl_callback_add_listener(struct wl_callback *,const struct wl_callback_listener *,void *);
void wl_callback_destroy(struct wl_callback *);
int wl_display_get_fd(struct wl_display *);
int wl_display_get_error(struct wl_display *);
int wl_display_dispatch_pending(struct wl_display *);
int wl_display_prepare_read(struct wl_display *);
int wl_display_read_events(struct wl_display *);
void wl_display_cancel_read(struct wl_display *);
int wl_display_dispatch(struct wl_display *);
int wl_display_flush(struct wl_display *);
void wl_display_disconnect(struct wl_display *);
void wl_registry_destroy(struct wl_registry *);
void wl_seat_destroy(struct wl_seat *);
struct zwp_virtual_keyboard_v1 *zwp_virtual_keyboard_manager_v1_create_virtual_keyboard(
 struct zwp_virtual_keyboard_manager_v1 *,struct wl_seat *);
void zwp_virtual_keyboard_manager_v1_destroy(struct zwp_virtual_keyboard_manager_v1 *);
void zwp_virtual_keyboard_v1_keymap(struct zwp_virtual_keyboard_v1 *,uint32_t,int32_t,uint32_t);
void zwp_virtual_keyboard_v1_modifiers(struct zwp_virtual_keyboard_v1 *,uint32_t,uint32_t,uint32_t,uint32_t);
void zwp_virtual_keyboard_v1_destroy(struct zwp_virtual_keyboard_v1 *);
#endif
'''

MOCK = r'''
#include "wayland-client.h"
#include <errno.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
struct wl_display { int fd[2], error, syncs, reply, mods; };
struct wl_registry { int unused; }; struct wl_seat { int unused; };
struct wl_callback { int unused; }; struct zwp_virtual_keyboard_manager_v1 { int unused; };
struct zwp_virtual_keyboard_v1 { int unused; };
const struct wl_interface wl_seat_interface={"wl_seat"};
const struct wl_interface zwp_virtual_keyboard_manager_v1_interface={"zwp_virtual_keyboard_manager_v1"};
static struct wl_display display;
static struct wl_registry registry; static struct wl_seat seat; static struct wl_callback callback;
static struct zwp_virtual_keyboard_manager_v1 manager; static struct zwp_virtual_keyboard_v1 keyboard;
static const struct wl_registry_listener *globals;
static const struct wl_callback_listener *synced; static void *sync_data;
static int env_number(const char *key){const char *s=getenv(key);return s?atoi(s):0;}
struct wl_display *wl_display_connect(const char *name){
 (void)name;if(pipe(display.fd)<0)abort();return &display;
}
struct wl_registry *wl_display_get_registry(struct wl_display *d){(void)d;return &registry;}
int wl_registry_add_listener(struct wl_registry *r,const struct wl_registry_listener *l,void *data){
 (void)r;(void)data;globals=l;return 0;
}
void *wl_registry_bind(struct wl_registry *r,uint32_t id,const struct wl_interface *i,uint32_t v){
 (void)r;(void)i;(void)v;return id==1?(void *)&manager:(void *)&seat;
}
struct wl_callback *wl_display_sync(struct wl_display *d){
 d->syncs++;fprintf(stderr,"sync %d\n",d->syncs);return &callback;
}
int wl_callback_add_listener(struct wl_callback *c,const struct wl_callback_listener *l,void *data){
 (void)c;synced=l;sync_data=data;return 0;
}
void wl_callback_destroy(struct wl_callback *c){(void)c;synced=NULL;}
int wl_display_get_fd(struct wl_display *d){return d->fd[0];}
int wl_display_get_error(struct wl_display *d){return d->error;}
int wl_display_flush(struct wl_display *d){
 if(d->error){errno=d->error;return -1;}
 if(d->fd[1]<0){d->error=EPIPE;errno=EPIPE;return -1;}
 fprintf(stderr,"delivered %d\n",d->mods);
 if(synced && !d->reply && d->syncs!=env_number("STALL_AT")){
  if(write(d->fd[1],"s",1)!=1){abort();}
  d->reply=1;
 }
 return 0;
}
int wl_display_prepare_read(struct wl_display *d){(void)d;return 0;}
void wl_display_cancel_read(struct wl_display *d){(void)d;}
int wl_display_read_events(struct wl_display *d){
 char ch;if(read(d->fd[0],&ch,1)!=1)return -1;d->reply=0;
 if(d->syncs==env_number("FAIL_AT")){d->error=EPROTO;errno=EPROTO;return -1;}
 if(d->syncs==1){
  globals->global(NULL,&registry,1,"zwp_virtual_keyboard_manager_v1",1);
  globals->global(NULL,&registry,2,"wl_seat",1);
 }
 if(synced)synced->done(sync_data,&callback,0);
 if(d->syncs==env_number("DROP_AT")){close(d->fd[1]);d->fd[1]=-1;}
 return 0;
}
int wl_display_dispatch_pending(struct wl_display *d){return d->error?-1:0;}
int wl_display_dispatch(struct wl_display *d){return wl_display_read_events(d);}
void wl_display_disconnect(struct wl_display *d){
 fprintf(stderr,"disconnect\n");close(d->fd[0]);if(d->fd[1]>=0)close(d->fd[1]);
}
void wl_registry_destroy(struct wl_registry *r){(void)r;}
void wl_seat_destroy(struct wl_seat *s){(void)s;}
struct zwp_virtual_keyboard_v1 *zwp_virtual_keyboard_manager_v1_create_virtual_keyboard(
 struct zwp_virtual_keyboard_manager_v1 *m,struct wl_seat *s){(void)m;(void)s;return env_number("NO_KEYBOARD")?NULL:&keyboard;}
void zwp_virtual_keyboard_manager_v1_destroy(struct zwp_virtual_keyboard_manager_v1 *m){(void)m;}
void zwp_virtual_keyboard_v1_keymap(struct zwp_virtual_keyboard_v1 *k,uint32_t format,int32_t fd,uint32_t size){
 (void)k;(void)fd;fprintf(stderr,"keymap %u %u\n",format,size);
}
void zwp_virtual_keyboard_v1_modifiers(struct zwp_virtual_keyboard_v1 *k,uint32_t dep,
 uint32_t lat,uint32_t lock,uint32_t group){
 (void)k;(void)lat;(void)lock;(void)group;display.mods=(int)dep;fprintf(stderr,"mods %u\n",dep);
}
void zwp_virtual_keyboard_v1_destroy(struct zwp_virtual_keyboard_v1 *k){(void)k;fprintf(stderr,"destroy_keyboard\n");}
'''


class ModifiersRuntime(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        compiler = shutil.which('cc')
        if not compiler:
            raise unittest.SkipTest('C compiler unavailable')
        cls.temp = tempfile.TemporaryDirectory()
        cls.addClassCleanup(cls.temp.cleanup)
        folder = Path(cls.temp.name)
        source = Path(__file__).resolve().parents[1] / 'native/modifiers.c'
        (folder / 'modifiers.c').write_bytes(source.read_bytes())
        (folder / 'wayland-client.h').write_text(HEADER)
        (folder / 'keyboard-protocol.h').write_text('#include "wayland-client.h"\n')
        (folder / 'mock.c').write_text(MOCK)
        cls.binary = folder / 'modifiers'
        result = subprocess.run([compiler, '-std=c11', '-Wall', '-Wextra', '-Werror',
                                 '-I', str(folder), '-o', str(cls.binary),
                                 str(folder / 'modifiers.c'), str(folder / 'mock.c'),
                                 '-lxkbcommon'], capture_output=True, text=True)
        if result.returncode:
            raise RuntimeError(result.stderr)

    def start(self, **options):
        process = subprocess.Popen([str(self.binary)], stdin=subprocess.PIPE,
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE, bufsize=0,
                                   env=dict(os.environ, **{k: str(v) for k, v in options.items()}))
        self.addCleanup(self.dispose, process)
        return process

    @staticmethod
    def dispose(process):
        if process.poll() is None:
            process.kill()
        process.wait(timeout=3)
        for stream in (process.stdin, process.stdout, process.stderr):
            if stream:
                stream.close()

    def expect_line(self, stream, expected):
        self.assertTrue(select.select([stream], [], [], 3)[0], 'helper failed to respond')
        self.assertEqual(stream.readline(), expected)

    def ready(self, process):
        self.expect_line(process.stdout, b'ready\n')

    def test_mods_masks_acknowledged_after_flush(self):
        process = self.start()
        self.ready(process)
        for mask in (1, 4, 8, 64, 128, 5, 205, 0):
            process.stdin.write(f'mods {mask}\n'.encode())
            process.stdin.flush()
            self.expect_line(process.stdout, b'ok\n')
        out, log = process.communicate(timeout=3)
        self.assertEqual(process.returncode, 0, log)
        self.assertEqual(out, b'')
        self.assertIn(b'mods 205\n', log)       # mask applied before ack
        self.assertIn(b'delivered 205\n', log)  # and delivered after a flush
        self.assertIn(b'mods 0\n', log)         # cleanup reset

    def test_invalid_masks_rejected_without_acknowledgement(self):
        commands = [b'mods 2\n', b'mods 256\n', b'mods abc\n', b'mods 5 9\n',
                    b'mods\n', b'mods ' + b'1' * 300 + b'\n']
        for command in commands:
            with self.subTest(command=command[:20]):
                process = self.start()
                self.ready(process)
                out, log = process.communicate(command, timeout=3)
                self.assertEqual(process.returncode, 2, log)
                self.assertEqual(out, b'')
                self.assertIn(b'invalid modifiers command', log)
                self.assertIn(b'mods 0\n', log)

    def test_signals_release_mods_zero(self):
        for sig in (signal.SIGTERM, signal.SIGINT, signal.SIGHUP):
            with self.subTest(signal=sig):
                process = self.start()
                self.ready(process)
                process.stdin.write(b'mods 1\n')
                process.stdin.flush()
                self.expect_line(process.stdout, b'ok\n')
                process.send_signal(sig)
                process.wait(timeout=3)  # stdin stays open during this wait.
                out, log = process.communicate(timeout=3)
                self.assertEqual(process.returncode, 128 + sig, log)
                self.assertEqual(out, b'')
                self.assertIn(b'mods 0\n', log)

    def test_idle_disconnect_is_bounded(self):
        process = self.start(DROP_AT=3)
        self.ready(process)
        started = time.monotonic()
        process.wait(timeout=3)
        out, log = process.communicate(timeout=3)
        self.assertEqual(process.returncode, 2, log)
        self.assertEqual(out, b'')
        self.assertIn(b'Wayland disconnected', log)
        self.assertLess(time.monotonic() - started, 2)

    def test_command_sync_stall_is_bounded_and_releases(self):
        process = self.start(STALL_AT=4)
        self.ready(process)
        started = time.monotonic()
        out, log = process.communicate(b'mods 5\n', timeout=3)
        self.assertEqual(process.returncode, 2, log)
        self.assertEqual(out, b'')
        self.assertIn(b'Wayland command failed', log)
        self.assertIn(b'mods 0\n', log)
        self.assertLess(time.monotonic() - started, 2)

    def test_signal_during_stalled_sync_is_bounded(self):
        process = self.start(STALL_AT=4)
        self.ready(process)
        process.stdin.write(b'mods 5\n')
        process.stdin.flush()
        prefix = b''
        deadline = time.monotonic() + 3
        while b'sync 4\n' not in prefix:
            remaining = deadline - time.monotonic()
            self.assertGreater(remaining, 0)
            self.assertTrue(select.select([process.stderr], [], [], remaining)[0])
            chunk = os.read(process.stderr.fileno(), 4096)
            self.assertTrue(chunk, 'helper exited before entering sync')
            prefix += chunk
        started = time.monotonic()
        process.send_signal(signal.SIGTERM)
        process.wait(timeout=3)
        out, log = process.communicate(timeout=3)
        self.assertEqual(process.returncode, 128 + signal.SIGTERM, log)
        self.assertEqual(out, b'')
        self.assertIn(b'mods 0\n', prefix + log)
        self.assertLess(time.monotonic() - started, 2)

    def test_startup_failures_clean_up_without_ready(self):
        for options, message in (({'FAIL_AT': 1}, b'Wayland discovery failed'),
                                 ({'NO_KEYBOARD': 1}, b'virtual keyboard initialization failed')):
            with self.subTest(options=options):
                process = self.start(**options)
                out, log = process.communicate(timeout=3)
                self.assertEqual(process.returncode, 2, log)
                self.assertEqual(out, b'')
                self.assertIn(message, log)


if __name__ == '__main__':
    unittest.main()
