# Maintaining dev-brain

This repository is the source of a personal harness for coding agents (OpenCode, Claude Code, Codex CLI, Cursor). It is not an application.
Its primary goal is readable, maintainable code across languages and frameworks. Workflows and saved state support that goal.

## What belongs where

- `core/` — the only source. `AGENTS.md` is the always-loaded rule set: keep it short, only instructions that change default behavior. `workflows/` (user-invoked, `disable-model-invocation: true`) and `skills/` use the Agent Skills format; `agents/reviewer.md` has neutral frontmatter; `bin/dev-brain-context` produces the injected state for every adapter; `templates/` are written into projects.
- `adapters/` — only what cannot be expressed as files (the OpenCode plugin).
- `install.py` — links `core/` or translates frontmatter per agent. It must not contain rules or prose for the model beyond frontmatter; if an adapter needs a rule, it belongs in `core/`.
- `evals/` — scenarios, measured results, and `offline/check.py` with `offline/mock_model.py`, a zero-token check against the real agent binaries.

## Changing the harness

1. Run the relevant scenarios in `evals/scenarios/` against the current version and record the baseline.
2. Make the smallest change that addresses an observed failure.
3. Re-run the same scenarios with the change. After touching `core/`, an adapter or `install.py`, also run `python3 evals/offline/check.py`.
4. Keep the change only if it improves a scenario or removes a real cost. Delete instructions that do not change behavior.
5. Record the result in `evals/results.md` with the date and the evidence.

Never add rules by intuition alone. A rule that the model already follows is pure context cost.

## Constraints

- All kit content is English. Exception: `MANUALE.md` is the Italian user manual.
- Runtime dependencies: the agent itself, `python3` and `git`. The OpenCode plugin uses only `@opencode/plugin` and Node built-ins.
- Workflows, skills and the reviewer must be portable: no absolute paths, no agent-specific syntax (`$ARGUMENTS`, `!` command expansion) in `core/`.
- Claude Code and Codex install the plugin from `build/` (generated, git-ignored); Codex copies it and drops symlinks, so the build uses real copies.
- Do not copy project facts (stack, commands, state) from a destination repository into this source repository.
