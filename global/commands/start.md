---
description: Adopt this repository into dev-brain (project facts + state)
---

Adopt the current repository into the dev-brain harness. This is an inspection and documentation task: do not modify application code, dependencies, configuration or git history.

Repository snapshot:
!`git status --short --branch 2>/dev/null || echo "not a git repository"`
!`ls -la`

Steps:

1. Inspect the actual repository: purpose, languages and declared versions, frameworks, package manager, entry points, build/lint/test commands, configuration, and the conventions the code really follows. Use the files, not assumptions.
   Never open or list directories or files that may contain personal, clinical or secret data (for example `input/`, `output/`, `.env`). Rely on documentation and configuration, and never copy such data into `AGENTS.md` or `.dev-brain/STATE.md`.
2. If a root `AGENTS.md` exists, merge into it and preserve every existing instruction. Otherwise create it. Keep it under 60 lines and include only:
   - one line of purpose;
   - stack and versions;
   - exact commands with their working directory and relevant side effects;
   - non-obvious architecture or conventions;
   - gotchas and known limitations.
   Do not add generic engineering advice; it is already in the global rules. Do not record absolute machine paths or values that only hold on this machine.
3. If `.dev-brain/STATE.md` exists, reconcile it with the current source instead of overwriting user notes. Otherwise create it using this structure:

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

4. Report separately: observed facts, unknowns, and any evidenced problem worth fixing. Do not fix anything.

Limits: do not install dependencies, run applications, migrations or external services, or start long builds. A command that only reads (`--version`, `--help`, a configured linter with no writes) is acceptable when safe.
