# Testing Standard

The `tdd` skill is the operating manual. This file holds the rules a reviewer checks.

## What a test is

- **TEST-1** Tests check behaviour through public interfaces. A test that breaks on a refactor when behaviour hasn't changed is coupled to the implementation and must be rewritten.
- **TEST-2** Expected values come from an independent source of truth: a literal, a worked example, or the spec. An assertion that recomputes the answer the same way the code does is tautological and is rejected.
- **TEST-3** Test names read as specifications in domain language: `test_customer_can_cancel_unshipped_order`.

## Where tests go

- **TEST-4** Tests attach only at seams agreed in the spec or ticket. Adding a test at a new seam reopens the seam agreement with a human.
- **TEST-5** Mock only at system boundaries you don't own: network, clock, randomness, third-party APIs. Never mock your own modules.
- **TEST-6** Prefer one high integration-style seam over many unit seams. Pure, complex logic, such as a calculator or a state machine, earns its own seam.

## How tests are written

- **TEST-7** Red before green: every behaviour change starts with a failing test, run and observed failing.
- **TEST-8** Work in vertical slices: one test, the minimum code to pass it, then the next. Never write all the tests first.
- **TEST-9** Every bug fix lands with a regression test that went red on the bug (`/diagnosing-bugs`, phase 1).
- **TEST-10** Tests are deterministic. Pin time, seed randomness, and isolate the filesystem and network. A flaky test is a bug and is fixed or deleted before merge.

## Running

- **TEST-11** While working, run single test files often. Run the full suite once before review. CI runs the full suite on every PR.
- **TEST-12** Don't set coverage targets. Judge coverage against the seams: every user story in the spec is exercised at some seam.
