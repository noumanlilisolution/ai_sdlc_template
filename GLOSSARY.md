# eCW to Medplum migration

Moves each clinic's records (Practitioner first) from its eClinicalWorks database into that clinic's own Medplum project, proving every source row ended in exactly one outcome.

## Clients and runs

**Client**:
One clinic being migrated, with its own folder under `config/clients/`, its own eCW database and its own Medplum project.
_Avoid_: tenant (only the mapping header's field name), customer, practice

**Client key**:
The lower_snake_case name of a client, e.g. `volusia_medical_center`; its folder name and `--client`.
_Avoid_: client id (that is the Medplum client's id)

**Medplum client**:
The OAuth client (`ecw-etl`) the ETL logs in to a Medplum project with.
_Avoid_: app, bot

**Run**:
One migration attempt for one client and one resource, named by its run id (a UTC timestamp such as `20261105T101500Z`).
_Avoid_: job, batch, load (a load is one stage)

**Invocation**:
One execution of the `ecw-etl` command; a run can span several (e.g. `--stage load` the next day). Reports are uploaded once per invocation.

**Stage**:
One of extract, transform, load, reconcile, run in that order. A **sub-step** is a timed part of a stage.

**Gate**:
A condition a stage checks before it touches the source or Medplum (read, connect and write blockers). A stage stopped by a gate is **BLOCKED**.

## Source data

**Source**:
The client's eCW SQL Server, reached read-only.

**Bronze**:
The raw extract of one run: the source tables as Parquet plus a manifest of row counts and SHA-256 checksums, written once to the bucket. The source of truth.
_Avoid_: raw dump, snapshot, backup

**Mapping**:
A client's rules for one resource (`practitioner.yml`): source tables, eligibility, and per FHIR element the rule and the source column.
_Avoid_: spec, profile, template

**Source uid**:
`users.uid` in eCW: the business key of a person. It becomes the identifier in the client's source-uid system.
_Avoid_: id, doctor id, server id

**Server id**:
The id Medplum gives a resource. Never used as a business key.

**Identifier system**:
A namespace URI owned by one client (`source_uid_system`, `category_tag_system`). Fixed and approved before the first write, because every loaded resource carries it.

**Population**:
The group a practitioner belongs to (`internal`, `referral-directory`), written to `meta.tag`; it decides which duplicate survives.

## Rules and outcomes

**Eligibility rule**:
A mapping rule (E1-E5) deciding whether a source row becomes a candidate; it rejects the row or holds it for review.

**Candidate**:
A mapped resource before the record rules run.

**Ready record**:
A resource that passed every rule and may be loaded.

**Ingestion rules**:
The four rules on missing data: (1) an optional value is missing: it is **omitted**; (2) a required inner value is missing: it gets a **data-absent-reason**; (3) a block has nothing useful left: it is **dropped**; (4) the record cannot be identified: it is **rejected**.

**Data-absent-reason**:
The FHIR extension that marks a required value as missing, with an official code (e.g. `unknown`). Only where the mapping says so.

**Merge**:
Combining source rows with the same source uid into one resource; the survivor's values win.

**Duplicate NPI**:
Two people with the same NPI: the survivor is loaded, the others are quarantined (rejected), and the case is held for review when their family names differ.

**Exception**:
Any source row not loaded as-is (rejected, held for review, merged away, duplicate review), listed by source id in `exceptions.csv`.
_Avoid_: error (errors are failures of the ETL, not of a record)

**Load guard**:
The last check of a resource right before it is sent: no empty values or blocks, and it carries its source identifier.

**Conditional create**:
Creating a resource only if none carries its source identifier (`If-None-Exist`); 201 created, 200 existing, 412 duplicates already exist.

**Reconciliation**:
The proof after a load: every source row is in exactly one bucket, every loaded record reads back equal, and a replay creates nothing.

**Read-back**:
Reading a loaded record from Medplum and comparing it with what was sent.

**Replay check**:
Sending the same conditional create again; it must return the same record and leave exactly one match.

## Operations

**Jump host**:
`medplum-db-jumphost`, the GCP VM the ETL runs on, inside `tmux`.

**Reports**:
A run's log folder (run.log, audit.jsonl, report.json, exceptions.csv, rule_summary.json, ui_checklist.txt, errors.log) uploaded to the bucket.

**Door**:
How reversible a pull request is: **one-way** (schema, identifier systems, what is written to Medplum, data loss, ADRs) or **two-way** (easy to walk back). It sets how deep the human review goes.
