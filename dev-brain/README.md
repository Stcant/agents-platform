# dev-brain

A personal, repository-local engineering kit for OpenCode: produce clean working code, understand the project and resume without reconstructing the last session. No runtime, hooks or global dashboard.

## Adopt in a new or existing repo

1. Copy the complete `dev-brain/` folder. Preserve any existing destination files; reconcile them instead of overwriting notes.
2. Merge the instructions from `dev-brain/AGENTS.md` into the destination's existing root instructions, or copy it if none exists. Do not replace unrelated instructions.
3. Ask OpenCode:

   > Read dev-brain/RULES.md. Adopt this kit for this repository. Inspect its actual code and configuration, identify any copied foreign context, and initialize NOW, state and map with this project's facts. Preserve existing notes. Identify stack, versions, conventions, code flow and verification commands. Report evidenced problems and useful improvements, but do not modify application code or install dependencies. Do not run applications, migrations or external services without authorization.

4. Review `dev-brain/NOW.md`. For a new empty project, leave architecture and stack undecided until requirements support a choice.

The context files here describe this source repo. They are not verified facts about your destination. Copying the kit does not automatically initialize it or authorize optimization.

## Daily use

- Open `dev-brain/NOW.md` for what was done and what comes next. Pin it in your editor if useful; this kit does not open it automatically at PC startup.
- Ask OpenCode to resume from the saved context and inspect current source before continuing.
- At handoff, ask it to update NOW and state with actual results, checks, blockers and the next step.
- Ask for an explanation of the real code flow whenever needed. The map provides stable entry points, not a substitute for reading current source.

## Files

| File | Responsibility |
| --- | --- |
| `dev-brain/AGENTS.md` | Project instructions to merge into the destination root entry point |
| `dev-brain/RULES.md` | Language-independent engineering principles and working method |
| `dev-brain/NOW.md` | Short visible summary: done, current focus, next actions |
| `dev-brain/PROJECT_STATE.md` | Resumable working detail and verification evidence |
| `dev-brain/PROJECT_MAP.md` | Purpose, stack, architecture, conventions, commands and reading order |
| `dev-brain/me.md` | Optional personal preferences, subordinate to project constraints |

Each repo stays independent. Framework-specific facts belong in its map, not in universal rules. Existing code is assessed before changes; justified improvements are proposed, not automatically applied.
