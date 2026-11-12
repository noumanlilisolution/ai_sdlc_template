# Approval status

The sign-offs a production change needs (orchestrator gate 14). **Only people fill this in**: an agent never
adds, edits or ticks a row. `scripts/readiness.py` counts each section's `approved` and `waived` rows at
session start.

Add one section per release and scope, shaped like the commented example below. Status is one of `pending`,
`approved`, `waived` or `rejected`.

<!--
## v1.0 · checkout

| Approval | Approver (role) | Status | Date | Where |
|---|---|---|---|---|
| Security review | Security lead | pending | | <link> |
-->
