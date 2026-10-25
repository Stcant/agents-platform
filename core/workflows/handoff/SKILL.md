---
name: handoff
description: Close a work session by rewriting .dev-brain/STATE.md with verified results and next actions. Run only when the user asks for it.
disable-model-invocation: true
---

Close the current work session by updating the saved state.

Steps:

1. Read the current `.dev-brain/STATE.md`, and run `git status --short --branch` and `git log --oneline -10`.
2. Establish what actually happened from the diff, the checks run in this session, and the conversation. Do not invent evidence and do not copy old results as new.
3. Rewrite `.dev-brain/STATE.md` using the existing structure:
   - goal and acceptance criteria, only if they changed;
   - done: latest verified outcomes, each with command and PASS/FAIL/NOT RUN, maximum five;
   - in progress / blockers: mark each item implemented, verified or blocked;
   - known pre-existing failures, if newly discovered;
   - next: at most three executable actions, most important first.
   Replace stale lines instead of appending. Keep it under 3000 characters: it is injected into the agent's context and larger files are skipped. The transcript is not the state.
4. Update the root `AGENTS.md` only if a stable fact changed: stack, commands, architecture, gotchas.
5. Report what changed in the two files, and list anything not verified.

Do not commit. A state update is not authorization for git writes.
