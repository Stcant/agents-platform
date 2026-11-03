# State — agents-platform
Updated: 2026-11-03 · Branch: ci/offline-check (PR #5; main has plugin 2.2.0)

## Goal
Claude Code plugin for readable, maintainable code at the lowest context cost — acceptance: installs from GitHub with two commands, every claim backed by `evals/` evidence, measured benefit on real tasks.

## Done (latest first, max 5)
- Offline check runs on GitHub Actions for every PR and push to main (Claude Code 2.1.310 pinned) — evidence: PR #5 run `offline-check` success, ALL PASS on a clean runner
- Plugin 2.2.0 merged (PR #4): minimal `start`, review passes the Goal line, reviewer checks weakened tests — evidence: `python3 evals/offline/check.py` ALL PASS on a clean clone of main (0d01d2b); external studies in `evals/results.md` 2026-11-03
- No commit without the user, enforced: `PreToolUse` git guard (plugin 2.1.0) — evidence: `python3 evals/offline/check.py` ALL PASS; mutation without the hook FAILs
- Plugin-only layout: rules + state via `SessionStart` hook, workflows as zero-cost skills, `plan` and other adapters removed, docs compacted — evidence: `python3 evals/offline/check.py` ALL PASS twice (Claude Code 2.1.310, mock model)
- hph adopted: `AGENTS.md` + 1.3 KB state, `harness/` retired — evidence: hph PR #10 open

## In progress / blockers
- Benefit of the rules on real code — status: NOT RUN; user postponed the benchmark
- Real-model and interactive behavior of the plugin, including the minimal `start` — status: NOT RUN; the user is collecting feedback from a real repository

## Known pre-existing failures
- none

## Next (max 3)
1. User: `claude plugin marketplace update dev-brain`, try `/dev-brain:start` on a real repo (keep a copy of its old `AGENTS.md`); review hph PR #10 (its `AGENTS.md` predates the minimal `start`).
2. Collect feedback from real use: the user's `AGENTS.md`/`STATE.md`, `/context`, `/usage`, `/skill-doctor`, `/doctor prompt-audit`, and a defect log; change only what repeats twice.
3. Ablation on real tasks: `core/AGENTS.md` full vs reduced, and the three model-loaded skills with vs without; keep only what moves steps, cost or review findings.
