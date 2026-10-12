# Project Context and Continuity

Use this reference for START, PORTABLE, HARNESS STATUS, RESUME, CHECKPOINT, JSON state, migration, or snapshot refresh. Load only the relevant section. These are prompt instructions, not registered client commands.

## Contents

- [Startup and Roles](#startup-and-roles)
- [Existing Projects and Repeated Startup](#existing-projects-and-repeated-startup)
- [State Contract](#state-contract)
- [HARNESS STATUS](#harness-status)
- [RESUME and CHECKPOINT](#resume-and-checkpoint)
- [Explicit Migration](#explicit-migration)
- [History and Snapshot Lifecycle](#history-and-snapshot-lifecycle)

## Startup and Roles

A bare explicit invocation, START, or first explicit development invocation prepares the minimal context. Reuse existing canonical documents; create at most these two project documents when neither role exists:

| Role / default path | Owner and lifetime |
| --- | --- |
| `harness/PROJECT_STATE.md` | Current objective, short active plan, criteria/evidence, relevant failed attempts, blockers, and next action. Update the current checkpoint rather than appending a session diary. Use [Markdown State](../assets/templates/PROJECT_STATE.md). |
| `harness/PROJECT_MAP.md` | Stable purpose, technologies, components, contracts, important decisions, and reading order. Follow [Project Mapping](PROJECT_MAP.md) and [Map Template](../assets/templates/PROJECT_MAP.md). Do not duplicate active progress here. |

START JSON selects [JSON State](../assets/templates/PROJECT_STATE.json) for new state instead of Markdown. Preserve established formats and locations. START LEARN adds unfamiliar-stack explanations to the initial map. START PORTABLE or PORTABLE adds the complete reusable package under `harness/skill/`; combine modifiers when useful.

Default startup creates no harness README, INDEX, AGENTS, PROJECT_RECORD, snapshot, archive, or root/client configuration. The installed skill supplies behavior; the two project documents alone are not a standalone skill. If the selected source is read from an existing portable snapshot, preserve that snapshot without copying it into itself.

PORTABLE requires an accessible complete source package. Copy SKILL.md, references, assets, and agents with relative links intact; exclude source-maintenance documents, Git metadata, caches, credentials, and unrelated files. Preserve an existing snapshot; refresh only on an explicit request. Do not claim portability if the package is inaccessible or incomplete.

Identify the actual target root and read its instructions, relevant sources, Git status/ref when available, and existing context before writing. With ambiguous project roots, resolve that choice first. Fill new documents with observed facts and relative paths; remove unused placeholders. Without a development objective, record pending, explicit waiting-task context, and a next step to obtain the goal; create no feature or invented acceptance evidence. Inspect a representative source flow for the initial map; an empty project has no established application architecture.

Startup authorizes context documents and, when requested, the portable snapshot only. It does not authorize application scaffolding, root instruction changes, tools, services, Git operations, or global installation. Review/feedback-only, DESIGN/PLAN, HARNESS STATUS, CHANGE IMPACT, and unsaved map requests stay read-only. SAVE authorizes the requested document, not full startup. RESUME uses existing context.

Read back new files, confirm one canonical state and the map role, resolve pointers, and verify a requested snapshot. Report created/reused paths, external canonical dependencies, conflicts, access limits, and the next step. Setup readiness is not application verification.

## Existing Projects and Repeated Startup

Read existing root instructions and any legacy index/guidance before choosing paths. Existing state, maps, and planning conventions satisfy their roles even outside harness/. Report external dependencies instead of creating duplicates. Record useful document pointers in new state when its format supports them; create no index solely to list paths.

Repeated START preserves existing bytes, status, evidence, notes, plans, and snapshots. Create only missing roles. An old kit remains usable; its README, AGENTS, INDEX, PROJECT_RECORD, and snapshot are optional legacy context, not missing requirements of the minimal profile. Do not rewrite them or trim records merely to meet a new file count.

Inspect destination symlinks, non-regular paths, and collisions before writes; do not follow a link to overwrite another project or truncate a destination to make setup succeed. Nested harness/AGENTS.md has directory scope in clients that load it and does not automatically govern application files elsewhere. Root integration requires an explicit request; reuse existing instructions.

Treat another project's copied state/map as imported context. Reconcile identity and facts before using its status or next step; never inherit verification or permissions. For clean adoption, copy only the reusable snapshot and request START in the new target.

For maintenance of this skill source, use its repository-maintenance state instead of initializing a target kit.

## State Contract

### Choose One Format

Reuse an established project convention. Otherwise, use [Markdown](../assets/templates/PROJECT_STATE.md) for a compact human-readable checkpoint, or [JSON](../assets/templates/PROJECT_STATE.json) when explicit fields help repeated handoffs or consumption by existing tools. Default paths are `harness/PROJECT_STATE.md` and `harness/PROJECT_STATE.json`; choose one, not both. Explicit startup initializes the two document roles; implicit small fixes and read-only reviews require no new state files. Preserve an existing agent-state/ or other location instead of silently migrating it.

JSON is data, not an executable dependency. Validate its syntax with an available tool when practical; valid syntax alone proves neither truthful evidence nor completed work. No bundled checker, schema package, or runtime is required. Preserve any existing machine/human pair and its synchronization contract.

### Fields and Meaning

The JSON template is a blank starting point. Empty fields belong to the blank template. An initialized startup checkpoint awaiting a development objective may have an empty criteria list only when status is `pending`, the waiting-task context is explicit, and the next action is to obtain the objective; it cannot establish verification. For an active checkpoint:

| Field | Contract |
| --- | --- |
| `schema_version` | Integer `1` for this format. Preserve an existing project's version convention instead of silently migrating it. |
| `objective`, `current_task` | Nonempty objective and task title; use an existing task identifier or create a local descriptive identifier. |
| `status` | Exactly `pending`, `in_progress`, `implemented`, `verified`, or `blocked`, as defined in [Workflow](WORKFLOW.md#status-and-checkpoint). |
| `context` | Actual branch, inspected revision, and access mode or limitation. Use `null` for an unavailable branch or revision; never infer clean local status from a remote read. |
| `last_checkpoint` | Actual checkpoint time in ISO 8601 format, including timezone. Do not invent a time for an earlier check. |
| `acceptance_criteria` | Nonempty array for an active development task; an explicit waiting-task startup may use an empty array. Each criterion has `id`, `description`, `required` boolean, `result`, `reason`, and `evidence`. |
| `changed_files` | Paths actually changed for this task, relative to the project root; an empty array is valid before implementation. |
| `confirmed_facts`, `hypotheses` | Keep observed facts separate from unconfirmed explanations; concise strings are sufficient. |
| `blockers` | Concrete unresolved conditions and their impact. May be empty. Missing required verification belongs here even when implementation is finished. |
| `next_action` | One executable next step, or an explicit completion statement when no work remains. |

Each criterion has a unique ID. `result` is exactly `PASS`, `FAIL`, `NOT RUN`, or `N/A`. Record the current result for the current scope; retain relevant history in the checkpoint or an existing linked record.

For an observed PASS or FAIL, `evidence` is an object containing `action`, `level`, `observed_at`, `revision`, `scope`, `summary`, and `limitations`. Name the command or inspection actually performed, state what it establishes, and include limitations. Use `null` for an unavailable evidence time or revision and explain the gap; the checkpoint time is not a substitute. Manual evidence is valid when it directly establishes the criterion. Include relevant local changes in the scope: a commit hash alone may not identify the tested working tree.

For NOT RUN or N/A, set `evidence` to `null` and give a nonempty `reason`. N/A applies only to an optional criterion that does not apply. Do not turn an unmet required criterion into optional merely to declare completion; changing acceptance scope needs support from the current request or applicable authorization.

### Verification Gate

Set `verified` only when all of these conditions hold:

1. The active criteria list is nonempty and contains at least one required criterion.
2. Every required criterion has a current PASS and concrete evidence covering its requirement.
3. No unresolved blocker prevents a required criterion from being established.
4. Relevant configured checks and the diff have been reviewed, or their omission is explicitly justified within the accepted scope.

A passing unit check cannot substitute for required integration evidence. A mock proves only the simulated behavior. Mark implementation as `implemented` when changes exist but required verification remains; use `blocked` when the next work itself cannot proceed. Neither status implies completion.

Invalidate affected evidence after changing behavior, requirements, configuration, or the tested environment. Recheck the affected scope before restoring PASS. A later passing check may supersede an earlier failure only for the behavior it actually covers; retain important failure history in the checkpoint or an existing linked record.

### Example: Implementation with Missing Integration Evidence

This illustrative checkpoint describes supplied observations; it does not certify a real project.

```json
{
  "schema_version": 1,
  "objective": "Create orders atomically",
  "current_task": {"id": "orders-transaction", "title": "Add transactional order creation"},
  "status": "implemented",
  "context": {"branch": "feature/orders", "revision": null, "access": "local working tree"},
  "last_checkpoint": "2026-10-07T08:10:00Z",
  "acceptance_criteria": [
    {
      "id": "unit",
      "description": "Unit tests cover order creation behavior",
      "required": true,
      "result": "PASS",
      "reason": "",
      "evidence": {
        "action": "Configured unit test command",
        "level": "unit",
        "observed_at": "2026-10-07T08:05:00Z",
        "revision": null,
        "scope": "src/orders.js and its tests in the current working tree",
        "summary": "Unit tests passed",
        "limitations": "No revision recorded; database rollback is not covered"
      }
    },
    {
      "id": "rollback",
      "description": "Real database rolls back a failed order",
      "required": true,
      "result": "NOT RUN",
      "reason": "No safe test database is available",
      "evidence": null
    }
  ],
  "changed_files": ["src/orders.js"],
  "confirmed_facts": ["Implementation exists; unit tests passed"],
  "hypotheses": [],
  "blockers": ["Required rollback verification needs a safe test database"],
  "next_action": "Obtain an authorized safe test database and run the configured rollback integration check"
}
```

Do not replace NOT RUN with PASS because code looks plausible. A checkpoint with `verified` and an empty criteria list is also invalid.

### Resume and Migrate

On resume, read the current request and project instructions, inspect the actual branch and changes, then reconcile the checkpoint with current facts. A checkpoint records context; it does not grant Git, deployment, data deletion, or external-service permissions. Use the sections below for explicit RESUME or a read-only HARNESS STATUS audit. Preserve historical evidence; invalidate only affected current claims and never label a saved result as a new check.

Follow Explicit Migration below; do not inherit source-maintenance tasks, evidence, or technology choices.


Optional JSON fields `plan`, `relevant_failed_attempts`, and `documents` hold the active deliverables, scoped failure summaries, and actual relative context paths. They do not change schema_version 1; older checkpoints without them remain valid. Preserve consumer contracts that reject extra fields and use an existing linked plan when needed. Markdown keeps the same facts without requiring these keys.

## HARNESS STATUS

Inspect without edits, startup, application checks, or services. Report OK, ATTENTION, or UNKNOWN with evidence and a next action; these describe context health, not test results.

Check the actual canonical state and stable map, their pointers, current task relevance, required verification gaps, and relevant source freshness. Use the verification gate above; a complete folder or recent timestamp cannot establish code correctness. Existing synchronized state pairs retain their contract.

No README, INDEX, AGENTS, PROJECT_RECORD, or snapshot is required for the minimal profile. Inspect legacy pointers when present and report inconsistencies. Check snapshot references/inventory only when a snapshot exists or portability is requested. Compare against an accessible selected source and label differences accurately; without a comparison source, version alignment is unknown. Identify unsafe destinations for later writes without repairing them. If neither role exists, suggest START without initializing.

## RESUME and CHECKPOINT

Reconstruct the objective, criteria, active plan, relevant failed attempts, confirmed facts, blockers, and next action from canonical state and linked existing records. Inspect actual sources/branch/diff and reconcile with the current request. Continue a clear unfinished task within existing authorization; resolve a missing, completed, imported, or ambiguous objective before implementation. Do not trigger full startup or invent work.

Keep unaffected supported evidence and its original time/scope. When relevant changes invalidate a PASS, retain a concise historical result and reason, mark the current criterion NOT RUN, and use implemented or blocked as appropriate. Do not relabel an old result as a new check. If history is longer than a compact checkpoint, retain a link to its existing record; do not discard it to reduce file count.

During ongoing authorized work or CHECKPOINT, update one canonical checkpoint with actual facts and an executable next step. Keep Markdown near 100 lines where practical; preserve necessary criteria and evidence. Record only failures still relevant to avoiding repeated mistakes. Save important durable decisions in existing stable documentation when the task authorizes that update. Name map areas needing review rather than automatically rewriting the map.

A saved action grants no Git, deployment, destructive, or service permission. A read-only request writes no checkpoint. Completed implementation with required checks missing is not verified. See [Workflow](WORKFLOW.md#status-and-checkpoint) for execution and statuses.

## Explicit Migration

HARNESS MIGRATE or an explicit consolidation request authorizes reconciliation into the minimal roles, not application edits, Git operations, snapshot changes, or deletion. Inspect all candidate documents and preserve the established canonical format/location.

Transfer active goals, criteria, plans, current evidence, blockers, next steps, and relevant failed attempts to canonical state. Transfer source-supported stable architecture/technology facts and material documented decisions to the existing map or established decision documents. Keep a long active plan in its existing record and link it; do not duplicate the whole plan in state. Preserve original timestamps, scope, failed/unperformed checks, and user notes. Flag contradictions or foreign facts rather than silently choosing an unsupported winner.

Read back both destinations and compare every substantive original item with its destination or retained reference. Report the reconciliation and which generated files are redundant. Preserve originals by default; migration alone does not authorize retiring them. If retirement is explicitly requested, remove or archive only identified generated documents whose contents have been preserved and whose consumers/pointers have been updated. Keep unclassified notes and evidence until their destination is clear. Do not create an archive automatically.

## History and Snapshot Lifecycle

Use Git for versioned code/diffs and reviewed document history, and existing PR/CI records for rationale or detailed test evidence when available. Do not duplicate transcripts or source-file history into Markdown. Never create a commit merely because a checkpoint was saved. Keep uncommitted evidence needed for handoff until a durable reference exists.

Create no dated session file or permanent diary by default. If a detailed session record or long plan is requested, reuse its existing location or use [Optional Record](../assets/templates/PROJECT_RECORD.md) at harness/PROJECT_RECORD.md; link it from state and label its task/scope. Preserve it until relevant evidence/decisions are retained elsewhere. It is not a second operational state.

For an explicitly requested snapshot refresh, identify the intended complete source, compare it with the current copy, and preserve customizations. Stage and validate a clean complete replacement before changing the active snapshot; omit removed source files instead of merging stale files. Keep one recoverable original outside harness/skill/ in an existing approved backup location or a non-colliding harness/.backups/ location. Skip backups in mapping and context discovery.

Do not overwrite an older backup containing unknown changes or delete backups automatically. Report redundant generated backups and the exact retention choice if cleanup is requested. On partial failure retain/restore a usable original and report actual paths. Snapshot refresh never edits project state/map, root instructions, or the global installation.
