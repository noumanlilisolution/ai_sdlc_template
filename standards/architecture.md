# Architecture Standard

The shared vocabulary (module, interface, depth, seam, adapter, leverage, locality) comes from the `codebase-design` skill. Load it when a design question comes up.

## Modules

- **ARCH-1** Prefer **deep modules**: a small interface hiding a large implementation. A module whose interface is about as complex as its body is shallow and should be merged or deepened.
- **ARCH-2** Every module has one entry point (`__init__.py`, `index.ts`, or equivalent). Callers import from the entry point, never from internals.
- **ARCH-3** Code that changes together lives together (locality). Organise by domain concept, not by technical layer.
- **ARCH-4** Dependencies point inward: domain logic does not import I/O, frameworks, or transport. I/O sits behind an adapter at the edge.

## Seams

- **ARCH-5** A seam is a public boundary where behaviour can be observed and substituted. Tests attach only at agreed seams (`standards/testing.md`).
- **ARCH-6** Reuse an existing seam before adding one. Each new seam needs a reason in the spec.

## Change shape

- **ARCH-7** "Make the change easy, then make the easy change." A prefactor lands as its own ticket, before the feature.
- **ARCH-8** A wide refactor goes expand, then migrate, then contract. First add the new form beside the old, then move callers over in batches with CI green after each one, then delete the old form.
- **ARCH-9** No speculative generality: add a hook, parameter, or abstraction only when a current spec needs it.

## Decisions

- **ARCH-10** Record an ADR in `docs/adr/` when a decision is hard to reverse, would surprise a future reader, and came from a real trade-off. All three must hold. The format is defined by the `domain-modeling` skill (`ADR-FORMAT.md`).
- **ARCH-11** A change that contradicts an accepted ADR either supersedes it with a new ADR or gets rejected in review.
- **ARCH-12** To find candidates for deepening in existing code, run `/improve-codebase-architecture`.
