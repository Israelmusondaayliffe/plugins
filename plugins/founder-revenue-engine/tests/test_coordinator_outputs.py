#!/usr/bin/env python3
"""Test every coordinator output contract in this plugin."""

from __future__ import annotations

import json
import contextlib
import importlib.util
import io
import subprocess
import tempfile
import unittest
from unittest import mock
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
SPEC = json.loads((ROOT / "bundle-spec.json").read_text(encoding="utf-8"))


class CoordinatorOutputTests(unittest.TestCase):
    def test_release_version_and_optional_companions(self) -> None:
        versions = {
            json.loads(
                (ROOT / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8")
            )["version"],
            json.loads(
                (ROOT / ".codex-plugin" / "plugin.json").read_text(encoding="utf-8")
            )["version"],
            SPEC["version"],
        }
        self.assertEqual(versions, {"0.2.2"})
        expected = {
            "sales",
            "creative-production",
            "gmail",
            "google-calendar",
            "canva",
            "writing-quality",
            "brand-world-studio",
            "strategy-room",
        }
        self.assertEqual({item["name"] for item in SPEC["companions"]}, expected)
        self.assertTrue(all(item["required"] is False for item in SPEC["companions"]))

    def test_zero_companion_preflight_stays_valid(self) -> None:
        module_path = ROOT / "scripts" / "check_companions.py"
        spec = importlib.util.spec_from_file_location("founder_revenue_companions", module_path)
        self.assertIsNotNone(spec)
        self.assertIsNotNone(spec.loader)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        completed = subprocess.CompletedProcess(
            ["codex", "plugin", "list", "--json"],
            0,
            stdout=json.dumps({"installed": []}),
            stderr="",
        )
        output = io.StringIO()
        with mock.patch.object(module.subprocess, "run", return_value=completed):
            with contextlib.redirect_stdout(output):
                result = module.main()
        report = json.loads(output.getvalue())
        self.assertEqual(result, 0)
        self.assertTrue(report["valid"])
        self.assertEqual(report["required_failures"], [])
        self.assertTrue(all(not item["available"] for item in report["companions"]))

    def test_local_copy_checks_replace_missing_writing_quality(self) -> None:
        checks = (
            ROOT
            / "skills"
            / "founder-revenue-router"
            / "references"
            / "commercial-copy-checks.md"
        ).read_text(encoding="utf-8")
        market = (
            ROOT / "skills" / "market-narrative-builder" / "SKILL.md"
        ).read_text(encoding="utf-8")
        outreach = (
            ROOT / "skills" / "outreach-sequence-builder" / "SKILL.md"
        ).read_text(encoding="utf-8")
        for phrase in (
            "Trace every result, number, customer statement, credential, and comparison",
            "Do not present an assumption as a customer fact",
            "Use personalization only when a named source supports it",
            "Remove prohibited claims",
            "no external action has been authorized by drafting alone",
        ):
            self.assertIn(phrase, checks)
        self.assertIn("plugin-owned commercial-copy checks", market)
        self.assertIn("plugin-owned commercial-copy checks", outreach)

    def test_local_commercial_decision_gap_is_complete(self) -> None:
        router = (
            ROOT / "skills" / "founder-revenue-router" / "SKILL.md"
        ).read_text(encoding="utf-8")
        market = (
            ROOT / "skills" / "market-narrative-builder" / "SKILL.md"
        ).read_text(encoding="utf-8")
        for phrase in (
            "Strategy Room is absent",
            "local commercial-decision gap",
            "evidence",
            "assumptions",
            "open questions",
            "prohibited claims",
            "exact next decision",
            "Stop before",
        ):
            self.assertIn(phrase, router)
            self.assertIn(phrase, market)

    def test_templates_pass(self) -> None:
        for name in SPEC["coordinator_skills"]:
            skill = ROOT / "skills" / name
            result = subprocess.run(
                ["python3", str(skill / "scripts/validate_output.py"), str(skill / "assets/output-template.json")],
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 0, f"{name}: {result.stdout}{result.stderr}")

    def test_empty_artifacts_fail(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            artifact = Path(temporary_directory) / "empty.json"
            artifact.write_text("{}\n", encoding="utf-8")
            for name in SPEC["coordinator_skills"]:
                skill = ROOT / "skills" / name
                result = subprocess.run(
                    ["python3", str(skill / "scripts/validate_output.py"), str(artifact)],
                    check=False,
                    capture_output=True,
                    text=True,
                )
                self.assertNotEqual(result.returncode, 0, f"{name} accepted an empty artifact")


if __name__ == "__main__":
    unittest.main()
