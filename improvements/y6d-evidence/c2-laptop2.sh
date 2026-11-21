#!/bin/bash
# Y6d C2 laptop part, v2: re-run on the adjudication-fixed runner + new cases.
# - Parser (verbatim extraction), teardown harness (verbatim extraction).
# - GRIM-A asserted with geometry derived from the live monitor position.
# - ldd pre-flight block (verbatim extraction): dead ABI on the real backup 1
#   .so must fail naming libaquamarine.so.14; a good .so must pass.
set -u
NEST=/tmp/y6-nested
RUNNER=$NEST/run-nested-wayland.sh
echo "=== Y6D-C2-LAPTOP2 start $(date +%H:%M:%S)"
bash -n "$RUNNER" && echo "C2-1 runner bash -n OK"
python3 -m py_compile $NEST/run-nested-pill.py && echo "C2-1 pill py_compile OK"
export XDG_RUNTIME_DIR=/run/user/1000 WAYLAND_DISPLAY=wayland-1
export HYPRLAND_INSTANCE_SIGNATURE=$(ls -t /run/user/1000/hypr/ | head -1)
echo "live sig $HYPRLAND_INSTANCE_SIGNATURE"
LIVE_PID=$(pgrep -x Hyprland)
echo "live pid $LIVE_PID"
md5sum "$RUNNER" $NEST/run-nested-pill.py $NEST/conf/hyprland-wayland.lua

# --- C2-2 parser: extract read_pill_geom verbatim from the fixed runner
mkdir -p /tmp/y6d-c2
awk '/^read_pill_geom\(\) \{/{f=1} f{print} /^}$/ && f{exit}' "$RUNNER" > /tmp/y6d-c2/read_pill_geom.sh
wc -l /tmp/y6d-c2/read_pill_geom.sh
export NEST=/tmp/y6d-c2
hyprctl -j layers > /tmp/y6d-c2/layers-live.json 2>/dev/null
python3 -c "import json; d=json.load(open('/tmp/y6d-c2/layers-live.json')); print('live layers monitors:', list(d.keys()))"
cat > /tmp/y6d-c2/synth.json << 'EOF'
{"WAYLAND-1": {"levels": {"2": [{"namespace": "computer-use-indicator", "x": 320, "y": 0, "w": 320, "h": 66}]}}}
EOF
cat > /tmp/y6d-c2/parser-test.sh << 'EOF'
#!/bin/bash
LAYERS_JSON="$1"
nest() { cat "$LAYERS_JSON"; }
. /tmp/y6d-c2/read_pill_geom.sh
OUT=$(read_pill_geom 2>/tmp/y6d-c2/parser-stderr.txt); RC=$?
echo "parser rc=$RC out='$OUT' stderr: $(cat /tmp/y6d-c2/parser-stderr.txt)"
EOF
chmod +x /tmp/y6d-c2/parser-test.sh
echo "-- live layers (no pill live): expect rc=1, no traceback"
bash /tmp/y6d-c2/parser-test.sh /tmp/y6d-c2/layers-live.json
echo "-- synthetic nested JSON: expect rc=0 out='320,0 320x66'"
bash /tmp/y6d-c2/parser-test.sh /tmp/y6d-c2/synth.json

# --- C2-3 grim dry run, geometry from the live monitor (council 2 N1)
MON_JSON=$(hyprctl -j monitors 2>/dev/null)
MON_NAME=$(echo "$MON_JSON" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d[0]['name'])")
MON_X=$(echo "$MON_JSON" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d[0]['x'])")
MON_Y=$(echo "$MON_JSON" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d[0]['y'])")
MON_W=$(echo "$MON_JSON" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d[0]['width'])")
MON_H=$(echo "$MON_JSON" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d[0]['height'])")
echo "live monitor $MON_NAME at $MON_X,$MON_Y ${MON_W}x${MON_H}"
cd /tmp
rm -f /tmp/y6d-grim-a.png /tmp/y6d-grim-a2.png
echo "-- grim space form at live top-left corner: expect file created (ASSERTED)"
grim -g "$MON_X,$MON_Y 200x200" /tmp/y6d-grim-a.png 2>&1
if [ -f /tmp/y6d-grim-a.png ]; then echo "GRIM-A OK bytes=$(stat -c%s /tmp/y6d-grim-a.png)"; else echo "GRIM-A FAIL: no file"; fi
echo "-- grim Y6b geometry 2464,902 200x200: expect file created"
grim -g "2464,902 200x200" /tmp/y6d-grim-a2.png 2>&1
if [ -f /tmp/y6d-grim-a2.png ]; then echo "GRIM-A2 OK bytes=$(stat -c%s /tmp/y6d-grim-a2.png)"; else echo "GRIM-A2 FAIL: no file"; fi
echo "-- grim 100,100 200x200 (outside every live output): expect did-not-intersect"
grim -g "100,100 200x200" /tmp/y6d-grim-b0.png 2>&1 || echo "GRIM-B0 rc=$? (expect did-not-intersect above)"
echo "-- grim nest-style geometry 320,0 320x66: expect NOT 'invalid geometry'"
grim -g "320,0 320x66" /tmp/y6d-grim-b.png 2>&1 || echo "GRIM-B rc=$? (error kind above, must not be invalid geometry)"
echo "-- grim old comma form: expect 'invalid geometry'"
grim -g "2464,902,200,200" /tmp/y6d-grim-c.png 2>&1 || echo "GRIM-C rc=$? (expect invalid geometry above)"
echo "-- grim -g plus -o: expect 'mutually exclusive'"
grim -g "$MON_X,$MON_Y 200x200" -o "$MON_NAME" /tmp/y6d-grim-d.png 2>&1 || echo "GRIM-D rc=$? (expect mutually exclusive above)"

# --- C2-3b ldd pre-flight block, verbatim extraction, real backup 1 .so
awk '/command -v ldd/{f=1} f{print} /plugin ABI OK/{exit}' "$RUNNER" > /tmp/y6d-c2/ldd-block.sh
wc -l /tmp/y6d-c2/ldd-block.sh
cat > /tmp/y6d-c2/ldd-test.sh << 'EOF'
#!/bin/bash
fail() { echo "FAIL: $1"; exit 1; }
CONF="$1"
. /tmp/y6d-c2/ldd-block.sh
EOF
chmod +x /tmp/y6d-c2/ldd-test.sh
echo "-- ldd block vs current conf (backup 1, dead ABI): expect FAIL naming libaquamarine.so.14"
bash /tmp/y6d-c2/ldd-test.sh /tmp/y6-nested/conf/hyprland-wayland.lua; echo "LDD-DEAD rc=$?"
ln -sf /usr/lib/libaquamarine.so.15 /tmp/y6d-good-hyprglass.so
printf 'hl.plugin.load("/tmp/y6d-good-hyprglass.so")\n' > /tmp/y6d-c2/good-conf.lua
echo "-- ldd block vs good .so (all deps resolve): expect plugin ABI OK"
bash /tmp/y6d-c2/ldd-test.sh /tmp/y6d-c2/good-conf.lua; echo "LDD-GOOD rc=$?"

# --- C2-4 teardown dry harness (extracted teardown, fake nested log)
mkdir -p /tmp/y6d-teardown/run/hypr/FAKESIG
printf 'fake-line-1\nfake-line-2\n' > /tmp/y6d-teardown/run/hypr/FAKESIG/hyprland.log
awk '/^teardown\(\) \{/{f=1} f{print} /^}$/ && f{exit}' "$RUNNER" > /tmp/y6d-teardown/teardown.sh
wc -l /tmp/y6d-teardown/teardown.sh
cat > /tmp/y6d-teardown/run-teardown.sh << 'EOF'
#!/bin/bash
set -u
NEST=/tmp/y6d-teardown
RUN_DIR=/tmp/y6d-teardown/run
LOCK=/tmp/y6d-teardown.lock
START_TS=test
SIG=FAKESIG
NEST_STARTED=1
NESTED_PID=""
PILL_PID=""
MPV_PID=""
LIVE_PID=1515
LIVE_SIG=$(ls -t /run/user/1000/hypr/ | head -1)
export XDG_RUNTIME_DIR=/run/user/1000 WAYLAND_DISPLAY=wayland-1
live() { env XDG_RUNTIME_DIR=/run/user/1000 WAYLAND_DISPLAY=wayland-1 HYPRLAND_INSTANCE_SIGNATURE="$LIVE_SIG" "$@" 9>&-; }
exec 9>"$LOCK"
. /tmp/y6d-teardown/teardown.sh
teardown
echo "TEARDOWN-ASSERT1: $(test -f /tmp/y6d-teardown/hypr-saved-test-FAKESIG/hyprland.log && grep -c fake-line /tmp/y6d-teardown/hypr-saved-test-FAKESIG/hyprland.log || echo MISSING)"
echo "TEARDOWN-ASSERT2: $(test ! -d /tmp/y6d-teardown/run && echo RUN-DIR-REMOVED || echo RUN-DIR-STILL-THERE)"
if flock -n "$LOCK" -c true 2>/dev/null; then echo "TEARDOWN-ASSERT3: LOCK-FREE"; else echo "TEARDOWN-ASSERT3: LOCK-HELD"; fi
kill -0 1515 && echo "TEARDOWN-ASSERT4: LIVE-1515-ALIVE"
live hyprctl version 2>&1 | head -2
EOF
chmod +x /tmp/y6d-teardown/run-teardown.sh
bash /tmp/y6d-teardown/run-teardown.sh
echo "=== Y6D-C2-LAPTOP2 done $(date +%H:%M:%S)"
