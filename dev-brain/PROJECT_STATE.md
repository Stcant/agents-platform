# Project state — agents-platform

## Goal and scope

Maintain an English, standalone, OpenCode-only engineering kit copied into each independent repo. The owner needs working clean code, understanding of the code flow and a visible done/next summary. No global system or imposed stack.

## Current change

Expanded RULES.md with decision priorities, engineering principles, paradigms, language/framework adaptation, existing-project assessment, correctness, security, tests and continuity. Consolidated the kit files into `dev-brain/`, including instructions and adoption guide; removed the unsuitable `src/` placeholder. No application code changed.

## Acceptance criteria

- Rules cover the agreed engineering topics without imposing classes, frameworks or speculative architecture.
- The entire kit is contained in one `dev-brain/` folder and has no `src/` directory.
- Adoption rebuilds foreign context from actual source, preserves notes and does not authorize automatic code optimization.
- NOW is the short entry point; state is working detail; map contains stable project facts; preferences are not project configuration.
- Documentation remains English and local references resolve.

## Evidence and limitations

- PASS: Python documentation check read all seven Markdown files, verified final newlines, trailing whitespace, local Markdown link targets and the five-file dev-brain inventory.
- PASS: `git diff --check`. These are static integrity checks, not proof that an agent follows the rules.
- No executable application or configured test suite exists in this source kit.
- No fresh-context behavioral evaluation, native discovery check or destination-project verification has been performed for these revised rules.
- Prior uncommitted deletions from the agreed repository simplification remain preserved; no commit, branch change, deployment or publication is included.

## Relevant history

The earlier minimal rules overemphasized short diffs and a fixed small test count. This revision prioritizes correctness, readability and risk-based verification instead. Earlier source content remains in Git; current uncommitted work must also be preserved.

## Next action

Run documentation integrity checks, then test adoption on a disposable existing-project fixture without authorizing application edits. Inspect actual files and side effects before claiming the kit's behavior is verified.
