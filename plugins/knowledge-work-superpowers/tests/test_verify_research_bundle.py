#!/usr/bin/env python3
"""Tests for the research-bundle verifier."""

from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path


PLUGIN_ROOT = Path(__file__).parents[1]
SCRIPT_PATH = PLUGIN_ROOT / "scripts" / "verify_research_bundle.py"
SPEC = importlib.util.spec_from_file_location("verify_research_bundle", SCRIPT_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"Could not load {SCRIPT_PATH}")
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class VerifyResearchBundleTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory(prefix="research-bundle-test-")
        self.bundle = Path(self.temp_dir.name) / "bundle"
        MODULE.write_valid_fixture(self.bundle)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_valid_research_bundle_passes(self) -> None:
        self.assertEqual(MODULE.validate_bundle(self.bundle, "research"), [])

    def test_placeholder_is_rejected(self) -> None:
        (self.bundle / "work-brief.md").write_text("# Work Brief\n\nTBD\n", encoding="utf-8")
        findings = MODULE.validate_bundle(self.bundle, "research")
        self.assertTrue(any("placeholder" in finding.message for finding in findings))

    def test_unknown_source_id_is_rejected(self) -> None:
        claim_path = self.bundle / "claim-ledger.md"
        content = claim_path.read_text(encoding="utf-8").replace("S1 | high", "S404 | high")
        claim_path.write_text(content, encoding="utf-8")
        findings = MODULE.validate_bundle(self.bundle, "research")
        self.assertTrue(any("unknown source ID 'S404'" in finding.message for finding in findings))

    def test_deliverable_profile_requires_delivery_files(self) -> None:
        findings = MODULE.validate_bundle(self.bundle, "deliverable")
        missing = {finding.path.name for finding in findings if finding.message == "required file is missing"}
        self.assertEqual(missing, {"deliverable.md", "review.md", "delivery-note.md"})

    def test_systematic_research_has_local_handoff_fallback(self) -> None:
        skill = (PLUGIN_ROOT / "skills" / "systematic-research" / "SKILL.md").read_text(encoding="utf-8")
        required = [
            "Continuity Vault is an optional companion",
            "research-handoff.md",
            "The complete current source ledger",
            "Open questions",
            "Research boundaries",
            "The next action",
            "The current verification state",
        ]
        for text in required:
            with self.subTest(text=text):
                self.assertIn(text, skill)

    def test_manifest_versions_match_release(self) -> None:
        versions = {
            json.loads((PLUGIN_ROOT / directory / "plugin.json").read_text(encoding="utf-8"))["version"]
            for directory in (".claude-plugin", ".codex-plugin")
        }
        self.assertEqual(versions, {"0.2.2"})


if __name__ == "__main__":
    unittest.main()
