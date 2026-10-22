---
description: Produce a plan-contract for a change (read-only, max 5 steps)
agent: plan
---

Plan this work: $ARGUMENTS

This is read-only: do not edit files, install dependencies or change git state.

First inspect the real code and configuration affected. Then produce a plan with at most 5 steps. Each step is a working deliverable, not an activity, and uses this table:

| # | Deliverable | Files / symbols | Input -> Output | Depends on | Check and expected result |
| - | ----------- | --------------- | --------------- | ---------- | ------------------------- |

Rules:

- No placeholders such as "handle edge cases". Name the concrete behavior.
- Producer and consumer of a shared interface must use the same contract.
- The check must be something that can fail if the step is wrong; state the expected result.
- Separate required work from optional improvements; list what is explicitly out of scope.
- If a decision needs the user, ask it before the plan rather than guessing.
- Finish with the main risk and the assumption most likely to be wrong.
