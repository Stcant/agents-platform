---
name: impact
description: Read-only impact analysis of a proposed change - consumers, contracts, tests and unknowns. Run only when the user asks for it.
disable-model-invocation: true
---

Analyze the impact of the change the user described with this request.

Read-only: do not modify files, generate patches or run checks.

Trace and report:

1. Direct consumers of the code, contract or data being changed: callers, imports, endpoints, events, queries, serialized formats, stored data.
2. Public contracts at risk: signatures, error behavior, side effects, invariants, configuration keys, API and schema compatibility.
3. Tests, fixtures and configuration that encode the current behavior.
4. Files that will likely need to change, separated from files that only need review.
5. Existing checks that would catch a mistake, with the command, without running them.
6. Unknowns and the smallest experiment that would resolve each one.

Label each statement OBSERVED (seen in source), INFERRED (follows from structure) or UNKNOWN. A dependency declaration alone does not prove an active connection.
