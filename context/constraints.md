# Constraints

Hard limits. Changing one is a one-way door: it needs an ADR and a code owner's review. Each row names where the
rule lives; the rule text is there, not here.

| Constraint | Rule lives in |
|---|---|
| Secrets never in the repo, prompts, issues or logs | `sec-no-secrets`, `lg-log-secret-or-pii` ([CODING_STANDARDS.md](../CODING_STANDARDS.md)) |
| Agents cannot read `secrets/` or `.env` files | [.claude/settings.json](../.claude/settings.json) |
| PRs only, CI green, one human approval; agents never commit, push or merge unasked | [docs/github.md](../docs/github.md) |
| Work follows the lifecycle | the `orchestrator` skill |
| <environment, access or platform limit> | <ADR or rule id> |
