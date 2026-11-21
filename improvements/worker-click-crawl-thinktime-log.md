# CLICK-CRAWL-THINKTIME log

Worker: CLICK-CRAWL-THINKTIME (research crawler, COORD-CLICK)
Topic: reducing agent think time while keeping accuracy >= 90%
Scope: computer-use-wayland project only. Crawling + candidate list only. No implementation, no live tests, no live driving, no browser tasks.
Started: 2026-11-22 02:05:29 Asia/Ho_Chi_Minh
Finished crawl: 2026-11-22 02:10 Asia/Ho_Chi_Minh (elapsed about 00:05)
Method: Scrapling 0.5.1 plain Fetcher only (StealthyFetcher blocked by VM proxy, NOT used). Fallback: browser.search to discover URLs + correct arXiv IDs, browser.open not needed because Scrapling succeeded on every target. Every Scrapling failure or wrong-ID fetch recorded below.
Goal bar: one vision (one observation) drives as many actions as possible, total task time reduced as much as possible, accuracy >= 90%. One vision, max actions, minimal total time, accuracy >= 90%.

## Baseline from task (what we must beat)
- Think-observe-think loop is ~87.8% of task time in prior measurements.
- A 3-6 operation task taking 5 minutes is way too slow.
- Codex send took 2.5 minutes and must be beaten.
- Screenshots today are JPEGs read by eye (slow); goal is DOM/a11y rects instead.
- Stack: Python, Hyprland/Wayland, Zen/Brave, wtype, grim.
- Acceptance benchmark (owner, 02:05-02:09): 2-vision task, clone1 + clone2 on ws2, VISION 1 finds ALL input boxes + buttons for both, one script/workflow (no vision) clicks + sends for both, VISION 2 checks both sent. Runs AFTER improvements look good, not before. Order: (1) research + improve one-vision, (2) run 2-vision benchmark to prove it, (3) then todolist + error-file fixes. Use existing tools/methods where they exist, build our own where they do not. Result matters, method is free.
- NOTE on data freshness (owner, 02:09): team should also use last30days-skill for real data from the last 30 days only. This crawl was assigned Scrapling method, so it used Scrapling; several sources below ARE Nov 2026 papers (VTR, HDM, capability routing) inside 30 days, provider docs are current, older papers are flagged as foundational. A dedicated last30days-skill re-crawl is a suggested follow-up, not done in this task.

## 02:05:40 +07 (elapsed 00:00:11) - setup
- Repo ~/workspace/computer-use-wayland, branch todolist-push, git fetch origin done, HEAD in sync with origin/todolist-push after fetch (no local ahead commits).
- Scrapling venv ~/workspace/scrapling-trial-venv, scrapling 0.5.1 confirmed.
- Scrapling API notes (learned live): Fetcher.get(url, timeout=30) works; page.text is empty on JS-heavy docs; page.markdown() is a METHOD returning str; page.get_all_text() returns a TextHandler. First script failed with adaptor_arguments kwarg (TypeError), then with .html attribute (no such attr), then with len(page.markdown) (method, not property). Fixed script saved at /tmp/thinktime_fetch.py; batch scripts at /tmp/thinktime_batch.py, /tmp/thinktime_batch2.py, /tmp/thinktime_batch3.py, /tmp/thinktime_batch4.py. Raw fetched markdown saved under /tmp/thinktime/ (26 files).

## 02:06-02:10 +07 - crawl runs
- Batch 1 (18 URLs, all 200): Anthropic prompt caching, OpenAI prompt caching, Anthropic computer-use tool, Anthropic parallel tool use, Anthropic context editing, Anthropic fast mode, OmniParser arXiv, ScreenSpot arXiv, ScreenSpot-Pro arXiv, UI-TARS arXiv, OSWorld arXiv, SeeClick arXiv, OS-Atlas arXiv, Florence-2 arXiv, Grounding DINO arXiv, LLMLingua arXiv, OmniParser GitHub, browser-use GitHub. All plain Fetcher, 1.0-5.4s each.
- Batch 2 (8 URLs, all 200): datarekha latency post, OSWright PyPI, OSWright GitHub, VTR arXiv, Anthropic vision docs, Anthropic effort docs, Anthropic context-engineering blog, OpenAI latency optimization.
- Batch 3 (6 URLs, all 200): corrected SeeClick + ScreenSpot-Pro arXiv IDs, openadapt literature review, Florence-2 + LLMLingua re-fetch, browser-use speed post.
- Batch 4 (4 URLs, all 200): HDM arXiv 2611.16961, capability-routing arXiv 2611.16414, R2R arXiv 2505.21600, Local-Splitter arXiv 2604.12301.
- browser.search runs (3): screenshot-token reduction (found OSWright, VTR, datarekha), grounding literature (found correct arXiv IDs + ScreenSeekeR numbers), reasoning-token reduction (found HDM, R2R, capability routing, Local-Splitter).
- WRONG arXiv IDs caught (first batch, my IDs, not source errors): 2401.07113 returned a planetary-integrator paper, not ScreenSpot; 2503.02235 returned a persistent-excitation paper, not ScreenSpot-Pro; 2309.07872 returned a DDP optimal-control paper, not SeeClick; 2410.13629 returned a cell-biology review, not OS-Atlas. Corrected IDs verified by search: SeeClick arXiv:2401.10935, ScreenSpot-Pro arXiv:2504.07981. OS-Atlas correct ID NOT verified in this crawl, so no OS-Atlas numbers are cited below. Florence-2 and LLMLingua first fetched empty markdown; re-fetch in batch 3 returned their abstracts.
- Scrapling proxy note: plain Fetcher worked on all 30 fetches (arXiv, GitHub, Anthropic docs, OpenAI docs, blogs, PyPI). Zero proxy failures in this crawl. StealthyFetcher never used.

## Candidates

### C1. Batched actions: one vision, many actions, executed blind in order
- What it is: the agent plans a short sequence (click, type, click, type) from ONE screenshot and returns all actions in one response; the harness runs them in order and stops at the first failure. This is exactly the one-vision-max-actions shape: Anthropic formalises it as batch actions in the computer-use toolset, and datarekha lists batched actions as technique 4.
- Source: Anthropic computer-use docs, https://docs.anthropic.com/en/docs/build-with-claude/prompt-caching (fetched, redirected to platform.claude.com) and https://docs.anthropic.com/en/docs/agents-and-tools/tool-use/computer-use-tool ; datarekha "Computer-use latency engineering: getting browser agents under a second", https://datarekha.com/blog/computer-use-latency-engineering/ . Accessed 2026-11-22.
- Goal bar: directly cuts think time (one LLM call instead of one per action) and total time; fewer observations. This is the core mechanism for the 2-vision benchmark.
- Applicability to our stack: our loop today is one screenshot per action. Change: add a batch-action executor in Python (run wtype/grim/hyprctl steps in order, stop on first failure, return per-block success/failure like Anthropic requires), and prompt the agent to emit the full predictable sequence (e.g. click input 1, type, click send, click input 2, type, click send) from one observation. Needs DOM/a11y rects (C2) to make blind execution safe, since blind clicks on JPEG-guessed coords are what failed before.
- Numbers: datarekha: naive loop 4-8s per step, production systems 600ms per step; batched actions amortise the LLM call across 3-4 actions. No isolated accuracy number for batching alone in these sources.
- Verdict: promising - the central candidate, already the shape of the acceptance benchmark.

### C2. DOM/a11y-first observation, screenshots only when needed
- What it is: navigate and act primarily from the DOM / accessibility tree (exact element rects, roles, names), and capture a screenshot only when visual context is actually necessary. Browser-use 1.0 does this; its extract tool queries page markdown from the DOM instead of dumping 20,000+ tokens of page text into context.
- Source: Browser-use "Speed Matters: How Browser Use Achieves the Fastest Agent Execution", https://browser-use.com/posts/speed-matters (Scrapling 200, accessed 2026-11-22); browser-use repo https://github.com/browser-use/browser-use (Scrapling 200).
- Goal bar: kills the slowest input (screenshot encode ~0.8s per step per browser-use) and the biggest token cost; fewer vision passes = lower think time and lower total time.
- Applicability: our stated direction already (DOM/a11y rects instead of JPEGs read by eye). Change: build a DOM/a11y snapshot tool for Zen/Brave (via CDP or accessibility APIs) returning element rects in screen coords; screenshot becomes the fallback for canvas/non-DOM UI (e.g. Messenger web app contenteditable areas). Directly attacks the root cause proven 01:46 (vision misread, click 64-75px above the real input box).
- Numbers: each screenshot adds ~0.8s LLM inference latency (browser-use published numbers); BU 1.0 averages 3s per step with its strongest model vs 225-330s per task for vision-heavy rivals (Gemini 2.5 Computer Use 225s, Claude Sonnet 4.5 285s, Sonnet 4 295s, OpenAI Computer-Using Model 330s); BU 1.0 65.7% accuracy on OnlineMind2Web.
- Verdict: promising - the highest-leverage structural change, and the one the owner already ordered.

### C3. Prompt caching with cache-aware ordering (history before fresh screenshot)
- What it is: put the stable prefix (system prompt + history) first so it hits the prompt cache, and the fresh screenshot LAST. Anthropic: 5-min default TTL, 1-hour TTL available; cache reads are far cheaper than full reprocessing. Browser-use fixed the same bug: history before browser state lets the whole history hit the KV cache.
- Source: Anthropic prompt caching docs, https://docs.anthropic.com/en/docs/build-with-claude/prompt-caching (Scrapling 200); OpenAI prompt caching guide, https://platform.openai.com/docs/guides/prompt-caching (Scrapling 200); browser-use speed post (above); datarekha technique 1 (above). Accessed 2026-11-22.
- Goal bar: lower think time (time to first token on cached prefix) and lower cost; no accuracy change.
- Applicability: applies to any API-based agent loop we run (Muse/Codex style calls). Change: order every request as [system, history, task, fresh screenshot last]; enable 1-hour cache for long loops; never put changing content before the stable prefix or the cache breaks every turn.
- Numbers: Anthropic 1-hour cache cuts cost up to 90% and latency up to 85% on cached prefixes (per datarekha citing Anthropic); on a 10K-token system+history prefix, 5-10x cost reduction and 85ms shaved off TTFT for the cached portion.
- Verdict: promising - cheapest win, zero code risk, do it in every loop.

### C4. Differential / diff-based observations (send the delta, not the full screen)
- What it is: after each action, compute a perceptual hash or bounding-box diff vs the previous screenshot. If the diff is below threshold, do NOT send a full screenshot; send a small textual delta ("the dropdown at (340,220) opened") plus a reference to the previous screenshot already in cached context. OSWright generalises it: ask the compositor what changed, rescan only that region.
- Source: datarekha technique 2 (above); OSWright, https://pypi.org/project/oswright/ and https://github.com/Ask-812/oswright (Scrapling 200, accessed 2026-11-22).
- Goal bar: fewer vision tokens per step, lower think time, lower total time; accuracy held by construction (full re-observe when the diff is large).
- Applicability: very direct for our stack. Change: in the loop, grim-capture, compare with previous frame (pixel diff / perceptual hash in Python, cheap), and if unchanged/small, skip the vision call and report a text delta; only re-observe on real change. OSWright's numbers come from a Windows compositor, but the diff idea ports to grim + Python PIL/numpy on Hyprland.
- Numbers: datarekha: 40-50% cut in average vision-token cost per step, under 2% degradation on test sets; 60-70% of steps change little. OSWright: median observation changes 0.012% of pixels; full screenshot costs ~2,800 image tokens whether anything changed or not; incremental perception ~21x fewer tokens per step; same task 7.4x less context than screenshot-every-step; accuracy identical across configurations while token cost falls 23x.
- Verdict: promising - second-biggest win after C1/C2, and cheap to prototype (diff is pure local compute).

### C5. Speculative perception: predict the result, verify cheaply, re-observe only on surprise
- What it is: learn what each action does (e.g. click send -> message bubble appears) and CONFIRM the expected result with a cheap check instead of a full re-observe; only pay for a full observation when the check reports a surprise. OSWright calls this speculative perception; datarekha technique 6 is the LLM version (verifier stream).
- Source: OSWright (above); datarekha technique 6 (above). Accessed 2026-11-22.
- Goal bar: removes most verification observations, which are pure think time; total time falls; accuracy held by the surprise path.
- Applicability: matches the owner rule "verify by re-checking without vision if possible" (02:06). Change: after a blind batch (C1), verify via DOM/a11y state or pixel checks (e.g. message bubble count in DOM, pixel diff in the sent-message region) instead of a second vision pass; VISION 2 in the benchmark becomes the only vision verification, and only if the cheap check is inconclusive.
- Numbers: OSWright: speculative check 19-23x cheaper than observing (2.3ms vs 43-50ms); screen memory 89x cheaper (125ms cold read to 1.4ms warm recall); adaptive waiting saves 11.9s over a 50-step task.
- Verdict: promising - the direct implementation of "verify without vision", pairs with C1.

### C6. Small local grounding model: OmniParser (YOLO detector + Florence-2 captioner) instead of a VLM for coords
- What it is: parse the screenshot locally into structured elements (boxes + semantics) with a fine-tuned YOLO icon detector + Florence-2 caption model + OCR, then give the big model text + boxes instead of asking it to eyeball pixels. Runs locally, no VLM round trip for grounding.
- Source: OmniParser paper, https://arxiv.org/abs/2408.00203 (Scrapling 200, 2024 paper); OmniParser repo https://github.com/microsoft/OmniParser (Scrapling 200); openadapt literature review https://github.com/openadaptai/openadapt-grounding/blob/HEAD/docs/literature_review.md (Scrapling 200, accessed 2026-11-22).
- Goal bar: grounding becomes fast local compute instead of a slow vision think; accuracy up on grounding benchmarks.
- Applicability: strong fit. Change: run OmniParser v2 (YOLOv9-E detector, Florence-2 captioner, MIT-licensed parts) on the laptop (RTX 4050, 32GB) over grim screenshots; feed its element list (box + label) to the agent as the observation, with the screenshot attached only when needed. This is the "DOM for non-DOM apps" path where no a11y tree exists (Messenger web app, canvas UI).
- Numbers: OmniParser + GPT-4V greatly improves ScreenSpot over GPT-4V alone; OmniParser v2 39.5% on ScreenSpot-Pro (vs GPT-4o alone 0.8% per lit review, +4,850%); UI-TARS 1.5 is 61.6% on ScreenSpot-Pro, so local grounding still trails the best end-to-end models on hard pro apps. No latency number published in the abstract; local YOLO inference is milliseconds on GPU.
- Verdict: promising - best local-grounding option, especially as the fallback when DOM/a11y is unavailable. Needs a live accuracy/latency measurement on our screens before trusting it.

### C7. Screenshot downscale / resize to the model's visual-token tier
- What it is: resize screenshots before upload so they fit the model's cheapest tier (Anthropic: visual tokens = ceil(width/28) x ceil(height/28); older models cap at 1,568px long edge / ~1.15MP, newer at 2,576px / 4,784 visual tokens). Oversized images are downscaled by the API anyway, so pre-resizing saves upload + encode time.
- Source: Anthropic vision docs, https://docs.anthropic.com/en/docs/build-with-claude/vision (Scrapling 200); Anthropic computer-use docs (above, "long agent loops accumulate screenshots quickly, roughly 1,000-1,800 input tokens each"). Accessed 2026-11-22.
- Goal bar: fewer tokens per observation, lower think time; small accuracy risk if downscaled too far (tiny targets blur).
- Applicability: trivial. Change: in the grim capture path, downscale to the tier limit (and to ~1280px long edge as realhands does) with LANCZOS before sending; keep a full-res crop path for small targets (see C13).
- Numbers: 1,000-1,800 input tokens per screenshot in a loop (Anthropic); image cost is exactly ceil(w/28) x ceil(h/28) visual tokens, so halving each dimension quarters the token cost.
- Verdict: promising - free, immediate, do it now; pair with cropped re-reads for small targets.

### C8. Context editing: keep only the latest screenshot, clear old tool results
- What it is: as the loop grows, clear old screenshots / tool results from history (Anthropic context editing, tool-result clearing with clear_at_least) and compact before hitting request limits. Old screenshots still count toward image limits even after clearing, so compact early. Anthropic's context-engineering post states the principle: context is a finite resource with diminishing returns, and irrelevant tokens degrade focus (context rot).
- Source: Anthropic context editing docs, https://docs.anthropic.com/en/docs/build-with-claude/context-editing (Scrapling 200); Anthropic "Effective context engineering for AI agents", https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents (Scrapling 200). Accessed 2026-11-22.
- Goal bar: shorter context = faster prefill/TTFT and better accuracy (less context rot); lower total time on long tasks.
- Applicability: direct. Change: in our loop, retain only the latest 1-2 screenshots in context, clear older tool results with a minimum-clear threshold so cache invalidation is worth it, and trigger on-demand compaction before the loop reaches image-count limits.
- Numbers: no single headline number in these docs; the mechanism is quadratic attention (n squared pairwise relationships) so context growth hurts superlinearly; context-rot studies show recall degrades as token count rises.
- Verdict: promising - standard practice, low risk, big effect on long tasks.

### C9. Lower reasoning effort / fewer output tokens (effort parameter, low mode)
- What it is: cap how many tokens the model spends answering (Anthropic effort parameter: low/medium/high; OpenAI reasoning_effort). For UI loops the computer-use docs say low effort uses FEWER output tokens than disabling thinking entirely, because fewer mistakes mean fewer retries; medium is the best accuracy-to-cost ratio on Sonnet/Opus 4.6, avoid max (adds token cost without improving UI accuracy).
- Source: Anthropic effort docs, https://docs.anthropic.com/en/docs/build-with-claude/effort (Scrapling 200); Anthropic computer-use docs (above, effort guidance). Accessed 2026-11-22.
- Goal bar: fewer output tokens = less think time per step, fewer retries; accuracy held or improved on routine UI steps.
- Applicability: direct for API-based loops. Change: set effort low for routine grounding/action steps, medium for planning steps; never max for UI tasks. For our own agents, the equivalent is a short-output prompt (coordinates + action only, no chain-of-thought prose).
- Numbers: qualitative in docs (no headline %); the "low beats no-thinking" claim is the key evidence that short reasoning can raise accuracy on UI tasks by cutting retries.
- Verdict: promising - free, and the accuracy direction is favourable, not a trade-off.

### C10. Adaptive waiting: wait for the screen to settle, not a fixed sleep
- What it is: after an action, poll for visual change / settle instead of sleeping a fixed 300ms. Fixed sleeps waste time on fast steps and are too short on slow ones.
- Source: OSWright (above). Accessed 2026-11-22.
- Goal bar: lower total time with zero accuracy cost; also fewer premature observations (which cause wrong reads and retries).
- Applicability: trivial for our stack. Change: replace fixed sleeps in the loop with a wait_for_change poll on grim frames (or DOM mutation wait), with a timeout cap.
- Numbers: 11.9s saved over a 50-step task (OSWright measured).
- Verdict: promising - trivial, zero risk, do it with any loop change.

### C11. Small-model routing: cheap model decides, big model only when needed
- What it is: a small local model (or a cheap API model) triages each step: trivial steps it handles or routes, hard steps go to the big model. Variants: R2R token-level routing (small model drafts, big model only on divergent tokens); HDM zero-or-T thinking (answer in one forward pass with zero reasoning tokens, escalate to full reasoning only when the value of thinking is high); capability routers (small model switches reasoning/retrieval/search on or off per query).
- Source: R2R, https://arxiv.org/abs/2505.21600 (Scrapling 200, May 2025); HDM "The Value of Thinking", https://arxiv.org/abs/2611.16961 (Scrapling 200, Nov 2026); capability routing, https://arxiv.org/abs/2611.16414 (Scrapling 200, Nov 2026); Local-Splitter, https://arxiv.org/abs/2604.12301 (Scrapling 200, Apr 2026). Accessed 2026-11-22.
- Goal bar: most steps are routine (click a known button), so most think time is wasted big-model reasoning; routing cuts it while the big model still handles hard steps.
- Applicability: medium. Change: two-tier loop, small local model (Qwen2.5 1.5-7B on the RTX 4050 via Ollama, or a cheap API model) handles "did anything change" gates and routine grounding, big model only for planning and failures. This is the same shape as C7's gate (datarekha technique 3) but with measured routing papers behind it. Needs local-model infra we do not have yet.
- Numbers: R2R: 2.8x wall-clock speedup vs R1-32B at comparable performance, 92% of R1-32B accuracy; HDM: up to 80% compute reductions; capability router (14B): downstream tokens down 68.7% (8,837 to 2,764), median latency down 80.5% (9.79s to 1.91s) at equal quality (BERTScore F1 0.8408 vs 0.8418 all-on); Local-Splitter: local routing + prompt compression 45-79% cloud token savings on edit/explanation workloads.
- Verdict: promising as a pattern, maybe as an immediate build - the numbers are the strongest in this crawl, but it needs a local small-model runtime first; start with the cheap gate version (C7 in datarekha terms) and grow to full routing.

### C12. Visual Token Routing (VTR): learn which screenshot regions matter, drop the rest
- What it is: train a lightweight spatio-temporal router with the vision-language model; it decides per image region (current vs previous screenshot) whether its visual token enters the model. Drops semantically irrelevant and temporally redundant tokens.
- Source: "Visual Token Routing: Learning to keep tokens that matter", https://arxiv.org/abs/2611.06854 (Scrapling 200, Nov 2026; also https://arxiv.org/html/2611.06854v1 via search). Accessed 2026-11-22.
- Goal bar: fewer visual tokens = faster prefill and cheaper inference, accuracy matched.
- Applicability: low for us directly. Change: would need training (2,000 steps) and a VLM we control; we drive vendor models (Muse/Codex), so we cannot insert a router. The idea ports only as inspiration: crop to the changed region (C4) and downscale (C7) are the no-training versions.
- Numbers: 2.5-5.8x fewer visual tokens, inference cost down up to 3.3x, prefill up to 2.9x faster, matches full-resolution performance on OSWorld/CUA-World/video-game action prediction with 2,000 training steps; beats naive downscaling by up to 12.8 points on OSWorld.
- Verdict: maybe - best numbers for token cutting, but needs model training we cannot do on vendor APIs; use its lesson (drop redundant regions) via C4/C7 instead.

### C13. Progressive cropping / ScreenSeekeR: crop to the region, then ground
- What it is: instead of grounding on the full screen, use planner knowledge to recursively crop to candidate regions, then ground inside the crop. Smaller search area = higher accuracy on small targets.
- Source: ScreenSpot-Pro paper, https://arxiv.org/abs/2504.07981 (Scrapling 200, 2025); openadapt literature review (above). Accessed 2026-11-22.
- Goal bar: accuracy up sharply; think time up per grounding (multiple crops) unless the crop replaces a full-screen pass rather than adding to it.
- Applicability: useful as a fallback, not the default. Change: when a target is small or the first grounding is low-confidence, crop around the predicted region and re-ground once at higher effective resolution; never as the default path, or it adds vision passes and breaks the one-vision bar.
- Numbers: ScreenSeekeR 48.1% on ScreenSpot-Pro vs best single-pass model 18.9% (lit review: +254% from progressive cropping); ScreenSpot-Pro has 1,581 instructions across 23 professional apps.
- Verdict: maybe - accuracy win is real but it costs extra vision passes, so it fights the one-vision goal; keep as a low-confidence fallback only.

### C14. LLMLingua prompt compression (up to 20x) for text context
- What it is: coarse-to-fine prompt compression (budget controller + token-level iterative compression) that shrinks long text prompts while keeping semantics.
- Source: LLMLingua, https://arxiv.org/abs/2310.05736 (Scrapling 200, 2023 paper, foundational). Accessed 2026-11-22.
- Goal bar: fewer input tokens = faster prefill, lower think time on text-heavy context.
- Applicability: limited for us. Change: could compress long DOM dumps or long histories before sending; but our direction is to NOT send long DOM dumps at all (C2 extract tool), which dominates compression. Only useful if a long text observation is unavoidable.
- Numbers: up to 20x compression with little performance loss (GSM8K, BBH, ShareGPT, Arxiv benchmarks).
- Verdict: maybe - strong compression, but dominated by C2 (do not send the bulk in the first place); revisit only for long-text steps.

### C15. Fast mode: 2.5x output tokens per second
- What it is: Anthropic fast mode (speed: fast) runs the same model with a faster inference config; no intelligence change, premium pricing.
- Source: Anthropic fast mode docs, https://docs.anthropic.com/en/docs/build-with-claude/fast-mode (Scrapling 200). Accessed 2026-11-22.
- Goal bar: output tokens per second up, so think time down on output-heavy steps; no accuracy change claimed.
- Applicability: only if our loop runs on Claude API with a supported model (Fable/Mythos 5.2, Opus 5.5); output speed is not our bottleneck (our bottleneck is vision input + reasoning per step), and it costs premium pricing.
- Numbers: up to 2.5x higher output tokens per second; benefits are output speed, not time to first token.
- Verdict: maybe - helps output-bound steps only, premium price, not our bottleneck; skip unless profiling shows output speed matters.

### C16. Parallel tool calls for independent read-only tools
- What it is: issue multiple independent tool calls in one turn (Anthropic parallel tool use; OpenAI parallel function calling). Cuts one round trip per extra call.
- Source: Anthropic parallel tool use docs, https://docs.anthropic.com/en/docs/agents-and-tools/tool-use/parallel-tool-use (Scrapling 200); Anthropic computer-use batch actions (C1 source). Accessed 2026-11-22.
- Goal bar: fewer round trips for independent reads; no help for dependent action sequences (those are C1 batch actions, run in order).
- Applicability: narrow. Change: in our loop, parallelise only independent reads (e.g. get window list + get focused window + read clipboard) in one turn; never parallelise clicks/types (ordering + shared state). The computer-use toolset requires sequential batch execution, so this is a complement to C1, not a substitute.
- Numbers: no headline number in the docs; saving is one round trip per parallelised call.
- Verdict: maybe - small, safe win for read-only fan-out; do not confuse with batch actions.

### C17. Predictive prefetch: start the next LLM call while the current action settles
- What it is: during the ~400ms page-settle after an action, start the next LLM call predicting the next action from the trajectory; accept it if it matches reality when the page settles, discard if not.
- Source: datarekha technique 5 (above). Accessed 2026-11-22.
- Goal bar: hides LLM latency behind settle time; total time down when predictions are right, wasted calls when wrong.
- Applicability: complex for our stack. Change: would need a prediction path and a discard path; mispredictions cost extra calls. Only for high-confidence paths (e.g. after clicking send, the next step is almost always a verification observe).
- Numbers: no isolated number in the source; settle time cited ~400ms per action.
- Verdict: maybe - real but complex, misprediction waste; defer until C1/C2/C4 are measured.

### C18. Speculative execution with a parallel verifier stream
- What it is: run two LLM streams, one doing the step and one verifying the action right before execute; abort if the verifier disagrees.
- Source: datarekha technique 6 (above). Accessed 2026-11-22.
- Goal bar: accuracy up (catches bad actions before they land), but costs a second LLM stream, so think time can rise, not fall.
- Applicability: poor fit for the goal bar as written. Change: none now; the cheap verification in C5 (DOM/pixel checks, no LLM) is the better version of this idea for us.
- Numbers: none isolated in the source; noted as used by few production systems because the engineering bar is high.
- Verdict: skip - two LLM calls per step fights the think-time goal; C5 does the same job cheaper.

### C19. End-to-end native GUI model (UI-TARS) as the agent
- What it is: a native GUI agent model that takes only screenshots and outputs actions, trained end-to-end with System-2 reasoning and reflective online traces, instead of a general VLM plus hand-built loop.
- Source: UI-TARS, https://arxiv.org/abs/2501.12326 (Scrapling 200, 2025). Accessed 2026-11-22.
- Goal bar: fewer prompt-engineering round trips; but it is still one vision per action by design, and accuracy on OSWorld is far below 90%.
- Applicability: low now. Change: would mean self-hosting a 7B model and replacing the loop; grounding is strong (61.6% ScreenSpot-Pro per lit review) but task success is not near the bar.
- Numbers: UI-TARS OSWorld 24.6 (50 steps) and 22.7 (15 steps) vs Claude 22.0 and 14.9; AndroidWorld 46.6 vs GPT-4o 34.5; SOTA on 10+ GUI benchmarks at publication.
- Verdict: skip for now - strong grounding research, but a model swap does not deliver one-vision-max-actions and its task accuracy is far under 90%.

### C20. Screen memory: recognise seen screens, reuse instead of re-reading
- What it is: hash screens already read; when the same screen reappears, reuse the stored parse instead of re-observing.
- Source: OSWright (above). Accessed 2026-11-22.
- Goal bar: zero think time for repeated screens (login screens, home screens, repeated dialogs).
- Applicability: niche but real for us (same Messenger thread view, same login screens recur). Change: cache parses keyed by perceptual hash; verify cheaply by pixels before reuse.
- Numbers: 125ms cold read to 1.4ms warm recall (89x cheaper).
- Verdict: maybe - big multiplier on repeated screens, small scope; fold into C4/C5 work rather than a standalone build.

### C21. OSWorld / SeeClick grounding pre-training (background, not a method to adopt now)
- What it is: SeeClick showed GUI grounding pre-training is the key bottleneck for visual agents, and created ScreenSpot; OSWorld is the benchmark showing best models at 12.24% vs humans 72.36% (2024). Included for context: grounding is the known hard part, which is why C2 (avoid grounding by using DOM rects) and C6 (local grounding model) matter.
- Source: SeeClick, https://arxiv.org/abs/2401.10935 (Scrapling 200); OSWorld, https://arxiv.org/abs/2404.07972 (Scrapling 200). Accessed 2026-11-22.
- Goal bar: background only; no direct think-time method.
- Applicability: none directly; use OSWorld-style success rate as a yardstick, not a target (our bar is 90% on our own tasks, not OSWorld).
- Numbers: OSWorld best model 12.24% vs human 72.36% (2024); SeeClick grounding pre-training gives significant ScreenSpot gains over baselines.
- Verdict: skip as a method - benchmark/context only.

## Ranked list (most promising first)
1. C1 batched actions, one vision many actions - the goal itself, benchmark shape.
2. C2 DOM/a11y-first, screenshots only when needed - removes the slowest input and the root cause of the misread clicks.
3. C4 diff-based observations - 40-50% vision-token cut, 21x per-step tokens in OSWright, cheap local compute.
4. C5 speculative perception / verify without vision - removes verification observations, matches the owner rule.
5. C3 prompt caching, cache-aware ordering - cheapest win, 85% latency cut on cached prefixes.
6. C6 OmniParser local grounding - fast local coords where DOM is unavailable.
7. C7 screenshot downscale to token tier - free, immediate.
8. C8 context editing, keep latest screenshot only - long-task speed + accuracy.
9. C9 low effort / minimal output tokens - fewer tokens, fewer retries.
10. C10 adaptive waiting instead of fixed sleep - 11.9s per 50 steps, zero risk.
11. C11 small-model routing - strongest published numbers (2.8x speedup, 80% latency cut), needs local-model infra.
12. C13 progressive cropping as low-confidence fallback only - +254% accuracy, but costs extra vision passes.
13. C12 VTR - best token-cut numbers, needs training, use its lesson via C4/C7.
14. C20 screen memory - 89x on repeated screens, fold into C4/C5.
15. C14 LLMLingua - 20x text compression, dominated by C2.
16. C16 parallel tool calls for independent reads - small safe win.
17. C17 predictive prefetch - complex, defer until C1/C2/C4 measured.
18. C15 fast mode - output-bound only, premium price.
19. C18 speculative verifier stream - skip, two LLM calls per step.
20. C19 UI-TARS model swap - skip for now, accuracy far under bar.
21. C21 OSWorld/SeeClick - background only, not a method.

## Recommended next step (for council + redteam, not this worker)
- Test first, in this order: C1+C2 together (batch executor fed by DOM/a11y rects) on the 2-vision benchmark shape; then add C4 diff-gating and C5 cheap verification; then C3/C7/C8/C9/C10 as free loop hygiene. Measure wall time per task and accuracy on the same tasks before/after; the bar is total time down as much as possible with accuracy >= 90%.
- Suggested follow-up crawl: last30days-skill pass (owner 02:09) for real data from the last 30 days only, to catch newer methods this Scrapling crawl may have missed.

## 02:10 +07 - wrap-up
- Log written. Next: commit with explicit pathspec only, push, verify via git ls-remote.
