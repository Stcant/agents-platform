# dev-brain

A Claude Code plugin that steers ordinary coding requests toward readable, maintainable code, keeps each project's state across sessions, and spends as little context as possible. Works with any model Claude Code can use.

It provides:
- global engineering rules, injected into every session;
- the project's saved state, injected within a 3000-character budget;
- user-invoked workflows: `start`, `resume`, `handoff`, `impact`, `learn`, `review` (no context cost until invoked);
- three skills the model loads when relevant: `debugging`, `engineering-risk`, `review-feedback`;
- a read-only reviewer subagent;
- a guard that makes Claude Code ask you before any commit, push or destructive git command.

> Manuale utente in italiano: [MANUALE.md](MANUALE.md).

## Install

```bash
claude plugin marketplace add Stcant/agents-platform
claude plugin install dev-brain@dev-brain
```

Requires `python3` and `git`. Update with `claude plugin marketplace update dev-brain`. For local development, add the cloned folder instead: `claude plugin marketplace add /path/to/agents-platform` (read in place).

## First step in every repository: `/dev-brain:start`

Run it once in each repository, from its root. Everything else builds on the two files it creates: `resume` and `handoff` read and rewrite the state, every session gets it automatically, and Claude Code reads the project facts natively.

1. Inspects the real repository: purpose, stack and versions, exact commands, conventions, gotchas. It does not open data directories (`input/`, `output/`, `.env`).
2. Writes or merges the root `AGENTS.md` (project facts, under 60 lines) and creates or reconciles `.dev-brain/STATE.md` (goal, done with evidence, blockers, next actions, under 3000 characters).
3. Uses files from the previous kit (`harness/`, `NOW.md`, `RULES.md`) as input and lists them for you to delete. On hph, 21 KB of `harness/` became a 3.1 KB `AGENTS.md` and a 1.3 KB state.
4. Reports observed facts, unknowns and problems; changes no code, installs nothing, commits nothing.

Then read both files, fix anything untrue, and commit them yourself if you want them versioned. Until a repository has a state file, the session only gets a one-line hint suggesting `start`; the global rules apply either way.

## Daily use

Ask Claude Code to implement or fix what you need. The rules already apply; the workflows support the work.

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

- **No commit without you: enforced.** A `PreToolUse` hook answers "ask" for `git commit` (including `--amend`), `push`, `merge`, `rebase`, `cherry-pick`, `revert`, `checkout`/`switch`, history-moving `reset`, `clean -f`, `branch -d/-m/-f`, `stash drop/pop/clear` and tag deletion, even inside chained commands and even when your settings allow git. Read-only git runs normally.
- **Reviewer read-only: enforced.** Its tool list allows Read, Grep, Glob and `git diff/log/show/status`; any command that creates, changes or removes files needs your approval.
- **State budget: enforced.** Over 3000 characters only a notice is injected, telling the model to read the file and suggest `handoff`.
- **Everything else is instructed:** rules guide the model; they do not guarantee good code.

## Evaluation

```bash
python3 evals/offline/check.py        # CLAUDE=<binary> if claude is not on PATH
```

Installs the plugin into a throwaway home, replaces the model with a local mock that records every request, and checks in about 20 seconds, at zero token cost: rules and state reach the session, oversized state becomes a notice, workflows expand and stay out of the skill listing, the reviewer reads the diff but cannot write, and commit and push need you even when your settings allow git. It does not judge model behavior; `evals/scenarios/` describes the real-model scenarios and `evals/results.md` records decisions and evidence.

## Layout

```
.claude-plugin/marketplace.json   marketplace listing the plugin
core/                             the plugin: AGENTS.md rules, skills/, agents/, hooks/, bin/ (context and git guard)
evals/                            scenarios, fixtures, results, offline check
MANUALE.md                        Italian user manual
```
