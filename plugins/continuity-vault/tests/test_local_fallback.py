#!/usr/bin/env python3
"""Test the bounded local recall and direct-digest fallback."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "skills" / "continuity-router" / "scripts" / "local_fallback.py"
AUTHORITY = "The current task explicitly authorized this temporary workspace root."


def run_fallback(*arguments: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *arguments],
        check=False,
        capture_output=True,
        text=True,
    )


class LocalFallbackTests(unittest.TestCase):
    def test_release_version_and_optional_companions(self) -> None:
        bundle = json.loads((ROOT / "bundle-spec.json").read_text(encoding="utf-8"))
        claude = json.loads((ROOT / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8"))
        codex = json.loads((ROOT / ".codex-plugin" / "plugin.json").read_text(encoding="utf-8"))
        self.assertEqual({bundle["version"], claude["version"], codex["version"]}, {"0.2.2"})
        self.assertTrue(bundle["companions"])
        self.assertTrue(all(item["required"] is False for item in bundle["companions"]))
        self.assertIn("notion", {item["name"] for item in bundle["companions"]})
        self.assertIn("google-drive", {item["name"] for item in bundle["companions"]})

    def test_search_stays_inside_authorized_root_and_records_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            temporary = Path(temporary_directory)
            workspace = temporary / "workspace"
            workspace.mkdir()
            evidence = workspace / "evidence.md"
            evidence.write_text("Decision: keep the local fallback bounded.\n", encoding="utf-8")
            outside = temporary / "outside.md"
            outside.write_text("Decision: this file is outside authority.\n", encoding="utf-8")
            (workspace / "outside-link.md").symlink_to(outside)
            result = run_fallback(
                "search",
                "--root",
                str(workspace),
                "--authority",
                AUTHORITY,
                "--query",
                "Decision",
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            report = json.loads(result.stdout)
            self.assertEqual(report["evidence_status"], "matches-found")
            self.assertEqual(report["query"], "Decision")
            self.assertEqual(report["roots_searched"], [str(workspace.resolve())])
            self.assertEqual([item["path"] for item in report["matches"]], [str(evidence.resolve())])
            self.assertEqual(report["authority_checks"][0]["authority_statement"], AUTHORITY)
            self.assertFalse(report["write_performed"])

    def test_empty_search_returns_honest_no_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            workspace = Path(temporary_directory) / "workspace"
            workspace.mkdir()
            (workspace / "notes.md").write_text("No matching phrase lives here.\n", encoding="utf-8")
            result = run_fallback(
                "search",
                "--root",
                str(workspace),
                "--authority",
                AUTHORITY,
                "--query",
                "missing-decision",
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            report = json.loads(result.stdout)
            self.assertEqual(report["evidence_status"], "no-evidence")
            self.assertEqual(report["matches"], [])
            self.assertTrue(report["search_complete"])

    def test_search_rejects_broad_root(self) -> None:
        result = run_fallback(
            "search",
            "--root",
            "/",
            "--authority",
            AUTHORITY,
            "--query",
            "anything",
        )
        self.assertEqual(result.returncode, 2)
        self.assertIn("refusing broad root", result.stderr)

    def test_search_rejects_symlink_root(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            temporary = Path(temporary_directory)
            workspace = temporary / "workspace"
            workspace.mkdir()
            linked_workspace = temporary / "workspace-link"
            linked_workspace.symlink_to(workspace, target_is_directory=True)
            result = run_fallback(
                "search",
                "--root",
                str(linked_workspace),
                "--authority",
                AUTHORITY,
                "--query",
                "anything",
            )
            self.assertEqual(result.returncode, 2)
            self.assertIn("authorized root cannot be a symlink", result.stderr)

    def test_file_limit_cannot_claim_no_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            workspace = Path(temporary_directory) / "workspace"
            workspace.mkdir()
            (workspace / "a.md").write_text("First file.\n", encoding="utf-8")
            (workspace / "b.md").write_text("The missing-decision is here.\n", encoding="utf-8")
            result = run_fallback(
                "search",
                "--root",
                str(workspace),
                "--authority",
                AUTHORITY,
                "--query",
                "missing-decision",
                "--max-files",
                "1",
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            report = json.loads(result.stdout)
            self.assertEqual(report["evidence_status"], "search-incomplete")
            self.assertTrue(report["file_limit_reached"])
            self.assertFalse(report["search_complete"])

    def test_skipped_content_cannot_claim_no_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            workspace = Path(temporary_directory) / "workspace"
            workspace.mkdir()
            (workspace / "binary.bin").write_bytes(b"\xff\xfe\xfd")
            result = run_fallback(
                "search",
                "--root",
                str(workspace),
                "--authority",
                AUTHORITY,
                "--query",
                "missing-decision",
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            report = json.loads(result.stdout)
            self.assertEqual(report["evidence_status"], "search-incomplete")
            self.assertEqual(report["skipped_files"]["non-utf8"], 1)
            self.assertFalse(report["search_complete"])

    def test_exact_file_limit_can_finish_with_no_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            workspace = Path(temporary_directory) / "workspace"
            workspace.mkdir()
            (workspace / "only.md").write_text("No match.\n", encoding="utf-8")
            result = run_fallback(
                "search",
                "--root",
                str(workspace),
                "--authority",
                AUTHORITY,
                "--query",
                "missing-decision",
                "--max-files",
                "1",
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            report = json.loads(result.stdout)
            self.assertEqual(report["evidence_status"], "no-evidence")
            self.assertFalse(report["file_limit_reached"])
            self.assertTrue(report["search_complete"])

    def test_match_limit_reports_search_incomplete(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            workspace = Path(temporary_directory) / "workspace"
            workspace.mkdir()
            (workspace / "matches.md").write_text(
                "Decision one.\nDecision two.\n",
                encoding="utf-8",
            )
            result = run_fallback(
                "search",
                "--root",
                str(workspace),
                "--authority",
                AUTHORITY,
                "--query",
                "Decision",
                "--max-matches",
                "1",
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            report = json.loads(result.stdout)
            self.assertEqual(report["evidence_status"], "search-incomplete")
            self.assertTrue(report["match_limit_reached"])
            self.assertFalse(report["search_complete"])

    def test_digest_is_source_bound_and_uses_no_writing_companion(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            workspace = Path(temporary_directory) / "workspace"
            workspace.mkdir()
            source = workspace / "decision.md"
            source.write_text("# Decision\n\nKeep source files authoritative.\n", encoding="utf-8")
            result = run_fallback(
                "digest",
                "--root",
                str(workspace),
                "--authority",
                AUTHORITY,
                "--source",
                str(source),
                "--audience",
                "A fresh task",
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            report = json.loads(result.stdout)
            self.assertEqual(report["evidence_status"], "evidence-found")
            self.assertFalse(report["writing_companion_used"])
            self.assertFalse(report["write_performed"])
            self.assertEqual(report["digest_entries"][0]["path"], str(source.resolve()))
            self.assertEqual(
                report["digest_entries"][0]["sha256"],
                hashlib.sha256(source.read_bytes()).hexdigest(),
            )
            self.assertEqual(
                [item["text"] for item in report["digest_entries"][0]["excerpts"]],
                ["# Decision", "Keep source files authoritative."],
            )

    def test_digest_rejects_source_outside_authorized_root(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            temporary = Path(temporary_directory)
            workspace = temporary / "workspace"
            workspace.mkdir()
            outside = temporary / "outside.md"
            outside.write_text("Outside authority.\n", encoding="utf-8")
            result = run_fallback(
                "digest",
                "--root",
                str(workspace),
                "--authority",
                AUTHORITY,
                "--source",
                str(outside),
                "--audience",
                "A fresh task",
            )
            self.assertEqual(result.returncode, 2)
            self.assertIn("source is outside authorized roots", result.stderr)

    def test_empty_digest_returns_honest_no_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            workspace = Path(temporary_directory) / "workspace"
            workspace.mkdir()
            source = workspace / "empty.md"
            source.write_text("\n\n", encoding="utf-8")
            result = run_fallback(
                "digest",
                "--root",
                str(workspace),
                "--authority",
                AUTHORITY,
                "--source",
                str(source),
                "--audience",
                "A fresh task",
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            report = json.loads(result.stdout)
            self.assertEqual(report["evidence_status"], "no-evidence")
            self.assertEqual(report["digest_entries"][0]["excerpts"], [])


if __name__ == "__main__":
    unittest.main()
