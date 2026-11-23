# State — agents-platform
Updated: 2026-11-23

## Goal
Plugin (Claude Code, plus an OpenCode adapter) for readable, maintainable code at the lowest context cost — acceptance: installs from GitHub with two commands, every claim backed by `evals/` evidence, measured benefit on real tasks.

## Done (latest first, max 5)
- Plugin 2.4.0 merged (PR #9, 2fc3c7e): Codex and Copilot support removed (user decision), OpenCode adapter `adapters/opencode/index.ts` added — evidence: `python3 evals/offline/check.py` ALL PASS (20 checks: 11 Claude Code 2.1.325, 9 OpenCode 2.3.2), six adapter mutations each FAIL the intended check; PR #9 CI success on both jobs (newest: Claude Code 2.1.330, OpenCode 2.4.0)
- Plugin 2.2.1 merged (PR #6): `handoff` stops writing branch/HEAD/commit status, CI pin 2.1.325 plus a newest-release job — evidence: CI success on both jobs; weekly schedule NOT RUN until it first fires
- Offline check on GitHub Actions for every PR — evidence: PR #5 run `offline-check` success, ALL PASS on a clean runner
- Plugin 2.2.0 merged (PR #4): minimal `start`, review passes the Goal line, reviewer checks weakened tests — evidence: `python3 evals/offline/check.py` ALL PASS on a clean clone of main (0d01d2b)

## In progress / blockers
- Benefit of the rules on real code — status: NOT RUN; `claude plugin eval` (with/without plugin) would measure it but needs the user's credentials and tokens
- Minimal `start` with a real model — status: partly seen on Presidio (deny rules and Stop hook adopted, `AGENTS.md` kept, not trimmed); its deletion-candidate list not seen
- Opus 5.5 system card read only through secondary reports (PDF unreachable here)
- OpenCode TUI (the interactive ask prompt, `@start`) and OpenCode 1.x — status: NOT RUN (the TUI cannot be driven here)

## Known pre-existing failures
- none

## Next (max 3)
1. User: adapter installed from `main` (user-run: `opencode debug agents` lists `reviewer`); still to try in the TUI: `@start` and a commit (the guard's ask prompt), then report what appears.
2. User decision: draft a `claude plugin eval` suite (authorization, weakened tests, `start` size) and run it with `--max-cost-usd`.
3. Collect Presidio feedback: `/context all` from a fresh session, the `start` candidate list; change only what repeats twice.
