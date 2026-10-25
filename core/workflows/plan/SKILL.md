---
name: plan
description: Produce a read-only plan-contract of at most 5 steps for a non-trivial change. Run only when the user asks for it.
disable-model-invocation: true
---

Plan the work the user described with this request.

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
