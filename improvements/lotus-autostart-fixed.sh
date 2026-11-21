#!/bin/sh
# Wait for fcitx5 to start, then switch to ngosen and turn it ON.
# Council 21/11/2026: the old name "lotus" was not a valid input method,
# so "-s lotus" was a silent no-op. DefaultIM=ngosen is what actually
# loads; this -s call only re-asserts it. Whether -s does anything at
# login with no focused window is still untested (redteam F1-4): the
# marker line below proves the script RAN, which is what we can verify.
for i in $(seq 1 40); do
    if fcitx5-remote --check 2>/dev/null; then
        break
    fi
    sleep 0.5
done

fcitx5-remote -s ngosen 2>/dev/null
fcitx5-remote -o 2>/dev/null
mkdir -p "$HOME/.cache/agent-computer-use"
printf '%s lotus-autostart ran, IM=%s\n' "$(date '+%F %T %z')" "$(fcitx5-remote -n 2>/dev/null)" >> "$HOME/.cache/agent-computer-use/lotus-autostart.log"
exit 0
