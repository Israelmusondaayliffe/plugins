"""End-to-end state-machine test for a compiled project."""

from __future__ import annotations

import argparse
import hashlib
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import gauntletctl  # noqa: E402


class IntegrationTests(unittest.TestCase):
    def test_plan_compile_run_verify_state_path(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory)
            gauntletctl.command_init(
                argparse.Namespace(project_root=str(project), name="Integration Project", actor="test", force=False)
            )
            root = project / ".gauntlet"
            plan = (root / "plan.md").read_text(encoding="utf-8")
            (root / "plan.md").write_text(plan.replace("Status: proposed", "Status: approved"), encoding="utf-8")
            (root / "decisions.md").write_text(
                "# Decisions\n\nApproval: User approved plan version 1 for this test.\n",
                encoding="utf-8",
            )
            gauntletctl.command_capabilities(
                argparse.Namespace(
                    project_root=str(project),
                    model="test-model",
                    reasoning="high",
                    agent_tools="available",
                    thread_tools="unavailable",
                    max_concurrency=3,
                    fresh_isolation=True,
                )
            )
            transitions = [
                ("grilling", "Explore ambiguity"),
                ("plan_proposed", "Present plan"),
                ("plan_approved", "Record user approval"),
            ]
            for target, reason in transitions:
                gauntletctl.command_transition(
                    argparse.Namespace(
                        project_root=str(project),
                        to=target,
                        actor="test",
                        reason=reason,
                        artifact=[".gauntlet/plan.md"],
                        next_action="Continue the integration test.",
                        force=False,
                    )
                )

            program = gauntletctl.initial_program()
            program.update(
                {
                    "status": "compiled",
                    "version": 1,
                    "plan_version": 1,
                    "plan_sha256": hashlib.sha256((root / "plan.md").read_bytes()).hexdigest(),
                    "project_type": "mixed",
                    "goal": "Prove the complete state path.",
                    "workstreams": [
                        {
                            "id": "ws-1",
                            "objective": "Build evidence",
                            "dependencies": [],
                            "write_targets": ["artifacts/ws-1"],
                            "acceptance_criteria": ["criterion-1", "criterion-2"],
                            "evidence_required": ["artifact.txt", "test.txt"],
                            "builder_charter": "Create the artifact and its test evidence.",
                            "critic_charter": "Evaluate criterion-1 from fresh context.",
                            "critic": "fresh-critic",
                            "max_critic_rounds": 2,
                            "stop_conditions": ["Stop if evidence cannot be produced."],
                        }
                    ],
                    "integration_waves": [{"id": "wave-1", "workstreams": ["ws-1"]}],
                    "verification_panel": ["acceptance", "evidence", "adversarial"],
                }
            )
            gauntletctl.write_json(project / ".gauntlet" / "gauntlet.yaml", program)

            for target in ["gauntlet_compiled", "executing", "integrating"]:
                gauntletctl.command_transition(
                    argparse.Namespace(
                        project_root=str(project),
                        to=target,
                        actor="test",
                        reason=f"Integration transition to {target}",
                        artifact=[".gauntlet/gauntlet.yaml"],
                        next_action="Continue the integration test.",
                        force=False,
                    )
                )

            critic_root = root / "workstreams" / "ws-1"
            critic_root.mkdir(parents=True)
            gauntletctl.write_json(
                critic_root / "critic-report.json",
                {
                    "workstream_id": "ws-1",
                    "round": 1,
                    "verdict": "artifact_wins",
                    "largest_gap": None,
                    "evidence": ["artifact.txt", "test.txt"],
                    "criteria_checked": ["criterion-1", "criterion-2"],
                    "critic_isolation": "fresh_no_inherited_turns",
                },
            )
            (root / "artifact-register.md").write_text(
                "# Artifact Register\n\n- artifact.txt: completed and tested.\n",
                encoding="utf-8",
            )
            (root / "source-register.md").write_text(
                "# Source Register\n\n- test.txt: deterministic integration evidence.\n",
                encoding="utf-8",
            )
            (root / "integration" / "synthesis-report.md").write_text(
                "# Synthesis Report\n\nThe workstream output passed its integration check with no conflicts.\n",
                encoding="utf-8",
            )
            with self.assertRaises(gauntletctl.GauntletError):
                gauntletctl.command_transition(
                    argparse.Namespace(
                        project_root=str(project),
                        to="ready_for_verification",
                        actor="test",
                        reason="Claim evidence without real paths",
                        artifact=[],
                        next_action="Repair evidence.",
                        force=False,
                    )
                )
            (project / "artifact.txt").write_text("tested artifact\n", encoding="utf-8")
            (project / "test.txt").write_text("PASS\n", encoding="utf-8")
            gauntletctl.command_transition(
                argparse.Namespace(
                    project_root=str(project),
                    to="ready_for_verification",
                    actor="test",
                    reason="Critic and integration gates passed",
                    artifact=[".gauntlet/workstreams/ws-1/critic-report.json"],
                    next_action="Run independent verification.",
                    force=False,
                )
            )
            (root / "verification" / "acceptance-matrix.md").write_text(
                "# Acceptance Matrix\n\n"
                "- [x] criterion-1 | Artifact: artifact.txt | Check: test.txt passes | "
                "Evidence: test.txt | Verifier: acceptance\n",
                encoding="utf-8",
            )
            with self.assertRaises(gauntletctl.GauntletError):
                gauntletctl.command_transition(
                    argparse.Namespace(
                        project_root=str(project),
                        to="verifying",
                        actor="test",
                        reason="Omit one material criterion",
                        artifact=[],
                        next_action="Complete the matrix.",
                        force=False,
                    )
                )
            (root / "verification" / "acceptance-matrix.md").write_text(
                "# Acceptance Matrix\n\n"
                "- [x] criterion-1 | Artifact: artifact.txt | Check: test.txt passes | "
                "Evidence: test.txt | Verifier: acceptance\n"
                "- [x] criterion-2 | Artifact: artifact.txt | Check: artifact inspection passes | "
                "Evidence: artifact.txt | Verifier: evidence\n",
                encoding="utf-8",
            )
            gauntletctl.command_transition(
                argparse.Namespace(
                    project_root=str(project),
                    to="verifying",
                    actor="test",
                    reason="Acceptance matrix is complete",
                    artifact=[".gauntlet/verification/acceptance-matrix.md"],
                    next_action="Collect three fresh verifier reports.",
                    force=False,
                )
            )
            with self.assertRaises(gauntletctl.GauntletError):
                gauntletctl.command_transition(
                    argparse.Namespace(
                        project_root=str(project),
                        to="verified",
                        actor="test",
                        reason="Unsupported claim",
                        artifact=[],
                        next_action="None.",
                        force=False,
                    )
                )
            for role in ["acceptance", "evidence", "adversarial"]:
                gauntletctl.write_json(
                    root / "verification" / "verifier-reports" / f"{role}.json",
                    {
                        "verifier_role": role,
                        "verdict": "pass",
                        "criteria_checked": [
                            {
                                "criterion": "criterion-1",
                                "result": "pass",
                                "evidence": ["artifact.txt", "test.txt"],
                            },
                            {
                                "criterion": "criterion-2",
                                "result": "pass",
                                "evidence": ["artifact.txt"],
                            }
                        ],
                        "findings": [],
                        "residual_risks": [],
                        "verifier_isolation": "fresh_no_inherited_turns",
                    },
                )
            gauntletctl.command_evidence(
                argparse.Namespace(project_root=str(project), verdict="verified")
            )
            critic_report = critic_root / "critic-report.json"
            critic_data = critic_report.read_text(encoding="utf-8")
            critic_report.unlink()
            (root / "integration" / "synthesis-report.md").write_text(
                "# Synthesis Report\n",
                encoding="utf-8",
            )
            with self.assertRaises(gauntletctl.GauntletError):
                gauntletctl.command_transition(
                    argparse.Namespace(
                        project_root=str(project),
                        to="verified",
                        actor="verification-panel",
                        reason="Attempt terminal transition after evidence tampering",
                        artifact=[".gauntlet/reports/evidence-report.md"],
                        next_action="Repair the evidence package.",
                        force=False,
                    )
                )
            critic_report.write_text(critic_data, encoding="utf-8")
            (root / "integration" / "synthesis-report.md").write_text(
                "# Synthesis Report\n\nThe workstream output passed its integration check with no conflicts.\n",
                encoding="utf-8",
            )
            gauntletctl.command_transition(
                argparse.Namespace(
                    project_root=str(project),
                    to="verified",
                    actor="verification-panel",
                    reason="Computed panel verdict is verified",
                    artifact=[".gauntlet/reports/evidence-report.md"],
                    next_action="Close out the project.",
                    force=False,
                )
            )
            gauntletctl.command_handoff(
                argparse.Namespace(
                    project_root=str(project),
                    actor="test",
                    objective="Close out the verified project.",
                    completed="Completed independent verification.",
                    failures="None.",
                    next_action="Archive the evidence package.",
                    do_not_redo="Do not rerun accepted workstreams.",
                    user_instructions="Preserve the evidence.",
                    artifact=[".gauntlet/reports/evidence-report.md"],
                    evidence=[".gauntlet/verification/verifier-reports/acceptance.json"],
                )
            )
            result = gauntletctl.command_validate(argparse.Namespace(project_root=str(project), strict=True))
            self.assertTrue(result["valid"], result["errors"])
            self.assertEqual(result["state"], "verified")

    def test_evidence_cannot_be_claimed_during_intake(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory)
            gauntletctl.command_init(
                argparse.Namespace(project_root=str(project), name="Evidence Gate", actor="test", force=False)
            )
            with self.assertRaises(gauntletctl.GauntletError):
                gauntletctl.command_evidence(
                    argparse.Namespace(project_root=str(project), verdict="verified")
                )


if __name__ == "__main__":
    unittest.main()
