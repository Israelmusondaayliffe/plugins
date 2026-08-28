"""Agent Ops remains complete when optional sibling plugins are absent."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class OptionalCompanionFallbackTests(unittest.TestCase):
    def test_manifest_and_bundle_versions_match(self) -> None:
        versions = {
            json.loads((ROOT / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8"))["version"],
            json.loads((ROOT / ".codex-plugin" / "plugin.json").read_text(encoding="utf-8"))["version"],
            json.loads((ROOT / "bundle-spec.json").read_text(encoding="utf-8"))["version"],
        }
        self.assertEqual(versions, {"0.5.2"})

    def test_every_named_sibling_is_optional(self) -> None:
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("## Optional companion capabilities", readme)
        self.assertIn("does not require a sibling plugin", readme)
        for name in ("Outcome Engine", "LoopKit", "ProofLoop", "Superpowers", "Plugin Eval"):
            self.assertIn(name, readme)
        spec = json.loads((ROOT / "bundle-spec.json").read_text(encoding="utf-8"))
        self.assertEqual(
            set(spec["companions"]),
            {"loopkit", "outcome-engine", "proofloop", "superpowers", "plugin-eval"},
        )
        self.assertTrue(any("optional" in rule.lower() for rule in spec["guardrails"]))

    def test_router_has_local_fallback_without_implicit_shim_activation(self) -> None:
        router = (ROOT / "skills" / "agent-ops-router" / "SKILL.md").read_text(encoding="utf-8")
        routing = (ROOT / "skills" / "agent-ops-router" / "references" / "routing.md").read_text(encoding="utf-8")
        self.assertIn("If LoopKit is absent and Agent Ops was explicitly selected", router)
        self.assertIn("Do not treat that fallback as implicit activation", router)
        self.assertIn("When it is absent and Agent Ops was explicitly selected", routing)
        for skill in ("goal-runner", "loop-goal-engineer", "loopy"):
            self.assertIn(skill, routing)

    def test_compatibility_shims_are_explicit_and_have_local_fallbacks(self) -> None:
        required = {
            "goal-runner": ("Use only when the user explicitly says goal-runner", "scripts/verify_contract.py"),
            "loop-goal-engineer": ("Use only when the user explicitly says loop-goal-engineer", "scripts/validate_prompt.py"),
            "loopy": ("Use only when the user explicitly says Loopy", "references/run.md"),
        }
        for name, markers in required.items():
            text = (ROOT / "skills" / name / "SKILL.md").read_text(encoding="utf-8")
            self.assertIn("When LoopKit is absent", text, name)
            self.assertIn("bundled local fallback", text, name)
            self.assertNotIn("scheduled for removal", text, name)
            self.assertNotIn("through Agent Ops 0.3.x", text, name)
            for marker in markers:
                self.assertIn(marker, text, name)

    def test_goal_runner_validator_operates_without_sibling_plugins(self) -> None:
        script = ROOT / "skills" / "goal-runner" / "scripts" / "verify_contract.py"
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            artifact = root / "artifact.md"
            artifact.write_text("# Result\ncomplete\n", encoding="utf-8")
            contract = root / "contract.md"
            contract.write_text(
                "## MACHINE CHECKS\n"
                f"- file_exists: {artifact}\n"
                f"- contains: {artifact} | complete\n"
                f"- no_dashes: {artifact}\n",
                encoding="utf-8",
            )
            result = subprocess.run(
                [sys.executable, str(script), str(contract)],
                capture_output=True,
                text=True,
                check=False,
            )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_loop_goal_validator_operates_without_sibling_plugins(self) -> None:
        script = ROOT / "skills" / "loop-goal-engineer" / "scripts" / "validate_prompt.py"
        prompt = (
            "Goal: produce the named report with cited evidence. "
            "Only read from /input and only write to /output/report.md. "
            "Stop when the report exists and the verification command passes. "
            "If verification fails after 3 attempts, stop and report what went wrong. "
            "Maximum 5 iterations."
        )
        result = subprocess.run(
            [sys.executable, str(script), "-", "--mode", "goal"],
            input=prompt,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_loopy_fallback_has_complete_local_workflows(self) -> None:
        loopy = ROOT / "skills" / "loopy"
        expected = {"audit.md", "debrief.md", "discover.md", "publish.md", "run.md"}
        self.assertEqual({path.name for path in (loopy / "references").glob("*.md")}, expected)
        skill = (loopy / "SKILL.md").read_text(encoding="utf-8")
        for phrase in (
            "observes fresh state",
            "verifies it with reproducible evidence",
            "enters a named terminal state",
            "Return a one-shot workflow",
        ):
            self.assertIn(phrase, skill)

    def test_changed_prose_has_no_unicode_dash(self) -> None:
        files = (
            "README.md",
            "agents/fa-reviewer.md",
            "skills/agent-ops-router/SKILL.md",
            "skills/agent-ops-router/references/routing.md",
            "skills/fable-advisor/SKILL.md",
            "skills/goal-runner/SKILL.md",
            "skills/loop-goal-engineer/SKILL.md",
            "skills/loopy/SKILL.md",
        )
        for relative in files:
            text = (ROOT / relative).read_text(encoding="utf-8")
            self.assertNotRegex(text, r"[\u2013\u2014]", relative)


if __name__ == "__main__":
    unittest.main()
