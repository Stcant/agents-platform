# Scenario: explain a real code flow

Fixture: `evals/fixtures/explain` (three Python modules, no dependencies)

Prompt:

> /dev-brain:learn how an order is created

Expected behavior:

1. Follows the real call chain `app.py -> service.py -> store.py`.
2. Uses actual file and symbol names.
3. Labels statements OBSERVED / INFERRED / UNKNOWN, or separates verified facts from guesses.
4. Gives a reading order.
5. Does not invent layers, frameworks or connections that are not in the code.

Failure signals:

- Generic tutorial about architecture.
- Mentions files or symbols that do not exist.
- Claims runtime behavior that was not inspected.
