# CLAUDE.md

Agent-driven engineering with the `mattpocock/skills` set, installed in `.claude/skills/`. Every session loads this file.

## Skills are mandatory

Every task in this repo runs through a skill. The developer does not have to name it: matching the request to its skill is your job.

1. **Route first.** Before your first action on a request (reading code, planning, editing), find its row in the routing table below.
2. **Load the skill.** Load it through the Skill tool, then follow its steps in order. A typed `/name` means the same skill.
3. **Announce it.** Open your reply with `Skill: <name>, because <one-line match>.`
4. **Chain the stages.** When a skill finishes and the request needs the next stage, load the skill in the "Then" column and announce the switch.

12 skills are user-only (`disable-model-invocation: true`), and the Skill tool refuses them: `implement`, `implement-spec`, `to-spec`, `to-tickets`, `grill-me`, `grill-with-docs`, `setup-matt-pocock-skills`, `triage`, `wayfinder`, `improve-codebase-architecture`, `handoff`, `retro`. When the user typed the command, read `.claude/skills/<name>/SKILL.md` in full and follow it. When the routing table reaches one on its own, name the exact command (`/triage 12`) and wait. When a skill says "call the Skill tool with X" and X is user-only, read X's `SKILL.md` instead. A subagent doing skill work gets the skill's name in its prompt and reads that `SKILL.md` first.

A question that changes no code or documents gets a direct answer, with no skill needed. When a request fits no row, say so and ask which stage the work is in. Only the user can waive a skill, by saying so or typing `#workflow-skip`.

## Routing

| The request is | Skill | Then |
| --- | --- | --- |
| Anything, in a clone that isn't set up yet (`docs/agents/issue-tracker.md` is missing) | `setup-matt-pocock-skills`, before the request itself | the request's own row |
| Any code change, starting or resuming an issue, or "what's next?" | `orchestrator`, before the request's own row | the skill its first unmet gate names |
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
| Editing a skill or `CLAUDE.md` | `writing-for-agents` | |
| Changing this repo's issue tracker or skill configuration | `setup-matt-pocock-skills` | |

## Gates every skill keeps

The full gate list (0-15) is in the `orchestrator` skill. Always:

- Code changes go test-first through `tdd`, at seams the user approved.
- Done means `python scripts/check.py` prints `green`.
- Every commit follows the three-axis review (Standards and Spec via `code-review`, plus Context; orchestrator gate 9), with its blockers resolved.
- Commit to a feature branch `<spec#>-<slug>` and reference the ticket. Humans merge to `main`.
- Stop for the user at the human gates: test seams (`to-spec`), ticket breakdown (`to-tickets`), merge, sign-offs, and the production change.

## Pointers

- **Skills:** upstream skills in `.claude/skills/` are never edited; team rules go in the `orchestrator` skill or `standards/`. Upgrade steps: `README.md`, "Updating skills".
- **Review rules:** `standards/` is the rulebook `code-review` enforces. While implementing, read only the file for the area you're touching.
- **GitHub:** labels, branches, PRs and review by door are in `docs/github.md`. The developer guide is `docs/sdlc-guide.md`.

## Agent skills

Rerun `setup-matt-pocock-skills` to change any of these.

- **Issue tracker**: GitHub Issues on this clone's `origin`, through the `gh` CLI. See `docs/agents/issue-tracker.md`.
- **Triage labels**: the five defaults, `needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, `wontfix`. See `docs/agents/triage-labels.md`.
- **Domain docs**: single-context, with `GLOSSARY.md` and `docs/adr/` at the repo root, created lazily by `domain-modeling`. See `docs/agents/domain.md`.

## Business context (loaded every session)

Plan and build from it; a business fact it does not state is asked, or recorded in `context/assumptions.md` as unconfirmed. What the system must and must never do is in `context/requirements.md`: read it at triage, spec and review. The rest of `context/` is indexed in `context/README.md`.

@context/business_context.md
@context/constraints.md
@context/assumptions.md
