from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import film_advisor  # noqa: E402
import scenario_evaluator  # noqa: E402
from validate_bundle import EXPECTED_INTERFACES, EXPECTED_SKILLS, validate_bundle, validate_value  # noqa: E402


class BundleTests(unittest.TestCase):
    def load_fixture(self, group: str, name: str):
        return json.loads((ROOT / "fixtures" / group / name).read_text(encoding="utf-8"))

    def test_bundle_validates(self):
        self.assertEqual(validate_bundle(ROOT), [])

    def test_manifest_declares_exactly_eleven_skills(self):
        manifest = json.loads((ROOT / ".codex-plugin" / "plugin.json").read_text(encoding="utf-8"))
        claude = json.loads((ROOT / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["version"], "0.2.0")
        self.assertEqual(claude["version"], "0.2.0")
        self.assertEqual(manifest["description"], claude["description"])
        self.assertEqual(manifest["author"]["name"], "Community Maintainers")
        self.assertEqual(claude["author"]["name"], "Community Maintainers")
        self.assertEqual(manifest["skills"], "./skills/")
        self.assertNotIn("mcpServers", manifest)
        self.assertNotIn("apps", manifest)
        self.assertNotIn("hooks", manifest)
        self.assertLessEqual(len(manifest["interface"]["defaultPrompt"]), 3)
        contract = json.loads((ROOT / "references" / "plugin-contract.json").read_text(encoding="utf-8"))
        self.assertEqual(contract["skills"], EXPECTED_SKILLS)

    def test_local_film_grill_is_complete_without_strategy_room(self):
        decisions = {
            field: {
                "decision": f"decided {field}",
                "alternatives": [],
                "reason": "user decision",
                "source": "user",
                "next_proof": "record in FilmBrief",
            }
            for field in film_advisor.FILM_GRILL_FIELDS
        }
        result = film_advisor.build_local_grill_state(decisions)
        self.assertEqual(result["status"], "ready")
        self.assertEqual(result["open"], [])
        self.assertIsNone(result["next_question"])
        for field in ("decided", "assumed", "alternatives", "decision_reasons", "source_evidence", "next_proof"):
            self.assertIn(field, result)

    def test_model_neutral_packet_completes_without_video_plugin(self):
        shot = json.loads((ROOT / "templates" / "ShotRecord.json").read_text(encoding="utf-8"))
        profile = json.loads((ROOT / "model-profiles" / "seedance-2.5-v1.json").read_text(encoding="utf-8"))
        result = film_advisor.build_model_neutral_shot_packet(shot, profile, formatter_available=False)
        self.assertEqual(result["status"], "complete_model_neutral")
        packet = result["prompt_packet"]
        self.assertEqual(packet["normalized_shot_record"]["geography"], shot["geography"])
        self.assertEqual(packet["compiled_prompt"], "")
        self.assertEqual(packet["validator_result"]["status"], "unrun")
        self.assertEqual(result["formatter_handoff"]["missing_optional_formatter"], "video-production-studio:video-prompt-builder")
        schema = json.loads((ROOT / "schemas" / "PromptPacket.schema.json").read_text(encoding="utf-8"))
        errors = []
        validate_value(packet, schema, "local-prompt-packet", errors)
        self.assertEqual(errors, [])

    def test_host_without_named_models_uses_local_bounded_planner(self):
        result = film_advisor.resolve_host_topology([])
        self.assertEqual(result["status"], "local_core_available")
        self.assertEqual(result["mode"], "local-bounded-planner")
        self.assertIn("verify", result["phases"])
        self.assertTrue(result["missing"])

    def test_enhanced_topology_requires_every_capability(self):
        result = film_advisor.resolve_host_topology(film_advisor.ENHANCED_TOPOLOGY_CAPABILITIES)
        self.assertEqual(result["status"], "enhanced_topology_proved")
        self.assertEqual(result["missing"], [])

    def test_unavailable_independent_runtime_has_exact_handoff(self):
        resolution = film_advisor.resolve_host_topology([])
        handoff = film_advisor.build_unsupported_topology_handoff(
            resolution,
            ["FilmBrief validated"],
            "independent fresh-task review is unproved",
            "run the verifier on a host that proves fresh non-forked tasks",
        )
        self.assertEqual(handoff["status"], "stopped")
        self.assertEqual(
            set(handoff),
            {"protocol", "status", "reason", "missing_capability", "completed_local_work", "unresolved_proof", "next_action"},
        )

    def test_stable_record_interface_inventory_is_complete(self):
        index = json.loads((ROOT / "schemas" / "stable-record-interfaces.json").read_text(encoding="utf-8"))
        self.assertEqual([entry["name"] for entry in index["interfaces"]], EXPECTED_INTERFACES)

    def test_explicit_packet_routes_without_execution_authority(self):
        packet = self.load_fixture("valid", "film-advisor-packet.json")
        result = film_advisor.evaluate_packet(packet)
        self.assertEqual(result["status"], "accepted")
        self.assertEqual(result["skill"], "shot-continuity-director")
        self.assertNotIn("generate", result["authority"])

    def test_unapproved_external_action_stops(self):
        packet = self.load_fixture("invalid", "film-advisor-external-unapproved.json")
        result = film_advisor.evaluate_packet(packet)
        self.assertEqual(result["status"], "stopped")
        self.assertEqual(result["reason"], "external_action_requires_approval")

    def test_implicit_activation_stops(self):
        packet = self.load_fixture("invalid", "film-advisor-implicit.json")
        result = film_advisor.evaluate_packet(packet)
        self.assertEqual(result["status"], "stopped")
        self.assertEqual(result["reason"], "activation_not_explicit")

    def test_malformed_and_unknown_actions_stop(self):
        packet = self.load_fixture("valid", "film-advisor-packet.json")
        packet.pop("project_root")
        self.assertEqual(film_advisor.evaluate_packet(packet)["status"], "stopped")
        packet = self.load_fixture("valid", "film-advisor-packet.json")
        packet["requested_actions"][0]["type"] = "delete_all"
        self.assertEqual(film_advisor.evaluate_packet(packet)["reason"], "invalid_action")

    def test_external_approval_is_bound_to_target_and_cost(self):
        packet = self.load_fixture("valid", "film-advisor-packet.json")
        packet["route"] = "iteration"
        packet["requested_actions"] = [{"type":"paid_generation","target":"surface-a","approval":{"status":"approved","id":"approval-1","action_type":"paid_generation","target":"surface-b","evidence":{"cost_preview":"USD 10"}}}]
        self.assertEqual(film_advisor.evaluate_packet(packet)["details"]["approval_error"], "approval_scope_mismatch")
        packet["requested_actions"][0]["approval"]["target"] = "surface-a"
        packet["requested_actions"][0]["approval"]["evidence"] = {}
        self.assertEqual(film_advisor.evaluate_packet(packet)["details"]["approval_error"], "missing_cost_preview")

    def test_three_reviewer_packets_are_independent_and_locked(self):
        packets = [json.loads((ROOT / "templates" / f"{name}.json").read_text()) for name in ("AuditPacket", "FixPacket", "VerificationPacket")]
        self.assertEqual(len({packet["thread_id"] for packet in packets}), 3)
        self.assertEqual([packet["model"] for packet in packets], ["gpt-5.6-sol"] * 3)
        self.assertEqual([packet["effort"] for packet in packets], ["xhigh"] * 3)
        self.assertFalse(packets[0]["authority"]["may_write"])
        self.assertTrue(packets[1]["authority"]["may_write"])
        self.assertFalse(packets[2]["authority"]["may_write"])

    def test_all_scenario_fixtures_are_executable(self):
        paths = sorted((ROOT / "fixtures" / "failure").glob("*.json")) + sorted((ROOT / "fixtures" / "end-to-end").glob("*.json"))
        self.assertEqual(len(paths), 9)
        for path in paths:
            with self.subTest(path=path.name):
                result = scenario_evaluator.evaluate_scenario(json.loads(path.read_text()))
                self.assertEqual(result["status"], "passed")

    def test_terminal_records_fail_closed(self):
        from validate_bundle import validate_record_semantics
        cases = [
            {"schema_version":"ai-film-studio/VerificationPacket/v1","status":"passed","evidence":[]},
            {"schema_version":"ai-film-studio/GenerationAttempt/v1","status":"observed","output_references":[],"approval":{"required":True,"approval_id":"","cost_preview":""}},
            {"schema_version":"ai-film-studio/DeliveryReceipt/v1","status":"delivered","final_files":[],"verification_evidence":[],"external_delivery":{"target":"","approval_id":""}},
        ]
        for index, record in enumerate(cases):
            errors = []
            validate_record_semantics(record, f"case-{index}", errors)
            self.assertTrue(errors)


if __name__ == "__main__":
    unittest.main()
