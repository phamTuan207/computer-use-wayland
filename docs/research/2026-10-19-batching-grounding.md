# Batching and GUI grounding research

Reviewed: 2026-10-19. Sources below were opened directly; benchmark results are the authors' reported results, not measurements of this repository.

## Decision

Make one model observation, plan the predictable sequence, execute one batch, then inspect its result. For a static drawing canvas, two model-visible images (before and after) should normally suffice. A third is reasonable after launching the app or discovering a previously unseen dialog. Break a batch when the next target depends on unknown UI, not after every pointer move or button selection.

This is a workflow change, not evidence that the current visual model has 95% grounding accuracy. The local executor moves an already chosen coordinate; it does not contain a model that recognizes buttons. Adding a second vision model is a substantial integration and would need a representative local evaluation before claiming better accuracy or latency.

Follow-up experiments now include an actual [OmniParser detector run](2026-10-19-omniparser-detector-experiment.md)
and [native semantic targeting plus automatic duplicate delivery](2026-10-19-adaptive-observation-experiment.md).
The latter adds runtime logic beyond the initial batching instructions.

## What OpenAI currently recommends

OpenAI's integration guide explicitly supports action arrays and returning the screenshot after the whole batch. It recommends `detail: "original"`; downscaled screenshots require coordinate remapping. It also permits existing custom desktop tools and suggests comparing designs on task success, elapsed time, model turns, and recovery. [Integration recipes](https://developers.openai.com/api/docs/guides/tools-computer-use-integration)

The current main guide recommends preserving the execution session, observing when UI state is unknown, and checking after a short action group. It does not require a model screenshot after each action. [Computer use guide](https://developers.openai.com/api/docs/guides/tools-computer-use)

The SDK driver executes actions once, in order, and captures the final screenshot. It does not retry driver actions. Its missed-click advice is to maintain one coordinate space, scale coordinates when resizing, and add crop offsets. [Driver reference](https://developers.openai.com/api/docs/guides/tools-computer-use-sdk-drivers)

## Grounding alternatives and limits

| First-party project | What it contributes | What the evidence does not establish |
| --- | --- | --- |
| [Microsoft OmniParser](https://github.com/microsoft/OmniParser) | Converts screenshot regions and icon descriptions to structured elements. Its README reports OmniParser v2 at 39.5% on ScreenSpot Pro; it now lists a newer YOLOv9-E detector. | Region detection is not a guarantee that an arbitrary requested button is correctly identified. No local Pinta or Hyprland accuracy is established. |
| [ByteDance UI-TARS](https://github.com/bytedance/UI-TARS) | Its UI-TARS-1.5 table reports 94.2% on ScreenSpot-V2 and 61.6% on ScreenSpotPro. This large gap shows how much benchmark difficulty matters. | These are model and benchmark results, not accuracy for this executor or a universal 95% floor. |
| [ShowUI paper](https://arxiv.org/abs/2411.17465) and [repository](https://github.com/showlab/ShowUI) | The paper reports a 2B model with 75.1% zero-shot grounding and visual-token reduction. The repository supports iterative refinement. | A separately trained grounding model is not a drop-in coordinate conversion patch. Refinement may require additional inference, which conflicts with the immediate latency goal unless evaluated. |

UI-TARS also has a newer [UI-TARS-2 report](https://arxiv.org/abs/2509.02544), using multi-turn reinforcement learning and hybrid GUI/file/terminal interaction. Its reported OSWorld result is a task completion measure, not single-click grounding accuracy. It does not justify transplanting older grounding percentages onto the local setup.

## Model views versus machine captures

The repository already supports 1–32 desktop actions per batch (`validate_actions` in [cu.py](../../scripts/cu.py)). `desktop_act` performs a fresh machine-side capture to reject a changed screen before input, checks focus and geometry, maps image coordinates through crop/scale metadata, and verifies the compositor's cursor position within 3 pixels before clicking. It returns a final observation by default.

A machine capture compared by code is not a model-visible observation and does not itself trigger another model decision. The 3-pixel guard measures whether the pointer reached the requested coordinate; it cannot prove the coordinate refers to the intended button. Preserve these guards while reducing redundant image returns and model turns. A final screenshot returned by `act` should be reused directly instead of immediately requesting another `observe`.

Latency should be measured separately as model response time, tool/runtime time, image capture time, and caller wait/poll overhead. No runtime-only benchmark proves the end-to-end model workflow became faster. Report model-visible image count and tool call count alongside completion and elapsed time. A fixed long shell polling delay can dominate a short tool action even when capture and pointing are fast.

## Small changes suited to this executor

1. Require agents to batch all currently predictable actions into one call, normally with one initial and one final image for a simple static task. A batch may include selecting a visible tool, setting a visible color, and drawing on the same canvas.
2. Prefer DOM/accessibility element identity and bounds when available. Use image coordinates for canvas/drawing or apps without useful structured targets. Keep image dimensions and crop/scale metadata attached to observations.
3. Do not move, inspect, then click merely to confirm pointer placement: the runtime already checks the requested coordinate. Do inspect when recognizing a new UI state or checking the completed result.
4. Stop and observe when targets depend on an unseen dialog, navigation, uncertain loading, user interference, changed focus/geometry, or a failed guard. Do not replay uncertain input.
5. Avoid installing OmniParser/UI-TARS/ShowUI as an automatic fallback without an evaluation. A future opt-in benchmark should test small buttons, scaled/cropped screens, overlapping windows, and canvas controls; compare grounding success and total latency against the current agent model.

The two-image target is a policy for predictable tasks, not an enforced ceiling that suppresses observations needed to recover safely.

## Local acceptance: Pinta, 2026-10-19

An owned blank 800×600 image was opened in Pinta. The agent inspected one 924×1176 window image
at original detail, then submitted one four-action desktop batch: ellipse tool, visible red color,
Shift-drag, hand tool to commit. It inspected the returned final image, showing the red circle and
the application's Ellipse Added/Finalized history. The persistent session finished normally.

| Measurement | Earlier demo trace | Batch-first acceptance |
| --- | ---: | ---: |
| Model-visible images | 5 | 2 |
| Desktop `act` calls | 4 | 1 |

The new batch completed all four actions in 1089 ms; initial/final capture took 53/51 ms, and the
caller returned after about 1703 ms for the batch request. These are runtime/caller measurements,
not model reasoning time or end-to-end task latency. The earlier demo is a retrospective trace,
not a rerun with identical settings; its width adjustment and drag duration differed. The result
establishes that this task can use two model images with unchanged preflight and pointer guards.
It does not establish a general accuracy percentage or a statistical speedup.

The policy is installed in the shared local skill plus the OpenCode/CommandCode routing and MCP
description. The public repository ships the portable skill/reference and CLI help; host-specific
agent configuration remains local. [Machine-readable acceptance record](../benchmarks/batch-first-pinta-2026-10-19.json).

Validation for this change: 35 `test_core.py` tests and 23 `test_session_driver.py` tests passed.
CLI action execution and native code are unchanged; this acceptance did not run the entire native
or compositor ABI suite, or evaluate a new grounding model.
