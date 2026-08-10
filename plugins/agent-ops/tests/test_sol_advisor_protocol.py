"""Focused contract tests for Sol Advisor packets and explicit routing."""

from __future__ import annotations

import copy
import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOL_ROOT = ROOT / "skills" / "sol-advisor"
sys.path.insert(0, str(SOL_ROOT / "scripts"))

import validate_packets  # noqa: E402


def load_template(name: str) -> dict:
    return json.loads((SOL_ROOT / "assets" / name).read_text(encoding="utf-8"))


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


class SolAdvisorProtocolTests(unittest.TestCase):
    def write_command_evidence(
        self,
        path: Path,
        *,
        run_id: str,
        task_id: str,
        task_packet_path: str,
        task_packet_sha256: str,
        command: str,
        exit_code: int,
        stdout: str,
        stderr: str = "",
    ) -> str:
        write_json(
            path,
            {
                "record_type": "SolAdvisorCommandEvidence",
                "protocol_version": 1,
                "run_id": run_id,
                "task_id": task_id,
                "task_packet_path": task_packet_path,
                "task_packet_sha256": task_packet_sha256,
                "command": command,
                "exit_code": exit_code,
                "stdout": stdout,
                "stdout_sha256": hashlib.sha256(stdout.encode("utf-8")).hexdigest(),
                "stderr": stderr,
                "stderr_sha256": hashlib.sha256(stderr.encode("utf-8")).hexdigest(),
            },
        )
        return digest(path)

    def write_task_runtime(self, root: Path, packet: dict, *, reviewer: bool = False) -> None:
        runtime = packet["runtime_attestation"]
        request = runtime["creation_request"]
        response = runtime["creation_response"]
        request_path = root / request["path"]
        response_path = root / response["path"]
        request_data = {
            "request_id": request["request_id"],
            "run_id": runtime["run_id"],
            "task_id": runtime["task_id"],
            "reviewer_id": runtime["reviewer_id"],
            "role": runtime["role"],
            "tool": "codex_app__create_thread",
            "model": runtime["model"],
            "thinking": runtime["reasoning_effort"],
            "target": {"type": "project", "projectId": "project-example", "environment": {"type": "local"}},
            "fresh_task": runtime["fresh_task"],
            "creation_method": runtime["creation_method"],
            "forked": runtime["forked"],
            "created_at": request["created_at"],
        }
        response_data = {
            "request_id": request["request_id"],
            "run_id": runtime["run_id"],
            "task_id": runtime["task_id"],
            "reviewer_id": runtime["reviewer_id"],
            "role": runtime["role"],
            "tool": "codex_app__create_thread",
            "model": runtime["model"],
            "thinking": runtime["reasoning_effort"],
            "target": copy.deepcopy(request_data["target"]),
            "fresh_task": runtime["fresh_task"],
            "creation_method": runtime["creation_method"],
            "forked": runtime["forked"],
            "threadId": response["thread_id"],
            "hostId": response["host_id"],
            "successful": response["successful"],
            "responded_at": response["responded_at"],
        }
        write_json(request_path, request_data)
        write_json(response_path, response_data)
        request["sha256"] = digest(request_path)
        response["sha256"] = digest(response_path)

    def valid_packets(self, root: Path) -> tuple[dict, dict, dict, dict]:
        plan_path = root / ".gauntlet" / "plan.md"
        plan_path.parent.mkdir()
        plan_path.write_text("# Approved plan\n", encoding="utf-8")
        approved = root / "approved-root"
        approved.mkdir()

        manifest = load_template("run-manifest.template.json")
        manifest["plan"]["sha256"] = digest(plan_path)
        authorization = manifest["task_authorization"][0]
        authorization["allowed_write_paths"] = [str(approved)]
        authorization["input_paths"][0]["sha256"] = digest(plan_path)
        manifest["write_policy"]["allowed_write_roots"] = [str(approved)]
        parent = manifest["parent_runtime_attestation"]
        parent["effective_model_source"] = "host_metadata"
        parent["effective_model"] = "gpt-5.6-sol"
        parent["unavailable_reason"] = None
        parent_file = root / "runtime" / "parent-host-metadata.json"
        parent_file.parent.mkdir()
        write_json(
            parent_file,
            {
                "run_id": parent["run_id"],
                "parent_id": parent["parent_id"],
                "effective_model": "gpt-5.6-sol",
                "threadId": "parent-thread",
                "hostId": "host-example",
                "observed_at": parent["observed_at"],
            },
        )
        parent["host_metadata"] = {
            "path": "runtime/parent-host-metadata.json",
            "sha256": digest(parent_file),
            "thread_id": "parent-thread",
            "host_id": "host-example",
            "observed_at": parent["observed_at"],
        }
        manifest_path = root / "run-manifest.json"
        write_json(manifest_path, manifest)

        task = load_template("task-packet.template.json")
        task["run_manifest_path"] = "run-manifest.json"
        task["run_manifest_sha256"] = digest(manifest_path)
        task["plan"] = copy.deepcopy(manifest["plan"])
        task["authorization"] = copy.deepcopy(authorization)
        task["scope"]["allowed_write_paths"] = [str(approved)]
        task["input_paths"] = copy.deepcopy(authorization["input_paths"])
        self.write_task_runtime(root, task)
        task_path = root / "task.json"
        write_json(task_path, task)

        artifact = approved / "artifacts" / "task-routine-001.md"
        artifact.parent.mkdir()
        artifact.write_text("bounded implementation\n", encoding="utf-8")
        evidence = root / "evidence" / "return.json"
        evidence.parent.mkdir()
        returned = load_template("return-packet.template.json")
        returned["task_packet_path"] = "task.json"
        returned["task_packet_sha256"] = digest(task_path)
        returned["plan"] = copy.deepcopy(manifest["plan"])
        returned["scope"]["allowed_write_paths"] = [str(approved)]
        returned["scope"]["actual_write_paths"] = [str(approved)]
        returned["artifacts"][0]["path"] = "approved-root/artifacts/task-routine-001.md"
        returned["artifacts"][0]["sha256"] = digest(artifact)
        returned["evidence"][0]["path"] = "evidence/return.json"
        evidence_hash = self.write_command_evidence(
            evidence,
            run_id=returned["run_id"],
            task_id=returned["task_id"],
            task_packet_path=returned["task_packet_path"],
            task_packet_sha256=returned["task_packet_sha256"],
            command=returned["commands"][0]["command"],
            exit_code=returned["commands"][0]["exit_code"],
            stdout="test output\n",
        )
        returned["evidence"][0]["sha256"] = evidence_hash
        returned["status_evidence"]["evidence_path"] = "evidence/return.json"
        returned["status_evidence"]["evidence_sha256"] = evidence_hash
        returned["criterion_to_evidence"][0]["evidence_paths"] = ["evidence/return.json"]
        return_path = root / "return.json"
        write_json(return_path, returned)

        review_evidence = root / "evidence" / "review.json"
        reviewed = load_template("review-packet.template.json")
        reviewed["plan"] = copy.deepcopy(manifest["plan"])
        reviewed["task_packet_path"] = "task.json"
        reviewed["task_packet_sha256"] = digest(task_path)
        reviewed["return_packet_path"] = "return.json"
        reviewed["return_packet_sha256"] = digest(return_path)
        reviewed["artifacts_or_diffs"][0]["path"] = "approved-root/artifacts/task-routine-001.md"
        reviewed["artifacts_or_diffs"][0]["sha256"] = digest(artifact)
        reviewed["evidence"][0]["path"] = "evidence/review.json"
        reviewed["reproduction_commands"][0]["evidence_path"] = "evidence/review.json"
        review_evidence_hash = self.write_command_evidence(
            review_evidence,
            run_id=reviewed["run_id"],
            task_id=reviewed["task_id"],
            task_packet_path=reviewed["task_packet_path"],
            task_packet_sha256=reviewed["task_packet_sha256"],
            command=reviewed["reproduction_commands"][0]["command"],
            exit_code=reviewed["reproduction_commands"][0]["exit_code"],
            stdout="review inspection\n",
        )
        reviewed["evidence"][0]["sha256"] = review_evidence_hash
        reviewed["reproduction_commands"][0]["evidence_sha256"] = review_evidence_hash
        self.write_task_runtime(root, reviewed, reviewer=True)
        return manifest, task, returned, reviewed

    def test_templates_cover_exact_packet_contracts(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            manifest, task, returned, reviewed = self.valid_packets(Path(directory))
            self.assertEqual(validate_packets.validate_packet(manifest, Path(directory)), [])
            self.assertEqual(validate_packets.validate_packet(task, Path(directory)), [])
            self.assertEqual(validate_packets.validate_packet(returned, Path(directory)), [])
            self.assertEqual(validate_packets.validate_packet(reviewed, Path(directory)), [])

    def test_run_manifest_requires_the_reviewed_fields_and_host_parent_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            manifest, task, _, _ = self.valid_packets(root)
            missing_goal = copy.deepcopy(manifest)
            missing_goal.pop("goal")
            self.assertTrue(any("RunManifest missing keys" in error for error in validate_packets.validate_packet(missing_goal, root)))

            missing_plan = copy.deepcopy(manifest)
            missing_plan["plan"]["path"] = "missing-plan.md"
            self.assertTrue(
                any("RunManifest.plan.path must resolve to an existing file" in error for error in validate_packets.validate_packet(missing_plan, root))
            )

            plan_path = root / ".gauntlet" / "plan.md"
            original_plan = plan_path.read_text(encoding="utf-8")
            plan_path.write_text("# Changed after approval\n", encoding="utf-8")
            self.assertIn(
                "RunManifest.plan.sha256 does not match the referenced approved plan",
                validate_packets.validate_packet(manifest, root),
            )
            plan_path.write_text(original_plan, encoding="utf-8")

            invented_hash = copy.deepcopy(manifest)
            invented_hash["plan"]["sha256"] = "0" * 64
            self.assertIn(
                "RunManifest.plan.sha256 does not match the referenced approved plan",
                validate_packets.validate_packet(invented_hash, root),
            )

            alternative_plan = root / "alternative-plan.md"
            alternative_plan.write_text(original_plan, encoding="utf-8")
            task_with_unbound_plan = copy.deepcopy(task)
            task_with_unbound_plan["plan"] = {
                "status": "approved",
                "version": 1,
                "path": "alternative-plan.md",
                "sha256": digest(alternative_plan),
            }
            self.assertIn(
                "TaskPacket.input_paths must bind the referenced approved plan path and SHA-256",
                validate_packets.validate_packet(task_with_unbound_plan, root),
            )

            forged_parent = copy.deepcopy(manifest)
            forged_parent["parent_runtime_attestation"]["effective_model_source"] = "config"
            self.assertIn(
                "RunManifest.parent_runtime_attestation.effective_model_source must be host_metadata or explicitly_unavailable",
                validate_packets.validate_packet(forged_parent, Path(directory)),
            )

            contradictory_parent = copy.deepcopy(manifest)
            parent_path = root / contradictory_parent["parent_runtime_attestation"]["host_metadata"]["path"]
            parent_data = json.loads(parent_path.read_text(encoding="utf-8"))
            parent_data["effective_model"] = "gpt-5.6-terra"
            write_json(parent_path, parent_data)
            contradictory_parent["parent_runtime_attestation"]["host_metadata"]["sha256"] = digest(parent_path)
            self.assertTrue(
                any(
                    "effective_model does not bind the parent runtime" in error
                    for error in validate_packets.validate_packet(contradictory_parent, root)
                )
            )

            cycle = copy.deepcopy(manifest)
            cycle["task_dag"][0]["dependencies"] = ["task-routine-001"]
            cycle["task_authorization"][0]["dependencies"] = ["task-routine-001"]
            errors = validate_packets.validate_packet(cycle, root)
            self.assertTrue(any("cycle" in error for error in errors), errors)

            uncovered = copy.deepcopy(manifest)
            uncovered["criteria"].append({"id": "unassigned", "description": "unassigned"})
            self.assertIn(
                "RunManifest every approved criterion must be assigned to at least one task authorization",
                validate_packets.validate_packet(uncovered, root),
            )

            builder_self_verdict = copy.deepcopy(manifest)
            builder_self_verdict["task_authorization"][0]["reviewer_id"] = "task-routine-001"
            self.assertIn(
                "RunManifest task reviewer_id must not equal its builder task_id",
                validate_packets.validate_packet(builder_self_verdict, root),
            )

            reused_reviewer = copy.deepcopy(manifest)
            second = copy.deepcopy(reused_reviewer["task_authorization"][0])
            second["task_id"] = "task-routine-002"
            second["allowed_write_paths"] = [str(Path(directory) / "approved-output-2")]
            second["expected_output"]["paths"] = ["approved-output-2/artifacts/task-routine-002.md"]
            reused_reviewer["task_authorization"].append(second)
            reused_reviewer["task_dag"].append({"task_id": "task-routine-002", "dependencies": []})
            reused_reviewer["write_policy"]["allowed_write_roots"].append(str(Path(directory) / "approved-output-2"))
            errors = validate_packets.validate_packet(reused_reviewer, root)
            self.assertFalse(any("reviewer_ids" in error for error in errors), errors)

            unapproved_high_cost = copy.deepcopy(manifest)
            unapproved_high_cost["budget"]["max_task_launches"] = 7
            self.assertIn(
                "RunManifest.budget high-cost limits require explicit approval",
                validate_packets.validate_packet(unapproved_high_cost, root),
            )

            impractical = copy.deepcopy(manifest)
            impractical["budget"]["max_task_launches"] = 25
            impractical["budget"]["high_cost_override_approved"] = True
            impractical["budget"]["cost_warning"] = "Approved higher-cost run."
            self.assertIn(
                "RunManifest.budget.max_task_launches must be from 1 to 24",
                validate_packets.validate_packet(impractical, root),
            )

    def test_task_runtime_and_authorization_fail_closed(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            _, task, _, _ = self.valid_packets(Path(directory))
            wrong_model = copy.deepcopy(task)
            wrong_model["worker"]["model"] = "gpt-5.6-terra"
            self.assertIn("TaskPacket.worker.model must be 'gpt-5.6-luna'", validate_packets.validate_packet(wrong_model, Path(directory)))

            stale_freshness = copy.deepcopy(task)
            stale_freshness["runtime_attestation"]["forked"] = True
            self.assertIn(
                "TaskPacket.runtime_attestation.forked must be False",
                validate_packets.validate_packet(stale_freshness, Path(directory)),
            )

            contradictory_response = copy.deepcopy(task)
            response_path = Path(directory) / contradictory_response["runtime_attestation"]["creation_response"]["path"]
            response_data = json.loads(response_path.read_text(encoding="utf-8"))
            response_data["fresh_task"] = False
            write_json(response_path, response_data)
            contradictory_response["runtime_attestation"]["creation_response"]["sha256"] = digest(response_path)
            self.assertTrue(
                any(
                    "creation_response evidence fresh_task does not bind the runtime" in error
                    for error in validate_packets.validate_packet(contradictory_response, Path(directory))
                )
            )

            missing_tools = copy.deepcopy(task)
            missing_tools.pop("tools")
            self.assertTrue(any("TaskPacket missing keys" in error for error in validate_packets.validate_packet(missing_tools, Path(directory))))

            forged_manifest = copy.deepcopy(task)
            forged_manifest["run_manifest_sha256"] = "0" * 64
            self.assertIn(
                "TaskPacket.run_manifest_sha256 does not match the referenced RunManifest",
                validate_packets.validate_packet(forged_manifest, Path(directory)),
            )

            missing_manifest = copy.deepcopy(task)
            Path(directory, "run-manifest.json").unlink()
            self.assertTrue(
                any("TaskPacket.run_manifest.path must resolve to an existing file" in error for error in validate_packets.validate_packet(missing_manifest, Path(directory)))
            )

    def test_return_statuses_require_evidence_but_do_not_require_passing_commands(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            _, _, returned, _ = self.valid_packets(root)
            evidence_path = root / "evidence" / "return.json"
            original_command_evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
            for status in ("blocked", "failed", "escalate"):
                with self.subTest(status=status):
                    non_success = copy.deepcopy(returned)
                    non_success["status"] = status
                    non_success["criterion_to_evidence"][0]["result"] = status
                    non_success["commands"][0]["exit_code"] = 1
                    command_evidence = copy.deepcopy(original_command_evidence)
                    command_evidence["exit_code"] = 1
                    write_json(evidence_path, command_evidence)
                    evidence_hash = digest(evidence_path)
                    non_success["evidence"][0]["sha256"] = evidence_hash
                    non_success["status_evidence"]["evidence_sha256"] = evidence_hash
                    self.assertEqual(validate_packets.validate_packet(non_success, root), [])
            write_json(evidence_path, original_command_evidence)

            legacy = copy.deepcopy(returned)
            legacy["status"] = "completed"
            self.assertIn(
                "ReturnPacket.status must be succeeded, blocked, failed, or escalate",
                validate_packets.validate_packet(legacy, Path(directory)),
            )

            forged = copy.deepcopy(returned)
            forged["evidence"][0]["sha256"] = "0" * 64
            self.assertTrue(any("does not match evidence/return.json" in error for error in validate_packets.validate_packet(forged, root)))

            forged_task = copy.deepcopy(returned)
            forged_task["task_packet_sha256"] = "0" * 64
            self.assertIn(
                "ReturnPacket.task_packet_sha256 does not match the referenced TaskPacket",
                validate_packets.validate_packet(forged_task, Path(directory)),
            )

            failed_success = copy.deepcopy(returned)
            failed_success["commands"][0]["exit_code"] = 1
            self.assertIn(
                "ReturnPacket.status=succeeded requires every evidence command to exit zero",
                validate_packets.validate_packet(failed_success, Path(directory)),
            )

            zero_delta = copy.deepcopy(returned)
            zero_delta["observable_delta"] = ""
            zero_delta["primary_output_count"] = 0
            zero_delta["unresolved_after"] = zero_delta["unresolved_before"]
            errors = validate_packets.validate_packet(zero_delta, root)
            self.assertIn("ReturnPacket implementation success requires a non-empty observable_delta", errors)
            self.assertIn("ReturnPacket implementation success requires primary_output_count >= 1", errors)
            self.assertIn("ReturnPacket implementation success must reduce unresolved work", errors)

    def test_review_packet_is_fresh_read_only_and_non_terminal(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            _, _, _, reviewed = self.valid_packets(Path(directory))
            self.assertEqual(validate_packets.validate_packet(reviewed, Path(directory)), [])

            legacy = copy.deepcopy(reviewed)
            legacy["verdict"] = "artifact_wins"
            self.assertIn(
                "ReviewPacket.verdict must be accepted, revise, blocked, or unable_to_verify",
                validate_packets.validate_packet(legacy, Path(directory)),
            )

            authority = copy.deepcopy(reviewed)
            authority["reviewer"]["may_repair"] = True
            authority["authority"]["may_replace_verification_panel"] = True
            errors = validate_packets.validate_packet(authority, Path(directory))
            self.assertIn("ReviewPacket.reviewer.may_repair must be False", errors)
            self.assertIn("ReviewPacket.authority.may_replace_verification_panel must be false", errors)

            self_verdict = copy.deepcopy(reviewed)
            self_verdict["reviewer_id"] = self_verdict["task_id"]
            self.assertIn(
                "ReviewPacket.reviewer_id must not equal the builder task_id",
                validate_packets.validate_packet(self_verdict, Path(directory)),
            )

            failed_acceptance = copy.deepcopy(reviewed)
            failed_acceptance["reproduction_commands"][0]["exit_code"] = 1
            self.assertIn(
                "ReviewPacket.verdict=accepted requires every reproduction command to exit zero",
                validate_packets.validate_packet(failed_acceptance, Path(directory)),
            )

    def test_artifact_command_and_review_bindings_fail_closed(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            _, task, returned, reviewed = self.valid_packets(root)

            sibling_artifact = root / "approved-root-sibling" / "artifacts" / "task-routine-001.md"
            sibling_artifact.parent.mkdir(parents=True)
            sibling_artifact.write_text("sibling artifact\n", encoding="utf-8")
            sibling_return = copy.deepcopy(returned)
            sibling_return["artifacts"][0]["path"] = "approved-root-sibling/artifacts/task-routine-001.md"
            sibling_return["artifacts"][0]["sha256"] = digest(sibling_artifact)
            self.assertTrue(
                any(
                    "ReturnPacket.artifacts[0].path must stay within TaskPacket allowed_write_paths" in error
                    for error in validate_packets.validate_packet(sibling_return, root)
                )
            )

            traversal_return = copy.deepcopy(returned)
            traversal_return["artifacts"][0]["path"] = "../outside/task-routine-001.md"
            self.assertTrue(
                any(
                    "ReturnPacket.artifacts[0].path must stay under the verification root" in error
                    for error in validate_packets.validate_packet(traversal_return, root)
                )
            )

            unapproved_artifact = root / "unapproved-root" / "artifacts" / "task-routine-001.md"
            unapproved_artifact.parent.mkdir(parents=True)
            unapproved_artifact.write_text("unapproved artifact\n", encoding="utf-8")
            unapproved_return = copy.deepcopy(returned)
            unapproved_return["artifacts"][0]["path"] = "unapproved-root/artifacts/task-routine-001.md"
            unapproved_return["artifacts"][0]["sha256"] = digest(unapproved_artifact)
            self.assertTrue(
                any(
                    "ReturnPacket.artifacts[0].path must stay within TaskPacket allowed_write_paths" in error
                    for error in validate_packets.validate_packet(unapproved_return, root)
                )
            )

            unapproved_output = copy.deepcopy(task)
            unapproved_output["authorization"]["expected_output"]["paths"] = ["unapproved-root/artifacts/task-routine-001.md"]
            unapproved_output["expected_output"] = copy.deepcopy(unapproved_output["authorization"]["expected_output"])
            self.assertIn(
                "TaskPacket.authorization.expected_output.paths[0] must stay within allowed_write_paths",
                validate_packets.validate_packet(unapproved_output, root),
            )

            wrong_return_hash = copy.deepcopy(reviewed)
            wrong_return_hash["return_packet_sha256"] = "0" * 64
            self.assertIn(
                "ReviewPacket.return_packet_sha256 does not match the referenced ReturnPacket",
                validate_packets.validate_packet(wrong_return_hash, root),
            )

            artifact_mismatch = copy.deepcopy(reviewed)
            artifact_mismatch["artifacts_or_diffs"][0]["kind"] = "diff"
            self.assertIn(
                "ReviewPacket reviewed artifacts must exactly equal the referenced ReturnPacket artifacts",
                validate_packets.validate_packet(artifact_mismatch, root),
            )

            command_evidence_path = root / "evidence" / "return.json"
            command_evidence = json.loads(command_evidence_path.read_text(encoding="utf-8"))
            mismatched_command = copy.deepcopy(command_evidence)
            mismatched_command["exit_code"] = 7
            write_json(command_evidence_path, mismatched_command)
            malformed_exit_code = copy.deepcopy(returned)
            evidence_hash = digest(command_evidence_path)
            malformed_exit_code["evidence"][0]["sha256"] = evidence_hash
            malformed_exit_code["status_evidence"]["evidence_sha256"] = evidence_hash
            malformed_exit_code["commands"][0]["evidence_mode"] = "file"
            malformed_exit_code["commands"][0]["evidence_path"] = "evidence/return.json"
            malformed_exit_code["commands"][0]["evidence_sha256"] = evidence_hash
            self.assertIn(
                "ReturnPacket.commands[0].evidence JSON exit_code does not bind the recorded command",
                validate_packets.validate_packet(malformed_exit_code, root),
            )

            command_evidence["stdout_sha256"] = "0" * 64
            write_json(command_evidence_path, command_evidence)
            malformed_output_hash = copy.deepcopy(returned)
            evidence_hash = digest(command_evidence_path)
            malformed_output_hash["evidence"][0]["sha256"] = evidence_hash
            malformed_output_hash["status_evidence"]["evidence_sha256"] = evidence_hash
            malformed_output_hash["commands"][0]["evidence_mode"] = "file"
            malformed_output_hash["commands"][0]["evidence_path"] = "evidence/return.json"
            malformed_output_hash["commands"][0]["evidence_sha256"] = evidence_hash
            self.assertIn(
                "ReturnPacket.commands[0].evidence JSON stdout_sha256 does not match recorded stdout",
                validate_packets.validate_packet(malformed_output_hash, root),
            )

if __name__ == "__main__":
    unittest.main()
