# Evaluation results

Fixtures are copied to `/tmp/opencode/dev-brain-evals` by `evals/setup.sh`, which recreates their git history; the source fixtures in this repository contain no `.git` directory.

Environment: OpenCode v2.1.3, model `opencode/deepseek-v4.1-flash-free`, 2026-10-22.
Baseline = same model, `XDG_CONFIG_HOME` pointing to an empty directory (no rules, skills, commands or plugin), `opencode run --standalone`.

## Bugfix with regression evidence

Prompt: "The discount test fails. Fix the code."

| | Baseline | dev-brain |
| --- | --- | --- |
| Order of work | Edited `discount.py` first, then ran the suite | Ran `python3 -m unittest -v` first, observed FAILED, then edited |
| Root cause | Correct one-line sign fix | Correct one-line sign fix |
| Verification | `python3 -m unittest -v` PASS after the change | PASS after the change; FAIL before is recorded in the answer |
| Session state | Untouched | Read and updated `.dev-brain/STATE.md` |
| Explanation | Short summary | Flow / Why / Checks / Read next, including what was not tested |
| Unrequested work | None | None |

Result: dev-brain improves the evidence trail (test-first, explicit before/after, state handoff) without adding scope. Baseline already solved the task.

Rule change after this run (2026-10-22): the Flow / Why / Checks / Read next walkthrough is now produced only when the user asks. The "Explanation" column above describes the old behavior; the default output is now a concise report of what changed, the checks run and what was not checked. No new scenario run was performed.

## Resume with stale state

Prompt: baseline "Resume work in this repository. Recap where we left off and what to do next."; dev-brain `/resume`.

| | Baseline | dev-brain |
| --- | --- | --- |
| Finds the state | Yes, after listing the directory | Injected into context by the plugin; command reads it |
| Detects divergence | Yes: `subtract` already implemented, state stale | Yes: same conclusion |
| Old evidence | Mentions the saved PASS | Runs a fresh suite and says it is a new result |
| Edits | Asks before updating state | Asks before updating state |

Result: both correct on this fixture. dev-brain makes the state visible without discovery and is stricter about evidence freshness. The fixture is too easy to separate the two strongly.

## Explain a real code flow

Prompt: baseline "Explain how an order is created in this codebase."; dev-brain `/learn how an order is created`.

| | Baseline | dev-brain |
| --- | --- | --- |
| Call chain | Correct: `app.py -> service.py -> store.py` | Correct, same chain |
| Real symbols | Yes | Yes |
| Evidence labels | No | OBSERVED / INFERRED / UNKNOWN |
| Runtime check | No | Ran `python3 app.py 42 12.5` and used the real output |
| Reading order | Implicit | Explicit, four entries |
| Limits | Some | Explicit "Not verified" section |

Result: both accurate; dev-brain adds labels, a reading order and a runtime check. Longer answer.

## Handoff

Prompt: `/handoff` with an uncommitted fix and no checks run in that session.

- The agent inspected the diff, ran `python3 -m unittest -v` itself, and recorded the fresh PASS with the command.
- It marked the change "verified locally, not committed", kept the next actions at two, removed the obsolete failure entry.
- No commit and no application edit beyond the existing fix.

Result: PASS.

## Review

- Direct `--agent reviewer`: shell is denied, edit is denied; the agent says it cannot run `git status` and does not guess. Permissions work.
- Orchestrated review through the `subagent` tool: the reviewer returned no correctness findings for the one-line fix, correctly noted that the second test does not guard the defect, and reported the suite as NOT RUN (no shell). Honest and read-only.
- First command version used `subagent: true` in frontmatter. In a session created without an active model the command switched nothing and produced no run. Changed to a normal command that instructs the main agent to call the `subagent` tool with agent `reviewer`.

## Adoption

`/start` was exercised on an unadopted fixture with `--auto` (the command itself was read and followed; the API-invoked command stopped at the write permission prompt, as expected without a user to approve). Result:

- root `AGENTS.md`: 27 lines with stack, layout, commands, conventions and gotchas, no generic advice;
- `.dev-brain/STATE.md`: goal, evidence, blockers and three next actions;
- no code, configuration or git changes;
- packaging and test-harness gaps reported as problems, not fixed.

One imperfection: the generated `AGENTS.md` contains an absolute repository path. The command now forbids absolute machine paths.

## Real repository: docling-parser (clinical data)

`/start` was run on `/home/stefano/codici/docling-parser` with explicit constraints: no access to `input/` or `output/` content, no conversions, no changes to the uncommitted Docling upgrade or the old `harness/` files.

- Created a 35-line root `AGENTS.md` and a `.dev-brain/STATE.md`; `git status` showed only those additions beyond the pre-existing changes.
- Fresh checks: `uv lock --check` PASS; `uv run --frozen python -m py_compile main.py` PASS; `uv run --frozen python main.py --help` PASS; Docling 2.138.0, pypdfium2 5.9.0.
- Plugin injection: a plan session reproduced the goal and first next action from the new state.
- `/resume` through the API expanded correctly. With an explicit model, it reconciled the state with git, re-ran `uv lock --check` and `--help`, and found README drift (Docling `>=2.100` vs `>=2.129.0`; page furniture described at the end vs interleaved) plus an output inventory mismatch (4 `.md` + 1 `.json` vs the recorded three-file sample).
- Privacy defect: during `/resume` the agent listed `input/` and `output/` filenames. The guard allowed "names/config only"; filenames can be identifying. The rule now forbids opening or listing those directories, and the project `AGENTS.md` was corrected.
- API-created sessions need an explicit `agent` and `model`; without them the command expands but no model call runs. This is a client-session issue, not a command-registration defect.

Result: adoption and injection PASS; privacy guard tightened after an observed failure.

## Command expansion

- `GET /api/command` lists all seven commands with descriptions.
- Invoking `plan` through the session command API produced the expanded prompt ("Plan this work: add a multiply function") and switched the session to the `plan` agent. Expansion works.
- `opencode run "/resume"` does not expand slash commands: the model receives the literal text and has to find the command file. This is a CLI-path limitation, not a registration problem. Use the TUI for commands.

## Limitations

- No automated TUI interaction; command behavior was verified through the server API and the CLI.
- One model and one run per scenario; small synthetic fixtures.
- The baseline is a no-harness configuration, not the previous dev-brain version. A comparison against the old kit still needs a separate run.
- The on-request walkthrough rule changed after the bugfix run; its effect on default output length has not been re-measured.

## Test on a docling-parser copy (2026-10-22, model `github-copilot/claude-haiku-5.5`)

Setup: a disposable copy under `/tmp/opencode/docling-test`, made with `rsync` excluding `input/`, `output/` and `.venv/`. It keeps git history, the uncommitted Docling changes and the dev-brain files. The real repository was not modified and no clinical data was copied.

Finding 1 — the running server caches command templates. Edits to `global/commands/*.md` did not reach expansions made through the running server (the expanded `/review` message lacked the new section). Tests through the server therefore used the old text. `opencode run --standalone` (private server, fresh files) used the new text. Restart the background server after editing commands when no session is active.

Finding 2 — `/resume` ran `uv run --frozen python main.py --help`, which created a 3.5 GB `.venv` in the tmpfs `/tmp` and failed with `No space left on device`.
- Original template, through the server: FAIL — `.venv` created.
- Fix attempt 1 (generic "never create environments"), through the server, old template still served: FAIL — `.venv` created again.
- Fix attempt 2 (precondition: `test -d .venv` before `uv run`), `--standalone`, new template: PASS — `.venv` absent after the run; `--help` reported NOT RUN. Side effect: `uv lock --check`, which is read-only, was also skipped, so the rule is stricter than needed.
- The rule depends on model compliance; the harness does not enforce it.

Finding 3 — `/review` did not include untracked files; the baseline reviewer stated that `.dev-brain/`, `AGENTS.md` and `harness/` were not reviewed.
- Fix: `git ls-files --others --exclude-standard` (names only; ignored `input/` and `output/` excluded) added to the command, and the reviewer is told to read untracked files in scope.
- Result (`--standalone`, new template): PASS — untracked files listed and reviewed for secrets and paths without opening `input/` or `output/`; no confirmed defect. The reviewer raised a suspicion about the `main.py` Docling API calls against 2.138, outside the diff; it is not verified.

NOT RUN in this test: `uv lock --check`, `py_compile`, `--help` (no environment), sample conversions, the `/resume` privacy guard against real `output/` content (the copy has no `output/`), `/handoff`, and the TUI itself.

## Readability and maintainability as the primary goal (2026-10-22)

The user clarified that readable, maintainable code is the purpose of dev-brain, across languages; workflow and session state are supporting tools. Inspection of `08baebc:dev-brain/RULES.md` showed that the global-rule reduction had dropped its explicit design criteria. The reviewer also explicitly excluded maintenance-only findings.

Changes: restored a compact, language-independent `Code design` section in `global/AGENTS.md`; broadened the reviewer and `/review` prompt to distinguish concrete maintenance problems from present behavior defects. This restores the user's requirements; the experiment below does not establish a benefit for every individual design instruction.

Scenario: `evals/scenarios/maintainability.md`, with its stdlib-only fixture. A duplicated shipping rule represents shared business knowledge; two identical label functions have independent owners and must not be merged just for DRY. Generation adds express shipping while preserving standard shipping, public callers and output keys. Review receives the original fixture as a new-file diff.

Environment: OpenCode v2.1.3, `github-copilot/claude-haiku-5.5`, four fresh `--standalone` runs (generation and review policy before/after), no delegation, no commits. Baseline means the current kit before this change, not no harness. Disposable copies and raw JSONL transcripts: `/tmp/opencode/dev-brain-quality-4mfgq_ok/`; policies were snapshotted before each phase. Those local artifacts are temporary, not a permanent archive.

Commands (from the matching fresh copy):

```bash
opencode run --standalone --agent build --model github-copilot/claude-haiku-5.5 --format json "$(cat ../generation-prompt.txt)"
opencode run --standalone --agent build --model github-copilot/claude-haiku-5.5 --format json "$(cat ../baseline-review-prompt.txt)"
opencode run --standalone --agent build --model github-copilot/claude-haiku-5.5 --format json "$(cat ../updated-review-prompt.txt)"
python3 -B -m unittest -v
```

The generation prompt was identical before/after. For policy evaluation the reviewer body was supplied to `build` with the same diff and request; only the supplied policy and installed global rules changed. This avoids delegation and does **not** test the actual `/review` command or reviewer permissions. The final wording of the finding-format bullet was then clarified from "trigger" to "trigger or maintenance scenario"; no model rerun was made for that editorial clarification.

| Check | Before | After |
| --- | --- | --- |
| Generation: suite independently rerun with `python3 -B -m unittest -v` | PASS, 4 tests | PASS, 4 tests |
| New tests on original source | Expected FAIL: missing `express` argument | Expected FAIL: missing `express` argument |
| Order observed in tool transcript | Tests fail before implementation | Tests fail before implementation |
| Shipping rule | One helper shared by both entry points | One helper shared by both entry points |
| Unrelated label policies | Unchanged and separate | Unchanged and separate |
| Speculative architecture/dependencies | None | None |
| Policy review: duplicated business rule | Excluded because no behavior changes today | Reported separately as a maintenance problem, with a shared helper as the smallest remedy |
| Policy review: similar but unrelated labels | No finding | Explicitly rejects merging them |

The baseline reviewer said: "I excluded the duplicated shipping rule [...] because neither changes behavior now." The updated policy identified changing the shipping threshold/fee as the maintenance scenario requiring edits in two locations. That is the observed improvement. The updated response also raised conditional input-validation questions; these are not confirmed defects, because no external-input contract was supplied.

Additional local `python3 -B` assertions independently checked eight `(subtotal, express)` combinations per implementation, unchanged label ASTs, one threshold decision and no added imports/classes: PASS for both. Generated tests were replayed against separate copies of the original source: both failed for the intended missing argument, not an import/setup error. JSONL inspection found no error events or delegation; the review-policy runs used no tools.

Fixture check: `python3 -B -m unittest discover -s evals/fixtures/maintainability -v` PASS (2 original tests). The fixture deliberately retains the duplicated rule for the review scenario; it is not the generated implementation.

Conclusion: the review policy now covers an observed gap in maintenance review. Generated code was already simple and readable in the baseline, so this run shows no generation-quality gain. One model, one run per task/version, Python only: no general quality claim or cross-language behavior claim. Instructions express a language-independent requirement, not a guarantee.

Final static checks: `git diff --check` PASS; `bash -n evals/setup.sh` PASS; per-file `git diff --no-index --check -- /dev/null <changed-file>` PASS for all 12 changed/new paths (exit 1 for a differing new file is not a whitespace failure). A local `python3 -B` check also verified balanced Markdown fences, Python AST parsing, no machine paths in the edited global definitions, installed symlinks to the edited rules/reviewer/command, and instruction/state line budgets: PASS. The initial checker incorrectly required exit 0 from `--no-index`; it was corrected and rerun, with no source whitespace defect found.

NOT RUN: the updated `/review` delegation/TUI path, scenarios in other languages, the full historical scenario set, or `evals/setup.sh` (it creates fixture commits; no commit was authorized). No docling work or service restart was performed.
