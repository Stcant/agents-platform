# Scenario: readable code with one source of business knowledge

Fixture: `evals/fixtures/maintainability` (Python stdlib, no dependencies).
Use a fresh disposable copy for each run. No commits are needed.

## Generation

Prompt:

> Add express shipping to `checkout_total_cents` and `order_summary`. Add an optional `express=False` argument to both functions. Standard shipping stays unchanged: free from 5000 cents, otherwise 500 cents. Express shipping always costs 1200 cents, even above the free-shipping threshold. Preserve existing callers and output keys. Add regression tests using the existing test harness. Do not commit or delegate.

Check behavior separately from structure:

- Existing tests still pass; test standard and express shipping below, at and above the threshold.
- Both entry points use one shipping-fee decision rather than duplicating the business rule.
- Names explain the domain and cents remain explicit; control flow is readable.
- No shipping strategy registry, factory, new dependency or unrelated rewrite for two fixed choices.
- Do not merge `customer_label` and `warehouse_label` merely because their implementations look alike: their contracts have separate owners.
- New checks fail for the intended reason before implementation; no commits.

## Review policy

Submit the fixture as a new-file diff with this prompt, using the reviewer policy:

> Review this diff. The tests pass and no current behavior defect is known. Do not modify files, run commands or delegate. Report only findings allowed by the supplied review policy.

Expected with the updated policy:

- Report the duplicated shipping rule in `checkout_total_cents` and `order_summary` as a maintenance issue, not a present output bug. Explain that changing shipping policy requires editing both places; propose a shared fee calculation.
- Do not report a correctness failure without a trigger.
- Do not demand a generic label helper, stylistic renaming or a larger architecture.

Use identical prompts, model and fixture before/after. Inspect the generated diff and tool transcript, not only the final answer. Record which policy was actually supplied. A policy-only run is not a test of `/review` delegation, and one run cannot establish general code-quality improvement.
