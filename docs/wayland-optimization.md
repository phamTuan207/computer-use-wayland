# Further Wayland research and image-path measurements

## Findings

[hypruse](https://github.com/IlyasKhallouki/hypruse/tree/0035d86db6679aca6a341331b8e60033a07d2670)
is a closely related Hyprland implementation. Its
[`_package` path](https://github.com/IlyasKhallouki/hypruse/blob/0035d86db6679aca6a341331b8e60033a07d2670/src/hypruse/server.py#L233)
writes encoded screenshot bytes directly. Its semantic targeting and action
sequences are useful architectural comparisons, not evidence it is faster or
safer on this host. Its screenshot retry loop captures again; it is not a
persistent-frame cache.

[wayland-mcp](https://github.com/kurojs/wayland-mcp/tree/6d4622daa4b82a0e07740a7ad8215c63d45ae255)
caches the selected capture backend, not a screenshot frame. Its chain processor
stops after errors. [wayshot](https://github.com/waycrate/wayshot) offers native
wlroots capture and an embeddable library; no rewrite, installation or comparative
runtime benchmark of these external projects was performed here.

## Changes adopted

Native desktop observations use PNG compression level 1 instead of 2, still
lossless. Browser screenshots can reuse their original PNG bytes when the decoded
image is RGB, single-frame, contains no metadata, and needs no resizing. A strict
chunk check accepts only IHDR/IDAT/IEND without trailing bytes. Other inputs are
decoded, converted to RGB, stripped of metadata and encoded again. Pixel hashing,
private PNG/JSON permissions, resize geometry and session checks remain intact.

No JPEG was substituted in the safety comparison path. The small PNG file-size
changes do not establish model-token savings: the model sees the same pixels.

## Measurements

PNG encoding only (milliseconds; decoding verified exact pixels after each run):

| Image | Level 2 median | Level 1 median | Level 2 bytes | Level 1 bytes |
|---|---:|---:|---:|---:|
| Actual desktop 1280x800 | 39.515 | 32.506 | 687,870 | 712,804 |
| Text fixture 1280x800 | 12.023 | 12.118 | 92,273 | 96,169 |
| Noise fixture 1280x800 | 39.440 | 37.373 | 1,524,782 | 1,531,181 |
| Text crop 300x300 | 1.220 | 1.210 | 11,510 | 12,008 |
| Actual GTK fixture 924x1176 | 18.880 | 18.088 | 176,787 | 184,862 |

The actual desktop comparison used eight samples per level; all other rows used
twelve and alternated level order. Small/text images show negligible differences,
including a small regression within normal timing noise. Compression level 1
trades somewhat larger files for faster encoding on more detailed images.

On an isolated real Chromium fixture, a 925x494 RGB screenshot processed and
saved with level-1 re-encoding took 7.701 ms median; reusing its original PNG took
3.858 ms median (twelve alternating samples per path). Files were 22,457 versus
16,472 bytes. This includes decode, save, hash and cache housekeeping, but not
CDP capture, browser startup or model reasoning. Additional PNG eligibility
checks were added after this measurement. Repeating on the synchronized installed
build with those checks gave 8.092 versus 4.201 ms, with the same file sizes and
twelve alternating samples. Final source suite: 253 tests with one optional
skip (21.312 seconds); capture/adapter regressions passed. The installed real
Chromium fixture passed 12/12 trusted clicks, Unicode, crop mapping, drag-drop,
Ctrl+T/Ctrl+W and rejection of stale/covered/changed-screen targets.

Cache scanning measured 0.836 ms median for 282 observation files (twelve runs).
It was not rate-limited: current evidence does not justify extra cleanup state.

## Reproduce

```sh
python3 tests/control_benchmark.py --samples 12 --window 0xADDRESS --crop X Y W H
python3 tests/control_benchmark.py --samples 12 --png /path/to/fixture.png
```

The first command captures a visible inert fixture without changing focus or
sending input. The second reads an existing image and creates disposable local
benchmark files; neither prints its image, window identifier or input path.
The helper verifies decoded pixels, but timings vary with image content and host
load. It does not contact a model API.
The `reuse` label means the eligible-byte path was requested, not that every input
qualifies; `original_bytes_preserved` reports whether the original bytes survived.
Images requiring fallback can therefore show no speedup. Chunk filtering does
not remove sensitive content embedded in the image pixels or prove that the
compressed IDAT stream contains no covert data.

Persistent CDP connections, native in-process capture and accessibility coverage
remain potential experiments. They have not demonstrated a further safe speedup
here; advertised speedups from other machines are not local measurements.
