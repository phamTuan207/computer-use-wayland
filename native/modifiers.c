// Session-owned Wayland virtual keyboard modifier helper.
// Holds Ctrl/Shift/Alt/Super/AltGr for mouse actions without uinput/root.
// Protocol: zwp_virtual_keyboard_v1 (Purism SPC / wtype, MIT license).
#define _GNU_SOURCE
#define _POSIX_C_SOURCE 200809L
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <ctype.h>
#include <errno.h>
#include <poll.h>
#include <signal.h>
#include <unistd.h>
#include <sys/mman.h>
#include <sys/prctl.h>
#include <wayland-client.h>
#include <xkbcommon/xkbcommon.h>
#include "keyboard-protocol.h"

// XKB mask bits: Shift 1, Ctrl 4, Alt 8, Super 64, AltGr 128
#define ALLOWED_MODS (1U | 4U | 8U | 64U | 128U)

static struct zwp_virtual_keyboard_manager_v1 *manager;
static struct wl_seat *seat;
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
      {.fd = STDIN_FILENO, .events = POLLIN},
      {.fd = wl_display_get_fd(display), .events = POLLIN}
    };
    int rc = poll(fds, 2, 100);
    if (rc < 0) {
      if (errno == EINTR) continue;
      perror("modifiers poll");
      return -1;
    }
    if (stopped) break;
    if (fds[1].revents & (POLLERR | POLLHUP | POLLNVAL)) {
      fprintf(stderr, "Wayland disconnected\n");
      return -1;
    }
    if ((fds[1].revents & POLLIN) && wl_display_dispatch(display) < 0) {
      fprintf(stderr, "Wayland dispatch failed\n");
      return -1;
    }
    if (fds[0].revents & (POLLERR | POLLNVAL)) {
      fprintf(stderr, "modifiers input failed\n");
      return -1;
    }
    if (!(fds[0].revents & (POLLIN | POLLHUP))) continue;
    char ch;
    ssize_t n = read(STDIN_FILENO, &ch, 1);
    if (n < 0) {
      if (errno == EINTR) continue;
      perror("modifiers read");
      return -1;
    }
    if (!n) { line[used] = '\0'; return used ? 1 : 0; }
    if (ch == '\n') { line[used] = '\0'; return 1; }
    if (!ch || used == size - 1) {
      fprintf(stderr, "invalid modifiers command\n");
      return -1;
    }
    line[used++] = ch;
  }
  return -2;
}

static uint32_t stamp(void) {
  struct timespec t;
  clock_gettime(CLOCK_MONOTONIC, &t);
  return (uint32_t)(t.tv_sec * 1000 + t.tv_nsec / 1000000);
}

static void synced(void *data, struct wl_callback *callback, uint32_t serial) {
  (void)callback;
  (void)serial;
  *(int *)data = 1;
}

static const struct wl_callback_listener sync_listener = {.done = synced};

// Bounded sync wait (<= 1s timeout), interruptible by signals.
static int sync_display(struct wl_display *display, int cleanup) {
  if (wl_display_get_error(display)) return -1;
  int complete = 0, result = -1;
  uint32_t started = stamp();
  struct wl_callback *callback = wl_display_sync(display);
  if (!callback) return -1;
  if (wl_callback_add_listener(callback, &sync_listener, &complete) < 0) goto finish;
  while (cleanup || !stopped) {
    if (wl_display_dispatch_pending(display) < 0) break;
    if (complete) { result = 0; break; }
    uint32_t elapsed = stamp() - started;
    if (elapsed >= 1000) { errno = ETIMEDOUT; break; }
    if (wl_display_prepare_read(display) < 0) continue;
    int flushed = wl_display_flush(display);
    if (flushed < 0 && errno != EAGAIN) {
      wl_display_cancel_read(display);
      break;
    }
    struct pollfd fd = {
      .fd = wl_display_get_fd(display),
      .events = POLLIN | (flushed < 0 ? POLLOUT : 0)
    };
    int rc = poll(&fd, 1, (int)(1000 - elapsed));
    if (rc <= 0 || (fd.revents & (POLLERR | POLLHUP | POLLNVAL))) {
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

static void global(void *data, struct wl_registry *registry, uint32_t name, const char *interface, uint32_t version) {
  (void)data;
  (void)version;
  if (!strcmp(interface, zwp_virtual_keyboard_manager_v1_interface.name)) {
    manager = wl_registry_bind(registry, name, &zwp_virtual_keyboard_manager_v1_interface, 1);
  } else if (!strcmp(interface, wl_seat_interface.name) && !seat) {
    seat = wl_registry_bind(registry, name, &wl_seat_interface, 1);
  }
}

static void removed(void *data, struct wl_registry *registry, uint32_t name) {
  (void)data;
  (void)registry;
  (void)name;
}

static const struct wl_registry_listener listener = {.global = global, .global_remove = removed};

static int upload_keymap(struct zwp_virtual_keyboard_v1 *keyboard) {
  struct xkb_context *ctx = xkb_context_new(XKB_CONTEXT_NO_FLAGS);
  if (!ctx) {
    fprintf(stderr, "failed to create xkb context\n");
    return -1;
  }
  // Pin US layout + lv3:ralt_switch so modifier bit indices are deterministic:
  // Shift:0 (1), Ctrl:2 (4), Alt:3 (8), Super:6 (64), AltGr:7 (128).
  // lv3:ralt_switch binds ISO_Level3_Shift to RAlt so AltGr modifier (index 7)
  // is present in this virtual keyboard's own keymap without touching user layout.
  struct xkb_rule_names names = {
    .rules = "evdev",
    .model = "pc105",
    .layout = "us",
    .variant = "",
    .options = "lv3:ralt_switch"
  };
  struct xkb_keymap *km = xkb_keymap_new_from_names(ctx, &names, XKB_KEYMAP_COMPILE_NO_FLAGS);
  if (!km) {
    fprintf(stderr, "failed to compile pinned us+lv3:ralt_switch xkb keymap\n");
    xkb_context_unref(ctx);
    return -1;
  }
  char *km_str = xkb_keymap_get_as_string(km, XKB_KEYMAP_FORMAT_TEXT_V1);
  if (!km_str) {
    fprintf(stderr, "failed to serialize xkb keymap\n");
    xkb_keymap_unref(km);
    xkb_context_unref(ctx);
    return -1;
  }
  size_t km_len = strlen(km_str) + 1;
  int fd = memfd_create("cu_modifiers_keymap", MFD_CLOEXEC);
  if (fd < 0) {
    perror("memfd_create");
    free(km_str);
    xkb_keymap_unref(km);
    xkb_context_unref(ctx);
    return -1;
  }
  ssize_t written = write(fd, km_str, km_len);
  free(km_str);
  xkb_keymap_unref(km);
  xkb_context_unref(ctx);
  if (written != (ssize_t)km_len) {
    perror("write keymap to memfd");
    close(fd);
    return -1;
  }
  lseek(fd, 0, SEEK_SET);
  zwp_virtual_keyboard_v1_keymap(keyboard, 1 /* WL_KEYBOARD_KEYMAP_FORMAT_XKB_V1 */, fd, (uint32_t)km_len);
  close(fd);
  return 0;
}

int main(int argc, char **argv) {
  (void)argc;
  (void)argv;
  // Ensure child terminates if guardian/parent dies unexpectedly.
  // Check return value and verify parent hasn't already terminated (race avoidance).
  pid_t parent = getppid();
  if (prctl(PR_SET_PDEATHSIG, SIGTERM) < 0) {
    perror("modifiers prctl");
    return 2;
  }
  if (getppid() != parent) {
    return 2;
  }

  struct sigaction action = {.sa_handler = stop};
  sigemptyset(&action.sa_mask);
  if (sigaction(SIGTERM, &action, NULL) < 0 ||
      sigaction(SIGINT, &action, NULL) < 0 ||
      sigaction(SIGHUP, &action, NULL) < 0) {
    perror("modifiers signal setup");
    return 2;
  }
  action.sa_handler = SIG_IGN;
  if (sigaction(SIGPIPE, &action, NULL) < 0) {
    perror("modifiers signal setup");
    return 2;
  }

  struct wl_display *display = wl_display_connect(NULL);
  if (!display) {
    fprintf(stderr, "Wayland unavailable\n");
    return 2;
  }

  int status = 2;
  struct zwp_virtual_keyboard_v1 *keyboard = NULL;
  struct wl_registry *registry = wl_display_get_registry(display);
  if (!registry || wl_registry_add_listener(registry, &listener, NULL) < 0 ||
      sync_display(display, 0) < 0 || stopped ||
      sync_display(display, 0) < 0 || stopped) {
    fprintf(stderr, "Wayland discovery failed\n");
    goto cleanup;
  }

  if (!manager || !seat) {
    fprintf(stderr, "virtual keyboard manager or seat unavailable\n");
    goto cleanup;
  }

  keyboard = zwp_virtual_keyboard_manager_v1_create_virtual_keyboard(manager, seat);
  if (!keyboard || upload_keymap(keyboard) < 0 ||
      sync_display(display, 0) < 0 || stopped) {
    fprintf(stderr, "virtual keyboard initialization failed\n");
    goto cleanup;
  }

  char line[256];
  if (puts("ready") == EOF || fflush(stdout) == EOF) goto cleanup;
  status = 0;

  while (!stopped) {
    int rc = read_command(display, line, sizeof line), used = 0;
    if (rc <= 0) {
      if (rc == -1) status = 2;
      break;
    }
    if (stopped) break;
    uint32_t mask = 0;
    if (sscanf(line, "mods %u %n", &mask, &used) == 1 && end_of_command(line, used) &&
        (mask & ~ALLOWED_MODS) == 0) {
      zwp_virtual_keyboard_v1_modifiers(keyboard, mask, 0, 0, 0);
      if (sync_display(display, 0) < 0) {
        fprintf(stderr, "Wayland command failed\n");
        status = 2;
        break;
      }
      if (stopped) break;
      if (puts("ok") == EOF || fflush(stdout) == EOF) {
        status = 2;
        break;
      }
    } else {
      fprintf(stderr, "invalid modifiers command\n");
      status = 2;
      break;
    }
  }

cleanup:
  if (keyboard) {
    // Reset modifiers to 0 on exit, signal, or failure.
    zwp_virtual_keyboard_v1_modifiers(keyboard, 0, 0, 0, 0);
    if (wl_display_flush(display) < 0 && errno != EAGAIN) status = 2;
    if (!wl_display_get_error(display) && sync_display(display, 1) < 0) status = 2;
    zwp_virtual_keyboard_v1_destroy(keyboard);
  }
  if (manager) zwp_virtual_keyboard_manager_v1_destroy(manager);
  if (seat) wl_seat_destroy(seat);
  if (registry) wl_registry_destroy(registry);
  if (!wl_display_get_error(display) && wl_display_flush(display) < 0 && errno != EAGAIN)
    status = 2;
  wl_display_disconnect(display);
  return stopped ? 128 + stopped : status;
}
