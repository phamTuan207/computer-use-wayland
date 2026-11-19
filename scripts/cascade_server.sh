#!/bin/bash
# Start/stop/status for the local cascade llama-server (Rank 1 / M4 gate).
# No broker, no desktop changes. The server only serves the local text
# model on 127.0.0.1; it never touches windows, files, or the relay.
# Paths are overridable by environment for other machines.
# Usage: cascade_server.sh start|stop|status
set -u
BIN="${CU_CASCADE_LLAMA_SERVER:-/home/james/.cache/cascade-gate/llama-bin/llama-b12359/llama-server}"
MODEL="${CU_CASCADE_MODEL:-/home/james/.cache/cascade-gate/Qwen2.5-3B-Instruct-Q4_K_M.gguf}"
CUDART_DIR="${CU_CASCADE_CUDART_DIR:-/home/james/.cache/cascade-gate/cudart-llama-b12359-bin-ubuntu-cuda-12.8-x64}"
PORT="${CU_CASCADE_PORT:-8088}"
GPU_LAYERS="${CU_CASCADE_GPU_LAYERS:-99}"
CTX_SIZE="${CU_CASCADE_CTX:-4096}"
PIDFILE="/tmp/cascade-gate/llama-server.pid"
LOG="/tmp/cascade-gate/llama-server.log"

cmd="${1:-status}"
case "$cmd" in
  start)
    if [ -f "$PIDFILE" ] && kill -0 "$(cat "$PIDFILE")" 2>/dev/null; then
      echo "already running pid $(cat "$PIDFILE")"
      exit 0
    fi
    if curl -s -m 3 "http://127.0.0.1:$PORT/health" >/dev/null 2>&1; then
      echo "port $PORT already answers, refusing to start a second server"
      exit 1
    fi
    [ -x "$BIN" ] || { echo "llama-server not found or not executable: $BIN"; exit 1; }
    [ -f "$MODEL" ] || { echo "model file not found: $MODEL"; exit 1; }
    mkdir -p "$(dirname "$PIDFILE")"
    echo "free VRAM before start:"
    nvidia-smi --query-gpu=memory.free --format=csv 2>/dev/null || true
    LD_LIBRARY_PATH="$CUDART_DIR:${LD_LIBRARY_PATH:-}" setsid nohup "$BIN" \
      -m "$MODEL" --port "$PORT" --host 127.0.0.1 \
      --n-gpu-layers "$GPU_LAYERS" --ctx-size "$CTX_SIZE" \
      >"$LOG" 2>&1 < /dev/null &
    echo $! > "$PIDFILE"
    echo "started pid $(cat "$PIDFILE"), log $LOG"
    for i in $(seq 1 25); do
      if curl -s -m 2 "http://127.0.0.1:$PORT/health" >/dev/null 2>&1; then
        echo "ready after ${i}s"
        nvidia-smi --query-gpu=memory.used,memory.free --format=csv
        exit 0
      fi
      sleep 1
    done
    echo "server did not become ready in 25s, check status later, see $LOG"
    tail -n 20 "$LOG"
    exit 1
    ;;
  stop)
    if [ -f "$PIDFILE" ]; then
      pid="$(cat "$PIDFILE")"
      if kill -0 "$pid" 2>/dev/null; then kill "$pid"; echo "stopped $pid"; else echo "pid $pid already dead"; fi
      rm -f "$PIDFILE"
    else
      echo "no pidfile, nothing to stop"
    fi
    ;;
  status)
    if curl -s -m 3 "http://127.0.0.1:$PORT/health" 2>/dev/null; then echo; else echo "server not answering on port $PORT"; fi
    nvidia-smi --query-gpu=memory.used,memory.free --format=csv 2>/dev/null || true
    ;;
  *)
    echo "usage: $0 start|stop|status"
    exit 2
    ;;
esac
