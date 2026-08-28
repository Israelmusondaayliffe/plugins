#!/usr/bin/env python3
"""Verify the complete local Writing Enforcer engine inventory."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parent.parent
MANIFEST = SKILL_ROOT / "references/unslop-engine-manifest.json"


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def engine_status() -> dict[str, object]:
    try:
        manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return {"status": "incomplete", "errors": [str(exc)]}
    errors: list[str] = []
    files = manifest.get("files")
    if not isinstance(files, dict) or len(files) != 19:
        errors.append("engine manifest must pin exactly 19 files")
        files = {}
    actual: dict[str, str] = {}
    for relative, expected in sorted(files.items()):
        path = (SKILL_ROOT / relative).resolve()
        try:
            path.relative_to(SKILL_ROOT.resolve())
        except ValueError:
            errors.append(f"engine file escapes the skill root: {relative}")
            continue
        if not path.is_file():
            errors.append(f"engine file is missing: {relative}")
            continue
        digest = sha256_bytes(path.read_bytes())
        actual[relative] = digest
        if digest != expected:
            errors.append(f"engine hash mismatch: {relative}")
    payload = "".join(
        f"{relative}\0{digest}\n" for relative, digest in sorted(actual.items())
    ).encode("utf-8")
    inventory = sha256_bytes(payload)
    if manifest.get("inventory_sha256") != inventory:
        errors.append("engine inventory digest does not match the manifest")
    if manifest.get("migration_source_sha256") != (
        "512f4daa985c7b52503c9c2cb7fb32c1cb4c36efd649d4072e3fec692d4131a6"
    ):
        errors.append("qualified migration-source digest is missing or changed")
    if manifest.get("runtime_dependency_on_harness_unslop") is not False:
        errors.append("runtime_dependency_on_harness_unslop must be false")
    return {
        "status": "complete" if not errors else "incomplete",
        "file_count": len(actual),
        "inventory_sha256": inventory,
        "migration_source_sha256": manifest.get("migration_source_sha256"),
        "runtime_dependency_on_harness_unslop": False,
        "errors": errors,
    }


def main() -> int:
    result = engine_status()
    print(json.dumps(result, indent=2))
    return 0 if result["status"] == "complete" else 1


if __name__ == "__main__":
    raise SystemExit(main())
