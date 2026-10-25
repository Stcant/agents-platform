# State — agents-platform
Updated: 2026-10-25 · Branch: improve/token-budget-and-review

## Goal
Agent-independent harness (OpenCode, Claude Code, Codex CLI, Cursor; any model provider) for readable, maintainable code at the lowest context cost — acceptance: one `core/` source, `install.py` per agent, every claim backed by `evals/` evidence.

## Done (latest first, max 5)
- `core/` + `install.py` adapters for 4 agents; Claude Code and Codex via a local plugin marketplace in `build/`; state via one script `core/bin/dev-brain-context` — evidence: `python3 evals/offline/check.py` ALL PASS (OpenCode 2.1.4, Claude Code 2.1.310, Codex 0.164, mock model); Cursor files only
- `/review` delegates the diff to the reviewer; plugin skips subagents; 3000-char state budget — evidence: `evals/results.md` 2026-10-25
- hph adoption patch (`AGENTS.md` + 1.3 KB state) — evidence: state and resume workflow reached Claude Code and Codex on the hph copy; not pushed

## In progress / blockers
- Codex reviewer read-only — status: blocked upstream; `sandbox_mode` not applied to spawned agents in 0.164, instruction only
- Cursor — status: NOT RUN; no CLI in the test environment; `sessionStart` context dropped by an open Cursor bug
- Real-model and TUI behavior of all workflows — status: NOT RUN

## Known pre-existing failures
- `opencode run "/command"` does not expand slash commands (CLI limitation)

## Next (max 3)
1. Run `./install.sh` and `python3 evals/offline/check.py` locally; approve the Codex hook; try `review` and `resume` in each agent's TUI with a real model.
2. Apply the hph patch, delete `harness/`, fix hph README's link to it.
3. Add a non-Python maintainability scenario before changing design rules again.
