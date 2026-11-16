/* Offline harness for the vendored corrected wtype (tests/test_wtype_native.py).
 *
 * Compiles the patched main.c with main() renamed and drives the REAL
 * planner AND the real emission path directly: parse_args() +
 * kbcorr_preflight() + kbcorr_prepare_keymap(), then upload_keymap() and
 * run_commands() with the Wayland protocol calls intercepted at the
 * source level (macro aliases, see below) and stubbed transport/delays.
 * No Wayland connection is made and no input is sent to any application.
 *
 * The intercepted keymap upload is captured and compiled into one
 * persistent libxkbcommon client state. Captured modifier requests update
 * that state (group = locked layout), and captured key presses are
 * resolved through it exactly as a client would decode them, producing
 * the decoded text in the trace. A second upload, if one ever occurred,
 * is recorded but ignored by the replay, simulating a receiver that only
 * honours the first map.
 *
 * Interception works because keyboard-protocol.h / wayland-client.h /
 * unistd.h are included BEFORE the macro aliases are defined: their
 * include guards preserve the original declarations, while the call sites
 * inside the included patched translation unit expand to the test
 * doubles below. The static-inline protocol wrappers are never replaced
 * at link time.
 *
 * Outputs (all paths from the environment):
 *   $KBCORR_DUMP   plan JSON: entries, commands, group_count.
 *   $KBCORR_KEYMAP serialized keymap bytes captured at the upload.
 *   $KBCORR_TRACE  emission trace JSON: upload count, decoded text,
 *                  modifier/key events with the active group, final
 *                  group, group-change-while-down / overlap flags.
 *
 * Build (from the test): cc -Wall -Wextra -O2 -I <tmp> -I <root>/native
 *   -o harness wtype_harness.c <root>/native/keyboard-protocol.c
 *   $(pkg-config --cflags --libs xkbcommon wayland-client)
 * where the patched TU is found as "main-patched.c" on the include path.
 */
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <wayland-client.h>
#include <xkbcommon/xkbcommon.h>

#include "keyboard-protocol.h"

/* ---- test doubles for the protocol calls in the patched TU ---- */

#define TRACE_MAX 16384

static int g_upload_count = 0;
static char *g_map_text = NULL;
static size_t g_map_len = 0;
static struct xkb_context *g_client_ctx = NULL;
static struct xkb_keymap *g_client_keymap = NULL;
static struct xkb_state *g_client_state = NULL;
static uint32_t g_group = 0;
static uint32_t g_last_dep = 0;
static int g_key_down = -1; /* evdev phys currently held, or -1 */
static int g_group_change_while_down = 0;
static int g_overlap_press = 0;
static char g_decoded[70000];
static size_t g_decoded_len = 0;
static int g_groups_seen[4] = {1, 0, 0, 0}; /* group 0 is active initially */

/* Trace records. */
static struct {
	uint32_t group, dep, latched, locked;
} g_trace_mods[TRACE_MAX];
static int g_trace_mods_n = 0;
static struct {
	uint32_t key, state, group, dep;
} g_trace_keys[TRACE_MAX];
static int g_trace_keys_n = 0;

static void test_zwp_keymap(struct zwp_virtual_keyboard_v1 *keyboard, uint32_t format, int32_t fd, uint32_t size)
{
	(void)keyboard;
	(void)format;
	g_upload_count++;
	if (g_upload_count > 1) {
		/* Simulate a receiver that ignores every upload after the
		 * first: the replay state keeps decoding from the first map.
		 */
		return;
	}
	lseek(fd, 0, SEEK_SET);
	free(g_map_text);
	g_map_text = malloc(size + 1);
	if (!g_map_text) {
		fprintf(stderr, "harness: out of memory capturing keymap\n");
		exit(1);
	}
	size_t got = 0;
	while (got < size) {
		ssize_t n = read(fd, g_map_text + got, size - got);
		if (n <= 0) {
			break;
		}
		got += (size_t)n;
	}
	g_map_len = got;
	g_map_text[g_map_len] = '\0';
	g_client_ctx = xkb_context_new(XKB_CONTEXT_NO_FLAGS);
	if (!g_client_ctx) {
		fprintf(stderr, "harness: cannot create xkb context\n");
		exit(1);
	}
	g_client_keymap = xkb_keymap_new_from_string(
		g_client_ctx, g_map_text, XKB_KEYMAP_FORMAT_TEXT_V1,
		XKB_KEYMAP_COMPILE_NO_FLAGS);
	if (!g_client_keymap) {
		fprintf(stderr, "harness: captured keymap failed to compile\n");
		exit(1);
	}
	g_client_state = xkb_state_new(g_client_keymap);
	if (!g_client_state) {
		fprintf(stderr, "harness: cannot create xkb state\n");
		exit(1);
	}
}

static void test_zwp_modifiers(struct zwp_virtual_keyboard_v1 *keyboard, uint32_t depressed, uint32_t latched, uint32_t locked, uint32_t group)
{
	(void)keyboard;
	if (g_trace_mods_n < TRACE_MAX) {
		g_trace_mods[g_trace_mods_n].group = group;
		g_trace_mods[g_trace_mods_n].dep = depressed;
		g_trace_mods[g_trace_mods_n].latched = latched;
		g_trace_mods[g_trace_mods_n].locked = locked;
		g_trace_mods_n++;
	}
	if (g_key_down >= 0) {
		g_group_change_while_down = 1;
	}
	g_group = group;
	g_last_dep = depressed;
	if (group < 4) {
		g_groups_seen[group] = 1;
	}
	if (g_client_state) {
		xkb_state_update_mask(g_client_state, depressed, latched,
			locked, 0, 0, group);
	}
}

static void test_zwp_key(struct zwp_virtual_keyboard_v1 *keyboard, uint32_t time, uint32_t key, uint32_t state)
{
	(void)keyboard;
	(void)time;
	if (g_trace_keys_n < TRACE_MAX) {
		g_trace_keys[g_trace_keys_n].key = key;
		g_trace_keys[g_trace_keys_n].state = state;
		g_trace_keys[g_trace_keys_n].group = g_group;
		g_trace_keys[g_trace_keys_n].dep = g_last_dep;
		g_trace_keys_n++;
	}
	if (state == WL_KEYBOARD_KEY_STATE_PRESSED) {
		if (g_key_down >= 0) {
			g_overlap_press = 1;
		}
		g_key_down = (int)key;
		/* Decode literal presses only: a key pressed with a
		 * modifier depressed is a chord key, not literal text.
		 * Fixed keysyms map to their control characters; Return
		 * decodes to "\n" (the helper maps both \n and \r to it).
		 */
		if (g_last_dep == 0 && g_client_state) {
			xkb_keysym_t sym = xkb_state_key_get_one_sym(
				g_client_state, key + 8);
			const char *fixed = NULL;
			char fixed_buf[2] = {0, 0};
			switch (sym) {
			case XKB_KEY_Return:
				fixed = "\n";
				break;
			case XKB_KEY_Tab:
			case XKB_KEY_ISO_Left_Tab:
				fixed = "\t";
				break;
			case XKB_KEY_Escape:
				fixed_buf[0] = 0x1b;
				fixed = fixed_buf;
				break;
			case XKB_KEY_BackSpace:
				fixed_buf[0] = 0x08;
				fixed = fixed_buf;
				break;
			case XKB_KEY_Delete:
				fixed_buf[0] = 0x7f;
				fixed = fixed_buf;
				break;
			default:
				break;
			}
			if (fixed) {
				size_t len = strlen(fixed);
				if (g_decoded_len + len < sizeof(g_decoded)) {
					memcpy(g_decoded + g_decoded_len, fixed, len);
					g_decoded_len += len;
				}
			} else {
				char buf[16];
				int n = xkb_keysym_to_utf8(sym, buf, sizeof(buf));
				if (n > 1 && g_decoded_len + (size_t)(n - 1) < sizeof(g_decoded)) {
					memcpy(g_decoded + g_decoded_len, buf, (size_t)(n - 1));
					g_decoded_len += (size_t)(n - 1);
				}
			}
		}
	} else {
		g_key_down = -1;
	}
}

static int test_roundtrip(struct wl_display *display)
{
	(void)display;
	return 0;
}

static int test_usleep(useconds_t usec)
{
	(void)usec;
	return 0;
}

/* Macro-alias the protocol calls inside the patched TU to the doubles. */
#define zwp_virtual_keyboard_v1_keymap test_zwp_keymap
#define zwp_virtual_keyboard_v1_modifiers test_zwp_modifiers
#define zwp_virtual_keyboard_v1_key test_zwp_key
#define wl_display_roundtrip test_roundtrip
#define usleep test_usleep

/* ---- the patched translation unit, with main() renamed ---- */
#define main kbcorr_patched_main
#include "main-patched.c"
#undef main

#undef usleep
#undef wl_display_roundtrip
#undef zwp_virtual_keyboard_v1_key
#undef zwp_virtual_keyboard_v1_modifiers
#undef zwp_virtual_keyboard_v1_keymap

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
	fprintf(f, "], \"group_count\": %lu}\n", (unsigned long)wtype->group_count);
	if (f != stdout) {
		fclose(f);
	}
}

static void json_escape_str(FILE *f, const char *s, size_t len)
{
	fputc('"', f);
	for (size_t i = 0; i < len; i++) {
		unsigned char c = (unsigned char)s[i];
		switch (c) {
		case '"':
			fputs("\\\"", f);
			break;
		case '\\':
			fputs("\\\\", f);
			break;
		case '\n':
			fputs("\\n", f);
			break;
		case '\r':
			fputs("\\r", f);
			break;
		case '\t':
			fputs("\\t", f);
			break;
		default:
			if (c < 0x20) {
				fprintf(f, "\\u%04x", c);
			} else {
				fputc(c, f);
			}
			break;
		}
	}
	fputc('"', f);
}

static void dump_trace(void)
{
	const char *path = getenv("KBCORR_TRACE");
	FILE *f = stdout;
	if (path && path[0]) {
		f = fopen(path, "w");
		if (!f) {
			return;
		}
	}
	g_decoded[g_decoded_len] = '\0';
	fprintf(f, "{\"uploads\": %d, \"decoded\": ", g_upload_count);
	json_escape_str(f, g_decoded, g_decoded_len);
	fprintf(f, ", \"final_group\": %u", g_group);
	fprintf(f, ", \"group_change_while_down\": %s",
		g_group_change_while_down ? "true" : "false");
	fprintf(f, ", \"overlap_press\": %s",
		g_overlap_press ? "true" : "false");
	fprintf(f, ", \"key_down_at_end\": %s",
		g_key_down >= 0 ? "true" : "false");
	fprintf(f, ", \"groups_seen\": [");
	bool first = true;
	for (int g = 0; g < 4; g++) {
		if (g_groups_seen[g]) {
			fprintf(f, "%s%d", first ? "" : ", ", g);
			first = false;
		}
	}
	fprintf(f, "], \"modifiers\": [");
	for (int i = 0; i < g_trace_mods_n; i++) {
		fprintf(f, "%s{\"group\": %u, \"dep\": %u, \"latched\": %u, \"locked\": %u}",
			i ? ", " : "", g_trace_mods[i].group,
			g_trace_mods[i].dep, g_trace_mods[i].latched,
			g_trace_mods[i].locked);
	}
	fprintf(f, "], \"keys\": [");
	for (int i = 0; i < g_trace_keys_n; i++) {
		fprintf(f, "%s{\"key\": %u, \"state\": %u, \"group\": %u, \"dep\": %u}",
			i ? ", " : "", g_trace_keys[i].key,
			g_trace_keys[i].state, g_trace_keys[i].group,
			g_trace_keys[i].dep);
	}
	fprintf(f, "]}\n");
	if (f != stdout) {
		fclose(f);
	}
	const char *mpath = getenv("KBCORR_KEYMAP");
	if (mpath && mpath[0] && g_map_text) {
		FILE *mf = fopen(mpath, "wb");
		if (mf) {
			fwrite(g_map_text, 1, g_map_len, mf);
			fclose(mf);
		}
	}
}

int main(int argc, char **argv)
{
	struct wtype wtype;
	memset(&wtype, 0, sizeof(wtype));
	/* argv[0] is this harness; the rest is the wtype invocation. */
	parse_args(&wtype, argc, (const char **)argv);
	kbcorr_preflight(&wtype);
	kbcorr_prepare_keymap(&wtype);
	dump_plan(&wtype);
	/* Drive the real emission path with dummy non-NULL handles; all
	 * protocol calls are intercepted by the test doubles above.
	 */
	wtype.display = (struct wl_display *)0x1;
	wtype.keyboard = (struct zwp_virtual_keyboard_v1 *)0x1;
	upload_keymap(&wtype);
	run_commands(&wtype);
	dump_trace();
	return 0;
}
