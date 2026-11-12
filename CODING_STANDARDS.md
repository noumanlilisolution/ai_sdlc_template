# Coding standards

Read at **review** time only, by the `code-review` skill's Standards axis and by `agent-review.yml`. These are the
judgement calls. Mechanical rules (format, lint, types, tests) are enforced by `scripts/check.py` and are **not**
reported here.

Cite a rule by its id. Severity: **critical** blocks a merge; the rest are findings to fix or argue. A judgement
call the team settles (a `/retro` outcome, a repeated review comment) becomes one new line here.

## Data protection

- **sec-no-secrets** (critical): secrets never appear in the repository, prompts, issues, PRs, commits or logs;
  code reads them at run time from the environment or a secret store.
- **lg-log-secret-or-pii** (critical): logs, audit events, alerts, exception messages and issue text carry ids,
  counts and paths only. Never personal data, a token or a secret.
- **sec-unvalidated-input**: values from config, the environment, files or HTTP are validated where they enter,
  not trusted downstream.

## Project rules

<!-- Add the rules only this project has, one line each, citing the ADR that holds them, for example:
- **xx-api-only** (critical): the store is written only through its API ([ADR-0001](docs/adr/0001-...md)). -->

## Design

- **cr-small-interface**: a module exports the least a caller needs. New behaviour goes behind the existing
  interface where it can (locality), not into a new public function.
- **cr-test-at-interface**: tests call what a module exports and assert on observable outcomes. A test that must
  change when the inside changes is testing past the seam.
- **cr-two-adapters**: a port needs two adapters (production + test) to exist. One adapter is indirection; inline
  it.
- **cr-time-comes-in**: the clock, the environment and the working directory are read only at the entry point;
  everything below takes them as arguments.
- **cr-glossary-words**: names in code, tests, issues, logs and PRs use [GLOSSARY.md](GLOSSARY.md) terms, not
  their listed synonyms.
- **cr-adr-conflict**: a change that contradicts an ADR says so in the PR and updates or supersedes the ADR.
  Silent contradictions are findings.

## Errors and logging

- **eh-broad-try**: catch the narrowest exception. A catch-all only at a boundary (an entry point, a job, an
  alert channel), and only where it records the traceback and an error id.
- **eh-missing-domain-exception**: raise a named exception rather than a generic one when a caller may need to
  tell the case apart.
- **lg-no-context**: a log line names the step, the id or count it is about, and the outcome.
- **lg-wrong-level**: ERROR means a person must act; WARNING means degraded but continuing; INFO is the normal
  story.
- **lg-log-in-tight-loop**: no logging inside per-field or per-value loops.

## Docs and code

- **ds-one-home**: a fact lives in one file and every other file points at it. The homes are the table in
  `.claude/skills/orchestrator/SKILL.md` section 4. A rule copied into a second file is a finding.
- **ds-stale**: a docstring, README, `context/` file or ADR that no longer matches the code is a finding on the PR
  that made it stale.
- **ds-incomplete**: a public function's docstring states what the types cannot: invariants, units, ordering,
  what is raised and when.
- **cs-redundant-comment**: comments say why, not what. Delete comments that repeat the code.
- **cd-rule-of-three**: tolerate a second copy; extract on the third.
