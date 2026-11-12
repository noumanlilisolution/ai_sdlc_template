"""The knowledge-docs check: every knowledge doc has a known type and its references resolve.

    python scripts/okf_check.py [repo-root]

Enforces requirement F2 (context/requirements.md); the rules are in spec #3 and the README's
"Knowledge docs" section. Standard library only and Python 3.9-safe, like scripts/check.py.
"""

from __future__ import annotations

import os
import posixpath
import re
import sys
from pathlib import Path
from typing import Iterator, Optional, Tuple
from urllib.parse import unquote

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
ID_RE = re.compile(r"[a-z0-9]+(-[a-z0-9]+)*\Z")

SCHEME_RE = re.compile(r"[A-Za-z][A-Za-z0-9+.-]*:")  # http:, mailto:, ...: not a file link
FENCE_RE = re.compile(r" {0,3}(`{3,}|~{3,})")
INLINE_CODE_RE = re.compile(r"(`+).*?\1")
INLINE_LINK_RE = re.compile(  # ](target) or ](target "title"); also matches image links
    r"\]\(\s*(<[^>]*>|[^\s)]+)(?:\s+(?:\"[^\"]*\"|'[^']*'|\([^)]*\)))?\s*\)"
)
REF_DEF_RE = re.compile(r" {0,3}\[[^\]]+\]:\s*(<[^>]*>|\S+)")  # [ref]: target


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


class Frontmatter:
    """What the check reads from a doc's frontmatter block, each value with its file line."""

    def __init__(self) -> None:
        self.fields: dict[str, tuple[str, int]] = {}
        self.related: list[tuple[str, int]] = []


def _flow_list(value: str, number: int) -> list[tuple[str, int]]:
    """`[a, "b"]` as (item, line) pairs; anything else is invalid."""
    if not (value.startswith("[") and value.endswith("]")):
        raise Invalid(number)
    items = [_unquote(item.strip()) for item in value[1:-1].split(",")]
    return [(item, number) for item in items if item]


def _frontmatter(text: str) -> Frontmatter:
    """Read the frontmatter block's top-level keys and its `related:` ids.

    Only top-level keys are read. Indented lines, and `- item` lines under a bare `key:`,
    belong to the key above them and are skipped, so OKF's nested fields pass. Under a bare
    `related:` they must be `- id` items, indented or not.
    """
    found = Frontmatter()
    lines = text.lstrip("\ufeff").splitlines()
    if not lines or lines[0].rstrip() != "---":
        return found
    end = next((i for i in range(1, len(lines)) if lines[i].rstrip() == "---"), None)
    if end is None:
        raise Invalid(1)
    key: Optional[str] = None  # the last top-level key; None before the first
    bare = False  # whether that key had no value on its own line
    for number, line in enumerate(lines[1:end], start=2):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        indented = line[0] in " \t"
        item = stripped == "-" or stripped.startswith("- ")
        if indented or item:
            if key is None or (item and not indented and not bare):
                raise Invalid(number)
            if key == "related":
                related_id = _unquote(stripped[1:].strip()) if item else ""
                if not related_id:
                    raise Invalid(number)
                found.related.append((related_id, number))
            continue
        match = KEY_RE.match(line.rstrip())
        if match is None or match.group(1) in found.fields:
            raise Invalid(number)
        key, raw = match.group(1), match.group(2).strip()
        bare = raw == ""
        value = _unquote(raw)
        if key in ("type", "id") and not value:
            raise Invalid(number)
        if key == "related" and not bare:
            found.related = _flow_list(raw, number)
        found.fields[key] = (value, number)
    return found


Problem = Tuple[str, int, str]  # (path, line, reason)


def _link_targets(text: str) -> Iterator[tuple[int, str]]:
    """(line, target) of each inline, image and reference-definition link outside code."""
    fence = ""  # the open code fence (``` or ~~~ run); empty when outside one
    for number, line in enumerate(text.lstrip("\ufeff").splitlines(), start=1):
        stripped = line.strip()
        if fence:
            if stripped and set(stripped) == {fence[0]} and len(stripped) >= len(fence):
                fence = ""
            continue
        opener = FENCE_RE.match(line)
        if opener:
            fence = opener.group(1)
            continue
        line = INLINE_CODE_RE.sub("", line)
        definition = REF_DEF_RE.match(line)
        if definition:
            yield number, definition.group(1)
            continue
        for link in INLINE_LINK_RE.finditer(line):
            yield number, link.group(1)


def _exists_exactly(root: Path, rel: str) -> bool:
    """Whether the repo-relative path exists with this exact case, on any OS."""
    current = root
    for part in rel.split("/"):
        try:
            names = os.listdir(current)
        except OSError:
            return False
        if part not in names:
            return False
        current = current / part
    return True


def _link_problem(root: Path, rel: str, raw: str) -> Optional[str]:
    """Why a link target does not resolve, or None when it does or is not a file link."""
    target = raw[1:-1] if raw.startswith("<") and raw.endswith(">") else raw
    if SCHEME_RE.match(target):
        return None
    path = unquote(re.split(r"[?#]", target, maxsplit=1)[0])
    if not path:
        return None  # a same-page #anchor
    if path.startswith("/"):
        joined = path.lstrip("/")  # repo root: the repo is not one OKF bundle
    else:
        joined = posixpath.join(posixpath.dirname(rel), path)
    resolved = posixpath.normpath(joined)
    if resolved == ".." or resolved.startswith("../"):
        return f"link '{target}' leaves the repo"
    if resolved != "." and not _exists_exactly(root, resolved):
        return f"broken link '{target}'"
    return None


def _link_problems(root: Path, rel: str, text: str) -> list[Problem]:
    problems = []
    for line, raw in _link_targets(text):
        reason = _link_problem(root, rel, raw)
        if reason:
            problems.append((rel, line, reason))
    return problems


def _read(root: Path, rel: str) -> tuple[list[Problem], Optional[Frontmatter]]:
    """The problems a doc has on its own, and its frontmatter when it could be read."""
    try:
        text = (root / rel).read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return [(rel, 1, "not UTF-8 text")], None
    problems = _link_problems(root, rel, text)
    try:
        found = _frontmatter(text)
    except Invalid as error:
        return [*problems, (rel, error.line, "invalid frontmatter")], None
    if "type" in found.fields:
        doc_type, line = found.fields["type"]
        if doc_type not in KNOWN_TYPES:
            problems.append((rel, line, f"unknown type '{doc_type}'"))
    elif _default_type(rel) is None:
        problems.append((rel, 1, "no type (add frontmatter type or a path mapping)"))
    if "id" in found.fields:
        doc_id, line = found.fields["id"]
        if not ID_RE.match(doc_id):
            problems.append((rel, line, f"id '{doc_id}' is not lower-kebab-case"))
    return problems, found


def check_knowledge_docs(root: Path) -> list[str]:
    """Problems as sorted `path:line: reason` lines; an empty list means clean."""
    problems: list[Problem] = []
    declared: dict[str, list[tuple[str, int]]] = {}  # id -> (path, line) of each declaration
    related: list[tuple[str, str, int]] = []  # (path, id, line) of each related: entry
    for rel in _docs(root):
        own, found = _read(root, rel)
        problems += own
        if found is None:
            continue
        if "id" in found.fields:
            doc_id, line = found.fields["id"]
            declared.setdefault(doc_id, []).append((rel, line))
        related += [(rel, related_id, line) for related_id, line in found.related]
    for doc_id, places in declared.items():
        for rel, line in places if len(places) > 1 else []:
            others = ", ".join(other for other, _ in places if other != rel)
            problems.append((rel, line, f"duplicate id '{doc_id}' (also in {others})"))
    for rel, related_id, line in related:
        if related_id not in declared:
            problems.append((rel, line, f"related id '{related_id}' not found"))
    return [f"{rel}:{line}: {reason}" for rel, line, reason in sorted(problems)]


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
