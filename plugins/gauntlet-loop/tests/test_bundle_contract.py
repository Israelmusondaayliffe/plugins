"""Bundle contract tests."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from verify_bundle import verify  # noqa: E402


class BundleContractTests(unittest.TestCase):
    def test_complete_bundle(self) -> None:
        result = verify(ROOT)
        self.assertTrue(result["valid"], result["errors"])
        self.assertEqual(result["skill_count"], 6)

    def test_every_skill_is_explicit_only(self) -> None:
        for skill in (ROOT / "skills").iterdir():
            metadata = (skill / "agents" / "openai.yaml").read_text(encoding="utf-8")
            self.assertIn("allow_implicit_invocation: false", metadata)

    def test_sol_advisor_registration_uses_work_first_next_action(self) -> None:
        adapter = (ROOT / "scripts" / "sol_advisor_adapter.py").read_text(encoding="utf-8")
        self.assertIn("returned['next_target_action']", adapter)
        self.assertNotIn("returned['next_action']", adapter)


if __name__ == "__main__":
    unittest.main()
