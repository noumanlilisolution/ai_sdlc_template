# Readiness checklist

What must be true before a production change (orchestrator gates 13 and 14). Items a computer can check are
computed by `scripts/readiness.py` at session start and are never ticked here; this file lists the items a
person confirms. Evidence goes in [readiness_report.md](readiness_report.md); sign-offs in
[approval_status.md](approval_status.md).

## Computed (by `scripts/readiness.py`, never ticked here)

- Every sign-off in `approval_status.md` for the change is `approved` or `waived`
- `.github/CODEOWNERS` names an owner
- CI passed on `main`

## Confirmed by a person

| # | Item | Who confirms | How (the QA step) |
|---|---|---|---|
| R1 | <what must be true> | <role> | <the check a person runs> |
