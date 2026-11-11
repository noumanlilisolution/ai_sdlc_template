#!/usr/bin/env bash
# Runs at the start of every Claude Code session (SessionStart hook in .claude/settings.json).
#   gate 0      labels: created when any is missing (bootstrap.sh labels)
#               protection: only reported; a repo admin runs `bash scripts/github/bootstrap.sh protection`
#   hook        switches on the pre-commit hook for this clone (core.hooksPath .githooks), unless the
#               clone already points core.hooksPath somewhere else
#   readiness   the computed items of context/readiness/readiness_checklist.md (scripts/readiness.py)
# Never blocks the session: every problem becomes a message, and the exit code is always 0.
set -uo pipefail

here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
root="$(cd "${here}/../.." && pwd)"
required=(needs-triage needs-info ready-for-agent ready-for-human wontfix bug enhancement
  door:one-way door:two-way)

say() {  # $1 message for the human, $2 context for the agent (double quotes and backslashes removed)
  local human="${1//[\"\\]/\'}" agent="${2//[\"\\]/\'}"
  printf '{"systemMessage":"%s","hookSpecificOutput":{"hookEventName":"SessionStart","additionalContext":"%s"}}\n' \
    "${human}" "${agent}"
  exit 0
}

# --- readiness (needs only the repo and a Python 3; gh is used for CI if present) -----------------
# gh is not on Git Bash's PATH on Windows by default.
if ! command -v gh >/dev/null 2>&1; then
  for dir in "/c/Program Files/GitHub CLI" "/mnt/c/Program Files/GitHub CLI"; do
    [[ -x "${dir}/gh.exe" ]] && export PATH="${dir}:${PATH}" && break
  done
fi
python=""
for candidate in "${root}/.venv/Scripts/python.exe" "${root}/.venv/bin/python" python3 python; do
  if command -v "${candidate}" >/dev/null 2>&1 && "${candidate}" -c 'import sys; sys.exit(sys.version_info < (3, 9))' 2>/dev/null; then
    python="${candidate}" && break
  fi
done
if [[ -n "${python}" ]]; then
  readiness="$(PYTHONIOENCODING=utf-8 "${python}" "${root}/scripts/readiness.py" 2>/dev/null | tr -d '\r' | paste -sd '|' - | sed 's/|/ | /g')"
else
  readiness="unknown: no Python 3.9+ found"
fi
readiness="Readiness: ${readiness:-unknown}"

# --- pre-commit hook (the agent, the hook and CI run the same check) -------------------------------
current_hooks="$(git -C "${root}" config --get core.hooksPath 2>/dev/null)"
if [[ -z "${current_hooks}" ]]; then
  if git -C "${root}" config core.hooksPath .githooks; then
    hook="pre-commit hook switched on"
  else
    hook="pre-commit hook could not be switched on"
  fi
elif [[ "${current_hooks}" == ".githooks" ]]; then
  hook="pre-commit hook on"
else
  hook="pre-commit hook not set: core.hooksPath is ${current_hooks}"
fi
readiness="${hook}. ${readiness}"

# --- gate 0 (needs gh) ------------------------------------------------------------------
if ! command -v gh >/dev/null 2>&1; then
  say "Gate 0 not checked: gh CLI not found. ${readiness}" "Orchestrator gate 0 unknown: gh CLI is not installed. ${readiness}"
fi
gh auth status >/dev/null 2>&1 \
  || say "Gate 0 not checked: run gh auth login. ${readiness}" "Orchestrator gate 0 unknown: gh is not logged in. ${readiness}"
repo="$(gh repo view --json nameWithOwner --jq .nameWithOwner 2>/dev/null)" \
  || say "Gate 0 not checked: no GitHub remote, or GitHub unreachable. ${readiness}" "Orchestrator gate 0 unknown: no GitHub repo for this clone. ${readiness}"

existing="$(gh label list --repo "${repo}" --limit 200 --json name --jq '.[].name' 2>/dev/null)"
missing=()
for name in "${required[@]}"; do
  grep -qxF "${name}" <<<"${existing}" || missing+=("${name}")
done
labels="labels ok"
if ((${#missing[@]})); then
  if bash "${here}/bootstrap.sh" labels >/dev/null 2>&1; then
    labels="labels created (${missing[*]})"
  else
    labels="labels missing (${missing[*]}), and creating them failed: needs write access"
  fi
fi

if gh api "repos/${repo}/branches/main/protection" >/dev/null 2>&1; then
  protection="main protected"
else
  protection="main NOT protected: an admin runs bash scripts/github/bootstrap.sh protection"
fi

summary="${labels}; ${protection}. ${readiness}."
if [[ "${labels}" == "labels missing"* || "${protection}" == *NOT* ]]; then
  say "Gate 0: ${summary}" "Orchestrator gate 0 UNMET for ${repo}: ${summary}"
fi
say "Gate 0: ${summary}" "Orchestrator gate 0 met for ${repo}: ${summary}"
