#!/usr/bin/env python3
"""Test every coordinator output contract in this plugin."""

from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
SPEC = json.loads((ROOT / "bundle-spec.json").read_text(encoding="utf-8"))
EXPECTED_COMPANIONS = {
    "continuity-vault",
    "knowledge-work-superpowers",
    "outcome-engine",
    "proofloop",
    "writing-quality",
}
APPROVED_INSTRUCTIONAL_PATHS = [
    "skills/assumption-challenger/SKILL.md",
    "skills/assumption-challenger/agents/challenger.md",
    "skills/assumption-challenger/agents/synthesizer.md",
    "skills/assumption-challenger/agents/verifier.md",
    "skills/assumption-challenger/references/analysis_frameworks.md",
    "skills/assumption-challenger/references/verification_protocol.md",
    "skills/decision-wayfinder/SKILL.md",
]


class CoordinatorOutputTests(unittest.TestCase):
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

    def test_companions_are_optional(self) -> None:
        companions = SPEC["companions"]
        self.assertEqual({item["name"] for item in companions}, EXPECTED_COMPANIONS)
        self.assertTrue(all(item.get("required") is False for item in companions))

    def test_local_fallback_contract_is_complete(self) -> None:
        required = {
            "README.md": [
                "self-contained execution brief or decision handoff",
                "<approved-output-root>/strategy-room/decision-map.md",
            ],
            "skills/strategy-room-router/SKILL.md": [
                "Local fallback contract",
                "<approved-output-root>/strategy-room/execution-handoff.md",
                "Stop before execution",
            ],
            "skills/strategy-room-router/references/workflow.md": [
                "optional companions",
                "<approved-output-root>/strategy-room/decision-map.md",
            ],
            "skills/decision-wayfinder/SKILL.md": [
                "Continuity Vault is optional",
                "<approved-output-root>/strategy-room/execution-handoff.md",
            ],
        }
        for relative, phrases in required.items():
            text = (ROOT / relative).read_text(encoding="utf-8")
            for phrase in phrases:
                self.assertIn(phrase, text, f"{relative} lacks {phrase!r}")

    def test_approved_instructional_paths_have_no_unicode_dashes(self) -> None:
        for relative in APPROVED_INSTRUCTIONAL_PATHS:
            text = (ROOT / relative).read_text(encoding="utf-8")
            self.assertNotIn("\u2014", text, relative)
            self.assertNotIn("\u2013", text, relative)

    def test_manifest_versions_match(self) -> None:
        claude = json.loads((ROOT / ".claude-plugin/plugin.json").read_text(encoding="utf-8"))
        codex = json.loads((ROOT / ".codex-plugin/plugin.json").read_text(encoding="utf-8"))
        self.assertEqual(claude["name"], codex["name"])
        self.assertEqual(claude["version"], codex["version"])
        self.assertEqual(codex["version"], SPEC["version"])
        self.assertEqual(codex["version"], "0.2.2")


if __name__ == "__main__":
    unittest.main()
