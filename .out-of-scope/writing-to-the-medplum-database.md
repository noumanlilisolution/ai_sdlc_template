# Writing to the Medplum database

The ETL does not connect to Medplum's Postgres, not for resources and not for an audit table of its own. Loading through the database would skip Medplum's access policies, validation, history and search indexing, and DevOps explicitly forbids it for this migration ("write to MedPlum only through the API; never connect to the MedPlum database or use medplum-psql from the script").

## Why this is out of scope

All writes are conditional creates through the FHIR API ([ADR-0001](../docs/adr/0001-medplum-through-the-fhir-api-only.md)); the audit trail is `audit.jsonl`, uploaded with the run's reports. An earlier version had a Postgres `etl_audit` sink and `MEDPLUM_DB_*` settings; both were removed on 2026-11-02.

## Prior requests

- 2026-11-02: the optional `etl_audit.event_log` table in Medplum's Postgres (removed)
