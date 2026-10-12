# Project Mapping

Use this reference when the user requests a project map, architecture overview, technology inventory, proposed change impact, or an explanation of how project components connect. Do not activate mapping because a repository is large, or include it in every development task.

## Contents

- [Request and Output](#request-and-output)
- [Inspect in Layers](#inspect-in-layers)
- [What to Explain](#what-to-explain)
- [Explain an Unfamiliar Stack](#explain-an-unfamiliar-stack)
- [Change Impact](#change-impact)
- [Evidence and Boundaries](#evidence-and-boundaries)
- [Save and Refresh](#save-and-refresh)

## Request and Output

Treat these phrases as instructions within the skill, not new client commands:

| Request | Behavior |
| --- | --- |
| `PROJECT MAP` | Inspect and explain the project in the response; create or modify no files. |
| `CHANGE IMPACT <proposed change>` | Inspect the proposed change's affected sources, contracts, direct consumers, and existing checks; change no files and run no checks. |
| `PROJECT MAP LEARN` | Produce a read-only map for someone unfamiliar with the stack, explaining source-level concepts along one real flow. |
| `PROJECT MAP <area or question>` | Map the named subsystem or flow, its direct dependencies, and affected consumers. |
| `PROJECT MAP SAVE` | Inspect and save a project map using existing documentation conventions, or `harness/PROJECT_MAP.md` when none exist. |
| `PROJECT MAP UPDATE` | Refresh an existing saved map against current sources; preserve user notes and unrelated documentation. If no saved map exists, explain that and offer a read-only map rather than creating one. |

Equivalent natural-language requests are valid. Use LEARN when requested or when the user explicitly says they are unfamiliar with the stack. LEARN may be combined with a named area or an explicit SAVE/UPDATE request; it does not grant write permission by itself. A request to save or update authorizes the map document only, not code changes, Git writes, services, or a project-state update. Keep the reusable skill and its templates unchanged.

## Inspect in Layers

1. **Establish scope.** Read project instructions, the current request, and relevant existing architecture or state documents. Inspect branch, revision, and local changes when available. Explain remote-only or partial access. If no scope is specified, start with a system overview.
2. **Inventory the project.** Search directory names, documentation indexes, manifests, lockfiles, safe configuration examples, entry points, build/deployment definitions, and test locations. Exclude generated output, vendored dependencies, binary assets, skill snapshots/backups, and unrelated large files. Find top-level applications and packages before expanding one area.
3. **Trace real connections.** Follow imports, callers, routes, interfaces, data models, migrations, worker registration, and message producers/consumers. A dependency declaration, comment, unused adapter, or deployment setting alone does not prove an implemented or active connection.
4. **Follow a useful flow.** Trace one representative user action, job, or data operation through its entry point, business logic, storage, and external boundaries where present. Include relevant failure behavior, consistency boundaries, and handoffs. For a focused request, follow the requested flow instead.
5. **Explain and bound the result.** Connect technical details to their purpose in plain language. Record evidence and unknowns, identify what was inspected, and stop when the requested scope is understandable. Do not scan every source file or claim exhaustive coverage from a representative trace.

For a large repository, first provide a compact component index and a main flow. Summarize each major area at the level supported by inspected evidence, and name areas needing deeper inspection. Load additional files to resolve concrete gaps, not to expand an inventory of every dependency. Do not delegate automatically.

## What to Explain

- **Purpose and current work:** explain the project's stable purpose. In a response, relate the current request to actual state/diff when useful. In a saved map, link canonical state for active work instead of copying goals, plans, progress, or test results; preserve imported user notes until an explicit reconciliation.
- **Technologies and roles:** important languages, frameworks, storage, build/test tools, and deployment components. Distinguish runtime from development-only dependencies and local from deployment configuration. Label declared version constraints and resolved versions separately; do not infer the running version. Explain why a technology was chosen only when a source documents the reason.
- **Components and entry points:** each major component's responsibility, source location, and public entry point or interface. Explain domain terms that the user needs to follow the flow.
- **Connections and contracts:** who calls or produces for whom, the mechanism, contract or data shape, and supporting path or symbol. Distinguish source-observed wiring, configuration-only possibilities, and unknown runtime activation.
- **Data and control flow:** where inputs enter, transform, persist, leave, and fail. Identify transactions, retries, authorization, and background handoffs only when evidenced.
- **Change navigation:** where to start for a likely change, immediate consumers or contracts to inspect, and relevant existing tests. Avoid declaring all downstream impact known from one call chain.
- **Coverage and unknowns:** inspected areas, omitted areas, conflicting documentation, unanswered questions, and runtime checks not performed.

Use compact tables for technology roles, components, and connections. Add a Mermaid diagram when topology makes the explanation clearer; use a small top-down overview or separate subsystem diagrams, with concise labels and one relationship per diagram. Every edge must be supported by source evidence or visibly labeled as inferred. Do not turn a package declaration into an arrow between running services. Use prose or tables when a diagram adds no value.

## Explain an Unfamiliar Stack

For LEARN, begin with the distinction between the programming language, framework, build tools, and external services actually present. Assume no prior knowledge of that stack when the user says it is new. Use a stated familiar technology for a helpful analogy only; do not store the user's background in the reusable skill or equate different frameworks' behavior.

Explain a small set of concepts needed for the chosen flow before using their jargon. For each concept, connect its plain-language meaning to a real path and symbol: what the code does, who invokes it, its inputs and outputs, and why it matters to the flow. Distinguish a framework feature from a convention chosen by the project; do not assume every project has the same layers.

When relevant, explain framework annotations, decorators, registration, dependency wiring, configuration, and generated behavior that make execution less obvious from direct calls. Tie each explanation to inspected code. Consult official documentation matching the project's declared version when API behavior is uncertain; disclose unavailable documentation rather than inventing semantics. Search public documentation without uploading private source or configuration.

Walk one real request or job from entry point to result. Include a short actual code excerpt only when it helps the user read that step; explain it in context rather than dumping entire classes. Keep documented rationale separate from an inferred benefit. Use a short concept table and a reading order, not a general language course or a rewrite of unfamiliar code.

Finish with concrete files or symbols to read next and an explanation of where a small change would start. Recommend only existing checks and describe what they establish; do not run them as part of mapping. Keep missing runtime behavior and uninspected areas visible. Follow the response depth requested by the user without expanding the task into implementation.

## Change Impact

For `CHANGE IMPACT <proposed change>` or an equivalent question about what a change could affect, use read-only source inspection. This request authorizes neither implementation nor startup. Add LEARN when unfamiliar concepts need explanation; saving requires an explicit documentation request.

1. Restate the intended behavior change and inspect its current implementation. If the proposal is too ambiguous to identify an entry point or contract, inspect available context and ask only the blocking question.
2. Trace direct callers and consumers plus relevant outward boundaries. Inspect data shapes, public APIs, persistence/migrations, messages, authorization, configuration, and error behavior only where the proposal can affect them. Search beyond a representative flow for known direct consumers of a shared contract.
3. Separate files likely to change from consumers that need review. Include uncommitted edits that intersect the proposal. Distinguish documented compatibility requirements from assumptions; do not invent a redesign.
4. Identify existing targeted and regression checks, relevant failure cases, and missing coverage. Explain what each would establish without running it or claiming it passed.
5. Provide a compact table: affected area/path, relationship or contract, possible impact, source evidence/confidence, and relevant check. End with the safest starting point, unresolved assumptions, and inspected versus omitted scope.

Use a saved map as an index, then confirm material claims against current sources. A declared dependency or one traced caller does not establish exhaustive impact. Flag generated/dynamic wiring and unavailable external consumers as limits; do not label a change safe from static inspection alone. Keep proposed behavior separate from the implementation that currently exists.

## Evidence and Boundaries

Label material claims `OBSERVED`, `INFERRED`, or `UNKNOWN`:

- **OBSERVED:** cite an inspected repository-relative path and relevant symbol or configuration key. A source observation proves what the source contains, not that a service is running.
- **INFERRED:** state the supporting paths and reasoning, plus what would confirm the claim.
- **UNKNOWN:** name the missing source, access, configuration, or runtime observation needed.

Prefer concise evidence alongside each table row or flow step over a detached list of unsupported claims. Use current project documentation as a starting point, then reconcile it with source; flag stale or contradictory diagrams and comments. Record source inspection separately from runtime validation. Mapping does not mark code tasks or integrations verified.

Use read-only repository inspection. Do not install dependencies, run builds/tests, start applications, contact external services, connect to databases, or read secret files to discover the architecture. If runtime confirmation is needed, name the missing check and its authorization requirements separately. Describe safe configuration keys rather than secret values or private endpoints.

Keep reusable templates anonymous. In generated project maps, use relative paths and logical component names; omit personal names, machine usernames, absolute home paths, confidential records, credentials, and private network addresses.

## Save and Refresh

For SAVE, reuse an established architecture-map location; otherwise initialize `harness/PROJECT_MAP.md` from [Map Template](../assets/templates/PROJECT_MAP.md). The template is a blank scaffold, not evidence. Fill only applicable sections, remove unused placeholders, and keep unknown facts explicit. The map belongs in the target project, outside the installed skill.

Record scope, actual inspection time, inspected revision or its unavailability, and relevant local changes. Never substitute a commit identifier for an inspected working tree with uncommitted changes. Keep architecture separate from the operational checkpoint. Link canonical state and retain stable source-supported facts/decisions; do not add a session diary or current-task progress. Startup creates this stable role through [Continuity](CONTINUITY.md#startup-and-roles).

For UPDATE, read the saved map and its sources. Use the recorded revision and diff when available to focus inspection, then follow changed contracts into direct consumers. Recheck affected claims and diagram edges; retain unchanged, supported context without starting the entire inventory again. If the baseline is unavailable, state the limitation and inspect the current mapped scope.

Preserve user-written decisions and notes. Flag or correct stale generated claims, summarize significant map changes, and record remaining uncertainty. Track freshness per mapped area with supporting paths and its last inspected revision/working-tree context. A focused update must retain the older context for untouched sections; the latest timestamp or revision must not imply that the whole map was rechecked. A focused update should identify which sections were refreshed and which remain outside the current inspection scope. Do not silently rewrite rationale or assert unchanged runtime behavior.

Use `RECHECKED` for claims inspected in the current pass, `NEEDS REVIEW` when relevant changed sources or contradictions affect an unrechecked claim, and `UNKNOWN` when its baseline or sources cannot be assessed. These labels concern source coverage, not running-system validation. Unrelated changes or elapsed time alone do not invalidate an observed relationship. On older maps without an area baseline, retain known context and state the gap rather than inventing a past inspection.

End with the requested map, a short coverage statement, and useful navigation or open questions. For saved output, include its path. Require no new dependency, framework, architecture service, or global state file.
