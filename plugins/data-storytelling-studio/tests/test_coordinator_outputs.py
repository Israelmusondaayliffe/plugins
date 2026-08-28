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
        self.assertEqual(versions, {"0.2.1"})
        self.assertTrue(SPEC["companions"])
        self.assertTrue(all(item["required"] is False for item in SPEC["companions"]))

    def test_zero_companion_preflight_stays_valid(self) -> None:
        module_path = ROOT / "scripts" / "check_companions.py"
        spec = importlib.util.spec_from_file_location("data_story_companions", module_path)
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

    def test_required_companions_are_production_needs_with_local_fallback(self) -> None:
        route = json.loads(
            (
                ROOT
                / "skills"
                / "analysis-to-story-router"
                / "assets"
                / "output-template.json"
            ).read_text(encoding="utf-8")
        )
        optional = {item["name"] for item in SPEC["companions"] if not item["required"]}
        self.assertTrue(set(route["required_companions"]).issubset(optional))
        skill = (
            ROOT / "skills" / "analysis-to-story-router" / "SKILL.md"
        ).read_text(encoding="utf-8")
        for phrase in (
            "does not prove installation or create a hard runtime dependency",
            "self-contained local Markdown or JSON story brief",
            "source artifact paths",
            "evidence limits",
            "Mark unsupported production or publication incomplete",
            "Stop before claiming",
        ):
            self.assertIn(phrase, skill)

    def test_templates_pass(self) -> None:
        for name in SPEC["coordinator_skills"]:
            skill = ROOT / "skills" / name
            command = [
                "python3",
                str(skill / "scripts/validate_output.py"),
                str(skill / "assets/output-template.json"),
            ]
            result = subprocess.run(
                command, capture_output=True, text=True, check=False
            )
            self.assertEqual(result.returncode, 0, f"{name}: {result.stdout}{result.stderr}")

    def test_empty_artifacts_fail(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            artifact = Path(temporary_directory) / "empty.json"
            artifact.write_text("{}\n", encoding="utf-8")
            for name in SPEC["coordinator_skills"]:
                skill = ROOT / "skills" / name
                command = [
                    "python3",
                    str(skill / "scripts/validate_output.py"),
                    str(artifact),
                ]
                result = subprocess.run(
                    command, capture_output=True, text=True, check=False
                )
                self.assertNotEqual(result.returncode, 0, f"{name} accepted an empty artifact")


if __name__ == "__main__":
    unittest.main()
