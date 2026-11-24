# Task Specification: [TASK NAME]

**Run code / branch**: `[e.g. R3-L2, or the feature branch]`

**Created**: [DATE]

**Status**: Draft

**Input**: Owner direction or council decision: "[quote the direction]"

> Who may read this spec: coordinators and the parent only. NEVER give this spec to
> an A1 executor (it contains acceptance criteria, i.e. the expected outcome, and
> would break blinding) and NEVER give it to a scorer for the task being scored
> (it is equivalent to the answer key). The executor is briefed from the runbook
> only; the scorer sees only the evidence snapshot plus the frozen key.

## User Scenarios & Testing *(mandatory)*

Write each scenario as a journey, prioritized P1, P2, P3. Each scenario must be
independently testable: if only that scenario is done, it still delivers value.

### Scenario 1 - [Brief Title] (Priority: P1)

[Describe this journey in plain language: who does what, in what order.]

**Why this priority**: [Explain the value and why it has this priority.]

**Independent Test**: [How this can be tested on its own, and what value it delivers.]

**Acceptance Scenarios**:

1. **Given** [initial state], **When** [action], **Then** [expected outcome]
2. **Given** [initial state], **When** [action], **Then** [expected outcome]

---

### Scenario 2 - [Brief Title] (Priority: P2)

[Describe this journey in plain language.]

**Why this priority**: [Explain the value.]

**Independent Test**: [How this can be tested on its own.]

**Acceptance Scenarios**:

1. **Given** [initial state], **When** [action], **Then** [expected outcome]

---

[Add more scenarios as needed, each with a priority.]

### Edge Cases

- What happens when [boundary condition]?
- How does the run handle [error scenario, e.g. service 429, session death, broker expired]?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The run MUST [specific capability, e.g. "produce all 8 evidence items"]
- **FR-002**: The coordinator MUST [specific duty, e.g. "verify the session is free by fd scan before issuing the run"]
- **FR-003**: The runner MUST [specific behavior, e.g. "stop after the current task and wait, never start the next task unprompted"]
- **FR-004**: The ledger MUST [specific record, e.g. "record both scorer verdicts with timestamps before the reset-log entry"]
- **FR-005**: The evidence MUST [specific property, e.g. "be hash-verified against the frozen list before scoring"]

*Marking unclear requirements (max 3 markers total in the whole spec):*

- **FR-006**: The run MUST use [NEEDS CLARIFICATION: which runner, FCC or Codex, if the session is contended?]
- **FR-007**: The pass bar is [NEEDS CLARIFICATION: recompute or keep 53/55 if a task drops out unreplaced?]

### Evidence Requirements

- **EV-001**: Evidence directory and its required items (list each file).
- **EV-002**: Hash / snapshot rule (what is hashed, where the snapshot is committed).
- **EV-003**: Log rule (which log file, wall-clock + elapsed, what each entry records).

### Key Entities *(include if the work involves data)*

- **[Entity 1]**: [What it represents, key attributes, no implementation.]
- **[Entity 2]**: [What it represents, relationships.]

## Success Criteria *(mandatory)*

Measurable, technology-agnostic where possible, verifiable without implementation details.

- **SC-001**: [Measurable metric, e.g. "All 12 runs have all 8 evidence items and a Stage 1 verdict"]
- **SC-002**: [Measurable metric, e.g. "Ledger has one row per graded task, each with both scorer verdicts and timestamps"]
- **SC-003**: [Measurable metric, e.g. "Zero overlaps between FCC and Codex task assignments"]
- **SC-004**: [Measurable metric, e.g. "Session contention causes zero voided runs"]

## Assumptions

- [Assumption about scope, e.g. "The frozen list and keys do not change during this work"]
- [Assumption about the fleet, e.g. "FCC and Codex runners stay available for the whole queue"]
- [Assumption about the session, e.g. "The single computer-use session is shared under P1-P10"]
- [Dependency, e.g. "Requires the R3-L2 freeze hashes to stay valid"]

## Quality Checklist

Validate the spec before planning. All items must pass.

- [ ] No implementation details (languages, frameworks, APIs) in the spec itself
- [ ] Focused on what the run must achieve and why
- [ ] No [NEEDS CLARIFICATION] markers remain (or at most 3, each answered)
- [ ] Requirements are testable and unambiguous
- [ ] Success criteria are measurable
- [ ] Evidence requirements name every file and hash rule
- [ ] Blinding note is present and correct (who may and may not read this spec)
- [ ] No personal info anywhere in the spec
- [ ] Scope is clearly bounded; no speculative or "might need" items

## Notes

- Items marked incomplete require spec updates before planning.
- If a [NEEDS CLARIFICATION] marker remains, present the question with options to
  the parent and wait for the answer; do not guess on a scope, security, or
  privacy decision.
- After the spec is approved, the plan follows (technical approach + constitution
  check), then tasks (numbered, [P] for parallel-safe work), then implementation.
