# Engineering Agent Template

A lean, project-agnostic starting repo for teams that build software with Claude Code using [Matt Pocock's skills](https://github.com/mattpocock/skills).

## Why this repo exists

Coding agents produce better work when they follow a process: agree on the idea, write a spec, break it into tickets, build each one test-first, then review it. Left alone, an agent tends to jump straight to code. This template gives you that process from the first commit:

- **Mandatory skills.** `CLAUDE.md` maps every kind of request (new feature, bug, refactor, review, PR) to a skill. The agent picks the skill itself, says which one it chose, and follows its steps. You never have to remember skill names.
- **Human gates.** The agent stops for your approval at the points that matter: test seams in the spec, the ticket breakdown, and the merge to `main`.
- **Shared standards.** `CODING_STANDARDS.md` holds the rules `code-review` enforces, so every agent and every developer reviews against the same rulebook.

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

Bugs enter at `diagnosing-bugs`, then go to `tdd` for the regression test and fix. The full routing table is in `CLAUDE.md`; the `orchestrator` skill holds the gates (0-15) between the stages. The developer guide, with what you type at each step, is [docs/sdlc-guide.md](docs/sdlc-guide.md).

## Setup after cloning

You need Git, Python 3.9+, the `gh` CLI, and Claude Code (it reads `CLAUDE.md` and `.claude/skills/`). The skills are committed, so a fresh clone works with no install step.

### 1. Clone the repo

```bash
git clone <this-repo-url> my-project
cd my-project
```

To start your own history instead of the template's, delete `.git`, run `git init`, and add your own remote.

### 2. Connect GitHub and open Claude Code

The template ships configured for GitHub Issues (`docs/agents/`). Push the repo to GitHub, then:

```bash
gh auth login      # the agent reads and writes issues and PRs through gh
claude             # or open the folder in the VS Code / JetBrains extension
```

The **session check** (`scripts/github/session_check.sh`) runs at every session start: it creates the GitHub labels, switches on the pre-commit hook, and reports branch protection and computed readiness in one line.

To use another tracker (GitLab, local markdown, Jira, Linear, ...), run `/setup-matt-pocock-skills`. It rewrites `docs/agents/` and the `## Agent skills` section of `CLAUDE.md`.

### 3. Run the check

```bash
python scripts/check.py     # must end in "green"
```

### 4. Start working

Describe what you want in plain words, for example "I want to add a login page". The agent opens with `Skill: <name>, because ...` and guides you through that stage. To skip the workflow for one request, say so or type `#workflow-skip`.

### Before your first real feature

- Fill in `context/`, starting with `business_context.md`.
- Read `CODING_STANDARDS.md`, adapt it to your stack, and add your project's own rules.
- Add your stack's format, lint, type and test commands to `PROJECT_STEPS` in `scripts/check.py`, and its toolchain to `.github/workflows/ci.yml`.
- Name real owners in `.github/CODEOWNERS`, then a repo admin runs `bash scripts/github/bootstrap.sh protection`.
- Add the `ANTHROPIC_API_KEY` repository secret, so `agent-review` runs on PRs.

## Updating skills

Upstream skills are never edited by hand (team rules go in `orchestrator/` or `CODING_STANDARDS.md`); `scripts/check.py` enforces it. Update in one reviewed PR:

```bash
npx skills add mattpocock/skills -a claude-code   # installs into .claude/skills/
python scripts/check.py --lock-skills    # rewrite scripts/skills.sha256
python scripts/check.py                  # must end in "green"
```

`skills-lock.json` pins the installed versions; `scripts/skills.sha256` checksums every upstream skill file.

## Knowledge docs

The files agents plan and review against (`context/*.md`, `context/readiness/*.md`, `docs/adr/*.md`,
`.out-of-scope/*.md`, `GLOSSARY.md`) are **OKF-shaped**, after Google's
[Open Knowledge Format](https://github.com/GoogleCloudPlatform/open-knowledge-format) v0.2. A knowledge-docs step
of `scripts/check.py` will enforce requirement F2. **It is planned (spec #3) and not built yet**; the rules below are
what it will check:

- **Type is inferred from the path; frontmatter is optional.** A frontmatter `type:` overrides the path default.
  The known types are `Business Context`, `Requirements`, `Constraints`, `Assumptions`, `Architecture`, `Hub`,
  `Readiness`, `Decision`, `Out of Scope` and `Glossary`, matched exactly.
- **Ids are optional.** An `id:` is lower-kebab-case and unique across all these folders; `related:` lists other
  docs' ids.
- **Links must resolve**, with exact case and inside the repo. A link starting with `/` resolves from the **repo
  root**, not a bundle root: the repo is not one OKF bundle.
- **Nothing is exported.** As stored, these files are not a conformant OKF bundle (OKF wants `type` in every file);
  only the check's view is. Anything outside the repo that reads them needs an export step first, and none exists.

## What's in the repo

| Path | Purpose |
| --- | --- |
| `CLAUDE.md` | Skill routing, gates, pointers, and the business context; Claude Code loads it every session |
| `.claude/skills/` | Installed skills, pinned in `skills-lock.json`, plus our `orchestrator` (the gates) and `context-review` (the Context axis) |
| `.claude/settings.json` | Claude Code hooks (session check at start, stale-docs check after each commit) and read bans on secrets |
| `context/` | Business context, requirements, constraints, assumptions, architecture, and go-live readiness |
| `docs/agents/` | Issue-tracker, triage-label, and domain-doc config (GitHub by default) |
| `docs/github.md` | Labels, branches, commits, PRs, review by door |
| `docs/sdlc-guide.md` | Developer guide: what you type at each step and where state lives |
| `CODING_STANDARDS.md` | Rules the `code-review` skill enforces, read at review only |
| `scripts/check.py` | The one check (skills lock, your project steps), run by you, the pre-commit hook and CI |
| `scripts/readiness.py` | Computed readiness, reported by the session check |
| `scripts/github/` | `bootstrap.sh` (labels, branch protection) and `session_check.sh` |
| `.githooks/pre-commit` | Runs `scripts/check.py` before every commit |
| `.github/` | CI (`ci.yml`, `agent-review.yml`), PR and issue templates, `CODEOWNERS` |
