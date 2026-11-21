# S5. Temporal UI State Inconsistency in Desktop GUI Agents (Xu, UCSD, April 2026)

- Class: (b) slow first action and think-observe loop costs
- URL: https://arxiv.org/pdf/2604.18860
- Accessed: 2026-11-21
- Crawler: OPT-WEB, 2026-11-21 22:50 +07

## What they did

Measured the observation-to-action gap on real OSWorld workloads (VMware Ubuntu 22.04, Claude Opus 4.6), then built PUSV, Pre-execution UI State Verification: re-verify UI state immediately before dispatch with masked pixel SSIM at the click target, global screenshot diff, and X window snapshot diff.

## Evidence shown

Mean gap 6.51s, std 3.59s, min 3.18s, max 13.23s, n=10 tasks. Attack primitive B (window focus manipulation) reaches 100% action-redirection success with zero visual evidence at observation time. PUSV reaches 100% Action Interception Rate across 180 adversarial trials (135 primitive A plus 45 primitive B), zero false positives, under 0.1s overhead. Against DOM injection (primitive C) PUSV is near 0% AIR, a structural blind spot of any visual-only check.

## Applicability verdict: APPLIES, with a split

The 6.51s mean gap is the published number closest to our 120s observation expiry problem: it proves a screenshot ages in seconds, not minutes, so our 120s expiry is far too generous and our first action must be re-grounded, not trusted. PUSV itself is directly usable as a cheap pre-dispatch check: a pixel diff at the target plus a DOM re-read costs under 0.1s and catches focus changes and overlay hijacks. But the 0% AIR on DOM injection is the warning: visual re-verification alone cannot catch a DOM that changed under a correct-looking screenshot, so our pre-dispatch check must include a DOM re-read (element still present, rect unchanged), not only pixels. That matches our stack: DOM rects are exact, vision is 58.6%.
