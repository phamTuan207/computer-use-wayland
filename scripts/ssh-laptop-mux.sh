#!/bin/bash
# S0 shell drop-in for ~/workspace/ssh-laptop.sh (same base options,
# plus persistent multiplexing). FINAL direction e05fc58, PROBE-S0 90eb8be.
#
#   scripts/ssh-laptop-mux.sh <remote command...>
#
# Hard rules, all measured:
# - The master is started with setsid/nohup and NO -f flag (see
#   scripts/ssh_mux.py ensure). An `ssh -f` master refuses mux
#   sessions and dies in 1-2 min. This wrapper never starts a master
#   itself: ControlMaster=auto lets the first client create one, and
#   scripts/ssh_mux.py ensure is the owned way to pre-start it.
# - ServerAliveInterval=15 keeps the master alive through idle
#   (without it the master dies inside 90 s idle; idle test B).
# - A dead master costs one slow (~4.5s) but correct fresh connect,
#   then ControlMaster=auto creates the replacement master. That is
#   the fallback, not a failure. Fresh SSH per call is gone as the
#   default path; it stays as the recovery path.
# - Socket: /tmp/cm-s0-%r@%h:%p, owned by S0, never a probe socket.
# - For timed or logged runs, or for the per-use liveness check plus
#   restart-on-death and the per-socket watchdog, use
#   python3 scripts/ssh_mux.py instead of this wrapper.
exec ssh -o BatchMode=yes -o ConnectTimeout=25 -o StrictHostKeyChecking=accept-new -o IdentitiesOnly=yes -o ProxyCommand="python3 $HOME/workspace/tailscale-proxy.py %h %p" -i "$HOME/.ssh/id_ed25519" -o ControlMaster=auto -o ControlPath=/tmp/cm-s0-%r@%h:%p -o ControlPersist=600 -o ServerAliveInterval=15 -o ServerAliveCountMax=3 "${CU_LAPTOP_SSH:?Set CU_LAPTOP_SSH to user@host for the laptop}" "$@"
