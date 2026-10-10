// Opt-in native entry demo shapes (pure geometry). No fills/text/rim/backend.
// Owned by CommandCode (C34); Codex owns indicator.c integration. Default OFF.
//
// All shapes stay inside a 320x66 logical surface. Fully-progressed (progress>=1)
// geometry is exactly the final capsule at (ENTRANCE_PILL_X, ENTRANCE_PILL_Y).
// Callers clamp a narrower pill width externally; this header only draws.
#ifndef ENTRANCE_H
#define ENTRANCE_H

#include <cairo.h>
#include <math.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

#define ENTRANCE_SURFACE_W 320.0
#define ENTRANCE_SURFACE_H 66.0
#define ENTRANCE_PILL_X 16.0
#define ENTRANCE_PILL_Y 16.0
#define ENTRANCE_PILL_W 288.0
#define ENTRANCE_PILL_H 38.0
#define ENTRANCE_DURATION_MS 1000.0

#define ENTRANCE_MODE_STATIC 0
#define ENTRANCE_MODE_DROP 1   // small protrusion at output top, neck narrows/detaches
#define ENTRANCE_MODE_SHEET 2  // pill-wide sheet protrudes from top, then gap, then settles

static inline double entrance_clamp01(double v) { return v < 0.0 ? 0.0 : (v > 1.0 ? 1.0 : v); }

// cubic-out easing for a 0..1 time fraction
static inline double entrance_ease(double t) {
  t = entrance_clamp01(t);
  return 1.0 - pow(1.0 - t, 3.0);
}

// eased progress for elapsed milliseconds against ENTRANCE_DURATION_MS
static inline double entrance_progress_ms(double elapsed_ms) {
  return entrance_ease(elapsed_ms / ENTRANCE_DURATION_MS);
}

// one sub-path: capsule/rounded box, radius clamped to half the smaller side
static inline void entrance_rounded(cairo_t *cr, double x, double y, double w, double h, double r) {
  if (w <= 0.0 || h <= 0.0) return;
  if (r > w * 0.5) r = w * 0.5;
  if (r > h * 0.5) r = h * 0.5;
  if (r < 0.0) r = 0.0;
  cairo_new_sub_path(cr);
  cairo_arc(cr, x + w - r, y + r, r, -M_PI / 2.0, 0.0);
  cairo_arc(cr, x + w - r, y + h - r, r, 0.0, M_PI / 2.0);
  cairo_arc(cr, x + r, y + h - r, r, M_PI / 2.0, M_PI);
  cairo_arc(cr, x + r, y + r, r, M_PI, 3.0 * M_PI / 2.0);
  cairo_close_path(cr);
}

// Builds the union of the growing pill and a top bridge into the current path.
// The pill itself grows/protrudes from the top: at progress 0 only a 2px
// protrusion touches y0 (no full pill mid-air at py). A bridge from y0 stays
// attached (overlapping the pill's upper half) while progress < 0.75, then a gap
// opens and only the pill settles to the final capsule at progress 1.
static inline void entrance_shape(cairo_t *cr, double px, double py, double pw, double ph,
                                  double progress, int mode) {
  progress = entrance_clamp01(progress);
  if (mode == ENTRANCE_MODE_STATIC || progress >= 1.0) {
    entrance_rounded(cr, px, py, pw, ph, ph * 0.5);   // exact final capsule
    return;
  }
  const double p = progress;
  const double y = py * p;                            // descends 0 -> py
  const double h = 2.0 + (ph - 2.0) * p;              // grows 2 -> ph
  const double w = (mode == ENTRANCE_MODE_DROP) ? pw * (0.2 + 0.8 * p) : pw;
  const double x = px + (pw - w) * 0.5;               // centred
  entrance_rounded(cr, x, y, w, h, h * 0.5);

  const double bridge_w = (mode == ENTRANCE_MODE_DROP) ? fmax(2.0, w * 0.25) : w;
  double bridge_bottom;
  if (p < 0.75)
    bridge_bottom = y + h * 0.5;                      // inside the pill's upper half
  else
    bridge_bottom = (y + h * 0.5) * (1.0 - 1.3 * (p - 0.75) / 0.25);
  if (bridge_bottom > 0.5) {
    const double bx = px + (pw - bridge_w) * 0.5;
    const double r = fmin(bridge_w * 0.5, bridge_bottom * 0.5);
    entrance_rounded(cr, bx, 0.0, bridge_w, bridge_bottom, r);
  }
}

#endif  // ENTRANCE_H
