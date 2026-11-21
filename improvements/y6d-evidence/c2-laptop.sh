#!/bin/bash
# Y6d C2 laptop part on the v3 runner: parser, grim, teardown harness.
set -u
NEST=/tmp/y6-nested
RUNNER=$NEST/run-nested-wayland.sh
echo "=== Y6D-C2-LAPTOP start $(date +%H:%M:%S)"
bash -n "$RUNNER" && echo "C2-1 runner bash -n OK"
python3 -m py_compile $NEST/run-nested-pill.py && echo "C2-1 pill py_compile OK"
export XDG_RUNTIME_DIR=/run/user/1000 WAYLAND_DISPLAY=wayland-1
export HYPRLAND_INSTANCE_SIGNATURE=$(ls -t /run/user/1000/hypr/ | head -1)
echo "live sig $HYPRLAND_INSTANCE_SIGNATURE"
LIVE_PID=$(pgrep -x Hyprland)
echo "live pid $LIVE_PID"

# --- C2-2 parser: extract read_pill_geom verbatim from the v3 runner
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

# --- C2-3 grim dry run (live env, writes only /tmp PNGs)
cd /tmp
echo "-- grim space form inside live output: expect file created"
grim -g "100,100 200x200" /tmp/y6d-grim-a.png && echo "GRIM-A OK bytes=$(stat -c%s /tmp/y6d-grim-a.png)"
echo "-- grim Y6b geometry 2464,902 200x200: record outcome (Y6b: success)"
grim -g "2464,902 200x200" /tmp/y6d-grim-a2.png 2>&1 && echo "GRIM-A2 OK bytes=$(stat -c%s /tmp/y6d-grim-a2.png)" || echo "GRIM-A2 rc=$? (see stderr above)"
echo "-- grim nest-style geometry 320,0 320x66: expect NOT 'invalid geometry'"
grim -g "320,0 320x66" /tmp/y6d-grim-b.png 2>&1 || echo "GRIM-B rc=$? (error kind above, must not be invalid geometry)"
echo "-- grim old comma form: expect 'invalid geometry'"
grim -g "2464,902,200,200" /tmp/y6d-grim-c.png 2>&1 || echo "GRIM-C rc=$? (expect invalid geometry above)"
echo "-- grim -g plus -o: expect 'mutually exclusive'"
grim -g "100,100 200x200" -o eDP-2 /tmp/y6d-grim-d.png 2>&1 || echo "GRIM-D rc=$? (expect mutually exclusive above)"

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
echo "=== Y6D-C2-LAPTOP done $(date +%H:%M:%S)"
