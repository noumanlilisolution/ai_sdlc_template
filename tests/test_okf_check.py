"""The knowledge-docs check (spec #3), tested through its one seam: repo root in, problem lines out."""

from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from typing import Dict, Union

from scripts.okf_check import check_knowledge_docs

Files = Dict[str, Union[str, bytes]]
SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "okf_check.py"


class Repo:
    """A throwaway repo holding only the files one test needs."""

    def __init__(self, files: Files) -> None:
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


def check(files: Files) -> list[str]:
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


class FrontmatterType(unittest.TestCase):
    def test_a_frontmatter_type_overrides_the_path_default(self) -> None:
        self.assertEqual(check({"docs/adr/0001-x.md": "---\ntype: Hub\n---\n# X\n"}), [])

    def test_a_frontmatter_type_gives_an_unmapped_doc_its_type(self) -> None:
        self.assertEqual(check({"context/roadmap.md": "---\ntype: Architecture\n---\n"}), [])

    def test_an_unknown_type_fails_on_the_line_of_the_type_key(self) -> None:
        self.assertEqual(
            check({"context/requirements.md": "---\ntitle: R\ntype: Roadmap\n---\n"}),
            ["context/requirements.md:3: unknown type 'Roadmap'"],
        )

    def test_type_matching_is_exact(self) -> None:
        self.assertEqual(
            check({"context/README.md": "---\ntype: hub\n---\n"}),
            ["context/README.md:2: unknown type 'hub'"],
        )

    def test_frontmatter_without_a_type_keeps_the_path_default(self) -> None:
        self.assertEqual(check({"GLOSSARY.md": "---\ntitle: Glossary\n---\n"}), [])


class InvalidFrontmatter(unittest.TestCase):
    def test_a_missing_closing_fence_is_invalid_on_line_1(self) -> None:
        self.assertEqual(
            check({"GLOSSARY.md": "---\ntype: Glossary\n# Glossary\n"}),
            ["GLOSSARY.md:1: invalid frontmatter"],
        )

    def test_a_top_level_line_that_is_not_a_key_is_invalid(self) -> None:
        self.assertEqual(
            check({"GLOSSARY.md": "---\ntype: Glossary\njust some words\n---\n"}),
            ["GLOSSARY.md:3: invalid frontmatter"],
        )

    def test_a_duplicate_key_is_invalid_on_its_second_line(self) -> None:
        self.assertEqual(
            check({"GLOSSARY.md": "---\ntype: Glossary\ntitle: A\ntype: Hub\n---\n"}),
            ["GLOSSARY.md:4: invalid frontmatter"],
        )

    def test_an_empty_type_is_invalid(self) -> None:
        self.assertEqual(
            check({"GLOSSARY.md": "---\ntype:\n---\n"}),
            ["GLOSSARY.md:2: invalid frontmatter"],
        )

    def test_a_parse_failure_never_prints_file_content(self) -> None:
        problems = check({"GLOSSARY.md": "---\npassword hunter2 leaked\n---\n"})
        self.assertEqual(problems, ["GLOSSARY.md:2: invalid frontmatter"])
        self.assertNotIn("hunter2", "".join(problems))


class FrontmatterTolerance(unittest.TestCase):
    def test_bom_and_crlf_line_endings_parse(self) -> None:
        text = "\ufeff---\r\ntype: Hub\r\n---\r\n# Doc\r\n".encode("utf-8")
        self.assertEqual(check({"context/roadmap.md": text}), [])

    def test_a_doc_that_is_not_utf8_fails_without_printing_it(self) -> None:
        self.assertEqual(
            check({"GLOSSARY.md": b"---\ntype: Glossary \xff\xfe\n---\n"}),
            ["GLOSSARY.md:1: not UTF-8 text"],
        )

    def test_blank_and_comment_lines_are_allowed(self) -> None:
        self.assertEqual(check({"GLOSSARY.md": "---\n\n# a comment\ntype: Glossary\n---\n"}), [])

    def test_matching_quotes_around_a_value_are_removed(self) -> None:
        self.assertEqual(
            check({"context/roadmap.md": "---\ntype: \"Architecture\"\ntitle: 'R'\n---\n"}), []
        )

    def test_a_value_splits_on_the_first_colon_only(self) -> None:
        self.assertEqual(
            check({"GLOSSARY.md": "---\ntitle: Terms: the full list\ntype: Glossary\n---\n"}), []
        )

    def test_okf_nested_fields_are_skipped(self) -> None:
        text = (
            "---\n"
            "type: Decision\n"
            "generated: { by: agent, at: 2026-08-21T00:00:00+00:00 }\n"
            "sources:\n"
            "  - resource: bq://p.d.t\n"
            "    id: s1\n"
            "verified:\n"
            "  by: someone\n"
            "tags:\n"
            "- okf\n"
            "---\n"
        )
        self.assertEqual(check({"docs/adr/0001-x.md": text}), [])

    def test_an_empty_block_is_valid(self) -> None:
        self.assertEqual(check({"GLOSSARY.md": "---\n---\n# Glossary\n"}), [])

    def test_a_doc_without_frontmatter_is_valid(self) -> None:
        self.assertEqual(check({"GLOSSARY.md": "# Glossary\n\n---\n\ntext\n"}), [])


ADR = "docs/adr/0001-x.md"


class IdsAndRelated(unittest.TestCase):
    def test_related_ids_resolve_across_folders(self) -> None:
        self.assertEqual(
            check(
                {
                    ADR: "---\nid: adr-0001\nrelated: [glossary, req-2]\n---\n",
                    "GLOSSARY.md": "---\nid: glossary\n---\n",
                    "context/requirements.md": "---\nid: req-2\nrelated:\n- adr-0001\n---\n",
                }
            ),
            [],
        )

    def test_an_indented_related_block_list_is_read(self) -> None:
        self.assertEqual(
            check({ADR: "---\nid: adr-0001\nrelated:\n  - missing-one\n---\n"}),
            [f"{ADR}:4: related id 'missing-one' not found"],
        )

    def test_an_unresolved_id_in_a_flow_list_fails_on_the_related_line(self) -> None:
        self.assertEqual(
            check({ADR: "---\ntype: Decision\nrelated: [\"nope\", glossary]\n---\n",
                   "GLOSSARY.md": "---\nid: glossary\n---\n"}),
            [f"{ADR}:3: related id 'nope' not found"],
        )

    def test_an_id_that_is_not_lower_kebab_case_fails(self) -> None:
        for bad in ("ADR-1", "adr_1", "adr--1", "-adr", "adr-"):
            with self.subTest(bad=bad):
                self.assertEqual(
                    check({ADR: f"---\nid: {bad}\n---\n"}),
                    [f"{ADR}:2: id '{bad}' is not lower-kebab-case"],
                )

    def test_a_duplicate_id_fails_on_every_file_that_declares_it(self) -> None:
        self.assertEqual(
            check({ADR: "---\nid: same\n---\n", "GLOSSARY.md": "---\n\nid: same\n---\n"}),
            [
                "GLOSSARY.md:3: duplicate id 'same' (also in docs/adr/0001-x.md)",
                f"{ADR}:2: duplicate id 'same' (also in GLOSSARY.md)",
            ],
        )

    def test_an_empty_id_is_invalid_frontmatter(self) -> None:
        self.assertEqual(check({ADR: "---\nid: ''\n---\n"}), [f"{ADR}:2: invalid frontmatter"])

    def test_a_scalar_related_value_is_invalid_frontmatter(self) -> None:
        self.assertEqual(
            check({ADR: "---\nrelated: glossary\n---\n"}), [f"{ADR}:2: invalid frontmatter"]
        )


class CommandLine(unittest.TestCase):
    def run_cli(self, files: Files) -> subprocess.CompletedProcess[str]:
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
