# Secrets in local files

The ETL reads secrets only from GCP Secret Manager. There is no `.env`, no `secrets/<client>.env` and no "envfile" provider.

## Why this is out of scope

A file of secrets on a laptop or the jump host outlives the run, gets copied, and is easy to commit. Secret Manager gives access control, audit logs and rotation; values stay in memory and are redacted from every log line ([ADR-0004](../docs/adr/0004-secrets-in-secret-manager-bucket-by-impersonation.md)).

## Prior requests

- 2026-10-30: `secrets/demo_clinic.env` for the local demo (deleted 2026-11-02)
- 2026-11-02: `secrets.provider: envfile` (removed)
