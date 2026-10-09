"""Run the real pointer main against an in-process mock, without a GUI/socket.

The mock queues button requests until frame/flush, records delivered state,
and uses a pipe to model sync replies, disconnects and an unresponsive server.
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
struct wl_display; struct wl_registry; struct wl_output; struct wl_seat;
struct wl_callback; struct zwlr_virtual_pointer_manager_v1;
struct zwlr_virtual_pointer_v1;
struct wl_interface { const char *name; };
extern const struct wl_interface wl_output_interface, wl_seat_interface;
extern const struct wl_interface zwlr_virtual_pointer_manager_v1_interface;
struct wl_registry_listener {
 void (*global)(void *,struct wl_registry *,uint32_t,const char *,uint32_t);
 void (*global_remove)(void *,struct wl_registry *,uint32_t);
};
struct wl_output_listener {
 void (*geometry)(void *,struct wl_output *,int32_t,int32_t,int32_t,int32_t,
                  int32_t,const char *,const char *,int32_t);
 void (*mode)(void *,struct wl_output *,uint32_t,int32_t,int32_t,int32_t);
 void (*done)(void *,struct wl_output *);
 void (*scale)(void *,struct wl_output *,int32_t);
 void (*name)(void *,struct wl_output *,const char *);
 void (*description)(void *,struct wl_output *,const char *);
};
struct wl_callback_listener { void (*done)(void *,struct wl_callback *,uint32_t); };
#define WL_POINTER_AXIS_SOURCE_WHEEL 0
#define WL_POINTER_AXIS_VERTICAL_SCROLL 0
#define WL_POINTER_AXIS_HORIZONTAL_SCROLL 1
struct wl_display *wl_display_connect(const char *);
struct wl_registry *wl_display_get_registry(struct wl_display *);
int wl_registry_add_listener(struct wl_registry *,const struct wl_registry_listener *,void *);
void *wl_registry_bind(struct wl_registry *,uint32_t,const struct wl_interface *,uint32_t);
int wl_output_add_listener(struct wl_output *,const struct wl_output_listener *,void *);
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
void wl_output_destroy(struct wl_output *);
struct zwlr_virtual_pointer_v1 *zwlr_virtual_pointer_manager_v1_create_virtual_pointer_with_output(
 struct zwlr_virtual_pointer_manager_v1 *,struct wl_seat *,struct wl_output *);
void zwlr_virtual_pointer_manager_v1_destroy(struct zwlr_virtual_pointer_manager_v1 *);
void zwlr_virtual_pointer_v1_destroy(struct zwlr_virtual_pointer_v1 *);
void zwlr_virtual_pointer_v1_motion_absolute(struct zwlr_virtual_pointer_v1 *,uint32_t,uint32_t,uint32_t,uint32_t,uint32_t);
void zwlr_virtual_pointer_v1_button(struct zwlr_virtual_pointer_v1 *,uint32_t,uint32_t,uint32_t);
void zwlr_virtual_pointer_v1_frame(struct zwlr_virtual_pointer_v1 *);
void zwlr_virtual_pointer_v1_axis_source(struct zwlr_virtual_pointer_v1 *,uint32_t);
void zwlr_virtual_pointer_v1_axis_discrete(struct zwlr_virtual_pointer_v1 *,uint32_t,uint32_t,int32_t,int32_t);
int32_t wl_fixed_from_double(double);
#endif
'''

MOCK = r'''
#include "wayland-client.h"
#include <errno.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
struct wl_display { int fd[2], error, syncs, reply, queued, framed, delivered; };
struct wl_registry { int unused; }; struct wl_output { int unused; };
struct wl_seat { int unused; }; struct wl_callback { int unused; };
struct zwlr_virtual_pointer_manager_v1 { int unused; };
struct zwlr_virtual_pointer_v1 { int unused; };
const struct wl_interface wl_output_interface={"wl_output"}, wl_seat_interface={"wl_seat"};
const struct wl_interface zwlr_virtual_pointer_manager_v1_interface={"virtual_pointer"};
static struct wl_display display;
static struct wl_registry registry;
static struct wl_output output;
static struct wl_seat seat;
static struct wl_callback callback;
static struct zwlr_virtual_pointer_manager_v1 manager;
static struct zwlr_virtual_pointer_v1 pointer;
static const struct wl_registry_listener *globals;
static const struct wl_output_listener *outputs;
static const struct wl_callback_listener *synced;
static void *sync_data;
static int env_number(const char *key) { const char *s=getenv(key);return s?atoi(s):0; }
struct wl_display *wl_display_connect(const char *name) {
 (void)name;if(pipe(display.fd)<0) abort();return &display;
}
struct wl_registry *wl_display_get_registry(struct wl_display *d) {(void)d;return &registry;}
int wl_registry_add_listener(struct wl_registry *r,const struct wl_registry_listener *l,void *data) {
 (void)r;(void)data;globals=l;return 0;
}
void *wl_registry_bind(struct wl_registry *r,uint32_t id,const struct wl_interface *i,uint32_t v) {
 (void)r;(void)i;(void)v;return id==1?(void *)&manager:id==2?(void *)&seat:(void *)&output;
}
int wl_output_add_listener(struct wl_output *o,const struct wl_output_listener *l,void *data) {
 (void)o;(void)data;outputs=l;return 0;
}
struct wl_callback *wl_display_sync(struct wl_display *d) {
 d->syncs++;fprintf(stderr,"sync %d\n",d->syncs);return &callback;
}
int wl_callback_add_listener(struct wl_callback *c,const struct wl_callback_listener *l,void *data) {
 (void)c;synced=l;sync_data=data;return 0;
}
void wl_callback_destroy(struct wl_callback *c) {(void)c;synced=NULL;}
int wl_display_get_fd(struct wl_display *d) {return d->fd[0];}
int wl_display_get_error(struct wl_display *d) {return d->error;}
int wl_display_flush(struct wl_display *d) {
 if(d->error) {errno=d->error;return -1;}
 if(d->fd[1]<0) {d->error=EPIPE;errno=EPIPE;return -1;}
 if(d->framed) {
   d->delivered=d->queued;d->framed=0;
   fprintf(stderr,"delivered %d\n",d->delivered);
 }
 if(synced && !d->reply && d->syncs!=env_number("STALL_AT")) {
   if(write(d->fd[1],"s",1)!=1) abort();
   d->reply=1;
 }
 return 0;
}
int wl_display_prepare_read(struct wl_display *d) {(void)d;return 0;}
void wl_display_cancel_read(struct wl_display *d) {(void)d;}
int wl_display_read_events(struct wl_display *d) {
 char ch;if(read(d->fd[0],&ch,1)!=1) return -1;d->reply=0;
 if(d->syncs==env_number("FAIL_AT")) {d->error=EPROTO;errno=EPROTO;return -1;}
 if(d->syncs==1) {
   globals->global(NULL,&registry,1,"virtual_pointer",2);
   globals->global(NULL,&registry,2,"wl_seat",1);
   globals->global(NULL,&registry,3,"wl_output",4);
 } else if(d->syncs==2 && !env_number("MISSING_OUTPUT")) outputs->name(NULL,&output,"MOCK");
 if(synced) synced->done(sync_data,&callback,0);
 if(d->syncs==env_number("DROP_AT")) {close(d->fd[1]);d->fd[1]=-1;}
 return 0;
}
int wl_display_dispatch_pending(struct wl_display *d) {return d->error?-1:0;}
int wl_display_dispatch(struct wl_display *d) {return wl_display_read_events(d);}
void wl_display_disconnect(struct wl_display *d) {
 fprintf(stderr,"disconnect %d\n",d->delivered);close(d->fd[0]);
 if(d->fd[1]>=0) close(d->fd[1]);
}
void wl_registry_destroy(struct wl_registry *r) {(void)r;}
void wl_seat_destroy(struct wl_seat *s) {(void)s;}
void wl_output_destroy(struct wl_output *o) {(void)o;}
struct zwlr_virtual_pointer_v1 *zwlr_virtual_pointer_manager_v1_create_virtual_pointer_with_output(
 struct zwlr_virtual_pointer_manager_v1 *m,struct wl_seat *s,struct wl_output *o) {
 (void)m;(void)s;(void)o;return env_number("NO_POINTER")?NULL:&pointer;
}
void zwlr_virtual_pointer_manager_v1_destroy(struct zwlr_virtual_pointer_manager_v1 *m) {(void)m;}
void zwlr_virtual_pointer_v1_destroy(struct zwlr_virtual_pointer_v1 *p) {
 (void)p;fprintf(stderr,"destroy %d\n",display.delivered);
}
void zwlr_virtual_pointer_v1_motion_absolute(struct zwlr_virtual_pointer_v1 *p,uint32_t t,
 uint32_t x,uint32_t y,uint32_t w,uint32_t h) {(void)p;(void)t;(void)x;(void)y;(void)w;(void)h;}
void zwlr_virtual_pointer_v1_button(struct zwlr_virtual_pointer_v1 *p,uint32_t t,uint32_t b,uint32_t down) {
 (void)p;(void)t;if(b<0x110 || b>0x112 || down>1) abort();
 unsigned bit=1u<<(b-0x110);
 if(down) display.queued|=bit;else display.queued&=~bit;
 fprintf(stderr,"button %u %u\n",b,down);
}
void zwlr_virtual_pointer_v1_frame(struct zwlr_virtual_pointer_v1 *p) {(void)p;display.framed=1;}
void zwlr_virtual_pointer_v1_axis_source(struct zwlr_virtual_pointer_v1 *p,uint32_t source) {(void)p;(void)source;}
void zwlr_virtual_pointer_v1_axis_discrete(struct zwlr_virtual_pointer_v1 *p,uint32_t t,
 uint32_t axis,int32_t distance,int32_t steps) {(void)p;(void)t;(void)axis;(void)distance;(void)steps;}
int32_t wl_fixed_from_double(double d) {return (int32_t)(d*256);}
'''


class NativePointer(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        compiler = shutil.which('cc')
        if not compiler:
            raise unittest.SkipTest('C compiler unavailable')
        cls.temp = tempfile.TemporaryDirectory()
        cls.addClassCleanup(cls.temp.cleanup)
        folder = Path(cls.temp.name)
        # Copy only to resolve quoted protocol includes to the mock headers.
        source = Path(__file__).resolve().parents[1] / 'native/pointer.c'
        (folder / 'pointer.c').write_bytes(source.read_bytes())
        (folder / 'wayland-client.h').write_text(HEADER)
        (folder / 'pointer-protocol.h').write_text('#include "wayland-client.h"\n')
        (folder / 'mock.c').write_text(MOCK)
        cls.binary = folder / 'pointer'
        result = subprocess.run([compiler, '-std=c11', '-Wall', '-Wextra', '-Werror',
                                 '-I', str(folder),
                                 '-o', str(cls.binary), str(folder / 'pointer.c'),
                                 str(folder / 'mock.c'), '-lm'], capture_output=True, text=True)
        if result.returncode:
            raise RuntimeError(result.stderr)

    def start(self, **options):
        process = subprocess.Popen([str(self.binary), 'MOCK'], stdin=subprocess.PIPE,
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                   bufsize=0,
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

    def hold(self, process):
        self.expect_line(process.stdout, b'ready\n')
        for button in range(3):
            process.stdin.write(f'button {button} 1\n'.encode())
            process.stdin.flush()
            self.expect_line(process.stdout, b'ok\n')

    def assert_released(self, log):
        self.assertIn(b'delivered 7\n', log)  # All three actually reached the mock server.
        for button in range(0x110, 0x113):
            self.assertIn(f'button {button} 0\n'.encode(), log)
        self.assertIn(b'delivered 0\n', log)
        self.assertIn(b'destroy 0\ndisconnect 0\n', log)

    def test_signals_release_while_stdin_open_or_partial(self):
        for sig in (signal.SIGTERM, signal.SIGINT, signal.SIGHUP):
            for partial in (b'', b'button 0'):
                with self.subTest(signal=sig, partial=partial):
                    process = self.start()
                    self.hold(process)
                    process.stdin.write(partial)
                    process.stdin.flush()
                    process.send_signal(sig)
                    process.wait(timeout=3)  # stdin remains open during this wait.
                    out, log = process.communicate(timeout=3)
                    self.assertEqual(process.returncode, 128 + sig)
                    self.assertEqual(out, b'')
                    self.assert_released(log)

    def test_eof_releases_and_succeeds(self):
        process = self.start()
        self.hold(process)
        out, log = process.communicate(timeout=3)
        self.assertEqual(process.returncode, 0, log)
        self.assertEqual(out, b'')
        self.assert_released(log)

    def test_invalid_commands_release_without_acknowledgement(self):
        for command in (b'bad\n', b'button 3 1\n', b'button 0 2\n',
                        b'button 0 1 extra\n', b'abs 2 0 2 2\n',
                        b'scroll nan 1\n', b'scroll 1 inf\n',
                        b'x' * 300 + b'\n', b'button\x00 0 1\n'):
            with self.subTest(command=command):
                process = self.start()
                self.hold(process)
                out, log = process.communicate(command, timeout=3)
                self.assertEqual(process.returncode, 2, log)
                self.assertEqual(out, b'')
                self.assertIn(b'invalid pointer command', log)
                self.assert_released(log)

    def test_startup_failures_clean_up_without_ready(self):
        for options in ({'FAIL_AT': 1}, {'FAIL_AT': 2}, {'FAIL_AT': 3},
                        {'MISSING_OUTPUT': 1}, {'NO_POINTER': 1}, {'DROP_AT': 1}):
            with self.subTest(options=options):
                process = self.start(**options)
                out, log = process.communicate(timeout=3)
                self.assertEqual(process.returncode, 2, log)
                self.assertEqual(out, b'')
                self.assertIn(b'disconnect 0\n', log)

    def test_command_protocol_error_has_no_ok(self):
        process = self.start(FAIL_AT=4)
        out, log = process.communicate(b'button 0 1\n', timeout=3)
        self.assertEqual(process.returncode, 2, log)
        self.assertEqual(out, b'ready\n')
        self.assertIn(b'Wayland command failed', log)
        self.assertIn(b'button 272 0\n', log)
        self.assertIn(b'disconnect', log)

    def test_idle_disconnect_exits_with_stdin_open(self):
        process = self.start(DROP_AT=3)
        self.expect_line(process.stdout, b'ready\n')
        process.wait(timeout=3)
        out, log = process.communicate(timeout=3)
        self.assertEqual(process.returncode, 2, log)
        self.assertEqual(out, b'')
        self.assertIn(b'Wayland disconnected', log)

    def test_signal_interrupts_stalled_sync(self):
        for sig in (signal.SIGTERM, signal.SIGINT, signal.SIGHUP):
            with self.subTest(signal=sig):
                process = self.start(STALL_AT=1)
                self.expect_line(process.stderr, b'sync 1\n')
                started = time.monotonic()
                process.send_signal(sig)
                out, log = process.communicate(timeout=3)
                self.assertEqual(process.returncode, 128 + sig, log)
                self.assertEqual(out, b'')
                self.assertLess(time.monotonic() - started, 1.5)
                self.assertIn(b'disconnect 0\n', log)

    def test_stalled_cleanup_is_bounded_and_releases_before_wait(self):
        process = self.start(STALL_AT=7)
        self.hold(process)
        started = time.monotonic()
        out, log = process.communicate(timeout=3)
        self.assertEqual(process.returncode, 2, log)
        self.assertEqual(out, b'')
        self.assertLess(time.monotonic() - started, 2)
        self.assert_released(log)

    def test_signal_during_stalled_command_releases_held_buttons(self):
        for sig in (signal.SIGTERM, signal.SIGINT, signal.SIGHUP):
            with self.subTest(signal=sig):
                process = self.start(STALL_AT=7)
                self.hold(process)
                process.stdin.write(b'abs 1 1 10 10\n')
                process.stdin.flush()
                prefix = b''
                deadline = time.monotonic() + 3
                while b'sync 7\n' not in prefix:
                    remaining = deadline - time.monotonic()
                    self.assertGreater(remaining, 0)
                    self.assertTrue(select.select([process.stderr], [], [], remaining)[0])
                    chunk = os.read(process.stderr.fileno(), 4096)
                    self.assertTrue(chunk, 'helper exited before entering sync')
                    prefix += chunk
                process.send_signal(sig)
                process.wait(timeout=3)  # No EOF to help the signal path.
                out, log = process.communicate(timeout=3)
                self.assertEqual(process.returncode, 128 + sig, log)
                self.assertEqual(out, b'')
                self.assert_released(prefix + log)

    def test_stalled_command_is_nonzero_without_ok(self):
        process = self.start(STALL_AT=4)
        out, log = process.communicate(b'button 0 1\n', timeout=3)
        self.assertEqual(process.returncode, 2, log)
        self.assertEqual(out, b'ready\n')
        self.assertIn(b'button 272 0\n', log)
        self.assertIn(b'destroy 0\ndisconnect 0\n', log)

    def assert_release_attempted(self, log):
        # Delivery cannot be confirmed once the connection is gone, but every
        # held button must still be released before the helper exits.
        for button in range(0x110, 0x113):
            self.assertIn(f'button {button} 0\n'.encode(), log)

    def test_disconnect_while_buttons_held_releases_them(self):
        # The compositor drops after the last held command; stdin stays open so
        # the idle read loop must notice the closed connection itself.
        process = self.start(DROP_AT=6)
        self.hold(process)
        process.wait(timeout=3)
        out, log = process.communicate(timeout=3)
        self.assertEqual(process.returncode, 2, log)
        self.assertEqual(out, b'')
        self.assertIn(b'Wayland disconnected', log)
        self.assert_release_attempted(log)

    def test_compositor_error_releases_all_held_buttons(self):
        # Unlike FAIL_AT=4 (one button), all three buttons are held when the
        # sync fails, so every held button must be released on the error path.
        process = self.start(FAIL_AT=7)
        self.hold(process)
        out, log = process.communicate(b'abs 1 1 10 10\n', timeout=3)
        self.assertEqual(process.returncode, 2, log)
        self.assertEqual(out, b'')
        self.assertIn(b'Wayland command failed', log)
        self.assert_release_attempted(log)


if __name__ == '__main__':
    unittest.main()
