---
name: review
description: Review correctness and maintainability of the current changes through the read-only reviewer subagent. Run only when the user asks for it.
disable-model-invocation: true
---

Review the current changes by delegating to the read-only `reviewer` subagent (`dev-brain:reviewer` in Claude Code).

Scope: the text the user gave with this request. If none, every uncommitted change: staged, unstaged and untracked files.

Steps:

1. Run `git status --short --branch` and `git diff HEAD --stat` (before the first commit: `git diff --cached --stat`). If the scope is empty and nothing is modified, staged or untracked, say so and stop.
2. Delegate once to the `reviewer` subagent. Give it the scope and the changed-file list. Do not paste the diff or file contents: the reviewer reads them itself with git and its read tool. Tell it to follow its own rules, keep behavior defects separate from maintenance problems, and state which files it actually read.
3. If no `reviewer` subagent is available, say so and stop; do not review the code yourself in this step.
4. Relay the reviewer's findings faithfully. Do not add findings of your own and do not soften them.

Do not modify files, run other commands or commit.
