# Project Map

Scope: [system overview or named subsystem]
Latest inspection: [actual ISO 8601 timestamp and area inspected]
Revision: [inspected revision or unavailable]
Working tree / access: [relevant local changes or access limitations]
Validation: [source inspection performed; runtime checks performed or NOT RUN]

## Purpose and Stable Context

[Explain what the project does and define necessary domain terms. Keep active tasks, plans, and test status in canonical state.]

Project documents: [actual relative canonical state path and useful existing documentation links]

## Technologies

| Technology | Role / environment | Declared constraint / resolved version | Evidence and confidence | Documented reason |
| --- | --- | --- | --- | --- |
| [important technology] | [runtime, development, build, storage, or deployment role] | [observed values or unknown; not the running version] | [OBSERVED / INFERRED / UNKNOWN; path and key] | [documented reason or unknown] |

## Components and Entry Points

| Component | Responsibility | Source location | Entry point or contract | Evidence and confidence |
| --- | --- | --- | --- | --- |
| [component] | [plain-language purpose] | [relative path] | [symbol, route, job, or interface] | [inspected source and confidence] |

## Connections

| From → To | Mechanism / contract | Failure or consistency behavior | Evidence and confidence | Runtime confirmation |
| --- | --- | --- | --- | --- |
| [source → destination] | [call, HTTP, message, storage operation, or unknown] | [observed behavior or unknown] | [path and symbol; OBSERVED / INFERRED / UNKNOWN] | [actual evidence or NOT RUN] |

## Main Flow

1. [Input or trigger; supporting source]
2. [Processing and handoff; supporting source]
3. [Storage, output, or failure; supporting source]

[Add a compact Mermaid diagram only when it helps; support its edges with the connection evidence. Remove this instruction from a saved map.]

## Concept Guide and Reading Order

[Include only for a requested learning-oriented map; otherwise omit. Explain language versus framework, then concepts needed for the inspected flow.]

| Concept | Plain-language meaning | Real example in this project | Evidence and limits |
| --- | --- | --- | --- |
| [unfamiliar concept] | [purpose without assumed jargon] | [relative path and symbol] | [source or matching official documentation; unknowns] |

Reading order: [entry point → next component → result, using actual paths and symbols]

## Where to Make Changes

| Goal or area | Starting point | Direct consumers / contracts to inspect | Relevant existing checks |
| --- | --- | --- | --- |
| [likely change] | [relative path and symbol] | [observed consumers or unknown] | [test locations; do not imply they ran] |

## Inspection Coverage

| Area / claims | Supporting source paths | Last inspected context | Source freshness and limits |
| --- | --- | --- | --- |
| [mapped area] | [relative paths or symbols] | [actual timestamp, revision and relevant working-tree context, or unavailable] | [RECHECKED / NEEDS REVIEW / UNKNOWN with reason; not runtime verification] |

[For a focused refresh, retain each untouched area's earlier context. Do not stamp the entire map as rechecked. Remove this instruction before saving.]

## Coverage and Open Questions

- Inspected: [areas and representative flows]
- Not inspected: [omitted areas and why]
- Conflicts or unknowns: [claim, missing evidence, and next read or check]
- Runtime limits: [what static inspection cannot establish]

## Preserved Decisions and Notes

[Keep documented rationale and user notes, with their source. Omit this section if absent. Do not invent reasons.]
