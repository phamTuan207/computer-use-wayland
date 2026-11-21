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

/* Consecutive presentation failures (discarded buffer, ack timeout) get one
   re-arm before the process quits: a transient compositor hiccup must not
   kill the pill. failures counts consecutive failures so far (0 on the
   first failure). Returns 1 when a retry is allowed, 0 when the process
   should quit. A presented frame resets the count to 0. */
static inline int indicator_should_retry_present(int failures) {
  return failures < 1;
}

#endif
