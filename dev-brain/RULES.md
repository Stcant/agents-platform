# Software engineering rules

## 1. Governing principle

Choose the simplest solution that fully meets the requirements and remains understandable, verifiable and changeable. Justify necessary complexity; reject speculative complexity. Minimum code is a consequence, not the goal.

Resolve trade-offs in this order: correctness, security and data integrity, project compatibility, maintainability, simplicity, then demonstrated performance needs. Apply the sections relevant to the task; a small edit does not require an architecture exercise.

## 2. Understand before changing

- Read applicable project instructions, this file, NOW.md and PROJECT_STATE.md; consult PROJECT_MAP.md and me.md for relevant context. Resolve these paths relative to dev-brain/.
- Inspect the actual source and working-tree changes. Preserve user work. Saved notes are context, not proof or permission.
- Identify the desired outcome, constraints, affected callers, consumers, tests, fixtures, configuration and public contracts.
- Trace the relevant flow from entry point through processing and storage to output. Search for existing solutions before adding anything.
- Separate observed facts, assumptions and unknowns. Ask about uncertainties that materially change scope, behavior or data safety; do not block clear work with unnecessary questions.
- Define observable acceptance criteria, failure cases, side effects, preconditions, postconditions and invariants before implementation.

## 3. Adapt to every language and framework

- Discover languages, supported versions, frameworks, package managers, build tools, formatters, linters and test tools from actual project files.
- Follow the idioms of each component. Do not write one language as though it were another or impose object orientation everywhere.
- Apply principles through the available mechanisms: functions, modules, structures, classes, protocols, types or runtime checks as appropriate.
- Respect framework lifecycle, routing, dependency management, persistence and error-handling conventions. Prefer established project patterns unless an observed defect justifies changing them.
- Use APIs and syntax supported by declared versions. Consult authoritative documentation when uncertain; do not invent APIs or commands.
- For mixed-language systems, respect local conventions and verify shared contracts. For new projects, propose stack choices from requirements rather than imposing a favorite stack.
- Record project-specific findings and real commands in PROJECT_MAP.md, not in reusable rules. Personal preferences never override correctness or project constraints.

## 4. Adopt existing projects without rewriting them

- On first adoption, inspect and map what already exists. Check whether copied context describes another repo; replace only identified template or foreign facts, preserving existing project notes and history.
- Identify purpose, stack, entry points, architecture, data flow, conventions, checks and current work. Mark unknowns explicitly; do not manufacture a previous session.
- Evaluate correctness, security, compatibility, maintainability and measured performance, not personal taste.
- Report findings with evidence, affected behavior, severity and the smallest useful remedy. Distinguish defects from optional improvements and explain what should remain unchanged.
- Copying the kit authorizes neither code changes nor optimization. Propose material refactors, dependency changes and architectural work before implementation. Apply small fixes only within an authorized coding task.
- Optimize when a requirement, measured bottleneck or concrete maintenance problem justifies it. No blanket cleanup, paradigm migration or rewrite.

## 5. KISS, YAGNI and reuse

- Solve the current problem completely; do not add unrequested features, options or future extension points.
- Prefer an appropriate existing project solution, then standard-library/platform capabilities, then suitable installed dependencies, before writing new machinery.
- Avoid wrappers, factories, plugins, configuration and layers without a concrete responsibility. A readable multi-line solution beats a clever one-liner.
- Do not trade required validation, accessibility, error handling or completeness for a smaller diff.
- Assess new dependencies for benefit, maintenance, compatibility, security and license obligations. Do not add one for trivial work or hand-roll complex security-sensitive functionality merely to avoid one.

## 6. Modular design and SOLID

- Keep related behavior cohesive and unrelated responsibilities separate. Hide implementation details and make dependencies explicit.
- Separate domain rules, transport, persistence and presentation where useful; do not require a layer or folder for every concept.
- Single responsibility: group behavior with coherent reasons to change, not one class per function.
- Open/closed: introduce extension points for real variability, not hypothetical futures.
- Liskov substitution: implementations preserve promised inputs, outputs, errors, invariants and side effects.
- Interface segregation: expose focused contracts that consumers actually need.
- Dependency inversion: protect important rules from volatile details where a real boundary warrants it; do not create an interface for every class.
- Favor composition over inheritance when it reduces coupling. Keep a conceptual change local where possible.

## 7. DRY and abstraction

- Avoid duplicating business knowledge and invariants. Similar-looking code is not necessarily the same concept.
- Accept small duplication rather than couple unrelated responsibilities through a generic helper full of flags.
- Extract an abstraction when a stable shared responsibility emerges. Name the concept it represents, not only the mechanism.
- Refactor when the abstraction clarifies current behavior; do not build an internal framework for a single case.

## 8. Programming paradigms

- Use procedural flows for straightforward sequences, objects for coherent state and invariants, and pure functions for deterministic transformations when appropriate.
- Use declarative facilities where they express intent clearly. Introduce event-driven, asynchronous or distributed designs only for justified requirements.
- Prefer explicit effects and limited shared mutable state; isolate I/O from calculations where useful without inventing unnecessary layers.
- Choose paradigms according to the problem and existing ecosystem, not ideology.

## 9. Contracts, types and data

- Make input, output, errors, ownership and side effects explicit. Use types to prevent invalid states where practical; validate external data at runtime regardless.
- Distinguish missing, empty, zero and failure. Avoid magic values and unnecessary conversions.
- Specify units, precision, rounding, encoding and time-zone semantics when relevant. Use appropriate representations for money and identifiers.
- Avoid hidden mutation and unclear aliases. Preserve public contracts or propose an explicit migration for consumers and stored data.

## 10. Errors and reliability

- Handle errors where a useful decision can be made. Do not swallow failures or return apparent success after failure.
- Preserve actionable causes without exposing sensitive details. Release resources using the language's supported lifecycle mechanisms.
- Consider cancellation, partial failure and external-operation timeouts where relevant.
- Retry only transient failures when repetition is safe; bound retries and avoid fallback behavior that silently masks defects.
- Do not add resilience infrastructure where simple error propagation is sufficient.

## 11. State, concurrency and persistence

- Identify who owns and mutates state. Consider concurrent access, duplicate requests and interrupted operations when applicable.
- Do not assume check-then-write is atomic. Use suitable transactions, constraints or synchronization to preserve invariants.
- Use idempotency where operations may be repeated. Consider migration compatibility and existing data.
- Propose destructive schema changes with explicit authorization and a recovery strategy. Do not introduce distributed machinery for a local problem.

## 12. Security and accessibility

- Validate at trust boundaries. Distinguish authentication from authorization and check access to the specific resource.
- Use parameterized queries, safe platform APIs and established cryptography. Apply least privilege.
- Consider context-specific injection, path traversal, unsafe uploads, rendering and remote-request risks.
- Do not inspect secret files without a necessary authorized purpose. Never place credentials or confidential content in code, logs, examples or session documents.
- Preserve accessibility and platform-specific safety requirements. Simplicity does not excuse removing protections.

## 13. Readability and conventions

- Follow project formatting, naming, module layout and tooling. Use intention-revealing names and explicit control flow.
- Keep functions and modules focused; avoid arbitrary line limits and forced fragmentation.
- Comment non-obvious reasons, constraints and trade-offs rather than narrating syntax. Keep comments accurate.
- Record a deliberate shortcut's limitation and revisit condition near the relevant code when useful.
- Do not mix unrelated stylistic cleanup into a task or reformat the repo to personal taste.

## 14. Tests and debugging

- Use the existing test system. Select checks according to changed behavior and risk, not a fixed test count.
- For a bug or new behavior, observe a focused regression/acceptance test fail for the intended reason before implementation when a suitable harness exists. Setup errors are not behavioral evidence.
- If code was already changed, safely demonstrate the regression against the original without disturbing user work and disclose the actual ordering.
- Assert observable outcomes, important side effects and relevant error/boundary cases. A test that passes on the original defect is not a useful regression.
- Keep tests deterministic and independent. Mock appropriate external boundaries, not the behavior being proved; use integration checks for interaction risks.
- Without a suitable harness, use a safe reproduction and disclose its limits rather than automatically adding a framework.
- Debug by reproducing, tracing the responsible boundary, testing a hypothesis and fixing the root cause. Avoid random edits and unnecessary rewrites.
- Refactoring preserves behavior. Separate it from functional changes when that improves review and verification.

## 15. Performance

- Consider algorithms, input size, query count, I/O and memory growth before micro-optimization.
- Measure suspected bottlenecks before introducing complex optimizations. Tie improvements to observable requirements or evidence.
- Avoid unbounded work, N+1 queries and needless repetition where relevant. Add caching only with a justified benefit and explicit invalidation behavior.

## 16. Verification and delivery

- Review acceptance criteria, the complete diff, new files and direct consumers. Verify functional requirements separately from structural quality.
- Run relevant configured tests, lint, type checks and builds when available and safe. Keep focused results distinct from the full suite.
- Report PASS, FAIL, NOT RUN or N/A with actual commands and limitations. A build is not proof of behavior; mocked integration is not live verification.
- Never claim success from planned checks or another agent's assertion alone. Identify which check would catch a wrong changed decision or missing side effect.
- Preserve the branch and user changes. No Git writes, destructive actions, publication or deployment without specific applicable authorization.
- Summarize the result, verification and unresolved risks concisely. Mention skipped work when material; do not add ritual disclaimers to every conversational reply.

## 17. Session continuity and understanding

- NOW.md is the visible summary: last useful verified outcome, current focus and at most three actionable next items. It links to detail instead of copying it.
- PROJECT_STATE.md holds resumable detail: goal, criteria, last step, actual evidence, relevant failed attempts, blockers and executable next action. Keep it compact, not a transcript or diary.
- PROJECT_MAP.md holds stable source-backed knowledge: purpose, stack/versions, components, contracts, data flow, conventions, real commands and reading order. Distinguish inspected structure from tested behavior.
- At meaningful handoffs or session end, reconcile NOW and state with actual work. Update the map when architecture, contracts, commands or important flows change.
- Explain changes through the actual code path, including responsibilities and why decisions were made. Do not assume that generating code means the user understands it.
- Every repo is independent. Copy no completion evidence, permissions or active work from another project. Do not create global dashboards, extra ledgers or automatic services.

## Sources

Simplicity and reuse guidance is informed by [Ponytail](https://github.com/DietrichGebert/ponytail). These rules are independently phrased; adopting this kit does not install Ponytail or its adapters.
