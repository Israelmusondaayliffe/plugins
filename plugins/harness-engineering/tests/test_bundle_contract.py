from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


def codex_manifest_path() -> Path:
    """Marketplace interface metadata is Codex-specific and lives only in that manifest."""
    return ROOT / ".codex-plugin" / "plugin.json"


def manifest_path() -> Path:
    for candidate in (ROOT / ".claude-plugin" / "plugin.json", ROOT / ".codex-plugin" / "plugin.json"):
        if candidate.is_file():
            return candidate
    raise FileNotFoundError("no plugin manifest found")


class BundleContractTests(unittest.TestCase):
    def test_manifest_and_marketplace_ready_shape(self) -> None:
        manifest = json.loads(manifest_path().read_text(encoding="utf-8"))
        self.assertEqual(manifest["name"], "harness-engineering")
        self.assertRegex(manifest["version"], r"^\d+\.\d+\.\d+$")
        self.assertEqual(manifest["license"], "MIT")
        codex = json.loads(codex_manifest_path().read_text(encoding="utf-8"))
        self.assertEqual(codex["version"], manifest["version"])
        self.assertEqual(len(codex["interface"]["defaultPrompt"]), 3)
        self.assertNotIn("apps", manifest)
        self.assertNotIn("mcpServers", manifest)

    def test_platform_references_exist(self) -> None:
        for name in ("platform-matrix.md", "platform-claude-code.md", "platform-cowork.md", "platform-codex.md"):
            self.assertTrue((ROOT / "references" / name).is_file(), name)

    def test_templates_have_no_unresolved_todo_markers(self) -> None:
        markers = ("[" + "TODO:", "__" + "REPLACE_ME__")
        for path in ROOT.rglob("*"):
            if path.is_file() and path.suffix in {".md", ".json", ".yaml", ".py"}:
                text = path.read_text(encoding="utf-8", errors="replace")
                for marker in markers:
                    self.assertNotIn(marker, text, str(path))

    def test_skill_descriptions_are_in_frontmatter(self) -> None:
        for path in (ROOT / "skills").glob("*/SKILL.md"):
            lines = path.read_text(encoding="utf-8").splitlines()
            self.assertEqual(lines[0], "---")
            self.assertTrue(any(line.startswith("name:") for line in lines[1:5]))
            self.assertTrue(any(line.startswith("description:") for line in lines[1:6]))

    def test_skills_name_all_three_platforms(self) -> None:
        for path in (ROOT / "skills").glob("*/SKILL.md"):
            text = path.read_text(encoding="utf-8")
            self.assertIn("Cowork", text, f"{path} does not mention Cowork")
            self.assertIn("Claude Code", text, f"{path} does not mention Claude Code")
            self.assertIn("Codex", text, f"{path} does not mention Codex")

    def test_qualitative_acceptance_cannot_be_replaced_by_functional_proof(self) -> None:
        standard = (ROOT / "references" / "verification-standard.md").read_text(encoding="utf-8")
        planner = (ROOT / "skills" / "harness-planner" / "SKILL.md").read_text(encoding="utf-8")
        verifier = (ROOT / "skills" / "harness-verifier" / "SKILL.md").read_text(encoding="utf-8")
        template = (ROOT / "assets" / "global-agents.template.md").read_text(encoding="utf-8")
        self.assertIn("functional_result", standard)
        self.assertIn("qualitative_result", standard)
        self.assertIn("task-owned qualitative acceptance artifact", planner)
        self.assertIn("below-threshold qualitative result prevents a complete verdict", verifier)
        self.assertIn("Functional or runtime proof cannot substitute", template)

    def test_unslop_repair_is_explicit_platform_neutral_and_maintenance_bounded(self) -> None:
        front_door = (ROOT / "skills" / "harness-engineering" / "SKILL.md").read_text(encoding="utf-8")
        maintainer = (ROOT / "skills" / "harness-maintainer" / "SKILL.md").read_text(encoding="utf-8")
        specialist = (ROOT / "skills" / "unslop-harness-repair" / "SKILL.md").read_text(encoding="utf-8")
        metadata = (ROOT / "skills" / "unslop-harness-repair" / "agents" / "openai.yaml").read_text(encoding="utf-8")
        outer_contract = "\n".join(
            path.read_text(encoding="utf-8")
            for path in (
                ROOT / "skills" / "unslop-harness-repair" / "SKILL.md",
                ROOT / "skills" / "unslop-harness-repair" / "references" / "repair-contract.md",
                ROOT / "skills" / "unslop-harness-repair" / "references" / "worker-contract.md",
                ROOT / "skills" / "unslop-harness-repair" / "references" / "unslop-engine-contract.md",
            )
        )

        self.assertIn("load `unslop-harness-repair`", front_door)
        self.assertIn("platform's instruction-file chain", maintainer)
        for excluded in ("cache cleanup", "authentication", "version-only changes", "binaries", "code-only maintenance"):
            self.assertIn(excluded, maintainer)
        self.assertIn("Contextual score must be at least 8.0 out of 10", specialist)
        self.assertIn("Target 10.0", specialist)
        self.assertIn("does not require the Writing Quality plugin", specialist)
        self.assertIn("isolated copy of this skill", specialist)
        self.assertIn("allow_implicit_invocation: false", metadata)
        for forbidden in ("AGENTS.md", "CLAUDE.md", "PROJECTS/", "/Users/", "personal-plugins-private", "claude-plugins-private"):
            self.assertNotIn(forbidden, outer_contract)

    def test_unslop_repair_bundles_its_complete_local_engine(self) -> None:
        skill = ROOT / "skills" / "unslop-harness-repair"
        manifest = json.loads((skill / "references/unslop-engine-manifest.json").read_text(encoding="utf-8"))
        self.assertFalse(manifest["runtime_dependency_on_writing_quality"])
        self.assertEqual(len(manifest["files"]), 19)
        personal_path = "/Users/" + "israelayliffe"
        for relative in manifest["files"]:
            self.assertTrue((skill / relative).is_file(), relative)
            self.assertNotIn(personal_path, (skill / relative).read_text(encoding="utf-8"), relative)
        runtime_contract = "\n".join(
            path.read_text(encoding="utf-8")
            for path in (
                skill / "SKILL.md",
                skill / "references/repair-contract.md",
                skill / "references/unslop-engine-contract.md",
                skill / "scripts/unslop_repair.py",
            )
        )
        self.assertNotIn("/plugins/writing-quality", runtime_contract)
        self.assertNotIn("Writing Quality owns the Unslop policy", runtime_contract)

    def test_sibling_capabilities_are_optional(self) -> None:
        skill_engineer = (ROOT / "skills" / "skill-engineer" / "SKILL.md").read_text(encoding="utf-8")
        unslop_repair = (ROOT / "skills" / "unslop-harness-repair" / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("optional quality companion", skill_engineer)
        self.assertIn("When it is absent", skill_engineer)
        self.assertIn("when that plugin is available", unslop_repair)
        self.assertIn("Its presence or absence does not change", unslop_repair)

if __name__ == "__main__":
    unittest.main()
