// Session-owned, click-through glass badge. stdin EOF is ownership loss.
#define _POSIX_C_SOURCE 200809L
#include <gtk/gtk.h>
#include <gtk4-layer-shell.h>
#include <gdk/wayland/gdkwayland.h>
#include <glib-unix.h>
#include <wayland-client.h>
#include "presentation-protocol.h"
#include "background-effect-protocol.h"
#include <math.h>
#include <signal.h>
#include <stdio.h>
#include <string.h>
#include <unistd.h>
#include <sys/prctl.h>

typedef struct {
  GtkWindow *window;
  GtkWidget *area;
  GdkMonitor *monitor;
  struct wp_presentation_feedback *frame;
  struct ext_background_effect_surface_v1 *glass;
  int pending;
} Output;
static GPtrArray *outputs;
static GMainLoop *loop;
static int hidden, busy, remaining;
static char acknowledgement[16];
static guint timeout_id;
static struct wp_presentation *presentation;
static struct ext_background_effect_manager_v1 *effects;
static struct wl_compositor *compositor;
static uint32_t effect_caps;
static int failed;
static int closing;

static void reply(void) {
  if (remaining) return;
  busy=0;
  if (timeout_id) { g_source_remove(timeout_id); timeout_id=0; }
  puts(acknowledgement); fflush(stdout);
  if (closing) g_main_loop_quit(loop);
}
static void framed(void *data, struct wp_presentation_feedback *callback,
                   uint32_t hi,uint32_t lo,uint32_t ns,uint32_t refresh,
                   uint32_t seq_hi,uint32_t seq_lo,uint32_t flags) {
  (void)hi;(void)lo;(void)ns;(void)refresh;(void)seq_hi;(void)seq_lo;(void)flags;
  Output *output=data;
  wp_presentation_feedback_destroy(callback); output->frame=NULL;
  if (output->pending) { output->pending=0; remaining--; }
  reply();
}
static void synchronized(void *data,struct wp_presentation_feedback *feedback,struct wl_output *output) {
  (void)data;(void)feedback;(void)output;
}
static void discarded(void *data,struct wp_presentation_feedback *feedback) {
  Output *output=data;wp_presentation_feedback_destroy(feedback);output->frame=NULL;
  failed=1;fputs("indicator buffer was not presented\n",stderr);g_main_loop_quit(loop);
}
static const struct wp_presentation_feedback_listener frame_listener={
  .sync_output=synchronized,.presented=framed,.discarded=discarded};
static void glass_region(Output *output) {
  if (!output->glass) return;
  if (hidden) {
    // Clearing pixels alone leaves compositor blur behind in screenshots.
    ext_background_effect_surface_v1_set_blur_region(output->glass,NULL);
    return;
  }
  int width=gtk_widget_get_width(output->area);
  if (width<=0) {
    failed=1;fputs("indicator output has no drawable width\n",stderr);
    g_main_loop_quit(loop);return;
  }
  double pw=fmax(1,fmin(320,width-32.0)),px=(width-pw)/2.0;
  struct wl_region *region=wl_compositor_create_region(compositor);
  if (!region) {
    failed=1;fputs("indicator blur region allocation failed\n",stderr);
    g_main_loop_quit(loop);return;
  }
  // Rounded scanlines keep the blur inside the pill, not its bounding box
  // or the full-output transparent surface. Coordinates are surface-local.
  double radius=fmin(22,pw/2);
  for (int row=0;row<44;row++) {
    double dy=fmax(0,radius-fmin(row+.5,44-row-.5));
    double inset=radius-sqrt(fmax(0,radius*radius-dy*dy));
    int left=(int)ceil(px+inset),right=(int)floor(px+pw-inset);
    if (right>left) wl_region_add(region,left,16+row,right-left,1);
  }
  ext_background_effect_surface_v1_set_blur_region(output->glass,region);
  wl_region_destroy(region);
}
static void painted(GdkFrameClock *clock, gpointer data) {
  (void)clock;
  Output *output=data;
  if (!output->pending || output->frame) return;
  GdkSurface *surface=gtk_native_get_surface(GTK_NATIVE(output->window));
  struct wl_surface *wl=gdk_wayland_surface_get_wl_surface(surface);
  glass_region(output);
  if (failed) return;
  // Recommit GTK's fresh buffer with damage and require actual presentation,
  // not merely a frame-scheduling callback or a server queue sync.
  output->frame=wp_presentation_feedback(presentation,wl);
  wp_presentation_feedback_add_listener(output->frame,&frame_listener,output);
  wl_surface_damage(wl,0,0,G_MAXINT,G_MAXINT);
  wl_surface_commit(wl);
  gdk_display_flush(gdk_surface_get_display(surface));
}
static gboolean expired(gpointer data) {
  (void)data;
  timeout_id=0;
  failed=1;
  fputs("indicator frame acknowledgement timed out\n",stderr);
  g_main_loop_quit(loop);
  return G_SOURCE_REMOVE;
}
static void redraw(const char *ack) {
  if (busy) { fputs("overlapping indicator command\n",stderr);g_main_loop_quit(loop);return; }
  busy=1;remaining=(int)outputs->len;
  snprintf(acknowledgement,sizeof acknowledgement,"%s",ack);
  timeout_id=g_timeout_add(2000,expired,NULL);
  for (guint i=0;i<outputs->len;i++) {
    Output *output=g_ptr_array_index(outputs,i);
    output->pending=1;
    gtk_widget_queue_draw(output->area);
  }
}
static void rounded(cairo_t *cr,double x,double y,double w,double h,double radius) {
  radius=fmin(radius,fmin(w,h)/2);
  cairo_new_sub_path(cr);
  cairo_arc(cr,x+w-radius,y+radius,radius,-G_PI/2,0);
  cairo_arc(cr,x+w-radius,y+h-radius,radius,0,G_PI/2);
  cairo_arc(cr,x+radius,y+h-radius,radius,G_PI/2,G_PI);
  cairo_arc(cr,x+radius,y+radius,radius,G_PI,3*G_PI/2);
  cairo_close_path(cr);
}
static void draw(GtkDrawingArea *area, cairo_t *cr, int width, int height, gpointer data) {
  (void)area;(void)height;(void)data;
  cairo_set_operator(cr,CAIRO_OPERATOR_SOURCE);
  cairo_set_source_rgba(cr,0,0,0,0);cairo_paint(cr);
  cairo_set_operator(cr,CAIRO_OPERATOR_OVER);
  if (hidden) return;
  double pw=fmax(1,fmin(320,width-32.0)),px=(width-pw)/2.0,py=16,ph=44;
  int escape=pw>=300 && g_strcmp0(g_getenv("CU_ESCAPE_AVAILABLE"),"1")==0;
  // Restrained elevation; the compositor supplies the real backdrop blur.
  for (int ring=6;ring>=1;ring--) {
    rounded(cr,px-ring,py+2-ring,pw+2*ring,ph+2*ring,ph/2+ring);
    cairo_set_source_rgba(cr,0,0,0,.012);cairo_fill(cr);
  }
  rounded(cr,px+.5,py+.5,pw-1,ph-1,ph/2);
  cairo_set_source_rgba(cr,.055,.065,.08,.66);cairo_fill_preserve(cr);
  cairo_pattern_t *wash=cairo_pattern_create_linear(px,py,px+pw*.25,py+ph);
  cairo_pattern_add_color_stop_rgba(wash,0,1,1,1,.13);
  cairo_pattern_add_color_stop_rgba(wash,.45,1,1,1,.025);
  cairo_pattern_add_color_stop_rgba(wash,1,1,1,1,0);
  cairo_set_source(cr,wash);cairo_fill_preserve(cr);cairo_pattern_destroy(wash);
  cairo_pattern_t *rim=cairo_pattern_create_linear(px,py,px+pw*.12,py+ph);
  cairo_pattern_add_color_stop_rgba(rim,0,1,1,1,.55);
  cairo_pattern_add_color_stop_rgba(rim,.50,1,1,1,.12);
  cairo_pattern_add_color_stop_rgba(rim,1,1,1,1,.28);
  cairo_set_source(cr,rim);cairo_set_line_width(cr,1);cairo_stroke(cr);
  cairo_pattern_destroy(rim);
  cairo_set_source_rgb(cr,.20,.82,.88);
  cairo_arc(cr,px+22,py+ph/2,3,0,2*G_PI);cairo_fill(cr);
  cairo_set_source_rgb(cr,.96,.96,.97);
  cairo_select_font_face(cr,"sans-serif",CAIRO_FONT_SLANT_NORMAL,CAIRO_FONT_WEIGHT_NORMAL);
  cairo_set_font_size(cr,14);
  cairo_text_extents_t text;cairo_text_extents(cr,"Computer use active",&text);
  double available=fmax(1,pw-62-(escape?66:0));
  if (text.width>available) cairo_set_font_size(cr,14*available/text.width);
  cairo_move_to(cr,px+38,py+ph/2+5);
  cairo_show_text(cr,"Computer use active");
  if (escape) {
    cairo_set_source_rgba(cr,1,1,1,.10);cairo_set_line_width(cr,1);
    cairo_move_to(cr,px+pw-77,py+13);cairo_line_to(cr,px+pw-77,py+ph-13);cairo_stroke(cr);
    rounded(cr,px+pw-64,py+10,44,24,6);
    cairo_set_source_rgba(cr,1,1,1,.08);cairo_fill(cr);
    cairo_set_source_rgb(cr,.81,.84,.85);
    cairo_set_font_size(cr,12);
    cairo_text_extents_t esc;cairo_text_extents(cr,"Esc",&esc);
    cairo_move_to(cr,px+pw-42-esc.width/2,py+ph/2+4);cairo_show_text(cr,"Esc");
  }
}
static void mapped(GtkWidget *widget, gpointer data) {
  (void)data;
  GdkSurface *surface=gtk_native_get_surface(GTK_NATIVE(widget));
  cairo_region_t *empty=cairo_region_create();
  gdk_surface_set_input_region(surface,empty);cairo_region_destroy(empty);
}
static gboolean input(GIOChannel *channel, GIOCondition condition, gpointer data) {
  (void)data;
  if (condition&(G_IO_HUP|G_IO_ERR|G_IO_NVAL)) { g_main_loop_quit(loop);return G_SOURCE_REMOVE; }
  gchar *line=NULL;gsize length=0;
  GIOStatus status=g_io_channel_read_line(channel,&line,&length,NULL,NULL);
  if (status==G_IO_STATUS_AGAIN) return G_SOURCE_CONTINUE;
  if (status!=G_IO_STATUS_NORMAL || !line || length>256 || busy) {
    g_free(line);g_main_loop_quit(loop);return G_SOURCE_REMOVE;
  }
  g_strstrip(line);
  double x,y;char name[128],extra;
  if (!strcmp(line,"hide")) { hidden=1;redraw("hidden"); }
  else if (!strcmp(line,"show")) { hidden=0;redraw("visible"); }
  else if (sscanf(line,"move %127s %lf %lf %c",name,&x,&y,&extra)==3 &&
           isfinite(x) && isfinite(y) && x>=0 && y>=0) {
    int found=0;
    for (guint i=0;i<outputs->len;i++) {
      Output *output=g_ptr_array_index(outputs,i);
      const char *connector=gdk_monitor_get_connector(output->monitor);
      GdkRectangle geometry;gdk_monitor_get_geometry(output->monitor,&geometry);
      if (connector && !strcmp(name,connector) && x<geometry.width && y<geometry.height) found=1;
    }
    if (!found) { g_free(line);g_main_loop_quit(loop);return G_SOURCE_REMOVE; }
    // Legacy coordinate command remains valid, but never duplicates the cursor.
    puts("ok");fflush(stdout);
  } else { g_free(line);g_main_loop_quit(loop);return G_SOURCE_REMOVE; }
  g_free(line);return G_SOURCE_CONTINUE;
}
static gboolean stopped(gpointer data) { (void)data;g_main_loop_quit(loop);return G_SOURCE_REMOVE; }
static void changed(GListModel *model,guint position,guint removed,guint added,gpointer data) {
  (void)model;(void)position;(void)removed;(void)added;(void)data;
  failed=1;fputs("indicator monitor layout changed\n",stderr);g_main_loop_quit(loop);
}
static void capabilities(void *data,struct ext_background_effect_manager_v1 *manager,uint32_t flags) {
  (void)data;(void)manager;
  // A lost capability would make the advertised material misleading.
  if (outputs && outputs->len && !(flags&EXT_BACKGROUND_EFFECT_MANAGER_V1_CAPABILITY_BLUR)) {
    failed=1;fputs("indicator backdrop blur lost\n",stderr);g_main_loop_quit(loop);
  }
  effect_caps=flags;
}
static const struct ext_background_effect_manager_v1_listener effect_listener={.capabilities=capabilities};
static void global(void *data,struct wl_registry *registry,uint32_t name,const char *interface,uint32_t version) {
  (void)data;(void)version;
  if (!strcmp(interface,wp_presentation_interface.name))
    presentation=wl_registry_bind(registry,name,&wp_presentation_interface,1);
  else if (!strcmp(interface,wl_compositor_interface.name))
    compositor=wl_registry_bind(registry,name,&wl_compositor_interface,1);
  else if (!strcmp(interface,ext_background_effect_manager_v1_interface.name)) {
    effects=wl_registry_bind(registry,name,&ext_background_effect_manager_v1_interface,1);
    ext_background_effect_manager_v1_add_listener(effects,&effect_listener,NULL);
  }
}
static void removed(void *data,struct wl_registry *registry,uint32_t name) {
  (void)data;(void)registry;(void)name;
}
static const struct wl_registry_listener registry_listener={.global=global,.global_remove=removed};
int main(void) {
  pid_t parent=getppid();
  if (prctl(PR_SET_PDEATHSIG,SIGTERM)==-1 || getppid()!=parent) return 2;
  gtk_init();
  if (!gtk_layer_is_supported()) { fputs("layer shell unavailable\n",stderr);return 2; }
  loop=g_main_loop_new(NULL,FALSE);outputs=g_ptr_array_new_with_free_func(g_free);
  struct wl_display *display=gdk_wayland_display_get_wl_display(gdk_display_get_default());
  struct wl_registry *registry=wl_display_get_registry(display);
  wl_registry_add_listener(registry,&registry_listener,NULL);
  if (wl_display_roundtrip(display)<0 || !presentation) {
    fputs("presentation feedback unavailable\n",stderr);return 2;
  }
  if (wl_display_roundtrip(display)<0 || !compositor || !effects ||
      !(effect_caps&EXT_BACKGROUND_EFFECT_MANAGER_V1_CAPABILITY_BLUR)) {
    fputs("indicator backdrop blur unavailable\n",stderr);return 2;
  }
  GtkCssProvider *css=gtk_css_provider_new();
  gtk_css_provider_load_from_string(css,"window.cu-indicator { background: transparent; box-shadow: none; }");
  gtk_style_context_add_provider_for_display(gdk_display_get_default(),GTK_STYLE_PROVIDER(css),GTK_STYLE_PROVIDER_PRIORITY_APPLICATION);
  g_object_unref(css);
  GListModel *monitors=gdk_display_get_monitors(gdk_display_get_default());
  g_signal_connect(monitors,"items-changed",G_CALLBACK(changed),NULL);
  for (guint i=0;i<g_list_model_get_n_items(monitors);i++) {
    Output *output=g_new0(Output,1);
    output->monitor=g_list_model_get_item(monitors,i);
    output->window=GTK_WINDOW(gtk_window_new());
    gtk_layer_init_for_window(output->window);
    gtk_layer_set_namespace(output->window,"computer-use-indicator");
    gtk_layer_set_monitor(output->window,output->monitor);
    gtk_layer_set_layer(output->window,GTK_LAYER_SHELL_LAYER_OVERLAY);
    gtk_layer_set_keyboard_mode(output->window,GTK_LAYER_SHELL_KEYBOARD_MODE_NONE);
    // -1 reserves no space and ignores panel reservations for exact output coordinates.
    gtk_layer_set_exclusive_zone(output->window,-1);
    for (int edge=0;edge<4;edge++) gtk_layer_set_anchor(output->window,edge,TRUE);
    gtk_widget_add_css_class(GTK_WIDGET(output->window),"cu-indicator");
    output->area=gtk_drawing_area_new();
    gtk_drawing_area_set_draw_func(GTK_DRAWING_AREA(output->area),draw,output,NULL);
    gtk_window_set_child(output->window,output->area);
    g_signal_connect(output->window,"map",G_CALLBACK(mapped),NULL);
    gtk_widget_realize(GTK_WIDGET(output->window));
    GdkSurface *surface=gtk_native_get_surface(GTK_NATIVE(output->window));
    output->glass=ext_background_effect_manager_v1_get_background_effect(effects,gdk_wayland_surface_get_wl_surface(surface));
    GdkFrameClock *clock=gtk_widget_get_frame_clock(GTK_WIDGET(output->window));
    g_signal_connect_after(clock,"after-paint",G_CALLBACK(painted),output);
    g_ptr_array_add(outputs,output);
    gtk_widget_set_visible(GTK_WIDGET(output->window),TRUE);
  }
  if (!outputs->len) return 2;
  GIOChannel *channel=g_io_channel_unix_new(STDIN_FILENO);
  g_io_channel_set_flags(channel,G_IO_FLAG_NONBLOCK,NULL);
  g_io_add_watch(channel,G_IO_IN|G_IO_HUP|G_IO_ERR,input,NULL);
  g_unix_signal_add(SIGTERM,stopped,NULL);g_unix_signal_add(SIGINT,stopped,NULL);
  g_unix_signal_add(SIGHUP,stopped,NULL);signal(SIGPIPE,SIG_IGN);
  redraw("ready");g_main_loop_run(loop);
  // Clear the buffer before unmapping: compositor close animations must fade
  // transparent pixels, not leave a badge in a post-session screenshot.
  closing=1;hidden=1;
  if (timeout_id) {g_source_remove(timeout_id);timeout_id=0;}
  for (guint i=0;i<outputs->len;i++) {
    Output *output=g_ptr_array_index(outputs,i);
    if (output->frame) {wp_presentation_feedback_destroy(output->frame);output->frame=NULL;}
    output->pending=0;
  }
  busy=0;redraw("closed");g_main_loop_run(loop);
  for (guint i=0;i<outputs->len;i++) {
    Output *output=g_ptr_array_index(outputs,i);
    if (output->frame) wp_presentation_feedback_destroy(output->frame);
    ext_background_effect_surface_v1_destroy(output->glass);
    gtk_window_destroy(output->window);g_object_unref(output->monitor);
  }
  gdk_display_sync(gdk_display_get_default());
  wp_presentation_destroy(presentation);wl_registry_destroy(registry);
  ext_background_effect_manager_v1_destroy(effects);wl_compositor_destroy(compositor);
  g_io_channel_unref(channel);g_ptr_array_free(outputs,TRUE);g_main_loop_unref(loop);
  return failed || timeout_id || busy ? 2 : 0;
}
