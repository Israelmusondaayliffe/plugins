"""Functional tests for deterministic Gauntlet project operations."""

from __future__ import annotations

import argparse
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import gauntletctl  # noqa: E402


class GauntletCtlTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.project = Path(self.temporary.name)
        self.init_result = gauntletctl.command_init(
            argparse.Namespace(project_root=str(self.project), name="Test Project", actor="test", force=False)
        )

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def test_init_creates_valid_workspace(self) -> None:
        self.assertTrue(self.init_result["valid"])
        self.assertEqual(self.init_result["state"], "intake")
        self.assertTrue((self.project / ".gauntlet" / "state.json").is_file())

    def test_invalid_transition_fails_closed(self) -> None:
        with self.assertRaises(gauntletctl.GauntletError):
            gauntletctl.command_transition(
                argparse.Namespace(
                    project_root=str(self.project),
                    to="verified",
                    actor="test",
                    reason="skip the workflow",
                    artifact=None,
                    next_action="none",
                    force=False,
                )
            )

    def test_handoff_has_all_sections(self) -> None:
        result = gauntletctl.command_handoff(
            argparse.Namespace(
                project_root=str(self.project),
                actor="test",
                objective="Continue the test project.",
                completed="Initialized project state.",
                failures="None.",
                next_action="Compile the approved plan.",
                do_not_redo="Do not initialize again.",
                user_instructions="Stay within the test directory.",
                artifact=[".gauntlet/state.json"],
                evidence=["tests/test_gauntletctl.py"],
            )
        )
        self.assertTrue(result["validation"]["valid"])
        self.assertTrue(Path(result["session_record"]).is_file())
        project = (self.project / ".gauntlet" / "project.md").read_text(encoding="utf-8")
        self.assertIn("Continue the test project.", project)
        self.assertIn("Compile the approved plan.", project)

    def test_transition_updates_canonical_project_summary(self) -> None:
        gauntletctl.command_transition(
            argparse.Namespace(
                project_root=str(self.project),
                to="grilling",
                actor="test",
                reason="Begin structured questions",
                artifact=[".gauntlet/brief.md"],
                next_action="Answer the unresolved questions.",
                force=False,
            )
        )
        project = (self.project / ".gauntlet" / "project.md").read_text(encoding="utf-8")
        self.assertIn("`grilling`", project)
        self.assertIn("Answer the unresolved questions.", project)

    def test_budget_and_fresh_judge_contracts_are_validated(self) -> None:
        program = gauntletctl.initial_program()
        program["execution"]["fresh_judges"] = False
        program["budget"]["max_agent_launches"] = 0
        errors = gauntletctl.validate_program(program, compiled=False)
        self.assertIn("program must require fresh judges", errors)
        self.assertIn("budget.max_agent_launches must be a positive integer", errors)


if __name__ == "__main__":
    unittest.main()
