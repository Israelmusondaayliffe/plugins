import importlib.util
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "skill_eval_loop.py"
SPEC = importlib.util.spec_from_file_location("skill_eval_loop", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(MODULE)


class SkillEvalLoopTests(unittest.TestCase):
    def initialized_target(self, root: Path):
        target = root / "target"
        target.mkdir()
        (target / "SKILL.md").write_text("fixture", encoding="utf-8")
        state_root = root / "state"
        MODULE.cmd_init(type("Args", (), {"target": str(target), "state_root": str(state_root)})())
        directory = MODULE.target_dir(target, state_root)
        suite = json.loads((Path(__file__).resolve().parents[1] / "fixtures" / "suite-valid.json").read_text())
        suite["target"] = str(target)
        suite["limits"] = {"max_iterations": 5, "max_minutes": 10, "max_tokens": 100}
        MODULE.atomic_json(directory / "suite.json", suite)
        return target, state_root, directory, suite

    def run_args(
        self, target: Path, state_root: Path, run_id: str, token_usage=None,
        case_results=None, rubric_results=None, evaluator_mode="auto", candidate=None,
    ):
        return type("Args", (), {
            "target": str(target),
            "state_root": str(state_root),
            "suite": None,
            "candidate": str(candidate) if candidate else None,
            "case_results": str(case_results) if case_results else None,
            "rubric_results": str(rubric_results) if rubric_results else None,
            "run_id": run_id,
            "token_usage": token_usage,
            "evaluator_mode": evaluator_mode,
        })()

    def passing_evidence(self, root: Path, suite: dict):
        case_path = root / "cases.json"
        rubric_path = root / "rubric.json"
        MODULE.atomic_json(case_path, {
            "results": [
                {"id": case["id"], "passed": True, "evidence": "fixture"}
                for case in suite["trigger_cases"] + suite["functional_cases"]
            ]
        })
        MODULE.atomic_json(rubric_path, {
            "results": [{"id": "r1", "passed": True, "evidence": "independent fixture"}]
        })
        return case_path, rubric_path

    def test_valid_suite_passes(self):
        suite = json.loads((Path(__file__).resolve().parents[1] / "fixtures" / "suite-valid.json").read_text())
        self.assertEqual([], MODULE.validate_suite_payload(suite))

    def test_suite_rejects_missing_negative_cases(self):
        suite = json.loads((Path(__file__).resolve().parents[1] / "fixtures" / "suite-valid.json").read_text())
        suite["trigger_cases"] = [case for case in suite["trigger_cases"] if case["should_trigger"]]
        self.assertTrue(any("stay-silent" in item for item in MODULE.validate_suite_payload(suite)))

    def test_suite_requires_target_path(self):
        suite = json.loads((Path(__file__).resolve().parents[1] / "fixtures" / "suite-valid.json").read_text())
        suite["target"] = ""
        self.assertIn("target must be a non-empty path string", MODULE.validate_suite_payload(suite))

    def test_result_file_requires_complete_evidence(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "results.json"
            path.write_text(json.dumps({"results": [{"id": "a", "passed": True, "evidence": "trace 1"}]}))
            results, errors = MODULE.validate_result_file(path, {"a", "b"}, "cases")
            self.assertEqual(1, len(results))
            self.assertTrue(any("missing IDs" in item for item in errors))

    def test_init_does_not_modify_target(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            target = root / "target"
            target.mkdir()
            (target / "SKILL.md").write_text("fixture")
            before = MODULE.fingerprint(target)
            args = type("Args", (), {"target": str(target), "state_root": str(root / "state")})()
            MODULE.cmd_init(args)
            self.assertEqual(before, MODULE.fingerprint(target))

    def test_reinitialization_does_not_reset_iteration(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            target, state_root, directory, _ = self.initialized_target(root)
            state = MODULE.load_json(directory / "state.json")
            state["iteration"] = 4
            state["status"] = "needs_repair"
            MODULE.atomic_json(directory / "state.json", state)
            result = MODULE.cmd_init(type("Args", (), {
                "target": str(target), "state_root": str(state_root)
            })())
            self.assertFalse(result["initialized"])
            self.assertEqual(4, MODULE.load_json(directory / "state.json")["iteration"])

    def test_token_budget_exhaustion_stops_safely(self):
        with tempfile.TemporaryDirectory() as temp:
            target, state_root, _, suite = self.initialized_target(Path(temp))
            case_path = Path(temp) / "cases.json"
            rubric_path = Path(temp) / "rubric.json"
            MODULE.atomic_json(case_path, {
                "results": [
                    {"id": case["id"], "passed": True, "evidence": "fixture"}
                    for case in suite["trigger_cases"] + suite["functional_cases"]
                ]
            })
            MODULE.atomic_json(rubric_path, {
                "results": [
                    {"id": "r1", "passed": True, "evidence": "independent fixture"}
                ]
            })
            analysis = {"summary": {"score": 90, "grade": "A"}, "checks": []}
            with mock.patch.object(MODULE, "plugin_eval_analyze", return_value=(analysis, 0.1)):
                result = MODULE.cmd_run(self.run_args(target, state_root, "budget", 101, case_path, rubric_path))
            self.assertEqual(result["stop_reason"], "token_limit")
            self.assertEqual(result["status"], "exhausted")

    def test_candidate_below_pinned_baseline_cannot_pass(self):
        with tempfile.TemporaryDirectory() as temp:
            target, state_root, directory, suite = self.initialized_target(Path(temp))
            MODULE.atomic_json(
                directory / "baseline.json",
                {"schema_version": 1, "pinned_run_id": "base", "score": 95},
            )
            case_path = Path(temp) / "cases.json"
            rubric_path = Path(temp) / "rubric.json"
            MODULE.atomic_json(case_path, {
                "results": [
                    {"id": case["id"], "passed": True, "evidence": "fixture"}
                    for case in suite["trigger_cases"] + suite["functional_cases"]
                ]
            })
            MODULE.atomic_json(rubric_path, {
                "results": [
                    {"id": "r1", "passed": True, "evidence": "independent fixture"}
                ]
            })
            analysis = {"summary": {"score": 90, "grade": "A"}, "checks": []}
            with mock.patch.object(MODULE, "plugin_eval_analyze", return_value=(analysis, 0.1)):
                result = MODULE.cmd_run(self.run_args(target, state_root, "regression", 50, case_path, rubric_path))
            self.assertEqual(result["status"], "needs_repair")
            diff = json.loads((directory / "runs" / "regression" / "diff.json").read_text())
            self.assertEqual(diff["score_delta"], -5)

    def test_repeated_failure_signature_stops(self):
        with tempfile.TemporaryDirectory() as temp:
            target, state_root, _, _ = self.initialized_target(Path(temp))
            analysis = {"summary": {"score": 90, "grade": "A"}, "checks": []}
            with mock.patch.object(MODULE, "plugin_eval_analyze", return_value=(analysis, 0.1)):
                MODULE.cmd_run(self.run_args(target, state_root, "repeat-1", 1))
                MODULE.cmd_run(self.run_args(target, state_root, "repeat-2", 1))
                result = MODULE.cmd_run(self.run_args(target, state_root, "repeat-3", 1))
            self.assertEqual(result["stop_reason"], "repeated_failure_signature")

    def test_approval_refusal_blocks_promotion(self):
        with tempfile.TemporaryDirectory() as temp:
            target, state_root, _, _ = self.initialized_target(Path(temp))
            args = type("Args", (), {
                "approval": "NO",
                "target": str(target),
                "staged": str(target),
                "run_id": "none",
                "expected_source_fingerprint": MODULE.fingerprint(target),
                "state_root": str(state_root),
            })()
            with self.assertRaisesRegex(MODULE.LoopError, "explicit user approval"):
                MODULE.cmd_promote(args)

    def test_missing_evaluator_is_safe_error(self):
        with tempfile.TemporaryDirectory() as temp:
            previous = os.environ.get("PLUGIN_EVAL_ROOT")
            os.environ["PLUGIN_EVAL_ROOT"] = temp
            try:
                with self.assertRaisesRegex(MODULE.LoopError, "CLI is missing"):
                    MODULE.resolve_plugin_eval()
            finally:
                if previous is None:
                    os.environ.pop("PLUGIN_EVAL_ROOT", None)
                else:
                    os.environ["PLUGIN_EVAL_ROOT"] = previous

    def test_zero_companion_run_reaches_terminal_local_receipt(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            target, state_root, directory, suite = self.initialized_target(root)
            case_path, rubric_path = self.passing_evidence(root, suite)
            missing_eval = root / "missing-plugin-eval"
            missing_eval.mkdir()
            with mock.patch.dict(os.environ, {"PLUGIN_EVAL_ROOT": str(missing_eval)}):
                result = MODULE.cmd_run(self.run_args(
                    target, state_root, "local-pass", 50, case_path, rubric_path
                ))
            self.assertEqual("passed", result["status"])
            self.assertEqual("local_pass", result["stop_reason"])
            receipt = MODULE.load_json(directory / "runs" / "local-pass" / "receipt.json")
            self.assertEqual("evaluator_unavailable", receipt["evaluator_status"])
            self.assertEqual("local", receipt["effective_evaluator_mode"])
            self.assertIsNone(receipt["plugin_eval_score"])
            self.assertIsNone(receipt["plugin_eval_grade"])
            self.assertTrue(receipt["local_baseline_comparison"]["no_regression"])

    def test_local_result_compares_pinned_case_and_rubric_baseline(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            target, state_root, directory, suite = self.initialized_target(root)
            MODULE.atomic_json(directory / "baseline.json", {
                "schema_version": 1,
                "target": str(target),
                "pinned_run_id": "local-base",
                "score": None,
                "case_summary": {"pass_rate": 1.0},
                "rubric_summary": {"pass_rate": 1.0},
            })
            case_path, rubric_path = self.passing_evidence(root, suite)
            cases = MODULE.load_json(case_path)
            cases["results"][0]["passed"] = False
            MODULE.atomic_json(case_path, cases)
            result = MODULE.cmd_run(self.run_args(
                target, state_root, "local-regression", 50, case_path, rubric_path,
                evaluator_mode="local",
            ))
            self.assertEqual("needs_repair", result["status"])
            diff = MODULE.load_json(directory / "runs" / "local-regression" / "diff.json")
            self.assertLess(diff["case_pass_rate_delta"], 0)
            receipt = MODULE.load_json(directory / "runs" / "local-regression" / "receipt.json")
            self.assertFalse(receipt["local_baseline_comparison"]["no_regression"])

    def test_enhanced_analyzer_adds_score_when_available(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            target, state_root, directory, suite = self.initialized_target(root)
            case_path, rubric_path = self.passing_evidence(root, suite)
            analysis = {"summary": {"score": 92, "grade": "A"}, "checks": []}
            with mock.patch.object(MODULE, "plugin_eval_analyze", return_value=(analysis, 0.2)):
                result = MODULE.cmd_run(self.run_args(
                    target, state_root, "enhanced-pass", 50, case_path, rubric_path,
                    evaluator_mode="enhanced",
                ))
            self.assertEqual("passed", result["status"])
            self.assertEqual("full_pass", result["stop_reason"])
            receipt = MODULE.load_json(directory / "runs" / "enhanced-pass" / "receipt.json")
            self.assertEqual("available", receipt["evaluator_status"])
            self.assertEqual(92, receipt["plugin_eval_score"])
            self.assertEqual("A", receipt["plugin_eval_grade"])

    def test_source_change_after_init_blocks_run(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            target, state_root, _, _ = self.initialized_target(root)
            (target / "SKILL.md").write_text("changed", encoding="utf-8")
            with self.assertRaisesRegex(MODULE.LoopError, "source fingerprint changed"):
                MODULE.cmd_run(self.run_args(target, state_root, "stale-source"))

    def test_candidate_must_be_owned_staging_copy(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            target, state_root, _, _ = self.initialized_target(root)
            arbitrary = root / "arbitrary-candidate"
            arbitrary.mkdir()
            (arbitrary / "SKILL.md").write_text("candidate", encoding="utf-8")
            with self.assertRaisesRegex(MODULE.LoopError, "staging copy"):
                MODULE.cmd_run(self.run_args(
                    target, state_root, "arbitrary", candidate=arbitrary
                ))

    def test_stage_requires_failed_or_review_state(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            target, state_root, _, _ = self.initialized_target(root)
            with self.assertRaisesRegex(MODULE.LoopError, "failed or needs-review"):
                MODULE.cmd_stage(type("Args", (), {
                    "target": str(target), "state_root": str(state_root), "stage_id": "early"
                })())

    def test_promotion_requires_pinned_passing_run(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            target, state_root, directory, suite = self.initialized_target(root)
            state = MODULE.load_json(directory / "state.json")
            state["status"] = "needs_repair"
            MODULE.atomic_json(directory / "state.json", state)
            staged_info = MODULE.cmd_stage(type("Args", (), {
                "target": str(target), "state_root": str(state_root), "stage_id": "candidate"
            })())
            staged = Path(staged_info["staged_path"])
            case_path, rubric_path = self.passing_evidence(root, suite)
            missing_eval = root / "missing-plugin-eval"
            missing_eval.mkdir()
            with mock.patch.dict(os.environ, {"PLUGIN_EVAL_ROOT": str(missing_eval)}):
                MODULE.cmd_run(self.run_args(
                    target, state_root, "candidate-pass", 50, case_path, rubric_path,
                    candidate=staged,
                ))
            args = type("Args", (), {
                "approval": "APPROVED",
                "target": str(target),
                "staged": str(staged),
                "run_id": "candidate-pass",
                "expected_source_fingerprint": MODULE.fingerprint(target),
                "state_root": str(state_root),
            })()
            with self.assertRaisesRegex(MODULE.LoopError, "pinned as the baseline"):
                MODULE.cmd_promote(args)
            MODULE.cmd_pin_baseline(type("Args", (), {
                "target": str(target), "run_id": "candidate-pass", "state_root": str(state_root)
            })())
            self.assertEqual("candidate-pass", MODULE.load_json(directory / "baseline.json")["pinned_run_id"])

    def test_promotion_rejects_staged_bytes_changed_after_passing_run(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            target, state_root, directory, suite = self.initialized_target(root)
            state = MODULE.load_json(directory / "state.json")
            state["status"] = "needs_repair"
            MODULE.atomic_json(directory / "state.json", state)
            staged_info = MODULE.cmd_stage(type("Args", (), {
                "target": str(target),
                "state_root": str(state_root),
                "stage_id": "mutated-candidate",
            })())
            staged = Path(staged_info["staged_path"])
            case_path, rubric_path = self.passing_evidence(root, suite)
            MODULE.cmd_run(self.run_args(
                target,
                state_root,
                "mutated-candidate-pass",
                50,
                case_path,
                rubric_path,
                evaluator_mode="local",
                candidate=staged,
            ))
            MODULE.cmd_pin_baseline(type("Args", (), {
                "target": str(target),
                "run_id": "mutated-candidate-pass",
                "state_root": str(state_root),
            })())
            target_before = MODULE.fingerprint(target)
            (staged / "SKILL.md").write_text("changed after passing", encoding="utf-8")
            args = type("Args", (), {
                "approval": "APPROVED",
                "target": str(target),
                "staged": str(staged),
                "run_id": "mutated-candidate-pass",
                "expected_source_fingerprint": target_before,
                "state_root": str(state_root),
            })()
            with self.assertRaisesRegex(MODULE.LoopError, "staged candidate fingerprint changed"):
                MODULE.cmd_promote(args)
            self.assertEqual(target_before, MODULE.fingerprint(target))


if __name__ == "__main__":
    unittest.main()
