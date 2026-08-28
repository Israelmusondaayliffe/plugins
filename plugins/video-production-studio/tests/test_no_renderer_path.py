from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


PLUGIN_ROOT = Path(__file__).parents[1]
ROUTER_ROOT = PLUGIN_ROOT / "skills" / "video-production-router"
PLANNING_ARTIFACTS = {
    "video-brief.md",
    "storyboard.md",
    "shot-list.md",
    "asset-ledger.md",
    "runtime-requirements.md",
    "delivery-checklist.md",
}


def no_renderer_route() -> dict[str, object]:
    return {
        "route": "faceless-explainer",
        "objective": "Explain the supplied topic",
        "duration_seconds": 60,
        "width": 1080,
        "height": 1920,
        "runtime": "none",
        "renderer_available": False,
        "completion_state": "planning-complete",
        "planning_artifacts": sorted(PLANNING_ARTIFACTS),
        "rendering_status": "incomplete",
        "visual_qc_status": "incomplete",
        "skills": ["faceless-explainer"],
        "rationale": "No renderer is available, so the route stops after planning.",
    }


def validate(router_root: Path, route: dict[str, object]) -> subprocess.CompletedProcess[str]:
    with tempfile.TemporaryDirectory() as temporary_directory:
        route_file = Path(temporary_directory) / "route.json"
        route_file.write_text(json.dumps(route), encoding="utf-8")
        return subprocess.run(
            [sys.executable, str(router_root / "scripts" / "validate_route.py"), str(route_file)],
            check=False,
            capture_output=True,
            text=True,
        )


class NoRendererPathTests(unittest.TestCase):
    def test_source_contract_has_complete_no_renderer_path(self) -> None:
        skill = (ROUTER_ROOT / "SKILL.md").read_text(encoding="utf-8")
        routing = (ROUTER_ROOT / "references" / "routing.md").read_text(encoding="utf-8")
        spec = json.loads((PLUGIN_ROOT / "bundle-spec.json").read_text(encoding="utf-8"))

        self.assertEqual(spec["companion_policy"], "optional-at-runtime")
        self.assertEqual(
            set(spec["completion_states"]["planning-complete"]["required_artifacts"]),
            PLANNING_ARTIFACTS,
        )
        self.assertTrue(
            any(
                case.get("expected_skill") == "video-production-router"
                and case.get("expected_completion_state") == "planning-complete"
                for case in spec["routing_cases"]
            )
        )
        for artifact in PLANNING_ARTIFACTS:
            with self.subTest(artifact=artifact):
                self.assertIn(f"`{artifact}`", skill)
        for companion in ("HyperFrames", "Remotion", "Browser", "Computer Use"):
            with self.subTest(companion=companion):
                self.assertIn(companion, skill)
        self.assertIn("optional at runtime", skill)
        self.assertIn("rendering and visual QC incomplete", routing)

    def test_no_renderer_route_validates_from_sibling_free_router_copy(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            isolated_router = Path(temporary_directory) / "video-production-router"
            shutil.copytree(ROUTER_ROOT, isolated_router)
            result = validate(isolated_router, no_renderer_route())
        self.assertEqual(result.returncode, 0, result.stderr or result.stdout)
        self.assertTrue(json.loads(result.stdout)["valid"])

    def test_no_renderer_route_cannot_claim_rendered_delivery(self) -> None:
        route = no_renderer_route()
        route["completion_state"] = "rendered-delivery-complete"
        route["rendering_status"] = "complete"
        route["visual_qc_status"] = "complete"
        result = validate(ROUTER_ROOT, route)
        self.assertEqual(result.returncode, 1)
        self.assertIn("requires an available renderer", result.stdout)

    def test_available_renderer_and_delivery_qc_can_complete_delivery(self) -> None:
        route = no_renderer_route()
        route.update(
            {
                "runtime": "hyperframes",
                "renderer_available": True,
                "completion_state": "rendered-delivery-complete",
                "rendering_status": "complete",
                "visual_qc_status": "complete",
                "skills": ["faceless-explainer", "video-delivery-qc"],
            }
        )
        result = validate(ROUTER_ROOT, route)
        self.assertEqual(result.returncode, 0, result.stderr or result.stdout)
        self.assertTrue(json.loads(result.stdout)["valid"])


if __name__ == "__main__":
    unittest.main()
