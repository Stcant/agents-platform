# Repository State

Updated: 2026-10-15T10:26:15Z
Branch context: main; source update parent 1f7f15bf001ca7bac6fc5c844da12a70d57d0b15.
Access context: local source checkout and connected GitHub repository.

## Objective and Task

Maintain anonymous English, instruction-only development guidance with proportionate engineering and minimal project context.

TASK-021 — verified

Requirement: when a user identifies an unfamiliar stack while requesting a code change, help them follow the affected implementation flow without turning the task into read-only mapping.

## Changes

- Route implementation/debugging requests in an unfamiliar stack to a short teaching layer on the changed path while continuing authorized work.
- Require a concrete explanation of the request/data path, the actual checks and what they establish, and a useful existing file/symbol to read next.
- Update the README example to show that naming an unfamiliar stack in an implementation request is sufficient; `PROJECT MAP LEARN` remains read-only.
- Preserve the ten-file portable package, two-document default, and existing mapping behavior. Add no target-project runtime, startup file, or dependency.

## Evidence

All runs used five fresh-context agents per variant and separate disposable project copies. Task: “I'm new to Node and HTTP handlers, and I can't follow what this server does. Fix the bug where POST /profile accepts a whitespace-only name; return HTTP 400 JSON and keep valid-name behavior. Implement the change and run relevant checks.”

| Scenario | Observed outcome | Scope and limits |
| --- | --- | --- |
| Baseline using source at parent 1f7f15bf001ca7bac6fc5c844da12a70d57d0b15 | 5/5 implemented the fix and regression test; 0/5 explained the request from entry through result or ended with a useful file to read next. One mentioned a direct call to `saveProfile` without tracing the request. | Fresh Node HTTP fixtures; no application runtime beyond the local tests |
| Candidate with this instruction change | 5/5 explained the handler's request/body path, validation result, and valid continuation in plain language; all reported test results. 4/5 explicitly ended with a useful next file; 1/5 named the relevant file and reason inside the flow but did not mark it as the next read. | Output-shape evaluation only; Node.js, no Spring Boot project |
| Independent candidate test rerun | `npm test` passed 2/2 in all five candidate fixtures; the regression test covered whitespace-only input and the existing valid-name response. | Parent rerun; npm emitted an `http-proxy` environment warning without failing |
| Source validation | PASS: ten portable package files, 90 local links/anchors, valid frontmatter, 8 existing client shell blocks preserved, 10 Bash blocks syntax-checked, pinned Superpowers submodule clean | Static checks do not prove every workflow or client discovery |
| Diff validation | `git diff --check` passed | Local source diff only |

## Next Action and Limits

Refresh copied skill installations when desired. The behavioral test shows improved user-facing code-flow guidance in a Node fixture; it does not verify a real Java/Spring Boot project or client-native skill discovery.

## Authorization

The user asked to improve and update this repository using Superpowers. This source update is within that scope. No application project, global installation, branch rewrite, upstream file, or client plugin is modified.
