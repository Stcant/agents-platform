---
name: engineering-risk
description: Use when a change touches authentication or authorization, user input, secrets, stored data, schema or migrations, concurrent or repeated operations, external services, or performance-sensitive paths.
---

# Engineering risk review

Load only the reference that matches the change:

- `references/security.md` — trust boundaries, access control, injection, secrets, uploads, outbound requests.
- `references/data.md` — ownership, transactions, idempotency, concurrency, migrations, destructive changes.
- `references/performance.md` — algorithms, query counts, I/O, memory growth, caching.

For each area, answer the concrete questions in the reference against the actual code. If the change does not touch an area, do not read it.

Report findings with: the risk, the concrete trigger, the impact, and the smallest remedy. Separate a real defect from a hardening suggestion. Never weaken validation, error handling or access checks to make a change smaller.
