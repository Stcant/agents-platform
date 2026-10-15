# Repository State

Updated: 2026-10-15T10:42:30.206117+00:00
Branch context: main; source update parent 60d1e36d6c903dbf871f250acb1665d5bba2acb5.
Access context: local source checkout and connected GitHub repository.

## Objective and Task

Maintain anonymous English, instruction-only development guidance with proportionate engineering and minimal project context.

TASK-022 — verified

Requirement: use the pinned Superpowers guidance to improve code implementation and verification, rather than only teaching output.

## Changes

- Route small bug fixes through behavior-first debugging and its regression requirement.
- With a suitable existing harness, require an acceptance/regression test that fails for the intended behavior before implementing the change; replace the previous optional wording.
- Require the regression to remain with the implementation. If behavior was already edited, demonstrate the test against the original in an isolated, user-change-preserving experiment and report the actual ordering.
- At completion, identify which check catches a wrong changed decision or missing side effect. A green happy-path suite or ad hoc probe is insufficient when the existing harness can express the defect.
- Retain manual reproduction for unsuitable/unavailable harnesses, proportionate engineering, read-only routes, and the ten-file package. Add no runtime, test framework, default file, or client requirement.

## Evidence

| Scenario | Observed outcome | Scope and limits |
| --- | --- | --- |
| Preserved earlier HTTP implementation artifact | Bug guard existed but only one valid-name test was retained. Parent reran that test on fixed and original buggy source: both passed 1/1. | Observed regression omission motivating this change; historical local artifact, not a new failure manufactured by this task |
| Current-source controls: retries, cancellation, CI discovery, tiny HTTP fix | All four agents completed correct focused code and regression tests. Retry and cancellation agents reported intended failures before implementation; discovery control also registered colocated tests in the CI command. | Existing successful behavior retained; no new architecture, CI-discovery, or suite rule added |
| Candidate retry feature | Recorded test runs show original source green baseline, intended red, then minimal implementation and green. Parent replay on original: 3 failures; fixed: 5/5 pass. | Actual return values, three-call limit, error identity, and immediate permanent failure tested |
| Candidate cancellation bug | Recorded runs include regression failures with original production source. Parent replay: 2 failures originally, 4/4 pass fixed. | Tests assert writes, idempotency, shipped rejection, missing/foreign ownership; no real database |
| Candidate tiny HTTP guard | New regression reports 200 instead of required 400 on original; fixed suite passes 2/2 in parent rerun. | Real local HTTP request; valid-name response preserved |
| Source/package checks | PASS: ten package files, 92 local links/anchors, valid frontmatter/JSON, eight original client Bash blocks preserved, all ten Bash blocks syntax checked, pinned upstream source clean | Static checks complement the fresh-agent task runs |

Fresh agents received only the source skill and normal task request in separate disposable projects. Parent inspected emitted source/tests and replayed candidate tests against original and fixed behavior. Temporary evaluation projects and logs stay outside the reusable package and are not published. Some npm invocations emitted an environment `http-proxy` warning without failing.

Historical TASK-021 remains in Git. This update improves an explicit regression-completeness requirement; the four new controls already succeeded before editing. These small Node fixtures do not establish universally better generated code, performance, or correctness in a real Java/Spring Boot project.

## Next Action and Limits

Refresh copied installations when desired. Existing project documents and installed copies are not refreshed by a repository commit. Client-native discovery and global installation were not exercised.

## Authorization

The user explicitly authorized proceeding with code-generation improvements to this skill and the established repository update. No target application, global skill, upstream source, branch rewrite, deployment, or external message is included.
