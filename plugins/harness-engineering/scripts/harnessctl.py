#!/usr/bin/env python3
"""Deterministic local operations for Harness Engineering."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import re
import shutil
import subprocess
import sys
import tempfile
from typing import Any, Iterable


SCHEMA_VERSION = 1
PROFILE_REQUIRED = {"schema_version", "user", "scope", "decisions"}
PLAN_REQUIRED = {
    "schema_version",
    "run_id",
    "allowed_roots",
    "approval_groups",
    "outcome",
    "resource_budget",
    "support_artifacts",
    "operations",
}
SECRET_KEY = re.compile(r"(?i)(token|secret|password|cookie|credential|authorization|api[_-]?key)")


class HarnessError(RuntimeError):
    pass


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise HarnessError(f"cannot read valid JSON from {path}: {exc}") from exc


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    data = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    atomic_write(path, data.encode("utf-8"))


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def atomic_write(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=path.parent, prefix=f".{path.name}.", delete=False) as handle:
        temporary = Path(handle.name)
        handle.write(data)
        handle.flush()
        os.fsync(handle.fileno())
    try:
        os.replace(temporary, path)
    finally:
        if temporary.exists():
            temporary.unlink()


def is_within(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False


def check_target(target: Path, allowed_roots: Iterable[Path]) -> Path:
    if not target.is_absolute():
        raise HarnessError(f"target must be absolute: {target}")
    resolved = target.resolve(strict=False)
    root_pairs = [(root.expanduser(), root.expanduser().resolve(strict=False)) for root in allowed_roots]
    matches = [(original, normalized) for original, normalized in root_pairs if is_within(resolved, normalized)]
    if not matches:
        raise HarnessError(f"target is outside approved roots: {target}")
    original_root, _ = max(matches, key=lambda pair: len(pair[1].parts))
    try:
        relative = target.relative_to(original_root)
    except ValueError:
        relative = resolved.relative_to(original_root.resolve(strict=False))
        original_root = original_root.resolve(strict=False)
    current = original_root
    for part in relative.parts:
        current = current / part
        if current.exists() and current.is_symlink():
            raise HarnessError(f"symbolic-link target is not allowed: {current}")
    return resolved


def validate_profile(data: Any) -> None:
    if not isinstance(data, dict) or not PROFILE_REQUIRED.issubset(data):
        missing = sorted(PROFILE_REQUIRED - set(data if isinstance(data, dict) else {}))
        raise HarnessError(f"profile missing required fields: {', '.join(missing)}")
    if data["schema_version"] != SCHEMA_VERSION:
        raise HarnessError("unsupported profile schema_version")
    if not isinstance(data["user"], dict) or not isinstance(data["scope"], dict):
        raise HarnessError("profile user and scope must be objects")
    if not isinstance(data["decisions"], list):
        raise HarnessError("profile decisions must be an array")


def validate_operations(data: Any) -> None:
    if not isinstance(data, dict) or not PLAN_REQUIRED.issubset(data):
        missing = sorted(PLAN_REQUIRED - set(data if isinstance(data, dict) else {}))
        raise HarnessError(f"operations plan missing required fields: {', '.join(missing)}")
    if data["schema_version"] != SCHEMA_VERSION:
        raise HarnessError("unsupported operations schema_version")
    if not data["run_id"] or not isinstance(data["run_id"], str):
        raise HarnessError("run_id must be a non-empty string")
    if not isinstance(data["allowed_roots"], list) or not data["allowed_roots"]:
        raise HarnessError("allowed_roots must be a non-empty array")
    groups = data["approval_groups"]
    if not isinstance(groups, list) or len(groups) != len(set(groups)):
        raise HarnessError("approval_groups must be a unique array")
    outcome = data["outcome"]
    outcome_fields = {
        "primary_metric",
        "before_state",
        "target_state",
        "unresolved_before",
        "unresolved_target",
        "expected_primary_outputs",
    }
    if not isinstance(outcome, dict) or set(outcome) != outcome_fields:
        raise HarnessError("outcome must contain the exact work-first fields")
    for field in ("primary_metric", "before_state", "target_state"):
        if not isinstance(outcome[field], str) or not outcome[field].strip():
            raise HarnessError(f"outcome.{field} must be a non-empty string")
    for field in ("unresolved_before", "unresolved_target"):
        if not isinstance(outcome[field], int) or isinstance(outcome[field], bool) or outcome[field] < 0:
            raise HarnessError(f"outcome.{field} must be a non-negative integer")
    if outcome["unresolved_target"] > outcome["unresolved_before"]:
        raise HarnessError("outcome.unresolved_target cannot exceed unresolved_before")
    if not isinstance(outcome["expected_primary_outputs"], int) or isinstance(outcome["expected_primary_outputs"], bool) or outcome["expected_primary_outputs"] < 1:
        raise HarnessError("outcome.expected_primary_outputs must be a positive integer")
    budget = data["resource_budget"]
    budget_fields = {
        "max_task_launches",
        "max_support_artifacts",
        "max_verification_passes",
        "max_low_yield_waves",
        "high_cost_approved",
        "cost_warning",
    }
    if not isinstance(budget, dict) or set(budget) != budget_fields:
        raise HarnessError("resource_budget must contain the exact work-first fields")
    launches = budget["max_task_launches"]
    if not isinstance(launches, int) or isinstance(launches, bool) or not 0 <= launches <= 24:
        raise HarnessError("resource_budget.max_task_launches must be from 0 to 24")
    support_limit = budget["max_support_artifacts"]
    if not isinstance(support_limit, int) or isinstance(support_limit, bool) or not 0 <= support_limit <= 12:
        raise HarnessError("resource_budget.max_support_artifacts must be from 0 to 12")
    if budget["max_verification_passes"] != 1 or budget["max_low_yield_waves"] != 1:
        raise HarnessError("resource_budget permits one final verification pass and one low-yield wave")
    if launches > 6:
        if budget["high_cost_approved"] is not True:
            raise HarnessError("a launch cap above 6 requires high_cost_approved=true")
        if not isinstance(budget["cost_warning"], str) or not budget["cost_warning"].strip():
            raise HarnessError("a launch cap above 6 requires a cost warning")
    elif budget["high_cost_approved"] is not False or budget["cost_warning"] is not None:
        raise HarnessError("ordinary launch caps use high_cost_approved=false and cost_warning=null")
    support_artifacts = data["support_artifacts"]
    if not isinstance(support_artifacts, list) or any(not isinstance(item, str) or not item.strip() for item in support_artifacts):
        raise HarnessError("support_artifacts must be a list of non-empty paths")
    if len(support_artifacts) != len(set(support_artifacts)):
        raise HarnessError("support_artifacts must not contain duplicates")
    if len(support_artifacts) > support_limit:
        raise HarnessError("support_artifacts exceeds resource_budget.max_support_artifacts")
    ids: set[str] = set()
    for operation in data["operations"]:
        if not isinstance(operation, dict):
            raise HarnessError("each operation must be an object")
        required = {"id", "action", "target", "approval_group"}
        if not required.issubset(operation):
            raise HarnessError(f"operation missing fields: {operation}")
        if operation["id"] in ids:
            raise HarnessError(f"duplicate operation id: {operation['id']}")
        ids.add(operation["id"])
        if operation["action"] not in {"create", "update"}:
            raise HarnessError(f"unsupported action: {operation['action']}")
        if operation["approval_group"] not in groups:
            raise HarnessError(f"unknown approval group: {operation['approval_group']}")
        if ("content" in operation) == ("source" in operation):
            raise HarnessError(f"operation {operation['id']} needs exactly one of content or source")
        target = Path(operation["target"]).expanduser()
        check_target(target, [Path(root) for root in data["allowed_roots"]])
        if operation["action"] == "update" and not operation.get("expected_sha256"):
            raise HarnessError(f"update {operation['id']} requires expected_sha256")


def operation_bytes(operation: dict[str, Any]) -> bytes:
    if "content" in operation:
        return operation["content"].encode("utf-8")
    source = Path(operation["source"]).expanduser()
    if not source.is_file() or source.is_symlink():
        raise HarnessError(f"operation source is not a regular file: {source}")
    return source.read_bytes()


def backup_name(target: Path) -> str:
    tag = hashlib.sha256(str(target).encode("utf-8")).hexdigest()[:12]
    return f"{tag}-{target.name}"


def apply_plan(
    plan: dict[str, Any],
    mode: str,
    approved: set[str],
    receipt_path: Path,
    backup_dir: Path | None = None,
    manifest_path: Path | None = None,
) -> dict[str, Any]:
    validate_operations(plan)
    unknown = approved - set(plan["approval_groups"])
    if unknown:
        raise HarnessError(f"unrecognized approved groups: {', '.join(sorted(unknown))}")
    roots = [Path(root).expanduser() for root in plan["allowed_roots"]]
    results: list[dict[str, Any]] = []
    manifest_entries: list[dict[str, Any]] = []

    for operation in plan["operations"]:
        if operation["approval_group"] not in approved:
            results.append({"id": operation["id"], "status": "not-approved"})
            continue
        target = check_target(Path(operation["target"]).expanduser(), roots)
        payload = operation_bytes(operation)
        desired_hash = sha256_bytes(payload)
        action = operation["action"]

        if action == "create" and target.exists():
            raise HarnessError(f"create target already exists: {target}")
        if action == "update":
            if not target.is_file() or target.is_symlink():
                raise HarnessError(f"update target is not a regular file: {target}")
            current_hash = sha256_file(target)
            if current_hash != operation["expected_sha256"]:
                raise HarnessError(f"hash changed since audit: {target}")
            if current_hash == desired_hash:
                results.append({"id": operation["id"], "status": "already-current", "sha256": current_hash})
                continue

        if mode == "dry-run":
            results.append({"id": operation["id"], "status": "would-change", "target": str(target), "sha256": desired_hash})
            continue

        if backup_dir is None or manifest_path is None:
            raise HarnessError("apply mode requires --backup-dir and --manifest")
        backup_dir.mkdir(parents=True, exist_ok=True)
        entry: dict[str, Any] = {
            "id": operation["id"],
            "action": action,
            "target": str(target),
            "applied_sha256": desired_hash,
        }
        if action == "update":
            backup = backup_dir / backup_name(target)
            shutil.copy2(target, backup)
            entry["backup"] = str(backup)
            entry["original_sha256"] = sha256_file(backup)
        atomic_write(target, payload)
        manifest_entries.append(entry)
        results.append({"id": operation["id"], "status": "changed", "target": str(target), "sha256": sha256_file(target)})

    receipt = {
        "schema_version": SCHEMA_VERSION,
        "run_id": plan["run_id"],
        "mode": mode,
        "approved_groups": sorted(approved),
        "outcome": plan["outcome"],
        "resource_budget": plan["resource_budget"],
        "results": results,
    }
    write_json(receipt_path, receipt)
    if mode == "apply" and manifest_path is not None:
        write_json(manifest_path, {"schema_version": SCHEMA_VERSION, "run_id": plan["run_id"], "entries": manifest_entries})
    return receipt


def rollback_manifest(manifest: dict[str, Any], receipt_path: Path) -> dict[str, Any]:
    if not isinstance(manifest, dict) or manifest.get("schema_version") != SCHEMA_VERSION:
        raise HarnessError("invalid rollback manifest")
    results: list[dict[str, Any]] = []
    for entry in reversed(manifest.get("entries", [])):
        target = Path(entry["target"])
        if not target.exists() or target.is_symlink():
            raise HarnessError(f"rollback target missing or unsafe: {target}")
        if sha256_file(target) != entry["applied_sha256"]:
            raise HarnessError(f"rollback target changed after apply: {target}")
        if entry["action"] == "create":
            target.unlink()
            results.append({"id": entry["id"], "status": "removed-created-file", "target": str(target)})
        elif entry["action"] == "update":
            backup = Path(entry["backup"])
            if not backup.is_file() or sha256_file(backup) != entry["original_sha256"]:
                raise HarnessError(f"rollback backup invalid: {backup}")
            atomic_write(target, backup.read_bytes())
            results.append({"id": entry["id"], "status": "restored", "target": str(target), "sha256": sha256_file(target)})
        else:
            raise HarnessError(f"unknown rollback action: {entry['action']}")
    receipt = {"schema_version": SCHEMA_VERSION, "run_id": manifest.get("run_id"), "results": results}
    write_json(receipt_path, receipt)
    return receipt


def parse_config_keys(path: Path) -> dict[str, Any]:
    sections: list[str] = []
    keys: list[str] = []
    if not path.is_file():
        return {"exists": False, "sections": sections, "keys": keys}
    for raw in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("[") and line.endswith("]"):
            section = line.strip("[] ")
            sections.append("redacted-sensitive-section" if SECRET_KEY.search(section) else section)
            continue
        if "=" in line:
            key = line.split("=", 1)[0].strip()
            keys.append("redacted-sensitive-key" if SECRET_KEY.search(key) else key)
    return {"exists": True, "sections": sorted(set(sections)), "keys": sorted(set(keys))}


def skill_names(root: Path) -> list[str]:
    names: list[str] = []
    if not root.is_dir():
        return names
    for skill_file in root.glob("*/SKILL.md"):
        try:
            for line in skill_file.read_text(encoding="utf-8").splitlines()[:12]:
                if line.startswith("name:"):
                    names.append(line.split(":", 1)[1].strip().strip('"'))
                    break
        except OSError:
            continue
    return sorted(set(names))


def codex_plugin_inventory() -> list[dict[str, Any]]:
    try:
        run = subprocess.run(["codex", "plugin", "list", "--json"], check=True, capture_output=True, text=True, timeout=20)
        payload = json.loads(run.stdout)
    except (OSError, subprocess.SubprocessError, json.JSONDecodeError):
        return []
    return sorted(
        [
            {
                "name": item.get("name"),
                "marketplace": item.get("marketplaceName"),
                "version": item.get("version"),
                "enabled": bool(item.get("enabled")),
            }
            for item in payload.get("installed", [])
        ],
        key=lambda item: (str(item["marketplace"]), str(item["name"])),
    )


def installed_plugin_inventory(home: Path) -> list[dict[str, Any]]:
    """List installed plugins from Claude Code's installed_plugins.json registry (schema version 2)."""
    registry = home / "plugins" / "installed_plugins.json"
    if not registry.is_file():
        return []
    try:
        payload = json.loads(registry.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return []
    plugins: list[dict[str, Any]] = []
    for key, installs in (payload.get("plugins") or {}).items():
        if not isinstance(installs, list) or not installs:
            continue
        name, _, marketplace = str(key).partition("@")
        for install in installs:
            if not isinstance(install, dict):
                continue
            plugins.append(
                {
                    "name": name,
                    "marketplace": marketplace or None,
                    "version": install.get("version"),
                    "scope": install.get("scope"),
                    "path": install.get("installPath"),
                }
            )
    return sorted(plugins, key=lambda item: (str(item["name"]), str(item["version"])))


def directory_plugin_inventory(root: Path) -> list[dict[str, Any]]:
    """List plugins by reading manifests under a plugin directory (Claude Code cache or Cowork synced dir).

    Covers both layouts: flat (<root>/<plugin>/) and the Claude Code cache
    nesting (<root>/<marketplace>/<plugin>/<version>/).
    """
    plugins: list[dict[str, Any]] = []
    if not root.is_dir():
        return plugins
    manifests = []
    for kind in (".claude-plugin", ".codex-plugin"):
        manifests += sorted(root.glob(f"*/{kind}/plugin.json"))
        manifests += sorted(root.glob(f"*/*/*/{kind}/plugin.json"))
    for manifest in manifests:
        try:
            data = json.loads(manifest.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        plugins.append({"name": data.get("name"), "version": data.get("version"), "path": str(manifest.parents[1])})
    return sorted(plugins, key=lambda item: str(item["name"]))


def json_key_names(path: Path) -> dict[str, Any]:
    """Record top-level key names of a JSON settings file, redacting sensitive names. Never records values."""
    if not path.is_file():
        return {"exists": False, "keys": []}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {"exists": True, "keys": [], "parse_error": True}
    keys = []
    if isinstance(data, dict):
        for key in data:
            keys.append("redacted-sensitive-key" if SECRET_KEY.search(key) else key)
    return {"exists": True, "keys": sorted(keys)}


def detect_platform() -> str:
    if Path("/mnt/user-data/uploads").is_dir() and (Path.home() / ".claude" / "plugins" / "synced").is_dir():
        return "cowork"
    if shutil.which("claude") or (Path.home() / ".claude" / "settings.json").is_file():
        return "claude-code"
    if shutil.which("codex") or Path(os.environ.get("CODEX_HOME", Path.home() / ".codex")).is_dir():
        return "codex"
    return "unknown"


def default_home(target: str) -> Path:
    if target == "codex":
        return Path(os.environ.get("CODEX_HOME", Path.home() / ".codex"))
    return Path(os.environ.get("CLAUDE_CONFIG_DIR", Path.home() / ".claude"))


def instruction_chain(target: str, home: Path, workspace: Path | None) -> list[str]:
    chain: list[str] = []
    if target == "codex":
        names = ["AGENTS.md"]
    else:
        names = ["CLAUDE.md"]
    for name in names:
        candidate = home / name
        if candidate.is_file():
            chain.append(str(candidate))
    if workspace:
        for name in (names + ["CLAUDE.local.md"] if target != "codex" else names):
            candidate = workspace / name
            if candidate.is_file():
                chain.append(str(candidate))
        dot_claude = workspace / ".claude" / "CLAUDE.md"
        if target != "codex" and dot_claude.is_file():
            chain.append(str(dot_claude))
    return chain


def audit_environment(target: str, home_path: Path, workspace: Path | None) -> dict[str, Any]:
    if target == "auto":
        target = detect_platform()
    home = home_path.expanduser().resolve(strict=False)
    workspace_resolved = workspace.expanduser().resolve(strict=False) if workspace else None

    if target == "codex":
        config = parse_config_keys(home / "config.toml")
        plugins: list[dict[str, Any]] = codex_plugin_inventory()
    else:
        config = json_key_names(home / "settings.json")
        plugins = (
            installed_plugin_inventory(home)
            or directory_plugin_inventory(home / "plugins" / "cache")
            or directory_plugin_inventory(home / "plugins" / "synced")
        )

    report: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "target_platform": target,
        "platform": {"system": platform.system(), "release": platform.release(), "python": platform.python_version()},
        "home": str(home),
        "workspace": str(workspace_resolved) if workspace_resolved else None,
        "instruction_chain": instruction_chain(target, home, workspace_resolved),
        "config": config,
        "skills": skill_names(home / "skills"),
        "plugins": plugins,
        "surfaces": {
            "hooks_file": (home / "hooks.json").is_file(),
            "rules_directory": (home / "rules").is_dir(),
            "memories_directory": (home / "memories").is_dir(),
            "agents_directory": (home / "agents").is_dir(),
            "commands_directory": (home / "commands").is_dir(),
            "computer_use_bundle": (home / "computer-use").exists(),
        },
    }
    if target == "cowork" and workspace_resolved:
        contract: list[str] = []
        for name in ("CLAUDE.md", "about-me.md", "voice-and-style.md", "working-rules.md"):
            candidate = workspace_resolved / name
            if candidate.is_file():
                contract.append(name)
        report["cowork_contract_files"] = contract
    return report


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Harness Engineering deterministic local operations")
    sub = parser.add_subparsers(dest="command", required=True)

    audit = sub.add_parser("audit")
    audit.add_argument("--output", required=True, type=Path)
    audit.add_argument("--platform", choices=["auto", "claude-code", "cowork", "codex"], default="auto", dest="target_platform")
    audit.add_argument("--home", type=Path, help="config home override; defaults per platform")
    audit.add_argument("--codex-home", type=Path, help="deprecated alias for --home with --platform codex")
    audit.add_argument("--workspace", type=Path)

    profile = sub.add_parser("validate-profile")
    profile.add_argument("path", type=Path)

    operations = sub.add_parser("validate-operations")
    operations.add_argument("path", type=Path)

    apply_cmd = sub.add_parser("apply")
    apply_cmd.add_argument("path", type=Path)
    apply_cmd.add_argument("--mode", choices=["dry-run", "apply"], default="dry-run")
    apply_cmd.add_argument("--approved", action="append", required=True)
    apply_cmd.add_argument("--backup-dir", type=Path)
    apply_cmd.add_argument("--receipt", type=Path, required=True)
    apply_cmd.add_argument("--manifest", type=Path)

    rollback = sub.add_parser("rollback")
    rollback.add_argument("manifest", type=Path)
    rollback.add_argument("--receipt", type=Path, required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.command == "audit":
            target = args.target_platform
            if args.codex_home is not None and args.home is None:
                target = "codex" if target == "auto" else target
                home = args.codex_home
            else:
                resolved = detect_platform() if target == "auto" else target
                home = args.home if args.home is not None else default_home(resolved)
                target = resolved
            write_json(args.output, audit_environment(target, home, args.workspace))
        elif args.command == "validate-profile":
            validate_profile(load_json(args.path))
            print("profile valid")
        elif args.command == "validate-operations":
            validate_operations(load_json(args.path))
            print("operations plan valid")
        elif args.command == "apply":
            approved = {item for group in args.approved for item in group.split(",") if item}
            apply_plan(load_json(args.path), args.mode, approved, args.receipt, args.backup_dir, args.manifest)
        elif args.command == "rollback":
            rollback_manifest(load_json(args.manifest), args.receipt)
        return 0
    except HarnessError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
