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
    "canva",
    "creative-production",
    "strategy-room",
    "writing-quality",
}
APPROVED_INSTRUCTIONAL_PATHS = [
    "skills/gpt-image-2-unified/agents/agent-narrative.md",
    "skills/gpt-image-2-unified/agents/agent-search.md",
    "skills/nano-banana-unified/agents/agent-grid.md",
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

    def test_local_positioning_fallback_is_complete(self) -> None:
        required = {
            "README.md": [
                "<approved-output-root>/brand-world-studio/positioning-gap.md",
                "known context, missing decisions, unsupported claims, evidence boundaries, and exact next decision",
            ],
            "skills/brand-world-router/SKILL.md": [
                "Local positioning fallback",
                "Stop after the positioning-gap handoff",
            ],
            "skills/brand-world-router/references/workflow.md": [
                "positioning-gap handoff",
                "stop without inventing strategy",
            ],
        }
        for relative, phrases in required.items():
            text = (ROOT / relative).read_text(encoding="utf-8")
            for phrase in phrases:
                self.assertIn(phrase, text, f"{relative} lacks {phrase!r}")

    def test_owned_path_survives_without_companions(self) -> None:
        phrase = "owned visual brief, prompt-pack, brandkit, and consistency-review path"
        for relative in (
            "README.md",
            "skills/brand-world-router/SKILL.md",
            "skills/brand-world-router/references/workflow.md",
        ):
            self.assertIn(phrase, (ROOT / relative).read_text(encoding="utf-8"), relative)

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
        self.assertEqual(codex["version"], "0.2.1")


if __name__ == "__main__":
    unittest.main()
