# Code Review Standard

How reviews run and how findings get resolved. The procedure is the `code-review` skill.

## Two axes

- **REV-1** Every review covers two separate axes, and `/code-review` runs them in parallel:
  - **Standards**: does the diff follow `standards/` plus the smell baseline?
  - **Spec**: does the diff do what the spec or ticket asked, no more and no less?
- **REV-2** The axes are reported separately and never merged into one ranked list. If the code meets every standard but builds the wrong thing, it fails review.

## Finding severity

- **REV-3** Every finding is one of:
  - **Blocker**: a breach of a hard rule (`standards/security.md`, a failing check, a missing or wrong requirement). Merge waits until it is fixed.
  - **Should-fix**: a breach of a documented judgement rule. Fix it, or reply with a reason the reviewer accepts.
  - **Consider**: a smell from the baseline. The author decides; no reply needed.
- **REV-4** Every finding cites its source: a rule ID (`CODE-4`), a spec line, or a named smell.

## Roles

- **REV-5** The author, human or agent, runs the checks and `/code-review` before asking for human review. The PR body links to the spec or ticket.
- **REV-6** Standards are applied at review, not front-loaded into implementation. Implementation agents run under the most context pressure; reviewers work from just the diff.
- **REV-7** Every merge needs at least one human approval. The human checks the Spec axis and the merge danger in the PR body (one-way or two-way door, blast radius).
- **REV-8** Refactoring that a review suggests happens in this stage, not during the red-green loop.

## Feeding back

- **REV-9** If the same finding shows up in three reviews, it becomes a lint rule, a CI check, or a new rule in `standards/` during the next `/retro`.
