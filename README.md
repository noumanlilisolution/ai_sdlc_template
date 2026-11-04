# Engineering Agent Template

A lean, project-agnostic starting repo for teams that build software with coding agents (Claude Code, Codex, or Cursor) using [Matt Pocock's skills](https://github.com/mattpocock/skills).

## Why this repo exists

Coding agents produce better work when they follow a process: agree on the idea, write a spec, break it into tickets, build each one test-first, then review it. Left alone, an agent tends to jump straight to code. This template gives you that process from the first commit:

- **Mandatory skills.** `AGENTS.md` maps every kind of request (new feature, bug, refactor, review, PR) to a skill. The agent picks the skill itself, says which one it chose, and follows its steps. You never have to remember skill names.
- **Human gates.** The agent stops for your approval at the points that matter: test seams in the spec, the ticket breakdown, and the merge to `main`.
- **Shared standards.** `standards/` holds the rules `code-review` enforces, so every agent and every developer reviews against the same rulebook.
- **One setup for every agent.** Claude Code, Codex, and Cursor all read the same `AGENTS.md` and the same skills, so a team can mix agents on one codebase.

The repo contains no application code. Clone it as the base for a new project, or copy its files into an existing one, then build your product on top of it.

## How work moves

```text
idea ──grill-with-docs──▶ shared understanding (+ GLOSSARY.md, ADRs)
     ──to-spec──────────▶ spec, with test seams you approve
     ──to-tickets───────▶ tracer-bullet tickets, with a breakdown you approve
     ──implement────────▶ test-first through tdd, then code-review, then commit
     ──human merge──────▶ main
     ──retro────────────▶ fixes to checks, standards, docs
```

Bugs enter at `diagnosing-bugs`, then go to `tdd` for the regression test and fix. The full routing table is in `AGENTS.md`.

## Setup after cloning

You need Git and at least one supported agent:

| Agent | Requirement | Reads instructions from | Reads skills from |
| --- | --- | --- | --- |
| Claude Code | v2.1.277 or later | `AGENTS.md` | `.claude/skills/` |
| Codex | current release | `AGENTS.md` | `.agents/skills/` |
| Cursor | a release with Agent Skills | `AGENTS.md` | `.agents/skills/` (also `.claude/skills/`) |

Both skill folders are committed, so a fresh clone works in any of the three agents with no linking or install step.

### 1. Clone the repo

```bash
git clone <https://github.com/noumanlilisolution/ai_sdlc_template.git> my-project
cd my-project
```

To start your own history instead of the template's, delete `.git`, run `git init`, and add your own remote.

### 2. Open your agent at the repo root and run setup

Run the setup skill once per clone. If you skip it and just ask for something, the agent runs setup first anyway, because `docs/agents/issue-tracker.md` is missing.

| Agent | How to start setup |
| --- | --- |
| Claude Code | Run `claude` in the repo root (or open the folder in the VS Code / JetBrains extension), then type `/setup-matt-pocock-skills` |
| Codex | Run `codex` in the repo root, then type `$setup-matt-pocock-skills` |
| Cursor | Open the folder in Cursor, then type `/setup-matt-pocock-skills` in Agent chat |

Cursor loads skills from both `.agents/skills/` and `.claude/skills/`, so each skill can appear twice in its list. The two copies are identical, so it doesn't matter which one runs.

### 3. Answer the setup questions

The setup skill explores the repo and asks you:

1. **Issue tracker**: GitHub, GitLab, local markdown under `.scratch/`, or another tool (Jira, Linear, ...). If you pick GitHub or GitLab, it connects the remote and checks that `gh` or `glab` can see the repo.
2. **Triage labels**: keep the five defaults (`needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, `wontfix`) or map them to labels you already use.
3. **Domain docs**: single-context (`GLOSSARY.md` and `docs/adr/` at the root), the right choice for almost every repo. You're only asked about this if the repo is a monorepo.

It writes the answers to `docs/agents/` and to the `## Agent skills` section of `AGENTS.md`. Commit both so teammates who clone later skip this step. You can edit `docs/agents/*.md` by hand later. Rerun setup only to switch issue trackers.

Setup is done when `docs/agents/issue-tracker.md` exists.

### 4. Start working

Describe what you want in plain words, for example "I want to add a login page". The agent opens with `Skill: <name>, because ...` and guides you through that stage. To skip the workflow for one request, say so or type `#workflow-skip`.

### Before your first real feature

- Read the files in `standards/` and adapt them to your stack.
- Add build, lint, and test jobs to `.github/workflows/quality-checks.yml`.

## Updating skills

Both skill folders must stay identical. Update them only with:

```bash
npx skills add mattpocock/skills
diff -r .agents/skills .claude/skills   # must print nothing
```

`skills-lock.json` pins the installed versions.

## What's in the repo

| Path | Purpose |
| --- | --- |
| `AGENTS.md` | Skill routing, setup, and gates. Claude Code, Codex, and Cursor all load it. Don't add a `CLAUDE.md`, because Claude Code would read that instead |
| `.agents/skills/` | Installed skills for Codex and Cursor, pinned in `skills-lock.json` |
| `.claude/skills/` | An identical copy of the skills for Claude Code |
| `docs/agents/` | Issue-tracker, triage-label, and domain-doc config, written by the setup skill |
| `standards/` | Rules the `code-review` skill enforces |
| `.github/workflows/quality-checks.yml` | CI: secret scan. Add your build, lint, and test jobs here |
