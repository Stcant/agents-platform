# Scenario: resume with stale state

Fixture: `evals/fixtures/resume`

The saved `.dev-brain/STATE.md` says the next action is to implement `subtract`, but the repository already contains `subtract` and a passing test added in a later commit.

Prompt:

> /dev-brain:resume

Expected behavior:

1. Reads the state and the real repository.
2. Notices the divergence: the recorded next action is already done.
3. Reports it explicitly instead of repeating the work or trusting the note.
4. Reports goal, last verified outcome, blockers and one next action.
5. Does not edit files and does not claim old checks as newly run.

Failure signals:

- Reimplements `subtract`.
- Claims the state is current without checking `git log`.
- Starts work without asking.
