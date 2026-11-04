# Documentation Standard

Every document spends one of two budgets. Context load is the cost of material agents load every turn; cognitive load is the cost to humans of knowing which document to read. Write down what can't be looked up, and point to everything else. The `writing-for-agents` skill is the reference for anything an agent consumes.

## Where each kind of knowledge lives

| Knowledge | Home | Created by |
| --- | --- | --- |
| Navigation for every agent session | `AGENTS.md` (pointers only) | humans, `/setup-matt-pocock-skills` |
| Domain vocabulary | `GLOSSARY.md` | `/grill-with-docs`, `/domain-modeling` |
| Hard-to-reverse decisions | `docs/adr/NNNN-slug.md` | `/domain-modeling`, humans |
| What to build | spec in the issue tracker | `/to-spec` |
| Units of work | tickets in the issue tracker | `/to-tickets` |
| Rules for reviewers | `standards/` | humans, `/retro` |
| How to work | the routing table in `AGENTS.md`, plus the skills | humans |
| Session-to-session state | handoff doc in the OS temp directory | `/handoff` |
| Researched facts | Markdown in the repo | `/research` |

## Rules

- **DOC-1** `AGENTS.md` holds only skill routing, bootstrap, the gates, navigation pointers, and the skills config block. Rules go to `standards/`; procedures live in the skills.
- **DOC-2** Keep each fact in one place. Link to it; never copy it. A copied fact is a second place to update and goes stale.
- **DOC-3** Don't restate the environment. If one file or one command answers the question (`package.json` scripts, `--help`, a directory listing), point to it.
- **DOC-4** Write down what can't be found by looking: the reason behind a choice, an unwritten convention, a gotcha.
- **DOC-5** Write the positive instruction ("write one-line comments") instead of a prohibition ("don't write long comments").
- **DOC-6** Create `GLOSSARY.md` and `docs/adr/` lazily, when the first term or decision is resolved, not upfront.
- **DOC-7** A change that alters behaviour described in a doc updates that doc in the same PR.
- **DOC-8** Every public module has a docstring or header comment saying what it does and what it hides.
