from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


CONTRACT = load_module(
    "visual_contract_validator",
    ROOT / "skills/visual-fidelity-gate/scripts/validate_visual_contract.py",
)
REVIEW = load_module(
    "visual_review_validator",
    ROOT / "skills/visual-fidelity-gate/scripts/validate_visual_review.py",
)


PNG = b"\x89PNG\r\n\x1a\ncontrolled-test-payload"


FAILURE_CASES = (
    {
        "id": "gargantua",
        "score": 2,
        "objective": "GARGANTUA black-hole raytracer hero must hold a recognizable lensing silhouette, not terrain-like output.",
        "first_glance": "A stable black sphere and thin luminous disk read as a black hole before any controls are read.",
        "gap": "GARGANTUA reads as thick orange terrain rather than a recognizable black hole.",
        "next_action": "Record the failed raytracer method and switch it before any secondary features.",
    },
    {
        "id": "procedural-ocean",
        "score": 3,
        "objective": "Procedural open-sea hero must make the violent state read as ocean rather than terrain.",
        "first_glance": "Violent open sea, breaking crests, and atmospheric depth read immediately at the hero frame.",
        "gap": "The violent ocean state reads as rounded reflective terrain rather than open sea.",
        "next_action": "Record the failed procedural method and switch it before any secondary features.",
    },
    {
        "id": "video-hero",
        "score": 4,
        "objective": "Video Hero Showcase must use a convincing cinematic hero medium instead of primitive procedural stand-ins.",
        "first_glance": "A distinct cinematic subject and material treatment carry the first screen without labels or controls.",
        "gap": "The video hero uses primitive procedural stand-ins and misses the cinematic material target.",
        "next_action": "Record the failed procedural medium and switch to a higher-fidelity video or hybrid method.",
    },
)


def valid_contract(
    root: Path,
    *,
    objective: str = "Build a cinematic black-hole hero from the supplied reference.",
    first_glance: str = "A bright asymmetric accretion disk bends around a deep black center.",
) -> dict:
    source_path = root / "hero-source.txt"
    source_path.write_text("controlled source", encoding="utf-8")
    reference_path = root / "reference.png"
    reference_path.write_bytes(PNG + b"reference")
    return {
        "schema_version": 1,
        "objective": objective,
        "references": [
            {
                "source": "User-supplied frame",
                "permission_status": "supplied-by-user",
                "evidence_path": str(reference_path),
            }
        ],
        "first_glance": first_glance,
        "non_negotiable_traits": ["asymmetric lensing", "thin bright disk", "deep black center"],
        "forbidden_failure_modes": ["flat orange ring", "generic eclipse", "telemetry-led composition"],
        "viewports": {
            "desktop": {"name": "desktop", "width": 1440, "height": 900, "framing": "centered hero"},
            "mobile": {"name": "mobile", "width": 390, "height": 844, "framing": "cropped hero"},
        },
        "medium": {
            "selected": "WebGL raytracer",
            "rejected": ["CSS gradients"],
            "rationale": "The selected method can bend the disk around the center.",
            "switch_condition": "Switch if the reference silhouette is not recognizable after the hero spike.",
        },
        "states": ["default", "extreme"],
        "source_path": str(source_path),
        "hero_spike_path": str(root / "render.png"),
        "secondary_features_started": False,
        "functional_gate": "pending",
        "visual_gate": "pending",
        "incomplete_wording": "The runtime works, but the hero is not visually accepted.",
        "constraint_conflicts": [],
        "conflicts_resolved": True,
        "source_hash": CONTRACT.hash_path(source_path),
    }


def valid_passing_review(
    root: Path,
    *,
    control_case: bool = False,
    objective: str | None = None,
    first_glance: str | None = None,
) -> dict:
    contract = valid_contract(
        root,
        objective=objective or "Build a cinematic black-hole hero from the supplied reference.",
        first_glance=first_glance or "A bright asymmetric accretion disk bends around a deep black center.",
    )
    reference_path = Path(contract["references"][0]["evidence_path"])
    if control_case:
        contract["hero_spike_path"] = str(reference_path)
        rendered_path = reference_path
    else:
        rendered_path = Path(contract["hero_spike_path"])
        rendered_path.write_bytes(PNG + b"render")
    contract_path = root / "contract.json"
    contract_path.write_text(json.dumps(contract, indent=2) + "\n", encoding="utf-8")
    return {
        "schema_version": 1,
        "contract_path": str(contract_path),
        "state": "full-build",
        "previous_state": "visual-passed",
        "reviewer": {"id": "review-task", "role": "visual reviewer", "independent": True},
        "comparison": {
            "viewport": "desktop",
            "reference_paths": [contract["references"][0]["evidence_path"]],
            "rendered_paths": [str(rendered_path)],
        },
        "visual_score": 10 if control_case else 8,
        "differences": [] if control_case else [{"severity": "P3", "description": "Minor highlight width mismatch."}],
        "functional_gate": "passed",
        "visual_gate": "passed",
        "secondary_features_started_before_visual_pass": False,
        "contract_hash": REVIEW.hashlib.sha256(contract_path.read_bytes()).hexdigest(),
        "source_hash": contract["source_hash"],
        "artifact_hash": REVIEW.hash_files([rendered_path]),
        "decision": "proceed",
        "incomplete_wording": "",
        "control_case": control_case,
        "control_limitation": "This mechanics-only control does not prove visual quality, mobile coverage, or extreme-state acceptance." if control_case else "",
    }


def regression_review(root: Path, case: dict) -> dict:
    review = valid_passing_review(
        root,
        objective=case["objective"],
        first_glance=case["first_glance"],
    )
    review.update(
        {
            "regression_case": case["id"],
            "state": "hero-spike",
            "previous_state": "target-locked",
            "visual_score": case["score"],
            "differences": [
                {"severity": "P1", "description": case["gap"]},
                {"severity": "P2", "description": "The representative hero still misses a locked non-negotiable trait."},
            ],
            "functional_gate": "passed",
            "visual_gate": "failed",
            "decision": "method-switch",
            "incomplete_wording": f"The runtime works, but the {case['id']} visual target is incomplete. {case['next_action']}",
        }
    )
    return review


class VisualFidelityGateTests(unittest.TestCase):
    def test_valid_contract_passes(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            self.assertEqual(CONTRACT.validate(valid_contract(Path(directory))), [])

    def test_contract_rejects_early_features_and_unresolved_physics_conflict(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            contract = valid_contract(Path(directory))
            contract["first_glance"] = "An Interstellar Kerr image rendered as a non-spinning Schwarzschild result."
            contract["secondary_features_started"] = True
            errors = CONTRACT.validate(contract)
            self.assertTrue(any("secondary features" in error for error in errors))
            self.assertTrue(any("conflict record" in error for error in errors))

    def test_contract_cannot_self_declare_visual_acceptance(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            contract = valid_contract(Path(directory))
            contract["visual_gate"] = "passed"
            self.assertTrue(any("cannot self-declare" in error for error in CONTRACT.validate(contract)))

    def test_review_rejects_a_contract_that_broke_the_feature_freeze(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            review = valid_passing_review(Path(directory))
            contract_path = Path(review["contract_path"])
            contract = json.loads(contract_path.read_text(encoding="utf-8"))
            contract["secondary_features_started"] = True
            contract_path.write_text(json.dumps(contract, indent=2) + "\n", encoding="utf-8")
            review["contract_hash"] = REVIEW.hashlib.sha256(contract_path.read_bytes()).hexdigest()
            self.assertTrue(any("feature freeze" in error for error in REVIEW.validate(review)))

    def test_source_bound_passing_review_can_enter_full_build(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            self.assertEqual(REVIEW.validate(valid_passing_review(Path(directory))), [])

    def test_stale_hashes_and_non_contract_reference_are_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            review = valid_passing_review(root)
            extra = root / "extra.png"
            extra.write_bytes(PNG + b"extra")
            review["comparison"]["reference_paths"] = [str(extra)]
            review["contract_hash"] = "a" * 64
            review["source_hash"] = "b" * 64
            review["artifact_hash"] = "c" * 64
            errors = REVIEW.validate(review)
            self.assertTrue(any("contract_hash does not match" in error for error in errors))
            self.assertTrue(any("reference_paths must be declared" in error for error in errors))
            self.assertTrue(any("source_hash does not match" in error for error in errors))
            self.assertTrue(any("artifact_hash does not match" in error for error in errors))

    def test_score_below_seven_cannot_advance(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            review = valid_passing_review(Path(directory))
            review["visual_score"] = 6
            review["visual_gate"] = "failed"
            review["decision"] = "repair"
            review["incomplete_wording"] = "The runtime works, but the hero remains visually incomplete."
            errors = REVIEW.validate(review)
            self.assertTrue(any("score of at least 7" in error for error in errors))
            self.assertTrue(any("cannot advance" in error for error in errors))

    def test_named_failure_regressions_stop_honestly_with_separate_gates(self) -> None:
        for case in FAILURE_CASES:
            with self.subTest(case=case["id"]), tempfile.TemporaryDirectory() as directory:
                review = regression_review(Path(directory), case)
                errors = REVIEW.validate(review)
                self.assertEqual(errors, [])
                self.assertEqual(review["regression_case"], case["id"])
                self.assertEqual(review["functional_gate"], "passed")
                self.assertEqual(review["visual_gate"], "failed")
                self.assertEqual(review["state"], "hero-spike")
                self.assertEqual(review["decision"], "method-switch")
                self.assertIn(case["gap"], review["differences"][0]["description"])
                self.assertIn(case["id"], review["incomplete_wording"])

    def test_ten_score_control_is_mechanics_only(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            review = valid_passing_review(Path(directory), control_case=True)
            self.assertEqual(REVIEW.validate(review), [])
            self.assertEqual(review["visual_score"], 10)
            self.assertEqual(review["decision"], "proceed")
            self.assertTrue(review["control_case"])
            self.assertIn("does not prove visual quality", review["control_limitation"])
            self.assertEqual(review["comparison"]["reference_paths"], review["comparison"]["rendered_paths"])

    def test_mechanics_control_rejects_missing_limitation_and_different_bytes(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            review = valid_passing_review(root, control_case=True)
            review["control_limitation"] = ""
            self.assertTrue(any("must state that it does not prove visual quality" in error for error in REVIEW.validate(review)))

            different_path = root / "different.png"
            different_path.write_bytes(PNG + b"different")
            contract_path = Path(review["contract_path"])
            contract = json.loads(contract_path.read_text(encoding="utf-8"))
            contract["hero_spike_path"] = str(different_path)
            contract_path.write_text(json.dumps(contract, indent=2) + "\n", encoding="utf-8")
            review["control_limitation"] = "This mechanics-only control does not prove visual quality."
            review["comparison"]["rendered_paths"] = [str(different_path)]
            review["contract_hash"] = REVIEW.hashlib.sha256(contract_path.read_bytes()).hexdigest()
            review["artifact_hash"] = REVIEW.hash_files([different_path])
            self.assertTrue(any("same reference and rendered bytes" in error for error in REVIEW.validate(review)))

    def test_p2_gap_blocks_a_high_score(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            review = valid_passing_review(Path(directory))
            review["differences"] = [{"severity": "P2", "description": "Required lensing is absent."}]
            self.assertTrue(any("P0, P1, or P2" in error for error in REVIEW.validate(review)))

    def test_final_review_requires_full_build(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            review = valid_passing_review(Path(directory))
            review["state"] = "final-reviewed"
            review["previous_state"] = "visual-passed"
            self.assertTrue(any("invalid transition" in error for error in REVIEW.validate(review)))

    def test_visual_gate_cannot_pass_during_hero_spike(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            review = valid_passing_review(Path(directory))
            review["state"] = "hero-spike"
            review["previous_state"] = "target-locked"
            review["differences"] = [{"severity": "P1", "description": "The first-glance silhouette is wrong."}]
            self.assertTrue(any("cannot be passed before" in error for error in REVIEW.validate(review)))

    def test_review_runs_the_full_contract_validator(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            review = valid_passing_review(Path(directory))
            contract_path = Path(review["contract_path"])
            contract = json.loads(contract_path.read_text(encoding="utf-8"))
            del contract["objective"]
            del contract["medium"]
            contract_path.write_text(json.dumps(contract, indent=2) + "\n", encoding="utf-8")
            review["contract_hash"] = REVIEW.hashlib.sha256(contract_path.read_bytes()).hexdigest()
            errors = REVIEW.validate(review)
            self.assertTrue(any("contract: objective must be non-empty" in error for error in errors))
            self.assertTrue(any("contract: medium must be an object" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
