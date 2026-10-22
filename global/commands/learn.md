---
description: Explain a flow, component or unfamiliar stack using the real code
---

Explain this for me: $ARGUMENTS

If the argument is empty, explain the main request flow of this project.

Read-only. Inspect the actual source before writing anything. Do not produce a generic tutorial.

Proceed in layers:

1. Scope: what the area is responsible for, and what it is not.
2. Inventory: the real files and symbols involved.
3. Connections: follow imports, calls and data from the entry point to the output. Do not trust dependency declarations or naming alone.
4. One concrete flow: trace a real request, command or event step by step.
5. Reading order: the shortest path for me to understand it myself.

For each connection use the format:
Flow: <entry path:symbol> -> <next path:symbol>: <what happens and what data moves> -> <output path:symbol>: <result>

For an unfamiliar stack, separate language concepts from framework concepts and explain each only where it appears in this project.

Label statements OBSERVED, INFERRED or UNKNOWN. End with the parts you did not verify.
