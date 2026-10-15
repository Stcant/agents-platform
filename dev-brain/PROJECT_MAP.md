# Project map — agents-platform

## Purpose and scope

Source of a standalone dev-brain folder copied into independent repositories. OpenCode-only, instruction-based, without runtime dependencies or automatic optimization.

## Stack and structure

- Markdown documentation; no application framework, package manager or executable test suite configured in this source kit.
- Root AGENTS.md directs the agent to the kit. README.md explains adoption and daily use.
- RULES.md defines proportional engineering, stack adaptation, existing-project assessment and evidence requirements.
- NOW.md summarizes current work; PROJECT_STATE.md holds details; this map holds stable knowledge; me.md holds personal preferences.
- `src/.gitkeep` is a pre-existing placeholder, not an imposed layout for destination projects.

## Working flow

Project request → applicable instructions → rules and current context → source inspection → scoped implementation when authorized → actual checks → updated handoff.

On adoption, inspect the destination and reconcile copied context before treating it as project truth. Existing code is mapped and assessed, not rewritten automatically.

## Conventions and commands

- Kit content is English. Programming languages and frameworks are chosen by each destination project.
- No universal build/test commands exist. Discover and record destination commands from its configuration, noting working directory and side effects.
- Source documentation whitespace check: `git diff --check` (does not validate agent behavior or untracked files).
- No application, database or external-service flow exists in this source kit.

## Reading order

NOW.md → PROJECT_STATE.md → relevant RULES.md sections → actual files affected by the task. Use README.md for initial adoption.

## Coverage and limits

This map describes inspected source documents, not demonstrated behavior in a destination application. Native client discovery and fresh-project adoption have not been tested in this update.
