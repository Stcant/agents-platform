# dev-brain

A plugin for Claude Code (also installable in Codex CLI and GitHub Copilot, see below) that steers ordinary coding requests toward readable, maintainable code, keeps each project's state across sessions, and spends as little context as possible. Works with any model the host can use.

It provides:
- global engineering rules, injected into every session;
- the project's saved state, injected within a 3000-character budget;
- user-invoked workflows: `start`, `resume`, `handoff`, `impact`, `learn`, `review` (no context cost until invoked);
- three skills the model loads when relevant: `debugging`, `engineering-risk`, `review-feedback`;
- a read-only reviewer subagent;
- a guard that makes the host ask you before any commit, push or destructive git command (Codex refuses instead, see below).

> Manuale utente in italiano: [MANUALE.md](MANUALE.md).

## Install

```bash
claude plugin marketplace add Stcant/agents-platform
claude plugin install dev-brain@dev-brain
```

Requires `python3` and `git`. Update with `claude plugin marketplace update dev-brain`. For local development, add the cloned folder instead: `claude plugin marketplace add /path/to/agents-platform` (read in place).

## Codex and GitHub Copilot

The same marketplace and plugin install unchanged; nothing is copied or forked. Checked with the real binaries against a mock model (`python3 evals/offline/check.py`), not with a real model.

| | Claude Code | Codex CLI | Copilot CLI |
| --- | --- | --- | --- |
| Install | `claude plugin marketplace add Stcant/agents-platform`, then `claude plugin install dev-brain@dev-brain` | `codex plugin marketplace add Stcant/agents-platform`, then `codex plugin add dev-brain@dev-brain` | `copilot plugin marketplace add Stcant/agents-platform`, then `copilot plugin install dev-brain@dev-brain` |
| Rules and state | yes | yes, once you trust the plugin's hooks with `/hooks`; until then they are silently off, and so is the git guard | yes |
| Workflow call | `/dev-brain:start` | `$dev-brain:start` | listed by `copilot skill list`; calling them in an interactive session is NOT RUN |
| Workflows cost no context | yes | yes, through `agents/openai.yaml` in each workflow | yes |
| Update | `claude plugin marketplace update dev-brain` | `codex plugin marketplace upgrade dev-brain`; whether it also refreshes the installed copy is NOT RUN, so `codex plugin add dev-brain@dev-brain` again if the version does not change | `copilot plugin marketplace update`, then `copilot plugin update dev-brain` |
| Remove | `claude plugin uninstall dev-brain@dev-brain` | `codex plugin remove dev-brain@dev-brain` | `copilot plugin uninstall dev-brain` |
| Commit, push, branch change | asks you | refused: Codex hooks cannot ask, so you run the command | asks you (the interactive prompt is NOT RUN; `-p` mode cannot ask and refuses) |
| Reviewer | read-only, reads the diff with git | not loaded: `review` says so and stops | read-only, but without a shell: it cannot run git and reads the listed files |

Tested versions: Claude Code 2.1.325 (CI also ran 2.1.329), Codex CLI 0.171.0, Copilot CLI 1.0.114. The oldest version that works is unknown; older releases are NOT RUN. The install commands above were run as written from GitHub (`Stcant/agents-platform`): both Codex and Copilot CLI installed 2.3.0. The workflow names below are written for Claude Code (`/dev-brain:<name>`); on Codex write `$dev-brain:<name>`.

VS Code (Copilot agent mode) is NOT RUN: it cannot be executed here. Its documentation says agent plugins read the Claude format: add `Stcant/agents-platform` in the Customizations editor (Configure Marketplaces) or in the `chat.plugins.marketplaces` setting, then install `dev-brain`. How VS Code loads a plugin's hooks and agents is not documented, so check that the rules arrive; if they do not, paste `core/AGENTS.md` into your Copilot instructions.

## First step in every repository: `/dev-brain:start`

Run it once in each repository, from its root. Everything else builds on the two files it creates: `resume` and `handoff` read and rewrite the state, every session gets it automatically, and Claude Code reads the project facts natively (Codex and Copilot document the same for `AGENTS.md`; not tested here).

1. Inspects the real repository: stack, commands, conventions, traps. It does not open data directories (`input/`, `output/`, `.env`).
2. Writes or merges the root `AGENTS.md` as a draft, under 40 lines and only what the code does not show: exact commands, project tooling, decisions that differ from defaults, gotchas. No purpose line, stack list or architecture tour: studies find that such overviews add cost without helping the agent. It also creates or reconciles `.dev-brain/STATE.md` (goal, done with evidence, blockers, next actions, under 3000 characters).
3. Uses files from the previous kit (`harness/`, `NOW.md`, `RULES.md`) as input and lists them for you to delete. On hph, 21 KB of `harness/` became a 3.1 KB `AGENTS.md` and a 1.3 KB state.
4. Reports observed facts, unknowns, problems and the `AGENTS.md` lines it suggests deleting (it never deletes them). If it sees names like `.env` or `input/`, it also prints the permission `deny` rules you can add yourself; if the repository has a fast check, it prints the Stop-hook line that makes a passing check mandatory before a turn can end. It edits no settings file. Changes no code, installs nothing, commits nothing.

Then read both files, delete the lines the code already shows, fix anything untrue, and commit them yourself if you want them versioned. Until a repository has a state file, the session only gets a one-line hint suggesting `start`; the global rules apply either way.

## Daily use

Ask the agent to implement or fix what you need. The rules already apply; the workflows support the work.

| Workflow | When |
| --- | --- |
| `/dev-brain:start` | First adoption of a repository (see above) |
| `/dev-brain:resume` | Start of a session: reconciles the saved state with git and the code |
| `/dev-brain:handoff` | End of meaningful work: rewrites the state with verified results and next actions |
| `/dev-brain:impact <change>` | Before editing shared code: callers, contracts, tests, unknowns |
| `/dev-brain:learn <area>` | Explain a real flow or an unfamiliar stack |
| `/dev-brain:review [scope]` | Review all uncommitted changes through the read-only reviewer, which reads the diff itself with git |

For planning use Claude Code's native plan mode (Shift+Tab): it is read-only by enforcement, which a prompt cannot match.

| Always active | Used when helpful | Requires your explicit decision |
| --- | --- | --- |
| Code-design guidance and self-review of changed code | Impact analysis, independent review, session continuity | Commits, amendments, pushes and branch changes (enforced: Claude Code asks you); unrelated refactors, new dependencies or architecture changes must be proposed first |

## What is enforced, what is instructed

- **No commit without you: enforced.** A `PreToolUse` hook answers "ask" (on Codex, which cannot ask: "deny") for `git commit` (including `--amend`), `push`, `merge`, `rebase`, `cherry-pick`, `revert`, `checkout`/`switch`, history-moving `reset`, `clean -f`, `branch -d/-m/-f`, `stash drop/pop/clear` and tag deletion, even inside chained commands and even when your settings allow git. Read-only git runs normally.
- **Reviewer read-only: enforced on Claude Code and Copilot CLI** (not loaded on Codex). Its tool list allows Read, Grep, Glob and `git diff/log/show/status`; any command that creates, changes or removes files needs your approval.
- **State budget: enforced.** Over 3000 characters only a notice is injected, telling the model to read the file and suggest `handoff`.
- **Everything else is instructed:** rules guide the model; they do not guarantee good code.

## Evaluation

```bash
python3 evals/offline/check.py        # CLAUDE / CODEX / COPILOT=<binary> if not on PATH
```

Installs the plugin into a throwaway home, replaces the model with a local mock that records every request, and checks in about 20 seconds, at zero token cost. Claude Code (required): rules and state reach the session, oversized state becomes a notice, workflows expand and stay out of the skill listing, the reviewer reads the diff but cannot write, and commit and push need you even when your settings allow git. Codex CLI and Copilot CLI (run when found; an explicit `CODEX` or `COPILOT` variable makes them required): rules and state arrive, workflows stay out of the skill listing, commit and push are stopped, and Copilot's reviewer has no shell. GitHub Actions runs it on every pull request (`.github/workflows/offline-check.yml`, Claude Code 2.1.325, Codex 0.171.0, Copilot CLI 1.0.114, no secrets); pushes to `main`, a weekly run and manual runs also test the newest releases. It does not judge model behavior; `evals/scenarios/` describes the real-model scenarios and `evals/results.md` records decisions and evidence.

## Layout

```
.claude-plugin/marketplace.json   marketplace listing the plugin
core/                             the plugin: AGENTS.md rules, skills/, agents/, hooks/, bin/ (context and git guard)
evals/                            scenarios, fixtures, results, offline check
MANUALE.md                        Italian user manual
```
