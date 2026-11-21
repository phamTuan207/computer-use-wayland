# Worker CLICK3: last30days skill path unification (laptop)

- Worker: CLICK3-SKILL-PATH, owner Pham Tuan
- Start: 2026-11-22 04:33 +07. Symlink live: 04:36 +07. Log written: 04:37 +07.
- Decision implemented: canonical last30days copy on the laptop is ~/.agents/skills/last30days/ (standard agent skills dir, dated 02:14, 197 files). The workspace copy at /home/james/workspace/custom-skills/last30days/ is now a symlink to it, so the two copies cannot drift.

## 1. Which agent loads skills from which path (laptop, james)

- ~/.agents/skills/ : canonical agent-skills dir. Holds last30days as a real dir (197 files, dated 2026-11-22 02:14), installed by `npx skills add mvanhorn/last30days-skill -g`.
- ~/.claude/skills/last30days : SYMLINK already (created 02:14) pointing to ../../.agents/skills/last30days. Claude Code, and fcc-claude (the ~/.local/bin/fcc-claude wrapper), load the canonical copy through a symlink. This is the established pattern on this machine.
- ~/.codex/skills/ : NO last30days entry. ~/.codex/config.toml has no skills path setting. Its dir holds symlinks into ~/.agents/skills for other skills (gsap-*, omacal, taste-reference) and into /usr/share/omarchy for omarchy skills. Codex follows symlinks into the canonical dir.
- ~/.config/opencode/skills/ : NO last30days entry. Many symlinks into ~/.agents/skills (gsap-core, gsap-frameworks, gsap-performance, gsap-plugins, gsap-react, gsap-scrolltrigger, gsap-timeline, gsap-utils, omacal, taste-reference). Opencode follows symlinks too.
- agy (/usr/bin/agy): no config dir (~/.config/agy and ~/.agy do not exist). Help shows skill expansion support and --add-dir. No evidence it reads the workspace path.
- fcc: no `fcc` on PATH; the launcher is ~/.local/bin/fcc-claude, a Claude Code wrapper, so it loads ~/.claude/skills, which already symlinks to canonical.
- ~/workspace/custom-skills/ : contained ONLY last30days. No laptop config references this path (grep over ~/.codex/config.toml, ~/.config/opencode/opencode.json, ~/.claude.json, ~/.agents found nothing). No agent loads ONLY from the workspace path.
- Conclusion: no agent needs a real directory at the workspace path. A symlink is safe. The "do not symlink, remove instead" exception does not apply.

## 2. Drift check (before the change)

- diff -rq canonical vs workspace: 197 files, exactly 1 differed: scripts/lib/pipeline.py.
- Canonical pipeline.py: 366051 bytes, 2026-11-22 02:14. Workspace pipeline.py: 368798 bytes, 2026-11-22 03:09, with 58 extra lines: a _comment_candidates() function (comment-enrichment candidate picker).
- SKILL.md identical in both (md5 5b69df66a3a716fc21c0f6775284bef6, version 4.5.0).
- So the copies HAD already drifted: the later workspace install carried a newer pipeline.py.
- The full diff is preserved at improvements/worker-click3-skill-path-pipeline-diff.txt (71 lines). The pre-change listing is at improvements/worker-click3-skill-path-backup-ls-R.txt (224 lines). Neither file is committed with this log.

## 3. Implementation (04:36 +07)

- Backed up the listing first: ls -R of the workspace copy to worker-click3-skill-path-backup-ls-R.txt. No 19M copy made.
- Saved the pipeline.py diff to worker-click3-skill-path-pipeline-diff.txt.
- rm -rf /home/james/workspace/custom-skills/last30days ; ln -s /home/james/.agents/skills/last30days /home/james/workspace/custom-skills/last30days
- Verify: readlink returns /home/james/.agents/skills/last30days; md5sum of SKILL.md identical through both paths (5b69df66a3a716fc21c0f6775284bef6); find -L through the symlink counts 197 files; pipeline.py through the symlink is the canonical 366051-byte version. (Plain find without -L counts 0 because it does not follow the symlink; that is expected, not a failure.)

## 4. Result

- Single canonical copy at ~/.agents/skills/last30days/. Both the workspace path and ~/.claude/skills/last30days are symlinks to it. The two laptop copies cannot drift anymore.
- OPEN ITEM for coordinator: the workspace-only _comment_candidates code is NOT in the canonical copy now. If that function is wanted, merge it into ~/.agents/skills/last30days/scripts/lib/pipeline.py (or reinstall the skill from upstream) and re-verify. I did not merge it: the brief names the 02:14 copy canonical, and merging would change canonical content without a decision.
- Elapsed: start 04:33, symlink live 04:36, log written 04:37. No stuck time. No Zen tabs, Zalo, Teams, music, or indicator.py touched. No ydotool used.
