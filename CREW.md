# Crew

## Roles

- **Codex** — architecture, integration, and final verification.
- **CommandCode** — small edits and tests within assigned files.
- **OpenCode** — clearly guided routine work and explicitly approved sync to
  the installed directory.
- **agy** — independent review and evidence for findings.

## Task handoff

Delegate through a CLI or API with a concrete task, allowed files, and checks.
Each agent returns a report of changes, check results, and unresolved issues;
Codex integrates and verifies the result. Avoid overlapping file ownership.
Multiple open terminals do not imply shared context. Verify the actual CLI/API
transport before claiming coordination.

Before starting a task, read the full instructions for the required skills
`i-have-adhd` and `ponytail`. Keep reports compact and implementation minimal
while preserving safety and everything the user requested.

## Ground rules for every agent

1. Give GUI control to one agent at a time and coordinate handover with the
   user and other agents. Honor an existing user handover within the authorized
   task; do not require fresh permission for every `act`, `click`, or `type`.
   `observe` does not take focus by default; `observe --window ADDRESS --focus`
   explicitly takes focus and may switch workspace.
2. Edit assigned repository files only. OpenCode may sync to the installed
   directory only with explicit approval.
3. This repository is public. Keep credentials, cookies, window titles, PIDs,
   and personal absolute paths out of committed content.
4. Support code claims with `file:line` and test or measurement results.
   Mark unverified claims OPEN; never invent numbers.
5. Disagree in writing with evidence. Preserve the requested removal of the
   cursor magnifier.
