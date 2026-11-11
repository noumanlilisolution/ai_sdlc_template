#!/usr/bin/env bash
# GitHub setup for this repository. Safe to rerun: labels are upserted, protection is replaced.
#   labels      the triage, category and door labels the skills and templates use
#   protection  branch protection on main: PRs only, CI green, one approval, code owners
#
#   bash scripts/github/bootstrap.sh [labels|protection|all]    (default: all)
#
# `labels` runs from scripts/github/session_check.sh at the start of every Claude Code session.
# `protection` is run by hand by a repo admin (`gh auth login`), once code owners are agreed.
set -euo pipefail

part="${1:-all}"
case "${part}" in
  labels | protection | all) ;;
  *) echo "usage: $0 [labels|protection|all]" >&2; exit 2 ;;
esac

repo="${GITHUB_REPOSITORY:-$(gh repo view --json nameWithOwner --jq .nameWithOwner)}"
echo "configuring ${repo}: ${part}"

if [[ "${part}" == labels || "${part}" == all ]]; then
  label() { gh label create "$1" --repo "${repo}" --color "$2" --description "$3" --force; }
  label needs-triage    "fbca04" "Maintainer needs to evaluate this issue"
  label needs-info      "d4c5f9" "Waiting on the reporter for more information"
  label ready-for-agent "0e8a16" "Fully specified, ready for an AFK agent"
  label ready-for-human "1d76db" "Requires human implementation"
  label wontfix         "ffffff" "Will not be actioned"
  label bug             "d73a4a" "Something the system does wrong"
  label enhancement     "a2eeef" "A problem the system does not solve yet"
  label door:one-way    "b60205" "Hard to reverse: a code owner reads the whole change"
  label door:two-way    "c2e0c6" "Easy to walk back: PR body, evidence and seam tests"
  echo "labels: done"
fi

if [[ "${part}" == protection || "${part}" == all ]]; then
  gh api --method PUT "repos/${repo}/branches/main/protection" --input - <<'JSON'
{
  "required_status_checks": {"strict": true, "contexts": ["check"]},
  "enforce_admins": true,
  "required_pull_request_reviews": {
    "required_approving_review_count": 1,
    "require_code_owner_reviews": true,
    "dismiss_stale_reviews": true
  },
  "restrictions": null,
  "allow_force_pushes": false,
  "allow_deletions": false
}
JSON
  echo "protection: main protected"
fi
