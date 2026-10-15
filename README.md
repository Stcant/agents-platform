# Coding Harness

A skill that guides an agent through maintainable software development: understanding the project, applying software engineering principles, implementing changes, verifying with evidence, and preserving continuity across sessions.

Follow the languages, frameworks, and tools already used by the project. The skill contains instructions, references, and templates; it requires no additional runtime, scripts, hooks, or dependencies.

## Choose Your Client

| Client | Personal installation, available across local projects | Invocation |
| --- | --- | --- |
| Codex CLI / IDE extension | `~/.agents/skills/coding-harness/` | `$coding-harness` or `/skills` |
| Claude Code | `~/.claude/skills/coding-harness/` | `/coding-harness` |
| Cursor | `~/.cursor/skills/coding-harness/` | Type `/` in Agent chat, then select the skill |
| ChatGPT with skill management | Create a personal skill through `@skill-creator` | Type `@` and select the skill |

Globally available means available across projects for that user on that machine. The agent may choose the skill when the request matches its description; invoke it explicitly at the start of a task to ensure it is used.

Local folders are not automatically installed in ChatGPT or cloud sessions. The [openai.yaml](coding-harness/agents/openai.yaml) metadata configures presentation and permits implicit invocation in clients that support it; it does not replace installation.

## Prepare the Source

The following commands use Bash on Linux, macOS, or WSL. Run installation and update commands from the source folder that contains `coding-harness/`. The folder can have any name and be located anywhere, including a path with spaces.

`repo_dir="$(pwd -P)"` resolves your current source folder. `$HOME` and `~` refer to the current user's home directory. These are portable variables and conventions, not links to a particular computer or user.

If you have already downloaded or cloned the repository, open a terminal in its source folder. Otherwise, replace `<repository-url>` with the URL of the source repository or your fork, then run:

```bash
git clone "<repository-url>" coding-harness-source
cd coding-harness-source
```

Always install the entire `coding-harness/` folder: copying only `SKILL.md` leaves references and templates unavailable. This repository contains the skill source and does not activate itself.

## Install for Your Client

These commands are for a first installation. If the destination already exists, follow [Updating](#updating) to preserve a backup.

### Codex CLI and IDE

```bash
(
  set -eu
  repo_dir="$(pwd -P)"
  skill_dir="$HOME/.agents/skills/coding-harness"
  test -f "$repo_dir/coding-harness/SKILL.md"
  test ! -e "$skill_dir"
  test ! -L "$skill_dir"
  mkdir -p "$skill_dir"
  cp -R "$repo_dir/coding-harness/." "$skill_dir/"
)
```

Open Codex in your project and enter:

```text
$coding-harness Implement this feature using the project's existing conventions.
```

Use `/skills` to find the skill. Codex detects skill changes; restart it if the skill does not appear.

### Claude Code

```bash
(
  set -eu
  repo_dir="$(pwd -P)"
  skill_dir="$HOME/.claude/skills/coding-harness"
  test -f "$repo_dir/coding-harness/SKILL.md"
  test ! -e "$skill_dir"
  test ! -L "$skill_dir"
  mkdir -p "$skill_dir"
  cp -R "$repo_dir/coding-harness/." "$skill_dir/"
)
```

Start Claude Code in your project and enter:

```text
/coding-harness Fix this bug and verify the behavior.
```

The personal folder makes the skill available across local projects. Open the `/` menu and search for `coding-harness` to check discovery.

### Cursor

```bash
(
  set -eu
  repo_dir="$(pwd -P)"
  skill_dir="$HOME/.cursor/skills/coding-harness"
  test -f "$repo_dir/coding-harness/SKILL.md"
  test ! -e "$skill_dir"
  test ! -L "$skill_dir"
  mkdir -p "$skill_dir"
  cp -R "$repo_dir/coding-harness/." "$skill_dir/"
)
```

Open **Customize → Skills**, then type `/` in Agent chat and select `coding-harness`. Reopen the client if it does not discover the skill after installation.

Cursor also reads `~/.agents/skills/` and directories compatible with other clients: if you already installed the skill for Codex, check whether it is available before creating another copy with the same name. For Cloud Agents, the documentation describes syncing skills from `~/.cursor/skills/` through **Settings → Agents → Sync Skills for Cloud Agents**; a local installation alone is not transferred to remote sessions.

### ChatGPT

When the client offers skill management and creation, invoke `@skill-creator` and ask:

> Create a personal skill named coding-harness from the coding-harness folder in the source repository or files I provide. Preserve its references, templates, instruction-only operation, and software engineering principles.

Make the source accessible to the creator through the connected GitHub integration or the folder's files. After the creator confirms saving, select the skill with `@`. To update it, ask the same creator to update the existing personal skill from the repository, preserving any declared customizations.

Having `~/.agents/skills/` on your computer does not install a skill in your ChatGPT account. This repository does not yet contain a plugin package that can be installed from the catalog.

## Updating

For a copied installation, open a terminal in the source folder, update the source, then replace the installed folder. This procedure preserves the previous version outside client discovery directories and prevents files removed from the source from remaining in the new copy.

Choose **one** destination for the client you want to update:

```bash
# Codex
skill_dir="$HOME/.agents/skills/coding-harness"

# Claude Code: use this line instead of the one above
# skill_dir="$HOME/.claude/skills/coding-harness"

# Cursor: use this line instead of the one above
# skill_dir="$HOME/.cursor/skills/coding-harness"
```

Then run:

```bash
(
  set -eu
  repo_dir="$(pwd -P)"
  branch_name="$(git -C "$repo_dir" branch --show-current)"
  if [ -z "$branch_name" ]; then
    echo "The source has a detached HEAD: select the intended branch before updating."
    exit 1
  fi
  git -C "$repo_dir" rev-parse --verify '@{upstream}' >/dev/null
  if [ -n "$(git -C "$repo_dir" status --porcelain)" ]; then
    echo "The source contains local changes: resolve them before updating."
    exit 1
  fi
  git -C "$repo_dir" pull --ff-only
  test -f "$repo_dir/coding-harness/SKILL.md"
  if [ -L "$skill_dir" ]; then
    echo "The skill is a symlink: use the symlink procedure."
    exit 1
  fi
  backup_root="$HOME/.local/share/coding-harness/backups"
  mkdir -p "$backup_root"
  backup_dir="$(mktemp -d "$backup_root/update-XXXXXXXX")"
  if [ -e "$skill_dir" ]; then
    mv "$skill_dir" "$backup_dir/coding-harness"
  fi
  mkdir -p "$skill_dir"
  cp -R "$repo_dir/coding-harness/." "$skill_dir/"
  echo "Skill updated. Backup: $backup_dir"
)
```

The initial checks stop the update if the source has local changes, has a detached HEAD, has no configured upstream, or cannot advance without a merge. The update follows the current branch's configured upstream; it does not assume a branch name, remote name, repository owner, or checkout location. If the folder came from a ZIP archive, download a fresh source version and apply the backup and copy steps: `git pull` requires a Git clone.

If you customized the installed skill, compare the backup with the new version and reapply only the changes you want. Check invocation in the client afterward; open a new session if it continues to use the previous version. Repeat the update for each separate copy you use.

### Alternative: Link to the Source

Codex and Claude Code document support for symlinked skill folders. On Linux, macOS, or WSL, you can avoid a second copy when the destination does not exist:

```bash
(
  set -eu
  repo_dir="$(pwd -P)"
  skill_root="$HOME/.agents/skills"
  # For Claude Code: skill_root="$HOME/.claude/skills"
  test -f "$repo_dir/coding-harness/SKILL.md"
  test ! -e "$skill_root/coding-harness"
  test ! -L "$skill_root/coding-harness"
  mkdir -p "$skill_root"
  ln -s "$repo_dir/coding-harness" "$skill_root/coding-harness"
)
```

If you already have a copy, move it outside the skill directory and preserve it first; do not create a link inside the existing copy. With a symlink, update only the repository using `git pull --ff-only` after checking the branch and local changes. The link sees the updated source without copying files again. Keep the source repository at the same location; local source changes become immediately visible to the skill.

## Install for One Project

Use these destinations inside the project instead of the personal folder:

| Client | Project destination |
| --- | --- |
| Codex | `.agents/skills/coding-harness/` |
| Claude Code | `.claude/skills/coding-harness/` |
| Cursor | `.cursor/skills/coding-harness/` or `.agents/skills/coding-harness/` |

Copy the entire folder and share it with the project when the team needs it. For remote sessions, make it available in the remote environment or repository according to the client. Do not assume a folder on your local computer also exists there.

## If the Skill Does Not Appear

1. Check that the path ends in `coding-harness/SKILL.md`, without an extra `coding-harness/coding-harness/` level.
2. Check that the file starts with frontmatter containing `name: coding-harness` and `description`.
3. Verify that `references/`, `assets/`, and `agents/` were copied with the file.
4. Find the skill in the client's menu and try explicit invocation. Reopen the client if needed.
5. Check that it is enabled in settings and that multiple directories do not contain copies with the same name.

For Codex, run these checks in the terminal:

```bash
codex --version
ls "$HOME/.agents/skills/coding-harness/SKILL.md"
sed -n '1,6p' "$HOME/.agents/skills/coding-harness/SKILL.md"
```

## Minimal Project Context

A bare explicit invocation, START, or the first explicit development invocation prepares at most two new project documents. Existing equivalents satisfy their roles, including canonical documents outside harness/:

| Default document | Purpose | Update when |
| --- | --- | --- |
| `harness/PROJECT_STATE.md` | Current goal, short active plan, criteria/evidence, relevant failed attempts, blockers, and next step | A meaningful work transition, blocker, handoff, or CHECKPOINT |
| `harness/PROJECT_MAP.md` | Stable purpose, technologies, components, contracts, material decisions, and reading order | An inspected architecture/contract change or explicit map refresh |

The installed skill provides the workflow. Default startup creates no harness README, AGENTS, INDEX, PROJECT_RECORD, archive, or skill copy. Keep the checkpoint compact; link a long existing plan instead of copying it. Keep active progress in state and stable knowledge in the map.

```text
$coding-harness
$coding-harness START
$coding-harness START JSON
$coding-harness START LEARN
```

START JSON uses JSON instead of Markdown for new state; existing formats and synchronization contracts remain authoritative. START LEARN explains unfamiliar technologies from actual sources. On an empty project, record that architecture is not established. Without a task, state remains pending and asks for the objective; setup is not application verification.

Repeated START preserves existing bytes, user notes, statuses, evidence, and snapshots. It creates only missing roles. Report external canonical dependencies and conflicting paths instead of duplicating or overwriting documents. Default new context files stay below harness/; root instructions and application configuration require their own authorized scope.

Reviews, explanations, design/plan-only requests, HARNESS STATUS, CHANGE IMPACT, and default map requests stay read-only. RESUME, CHECKPOINT, and HARNESS MIGRATE use existing context without full startup. Implicit selection for a small change creates no kit.

## Portable Mode

Use PORTABLE when the project must carry a complete reusable skill without a global installation:

```text
$coding-harness START PORTABLE
$coding-harness START PORTABLE LEARN
```

This adds `harness/skill/` with the complete SKILL.md, references, templates, and metadata. The current package has ten files; a fresh portable setup therefore adds twelve files instead of the previous twenty-one-file default. Copying only SKILL.md breaks its references.

Without a global installation, explicitly ask the agent:

```text
Read harness/skill/SKILL.md and the project's applicable instructions.
Use the actual canonical state and map, starting with
harness/PROJECT_STATE.md and harness/PROJECT_MAP.md when those are the selected paths.
```

The two context documents alone are not a standalone skill or automatically registered commands. A portable snapshot does not activate itself. If the source is unavailable, report that limitation; do not claim a complete portable package.

For a new repository, copy the reusable snapshot and request START there to create fresh project facts. State, maps, evidence, and permissions belong to their original project.

Existing snapshots remain preserved. Updating the global installation does not refresh them. An explicit refresh stages/validates the complete intended source, preserves customizations and one recoverable original, and reports retained backup locations. Backups are excluded from project mapping. Cleanup is explicit; do not delete unknown backup contents. See [Snapshot Lifecycle](coding-harness/references/CONTINUITY.md#history-and-snapshot-lifecycle).

## Check, Resume, and Consolidate

| Request | Result |
| --- | --- |
| `HARNESS STATUS` | Read-only check of actual state/map, evidence gaps, useful pointers, and a snapshot when present |
| `RESUME` | Reconcile saved facts with current instructions/source and continue a clear unfinished task |
| `CHECKPOINT` | Update one current checkpoint; no commit or diary implied |
| `HARNESS MIGRATE` | Reconcile legacy records into the two roles, preserve evidence/notes, and report redundant documents |

STATUS does not treat absent README, AGENTS, INDEX, PROJECT_RECORD, or snapshot as a defect in a minimal kit. Source freshness and application verification remain separate.

RESUME keeps supported unaffected evidence, invalidates affected current results when necessary, and retains historical context. It does not resurrect a completed task or execute an imported action blindly.

Migration preserves existing formats and canonical locations. Move active plans, checks, relevant failed attempts, blockers, and next steps into state; move stable documented knowledge into the map or existing decision records. Link long plans or important existing history. Read back destinations and account for original content before considering retirement.

MIGRATE alone does not delete originals or change code, snapshots, Git, or root instructions. Retirement requires an explicit request identifying generated redundant files; preserve notes, unresolved evidence, and existing consumers. Existing kits remain usable while reconciliation is reviewed.

## Design, Plan, Review, and Verify

```text
$coding-harness DESIGN Add cancellation to the existing order workflow
$coding-harness PLAN Add cancellation while preserving the public order ID
$coding-harness PLAN SAVE Add cancellation without changing the payment contract
$coding-harness REVIEW FEEDBACK Evaluate these comments against the API contract
$coding-harness Apply the supported review fixes and verify affected behavior
```

DESIGN and PLAN inspect without application edits, startup, or check execution. SAVE stores a short proposal/plan in canonical state or an established plan record. It preserves an unrelated active task; a long/independent plan can use an optional linked record. Planned checks remain separate from actual results.

Plans contain at most five active working deliverables with paths, shared input/output contracts, prerequisites, and observable checks. Each deliverable includes its own test/implementation/documentation cycle. Material plan corrections retain their evidence and affected interfaces.

Review checks required behavior and exact constraints before engineering quality. Received suggestions are evaluated against actual contracts; independent supported fixes can proceed when application edits are authorized. Debugging traces the bad value/failure to its responsible boundary, and regressions must demonstrate the intended defect instead of a setup error or mocked result.

Software engineering requirements, evidence gates, privacy, authorization, and stack independence remain in [Workflow](coding-harness/references/WORKFLOW.md) and [Engineering](coding-harness/references/ENGINEERING.md).

## Project Orientation and Change Impact

| Request | Result |
| --- | --- |
| `PROJECT MAP` | Read-only source-backed overview |
| `PROJECT MAP LEARN` | Explain an unfamiliar stack along a real source flow |
| `PROJECT MAP <area>` | Focused inspection of the named subsystem |
| `PROJECT MAP SAVE` | Save to the established map or harness/PROJECT_MAP.md |
| `PROJECT MAP UPDATE` | Refresh requested areas while retaining untouched inspection context and user notes |
| `CHANGE IMPACT <proposal>` | Trace affected contracts, consumers, likely edit paths, and existing checks without implementation |

LEARN can accompany a named area, explicit map SAVE/UPDATE, or CHANGE IMPACT. For example:

```text
$coding-harness PROJECT MAP LEARN I am new to Java and Spring Boot; explain one request
$coding-harness CHANGE IMPACT LEARN Add cancellation to the order workflow
```

To learn while implementing, say which stack is new to you in the same request. The skill will continue the requested code work and finish with the inspected request flow, actual check results, and one useful file to read next. For example: `$coding-harness I am new to this Spring Boot project. Add order validation.` This keeps a coding request actionable; `PROJECT MAP LEARN` on its own remains a read-only map.

These phrases are prompt instructions, not client commands. Mapping runs no tests, applications, databases, or services. Claims distinguish observations, inferences, and unknowns. A saved map contains stable knowledge and links state for current work; it is not a second checkpoint. See [Project Mapping](coding-harness/references/PROJECT_MAP.md).

## File Ownership and History

| Location | What belongs here |
| --- | --- |
| Installed coding-harness package | Reusable instructions/templates; no project facts |
| Canonical state | Active work and enough evidence/failure context to resume |
| Stable map / established docs | Project knowledge and material decisions |
| Optional linked record | Explicitly requested detailed history or a long plan |
| Git and existing PR/CI records | Versioned changes, reviewed rationale, and referenced verification evidence |
| Portable snapshot / backups | Explicit distribution and recovery; exclude from architecture discovery |

A checkpoint update does not authorize a commit. Preserve uncommitted evidence until a durable reference exists. Create no transcript copy or dated session diary by default.

## Resources

| Resource | Purpose |
| --- | --- |
| [SKILL.md](coding-harness/SKILL.md) | Entry point and smallest workflow |
| [Continuity](coding-harness/references/CONTINUITY.md) | Startup modes, state contract, health, resume, migration, and retention |
| [Workflow](coding-harness/references/WORKFLOW.md) | Design/plans, implementation/debugging, review, and evidence gates |
| [Engineering](coding-harness/references/ENGINEERING.md) | Proportionate software engineering requirements |
| [Project Mapping](coding-harness/references/PROJECT_MAP.md) | Technologies, connections, learning, impact, and source coverage |
| [Markdown State](coding-harness/assets/templates/PROJECT_STATE.md) | Compact checkpoint with an optional active plan |
| [JSON State](coding-harness/assets/templates/PROJECT_STATE.json) | Optional structured equivalent; older schema-version-1 state remains supported |
| [Map Template](coding-harness/assets/templates/PROJECT_MAP.md) | Stable source-backed documentation |
| [Optional Record](coding-harness/assets/templates/PROJECT_RECORD.md) | Requested long plan or detailed history |
| [openai.yaml](coding-harness/agents/openai.yaml) | Compatible-client metadata |

Maintenance of this source resumes from [REPOSITORY_STATE.md](REPOSITORY_STATE.md); never copy its tasks or evidence into a target project. Without a skill loader, use [PROJECT_START_PROMPT.md](PROJECT_START_PROMPT.md).

## Superpowers for Repository Maintenance

[Superpowers](https://github.com/obra/superpowers) is installed in this source repository as a Git submodule at `vendor/superpowers`, pinned to revision `bb92a77741419a4ab5f06e711a283343f1ada0c3` (7.0.0). It supports maintaining and evaluating this skill. It is outside the ten-file `coding-harness/` package and is never copied by START, PORTABLE, or client installation commands.

Initialize it after cloning or updating this source checkout:

```bash
git submodule update --init -- vendor/superpowers
git submodule status -- vendor/superpowers
```

The first command checks out the revision recorded by the parent repository, not the latest upstream release. A leading space in the status output indicates the recorded revision is checked out; `-` means uninitialized and `+` means a different revision. A ZIP download of the parent repository does not include submodule contents. Use a Git checkout for Superpowers maintenance; ordinary skill installation needs only coding-harness/.

[AGENTS.md](AGENTS.md) bootstraps Superpowers by directing repository agents to its using-superpowers skill and relevant writing-skills, debugging, test, and verification guidance. For an agent that does not read AGENTS.md, provide that file explicitly. Example maintenance request:

```text
Read AGENTS.md and use the pinned Superpowers writing-skills workflow to improve coding-harness. Test the current behavior before editing, then verify the candidate in fresh disposable projects. Preserve the two-document default and the standalone package.
```

This is a repository-scoped source installation with file-based loading. It does not register a native plugin, install account-wide skills, enable client hooks, or change other projects. For native client integration, follow the [upstream installation instructions](https://github.com/obra/superpowers#installation); do not combine installations blindly or claim native discovery from files being present.

### Update the Pinned Superpowers Version

Normal source updates followed by submodule initialization use the reviewed pin. To evaluate a different upstream revision, first ensure the submodule has no local changes, then fetch and select a reviewed commit:

```bash
(
  set -eu
  git submodule update --init -- vendor/superpowers
  test -z "$(git -C vendor/superpowers status --porcelain)"
  git -C vendor/superpowers fetch origin
  git -C vendor/superpowers checkout --detach "<reviewed-commit>"
  git diff --submodule=log -- vendor/superpowers
)
```

Replace `<reviewed-commit>` before running. Review changed upstream instructions and licenses, rerun the maintenance scenarios, and update the revision above. Saving the new gitlink in the parent repository requires the applicable Git authorization. Never overwrite a modified submodule or advance it automatically during target-project work. Upstream retains its own MIT license and attribution; do not edit its files to customize this skill.

### Evaluate Changes to This Skill

Keep maintenance evidence in [REPOSITORY_STATE.md](REPOSITORY_STATE.md), separate from target-project checkpoints. Use the baseline/candidate method in AGENTS.md and inspect emitted files and actual check results independently. Static link/frontmatter checks complement behavioral runs; they do not prove that an agent follows the instructions.

Select scenarios for the changed boundary. The core regression set is: minimal START then repeated START/STATUS; PORTABLE with an exact package comparison; read-only PLAN or mapping; and a code fix with an existing failing suite check. Preserve user notes and legacy canonical state when continuity changes. Exercise only disposable fixtures, without live services or personal data. If independent agents or native client discovery cannot be exercised, state that limit explicitly.

## Inspiration and Documentation

Workflow improvements draw on [ECC](https://github.com/affaan-m/ECC), revision `ef648e01899ba3e8dc6371642deaaf64b4477775`: progressive context retrieval, meaningful tests, explicit verification, and checkpoints before phase transitions. The instructions are written for this skill; they include no executable code or substantial text copied from ECC.

Earlier workflow ideas draw on [Superpowers](https://github.com/obra/superpowers), revision `8ca22dba9a94f28898bbce59f2537ff4d87c747d`: concrete task contracts, design tradeoffs, review reception, root-cause tracing, and regression-test integrity. The repository now also pins upstream source for maintenance, as described above. Coding-harness guidance remains independently written and requires no upstream scripts, hooks, runtime, approval chain, or automatic agent/worktree lifecycle when installed in a target project.

Client procedures were checked on October 7, 2026 against official documentation:

- [OpenAI: Build skills](https://learn.chatgpt.com/docs/build-skills)
- [Claude Code: Skills](https://code.claude.com/docs/en/skills)
- [Cursor: Agent Skills](https://cursor.com/docs/skills)

The previous kit was removed from the source; earlier versions remain in Git history.
