"""The one umbrella check. Done means green.

    python scripts/check.py                every step, in order (runs them all)
    python scripts/check.py --lock-skills  rewrite the upstream-skills lock after an upgrade

The agent, the pre-commit hook (.githooks/pre-commit) and CI (.github/workflows/ci.yml)
all run this same command. Standard library only, so it runs before any project
dependency is installed.

Built-in step:
  skills lock    no upstream skill file was edited, added or removed. Team rules go in
                 the orchestrator skill; scripts/skills.sha256 holds a checksum of every
                 other skill file. Upgrading is one reviewed PR: `npx skills add
                 mattpocock/skills`, then --lock-skills.

Add your stack's format, lint, types and tests to PROJECT_STEPS below.
"""

from __future__ import annotations

import hashlib
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PY = sys.executable
SKILLS = ROOT / ".claude" / "skills"
SKILLS_LOCK = ROOT / "scripts" / "skills.sha256"
OURS = {"orchestrator", "context-review"}  # skill folders that are not from upstream

# The project's own checks, in order: (name, command). Each runs from the repo root and
# fails the check on a non-zero exit. Examples:
#   ("format", ["npx", "prettier", "--check", "."]),
#   ("lint", [PY, "-m", "ruff", "check", "."]),
#   ("types", [PY, "-m", "mypy"]),
#   ("tests", [PY, "-m", "pytest"]),
PROJECT_STEPS: list[tuple[str, list[str]]] = [
    ("tests", [PY, "-m", "unittest", "discover", "-s", "tests", "-t", "."]),
    ("knowledge docs", [PY, str(ROOT / "scripts" / "okf_check.py")]),  # F2, spec #3
]


def _skill_files() -> list[Path]:
    """Every upstream skill file, in a stable order."""
    return sorted(
        p
        for p in SKILLS.rglob("*")
        if p.is_file() and p.relative_to(SKILLS).parts[0] not in OURS
    )


def _digest(path: Path) -> str:
    """SHA-256 of the file with line endings normalised (a checkout may use CRLF)."""
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def _lock_lines() -> list[str]:
    return [f"{_digest(p)}  {p.relative_to(SKILLS).as_posix()}" for p in _skill_files()]


def lock_skills() -> int:
    """Rewrite the lock from the files on disk (after a reviewed upgrade)."""
    lines = _lock_lines()
    SKILLS_LOCK.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    print(f"locked {len(lines)} upstream skill files")
    return 0


def check_skills_lock() -> int:
    """Fail when an upstream skill file was edited, added or removed."""
    if not SKILLS_LOCK.exists():
        print(f"missing {SKILLS_LOCK.relative_to(ROOT)}: run check.py --lock-skills")
        return 1
    want = set(SKILLS_LOCK.read_text(encoding="utf-8").splitlines())
    have = set(_lock_lines())
    for line in sorted(want - have):
        print(f"changed or removed: {line.split('  ', 1)[1]}")
    for line in sorted(have - want):
        print(f"changed or added:   {line.split('  ', 1)[1]}")
    if want != have:
        print(
            "Upstream skills are never edited: put team rules in the orchestrator skill "
            "or CODING_STANDARDS.md. Upgrading? Run `npx skills add mattpocock/skills`, then "
            "check.py --lock-skills, in the same reviewed PR."
        )
        return 1
    print(f"upstream skills: {len(have)} files match the lock")
    return 0


def _steps() -> list[tuple[str, list[str]]]:
    me = str(Path(__file__).resolve())
    return [
        ("skills lock", [PY, me, "--check-skills"]),
        *PROJECT_STEPS,
    ]


def main(argv: list[str]) -> int:
    """Run every step; report each; fail if any failed."""
    if "--lock-skills" in argv:
        return lock_skills()
    if "--check-skills" in argv:
        return check_skills_lock()
    results = []
    for name, cmd in _steps():
        shown = " ".join([Path(cmd[0]).name, *cmd[1:]])
        print(f"\n=== {name}: {shown}", flush=True)
        start = time.monotonic()
        try:
            code = subprocess.run(cmd, cwd=ROOT, check=False).returncode
        except FileNotFoundError:
            print(f"command not found: {cmd[0]}")
            code = 127
        results.append((name, code, time.monotonic() - start))
    print("\n=== summary", flush=True)
    for name, code, seconds in results:
        print(f"  {'ok  ' if code == 0 else 'FAIL'}  {name:<14} {seconds:5.1f}s")
    failed = [name for name, code, _ in results if code != 0]
    print("green" if not failed else f"RED: {', '.join(failed)}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
