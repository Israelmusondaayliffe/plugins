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
if __name__ == "__main__":
    unittest.main()
