---
description: Resume work from saved state, reconciled with the real repository
---

Resume work in this repository.

Repository snapshot:
!`git status --short --branch`
Recent commits:
!`git log --oneline -15`

Steps:

1. Read `.dev-brain/STATE.md` and the root `AGENTS.md`.
2. Reconcile the saved state with reality: branch, working-tree changes, recent commits, and the files named in the state. Saved notes are context, not proof. If something no longer matches, say so before continuing.
3. If the state records a smoke check or a quick verification command, run it only when it is safe and read-only, and report the actual result. Never present an old check as freshly run. Before any `uv run`, check that `.venv` already exists (for example `test -d .venv`); if it does not, report the check as NOT RUN and do not create it. Never run `uv sync`, `pip install` or any command that writes caches or environments.
4. Report in a few lines: goal, last verified outcome, current blockers, and the single next action. Ask before starting work that changes behavior, data or git state.

Do not edit files as part of this command.
