"""Checks for the staged pressure-test controls."""

from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXPECTED = {
    "gauntlet",
    "gauntlet-plan",
    "gauntlet-compile",
    "gauntlet-run",
    "gauntlet-handoff",
    "gauntlet-verify",
}


class PressureScenarioTests(unittest.TestCase):
    def test_each_skill_has_a_preimplementation_baseline(self) -> None:
        scenarios = {}
        for path in (ROOT / "tests" / "pressure-scenarios").glob("*.json"):
            data = json.loads(path.read_text(encoding="utf-8"))
            scenarios[data["skill"]] = data
        self.assertEqual(set(scenarios), EXPECTED)
        for skill, data in scenarios.items():
            self.assertEqual(data["baseline_state"], "missing")
            self.assertGreaterEqual(len(data["pressure_cases"]), 5)
            self.assertGreaterEqual(len(data["required_controls"]), 5)
            self.assertTrue((ROOT / "skills" / skill / "SKILL.md").is_file())

    def test_isolation_and_budget_language_is_enforced(self) -> None:
        corpus = "\n".join(
            (ROOT / "skills" / skill / "SKILL.md").read_text(encoding="utf-8")
            for skill in sorted(EXPECTED)
        )
        self.assertIn('fork_turns: "none"', corpus)
        self.assertIn("finite", corpus)
        self.assertIn("user approval", corpus)
        self.assertIn("disjoint", corpus)
        self.assertIn("Builders cannot issue the final verdict", corpus)


if __name__ == "__main__":
    unittest.main()
