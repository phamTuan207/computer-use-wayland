/* Offline harness for the vendored corrected wtype (tests/test_wtype_native.py).
 *
 * Compiles the patched main.c with main() renamed and drives the REAL
 * planner directly: parse_args() + kbcorr_preflight(), then dumps the
 * resulting keymap entries and command stream as JSON to $KBCORR_DUMP.
 * No Wayland connection is made and no protocol function is stubbed: the
 * static-inline protocol wrappers in the Wayland headers cannot be
 * intercepted, so the harness tests allocation, canonical resolution,
 * paging, conflicts and fail-closed validation at the planner level.
 * Actual key emission (type_keycode/run_key sending e->phys) is verified
 * by the live gates (i)-(iv), not here.
 *
 * Build (from the test): cc -Wall -Wextra -O2 -I <root>/native
 *   -o harness wtype_harness.c <root>/native/keyboard-protocol.c
 *   $(pkg-config --cflags --libs xkbcommon wayland-client)
 * where the patched TU is found as "main-patched.c" on the include path.
 */
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <wayland-client.h>

#include "keyboard-protocol.h"

/* ---- the patched translation unit, with main() renamed ---- */
#define main kbcorr_patched_main
#include "main-patched.c"
#undef main

static void dump_plan(struct wtype *wtype)
{
	const char *path = getenv("KBCORR_DUMP");
	FILE *f = stdout;
	if (path && path[0]) {
		f = fopen(path, "w");
		if (!f) {
			return;
		}
	}
	fprintf(f, "{\"entries\": [");
	for (size_t i = 0; i < wtype->keymap_len; i++) {
		struct keymap_entry *e = &wtype->keymap[i];
		fprintf(f, "%s{\"wchr\": %ld, \"xkb\": %u, \"phys\": %u, "
			"\"page\": %lu, \"pool\": %s, \"fixed\": %s, "
			"\"sentinel\": %s, \"explicit\": %s, \"referenced\": %s}",
			i ? ", " : "", (long)e->wchr, e->xkb, e->phys,
			(unsigned long)e->page,
			e->is_pool_literal ? "true" : "false",
			e->is_fixed ? "true" : "false",
			e->is_sentinel ? "true" : "false",
			e->is_explicit ? "true" : "false",
			e->referenced ? "true" : "false");
	}
	fprintf(f, "], \"commands\": [");
	for (size_t c = 0; c < wtype->command_count; c++) {
		struct wtype_command *cmd = &wtype->commands[c];
		fprintf(f, "%s{\"type\": %d, \"noop\": %s, \"mod\": %u, "
			"\"sleep_ms\": %u, \"single\": %u, \"codes\": [",
			c ? ", " : "", (int)cmd->type,
			cmd->noop ? "true" : "false",
			(unsigned int)cmd->mod, cmd->sleep_ms,
			cmd->single_key_code);
		if (cmd->type == WTYPE_COMMAND_TEXT) {
			for (size_t t = 0; t < cmd->key_codes_len; t++) {
				fprintf(f, "%s%u", t ? ", " : "",
					cmd->key_codes[t]);
			}
		}
		fprintf(f, "]}");
	}
	fprintf(f, "]}\n");
	if (f != stdout) {
		fclose(f);
	}
}

int main(int argc, char **argv)
{
	struct wtype wtype;
	memset(&wtype, 0, sizeof(wtype));
	/* argv[0] is this harness; the rest is the wtype invocation. */
	parse_args(&wtype, argc, (const char **)argv);
	kbcorr_preflight(&wtype);
	dump_plan(&wtype);
	return 0;
}
