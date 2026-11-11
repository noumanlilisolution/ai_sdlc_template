"""Computed readiness for a production change, printed at session start.

    python scripts/readiness.py

The computer-checkable items of context/readiness/readiness_checklist.md, worked out
live so they never go stale in a file:

- per section of context/readiness/approval_status.md (`## <release> · <scope>`): how
  many people's sign-offs are approved or waived;
- for the repository: whether CODEOWNERS names an owner and whether CI passed on main.

Add project-specific computed items (config switches, migrations pending, ...) as new
functions in main(). Prints one line per item and always exits 0: it informs, it never
blocks a session.
"""

from __future__ import annotations

import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APPROVALS = ROOT / "context" / "readiness" / "approval_status.md"
COMMENT_RE = re.compile(r"<!--.*?-->", re.DOTALL)  # example sections are commented out
SECTION_RE =re.compile(r"^## (.+?)\s*$")
ROW_RE = re.compile(r"^\|([^|]*)\|([^|]*)\|([^|]*)\|")
STATUS_COLUMN = 3  # Approval | Approver (role) | Status | Date | Where


def _approval_lines() -> list[str]:
    """One line per approval_status.md section: approved or waived / total."""
    if not APPROVALS.exists():
        return ["sign-offs: no approval_status.md"]
    counts: dict[str, tuple[int, int]] = {}
    section: str | None = None
    text = COMMENT_RE.sub("", APPROVALS.read_text(encoding="utf-8"))
    for line in text.splitlines():
        head = SECTION_RE.match(line)
        if head:
            section = head.group(1)
            continue
        row = ROW_RE.match(line)
        if section is None or row is None:
            continue
        status = row.group(STATUS_COLUMN).strip().lower()
        if status in {"status", ""} or set(status) <= {"-", ":"}:
            continue  # header or separator row
        approved, total = counts.get(section, (0, 0))
        counts[section] = (approved + (status in {"approved", "waived"}), total + 1)
    if not counts:
        return ["sign-offs: none requested"]
    return [f"{name}: sign-offs {ok}/{total}" for name, (ok, total) in counts.items()]


def _codeowners_line() -> str:
    path = ROOT / ".github" / "CODEOWNERS"
    text = path.read_text(encoding="utf-8") if path.exists() else ""
    owners = [
        line
        for line in text.splitlines()
        if line.strip() and not line.lstrip().startswith("#") and "@" in line
    ]
    return "CODEOWNERS names owners" if owners else "CODEOWNERS names no owner"


def _ci_line() -> str:
    gh = shutil.which("gh")
    if gh is None:
        return "CI on main: unknown (gh not found)"
    try:
        result = subprocess.run(
            [gh, "run", "list", "--branch", "main", "--workflow", "ci.yml", "--limit", "1"]
            + ["--json", "conclusion", "--jq", '.[0].conclusion // "no run"'],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
            timeout=30,
        )
    except subprocess.TimeoutExpired:
        return "CI on main: unknown (gh timed out)"
    if result.returncode != 0:
        return "CI on main: unknown (gh failed)"
    return f"CI on main: {result.stdout.strip() or 'no run'}"


def main() -> int:
    """Print the computed readiness lines."""
    for line in [*_approval_lines(), _codeowners_line(), _ci_line()]:
        print(line)
    return 0


if __name__ == "__main__":
    sys.exit(main())
