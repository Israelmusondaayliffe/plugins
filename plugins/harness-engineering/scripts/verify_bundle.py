#!/usr/bin/env python3
"""Verify the Harness Engineering source bundle."""

from __future__ import annotations

import json
from pathlib import Path
import re
import subprocess
import sys


EXPECTED_SKILLS = {
    "agents-md-engineer",
    "harness-audit",
    "harness-builder",
    "harness-engineering",
    "harness-interview",
    "harness-maintainer",
    "harness-planner",
    "harness-runner",
    "harness-verifier",
    "model-prompt-engineer",
    "plugin-engineer",
    "skill-engineer",
}
TEXT_SUFFIXES = {".md", ".json", ".yaml", ".yml", ".py"}
VERSION_PATTERN = re.compile(r"^2\.1\.0$")


def fail(message: str) -> None:
    raise RuntimeError(message)


def main() -> int:
    root = Path(sys.argv[1] if len(sys.argv) > 1 else Path(__file__).resolve().parents[1]).resolve()
    manifests = {}
    for platform in ("codex", "claude"):
        manifest_path = root / f".{platform}-plugin" / "plugin.json"
        if not manifest_path.is_file():
            fail(f"{platform} manifest is missing")
        manifests[platform] = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest = manifests["codex"]
    for field in ("name", "version", "description", "license"):
        if manifests["codex"].get(field) != manifests["claude"].get(field):
            fail(f"manifest {field} differs across Codex and Claude")
    for platform, platform_manifest in manifests.items():
        version = platform_manifest.get("version")
        if platform_manifest.get("name") != "harness-engineering" or not isinstance(version, str) or not VERSION_PATTERN.fullmatch(version):
            fail(f"{platform} manifest identity or version is incorrect")
        if platform_manifest.get("author", {}).get("name") != "Israel Ayliffe" or platform_manifest.get("license") != "MIT":
            fail(f"{platform} publisher or license metadata is incorrect")
        if "apps" in platform_manifest or "mcpServers" in platform_manifest or "hooks" in platform_manifest:
            fail(f"{platform} manifest declares a component that the plugin does not ship")

    actual = {path.parent.name for path in (root / "skills").glob("*/SKILL.md")}
    if actual != EXPECTED_SKILLS:
        fail(f"skill set mismatch: expected {sorted(EXPECTED_SKILLS)}, got {sorted(actual)}")

    validator = Path.home() / ".codex" / "skills" / ".system" / "skill-creator" / "scripts" / "quick_validate.py"
    validations = []
    for name in sorted(EXPECTED_SKILLS):
        skill_dir = root / "skills" / name
        if validator.is_file():
            result = subprocess.run([sys.executable, str(validator), str(skill_dir)], capture_output=True, text=True)
            if result.returncode != 0:
                fail(f"skill validation failed for {name}: {result.stdout}{result.stderr}")
        else:
            text = (skill_dir / "SKILL.md").read_text(encoding="utf-8")
            if not text.startswith("---") or "description:" not in text.splitlines()[2][:12] and not any(l.startswith("description:") for l in text.splitlines()[:6]):
                fail(f"SKILL.md frontmatter incomplete for {name}")
        metadata_path = skill_dir / "agents" / "openai.yaml"
        if metadata_path.is_file():
            metadata = metadata_path.read_text(encoding="utf-8")
            if f"${name}" not in metadata:
                fail(f"default prompt does not name ${name}")
        validations.append(name)

    for path in root.rglob("*"):
        if path.is_symlink():
            fail(f"bundle contains a symbolic link: {path}")
        if path.is_file() and path.suffix.lower() in TEXT_SUFFIXES:
            text = path.read_text(encoding="utf-8", errors="replace")
            markers = ("[" + "TODO:", "__" + "REPLACE_ME__")
            if any(marker in text for marker in markers):
                fail(f"placeholder remains in {path}")
            if "\u2014" in text:
                fail(f"em dash remains in {path}")
            personal_path = "/Users/" + "israelayliffe"
            if personal_path in text:
                fail(f"personal absolute path remains in {path}")

    required = [
        root / "README.md",
        root / "LICENSE",
        root / "PRIVACY.md",
        root / "SECURITY.md",
        root / "TERMS.md",
        root / "scripts" / "harnessctl.py",
        root / "schemas" / "profile.schema.json",
        root / "schemas" / "operations.schema.json",
    ]
    missing = [str(path) for path in required if not path.is_file()]
    if missing:
        fail(f"required files missing: {missing}")
    print(json.dumps({"plugin": "harness-engineering", "version": manifest["version"], "skills_validated": validations}, indent=2))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"bundle verification failed: {exc}", file=sys.stderr)
        raise SystemExit(1)
