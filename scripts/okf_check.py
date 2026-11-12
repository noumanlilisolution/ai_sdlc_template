"""The knowledge-docs check: every knowledge doc has a known type and its references resolve.

    python scripts/okf_check.py [repo-root]

Enforces requirement F2 (context/requirements.md); the rules are in spec #3 and the README's
"Knowledge docs" section. Standard library only and Python 3.9-safe, like scripts/check.py.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Optional

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
KNOWN_TYPES = frozenset(TYPE_BY_PATH.values()) | frozenset(TYPE_BY_FOLDER.values())

KEY_RE = re.compile(r"([A-Za-z_][A-Za-z0-9_-]*)[ \t]*:(.*)\Z")  # splits on the first colon


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


def _default_type(rel: str) -> Optional[str]:
    if rel in TYPE_BY_PATH:
        return TYPE_BY_PATH[rel]
    folder = rel.rpartition("/")[0]
    return TYPE_BY_FOLDER.get(folder)


class Invalid(Exception):
    """Frontmatter that cannot be read. Carries only a line number, never file content."""

    def __init__(self, line: int) -> None:
        super().__init__(line)
        self.line = line


def _unquote(value: str) -> str:
    if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
        return value[1:-1]
    return value


def _frontmatter(text: str) -> dict[str, tuple[str, int]]:
    """Top-level `key: value` pairs of the frontmatter block, each with its file line.

    Only top-level keys are read. Indented lines, and `- item` lines under a bare `key:`,
    belong to the key above them and are skipped, so OKF's nested fields pass.
    """
    lines = text.lstrip("﻿").splitlines()
    if not lines or lines[0].rstrip() != "---":
        return {}
    end = next((i for i in range(1, len(lines)) if lines[i].rstrip() == "---"), None)
    if end is None:
        raise Invalid(1)
    fields: dict[str, tuple[str, int]] = {}
    last_value: Optional[str] = None  # value of the last top-level key; None before the first
    for number, line in enumerate(lines[1:end], start=2):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if line[0] in " \t":
            if last_value is None:
                raise Invalid(number)
            continue
        if stripped == "-" or stripped.startswith("- "):
            if last_value != "":
                raise Invalid(number)
            continue
        match = KEY_RE.match(line.rstrip())
        if match is None or match.group(1) in fields:
            raise Invalid(number)
        key, last_value = match.group(1), match.group(2).strip()
        value = _unquote(last_value)
        if key in ("type", "id") and not value:
            raise Invalid(number)
        fields[key] = (value, number)
    return fields


def _doc_problems(root: Path, rel: str) -> list[str]:
    try:
        text = (root / rel).read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return [f"{rel}:1: not UTF-8 text"]
    try:
        fields = _frontmatter(text)
    except Invalid as error:
        return [f"{rel}:{error.line}: invalid frontmatter"]
    if "type" in fields:
        doc_type, line = fields["type"]
        if doc_type not in KNOWN_TYPES:
            return [f"{rel}:{line}: unknown type '{doc_type}'"]
    elif _default_type(rel) is None:
        return [f"{rel}:1: no type (add frontmatter type or a path mapping)"]
    return []


def check_knowledge_docs(root: Path) -> list[str]:
    """Problems as sorted `path:line: reason` lines; an empty list means clean."""
    problems = []
    for rel in _docs(root):
        problems += _doc_problems(root, rel)
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
