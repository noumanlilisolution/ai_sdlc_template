# Requirements

Each row points at where the rule is enforced or decided. Words are from `GLOSSARY.md`. Triage, specs and the
Context review cite rows by number (F1, N1).

## Functional

| # | The system must | Where |
|---|---|---|
| F1 | <behaviour> | <module, ADR or spec> |
| F2 | `check.py` fails on a knowledge document with an unknown type, invalid frontmatter, a broken link, an unresolved `related:` id, a duplicate id, or an id that isn't lower-kebab-case | `scripts/check.py`, knowledge-docs step (spec #3) |

## Must never

| # | The system must never | Decided in |
|---|---|---|
| N1 | <forbidden behaviour> | <ADR or CODING_STANDARDS.md rule id> |

## Quality

- `python scripts/check.py` is green on every commit and in CI.
- Every PR is reviewed as [docs/github.md](../docs/github.md) says (three automated axes, one human approval by
  door).
