#ifndef CU_INDICATOR_STATE_H
#define CU_INDICATOR_STATE_H

static inline int indicator_set_hidden(int *hidden, int desired_hidden) {
  if (*hidden == desired_hidden) return 0;
  *hidden = desired_hidden;
  return 1;
}

static inline int indicator_needs_present(int pending, int frame_pending) {
  return pending && !frame_pending;
}

#endif
