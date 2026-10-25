# dev-brain

Personal engineering harness for coding agents: **OpenCode, Claude Code, Codex CLI and Cursor**, with any model provider. One install, used across every repository.

Its primary goal is to guide normal coding requests toward readable, maintainable code, adapted to each project's language and conventions. Workflows and saved state are supporting tools, not the purpose of the kit.

It provides:
- rules that are always loaded, kept short and limited to behavior the model would not follow by default;
- user-invoked workflows: start, resume, handoff, plan, impact, learn, review;
- an independent read-only reviewer;
- three on-demand skills: debugging, review feedback, engineering risk;
- the project's saved state injected into the agent's context, within a size budget.

Project facts stay in each repository. Nothing from one project is reused in another.

> Manuale utente in italiano: [MANUALE.md](MANUALE.md).

## Code quality by default

The global rules apply to ordinary coding requests; no special workflow is required. They favor complete but simple solutions, cohesive responsibilities, explicit effects, intention-revealing names and a single source for shared business rules. They reject speculative abstractions, forced layering and silent error handling. Before delivery the agent checks its changed code for these problems without adding an unsolicited explanation.

These are language-independent criteria, not a Python style guide. The agent discovers the stack and follows its idioms. The review workflow adds an independent check for defects and concrete maintenance costs, not cosmetic preferences.

| Always active | Used when helpful | Requires your explicit decision |
| --- | --- | --- |
| Code-design guidance and self-review of changed code | Planning, impact analysis, independent review and session continuity | Commits, amendments and pushes; unrelated refactors, new dependencies or architecture changes must be proposed first |

Detailed change walkthroughs are on request only. See [`core/AGENTS.md`](core/AGENTS.md) for the full rules. Instructions guide the model; they do not guarantee good code.

## How it is built

`core/` is the only source. It uses the formats the agents share: `AGENTS.md` for rules and Agent Skills (`SKILL.md`) for workflows and skills. `install.py` links or translates it into what each agent reads; no rule lives in an adapter.

| | OpenCode | Claude Code | Codex CLI | Cursor |
| --- | --- | --- | --- | --- |
| Global rules | `AGENTS.md` (link) | `CLAUDE.md` imports `core/AGENTS.md` | `AGENTS.md` (link) | `rules/dev-brain.mdc` (copy) |
| Workflows | commands `/review` | plugin `/dev-brain:review` | plugin skills `$dev-brain:review` | skills `/review` |
| Skills | `skills/` (links) | plugin | plugin | `skills/` (links) |
| Read-only reviewer | permissions: only `git diff/log/show/status`; `>` and `--output` denied | tools: Read, Grep, Glob, read-only git; other commands need your approval | `sandbox_mode = "read-only"`, **not enforced on spawned agents** (Codex 0.164): instruction only | `readonly: true` |
| Saved state | plugin, every main-session call | `SessionStart` hook | `SessionStart` hook, after you approve it once | `sessionStart` hook (Cursor bug drops it) + rule fallback |

When an agent cannot inject the state, the global rules tell it to read `.dev-brain/STATE.md` before continuing earlier work. The state text and its 3000-character budget come from one script, `core/bin/dev-brain-context`, used by every adapter.

## Install

```bash
./install.sh                          # every agent found on this machine
./install.sh opencode claude-code     # or name them: opencode claude-code codex cursor
```

Requires `python3` and `git`. Re-run it after pulling changes. Existing files that are not managed by this kit are moved to `*.bak.<timestamp>`, never deleted.

- **OpenCode**: restart the background server when no session is active (`opencode service restart`).
- **Claude Code / Codex**: the installer builds a local plugin marketplace in `build/` and installs `dev-brain` from it with the agent's own CLI.
- **Codex**: approve the `SessionStart` hook once in the TUI; new hooks need review before they run.
- **Cursor**: if the agent ignores the rules, paste `core/AGENTS.md` into Settings > Rules (file-based global rules are not always loaded).

## Daily use

Ask the agent to implement or fix what you need. The workflows support that work; they are not a mandatory sequence or a switch that enables code quality. Invoke them with the agent's syntax from the table above (`/review`, `/dev-brain:review`, `$dev-brain:review`).

| Workflow | When |
| --- | --- |
| `start` | First adoption of a repository: writes project facts in the root `AGENTS.md` and creates `.dev-brain/STATE.md`; migrates files from the previous kit (`harness/`) without deleting them |
| `resume` | Start of a session: reconciles the saved state with the real repository |
| `handoff` | End of meaningful work: rewrites the state with verified results and next actions |
| `plan` | Non-trivial change: read-only plan-contract with at most five steps |
| `impact` | Before editing: callers, contracts, tests and unknowns |
| `learn` | Explain a real flow or an unfamiliar stack |
| `review` | Review all uncommitted changes (staged, unstaged, untracked) through the read-only reviewer, which reads the diff itself with git |

## What lives in a project

```
<repo>/
├── AGENTS.md            project facts: stack, commands, conventions, gotchas (under 60 lines)
└── .dev-brain/
    └── STATE.md         goal, done with evidence, blockers, max 3 next actions (under 3000 characters)
```

All four agents read the project `AGENTS.md`. Both files are intended for version control, but committing them always requires your explicit decision. The state is a working document, not a diary.

## Evaluation

`evals/offline/check.py` installs the kit into a throwaway home for every agent CLI it finds, replaces the model with a local mock that records every request (`evals/offline/mock_model.py`), and checks in about ten seconds, at zero token cost, what the kit controls: rules and state reach the agent, oversized state becomes a notice, workflows expand, the reviewer reads the diff but cannot write. Cursor is checked only for its generated files. Run it after changing `core/`, an adapter or the installer:

```bash
python3 evals/offline/check.py        # OPENCODE / CLAUDE / CODEX=<binary> if not on PATH
```

`evals/scenarios/` describes realistic tasks and the expected model behavior; `evals/results.md` records measured results and limits. Every change to rules, workflows or skills should be justified by a scenario.

Run a scenario manually in a fixture:

```bash
# Only after explicitly authorizing local fixture commits:
./evals/setup.sh          # copies fixtures to /tmp/opencode/dev-brain-evals and recreates git history
cd /tmp/opencode/dev-brain-evals/bugfix
opencode run --standalone -m <provider/model> "The discount test fails. Fix the code." < /dev/null
```

In scripts, close stdin: `opencode run` waits for EOF on non-terminal stdin.

## Migration from the previous kit

Content of the old visible `dev-brain/` folder remains in git history at commit `08baebc`. For a repository that received a copy (`RULES.md`, `NOW.md`, `harness/PROJECT_STATE.md`, `harness/PROJECT_MAP.md`), run the `start` workflow: it carries still-true facts into `AGENTS.md` and `.dev-brain/STATE.md` and lists the old files for you to delete.

## Layout

```
core/         the only source: AGENTS.md rules, workflows/, skills/, agents/reviewer.md, bin/, templates/
adapters/     agent-specific code that cannot be expressed as files (OpenCode plugin)
install.py    links or translates core/ for each agent; install.sh is a wrapper
evals/        scenarios, fixtures, results, offline mock check
MANUALE.md    Italian user manual
```
