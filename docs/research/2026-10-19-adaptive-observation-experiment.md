# Native grounding and adaptive image delivery

Tested 2026-10-19 on owned GTK/Pinta fixtures. This extends the earlier batching-only change
with real native state and delivery logic. No model API was called by the executor.

## Alternatives examined

- [Microsoft OmniParser](https://github.com/microsoft/OmniParser) proposes interactive-region
  boxes from pixels. Our [actual detector experiment](2026-10-19-omniparser-detector-experiment.md)
  found the ellipse and hand buttons, but failed to isolate the red swatch; default CPU inference
  added about 1.2 s per screenshot, and 1280 px added about 4.8 s. Detection alone does not name
  the requested target. It remains an experimental optional candidate, not a mandatory backend.
- [Agent S2](https://arxiv.org/abs/2504.00906) combines specialist grounding and hierarchical
  planning. It is evidence of useful alternative methods, not proof of an improvement for this
  executor. Importing its whole model stack is not required to exploit native element identity.
- [browser-use](https://github.com/browser-use/browser-use/blob/main/AGENTS.md) documents vision
  on demand (`use_vision: auto`) and executing action groups until the page changes. Our analogous
  desktop implementation preserves captures/guards and returns native state or an exact visual
  duplicate hint. It does not claim to reproduce browser-use's browser controller.

## Experiment 1: element identity instead of estimated coordinates

The existing AT-SPI adapter found Pinta's **Ellipse** and **Pan** toggle tools by their names and
actions. No screenshot was needed to choose them. However, its result omitted native toggle
state, so a model could still ask for an image to verify selection. `describe()` now exposes
positive `pressed`, `checked`, `selected` and `expanded` states without collecting field values.

On an owned GTK test window, ten distinct text assignments and ten button clicks were verified
against the application's independent event log with **zero model-visible images**. Pinta's
Ellipse selection was confirmed through its native `pressed` state, also without an image.
The GTK fixture was not resized across these trials; this is not a geometry stress test or a
20/20 general grounding benchmark. Native text/button identity avoids estimating coordinates
for these supported controls; canvas drawing still needs a visual/geometry target.

An early harness checked the event log too soon; action callbacks arrived later. A second Pinta
oracle incorrectly expected `checked`; this GTK toggle actually reports `pressed`. Reading the
actual state established the correct result. Therefore an acknowledged action and its immediate
after-snapshot are not sufficient app-result proof. Poll the semantic result without replaying
input; request an image only if the state/result remains unknown. Application accessibility is
not universally available or guaranteed correct.

## Experiment 2: exact duplicate delivery, not a fixed screenshot count

`VisualCheckpoint` is session-local and opt-in in the JSON-line driver (`image_policy: auto`).
The local MCP embedding enables it by default. It hashes the actual PNG and compares its
window/monitor/crop/dimensions/scale/transform coordinate context. All observations and files
remain available. The embedding omits only a duplicate attachment, preserving JSON metadata and
the fresh observation path. `image_policy: always` forces delivery. The default driver protocol
remains `always` so existing embeddings do not change behavior automatically.

| Live stable Pinta case | Attached images | Observed caller time |
| --- | ---: | ---: |
| First `auto` view, including initial pixel settling | 1 | 297.16 ms |
| Repeated unchanged `auto` view | 0 | 67.94 ms |
| Explicit `always` view | 1 | 62.32 ms |

These timings are not an A/B speedup: the first request also settled the initial frame, and all
three requests still captured the screen. The saving is one redundant model-visible image,
not elimination of machine capture cost. The raw record also measures local hash/metadata
overhead separately. Model reasoning, network latency and input tokens were not measured.

A useful negative control occurred before settling: three rapid frames changed during Pinta's
toolbar animation. All images were delivered, as intended. Unit tests additionally require
delivery after changed pixels, another coordinate frame, errors/refusals/warnings, missing
metadata and checkpoint reset. The policy uses no approximate/perceptual similarity threshold
that could hide a changed small button. Nonvisual responses reset it conservatively.

The hint means **same visible frame**, not **same application state** or **successful action**.
Native state/app-result verification and a final meaningful result check remain necessary.
This is a conservative adaptive improvement, not an optimal observation scheduler or a measured
95% general accuracy guarantee.

[Machine-readable acceptance results](../benchmarks/adaptive-observation-2026-10-19.json).

Validation: the complete offline suite ran 682 tests, passed, with one existing optional skip.
A missing cached previous PNG now forces `required` delivery instead of an `unchanged` hint
pointing at a path that no longer exists.
The local MCP embedding was also checked to retain error-image attachments with `isError: true`,
including an erroneous duplicate hint, while omitting a successful exact duplicate. The live
MCP trial verified first/duplicate/forced delivery and finished its session normally.
