from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import subprocess
import unittest


ROOT = Path(__file__).resolve().parents[1]
ENGINE_ROOT = ROOT / "skills" / "last30days"
ENGINE_SHA256 = "1d475193f65475897c372be286e86d9652507e8b10c8622febd9779661917de0"
ENGINE_FILE_COUNT = 116
EXCLUDED_MEDIA = (
    "assets/aging-portrait.jpeg",
    "assets/claude-code-rap.mp3",
    "assets/dog-as-human.png",
    "assets/dog-original.jpeg",
    "assets/swimmom-mockup.jpeg",
)


def engine_digest() -> str:
    digest = hashlib.sha256()
    for path in sorted(item for item in ENGINE_ROOT.rglob("*") if item.is_file()):
        if "__pycache__" in path.parts or path.suffix == ".pyc":
            continue
        digest.update(path.relative_to(ENGINE_ROOT).as_posix().encode())
        digest.update(b"\0")
        digest.update(path.read_bytes())
    return digest.hexdigest()


def run(*args: str) -> subprocess.CompletedProcess[str]:
    environment = os.environ.copy()
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    return subprocess.run(
        ["bash", str(ROOT / "scripts" / "run_last30days.sh"), *args],
        cwd=ROOT,
        env=environment,
        text=True,
        capture_output=True,
        timeout=60,
    )


def report_from(result: subprocess.CompletedProcess[str]) -> dict[str, object]:
    start = result.stdout.find("{")
    if start < 0:
        raise AssertionError(f"JSON report missing from stdout: {result.stdout!r}")
    return json.loads(result.stdout[start:])


class Last30DaysStandaloneTests(unittest.TestCase):
    def test_public_manifests_preserve_upstream_author(self) -> None:
        for relative in (".codex-plugin/plugin.json", ".claude-plugin/plugin.json"):
            manifest = json.loads((ROOT / relative).read_text(encoding="utf-8"))
            self.assertEqual(manifest["version"], "3.16.1")
            self.assertEqual(manifest["author"]["name"], "mvanhorn")
            self.assertEqual(manifest["license"], "MIT")

    def test_frozen_engine_payload_matches_audited_digest_after_media_exclusions(self) -> None:
        packaged_files = [
            path
            for path in ENGINE_ROOT.rglob("*")
            if path.is_file() and "__pycache__" not in path.parts and path.suffix != ".pyc"
        ]
        self.assertEqual(len(packaged_files), ENGINE_FILE_COUNT)
        self.assertEqual(engine_digest(), ENGINE_SHA256)
        for relative in EXCLUDED_MEDIA:
            self.assertFalse((ENGINE_ROOT / relative).exists(), relative)

    def test_generated_python_caches_are_not_packaged(self) -> None:
        self.assertFalse(any("__pycache__" in path.parts for path in ROOT.rglob("*")))
        self.assertFalse(any(ROOT.rglob("*.pyc")))

    def test_main_launcher_help(self) -> None:
        result = run("--help")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Research a topic across live social", result.stdout)

    def test_permission_preflight_plans_no_writes(self) -> None:
        result = run("--preflight", "--no-browser-cookies")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Local writes:\n- none planned", result.stdout)
        self.assertIn("Browser cookies: off", result.stdout)

    def test_mock_research_is_local_and_machine_readable(self) -> None:
        result = run(
            "openclaw skills",
            "--mock",
            "--emit=json",
            "--json-profile=raw",
            "--search=reddit,hackernews",
            "--no-browser-cookies",
            "--as-of=2026-08-28",
            "--days=30",
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        report = report_from(result)
        self.assertEqual(report["topic"], "openclaw skills")
        self.assertEqual(report["range_from"], "2026-07-29")
        self.assertEqual(report["range_to"], "2026-08-28")
        self.assertIn("reddit", report["source_status"])


if __name__ == "__main__":
    unittest.main()
