from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skills/web-product-router/scripts/validate_route.py"
SPEC = importlib.util.spec_from_file_location("web_route_validator", SCRIPT)
assert SPEC and SPEC.loader
ROUTER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(ROUTER)


def route(objective: str, gate: bool) -> dict:
    skills = ["code-production-agent"]
    if gate:
        skills.append("visual-fidelity-gate")
    return {
        "route": "greenfield",
        "objective": objective,
        "design_constitution": None,
        "implementation_skills": skills,
        "acceptance_flow": "/tmp/acceptance.json",
        "visual_gate_required": gate,
        "visual_contract": "/tmp/visual-contract.json" if gate else None,
        "rationale": "Use the narrow route required by the objective.",
    }


class WebProductRouterVisualTests(unittest.TestCase):
    def test_webgl_reference_cannot_bypass_gate(self) -> None:
        errors = ROUTER.validate(route("Build a WebGL hero that must match the reference.", False))
        self.assertIn("the objective requires visual_gate_required true", errors)

    def test_high_visual_route_with_specialist_passes(self) -> None:
        self.assertEqual(ROUTER.validate(route("Build a cinematic WebGPU ocean hero.", True)), [])

    def test_full_screen_video_hero_cannot_opt_out(self) -> None:
        errors = ROUTER.validate(route("Build an immersive full-screen video hero for this website.", False))
        self.assertIn("the objective requires visual_gate_required true", errors)

    def test_routine_crud_route_stays_ungated(self) -> None:
        self.assertEqual(ROUTER.validate(route("Build a routine CRUD admin page.", False)), [])

    def test_hidden_specialist_remains_implicit_off(self) -> None:
        metadata = (ROOT / "skills/visual-fidelity-gate/agents/openai.yaml").read_text(encoding="utf-8")
        self.assertIn("allow_implicit_invocation: false", metadata)

    def test_declared_trigger_corpus_cannot_bypass_gate(self) -> None:
        corpus = json.loads((ROOT / "skills/visual-fidelity-gate/evals/evals.json").read_text(encoding="utf-8"))
        for prompt in corpus["should_trigger"]:
            with self.subTest(prompt=prompt):
                self.assertIn("the objective requires visual_gate_required true", ROUTER.validate(route(prompt, False)))

    def test_declared_near_miss_corpus_stays_ungated(self) -> None:
        corpus = json.loads((ROOT / "skills/visual-fidelity-gate/evals/evals.json").read_text(encoding="utf-8"))
        for prompt in corpus["should_not_trigger"]:
            with self.subTest(prompt=prompt):
                self.assertEqual(ROUTER.validate(route(prompt, False)), [])


if __name__ == "__main__":
    unittest.main()
