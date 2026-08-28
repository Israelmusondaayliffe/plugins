#!/usr/bin/env python3
"""Basic bundle contract tests."""

from __future__ import annotations

import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent


class BundleTests(unittest.TestCase):
    def test_manifest_and_spec_match(self):
        manifest = json.loads((ROOT / ".codex-plugin/plugin.json").read_text())
        spec = json.loads((ROOT / "bundle-spec.json").read_text())
        self.assertEqual(manifest["name"], spec["plugin"])
        self.assertEqual(manifest["version"], spec["version"])

    def test_skill_names_match_folders(self):
        spec = json.loads((ROOT / "bundle-spec.json").read_text())
        actual = {path.parent.name for path in (ROOT / "skills").glob("*/SKILL.md")}
        self.assertEqual(actual, set(spec["skills"]))
        for path in (ROOT / "skills").glob("*/SKILL.md"):
            match = re.search(r"^name:\s*([a-z0-9-]+)\s*$", path.read_text(), re.MULTILINE)
            self.assertIsNotNone(match)
            self.assertEqual(match.group(1), path.parent.name)

    def test_trigger_balance_and_outcome_coverage(self):
        triggers = json.loads((ROOT / "tests/trigger-cases.json").read_text())["cases"]
        self.assertEqual(sum(case["should_trigger"] is True for case in triggers), 10)
        self.assertEqual(sum(case["should_trigger"] is False for case in triggers), 10)
        outcomes = json.loads((ROOT / "tests/outcome-cases.json").read_text())["cases"]
        self.assertEqual(len(outcomes), 10)


if __name__ == "__main__":
    unittest.main()
