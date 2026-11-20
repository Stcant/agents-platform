# State — agents-platform
Updated: 2026-11-20

## Goal
Plugin (Claude Code; Codex CLI and Copilot read it too) for readable, maintainable code at the lowest context cost — acceptance: installs from GitHub with two commands, every claim backed by `evals/` evidence, measured benefit on real tasks.

## Done (latest first, max 5)
- Plugin 2.3.0 in a PR, not merged: Codex 0.171.0 and Copilot CLI 1.0.114 support (six `agents/openai.yaml`, guard denies on Codex, Copilot context key) — evidence: `python3 evals/offline/check.py` ALL PASS (24 checks, local), six mutations each FAIL the intended check; PR #7 CI success, manual run of both jobs success (newest: Claude Code 2.1.329, Codex 0.171.0, Copilot CLI 1.0.114)
- Plugin 2.2.1 merged (PR #6): `handoff` stops writing branch/HEAD/commit status, CI pin 2.1.325 plus a newest-release job — evidence: CI success on both jobs; weekly schedule NOT RUN until it first fires
- Offline check on GitHub Actions for every PR — evidence: PR #5 run `offline-check` success, ALL PASS on a clean runner
- Plugin 2.2.0 merged (PR #4): minimal `start`, review passes the Goal line, reviewer checks weakened tests — evidence: `python3 evals/offline/check.py` ALL PASS on a clean clone of main (0d01d2b)
- No commit without the user, enforced: `PreToolUse` git guard (2.1.0) — evidence: `python3 evals/offline/check.py` ALL PASS; mutation without the hook FAILs

## In progress / blockers
- Benefit of the rules on real code — status: NOT RUN; `claude plugin eval` (with/without plugin) would measure it but needs the user's credentials and tokens
- Minimal `start` with a real model — status: partly seen on Presidio (deny rules and Stop hook adopted, `AGENTS.md` kept, not trimmed); its deletion-candidate list not seen
- Opus 5.5 system card read only through secondary reports (PDF unreachable here)
- VS Code Copilot, interactive Copilot prompts and the Codex `/hooks` trust screen — status: NOT RUN (cannot be driven here)

## Known pre-existing failures
- none

## Next (max 3)
1. User: try 2.3.0 in VS Code Copilot (do the rules arrive? do the workflows list?) and in Codex (`/hooks` trust), then decide the PR merge and run `claude plugin marketplace update dev-brain`; review hph PR #10.
2. User decision: draft a `claude plugin eval` suite (authorization, weakened tests, `start` size) and run it with `--max-cost-usd`.
3. Collect Presidio feedback: `/context all` from a fresh session, the `start` candidate list; change only what repeats twice.
