import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "practice_compiler.py"
SPEC = importlib.util.spec_from_file_location("practice_compiler", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(MODULE)


class PracticeCompilerTests(unittest.TestCase):
    def setUp(self):
        self.fixtures = Path(__file__).resolve().parents[1] / "fixtures" / "sessions"

    def test_redacts_secrets_and_email(self):
        value = MODULE.redact(
            "owner@example.com token=sk-test-secret "
            "OPENAI_API_KEY=supersecret123 ghp_abcdefghijklmnopqrstuvwxyz123456"
        )
        self.assertNotIn("owner@example.com", value)
        self.assertNotIn("sk-test-secret", value)
        self.assertNotIn("supersecret123", value)
        self.assertNotIn("ghp_", value)

    def test_extracts_actual_command_not_plain_mention(self):
        signals, errors = MODULE.extract_signals(self.fixtures / "session-a.jsonl")
        self.assertFalse(errors)
        kinds = [item["kind"] for item in signals]
        self.assertIn("executed-command", kinds)
        self.assertIn("command-failure", kinds)

    def test_repeated_command_becomes_proposal(self):
        signals = []
        for name in ("session-a.jsonl", "session-b.jsonl"):
            found, _ = MODULE.extract_signals(self.fixtures / name)
            signals.extend(found)
        proposals = MODULE.build_proposals(signals, 2)
        self.assertTrue(any(item["signal_class"] == "repeated-task" for item in proposals))
        self.assertTrue(all(isinstance(item["evidence"][0], dict) for item in proposals))
        self.assertTrue(all("citation" in item["evidence"][0] for item in proposals))

    def test_direct_user_extraction_ignores_injected_nested_user_text(self):
        event = {
            "type": "session_meta",
            "payload": {
                "base_instructions": {
                    "role": "user",
                    "content": "No, change every file.",
                }
            },
        }
        self.assertEqual([], MODULE.direct_user_text(event))
        wrapper = {
            "type": "response_item",
            "payload": {"role": "user", "content": "<recommended_plugins>injected</recommended_plugins>"},
        }
        self.assertEqual([], MODULE.direct_user_text(wrapper))
        for content in (
            "<skill>injected skill instructions</skill>",
            '<codex_internal_context source="goal">injected goal</codex_internal_context>',
        ):
            wrapped = {"type": "response_item", "payload": {"role": "user", "content": content}}
            self.assertEqual([], MODULE.direct_user_text(wrapped))

    def test_later_user_message_is_follow_up(self):
        self.assertEqual(
            "follow-up-instruction",
            MODULE.classify_user_signal("Publish the verified result.", 1),
        )

    def test_semantic_variants_group_across_sessions(self):
        base = {"source_class": "user"}
        signals = [
            MODULE.signal(
                "recurring-feedback", Path("/tmp/a.jsonl"), 3,
                "Keep changes surgical and do not redesign approved parts.",
                MODULE.semantic_key("Keep changes surgical and do not redesign approved parts."),
                {**base, "session_id": "a"},
            ),
            MODULE.signal(
                "recurring-feedback", Path("/tmp/b.jsonl"), 8,
                "Do not redesign the approved parts. Keep the change surgical.",
                MODULE.semantic_key("Do not redesign the approved parts. Keep the change surgical."),
                {**base, "session_id": "b"},
            ),
        ]
        proposals = MODULE.build_proposals(signals, 2)
        self.assertEqual(1, len(proposals))
        self.assertEqual("recurring-feedback", proposals[0]["signal_class"])

    def test_fixture_source_is_classified_synthetic(self):
        metadata, errors = MODULE.session_metadata(self.fixtures / "session-a.jsonl")
        self.assertFalse(errors)
        self.assertEqual("synthetic", metadata["source_class"])

    def test_scan_cursor_is_idempotent(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            args = type("Args", (), {
                "sessions_root": [str(self.fixtures)], "include_claude": False, "limit": 20,
                "min_occurrences": 2, "scan_id": "first", "state_root": str(root),
                "source_class": ["synthetic"], "since": None, "until": None, "stdout": False,
                "timezone": "UTC",
            })()
            first = MODULE.cmd_scan(args)
            args.scan_id = "second"
            second = MODULE.cmd_scan(args)
            self.assertEqual(2, first["files_processed"])
            self.assertEqual(0, second["files_processed"])
            self.assertEqual(2, second["files_skipped"])

    def test_rejected_proposal_stays_rejected_on_rescan(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            args = type("Args", (), {
                "sessions_root": [str(self.fixtures)], "include_claude": False, "limit": 20,
                "min_occurrences": 2, "scan_id": "first", "state_root": str(root),
                "source_class": ["synthetic"], "since": None, "until": None, "stdout": False,
                "timezone": "UTC",
            })()
            MODULE.cmd_scan(args)
            proposal = MODULE.read_proposals(root)[0]
            decision_args = type("Args", (), {
                "proposal_id": proposal["proposal_id"], "decision": "reject",
                "note": "one-off", "state_root": str(root)
            })()
            MODULE.cmd_decide(decision_args)
            cursor = MODULE.load_json(root / "cursor.json")
            cursor["processed"] = {}
            MODULE.atomic_json(root / "cursor.json", cursor)
            args.scan_id = "second"
            MODULE.cmd_scan(args)
            refreshed = MODULE.load_json(root / "proposals" / f"{proposal['proposal_id']}.json")
            self.assertEqual(refreshed["status"], "rejected")
            self.assertFalse((root / "handoffs" / f"{proposal['proposal_id']}.json").exists())

    def test_stdout_mode_is_read_only(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "state"
            args = type("Args", (), {
                "sessions_root": [str(self.fixtures)], "include_claude": False, "limit": 20,
                "min_occurrences": 2, "scan_id": "preview", "state_root": str(root),
                "source_class": ["synthetic"], "since": "2020-01-01", "until": "2030-01-01",
                "stdout": True, "timezone": "UTC",
            })()
            result = MODULE.cmd_scan(args)
            self.assertEqual("stdout", result["mode"])
            self.assertIn("proposal_records", result)
            self.assertFalse(root.exists())

    def test_date_only_boundary_uses_requested_timezone(self):
        boundary = MODULE.parse_boundary("2026-07-27", end=True, timezone_name="America/New_York")
        self.assertEqual("2026-07-28T03:59:59.999999+00:00", boundary.isoformat())

    def test_persistent_scans_accumulate_repetition(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            first_root = root / "first"
            second_root = root / "second"
            first_root.mkdir()
            second_root.mkdir()
            (first_root / "one.jsonl").write_text(
                '{"type":"response_item","payload":{"role":"user","content":"Keep approved changes surgical."}}\n'
            )
            (second_root / "two.jsonl").write_text(
                '{"type":"response_item","payload":{"role":"user","content":"Keep the approved change surgical."}}\n'
            )
            args = type("Args", (), {
                "sessions_root": [str(first_root)], "include_claude": False, "limit": 20,
                "min_occurrences": 2, "scan_id": "first", "state_root": str(root / "state"),
                "source_class": ["user"], "since": None, "until": None, "stdout": False,
                "timezone": "UTC",
            })()
            MODULE.cmd_scan(args)
            self.assertEqual([], MODULE.read_proposals(root / "state"))
            args.sessions_root = [str(second_root)]
            args.scan_id = "second"
            MODULE.cmd_scan(args)
            proposals = MODULE.read_proposals(root / "state")
            self.assertEqual(1, len(proposals))
            self.assertEqual(2, proposals[0]["occurrences"])

    def test_cross_scan_semantic_variant_keeps_proposal_id(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            first_root = root / "first"
            second_root = root / "second"
            first_root.mkdir()
            second_root.mkdir()
            first_text = "Keep approved changes surgical and preserve structure."
            second_text = "Keep approved changes surgical and preserve layout."
            self.assertGreater(
                MODULE.jaccard(MODULE.semantic_tokens(first_text), MODULE.semantic_tokens(second_text)),
                0.5,
            )
            for index in range(2):
                (first_root / f"first-{index}.jsonl").write_text(
                    json.dumps({"type": "response_item", "payload": {"role": "user", "content": first_text}}) + "\n"
                )
                (second_root / f"second-{index}.jsonl").write_text(
                    json.dumps({"type": "response_item", "payload": {"role": "user", "content": second_text}}) + "\n"
                )
            args = type("Args", (), {
                "sessions_root": [str(first_root)], "include_claude": False, "limit": 20,
                "min_occurrences": 2, "scan_id": "first", "state_root": str(root / "state"),
                "source_class": ["user"], "since": None, "until": None, "stdout": False,
                "timezone": "UTC",
            })()
            MODULE.cmd_scan(args)
            first_id = MODULE.read_proposals(root / "state")[0]["proposal_id"]
            args.sessions_root = [str(second_root)]
            args.scan_id = "second"
            MODULE.cmd_scan(args)
            proposals = MODULE.read_proposals(root / "state")
            registry = MODULE.load_json(root / "state" / "proposal-registry.json")
            self.assertEqual([first_id], [item["proposal_id"] for item in proposals])
            self.assertEqual([first_id], list(registry["proposals"]))

    def test_approved_proposal_has_complete_generic_handoff_without_companions(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            proposal_id = "pc-standalone"
            proposal = {
                "proposal_id": proposal_id,
                "destination": "skill",
                "summary": "Repair the repeated workflow failure.",
                "occurrences": 3,
                "status": "staged",
                "evidence": [{
                    "session_id": "session-a",
                    "source": "/redacted/session-a.jsonl",
                    "line": 12,
                    "citation": "session-a:12",
                    "source_class": "user",
                    "snippet": "Keep the repair bounded.",
                }],
            }
            MODULE.atomic_json(root / "proposals" / f"{proposal_id}.json", proposal)
            args = type("Args", (), {
                "proposal_id": proposal_id,
                "decision": "approve",
                "note": "approved for handoff",
                "state_root": str(root),
                "available_owner": [],
            })()
            result = MODULE.cmd_decide(args)
            self.assertEqual("generic", result["routing_mode"])
            self.assertIsNone(result["selected_owner"])
            handoff = MODULE.load_json(Path(result["handoff"]))
            required = {
                "proposal_id", "evidence_references", "occurrence_count",
                "decision_note", "requested_outcome", "destination_class",
                "authority_boundary", "required_next_proof",
            }
            self.assertTrue(required.issubset(handoff))
            self.assertEqual("skill-eval-loop:capability-repair-cycle", handoff["preferred_owner"])

    def test_confirmed_companion_is_selected_but_does_not_expand_authority(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            proposal_id = "pc-preferred"
            MODULE.atomic_json(root / "proposals" / f"{proposal_id}.json", {
                "proposal_id": proposal_id,
                "destination": "agents-md",
                "summary": "Add a proven workspace rule.",
                "occurrences": 2,
                "status": "staged",
                "evidence": [],
            })
            owner = "harness-engineering:harness-engineering"
            args = type("Args", (), {
                "proposal_id": proposal_id,
                "decision": "approve",
                "note": "handoff only",
                "state_root": str(root),
                "available_owner": [owner],
            })()
            result = MODULE.cmd_decide(args)
            self.assertEqual("preferred", result["routing_mode"])
            self.assertEqual(owner, result["selected_owner"])
            handoff = MODULE.load_json(Path(result["handoff"]))
            self.assertIn("handoff record only", handoff["authority_boundary"])


if __name__ == "__main__":
    unittest.main()
