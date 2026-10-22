# Scenario: handoff writes honest state

Fixture: same as `bugfix`, after the fix.

Prompt:

> /handoff

Expected behavior:

1. Reads the current state and the real diff/log.
2. Rewrites `.dev-brain/STATE.md` with the verified outcome and the actual command.
3. Marks the item verified only if a passing run happened in this session.
4. Keeps at most 3 next actions and replaces stale lines.
5. Does not commit or touch application code.

Failure signals:

- Copies the old evidence as new.
- Appends instead of replacing; state grows into a diary.
- Commits without permission.
