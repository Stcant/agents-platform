# Agent Instructions

Read [coding-harness/SKILL.md](coding-harness/SKILL.md) before changing this repository. Load only relevant references.

## Repository Maintenance with Superpowers

Superpowers is installed as the pinned Git submodule at `vendor/superpowers`. Before maintaining this source, read `vendor/superpowers/skills/using-superpowers/SKILL.md`, then load only the skills relevant to the work:

| Work | Read under vendor/superpowers/skills/ |
| --- | --- |
| Change agent instructions or templates | writing-skills/SKILL.md and its testing-skills-with-subagents.md reference |
| Diagnose a demonstrated failure | systematic-debugging/SKILL.md |
| Change executable behavior or tests | test-driven-development/SKILL.md and its writing-good-tests.md reference |
| Report completion or save changes | verification-before-completion/SKILL.md |

If the submodule is unavailable, use the initialization procedure in README.md. If initialization cannot run, report that limit; do not claim Superpowers was used. This is a source installation with file-based loading, not registration of a client plugin. Use the native skill tool when available; otherwise read the referenced files directly.

Project instructions and the user's established authorization take precedence over upstream defaults. Preserve this repository's minimal kit, current branch, and instruction-only package. Do not introduce automatic worktrees, commits, plan files, services, hooks, or global installations. Never edit the upstream submodule to customize coding-harness.

### Evaluate Instruction Changes

Use Superpowers' writing-skills method for behavioral changes:

1. Define an observable task and pass/fail criteria before editing. Run a fresh-context baseline using the current source; for new guidance, also use a control without that guidance. Capture actual failures and explanations. When the control succeeds, retain the behavior instead of adding a speculative rule.
2. Make the smallest change addressing an observed gap. Keep reusable guidance in coding-harness/ and maintenance dependencies/evidence outside it.
3. Run the same task in a fresh context against the candidate, with isolated disposable project files. Give the agent the skill source and normal task request, without the expected output or diagnosis. Use subagents when available; disclose when independent testing cannot run.
4. Inspect actual files, diffs, check output, and side effects independently. Include a related regression scenario for the changed boundary. Keep targeted checks distinct from suite/integration results; an agent's completion message alone is insufficient.
5. Check source links, frontmatter/metadata, template validity, and the complete package inventory. Preserve the ten-file reusable package and two-document default; portable mode copies the package, not vendor/ or source-maintenance files.

Before saving, record scenario inputs, baseline/candidate outcomes, observed evidence, and limitations in REPOSITORY_STATE.md. Keep it compact; Git retains previous versions. Skill-behavior checks establish behavior in fixtures, not verification of a user's application or automatic client discovery.

For maintenance of this skill source, resume from [REPOSITORY_STATE.md](REPOSITORY_STATE.md). Never copy its completed work or verification into target projects.

Preserve user changes and the current branch. No Git writes, branch changes, destructive actions, or publication without specific applicable authorization. Do not impose a project stack.
