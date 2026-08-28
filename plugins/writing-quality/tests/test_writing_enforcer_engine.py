#!/usr/bin/env python3
"""Test the protected 47-pattern Writing Enforcer migration."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parent.parent
ENFORCER = ROOT / "skills/writing-enforcer"
SOURCE_ENGINE_SHA256 = "512f4daa985c7b52503c9c2cb7fb32c1cb4c36efd649d4072e3fec692d4131a6"


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def run_python(*args: Path | str) -> subprocess.CompletedProcess[str]:
    environment = dict(os.environ)
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    return subprocess.run(
        [sys.executable, *(str(value) for value in args)],
        capture_output=True,
        text=True,
        check=False,
        env=environment,
    )


class WritingEnforcerEngineTests(unittest.TestCase):
    def test_engine_manifest_pins_complete_qualified_snapshot(self) -> None:
        checked = run_python(ENFORCER / "scripts/engine_check.py")
        self.assertEqual(checked.returncode, 0, checked.stdout + checked.stderr)
        status = json.loads(checked.stdout)
        self.assertEqual(status["status"], "complete")
        self.assertEqual(status["file_count"], 19)
        self.assertEqual(status["migration_source_sha256"], SOURCE_ENGINE_SHA256)
        self.assertFalse(status["runtime_dependency_on_harness_unslop"])

    def test_pattern_catalog_contains_exactly_1_through_47(self) -> None:
        catalog = "\n".join(
            (ENFORCER / relative).read_text(encoding="utf-8")
            for relative in (
                "references/unslop-engine/ai-pattern-taxonomy.md",
                "references/unslop-engine/extended-patterns.md",
            )
        )
        numbers = {
            int(value)
            for value in re.findall(r"^#{2,3} Pattern (\d+):", catalog, re.MULTILINE)
        }
        self.assertEqual(numbers, set(range(1, 48)))

    def test_source_backed_voice_replaces_synthetic_soul_rules(self) -> None:
        skill = (ENFORCER / "SKILL.md").read_text(encoding="utf-8")
        workflow = (ENFORCER / "references/unslop-engine/workflow.md").read_text(encoding="utf-8")
        policy = (ENFORCER / "references/unslop-engine/unslop-policy.md").read_text(encoding="utf-8")
        contract = skill + "\n" + workflow + "\n" + policy
        self.assertIn("Do not infer voice from general memory", contract)
        self.assertIn("Neutral source text stays neutral", contract)
        self.assertIn("Never invent personality", contract)
        for forbidden in (
            "inject soul",
            "Known user preferences from memory",
            "Have opinions.",
            "Use \"I\" when it fits.",
            "Add opinions, rhythm variation, first-person",
            "Quality score ≥ 7/10",
        ):
            self.assertNotIn(forbidden, contract)

    def test_detect_scanner_does_not_mutate_input(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            sample = Path(temporary_directory) / "sample.md"
            sample.write_text("Certainly! This is a pivotal moment.\n", encoding="utf-8")
            before = hashlib.sha256(sample.read_bytes()).hexdigest()
            scanned = run_python(
                ENFORCER / "scripts/unslop-engine/quality_validator.py",
                sample,
                "--json",
            )
            after = hashlib.sha256(sample.read_bytes()).hexdigest()
        self.assertEqual(before, after)
        self.assertTrue(scanned.stdout.strip())
        self.assertGreater(json.loads(scanned.stdout)["ai_tell_count"], 0)

    def test_punctuation_helper_requires_separate_scratch_output(self) -> None:
        helper_path = ENFORCER / "scripts/unslop-engine/emdash_replacer.py"
        helper_text = helper_path.read_text(encoding="utf-8")
        self.assertNotIn("--in-place", helper_text)
        self.assertNotIn("--text", helper_text)
        self.assertIn("scratch-input.txt scratch-output.txt", helper_text)
        module = load_module(
            helper_path,
            "writing_enforcer_emdash_replacer",
        )
        with tempfile.TemporaryDirectory() as temporary_directory:
            source = Path(temporary_directory) / "scratch-input.txt"
            output = Path(temporary_directory) / "scratch-output.txt"
            source.write_text("One thought—then another.\n", encoding="utf-8")
            original = source.read_bytes()
            with self.assertRaises(ValueError):
                module.process_file(str(source))
            with self.assertRaises(ValueError):
                module.process_file(str(source), in_place=True)
            direct_text = run_python(helper_path, "--text", "One thought—then another.")
            self.assertNotEqual(direct_text.returncode, 0)
            self.assertIn("unrecognized arguments", direct_text.stderr)
            result = module.process_file(str(source), str(output))
            self.assertEqual(source.read_bytes(), original)
            self.assertNotIn("—", output.read_text(encoding="utf-8"))
            self.assertEqual(result["output"], str(output))

    def test_protected_scope_rejects_every_named_category(self) -> None:
        module = load_module(
            ENFORCER / "scripts/protected_scope_validator.py",
            "writing_enforcer_protected_scope",
        )
        examples = (
            ("---\nname: exact\n---\nBody.\n", "---\nname: changed\n---\nBody.\n", ".md"),
            ("```text\nexact prompt\n```\n", "```text\nchanged prompt\n```\n", ".md"),
            ("Use `exact-command --flag`.\n", "Use `changed-command --flag`.\n", ".md"),
            ("> exact quoted log\n", "> changed quoted log\n", ".md"),
            ('The source says "exact words".\n', 'The source says "changed words".\n', ".md"),
            ("See [source](https://example.com/exact).\n", "See [source](https://example.com/changed).\n", ".md"),
            ("Use /absolute/exact/path.md.\n", "Use /absolute/changed/path.md.\n", ".md"),
            ("Route writing-quality:writing-enforcer.\n", "Route writing-quality:claim-boundary-checker.\n", ".md"),
            ("Key | Value\n--- | ---\nA | B\n", "Key | Value\n--- | ---\nA | C\n", ".md"),
            ('{"template": "exact"}\n', '{"template": "changed"}\n', ".json"),
        )
        for before, after, suffix in examples:
            with self.subTest(before=before):
                self.assertFalse(module.compare_protected(before, after, suffix)["valid"])

    def test_duplicate_and_multiline_strong_text_cannot_hide_changes(self) -> None:
        module = load_module(
            ENFORCER / "scripts/protected_scope_validator.py",
            "writing_enforcer_strong_scope",
        )
        self.assertTrue(
            module.compare_protected("Keep **this exact phrase**.\n", "Keep this exact phrase.\n")["valid"]
        )
        duplicate_before = "Keep **this exact phrase** and this exact phrase elsewhere.\n"
        duplicate_after = "Keep **changed words here** and this exact phrase elsewhere.\n"
        self.assertFalse(module.compare_protected(duplicate_before, duplicate_after)["valid"])
        multiline_before = "Keep **this exact first line\nand exact second line** here.\n"
        multiline_unbolded = "Keep this exact first line\nand exact second line here.\n"
        multiline_changed = "Keep **this exact first line\nand a changed second line** here.\n"
        self.assertTrue(module.compare_protected(multiline_before, multiline_unbolded)["valid"])
        self.assertFalse(module.compare_protected(multiline_before, multiline_changed)["valid"])

    def test_contextual_floor_and_hard_gates_override_raw_scores(self) -> None:
        spec = json.loads((ROOT / "bundle-spec.json").read_text(encoding="utf-8"))
        engine = spec["writing_enforcer_engine"]
        self.assertEqual(engine["contextual_score_floor"], 8.0)
        self.assertEqual(engine["contextual_score_target"], 10.0)
        self.assertFalse(engine["raw_script_scores_are_verdicts"])
        skill = (ENFORCER / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("any hard gate", skill)

    def test_ownership_has_no_runtime_dependency_loop(self) -> None:
        spec = json.loads((ROOT / "bundle-spec.json").read_text(encoding="utf-8"))
        ownership = spec["ownership"]
        self.assertEqual(ownership["ordinary_prose_owner"], "writing-quality")
        self.assertFalse(ownership["writing_quality_requires_harness_unslop"])
        self.assertFalse(ownership["harness_unslop_requires_writing_quality"])
        for path in ENFORCER.rglob("*.py"):
            text = path.read_text(encoding="utf-8", errors="replace")
            self.assertNotIn("plugins/harness-engineering", text)

    def test_protected_sibling_skills_match_frozen_digests(self) -> None:
        spec = json.loads((ROOT / "bundle-spec.json").read_text(encoding="utf-8"))
        for relative, expected in spec["protected_subtrees"].items():
            subtree = ROOT / relative
            files = sorted(path for path in subtree.rglob("*") if path.is_file())
            payload = b"".join(
                str(path.relative_to(subtree)).encode("utf-8")
                + b"\0"
                + hashlib.sha256(path.read_bytes()).hexdigest().encode("ascii")
                + b"\n"
                for path in files
            )
            self.assertEqual(len(files), expected["files"])
            self.assertEqual(hashlib.sha256(payload).hexdigest(), expected["inventory_sha256"])

    def test_sibling_free_copy_runs_engine_and_bundle(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            isolated = Path(temporary_directory) / "writing-quality"
            shutil.copytree(ROOT, isolated)
            bundle = run_python(isolated / "scripts/verify_bundle.py")
            engine = run_python(isolated / "skills/writing-enforcer/scripts/engine_check.py")
            sample = Path(temporary_directory) / "neutral.txt"
            profile = Path(temporary_directory) / "profile.json"
            sample.write_text("The meeting starts at nine. The agenda lists the budget.\n", encoding="utf-8")
            scanned = run_python(
                isolated / "skills/writing-enforcer/scripts/unslop-engine/quality_validator.py",
                sample,
                "--json",
            )
            profiled = run_python(
                isolated / "skills/writing-enforcer/scripts/unslop-engine/voice_profiler.py",
                sample,
                "--output",
                profile,
            )
            profile_created = profile.is_file()
        self.assertEqual(bundle.returncode, 0, bundle.stdout + bundle.stderr)
        self.assertEqual(engine.returncode, 0, engine.stdout + engine.stderr)
        self.assertTrue(scanned.stdout.strip())
        self.assertEqual(profiled.returncode, 0, profiled.stdout + profiled.stderr)
        self.assertTrue(profile_created)


if __name__ == "__main__":
    unittest.main()
