---
description: Review correctness and maintainability of the current diff (read-only subagent)
---

Review the current changes by delegating to the read-only `reviewer` subagent with the `subagent` tool.

Scope requested by the user: $ARGUMENTS

Diff to review:
!`git status --short --branch && git diff --stat && git diff`

Untracked files (not in the diff; names only):
!`git ls-files --others --exclude-standard`

Steps:

1. Call the `subagent` tool once with agent `reviewer`. Put the scope and the full diff from above in the prompt, and instruct it to follow its own rules: report correctness, security and data-integrity defects separately from concrete maintenance problems, with file:line, trigger or maintenance scenario, impact and smallest fix. Exclude subjective style and speculative redesigns. If untracked files are in scope, tell it to read them directly.
2. Relay the reviewer's findings faithfully. Do not add findings of your own in this step and do not soften them.
3. If the diff is empty, say so and stop.

Do not modify files, run commands beyond the diff already captured, or commit.
