# dev-brain

Personal engineering harness for OpenCode V2. One install, used across every repository.

Its primary goal is to guide normal coding requests toward readable, maintainable code, adapted to each project's language and conventions. Commands and saved state are supporting tools, not the purpose of the kit.

It provides:
- rules that are always loaded, kept short and limited to behavior the model would not follow by default;
- commands for the recurring workflow: start, resume, handoff, plan, impact, learn, review;
- an independent read-only reviewer;
- three on-demand skills: debugging, review feedback, engineering risk;
- a small plugin that injects each project's saved state into the main session's model calls, within a size budget.

Project facts stay in each repository. Nothing from one project is reused in another.

> Manuale utente in italiano: [MANUALE.md](MANUALE.md).

## Code quality by default

The global rules apply to ordinary coding requests; no special command is required. They favor complete but simple solutions, cohesive responsibilities, explicit effects, intention-revealing names and a single source for shared business rules. They reject speculative abstractions, forced layering and silent error handling. Before delivery the agent checks its changed code for these problems without adding an unsolicited explanation.

These are language-independent criteria, not a Python style guide. The agent discovers the stack and follows its idioms. `/review` adds an independent check for defects and concrete maintenance costs, not cosmetic preferences.

Describe the feature or bug, its constraints and the expected behavior. You do not need to repeat "write maintainable code", invoke a skill, or create a state file before these rules apply.

| Always active | Used when helpful | Requires your explicit decision |
| --- | --- | --- |
| Code-design guidance and self-review of changed code | Planning, impact analysis, independent review and session continuity | Commits, amendments and pushes; unrelated refactors, new dependencies or architecture changes must be proposed first |

Detailed change walkthroughs are on request only. A normal answer stays concise: what changed, checks actually run, and material limits. See [`global/AGENTS.md`](global/AGENTS.md) for the full rules.

Instructions guide the model; they do not guarantee good code. Behavioral tests and maintenance scenarios are evaluated separately in `evals/`.

## Install

```bash
./install.sh
```

The script symlinks the kit into `~/.config/opencode` and registers the plugin in `~/.config/opencode/opencode.json`:

| Source | Destination |
| --- | --- |
| `global/AGENTS.md` | `~/.config/opencode/AGENTS.md` |
| `global/commands/*.md` | `~/.config/opencode/commands/` |
| `global/agents/*.md` | `~/.config/opencode/agents/` |
| `global/skills/*` | `~/.config/opencode/skills/` |
| `plugin/dev-brain` | registered in `opencode.json` |

Existing files that are not managed by this kit are moved to `*.bak.<timestamp>`, never deleted. The script is idempotent.

After installing, start a new session. If the background server was already running, restart it when no session is active (`opencode service restart`) so commands are reloaded.

## Daily use

Ask OpenCode to implement or fix what you need, using the project's existing language and tools. The commands below support that work; they are not a mandatory sequence or a switch that enables code quality.

| Command | When |
| --- | --- |
| `/start` | First adoption of a repository: writes project facts in the root `AGENTS.md` and creates `.dev-brain/STATE.md`; migrates files from the previous kit (`harness/`) without deleting them |
| `/resume` | Start of a session: reconciles the saved state with the real repository |
| `/handoff` | End of meaningful work: rewrites the state with verified results and next actions |
| `/plan <goal>` | Non-trivial change: plan-contract with at most five steps |
| `/impact <change>` | Before editing: callers, contracts, tests and unknowns |
| `/learn <area>` | Explain a real flow or an unfamiliar stack |
| `/review [scope]` | Review all uncommitted changes (staged, unstaged, untracked) through the read-only reviewer, which reads the diff itself with git |

When present, the plugin injects `.dev-brain/STATE.md` automatically, making the saved goal available at session start. Saved notes may be stale: `/resume` reconciles them with `git status` and recent commits. Neither `/start` nor a state file is required for the global design rules to apply.

## What lives in a project

```
<repo>/
├── AGENTS.md            project facts: stack, commands, conventions, gotchas (under 60 lines)
└── .dev-brain/
    └── STATE.md         goal, done with evidence, blockers, max 3 next actions (under 3000 characters)
```

Create them with `/start` when adopting the project. Both files are intended for version control, but committing them always requires your explicit decision. The state is a working document, not a diary: replace stale content at every handoff.

## Plugin

`plugin/dev-brain/index.ts` uses only `@opencode/plugin` and Node built-ins:

- `session.hook("context")` appends `.dev-brain/STATE.md` to the system context of every model call in the main session. Subagent sessions (reviewer, explore, general) do not get it: they work from the prompt their caller writes. The injection is transient, so it survives compaction.
- Budget: a state over 3000 characters is not injected; a one-line notice tells the model to read it when needed and to suggest `/handoff` to compact it. It is not truncated, because truncation would drop the `Next` section at the end.
- If the repository has no state file, it adds one line suggesting `/start`; it never creates the file by itself.
- `session.hook("compaction")` asks the summary to preserve goal, evidence, blockers and next action.

## Evaluation

`evals/offline/check.py` installs the kit into a temporary configuration, replaces the model with a local mock that records every request, and checks in about five seconds, at zero token cost, what the kit controls: state injection scope and budget, and the reviewer's read-only git permissions. Run it after changing the plugin, agents or installer:

```bash
python3 evals/offline/check.py          # set OPENCODE=<binary> if opencode is not on PATH
```

`evals/scenarios/` describes realistic tasks and the expected behavior. `evals/results.md` records the measured results and limitations. Every change to rules, commands or skills should be justified by a scenario; instructions that do not change behavior are removed.

The maintainability scenario found an improvement in **review policy**: it now reports duplicated business knowledge as a maintenance problem without merging unrelated policies. Generated code was already readable in the baseline and remained so afterward; that run does not demonstrate a generation-quality gain. The new fixture is Python-only: language-independent rules do not mean cross-language results have been verified. The `/review` delegation path is verified through the server API with a mock model, not through the TUI or a real model.

Run a scenario manually in a fixture:

```bash
# Only after explicitly authorizing local fixture commits:
./evals/setup.sh          # copies fixtures to /tmp/opencode/dev-brain-evals and recreates git history
cd /tmp/opencode/dev-brain-evals/bugfix
opencode run --standalone -m <provider/model> "The discount test fails. Fix the code."
```

For commands, use the TUI or the server command API; `opencode run` sends slash commands as literal text. In scripts, close stdin (`< /dev/null`): `opencode run` reads non-terminal stdin and waits for EOF.

`evals/setup.sh` replaces its disposable output directory and creates commits in the history-based fixtures. The maintainability scenario can instead run on fresh copies without git history or commits; see [`evals/scenarios/maintainability.md`](evals/scenarios/maintainability.md).

## Migration from the previous kit

The previous visible `dev-brain/` folder has been removed. Its content remains in git history at commit `08baebc`; inspect it with `git show 08baebc:dev-brain/RULES.md` or extract it with `git archive 08baebc dev-brain | tar -x -C /tmp`.

For each repository that received a copy:

1. Diff its `RULES.md` against `global/AGENTS.md` and keep any project-specific or genuinely useful rule.
2. Move stable project facts into the root `AGENTS.md`.
3. Convert `NOW.md`, `PROJECT_STATE.md` and `PROJECT_MAP.md` into `.dev-brain/STATE.md` plus the project `AGENTS.md`.
4. Remove the copied kit files.

## Layout

```
global/       always-loaded rules, commands, agents, skills
plugin/       OpenCode V2 plugin
templates/    STATE.md and project AGENTS.md templates
evals/        scenarios, fixtures, results, offline mock check
MANUALE.md    Italian user manual
```
