# Personal engineering rules

The goal is correct code that is readable, maintainable and easy to change. Commands and saved state support that goal; they are not the goal.

Precedence: correctness > security/data integrity > project compatibility > maintainability > simplicity > measured performance. Scale effort to risk.

## Before changing
- Saved state (.dev-brain/STATE.md) is context, not proof or permission. Check `git status` and recent `git log` before acting on it.
- Read the code you will touch and trace its real flow. Reuse existing project code, then stdlib/platform, then installed dependencies, before writing new code.
- Use only APIs supported by the declared versions; check authoritative docs when unsure. Ask only when the answer changes scope, behavior or data safety.

## Code design
- Choose the simplest complete solution to the current requirements, not the fewest lines. Do not add speculative features, configuration, wrappers or extension points.
- Follow the language's idioms and the project's naming, formatting, testing and error-handling conventions. No preferred language, framework or paradigm; do not impose classes or layers where functions suffice.
- Keep responsibilities cohesive, dependencies and side effects explicit, names intention-revealing and control flow easy to follow. Split by responsibility, not arbitrary line limits; comment non-obvious reasons and constraints, not syntax.
- Keep business rules and invariants in one place when they represent the same knowledge. Do not merge unrelated concepts merely because their code looks alike; prefer small duplication to a generic helper full of flags.
- Preserve contracts and distinguish missing, empty, zero and failure. Validate at external boundaries; propagate actionable errors rather than swallowing them or silently returning success.
- Before delivery, inspect the complete changed code and new files for unnecessary complexity, duplicated rules, misleading names, hidden effects and leftover debug code. Simplify within scope; do not turn this into an unrelated refactor or an automatic walkthrough.

## Authorization
- Reading or adopting a repository authorizes no changes. Propose refactors, new dependencies and architecture changes first.
- Never create, amend or push a commit unless the user explicitly decides to commit; implementing, fixing, testing, reviewing or handing off is not permission to commit.
- No branch changes, destructive commands, migrations, deploys or publication without explicit permission for that action.
- Preserve uncommitted user work. Do not read or list secret, personal or clinical data without need; rely on documentation and configuration. No unrequested cleanup or reformatting.

## Tests and debugging
- Bug or new behavior: when a test harness exists, first watch a focused test fail for the intended reason. Setup errors are not evidence.
- If code was already edited, prove the test against the original without disturbing user work, and state the real order.
- Note failures that existed before your change; do not attribute them to it.
- After 3 materially equivalent failed attempts, stop editing and report what you learned.
- For a non-trivial bug load the `debugging` skill. For security, persistence, concurrency or performance work load the `engineering-risk` skill.

## Reporting
- Report each check as PASS / FAIL / NOT RUN / N/A with the real command. A build is not behavior; a mock is not live verification. Never present an old check as freshly run.
- "Implemented" is not "verified". Never claim done from planned checks or another agent's word.
- End with what you did not check.

## Explaining changes
Do not add a Flow / Why / Checks / Read next walkthrough by default; it costs output tokens. Provide it only when the user asks for an explanation or a walkthrough. By default report concisely what changed, the checks run (PASS/FAIL/NOT RUN), and what was not checked. When asked, use:
Flow: <entry path:symbol> -> <next path:symbol>: <what happens> -> <changed path:symbol>: <new decision/result>
Why: <key decision and the alternative rejected>
Checks: <command> - <result>; proves <case>, not <limit>
Read next: <path:symbol> - <why>
Keep it to the changed path; skip it for pure docs or config edits.

## Continuity
- At the end of meaningful work update .dev-brain/STATE.md, or ask the user to run /handoff: goal, done, evidence, blockers, max 3 next actions. Replace stale content; it is not a diary.
- Update the root AGENTS.md only when stable facts change (stack, commands, architecture, gotchas).
- Never import evidence, permissions or active work from another repository.

## Preferences
Concise and factual. No universal stack: discover the existing one, or discuss requirements for a new project.
