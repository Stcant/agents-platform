# Maintaining dev-brain

This repository is a plugin marketplace with one plugin, `dev-brain`, in `core/`, built for Claude Code, with an adapter for OpenCode in `adapters/opencode/`. It is not an application.
Its primary goal is readable, maintainable code across languages and frameworks. Workflows and saved state support that goal.

## What belongs where

- `core/AGENTS.md` — the global rules, injected into every session by the `SessionStart` hook. Keep it short: only instructions that change default behavior.
- `core/skills/` — Agent Skills. User-invoked workflows (`start`, `resume`, `handoff`, `impact`, `learn`, `review`) set `disable-model-invocation: true`, so they cost no context until invoked; `debugging`, `engineering-risk`, `review-feedback` are loaded by the model when relevant.
- `core/agents/reviewer.md` — the read-only reviewer; its `tools` line is the enforcement.
- `core/hooks/hooks.json` + `core/bin/dev-brain-context` — inject rules and the project state (3000-character budget).
- `core/bin/dev-brain-guard` — `PreToolUse` hook that answers "ask" for git commands changing history, branches or the remote; keep its list in sync with the Authorization rules in `core/AGENTS.md`.
- `adapters/opencode/index.ts` — OpenCode has no plugin marketplace, so this one file runs `dev-brain-context` and `dev-brain-guard`, registers `core/skills` and builds the reviewer from `core/agents/reviewer.md`. It holds no rule of its own: change the rule in `core/`, not here. Its one extra line of policy is the reviewer's denial of redirections, which OpenCode's shell matcher does not parse.
- `core/.claude-plugin/plugin.json` — bump `version` on every change so installed copies refresh. `.claude-plugin/marketplace.json` at the root lists the plugin.
- `evals/` — scenarios, measured results, and `offline/check.py` with `offline/mock_model.py`, a zero-token check against the real Claude Code and OpenCode binaries. The OpenCode TUI cannot run here, so it is untested.

## Changing the harness

1. Run the relevant scenarios in `evals/scenarios/` against the current version and record the baseline.
2. Make the smallest change that addresses an observed failure.
3. Re-run the same scenarios, and `python3 evals/offline/check.py`.
4. Keep the change only if it improves a scenario or removes a real cost. Delete instructions that do not change behavior.
5. Record the result in `evals/results.md`: date, change, evidence, limits. Keep it a log of decisions, not of sessions.

Never add rules by intuition alone. A rule that the model already follows is pure context cost.

## Constraints

- All kit content is English. Exception: `MANUALE.md` is the Italian user manual.
- Runtime dependencies: Claude Code or OpenCode, `python3`, `git`.
- Skills and rules stay in standard formats (`AGENTS.md`, `SKILL.md`) with no absolute paths, so another agent is supported with an adapter instead of a rewrite. Host-specific code stays limited to `adapters/`.
- Do not duplicate a rule or template across files: `core/` holds each once.
- Do not copy project facts (stack, commands, state) from a destination repository into this source repository.
