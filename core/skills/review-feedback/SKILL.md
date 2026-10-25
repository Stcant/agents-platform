---
name: review-feedback
description: Use when handling code review comments, pull request feedback or another agent's findings, including when deciding whether a comment should be implemented.
---

# Handling review feedback

Do not implement a comment just because it exists. Classify every item first.

| Class | Meaning | Action |
| --- | --- | --- |
| SUPPORTED | The code or requirement confirms the problem | Fix it, with a check |
| UNSUPPORTED | The code contradicts the claim | Reply with the evidence; do not change code |
| NEEDS CONTEXT | The comment depends on intent not visible in the change | Ask the specific question |
| OUT OF SCOPE | Valid but unrelated to this change | Record it; propose separately |

## Rules

- Read the surrounding code before accepting or rejecting a finding.
- Distinguish a demonstrated defect from a preference. Preferences do not override project conventions.
- If a suggested fix would break a contract, say so and propose the compatible alternative.
- Implement accepted items one at a time, keeping behavior changes separate from refactors.
- Re-run the relevant checks after the changes; never reuse a pre-change result.

## Response

Lead with the classification and the evidence, then the fix or the reason for rejecting it. Keep it short. Do not defend code you wrote; the review is about the code.
