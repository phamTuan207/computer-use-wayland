// Output-bound Wayland pointer. Commands are internal to cu.py, not a shell.
#define _POSIX_C_SOURCE 200809L
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <ctype.h>
#include <errno.h>
#include <limits.h>
#include <math.h>
#include <poll.h>
#include <signal.h>
#include <unistd.h>
#include <wayland-client.h>
#include "pointer-protocol.h"

static struct zwlr_virtual_pointer_manager_v1 *manager;
static struct wl_seat *seat;
static struct wl_output *selected;
static const char *wanted;
static unsigned manager_version;
static volatile sig_atomic_t stopped;
static void stop(int sig) { stopped = sig; }
static int end_of_command(const char *line, int used) {
  if (!used) return 0;
  while (isspace((unsigned char)line[used])) used++;
  return !line[used];
}
// Poll both descriptors so an idle stdin cannot hide a signal or disconnect.
// Return 1 for a line, 0 for EOF, -1 for an error, -2 for a signal.
static int read_command(struct wl_display *display, char *line, size_t size) {
  size_t used = 0;
  while (!stopped) {
    struct pollfd fds[2] = {
      {.fd=STDIN_FILENO,.events=POLLIN},
      {.fd=wl_display_get_fd(display),.events=POLLIN}
    };
    // A bounded wait also covers a signal arriving just before poll().
    int rc = poll(fds, 2, 100);
    if (rc < 0) {
      if (errno == EINTR) continue;
      perror("pointer poll"); return -1;
    }
    if (stopped) break;
    if (fds[1].revents & (POLLERR|POLLHUP|POLLNVAL)) {
      fprintf(stderr,"Wayland disconnected\n"); return -1;
    }
    if ((fds[1].revents & POLLIN) && wl_display_dispatch(display) < 0) {
      fprintf(stderr,"Wayland dispatch failed\n"); return -1;
    }
    if (fds[0].revents & (POLLERR|POLLNVAL)) {
      fprintf(stderr,"pointer input failed\n"); return -1;
    }
    if (!(fds[0].revents & (POLLIN|POLLHUP))) continue;
    char ch;
    ssize_t n = read(STDIN_FILENO, &ch, 1);
    if (n < 0) {
      if (errno == EINTR) continue;
      perror("pointer read"); return -1;
    }
    if (!n) { line[used] = '\0'; return used ? 1 : 0; }
    if (ch == '\n') { line[used] = '\0'; return 1; }
    if (!ch || used == size - 1) {
      fprintf(stderr,"invalid pointer command\n"); return -1;
    }
    line[used++] = ch;
  }
  return -2;
}
static uint32_t stamp(void) {
  struct timespec t; clock_gettime(CLOCK_MONOTONIC, &t);
  return (uint32_t)(t.tv_sec * 1000 + t.tv_nsec / 1000000);
}
static void synced(void *data, struct wl_callback *callback, uint32_t serial) {
  (void)callback;(void)serial; *(int *)data = 1;
}
static const struct wl_callback_listener sync_listener = {.done=synced};
// wl_display_roundtrip() can wait forever. Use the same sync request with a
// bounded, interruptible wait; cleanup gets its own one-second release window.
static int sync_display(struct wl_display *display, int cleanup) {
  if (wl_display_get_error(display)) return -1;
  int complete = 0, result = -1;
  uint32_t started = stamp();
  struct wl_callback *callback = wl_display_sync(display);
  if (!callback) return -1;
  if (wl_callback_add_listener(callback,&sync_listener,&complete) < 0) goto finish;
  while (cleanup || !stopped) {
    if (wl_display_dispatch_pending(display) < 0) break;
    if (complete) { result = 0; break; }
    uint32_t elapsed = stamp() - started;
    if (elapsed >= 1000) { errno = ETIMEDOUT; break; }
    if (wl_display_prepare_read(display) < 0) continue;
    int flushed = wl_display_flush(display);
    if (flushed < 0 && errno != EAGAIN) {
      wl_display_cancel_read(display); break;
    }
    struct pollfd fd = {.fd=wl_display_get_fd(display),
      .events=POLLIN | (flushed < 0 ? POLLOUT : 0)};
    int rc = poll(&fd,1,(int)(1000-elapsed));
    if (rc <= 0 || (fd.revents & (POLLERR|POLLHUP|POLLNVAL))) {
      wl_display_cancel_read(display);
      if (rc < 0 && errno == EINTR) continue;
      if (!rc) errno = ETIMEDOUT;
      break;
    }
    if (fd.revents & POLLIN) {
      if (wl_display_read_events(display) < 0) break;
    } else wl_display_cancel_read(display);
  }
finish:
  wl_callback_destroy(callback);
  return result;
}
static void geometry(void *d, struct wl_output *o, int32_t x, int32_t y,
    int32_t pw, int32_t ph, int32_t s, const char *m, const char *model, int32_t t) {
  (void)d;(void)o;(void)x;(void)y;(void)pw;(void)ph;(void)s;(void)m;(void)model;(void)t;
}
static void mode(void *d, struct wl_output *o, uint32_t f, int32_t w, int32_t h, int32_t r) {
  (void)d;(void)o;(void)f;(void)w;(void)h;(void)r;
}
static void done(void *d, struct wl_output *o) {(void)d;(void)o;}
static void scale(void *d, struct wl_output *o, int32_t s) {(void)d;(void)o;(void)s;}
static void name(void *d, struct wl_output *o, const char *n) {
  (void)d; if (!strcmp(wanted, n)) selected = o;
}
static void description(void *d, struct wl_output *o, const char *n) {(void)d;(void)o;(void)n;}
static const struct wl_output_listener output_listener = {
  .geometry=geometry,.mode=mode,.done=done,.scale=scale,.name=name,.description=description
};
static void global(void *d, struct wl_registry *r, uint32_t id, const char *i, uint32_t v) {
  (void)d;
  if (!strcmp(i, zwlr_virtual_pointer_manager_v1_interface.name)) {
    manager_version = v < 2 ? v : 2;
    manager = wl_registry_bind(r, id, &zwlr_virtual_pointer_manager_v1_interface, manager_version);
  } else if (!strcmp(i, wl_seat_interface.name) && !seat) {
    seat = wl_registry_bind(r, id, &wl_seat_interface, 1);
  } else if (!strcmp(i, wl_output_interface.name) && v >= 4) {
    struct wl_output *o = wl_registry_bind(r, id, &wl_output_interface, 4);
    wl_output_add_listener(o, &output_listener, NULL);
  }
}
static void removed(void *d, struct wl_registry *r, uint32_t id) {(void)d;(void)r;(void)id;}
static const struct wl_registry_listener listener = {.global=global,.global_remove=removed};
int main(int argc, char **argv) {
  if (argc != 2) {fprintf(stderr,"output name required\n");return 2;}
  struct sigaction action = {.sa_handler=stop};
  sigemptyset(&action.sa_mask);
  if (sigaction(SIGTERM,&action,NULL) < 0 ||
      sigaction(SIGINT,&action,NULL) < 0 ||
      sigaction(SIGHUP,&action,NULL) < 0) {
    perror("pointer signal setup"); return 2;
  }
  // Broken stdout must also take the normal button-release path.
  action.sa_handler = SIG_IGN;
  if (sigaction(SIGPIPE,&action,NULL) < 0) {
    perror("pointer signal setup"); return 2;
  }
  wanted = argv[1];
  struct wl_display *display = wl_display_connect(NULL);
  if (!display) {fprintf(stderr,"Wayland unavailable\n");return 2;}
  int status = 2, held[3] = {0};
  struct zwlr_virtual_pointer_v1 *p = NULL;
  struct wl_registry *registry = wl_display_get_registry(display);
  if (!registry || wl_registry_add_listener(registry,&listener,NULL) < 0 ||
      sync_display(display,0) < 0 || stopped ||
      sync_display(display,0) < 0 || stopped) {
    fprintf(stderr,"Wayland discovery failed\n"); goto cleanup;
  }
  if (!manager || manager_version < 2 || !selected) {
    fprintf(stderr,"output-bound pointer v2 / named output unavailable\n");goto cleanup;
  }
  p = zwlr_virtual_pointer_manager_v1_create_virtual_pointer_with_output(manager,seat,selected);
  if (!p || sync_display(display,0) < 0 || stopped) {
    fprintf(stderr,"Wayland pointer startup failed\n"); goto cleanup;
  }
  char line[256]; unsigned x,y,w,h,button,down; double dx,dy;
  if (puts("ready") == EOF || fflush(stdout) == EOF) goto cleanup;
  status = 0;
  while (!stopped) {
    int rc = read_command(display,line,sizeof line), used = 0;
    if (rc <= 0) { if (rc == -1) status = 2; break; }
    if (stopped) break;
    if (sscanf(line,"abs %u %u %u %u %n",&x,&y,&w,&h,&used)==4 &&
        end_of_command(line,used) && w && h && x<w && y<h) {
      zwlr_virtual_pointer_v1_motion_absolute(p,stamp(),x,y,w,h);
    } else if ((used=0,sscanf(line,"button %u %u %n",&button,&down,&used))==2 &&
        end_of_command(line,used) && button<3 && down<2) {
      zwlr_virtual_pointer_v1_button(p,stamp(),0x110+button,down);held[button]=down;
    } else if ((used=0,sscanf(line,"scroll %lf %lf %n",&dx,&dy,&used))==2 &&
        end_of_command(line,used) && isfinite(dx) && isfinite(dy) &&
        fabs(dx) <= INT_MAX/256.0 && fabs(dy) <= INT_MAX/256.0) {
      zwlr_virtual_pointer_v1_axis_source(p,WL_POINTER_AXIS_SOURCE_WHEEL);
      // Wheel source needs discrete detents as well as continuous distance.
      // Firefox/Zen can ignore wheel events lacking discrete information.
      int sy=(int)(dy/15.0), sx=(int)(dx/15.0);
      if (dy && !sy) sy=dy>0 ? 1 : -1;
      if (dx && !sx) sx=dx>0 ? 1 : -1;
      if (dy) zwlr_virtual_pointer_v1_axis_discrete(p,stamp(),WL_POINTER_AXIS_VERTICAL_SCROLL,wl_fixed_from_double(dy),sy);
      if (dx) zwlr_virtual_pointer_v1_axis_discrete(p,stamp(),WL_POINTER_AXIS_HORIZONTAL_SCROLL,wl_fixed_from_double(dx),sx);
    } else {fprintf(stderr,"invalid pointer command\n");status=2;break;}
    zwlr_virtual_pointer_v1_frame(p);
    if (sync_display(display,0)<0) {
      fprintf(stderr,"Wayland command failed\n");status=2;break;
    }
    if (stopped) break;
    if (puts("ok") == EOF || fflush(stdout) == EOF) {status=2;break;}
  }
cleanup:
  if (p) {
    for (unsigned b=0;b<3;b++) if (held[b])
      zwlr_virtual_pointer_v1_button(p,stamp(),0x110+b,0);
    zwlr_virtual_pointer_v1_frame(p);
    // Flush releases first, then confirm delivery within the cleanup deadline.
    if (wl_display_flush(display) < 0 && errno != EAGAIN) status=2;
    if (!wl_display_get_error(display) && sync_display(display,1) < 0) status=2;
    zwlr_virtual_pointer_v1_destroy(p);
  }
  if (manager) zwlr_virtual_pointer_manager_v1_destroy(manager);
  if (seat) wl_seat_destroy(seat);
  if (selected) wl_output_destroy(selected);
  if (registry) wl_registry_destroy(registry);
  if (!wl_display_get_error(display) && wl_display_flush(display) < 0 && errno != EAGAIN)
    status=2;
  wl_display_disconnect(display);
  return stopped ? 128 + stopped : status;
}
