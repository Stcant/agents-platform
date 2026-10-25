# Data, state and concurrency reference

## Ownership and invariants

- Who owns this state, and which invariants must always hold?
- Is the mutable state shared? If yes, what protects each invariant under concurrent access?
- Is a check-then-write sequence assumed atomic? Use a transaction, constraint or synchronization instead.

## Transactions and partial failure

- Does the operation span multiple writes? Can it leave a partial result when one step fails?
- Is the transaction boundary where the invariant is, not where the function boundary is?
- Are resources released on every path, including errors and cancellation?

## Idempotency and repetition

- Can this operation be retried or delivered twice? What happens then?
- Are retries bounded and applied only to transient failures? Is fallback behavior hiding a defect?
- Are external calls given timeouts and cancellation?

## Schema and stored data

- Is the migration backward compatible with data already stored and code still running?
- Are new constraints satisfiable by existing rows? Is required data backfilled, and in which order?
- Is a destructive change explicitly authorized, with a recovery strategy?
- Does the change alter a serialized format or public contract? Name the consumers and the migration.
