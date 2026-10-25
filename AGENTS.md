# Maintaining dev-brain

This repository is the source of the personal OpenCode harness. It is not an application.
Its primary goal is readable, maintainable code across languages and frameworks. Workflow commands and saved state support that goal.

## What belongs where

- `global/AGENTS.md` — always-loaded personal rules. Keep it short: only instructions that change the model's default behavior.
- `global/commands/`, `global/agents/`, `global/skills/` — installed into `~/.config/opencode/` by `install.sh`.
- `plugin/dev-brain/` — the V2 plugin injecting project state; registered in the global `opencode.json`.
- `templates/` — files written into destination projects.
- `evals/` — scenarios, measured results and `offline/check.py`, a zero-token check against a mock model.

## Changing the harness

1. Run the relevant scenarios in `evals/scenarios/` against the current version and record the baseline.
2. Make the smallest change that addresses an observed failure.
3. Re-run the same scenarios with the change. After touching the plugin, agents or `install.sh`, also run `python3 evals/offline/check.py`.
4. Keep the change only if it improves a scenario or removes a real cost. Delete instructions that do not change behavior.
5. Record the result in `evals/results.md` with the date and the evidence.

Never add rules by intuition alone. A rule that the model already follows is pure context cost.

## Constraints

- All kit content is English. Exception: `MANUALE.md` is the Italian user manual.
- No runtime dependency beyond the OpenCode binary itself; the plugin uses only `@opencode/plugin` and Node built-ins.
- Commands, agents and skills must be portable: no absolute paths inside their content.
- Do not copy project facts (stack, commands, state) from a destination repository into this source repository.
