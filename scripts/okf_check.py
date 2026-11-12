"""The knowledge-docs check: every knowledge doc has a known type and its references resolve.

    python scripts/okf_check.py [repo-root]

Enforces requirement F2 (context/requirements.md); the rules are in spec #3 and the README's
"Knowledge docs" section. Standard library only and Python 3.9-safe, like scripts/check.py.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# The knowledge docs in scope: a folder (repo-relative) and the files directly in it.
SCOPE_FOLDERS = ("context", "context/readiness", "docs/adr", ".out-of-scope")
SCOPE_FILES = ("GLOSSARY.md",)

# Default type by exact path, then by folder. Spelling and case match the README and spec #3.
TYPE_BY_PATH = {
    "context/business_context.md": "Business Context",
    "context/requirements.md": "Requirements",
    "context/constraints.md": "Constraints",
    "context/assumptions.md": "Assumptions",
    "context/technical_architecture.md": "Architecture",
    "context/README.md": "Hub",
    "context/decisions.md": "Hub",
    "context/domain_glossary.md": "Hub",
    "GLOSSARY.md": "Glossary",
}
TYPE_BY_FOLDER = {
    "context/readiness": "Readiness",
    "docs/adr": "Decision",
    ".out-of-scope": "Out of Scope",
}


def _docs(root: Path) -> list[str]:
    """Repo-relative POSIX paths of the knowledge docs in scope, sorted."""
    found = [name for name in SCOPE_FILES if (root / name).is_file()]
    for folder in SCOPE_FOLDERS:
        base = root / folder
        if base.is_dir():
            found += [
                f"{folder}/{p.name}" for p in base.iterdir() if p.is_file() and p.suffix == ".md"
            ]
    return sorted(found)


def _default_type(rel: str) -> str | None:
    if rel in TYPE_BY_PATH:
        return TYPE_BY_PATH[rel]
    folder = rel.rpartition("/")[0]
    return TYPE_BY_FOLDER.get(folder)


def check_knowledge_docs(root: Path) -> list[str]:
    """Problems as sorted `path:line: reason` lines; an empty list means clean."""
    problems = []
    for rel in _docs(root):
        if _default_type(rel) is None:
            problems.append(f"{rel}:1: no type (add frontmatter type or a path mapping)")
    return problems


def main(argv: list[str]) -> int:
    """Print each problem, or the doc count when clean; exit 1 on any problem."""
    root = Path(argv[0]).resolve() if argv else ROOT
    problems = check_knowledge_docs(root)
    for line in problems:
        print(line)
    if problems:
        return 1
    print(f"okf bundle: {len(_docs(root))} docs ok")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
