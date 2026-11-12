# Approval status

The sign-offs a production change needs (orchestrator gate 14). Who may fill it in: see the rules in
[context/README.md](../README.md). `scripts/readiness.py` counts each section's `approved` and `waived` rows.

Add one section per release and scope, shaped like the commented example below. Status is one of `pending`,
`approved`, `waived` or `rejected`.

<!--
## v1.0 · checkout

| Approval | Approver (role) | Status | Date | Where |
|---|---|---|---|---|
| Security review | Security lead | pending | | <link> |
-->
