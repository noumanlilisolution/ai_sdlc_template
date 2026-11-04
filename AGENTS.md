# AGENTS.md

Agent-driven engineering with the `mattpocock/skills` set, installed in `.agents/skills/`. Every session loads this file.

## Skills are mandatory

Every task in this repo runs through a skill. The developer does not have to name it: matching the request to its skill is your job.

1. **Route first.** Before your first action on a request (reading code, planning, editing), find its row in the routing table below.
2. **Load the skill.** Read `.agents/skills/<name>/SKILL.md` in full, then follow its steps in order. A typed `/name` or `$name` means the same skill.
3. **Announce it.** Open your reply with `Skill: <name>, because <one-line match>.`
4. **Chain the stages.** When a skill finishes and the request needs the next stage, load the skill in the "Then" column and announce the switch.

**In Claude Code**, 12 skills are user-only (`disable-model-invocation: true`), and the Skill tool refuses them: `implement`, `implement-spec`, `to-spec`, `to-tickets`, `grill-me`, `grill-with-docs`, `setup-matt-pocock-skills`, `triage`, `wayfinder`, `improve-codebase-architecture`, `handoff`, `retro`. Load these by reading their `SKILL.md` as in step 2, and follow it as if the user had typed `/<name>`. Load every other skill through the Skill tool. When a skill says "call the Skill tool with X" and X is user-only, read X's `SKILL.md` instead. A subagent doing skill work gets the skill's name in its prompt and reads that `SKILL.md` first.

A question that changes no code or documents gets a direct answer, with no skill needed. When a request fits no row, say so and ask which stage the work is in. Only the user can waive a skill, by saying so or typing `#workflow-skip`.

## Routing

| The request is | Skill | Then |
| --- | --- | --- |
| Anything, in a clone that isn't set up yet (`docs/agents/issue-tracker.md` is missing) | `setup-matt-pocock-skills`, before the request itself | the request's own row |
| A new feature, idea, or plan that isn't agreed yet | `grill-with-docs` | `to-spec` |
| Stress-testing a plan or decision, without writing docs | `grill-me` | |
| An agreed plan that needs writing up | `to-spec` | `to-tickets` |
| A spec that needs breaking into work | `to-tickets` | `implement` |
| Building a ticket, a spec, or a small agreed change | `implement` (it drives `tdd` and `code-review`) | |
| A bug, error, failing test, or slowdown | `diagnosing-bugs` | `tdd` for the regression test and fix |
| A UI or state-model question that's best answered by trying it | `prototype` | `grill-with-docs` |
| Module shape, seams, or interfaces | `codebase-design` | |
| Finding refactor targets across the codebase | `improve-codebase-architecture` | `to-tickets` |
| Domain terms, `GLOSSARY.md`, or an ADR | `domain-modeling` | |
| Facts from external docs or APIs | `research` | |
| Incoming issue reports | `triage` | |
| Work too big for one session | `wayfinder` | |
| Reviewing a diff, branch, or PR | `code-review` | |
| Writing a PR description | `pr` | |
| A session running out of context, or ending mid-task | `handoff` | |
| Looking back on a finished feature or a bad session | `retro` | |
| Editing a skill, `AGENTS.md`, or `CLAUDE.md` | `writing-for-agents` | |
| Changing this repo's issue tracker or skill configuration | `setup-matt-pocock-skills` | |

## Setup

Each clone is set up once, with `/setup-matt-pocock-skills` in Claude Code or Cursor, or `$setup-matt-pocock-skills` in Codex. Write its `## Agent skills` block into this file, replacing the one below, because all three agents read `AGENTS.md`. Its `docs/agents/*.md` files mark the clone as set up.

Skills live twice: `.agents/skills/` for Codex and Cursor, and `.claude/skills/` for Claude Code, as identical committed copies. Change them only with `npx skills add mattpocock/skills`, then confirm that `diff -r .agents/skills .claude/skills` prints nothing.

## Gates every skill keeps

- Code changes go test-first through `tdd`, at seams the user approved.
- Every commit follows `code-review` on the diff, with its blockers resolved.
- Commit to a feature branch and reference the ticket. Humans merge to `main`.
- Stop for the user at the human gates: test seams (`to-spec`), ticket breakdown (`to-tickets`), and merge.

## Standards

`standards/` is the rulebook `code-review` enforces. While implementing, read only the file for the area you're touching.

## Agent skills

Defaults until `setup-matt-pocock-skills` replaces this section.

- **Issue tracker**: local markdown. Each spec is `.scratch/<feature-slug>/spec.md`; each ticket is `.scratch/<feature-slug>/issues/<NN>-<slug>.md` with a `Status:` line.
- **Triage labels**: the five defaults, `needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, `wontfix`.
- **Domain docs**: single-context, with `GLOSSARY.md` and `docs/adr/` at the repo root, created lazily by `domain-modeling`.
