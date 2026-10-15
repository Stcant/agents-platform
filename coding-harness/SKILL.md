---
name: coding-harness
description: "Use when starting or resuming development, implementing features, fixing bugs, refactoring, designing or planning changes, reviewing code or feedback, verifying work, maintaining project checkpoints, consolidating harness documents, or understanding an unfamiliar stack, component connections, and change impact."
---

# Coding Harness

Help the user develop working, maintainable software using the project's existing stack and conventions. Keep this skill independent of languages, runtimes, and services.

## Essential Rules

- Inspect applicable instructions, current scope, source, callers/tests, and relevant state before editing. Preserve user changes, public contracts, and declared versions.
- Apply SOLID, KISS, DRY, YAGNI, separation of concerns, explicit contracts, reliability, security, and testability proportionately. Reuse behavior before adding code or dependencies.
- Use configured project checks. Distinguish actual PASS, FAIL, NOT RUN, and N/A; unperformed/failed checks and mock-only integrations cannot establish verified status.
- Keep Git writes, branch operations, destruction, deployment, and publication within specific applicable authorization. CHECKPOINT and a file-edit request alone do not authorize them.
- Do not read secret files or expose confidential data in code, logs, examples, or state.
- Search first, read relevant ranges, batch independent lookups, and load only references needed for a concrete gap.

## Route the Request

| Request / situation | Workflow |
| --- | --- |
| Bare explicit invocation, START, or first explicit development invocation | [Continuity: startup](references/CONTINUITY.md#startup-and-roles). Reuse canonical state and stable map; create at most those two documents. START JSON selects new JSON state; START LEARN explains the stack. |
| START PORTABLE or PORTABLE | Continuity: prepare the same roles plus an explicitly requested complete skill snapshot. No default snapshot, local instruction file, or index. |
| HARNESS STATUS / RESUME / CHECKPOINT / HARNESS MIGRATE | Relevant [Continuity](references/CONTINUITY.md) sections. STATUS is read-only; RESUME reconciles work; CHECKPOINT updates state; MIGRATE reconciles legacy documents without automatic deletion. |
| DESIGN / PLAN / received review feedback | Relevant [Workflow](references/WORKFLOW.md) sections. Assessments are read-only; SAVE stores only the requested proposal/plan; apply fixes when requested. |
| PROJECT MAP / PROJECT MAP LEARN / named area / CHANGE IMPACT | [Project Mapping](references/PROJECT_MAP.md). Read-only by default; SAVE/UPDATE modify requested map documentation only. |
| Read-only review or explanation | Inspect and report without files, startup, or application checks. Use [Review](references/WORKFLOW.md#requirements-engineering-and-review-feedback). |
| Small localized change or implicit selection for a small fix | Inspect, edit, run the nearest relevant check, and report. No new planning files or automatic startup for implicit selection. |
| Bug / nontrivial or ongoing work | Relevant Workflow sections: reproduce, plan useful deliverables, implement, review, verify, and checkpoint. |
| New project without a stack | Resolve blocking choices before scaffolding; do not impose a language or framework. |

Read-only modes, RESUME, CHECKPOINT, and MIGRATE never trigger full startup. Existing canonical documents outside harness/ remain authoritative. Minimal context needs an accessible installed/provided skill; PORTABLE explicitly requests a standalone package. These phrases are prompt instructions, not registered commands.

## Execute

1. Inspect instructions and current scope. In a checkout use `git status --short --branch`; preserve edits and branch. With remote-only access inspect the actual ref/commit and disclose unavailable local checks.
2. Trace affected behavior, callers, contracts, tests, and existing solutions.
3. Define observable success and failure cases. Reproduce bugs before editing when practical; prefer meaningful failing tests for testable new behavior. Setup failures do not demonstrate a regression.
4. Implement the smallest complete change using [Engineering](references/ENGINEERING.md). For shared interfaces, use [Design and Plans](references/WORKFLOW.md#design-and-executable-plans).
5. Run relevant configured checks; review the full change, new files, and direct consumers. For nontrivial work check requirements separately from engineering. Record actual evidence, scope, time, and limitations using the [Completion Gate](references/WORKFLOW.md#completion-gate).
6. Finish when accepted criteria and required checks are satisfied; preserve necessary state and report actual results and unresolved work.

Inspection-only requests follow their route instead of implementation/testing. Clear implementation authorization needs no repeated design approval.

## Keep Context Small and Durable

Keep reusable instructions/templates unchanged during target-project work. Use one canonical checkpoint for the active goal, plan, criteria/evidence, relevant failures, blockers, and next action. Use [Markdown State](assets/templates/PROJECT_STATE.md) or [JSON State](assets/templates/PROJECT_STATE.json); consult the [State Contract](references/CONTINUITY.md#state-contract) when needed.

Use the [Map Template](assets/templates/PROJECT_MAP.md) for stable technologies, responsibilities, contracts, material decisions, and reading order. Link current state rather than duplicating progress. Preserve source coverage; inspection does not prove running behavior.

Reuse existing plans/records. An explicitly requested long plan or detailed history may use a linked [Optional Record](assets/templates/PROJECT_RECORD.md). Create no automatic diary, second state, index, instruction file, archive, or snapshot.

Before phase changes or context reduction, save necessary facts and an executable next action. Preserve evidence/history and notes; follow [Migration and Retention](references/CONTINUITY.md#explicit-migration) before retiring legacy documents. A checkpoint is neither a commit nor permission to act.

Actual tools, access controls, and repository protections determine what can run.
