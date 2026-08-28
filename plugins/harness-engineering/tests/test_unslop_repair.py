from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SKILL_ROOT = ROOT / "skills" / "unslop-harness-repair"
SCRIPT = SKILL_ROOT / "scripts" / "unslop_repair.py"
SPEC = importlib.util.spec_from_file_location("unslop_repair", SCRIPT)
assert SPEC and SPEC.loader
unslop_repair = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(unslop_repair)


class UnslopRepairTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.base = Path(self.temp.name)
        self.source = self.base / "source"
        self.evidence = self.base / "evidence"
        self.source.mkdir()
        self.evidence.mkdir()
        self.doc = self.source / "INSTRUCTIONS.md"
        self.doc.write_text("Keep the selected harness precise. Preserve `exact-token`.\n", encoding="utf-8")
        self.audit = self.evidence / "audit.json"
        self.freeze = self.evidence / "freeze.json"
        self.ledger = self.evidence / "ledger.json"
        self.report = self.evidence / "report.json"

    def tearDown(self) -> None:
        self.temp.cleanup()

    def audit_and_freeze(self) -> None:
        self.assertEqual(
            unslop_repair.main([
                "audit", "--run-id", "test-run", "--root", str(self.source), "--output", str(self.audit)
            ]),
            0,
        )
        self.assertEqual(
            unslop_repair.main(["freeze", "--audit", str(self.audit), "--output", str(self.freeze)]),
            0,
        )

    def current_digest(self) -> str:
        roots = unslop_repair.normalize_roots([str(self.source)])
        return unslop_repair.inventory_sha256(unslop_repair.inventory(roots))

    def valid_ledger(self, approved_paths: list[Path] | None = None, created_paths: list[Path] | None = None) -> dict:
        approved = approved_paths if approved_paths is not None else [self.doc]
        created = created_paths if created_paths is not None else []
        return {
            "schema_version": 1,
            "run_id": "test-run",
            "approval": {
                "status": "approved",
                "group": "bounded-repair",
                "authority": "user",
                "evidence": "user approved bounded-repair",
                "approved_paths": [str(path) for path in approved],
                "created_paths": [str(path) for path in created],
            },
            "workers": [],
            "findings": [
                {"id": "F-001", "state": "repaired", "evidence": "Candidate removes the accepted prose defect."}
            ],
            "residuals": [
                {
                    "term": "harness",
                    "classification": "legitimate-technical",
                    "reason": "The term names the system under maintenance.",
                    "source_owner": "Harness Engineering",
                    "evidence": "The skill operates on the selected harness.",
                }
            ],
            "quality": {
                "score": 10.0,
                "floor": 8.0,
                "target": 10.0,
                "category_scores": {
                    "meaning_factual_fidelity": {"score": 2.0, "max": 2.0, "evidence": "Meaning is preserved."},
                    "protected_material": {"score": 2.0, "max": 2.0, "evidence": "Protected fingerprints match."},
                    "scope_authority": {"score": 1.5, "max": 1.5, "evidence": "All changes are approved."},
                    "finding_reconciliation": {"score": 1.5, "max": 1.5, "evidence": "Every finding is terminal."},
                    "language_quality": {"score": 2.0, "max": 2.0, "evidence": "The prose is direct and specific."},
                    "verification_evidence": {"score": 1.0, "max": 1.0, "evidence": "Behavior tests and review pass."},
                },
                "hard_gates": {
                    "fabrication_free": True,
                    "protected_material_intact": True,
                    "scope_intact": True,
                    "terminal_findings": True,
                    "p0_clear": True,
                    "authored_em_dash_free": True,
                    "unslop_engine_complete": True,
                },
            },
            "repair_waves": [{"unresolved_before": 1, "unresolved_after": 0}],
            "integrated_review": {
                "status": "clear",
                "fresh": True,
                "reviewer": "fresh-reviewer",
                "inventory_sha256": self.current_digest(),
            },
        }

    def worker_record(
        self,
        worker_id: str,
        owned_paths: list[Path],
        changed_paths: list[Path] | None = None,
        recursive_launches: int = 0,
    ) -> dict:
        return {
            "run_id": "test-run",
            "unslop_engine_sha256": unslop_repair.engine_status()["inventory_sha256"],
            "worker_id": worker_id,
            "owned_paths": [str(path) for path in owned_paths],
            "status": "complete",
            "changed_paths": [str(path) for path in (changed_paths or [])],
            "finding_dispositions": [],
            "residuals": [],
            "tests": ["worker check passed"],
            "unresolved_count": 0,
            "recursive_launches": recursive_launches,
            "risks": [],
        }

    def write_ledger(self, payload: dict) -> None:
        self.ledger.write_text(json.dumps(payload), encoding="utf-8")

    def verify(self) -> int:
        return unslop_repair.main([
            "verify", "--freeze", str(self.freeze), "--ledger", str(self.ledger), "--output", str(self.report)
        ])

    def test_audit_is_read_only(self) -> None:
        before = self.doc.read_bytes()
        self.assertEqual(
            unslop_repair.main([
                "audit", "--run-id", "test-run", "--root", str(self.source), "--output", str(self.audit)
            ]),
            0,
        )
        self.assertEqual(self.doc.read_bytes(), before)

    def test_bundled_engine_is_complete_and_independent(self) -> None:
        status = unslop_repair.engine_status()
        self.assertEqual(status["status"], "complete")
        self.assertEqual(status["file_count"], 19)
        self.assertFalse(status["runtime_dependency_on_writing_quality"])
        manifest = json.loads((SKILL_ROOT / "references/unslop-engine-manifest.json").read_text(encoding="utf-8"))
        self.assertFalse(manifest["runtime_dependency_on_writing_quality"])
        self.assertEqual(len(manifest["files"]), 19)

    def test_full_workflow_is_mandatory_and_third_party_terms_are_preserved(self) -> None:
        skill_text = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
        contract_text = (SKILL_ROOT / "references/unslop-engine-contract.md").read_text(encoding="utf-8")
        notices = (SKILL_ROOT / "references/unslop-engine/THIRD_PARTY_NOTICES.md").read_text(encoding="utf-8")
        self.assertIn("four-phase workflow", skill_text)
        self.assertIn("mandatory runtime policy", skill_text)
        self.assertIn("Load [workflow.md]", contract_text)
        self.assertIn("Copyright (c) 2025 Hardik Pandya", notices)
        self.assertIn("Copyright (c) 2025 Siqi Chen", notices)
        self.assertIn("Copyright (c) 2026 Peter Yang", notices)
        self.assertIn("Copyright (c) 2026 Conor Bronsdon", notices)
        self.assertIn("Creative Commons Attribution-ShareAlike 4.0 International", notices)
        self.assertIn("revision 1371562925", notices)
        worker_contract = (SKILL_ROOT / "references/worker-contract.md").read_text(encoding="utf-8")
        return_packet = worker_contract.split("## Return packet", 1)[1].split("## Parent reconciliation", 1)[0]
        self.assertIn('"unslop_engine_sha256": "PINNED_ENGINE_SHA256"', return_packet)
        workflow = (SKILL_ROOT / "references/unslop-engine/workflow.md").read_text(encoding="utf-8")
        self.assertIn("required audit mode before approval", workflow)
        self.assertIn("8/10 minimum", workflow)
        self.assertIn("Target 10/10", workflow)
        self.assertNotIn("REWRITE** (default)", workflow)
        self.assertNotIn("Run `scripts/unslop-engine/emdash_replacer.py` on ALL output", workflow)

    def test_local_scan_uses_bundled_unslop_engine(self) -> None:
        scan_input = self.source / "draft.md"
        scan_output = self.evidence / "scan.json"
        scan_input.write_text(
            "Certainly! This groundbreaking paradigm shift serves as a robust solution. Perhaps it helps.\n",
            encoding="utf-8",
        )
        self.assertEqual(
            unslop_repair.main(["scan", "--input", str(scan_input), "--output", str(scan_output)]),
            0,
        )
        payload = json.loads(scan_output.read_text(encoding="utf-8"))
        self.assertEqual(payload["mode"], "detect")
        self.assertFalse(payload["runtime_dependency_on_writing_quality"])
        self.assertGreater(payload["raw_result"]["ai_tell_count"], 0)
        self.assertEqual(
            set(payload["raw_result"]["issues"]),
            {
                "emdash",
                "ai_tells",
                "cliches",
                "hedges",
                "copula",
                "ing_constructions",
                "significance",
                "sycophancy",
                "curly_quotes",
                "negative_parallelisms",
                "rule_of_three",
                "generic_conclusions",
                "structural_slop",
            },
        )

    def test_engine_runs_from_isolated_skill_copy_and_detects_tampering(self) -> None:
        isolated = self.base / "isolated-skill"
        shutil.copytree(SKILL_ROOT, isolated)
        isolated_script = isolated / "scripts/unslop_repair.py"
        complete = subprocess.run(
            [sys.executable, str(isolated_script), "engine-check"],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(complete.returncode, 0, complete.stderr)
        sample = self.source / "isolated.md"
        result = self.evidence / "isolated-scan.json"
        sample.write_text("A groundbreaking paradigm shift.\n", encoding="utf-8")
        scan = subprocess.run(
            [sys.executable, str(isolated_script), "scan", "--input", str(sample), "--output", str(result)],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(scan.returncode, 0, scan.stderr)
        engine_file = isolated / "references/unslop-engine/unslop-policy.md"
        engine_file.write_text(engine_file.read_text(encoding="utf-8") + "Changed.\n", encoding="utf-8")
        tampered = subprocess.run(
            [sys.executable, str(isolated_script), "engine-check"],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(tampered.returncode, 2)
        self.assertIn("hash mismatch", tampered.stderr)

    def test_bundled_voice_protection_and_punctuation_tools_run(self) -> None:
        engine_scripts = SKILL_ROOT / "scripts/unslop-engine"
        source = self.source / "voice.md"
        source.write_text("I think this works. But I want it clearer.\n", encoding="utf-8")
        profile = self.evidence / "voice.json"
        voice = subprocess.run(
            [sys.executable, str(engine_scripts / "voice_profiler.py"), str(source), "--output", str(profile)],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(voice.returncode, 0, voice.stderr)
        self.assertIn("tone", json.loads(profile.read_text(encoding="utf-8")))
        after = self.source / "voice-after.md"
        after.write_text("I think this works. Keep `exact-token`.\n", encoding="utf-8")
        source.write_text("I think this works. Keep `exact-token`.\n", encoding="utf-8")
        protected = subprocess.run(
            [sys.executable, str(engine_scripts / "protected_material_validator.py"), str(source), str(after)],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(protected.returncode, 0, protected.stderr)
        punctuation = subprocess.run(
            [sys.executable, str(engine_scripts / "emdash_replacer.py"), "--text", "One \u2014 two"],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(punctuation.returncode, 0, punctuation.stderr)
        self.assertNotIn("\u2014", punctuation.stdout)

    def test_freeze_refuses_post_audit_drift(self) -> None:
        self.assertEqual(
            unslop_repair.main([
                "audit", "--run-id", "test-run", "--root", str(self.source), "--output", str(self.audit)
            ]),
            0,
        )
        self.doc.write_text("Changed before freeze.\n", encoding="utf-8")
        self.assertEqual(unslop_repair.main(["freeze", "--audit", str(self.audit), "--output", str(self.freeze)]), 2)

    def test_qualified_repair_passes(self) -> None:
        self.audit_and_freeze()
        self.doc.write_text("Keep the selected harness exact. Preserve `exact-token`.\n", encoding="utf-8")
        self.write_ledger(self.valid_ledger())
        self.assertEqual(self.verify(), 0)
        self.assertEqual(json.loads(self.report.read_text())["status"], "qualified")

    def test_missing_approval_fails(self) -> None:
        self.audit_and_freeze()
        payload = self.valid_ledger()
        payload["approval"]["status"] = "pending"
        self.write_ledger(payload)
        self.assertEqual(self.verify(), 2)

    def test_approval_requires_user_authority_and_evidence(self) -> None:
        self.audit_and_freeze()
        for field, value in (("authority", "agent"), ("evidence", "")):
            with self.subTest(field=field):
                payload = self.valid_ledger()
                payload["approval"][field] = value
                self.write_ledger(payload)
                self.assertEqual(self.verify(), 2)

    def test_changed_path_outside_approval_fails(self) -> None:
        other = self.source / "reference.md"
        other.write_text("Original.\n", encoding="utf-8")
        self.audit_and_freeze()
        other.write_text("Changed.\n", encoding="utf-8")
        payload = self.valid_ledger(approved_paths=[self.doc])
        payload["integrated_review"]["inventory_sha256"] = self.current_digest()
        self.write_ledger(payload)
        self.assertEqual(self.verify(), 2)

    def test_path_outside_frozen_roots_fails(self) -> None:
        self.audit_and_freeze()
        outside = self.base / "unnamed-plugin" / "SKILL.md"
        payload = self.valid_ledger(approved_paths=[outside])
        self.write_ledger(payload)
        self.assertEqual(self.verify(), 2)

    def test_more_than_three_workers_fails(self) -> None:
        self.audit_and_freeze()
        payload = self.valid_ledger()
        payload["workers"] = [
            self.worker_record(f"w{index}", [self.doc])
            for index in range(4)
        ]
        self.write_ledger(payload)
        self.assertEqual(self.verify(), 2)

    def test_overlapping_worker_paths_fail(self) -> None:
        self.audit_and_freeze()
        payload = self.valid_ledger()
        payload["workers"] = [
            self.worker_record("w1", [self.source]),
            self.worker_record("w2", [self.doc]),
        ]
        payload["approval"]["approved_paths"] = [str(self.source)]
        self.write_ledger(payload)
        self.assertEqual(self.verify(), 2)

    def test_worker_cannot_claim_a_parent_of_approved_path(self) -> None:
        self.audit_and_freeze()
        payload = self.valid_ledger()
        payload["workers"] = [self.worker_record("w1", [self.source])]
        self.write_ledger(payload)
        self.assertEqual(self.verify(), 2)

    def test_recursive_worker_launch_fails(self) -> None:
        self.audit_and_freeze()
        payload = self.valid_ledger()
        payload["workers"] = [self.worker_record("w1", [self.doc], recursive_launches=1)]
        self.write_ledger(payload)
        self.assertEqual(self.verify(), 2)

    def test_worker_changed_path_must_match_candidate(self) -> None:
        other = self.source / "other.md"
        other.write_text("Unchanged.\n", encoding="utf-8")
        self.audit_and_freeze()
        payload = self.valid_ledger(approved_paths=[self.source])
        payload["workers"] = [self.worker_record("w1", [self.source], changed_paths=[other])]
        self.write_ledger(payload)
        self.assertEqual(self.verify(), 2)

    def test_worker_run_id_and_residuals_are_required(self) -> None:
        self.audit_and_freeze()
        for field in ("run_id", "residuals", "unslop_engine_sha256"):
            with self.subTest(field=field):
                payload = self.valid_ledger()
                worker = self.worker_record("w1", [self.doc])
                del worker[field]
                payload["workers"] = [worker]
                self.write_ledger(payload)
                self.assertEqual(self.verify(), 2)

    def test_worker_cannot_claim_parent_authority(self) -> None:
        self.audit_and_freeze()
        for field, value in (
            ("may_install", True),
            ("installed", True),
            ("declares_complete", True),
            ("authority", {"may_integrate": True}),
        ):
            with self.subTest(field=field):
                payload = self.valid_ledger()
                worker = self.worker_record("w1", [self.doc])
                worker[field] = value
                payload["workers"] = [worker]
                self.write_ledger(payload)
                self.assertEqual(self.verify(), 2)

    def test_unresolved_finding_fails(self) -> None:
        self.audit_and_freeze()
        payload = self.valid_ledger()
        payload["findings"] = [{"id": "F-001", "state": "unresolved"}]
        self.write_ledger(payload)
        self.assertEqual(self.verify(), 2)

    def test_unclassified_residual_fails(self) -> None:
        self.audit_and_freeze()
        payload = self.valid_ledger()
        payload["residuals"][0]["classification"] = "ignored"
        self.write_ledger(payload)
        self.assertEqual(self.verify(), 2)

    def test_protected_material_drift_fails(self) -> None:
        protected_examples = [
            ("Keep `exact-token`.\n", "Keep `changed-token`.\n"),
            ("Keep ``exact ` token``.\n", "Keep ``changed ` token``.\n"),
            ('Keep "quoted text".\n', 'Keep "changed quote".\n'),
            ("Keep **exact phrase**.\n", "Keep **changed phrase**.\n"),
            ("“Exact first line\nexact second line”\n", "“Exact first line\nchanged second line”\n"),
            ("> Exact first line\nexact continuation\n", "> Exact first line\nchanged continuation\n"),
            ("    exact indented code\n", "    changed indented code\n"),
            ("Keep [label](https://example.com/a).\n", "Keep [label](https://example.com/b).\n"),
            ("| Key | Value |\n| --- | --- |\n| A | B |\n", "| Key | Value |\n| --- | --- |\n| A | C |\n"),
            ("Key | Value\n--- | ---\nA | B\n", "Key | Value\n--- | ---\nA | C\n"),
            ("````markdown\n```inner\nexact\n```\n````\n", "````markdown\n```inner\nchanged\n```\n````\n"),
            ("Keep /absolute/path/file.md.\n", "Keep /absolute/path/other.md.\n"),
            ("Use writing-quality:writing-quality-router.\n", "Use writing-quality:writing-enforcer.\n"),
        ]
        for original, changed in protected_examples:
            with self.subTest(original=original):
                self.doc.write_text(original, encoding="utf-8")
                self.audit_and_freeze()
                self.doc.write_text(changed, encoding="utf-8")
                payload = self.valid_ledger()
                payload["integrated_review"]["inventory_sha256"] = self.current_digest()
                self.write_ledger(payload)
                self.assertEqual(self.verify(), 2)

    def test_unbolding_preserves_and_accepts_frozen_strong_content(self) -> None:
        self.doc.write_text("Keep **this exact phrase**.\n", encoding="utf-8")
        self.audit_and_freeze()
        self.doc.write_text("Keep this exact phrase.\n", encoding="utf-8")
        payload = self.valid_ledger()
        payload["integrated_review"]["inventory_sha256"] = self.current_digest()
        self.write_ledger(payload)
        self.assertEqual(self.verify(), 0)

    def test_unbolding_cannot_change_frozen_strong_content(self) -> None:
        self.doc.write_text("Keep **this exact phrase**.\n", encoding="utf-8")
        self.audit_and_freeze()
        self.doc.write_text("Keep a changed phrase.\n", encoding="utf-8")
        payload = self.valid_ledger()
        payload["integrated_review"]["inventory_sha256"] = self.current_digest()
        self.write_ledger(payload)
        self.assertEqual(self.verify(), 2)

    def test_existing_plain_duplicate_cannot_hide_changed_strong_content(self) -> None:
        self.doc.write_text(
            "Keep **this exact phrase** and this exact phrase elsewhere.\n",
            encoding="utf-8",
        )
        self.audit_and_freeze()
        self.doc.write_text(
            "Keep **changed words here** and this exact phrase elsewhere.\n",
            encoding="utf-8",
        )
        payload = self.valid_ledger()
        payload["integrated_review"]["inventory_sha256"] = self.current_digest()
        self.write_ledger(payload)
        self.assertEqual(self.verify(), 2)

    def test_multiline_strong_content_can_be_unbolded_but_not_changed(self) -> None:
        original = "Keep **this exact first line\nand exact second line** here.\n"
        self.doc.write_text(original, encoding="utf-8")
        self.audit_and_freeze()

        self.doc.write_text(
            "Keep this exact first line\nand exact second line here.\n",
            encoding="utf-8",
        )
        payload = self.valid_ledger()
        payload["integrated_review"]["inventory_sha256"] = self.current_digest()
        self.write_ledger(payload)
        self.assertEqual(self.verify(), 0)

        self.doc.write_text(original, encoding="utf-8")
        self.audit_and_freeze()
        self.doc.write_text(
            "Keep **this exact first line\nand a changed second line** here.\n",
            encoding="utf-8",
        )
        payload = self.valid_ledger()
        payload["integrated_review"]["inventory_sha256"] = self.current_digest()
        self.write_ledger(payload)
        self.assertEqual(self.verify(), 2)

    def test_retained_bold_content_still_passes(self) -> None:
        self.doc.write_text("Keep **this exact phrase** here.\n", encoding="utf-8")
        self.audit_and_freeze()
        self.doc.write_text("Please keep **this exact phrase** here.\n", encoding="utf-8")
        payload = self.valid_ledger()
        payload["integrated_review"]["inventory_sha256"] = self.current_digest()
        self.write_ledger(payload)
        self.assertEqual(self.verify(), 0)

    def test_structured_data_change_fails_without_exact_approval(self) -> None:
        structured = self.source / "metadata.json"
        structured.write_text('{"count": 1}\n', encoding="utf-8")
        self.audit_and_freeze()
        structured.write_text('{"count": 2}\n', encoding="utf-8")
        payload = self.valid_ledger(approved_paths=[structured])
        payload["integrated_review"]["inventory_sha256"] = self.current_digest()
        self.write_ledger(payload)
        self.assertEqual(self.verify(), 2)

    def test_protected_change_cannot_be_approved_inside_repair(self) -> None:
        self.doc.write_text('Keep "original metadata".\n', encoding="utf-8")
        self.audit_and_freeze()
        self.doc.write_text('Keep "approved metadata".\n', encoding="utf-8")
        payload = self.valid_ledger()
        payload["approved_protected_changes"] = []
        payload["integrated_review"]["inventory_sha256"] = self.current_digest()
        self.write_ledger(payload)
        self.assertEqual(self.verify(), 2)

    def test_protected_delimiter_suffix_corruption_fails(self) -> None:
        examples = [
            ("Keep `exact-token`.\n", "Keep `exact-token`1.\n"),
            ('Keep "exact phrase".\n', 'Keep "exact phrase"1.\n'),
            ("Keep **exact phrase**.\n", "Keep **exact phrase**1.\n"),
        ]
        for original, corrupted in examples:
            with self.subTest(original=original):
                self.doc.write_text(original, encoding="utf-8")
                self.audit_and_freeze()
                self.doc.write_text(corrupted, encoding="utf-8")
                payload = self.valid_ledger()
                payload["integrated_review"]["inventory_sha256"] = self.current_digest()
                self.write_ledger(payload)
                self.assertEqual(self.verify(), 2)

    def test_approved_created_path_passes(self) -> None:
        self.audit_and_freeze()
        created = self.source / "new-reference.md"
        created.write_text("Precise new guidance.\n", encoding="utf-8")
        payload = self.valid_ledger(created_paths=[created])
        payload["integrated_review"]["inventory_sha256"] = self.current_digest()
        self.write_ledger(payload)
        self.assertEqual(self.verify(), 0)

    def test_valid_markdown_fences_and_separate_tokens_do_not_false_positive(self) -> None:
        self.audit_and_freeze()
        created = self.source / "valid-reference.md"
        created.write_text(
            "Use `first` and `second`. Keep \"left\": 1 and \"right\": 2.\n\n```bash\nprintf 'ok'\n```\n\n```json\n{}\n```\n",
            encoding="utf-8",
        )
        payload = self.valid_ledger(created_paths=[created])
        payload["integrated_review"]["inventory_sha256"] = self.current_digest()
        self.write_ledger(payload)
        self.assertEqual(self.verify(), 0)

    def test_created_unclosed_fence_fails(self) -> None:
        self.audit_and_freeze()
        created = self.source / "broken-reference.md"
        created.write_text("```bash\nprintf 'broken'\n```1\n", encoding="utf-8")
        payload = self.valid_ledger(created_paths=[created])
        payload["integrated_review"]["inventory_sha256"] = self.current_digest()
        self.write_ledger(payload)
        self.assertEqual(self.verify(), 2)

    def test_created_file_with_em_dash_fails(self) -> None:
        self.audit_and_freeze()
        created = self.source / "new-reference.md"
        created.write_text("New prose \u2014 with an authored em dash.\n", encoding="utf-8")
        payload = self.valid_ledger(created_paths=[created])
        payload["integrated_review"]["inventory_sha256"] = self.current_digest()
        self.write_ledger(payload)
        self.assertEqual(self.verify(), 2)

    def test_score_below_eight_fails(self) -> None:
        self.audit_and_freeze()
        payload = self.valid_ledger()
        payload["quality"]["score"] = 7.9
        self.write_ledger(payload)
        self.assertEqual(self.verify(), 2)

    def test_quality_category_total_must_match_score(self) -> None:
        self.audit_and_freeze()
        payload = self.valid_ledger()
        payload["quality"]["category_scores"]["language_quality"]["score"] = 1.5
        self.write_ledger(payload)
        self.assertEqual(self.verify(), 2)

    def test_failed_hard_gate_fails(self) -> None:
        self.audit_and_freeze()
        payload = self.valid_ledger()
        payload["quality"]["hard_gates"]["fabrication_free"] = False
        self.write_ledger(payload)
        self.assertEqual(self.verify(), 2)

    def test_no_progress_wave_fails(self) -> None:
        self.audit_and_freeze()
        payload = self.valid_ledger()
        payload["repair_waves"] = [{"unresolved_before": 1, "unresolved_after": 1}]
        self.write_ledger(payload)
        self.assertEqual(self.verify(), 2)

    def test_stale_integrated_review_fails(self) -> None:
        self.audit_and_freeze()
        payload = self.valid_ledger()
        payload["integrated_review"]["inventory_sha256"] = "0" * 64
        self.write_ledger(payload)
        self.assertEqual(self.verify(), 2)


if __name__ == "__main__":
    unittest.main()
