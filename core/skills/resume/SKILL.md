---
name: resume
description: Resume work from .dev-brain/STATE.md, reconciled with the real repository. Run only when the user asks for it.
disable-model-invocation: true
---

Resume work in this repository.

Steps:

1. Read `.dev-brain/STATE.md` and the root `AGENTS.md`, and run `git status --short --branch` and `git log --oneline -15`.
2. Reconcile the saved state with reality: branch, working-tree changes, recent commits, and the files named in the state. Saved notes are context, not proof. If something no longer matches, say so before continuing.
3. If the state records a quick verification command, run it only when it is read-only and fast, and report the actual result. Never present an old check as freshly run. Report as NOT RUN, without running, anything that would install, download, compile or create an environment or cache: `uv sync`, `pip install`, `npm install`, `uv run` without an existing `.venv`, `cargo test`/`cargo build`, full builds.
4. Report in a few lines: goal, last verified outcome, current blockers, and the single next action. Ask before starting work that changes behavior, data or git state.

Do not edit files as part of this command.
