# Local computer-use research and measured changes

## Architecture decision

Keep native Wayland input/capture, the session guardian and semantic CDP targets.
Reuse the existing Python CLI inside the interactive driver instead of forking it
for every request. This changes execution lifetime, not the action schemas or
the focus, screen-change, cancellation and permission checks. It is sequential:
there is no arbitrary-code endpoint or concurrent command execution.

The [OpenAI integration recipes](https://developers.openai.com/api/docs/guides/tools-computer-use-integration)
describe persistent runtimes, concise text/image outputs and preserved session
state. The [sample app](https://github.com/openai/openai-cua-sample-app/tree/f2a3dc523ae406f9b704f9a420a05402a63b4522)
implements persistent Playwright/Python workers, but its Python desktop route
requires X11. It is not a drop-in replacement for this Wayland host, nor evidence
that every task becomes faster. No model API or paid service was used here.

[anaisbetts/mcp-computer-use](https://github.com/anaisbetts/mcp-computer-use/tree/5f7b4a5f480eb665144d859c2297e85a8d3cd5b9)
offers an MCP/Rust input and screencopy architecture. Its batch error behavior
and platform support differ from this tool. Adopting MCP, Rust or another capture
library alone does not establish a latency or token benefit; they were not
installed or run on the host during this comparison.

The [original CUA research article](https://openai.com/index/computer-using-agent/)
describes an iterative perception/action loop and remaining limitations. Executor
timings below do not measure model reasoning, task success on general benchmarks,
or the performance of OpenAI's production runtime.

## Measurements on this host

| Operation | Before median | After median | Samples per path |
|---|---:|---:|---:|
| Read-only status command | 46.088 ms | 0.861 ms | 25 |
| Actual 300×300 GTK fixture capture | 98.34 ms | 29.54 ms | 12 |
| 5 ms wait executor only | 23.64 ms | 5.15 ms | 12 |

Capture and wait paths alternated to reduce ordering bias. Capture uses the same
production checks, crop and PNG saving. It does not include model inference or
an input action; the first resident import is cold, later imports are reused.
The wait comparison replaces the previous `wtype` sleep/key-release invocation
with `wait_cancelable`: no keyboard process, key events or IME state changes.
These numbers depend on hardware, compositor state and running applications.

Reproduce the read-only CLI/resident comparison:

```sh
python3 tests/control_benchmark.py --samples 12
python3 tests/control_benchmark.py --samples 12 --window 0xADDRESS --crop X Y W H
```

Use only a visible inert fixture for the second command. It never changes focus
or sends input. Results omit private window identifiers and screenshot paths.

## DOM output and privacy

Snapshots prioritize viewport-visible elements before offscreen fallback, with
the same default 80-ref output limit. `browser --max-elements 16` reduces the
output budget when a small view is sufficient; increase it if the needed target
is omitted, rather than guessing. On an 80-control synthetic fixture, snapshot
JSON shrank from 4,093 to 892 bytes (78.2%). This is a text-byte proxy, not a
model-billed token measurement. Both CLI and adapter validate the 1..80 bound
before dispatch. Returned debugger URLs must also remain loopback WebSockets.
Form values and editable contents are redacted;
checkbox/radio checked state remains available. `fill` and `assert` verify values
internally without returning entire field contents. Target lookup expressions
carry only ref/selector, not repeated fill payloads.

This reduces avoidable text and sensitive-value disclosure; it is not a claim
that screenshots or every page label are secret-free. Generated UI text is still
untrusted data. No model-billed token savings were measured. Cropping an image
reduces pixels, but pixels/bytes are not an exact model token or billing count.

## Deliberately not added

The isolated real Chromium fixture passed 12/12 trusted small-target clicks,
crop mapping, Unicode input, Ctrl+T/Ctrl+W and drag-drop. Stale refs, covered
targets, out-of-bounds batches and changed screens were rejected. These are
scripted fixture checks, not arbitrary-app or model reasoning success rates.
Final source suite: 242 tests, one optional skip, 21.028 seconds; capture/adapter
regressions passed. The synchronized installed Chromium fixture passed again:
native click batch median 194 ms (12 clicks), Unicode DOM form 28 ms (3 actions).
These batch timings include executor checks, not model reasoning.

No extra MCP service, OCR dependency, model API loop or whole-backend rewrite.
A persistent CDP connection and alternate capture implementation remain possible
experiments, not proven improvements in this report. They require their own
measured benefit and lifecycle/privacy tests before replacing the current path.
