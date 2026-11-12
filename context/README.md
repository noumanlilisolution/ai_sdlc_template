# Project context

What an agent or a new teammate reads **before** planning or building anything. Read in this order:

1. [business_context.md](business_context.md): why the project exists, for whom, what success means
2. [requirements.md](requirements.md): what the system must do, and what it must never do
3. [constraints.md](constraints.md): the hard limits (security, access, environment)
4. [technical_architecture.md](technical_architecture.md): how it is built, one page
5. [assumptions.md](assumptions.md): what we believe but have not confirmed
6. [domain_glossary.md](domain_glossary.md) and [decisions.md](decisions.md): indexes into `GLOSSARY.md`,
   `docs/adr/` and `.out-of-scope/`
7. [readiness/](readiness/readiness_checklist.md): what must be true before a production change, its state, and
   the sign-offs

`GLOSSARY.md`, `docs/adr/`, `.out-of-scope/` and `CODING_STANDARDS.md` stay at the repo root: the skills read and write
them there.

## Rules for these files

- **One home per fact** (`ds-one-home`). Domain words live in `GLOSSARY.md`, decisions in `docs/adr/`, rejected
  ideas in `.out-of-scope/`, review rules in [CODING_STANDARDS.md](../CODING_STANDARDS.md). These files summarise
  and point; they never copy a rule.
- **Never invent.** A fact nobody has confirmed goes in `assumptions.md` or under *Open questions*, with who can
  answer it.
- **Ids, counts and paths only.** No secrets, no personal data.
- **Keep it current** (`ds-stale`). A PR that makes one of these files wrong updates it, or waives it in its body
  (orchestrator gate 10).
- A computer-checkable fact (branch protection, CI, config switches) is checked at session start by
  `scripts/readiness.py`, never written here.
- Only people fill in [readiness/approval_status.md](readiness/approval_status.md).
