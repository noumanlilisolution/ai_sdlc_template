# A demo client or file-based source in the repository

The repository holds no demo clinic, synthetic dump or file-based source (`source.files_dir`) for running the ETL end to end on fake data.

## Why this is out of scope

Production code must carry no switch that reads anything but the client's real source, and a demo client config next to real ones invites mistakes (copied identifier systems, a run against the wrong project). End-to-end behaviour is covered by the test suite instead: `tests/test_pipeline.py` runs the whole pipeline with in-memory adapters at every port, on the synthetic tables in `tests/ecw_tables.py`.

## Prior requests

- 2026-10-29 / 2026-10-30: `demo_clinic` on a local Medplum, with `src/extract/file_source.py` (removed 2026-11-02)
