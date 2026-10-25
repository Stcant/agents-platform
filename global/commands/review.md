---
description: Review correctness and maintainability of the current changes (read-only subagent)
---

Review the current changes by delegating to the read-only `reviewer` subagent with the `subagent` tool.

Scope requested by the user: $ARGUMENTS
If empty, the scope is every uncommitted change: staged, unstaged and untracked files.

Changed files (names and counts only; the reviewer reads the content itself):
!`git status --short --branch`
!`git diff HEAD --stat 2>/dev/null || git diff --cached --stat`

Steps:

1. If the scope is empty and nothing above is modified, staged or untracked, say so and stop.
2. Call the `subagent` tool once with agent `reviewer`. Give it the scope and the changed-file list above. Do not paste the diff or file contents: the reviewer reads them with git and its read tool. Tell it to follow its own rules, keep behavior defects separate from maintenance problems, and state which files it actually read.
3. Relay the reviewer's findings faithfully. Do not add findings of your own in this step and do not soften them.

Do not modify files, run further commands or commit.
