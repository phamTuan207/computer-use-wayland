// Output-bound Wayland pointer. Commands are internal to cu.py, not a shell.
#define _POSIX_C_SOURCE 200809L
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <wayland-client.h>
#include "pointer-protocol.h"

static struct zwlr_virtual_pointer_manager_v1 *manager;
static struct wl_seat *seat;
static struct wl_output *selected;
static const char *wanted;
static unsigned manager_version;
static uint32_t stamp(void) {
  struct timespec t; clock_gettime(CLOCK_MONOTONIC, &t);
  return (uint32_t)(t.tv_sec * 1000 + t.tv_nsec / 1000000);
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
  wanted = argv[1];
  struct wl_display *display = wl_display_connect(NULL);
  if (!display) {fprintf(stderr,"Wayland unavailable\n");return 2;}
  struct wl_registry *registry = wl_display_get_registry(display);
  wl_registry_add_listener(registry,&listener,NULL);
  wl_display_roundtrip(display); wl_display_roundtrip(display);
  if (!manager || manager_version < 2 || !selected) {
    fprintf(stderr,"output-bound pointer v2 / named output unavailable\n");return 2;
  }
  struct zwlr_virtual_pointer_v1 *p =
    zwlr_virtual_pointer_manager_v1_create_virtual_pointer_with_output(manager,seat,selected);
  wl_display_roundtrip(display);
  char line[256]; unsigned x,y,w,h,button,down; double dx,dy; int held[3]={0};
  puts("ready");fflush(stdout);
  while (fgets(line,sizeof line,stdin)) {
    if (sscanf(line,"abs %u %u %u %u",&x,&y,&w,&h)==4 && w && h && x<w && y<h) {
      zwlr_virtual_pointer_v1_motion_absolute(p,stamp(),x,y,w,h);
    } else if (sscanf(line,"button %u %u",&button,&down)==2 && button<3 && down<2) {
      zwlr_virtual_pointer_v1_button(p,stamp(),0x110+button,down);held[button]=down;
    } else if (sscanf(line,"scroll %lf %lf",&dx,&dy)==2) {
      zwlr_virtual_pointer_v1_axis_source(p,WL_POINTER_AXIS_SOURCE_WHEEL);
      // Wheel source needs discrete detents as well as continuous distance.
      // Firefox/Zen can ignore wheel events lacking discrete information.
      int sy=(int)(dy/15.0), sx=(int)(dx/15.0);
      if (dy && !sy) sy=dy>0 ? 1 : -1;
      if (dx && !sx) sx=dx>0 ? 1 : -1;
      if (dy) zwlr_virtual_pointer_v1_axis_discrete(p,stamp(),WL_POINTER_AXIS_VERTICAL_SCROLL,wl_fixed_from_double(dy),sy);
      if (dx) zwlr_virtual_pointer_v1_axis_discrete(p,stamp(),WL_POINTER_AXIS_HORIZONTAL_SCROLL,wl_fixed_from_double(dx),sx);
    } else {fprintf(stderr,"invalid pointer command\n");break;}
    zwlr_virtual_pointer_v1_frame(p);
    if (wl_display_roundtrip(display)<0) break;
    puts("ok");fflush(stdout);
  }
  for (unsigned b=0;b<3;b++) if (held[b]) zwlr_virtual_pointer_v1_button(p,stamp(),0x110+b,0);
  zwlr_virtual_pointer_v1_frame(p);wl_display_roundtrip(display);
  zwlr_virtual_pointer_v1_destroy(p);wl_display_roundtrip(display);wl_display_disconnect(display);
  return 0;
}
