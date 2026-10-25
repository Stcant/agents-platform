# State — agents-platform
Updated: 2026-10-25 · Branch: improve/token-budget-and-review

## Goal
Personal OpenCode harness for readable, maintainable code at the lowest context cost — acceptance: always-on design rules installed, review covers real defects and maintenance costs, every claim backed by `evals/` evidence.

## Done (latest first, max 5)
- `/review` delegates the diff to the reviewer (read-only git allowlist); covers staged, unstaged and untracked; plugin skips subagents and enforces a 3000-char state budget; `/resume` stack-agnostic; `/start` migrates `harness/` — evidence: `python3 evals/offline/check.py` PASS (mock model, OpenCode 2.1.4); `evals/results.md` 2026-10-25
- hph adopted by following `/start` (patch, not pushed) — evidence: plugin injected the 1.3 KB state; `git apply --check` PASS on hph `d6ee299`
- Maintainability scenario: review policy reports duplicated business rules — evidence: `evals/results.md` 2026-10-22 (Python only)

## In progress / blockers
- Real-model behavior of the new `/review`, `/resume` and plugin — status: NOT RUN; providers unreachable from the test environment
- Cross-language generation scenario — status: NOT RUN
- hph `harness/` deletion and patch commit — status: waiting for the owner

## Known pre-existing failures
- `opencode run "/command"` does not expand slash commands (CLI limitation)

## Next (max 3)
1. Run `python3 evals/offline/check.py` locally, then `/review` on a real diff with a real model in the TUI.
2. Apply the hph patch, review it, delete `harness/` and fix the README link to it.
3. Add a non-Python maintainability scenario before changing design rules again.
