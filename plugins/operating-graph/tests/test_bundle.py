"""Operating Graph bundle and explicit-only release contracts."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]


class BundleTests(unittest.TestCase):
    def test_bundle_validator_passes(self) -> None:
        completed = subprocess.run(
            [sys.executable, str(ROOT / "scripts/verify_bundle.py"), str(ROOT)],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
        self.assertTrue(json.loads(completed.stdout)["valid"])

    def test_every_skill_is_explicit_only(self) -> None:
        for skill in (ROOT / "skills").glob("*/SKILL.md"):
            metadata = skill.parent / "agents" / "openai.yaml"
            self.assertIn("allow_implicit_invocation: false", metadata.read_text(encoding="utf-8"))
            self.assertIn("explicit-only", skill.read_text(encoding="utf-8"))

    def test_front_door_has_no_named_loop_plugin_dependency(self) -> None:
        front_door = (ROOT / "skills/graph-engineering/SKILL.md").read_text(encoding="utf-8")
        self.assertNotIn("LoopKit", front_door)
        self.assertIn("does not require that companion", front_door)


if __name__ == "__main__":
    unittest.main()
