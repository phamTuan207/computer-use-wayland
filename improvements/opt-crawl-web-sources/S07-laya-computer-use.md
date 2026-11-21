# S7. Laya computer-use (AX tree plus decision model, macOS)

- Class: (b) slow first action and think-observe loop costs
- URL: https://github.com/ChenneyZhuang/laya-computer-use
- Accessed: 2026-11-21
- Crawler: OPT-WEB, 2026-11-21 22:52 +07

## What they did

Replaced screenshot plus vision LLM with macOS Accessibility tree plus a small local decision model. The model picks an element index from a numbered table; code resolves the index to the real element. No coordinates, no screenshots, no cloud.

## Evidence shown

AX walk median about 110ms (22 actionable of 169 raw elements), one decision about 110ms at up to 20 options, about 230ms at 40 options, total about 220ms per step, $0. Honest negative result: the official Laya checkpoints score 0/12 on control selection (they answer DONE/WAIT without reading the options), while a vision model (OmniJev-4B) scores 9/12 but at about 142s per decision, about 600x slower.

## Applicability verdict: PARTIAL

The latency numbers (about 220ms per step vs our multi-second think loop) prove the ceiling of a structured-tree route, and the design (decide on element identity, resolve coordinates at dispatch) is the same late-binding idea as S6. But it is macOS-only (AX API plus cua-driver), and the headline decision model scores 0/12, so there is no usable model to copy. For us the transferable part is the architecture, not the code: our DOM is our AX tree, and our el.click() path already resolves identity at dispatch. The 600x vision-vs-tree latency gap is also a useful number to quote when defending the DOM-first design against vision-first proposals.
