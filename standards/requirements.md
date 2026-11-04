# Requirements Standard

Applies to specs (`/to-spec`) and tickets (`/to-tickets`). The shapes are the templates inside those two skills.

## Specs

- **REQ-1** A spec states the problem and the solution from the user's point of view before any implementation detail.
- **REQ-2** User stories follow `As a <actor>, I want <capability>, so that <benefit>`, and together they cover every behaviour in scope.
- **REQ-3** The spec names the test seams and the user approved them before it was published. Use the fewest seams possible, placed as high as possible, with one as the ideal.
- **REQ-4** Implementation decisions describe modules, interfaces, contracts, and schema shapes. File paths and code snippets stay out, because they go stale. The one exception is a decision-rich snippet from a prototype.
- **REQ-5** "Out of scope" is filled in. An empty section means scope was never discussed.
- **REQ-6** Domain terms match `GLOSSARY.md`. A term the glossary lacks goes to `/domain-modeling`; nobody invents a synonym.
- **REQ-7** A spec that contradicts an ADR says so explicitly and gives the reason.

## Tickets

- **REQ-8** Each ticket is a vertical tracer-bullet slice: a narrow path through every layer that can be demonstrated or verified on its own.
- **REQ-9** Each ticket fits in one fresh agent context window. A ticket that doesn't fit gets split.
- **REQ-10** Each ticket lists its blockers, or says `None`. Prefactoring tickets come first.
- **REQ-11** Acceptance criteria are checkable statements about behaviour, not "works correctly" or "is clean".
- **REQ-12** A wide mechanical refactor is sequenced as expand, then migrate, then contract (see `standards/architecture.md`).

## Definition of ready

A ticket can be labelled `ready-for-agent` when REQ-8 to REQ-11 hold and a fresh agent could start it from the ticket alone, with no conversation history. If it needs human judgement mid-flight, label it `ready-for-human` instead.
