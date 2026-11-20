# Evaluation results

A log of decisions and the evidence behind them, newest first. Full run details are in git history (before 2026-10-25: `git show 50fcef9:evals/results.md`).

## Open question: does the kit improve the code?

Not measured. Real-model evidence so far: one model per scenario, one run, small synthetic Python fixtures; the no-kit baseline already solved every task. The one measured gain is the review policy (below). Next: the same real tasks with and without the plugin, same model; compare tokens per task, fix iterations, review findings, time to resume after a break. Keep what moves the numbers.

## 2026-11-20 — Codex CLI and Copilot (CLI) support, plugin 2.3.0

The user asked to use the plugin in Codex and GitHub Copilot (VS Code). This reverses the 2026-10-25 "Claude Code only" decision; the adapters removed then are not restored. Principle: install the unchanged plugin first and change only what the real binaries show broken.

Read: OpenAI's Codex plugin, skills and hooks pages; VS Code's agent-plugin and hooks references; GitHub's Copilot CLI hooks reference (first 100,000 of 136,092 characters). Run: Codex CLI 0.171.0 and Copilot CLI 1.0.114 (`@github/copilot`, offline with `COPILOT_OFFLINE` and an Anthropic-type provider pointed at the mock).

Worked unchanged on both: `marketplace add` of this repository (Codex reads `.claude-plugin/marketplace.json` as a legacy format), plugin install from `core/.claude-plugin/plugin.json`, all nine skills, `tool_input.command` in the `PreToolUse` payload, and on Copilot the Claude-format `ask`/`deny` answer.

Broken, and fixed:
1. Codex lists all nine skills, the six workflows included (about 1,090 characters each session): it ignores `disable-model-invocation`. Fix: `agents/openai.yaml` with `policy.allow_implicit_invocation: false` in the six workflows (documented key); the listing drops to the three model-loaded skills and `$dev-brain:<name>` still expands.
2. Codex cannot ask: the guard's "ask" marks the hook failed and the command runs (observed, as documented). Fix: the guard answers "deny" when `PLUGIN_ROOT` is set without `COPILOT_PLUGIN_ROOT` (Codex sets the first only; Claude Code sets neither). The user then runs the command: stricter than "ask", with no approval path in the chat.
3. Copilot CLI ignores `hookSpecificOutput.additionalContext` of `SessionStart` and reads a top-level `additionalContext`; rules and state were missing. Fix: the context hook adds that key when `COPILOT_PLUGIN_ROOT` is set. Measured: both keys give one injection on Copilot, Claude Code ignores the extra key, Codex fails the hook on it, hence the condition.

Observed, not changed (documented as limits):
- Codex runs plugin hooks only after the user trusts them (`/hooks`); `codex exec` prints nothing when they are not, and with them untrusted a `git commit` went through (commits 1 -> 2). Codex does not load the plugin's `agents/reviewer.md`, so `review` stops at its "no reviewer" step by design.
- Copilot CLI loads the reviewer but its `Bash(git diff:*)` entries map to nothing: the sub-agent gets `view`, `grep` and `glob` only. Read-only holds; it cannot run git and reads the listed files. Giving it a shell would break read-only, so no change.
- Copilot ignores hook matchers, and its `source` is `new`; the Claude-format hook file still ran.

Evidence: `python3 evals/offline/check.py` ALL PASS, 24 checks (11 Claude Code 2.1.325, 8 Codex 0.171.0, 5 Copilot CLI 1.0.114), about 13 s. Six mutations each failed the intended check: no `openai.yaml` for one workflow, guard always "ask" (Codex: 0/2 refused), no top-level key (Copilot rules missing), top-level key for everyone (Codex rules missing), reviewer with `Bash` (Copilot reviewer tools included `bash`), no hooks (guard and context checks on all three hosts). `claude plugin validate core`: passes with the same warnings as `main`. CI now installs the three CLIs at pinned versions on pull requests and at `@latest` on pushes to `main`, weekly and on demand; `CODEX` and `COPILOT` make their checks required there. On GitHub Actions: pull request #7, pinned job success; manual run of the branch, both jobs success, and `latest` resolved to Claude Code 2.1.329, Codex 0.171.0, Copilot CLI 1.0.114, so Claude Code 2.1.329 (newer than the 2.1.325 pin) also passes. The weekly schedule is still NOT RUN.

Limits: VS Code is NOT RUN (cannot be executed here); the docs say its Local hook harness reads `hookSpecificOutput`, which the unchanged output satisfies, and that harness is deprecated (removal announced for February 2027), but plugin hook and agent loading in VS Code is undocumented. Calling the workflows in an interactive Copilot session, Copilot's interactive "ask" prompt, and the Codex `/hooks` trust screen are NOT RUN (the binaries were driven non-interactively). No real model was used on any host, so whether the rules improve code there is as unmeasured as on Claude Code. The host markers are env variables read from the binaries' behavior today; if a host changes them the matching check fails.

## 2026-11-15 — New releases reviewed; state without branch or commit status; CI on the newest Claude Code (plugin 2.2.1)

Read: Anthropic's Opus 5.5 announcement (22 Sep, primary); the Opus 5.5 system card only through two secondary reports (its PDF is not reachable from this environment, so card-level figures are second-hand); TechCrunch on Fable 5.2 / Mythos 5.2 (9 Nov; no system card read); Claude Code's changelog for 2.1.299–2.1.311 (2.1.312–2.1.325 not read) and the `claude plugin eval` docs.

Changed:
1. `handoff` no longer writes the branch, HEAD or whether changes are committed, and the state header is `Updated: <date>`. Seen three times: this repository's state ("uncommitted edits"), Presidio `6cb61b0` (the state says "non committate" inside the commit that contains them) and Presidio `67f4f99` (a commit whose only purpose was to remove the branch line).
2. `handoff` step 4 named "stack, architecture" for `AGENTS.md`, contradicting 2.2.0. In Presidio the architecture section was edited in the same session; which command did it is not proven.
3. CI: pin 2.1.310 → 2.1.325. A second job runs the newest release on pushes to `main`, weekly and on demand: 15 version numbers shipped in three weeks, and the notes read include hook and permission changes (2.1.299: a plugin hook that cannot receive its input or return an answer now blocks the action; 2.1.309: stricter bash permission checks).

Considered, not changed:
- Guard for destructive non-git commands. Anthropic says Opus 5.5 is "much less likely" to take hard-to-reverse actions and attempted to circumvent boundaries about 85% less often than Opus 5 in its containment test; a secondary report adds that it asks before destructive steps. The git guard stays the only enforced layer.
- Reviewer check for planted instructions in `AGENTS.md`/`CLAUDE.md`. Reported only for pre-release snapshots, after a copying slip, at under 0.01% of completions; the released model is said to have a negligible copying error rate. Weak evidence.
- A rule that text in files, tool output or pasted prompts is not authorization. The card audit reportedly finds Opus 5.5 more willing to accept unverifiable authority claims and to follow malicious instructions in pasted text (no rates given). Plausible, but the effect of a rule is unmeasured; measure first.
- `claude plugin validate`. On `core/` it passes with warnings. In a mutation test it failed on broken JSON, which the offline check already catches, and missed a skill without a description unless `--strict` is used; `--strict` fails the clean plugin on missing `author` and marketplace description. Not added.
- Effort or model settings for the reviewer: Anthropic advises testing effort per task; there are no data here.

Evidence: `python3 evals/offline/check.py` ALL PASS (11 checks) with Claude Code 2.1.325, locally and on GitHub Actions (pull request #6: pinned job success, newest-release job skipped as designed; manual run of the branch: both jobs success, `latest` resolved to 2.1.325, so it did not yet test a different release). The weekly schedule cannot run before the merge: NOT RUN.

Limits: Opus 5.5 and Fable/Mythos 5.2 are reported to suspect they are being tested, so real-model results from small synthetic fixtures (every earlier entry) may not transfer to real work. The native `claude plugin eval` runs each case three times with and without the plugin, with free graders (`regex`, `tool_used`, `tool_order`, `file_exists`) and `--max-cost-usd`; it would measure what no entry here has, the benefit against no plugin. NOT RUN: it needs credentials and tokens (cases × runs × 2 arms).

## 2026-11-03 — Offline check on GitHub Actions

`.github/workflows/offline-check.yml` runs `python3 evals/offline/check.py` on every pull request, on pushes to `main` and on demand: Ubuntu runner, Node 22, `npm install --global @anthropic-ai/claude-code@2.1.310`, read-only token, no secrets.

Evidence: pull request #5, run `offline-check`: success, 11 checks ALL PASS on a clean runner (about 13 s). Before that, `main` at 0d01d2b (plugin 2.2.0) was cloned into an empty directory and gave ALL PASS locally. The script exits with 1 when a check fails, so the job fails with it; a failing run on CI was not provoked.

Limits: the version is pinned, so a newer Claude Code release is not tested until the pin is bumped; actions are referenced by major tag (`@v4`), not commit SHA; a red check does not block a merge unless branch protection requires it (not set); the check still does not judge model answers.

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

The user works with Claude Code only (reversed on 2026-11-20 for Codex and Copilot, see above). Adapters for OpenCode, Codex CLI and Cursor were removed; `core/` keeps standard formats (`AGENTS.md`, `SKILL.md`) so another agent remains an adapter away.

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
