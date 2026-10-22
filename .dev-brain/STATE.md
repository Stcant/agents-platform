# State — agents-platform
Updated: 2026-10-22 · Branch: main

## Goal
A personal OpenCode engineering harness whose primary goal is readable, maintainable, correct code across languages and frameworks. Always-on design rules guide ordinary coding requests; review, commands, skills and saved state support that goal. Acceptance: concrete design guidance is installed, review covers real maintenance costs without cosmetic noise, and claims are backed by scenarios rather than assumed quality gains.

## Done (latest first, max 5)
- Updated `README.md` and `MANUALE.md`: ordinary coding requests use the design rules without special commands or a state file; Python is not required; workflow supports code quality. Clarified user-only commit decisions, review coverage and measured limits, removing stale manual claims — evidence: `python3 -B /tmp/opencode/dev-brain-docs-30rldc5g/check_docs.py` PASS (documentation checks and source hashes only); no behavioral scenarios rerun.
- Restored concise always-on code-design criteria from the old rules: complete simple solutions, project/language idioms, cohesive responsibilities, explicit effects, meaningful names, shared business knowledge without forced abstraction, error contracts and self-review — evidence: `global/AGENTS.md`; purpose aligned in `AGENTS.md`, `README.md` and `MANUALE.md`. Python is not a required stack.
- Added `evals/scenarios/maintainability.md` and fixture; ran generation and review-policy baselines before changes, then the same tasks afterward. Generation PASS before/after; policy review now reports duplicated business knowledge as maintenance risk without merging unrelated label policies — evidence: `evals/results.md`, "Readability and maintainability as the primary goal". No general generation-quality gain demonstrated.
- Tested on a disposable docling-parser copy: `/review` now lists untracked files by name and the reviewer reads them (PASS, fresh template); `/resume` no longer creates a `.venv` (PASS on the second fix; the first two attempts were served a cached template) — evidence: `evals/results.md`, section "Test on a docling-parser copy"; no commit.
- Made walkthroughs on request only and commits/amends/pushes subject to the user's explicit decision — evidence: `global/AGENTS.md`, `MANUALE.md`; no commits in this work.

## In progress / blockers
- User direction: leave docling-parser alone; no active docling work or pending request to edit its state.
- Updated `/review` delegation and TUI behavior — status: NOT RUN; the new experiment evaluated the review policy directly, not delegation or permissions. Staged-only and untracked-only/diff-empty coverage is not verified; the manual now makes the scope limits explicit.
- Cross-language code generation — status: NOT RUN; rules are language-independent, but the new fixture is Python only.
- Background server last observed serving cached command templates — not restarted in this work. Reload when safe, without interrupting user sessions.
- Italian manual — status: written — not yet exercised end-to-end by the user.
- Old copies of the kit in other repositories — status: implemented — need migration to the root `AGENTS.md` + `.dev-brain/STATE.md`.
- `/handoff` on a real repository — status: NOT RUN.

## Known pre-existing failures
- `opencode run "/command"` does not expand slash commands; this is a CLI limitation, not a kit defect.

## Next (max 3)
1. Exercise the updated reviewer through `/review` on a synthetic diff after a safe template reload; keep behavior defects separate from maintenance findings.
2. Evaluate a realistic maintenance task in a second language, without imposing Python conventions or treating one run as proof of general quality.
3. Add design instructions only for observed gaps or explicit user requirements; keep the always-on core short and output explanations on request.
