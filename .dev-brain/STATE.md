# State — agents-platform
Updated: 2026-10-25 · Branch: improve/token-budget-and-review

## Goal
Claude Code plugin for readable, maintainable code at the lowest context cost — acceptance: installs from GitHub with two commands, every claim backed by `evals/` evidence, measured benefit on real tasks.

## Done (latest first, max 5)
- Plugin-only layout: rules + state via `SessionStart` hook, workflows as zero-cost skills, `plan` and other adapters removed, docs compacted — evidence: `python3 evals/offline/check.py` ALL PASS twice (Claude Code 2.1.310, mock model)
- hph adopted: `AGENTS.md` + 1.3 KB state, `harness/` retired — evidence: hph PR #10 open
- Review no longer pays the diff three times (7005 → 1101 chars on hph) — evidence: `evals/results.md` 2026-10-25

## In progress / blockers
- Benefit of the rules on real code — status: NOT RUN; user postponed the benchmark
- Real-model and interactive behavior of the plugin — status: NOT RUN

## Known pre-existing failures
- none

## Next (max 3)
1. Merge PR #2, install from GitHub (`claude plugin marketplace add Stcant/agents-platform`), try `/dev-brain:start` and `/dev-brain:review` in a real session.
2. Review and merge hph PR #10.
3. Benchmark: same real hph tasks with and without the plugin; keep only rules that move the numbers.
