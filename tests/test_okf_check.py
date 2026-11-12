"""The knowledge-docs check (spec #3), tested through its one seam: repo root in, problem lines out."""

from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from scripts.okf_check import check_knowledge_docs

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "okf_check.py"


class Repo:
    """A throwaway repo holding only the files one test needs."""

    def __init__(self, files: dict[str, str | bytes]) -> None:
        self._dir = tempfile.TemporaryDirectory()
        self.root = Path(self._dir.name)
        for rel, content in files.items():
            path = self.root / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            if isinstance(content, bytes):
                path.write_bytes(content)
            else:
                path.write_text(content, encoding="utf-8", newline="")

    def check(self) -> list[str]:
        return check_knowledge_docs(self.root)

    def close(self) -> None:
        self._dir.cleanup()


def check(files: dict[str, str | bytes]) -> list[str]:
    repo = Repo(files)
    try:
        return repo.check()
    finally:
        repo.close()


class PathDefaultTypes(unittest.TestCase):
    def test_a_doc_in_scope_with_no_path_default_fails_with_no_type(self) -> None:
        self.assertEqual(
            check({"context/roadmap.md": "# Roadmap\n"}),
            ["context/roadmap.md:1: no type (add frontmatter type or a path mapping)"],
        )

    def test_every_path_default_in_the_spec_passes(self) -> None:
        mapped = [
            "context/business_context.md",
            "context/requirements.md",
            "context/constraints.md",
            "context/assumptions.md",
            "context/technical_architecture.md",
            "context/README.md",
            "context/decisions.md",
            "context/domain_glossary.md",
            "context/readiness/readiness_checklist.md",
            "docs/adr/0001-some-decision.md",
            ".out-of-scope/some-idea.md",
            "GLOSSARY.md",
        ]
        self.assertEqual(check({path: "# Doc\n" for path in mapped}), [])

    def test_files_outside_scope_are_not_checked(self) -> None:
        self.assertEqual(
            check(
                {
                    "docs/adr/old/roadmap.md": "# nested: not in scope\n",
                    "docs/guide.md": "# not a knowledge doc\n",
                    "context/notes.txt": "not markdown\n",
                }
            ),
            [],
        )

    def test_problems_are_sorted_by_path(self) -> None:
        self.assertEqual(
            check({"context/zeta.md": "", "context/alpha.md": ""}),
            [
                "context/alpha.md:1: no type (add frontmatter type or a path mapping)",
                "context/zeta.md:1: no type (add frontmatter type or a path mapping)",
            ],
        )


class CommandLine(unittest.TestCase):
    def run_cli(self, files: dict[str, str | bytes]) -> subprocess.CompletedProcess[str]:
        repo = Repo(files)
        self.addCleanup(repo.close)
        return subprocess.run(
            [sys.executable, str(SCRIPT), str(repo.root)],
            capture_output=True,
            text=True,
            check=False,
        )

    def test_clean_run_exits_0_and_counts_the_docs(self) -> None:
        result = self.run_cli({"GLOSSARY.md": "# G\n", "context/requirements.md": "# R\n"})
        self.assertEqual((result.returncode, result.stdout), (0, "okf bundle: 2 docs ok\n"))

    def test_problems_exit_1_and_print_one_line_each(self) -> None:
        result = self.run_cli({"context/roadmap.md": "# R\n"})
        self.assertEqual(
            (result.returncode, result.stdout),
            (1, "context/roadmap.md:1: no type (add frontmatter type or a path mapping)\n"),
        )


if __name__ == "__main__":
    unittest.main()
