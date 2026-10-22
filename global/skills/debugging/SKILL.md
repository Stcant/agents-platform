---
name: debugging
description: Use when a bug, test failure or unexpected behavior needs a root cause, especially when a first fix attempt failed or the failure is hard to reproduce.
---

# Debugging by evidence

## Rules

- Reproduce before changing code. Record the exact command, input and observed result.
- A setup failure (missing dependency, broken fixture, wrong environment) is not evidence about the defect.
- After 3 materially equivalent failed attempts, stop editing. Report what was ruled out and what is still unknown.
- Do not fix symptoms that hide the cause. Do not rewrite unrelated code while debugging.

## Procedure

1. **Reproduce.** Find the smallest command or input that shows the failure. Confirm it fails for the stated reason, not a different one.
2. **Localize.** Trace the bad value backward from where it is observed to the boundary that introduced it. Compare with a working sibling path. Use temporary probes that log shapes and identifiers, not secrets or full payloads; remove them afterward.
3. **Hypothesize.** Write the cause as a single sentence that predicts what will change when it is fixed. If two hypotheses are plausible, choose the experiment that separates them.
4. **Test the hypothesis.** Run the smallest check that distinguishes it. Change one thing at a time.
5. **Fix the root cause.** Make the smallest complete change. If a test harness exists, first observe a focused test fail for the intended reason, then pass. Setup errors are not a regression demonstration.
6. **Verify.** Re-run the original reproduction and the relevant checks. Report PASS / FAIL / NOT RUN with the real commands, and what they do not prove.

## Reporting

State the cause, the evidence that identifies it, the fix, the checks, and the remaining unknowns. If the cause is not proven, say so.
