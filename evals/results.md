# Evaluation results

A log of decisions and the evidence behind them, newest first. Full run details are in git history (before 2026-10-25: `git show 50fcef9:evals/results.md`).

## Open question: does the kit improve the code?

Not measured. Real-model evidence so far: one model per scenario, one run, small synthetic Python fixtures; the no-kit baseline already solved every task. The one measured gain is the review policy (below). Next: the same real tasks with and without the plugin, same model; compare tokens per task, fix iterations, review findings, time to resume after a break. Keep what moves the numbers.

## 2026-11-03 — Minimal `start`, review against the goal, weakened-test check (plugin 2.2.0)

Changes: (1) `start` writes `AGENTS.md` as a draft under 40 lines with only commands, tooling, deviations from defaults and gotchas; no purpose line, stack list or architecture overview. Overview lines already in an existing file are listed for deletion, never removed. For names like `.env` or `input/` it prints the permission deny rules for the user to add. (2) `review` passes the state's Goal line to the reviewer as unverified requirements. (3) The reviewer also checks that no test was deleted, skipped, loosened or special-cased to pass. (4) When the repository has a fast check, `start` prints a Stop-hook line (exit code 2 blocks the turn) for the user to add; the plugin enforces nothing there.

Evidence is external; nothing is measured locally yet:
- arXiv 2602.11988 (four agents, including Claude Code with Sonnet 4.5): LLM-generated context files changed success by -0.5 to -2 points and raised cost about 20-23%; overviews did not reduce the steps to the first relevant file; tooling instructions were followed (a mentioned tool was used 1.6 times per task against under 0.01).
- arXiv 2601.20404 (Codex, 124 PRs) found shorter runs with an `AGENTS.md` (median -28.6% time, -16.6% output tokens, total tokens about unchanged, correctness not measured). The effect is contested, so it needs a measurement here.
- Anthropic's best-practices guide: review against a spec, keep the context file to what the code does not show, put no-exception rules in hooks or deny rules. arXiv 2606.26300 lists test tampering and overfitting to visible tests among documented agent failures.

Local: `python3 evals/offline/check.py` ALL PASS (11 checks, Claude Code 2.1.310, mock model).

Limits: no real-model run of the new `start`; hph's 41-line `AGENTS.md` predates it and is not re-trimmed; deny rules are suggestions, not enforced by the plugin, and do not stop a script that opens the file; the studies measure task success and cost, not maintainability; the goal line can be stale, so the reviewer treats it as unverified. The built-in `/code-review` (alias `/review`; it looks for correctness bugs and can apply fixes) is documented; a side-by-side run against `/dev-brain:review` on one diff is NOT RUN.

## 2026-10-25 — Commit rule enforced by a hook (plugin 2.1.0)

The no-commit rule was instruction only; the user asked for enforcement. `core/bin/dev-brain-guard` is a `PreToolUse` hook on Bash that answers "ask" for git commands changing history, branches or the remote (commit/amend, push, merge, rebase, cherry-pick, revert, am, checkout, switch, history-moving reset, clean -f, branch -d/-m/-f, stash drop/pop/clear, tag -d/-f), parsed per chained segment and past global options (`git -C dir commit`).

- Unit cases: 30 commands, read-only ones pass (`status`, `diff`, `log`, `show`, `stash`, `reset <file>`, `clean -n`, `echo git commit`).
- `evals/offline/check.py`: with `--allowedTools "Bash(git:*)"`, `git status` ran, `git commit -am` and `git push` were stopped with the guard's reason, commit count unchanged. Removing the hook makes this check FAIL (0/2 guarded).
- The rule in `core/AGENTS.md` now tells the model not to work around the prompt.
- Limits: a commit made by a tool other than Bash (an MCP git server, a script the user runs) is not covered; in an interactive session "ask" shows a prompt, so the user's yes still commits — by design.

## 2026-10-25 — Claude Code only, distributed as a plugin

The user works with Claude Code only. Adapters for OpenCode, Codex CLI and Cursor were removed; `core/` keeps standard formats (`AGENTS.md`, `SKILL.md`) so another agent remains an adapter away.

- Global rules and state come from one `SessionStart` hook (`startup|resume|clear|compact`); no edit to `CLAUDE.md` or settings. Claude Code puts the hook output in a system-role message.
- Workflows are plugin skills with `disable-model-invocation: true`: not listed in the system prompt (verified), invoked as `/dev-brain:<name>`. The bare `/review` keeps opening Claude Code's built-in review.
- `plan` removed: Claude Code's plan mode is read-only by enforcement; a prompt cannot match that.
- Templates removed: the `start` skill holds them, once.
- Evidence: `python3 evals/offline/check.py` ALL PASS twice (Claude Code 2.1.310, mock model): rules and state in context, oversized state → notice, `start`/`resume`/`review` expand, workflows absent from the listing, reviewer reads `git diff` and has `>`, `touch`, `; rm` refused pending approval, no file written.
- Limits: no real model, no interactive session.

## 2026-10-25 — Multi-agent probe (superseded, findings kept)

Tested OpenCode 2.1.4, Claude Code 2.1.310, Codex 0.164 against the mock; Cursor from docs only.

- Claude Code reads project `AGENTS.md` natively; global rules need `CLAUDE.md` (`@/abs/path` import works) or a hook.
- No skill directory is read by all four agents; Codex copies plugins and drops symlinked directories.
- Codex 0.164 does not apply a custom agent's `sandbox_mode = "read-only"` to the spawned agent: with a writable parent, the reviewer wrote a file. Codex hooks run only after the user trusts them.
- Cursor's `sessionStart` `additional_context` is dropped (open Cursor bug).

## 2026-10-25 — Review and state token cost (tested on hph)

- The review command embedded the full diff, then the agent copied it into the subagent prompt: the diff was paid as input, output and reviewer input. Now the reviewer reads it with read-only git; on a 5.9 KB hph diff the command message went from 7005 to 1101 characters.
- `git diff` missed staged changes and stopped on untracked-only changes; now `git status` + `git diff HEAD --stat` (fallback `--cached`).
- The state was injected into subagents too, and an 80-line cap did not bound size (this repo's state was 3.9 KB). Now: main session only, 3000-character budget, a notice above it (not truncated: truncation would drop `Next`).
- `resume` guarded only Python (`uv`/`.venv`); now any install, download or compile is reported NOT RUN.
- `start` now migrates previous-kit files; hph's 21 KB `harness/` became `AGENTS.md` 3.1 KB + state 1.3 KB (hph PR #10). Its old next action was already done.
- Gotchas found: OpenCode did not block `>` without an explicit rule; `opencode run` waits on non-terminal stdin.

## 2026-10-22 — Review policy covers maintenance problems

Scenario `scenarios/maintainability.md`, model `github-copilot/claude-haiku-5.5`, one run per version. Before: the reviewer excluded a duplicated shipping rule because no behavior changed. After: reported as a maintenance problem with the two locations and a shared calculation as the fix; similar but unrelated label functions correctly not merged. Generated code was already readable before and after: no generation-quality gain shown. Python only.

## 2026-10-22 — Workflow scenarios on OpenCode (historical)

Model `opencode/deepseek-v4.1-flash-free`, baseline = no kit.

- Bugfix: both fixed the sign error; the kit ran the failing test first and recorded before/after evidence.
- Resume with stale state: both noticed the stale next action; the kit reran the suite instead of quoting the old PASS.
- Explain a flow: both correct; the kit added OBSERVED/INFERRED labels, a reading order and a runtime check, at greater length.
- Handoff: fresh evidence, two next actions, no commit.
- Adoption on docling-parser (clinical data): the agent listed `input/`/`output/` filenames; the rule now forbids opening or listing data directories.
- `resume` created a 3.5 GB `.venv`; fixed by the no-install rule.
