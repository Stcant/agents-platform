---
name: start
description: Adopt the current repository into dev-brain by writing its commands, tooling and gotchas (AGENTS.md) and its saved state (.dev-brain/STATE.md). Run only when the user asks for it.
disable-model-invocation: true
---

Adopt the current repository into the dev-brain harness. This is an inspection and documentation task: do not modify application code, dependencies, configuration or git history.

Steps:

1. Run `git status --short --branch` and list the repository root. Inspect the actual repository: languages and declared versions, frameworks, package manager, entry points, build/lint/test commands, configuration, and the conventions the code really follows. Use the files, not assumptions.
   Never open or list directories or files that may contain personal, clinical or secret data (for example `input/`, `output/`, `.env`). Rely on documentation and configuration, and never copy such data into `AGENTS.md` or `.dev-brain/STATE.md`.
2. Files from the previous kit (`harness/PROJECT_STATE.md`, `harness/PROJECT_MAP.md`, `NOW.md`, a copied `dev-brain/` or `RULES.md`) are input, not a second source of truth. Carry still-true commands, tooling and gotchas into `AGENTS.md`, and only the current goal, latest evidence, blockers and next action into `.dev-brain/STATE.md`; leave history in git. Do not delete the old files: list them for the user.
3. Write the root `AGENTS.md` as a draft for the user to edit. Keep it under 40 lines and include only what the code does not tell the agent:
   - exact commands with their working directory and side effects: install, run one test, run all tests, lint, typecheck, build;
   - project tooling the agent must use instead of its defaults;
   - decisions and conventions that differ from the language or tool defaults;
   - gotchas: misleading or legacy code not to copy, directories that look unused but are live, required environment.
   Do not write a purpose line, a stack or dependency list, a directory tour or an architecture overview: the agent reads them from the code, and they add cost without helping it find files. Do not add generic engineering advice; it is already in the global rules. Do not record absolute machine paths or values that only hold on this machine.
   If a root `AGENTS.md` already exists, merge into it and preserve every existing instruction. List in the report the lines that only restate what the code shows, as candidates for the user to delete; do not delete them.
4. If `.dev-brain/STATE.md` exists, reconcile it with the current source instead of overwriting user notes. Otherwise create it using this structure. Keep it under 3000 characters: it is injected into the agent's context and larger files are skipped.

```markdown
# State — <project>
Updated: <date> · Branch: <branch>

## Goal
<one line> — acceptance: <observable criteria>

## Done (latest first, max 5)
- <outcome> — evidence: <command> PASS|FAIL|NOT RUN

## In progress / blockers
- <item> — status: implemented|verified|blocked — <why>

## Known pre-existing failures
- <command> — <failure> — since <date>

## Next (max 3)
1. <executable action>
```

5. Report separately: observed facts, unknowns, legacy files to delete, `AGENTS.md` lines proposed for deletion, and any evidenced problem worth fixing. Do not fix anything.
   If the root listing shows names that suggest secret or personal data (`.env*`, `input/`, `output/`, `data/`, exports), also give the permission deny rules the user can add themselves, for example `Read(./.env)` and `Read(./input/**)`, without opening those paths and without editing any settings file. State the limit: a deny rule stops Claude's file tools and common read commands, not a script that opens the file; `/sandbox` covers that.
   If the commands include a fast check (typecheck, lint or a quick test target), also give the user this Stop hook for their project settings, with the real command in place of `<check>`, so a turn cannot end until the check passes: `{"hooks":{"Stop":[{"hooks":[{"type":"command","command":"<check> 1>&2 || exit 2"}]}]}}`. Say it must stay fast: a slow check delays every turn, and Claude Code ends the turn anyway after 8 blocks in a row.

Limits: do not install dependencies, run applications, migrations or external services, or start long builds. A command that only reads (`--version`, `--help`, a configured linter with no writes) is acceptable when safe.
