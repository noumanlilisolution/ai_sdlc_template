# How we use GitHub

The lifecycle's steps and gates are in the `orchestrator` skill (`.claude/skills/orchestrator/SKILL.md`). This page
is how we use GitHub along the way.

## Labels

Created by `scripts/github/bootstrap.sh`. Every Claude Code session starts with `scripts/github/session_check.sh`
(SessionStart hook in `.claude/settings.json`): it creates any missing label, reports whether `main` is protected
and the computed readiness (`scripts/readiness.py`), and switches on the pre-commit hook for the clone. Protection
itself stays manual (`bash scripts/github/bootstrap.sh protection`, repo admin), because it needs agreed code
owners.

| Label | Meaning |
|---|---|
| `needs-triage` | New; a maintainer must evaluate it (set by the issue templates) |
| `needs-info` | Waiting on the reporter |
| `ready-for-agent` | Fully specified (Agent Brief comment); an AFK agent may build it |
| `ready-for-human` | Needs a person to implement |
| `wontfix` | Will not be done; a rejected enhancement gets a record in `.out-of-scope/` |
| `bug`, `enhancement` | Category |
| `door:one-way`, `door:two-way` | On every PR: how deep the human review goes |

## Branches, commits, PRs

- One branch and one PR per spec: `<spec#>-<slug>`, e.g. `12-password-reset`.
- Each ticket is a sub-issue of its spec; commits end with `(#<ticket>)`. Fixes from review land as their own
  commits (`fix(review): ... (#n)`), so `/retro` can see what the brakes caught.
- The PR body follows the `pr` skill ([template](../.github/pull_request_template.md)): Summary, Evidence, Merge
  Danger, and exactly one door label. It closes the tickets (`Closes #14 #15`); the spec and the request issue are
  closed by hand after QA.
- **Work notes:** each spec issue carries one `<!-- work-notes -->` comment, the temporary memory that lets a
  cleared context resume ([shape](../.claude/skills/orchestrator/WORK-NOTES.md)). Durable knowledge is promoted
  out of it as it settles; the notes close with the spec.
- Merge with a merge commit (no squash), so ticket and review commits stay readable.

## Review by door

Every PR needs `scripts/check.py` green (CI job `check`), the three-axis review (Standards against
[CODING_STANDARDS.md](../CODING_STANDARDS.md), Spec, Context; locally at orchestrator gate 9, on the PR by
`agent-review.yml`), a docs check that came back ok or a `## Docs waivers` section in the body (orchestrator gate
10), and **one human approval**.

| Door | Examples | Human review |
|---|---|---|
| **one-way** | data that is written and cannot be walked back, public interfaces, identifiers, storage layout, secrets and access, ADRs | a code owner reads the whole change |
| **two-way** | logging, refactors behind an interface, new checks, docs | PR body, evidence, and the tests at the seam |

## Main is protected

PRs only, CI green, one approval, code owners on the paths in `.github/CODEOWNERS`, no force pushes.

## Skills

Committed in `.claude/skills/`, never edited; team rules live in the `orchestrator` skill and `CODING_STANDARDS.md`.
`scripts/check.py` fails when an upstream skill file changes (`scripts/skills.sha256`). Upgrade steps: [README](../README.md#updating-skills).

## Additions to the upstream playbook

| Topic | Our rule | Why |
|---|---|---|
| Orchestrator | One team skill that finds the current step, holds the gates and carries team rules over the unedited upstream skills | A plain request ("fix the X") otherwise skips straight to code |
| Business context | `context/`, a third review axis (Context), and a production-change gate with people-only sign-offs | Never guess a business fact; the two upstream axes miss business rules |
| Session check | Every session: creates missing labels, switches on the pre-commit hook, reports protection and computed readiness | A fact a computer can check is checked, not written down; git hooks are off in a fresh clone |
| Skills lock | Upstream skill files are checksummed; an edit fails `check.py` | An intended change shows up in the PR, so it is never silent |
| Docs drift | A Claude Code hook after each agent commit, and a branch-wide docs check before `gh pr create` (orchestrator gate 10), ask a sub-agent which docs are stale | Rules get copied into new docs and go stale; a fix promised for "the next commit" is easy to forget |
