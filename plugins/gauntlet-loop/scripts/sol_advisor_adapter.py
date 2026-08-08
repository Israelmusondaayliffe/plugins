#!/usr/bin/env python3
"""Compile and register Sol Advisor packets as bounded Gauntlet operations."""

from __future__ import annotations

import argparse
import copy
import hashlib
import importlib.util
import json
import os
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from types import ModuleType
from typing import Any


GAUNTLET_OWNED_SURFACES = (
    "state",
    "budget",
    "approval",
    "integration",
    "final_answer",
    "terminal_verdict",
)
MODEL_EFFORTS = {
    "gpt-5.6-sol": {"high", "xhigh"},
    "gpt-5.6-luna": {"max"},
    "gpt-5.6-terra": {"max"},
}
SHA256 = re.compile(r"^[0-9a-f]{64}$")
TASK_RECORD_STATUSES = {"authorized", "compiled", "created", "active", "running", "dispatched", "repairing", "succeeded", "blocked", "failed", "escalate"}
TERMINAL_TASK_STATUSES = {"succeeded", "blocked", "failed", "escalate"}
OCCUPYING_TASK_STATUSES = {"compiled", "created", "active", "running", "dispatched", "repairing"}
ACTIVE_CONCURRENCY_STATUSES = {"created", "active", "running", "dispatched", "repairing"}


class AdapterError(RuntimeError):
    """Raised when an adapter request would violate the composition contract."""


@dataclass(frozen=True)
class GauntletContext:
    project_root: Path
    gauntlet_root: Path
    state: dict[str, Any]
    program: dict[str, Any]
    budget_ledger: dict[str, Any]
    plan_path: Path
    runtime_capabilities: dict[str, Any]
    task_records_path: Path
    task_records: dict[str, Any]


def utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


def read_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise AdapterError(f"missing file: {path}") from exc
    except json.JSONDecodeError as exc:
        raise AdapterError(f"invalid JSON in {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise AdapterError(f"JSON object required: {path}")
    return data


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def json_bytes(data: dict[str, Any]) -> bytes:
    return (json.dumps(data, indent=2) + "\n").encode("utf-8")


def is_descendant(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
    except ValueError:
        return False
    return True


def normal_path(value: Any, label: str) -> Path:
    if not isinstance(value, str) or not value.strip():
        raise AdapterError(f"{label} must be a non-empty path")
    raw = Path(value)
    if not raw.is_absolute():
        raise AdapterError(f"{label} must be an absolute path")
    if ".." in raw.parts:
        raise AdapterError(f"{label} must not contain parent traversal")
    path = raw.resolve()
    if path == Path("/") or len(path.parts) < 3:
        raise AdapterError(f"{label} is too broad")
    return path


def relative_project_path(path: Path, project_root: Path, label: str) -> str:
    resolved = path.resolve()
    if not is_descendant(resolved, project_root):
        raise AdapterError(f"{label} must stay beneath the project root")
    return str(resolved.relative_to(project_root))


def resolve_project_reference(value: Any, project_root: Path, label: str) -> Path:
    if not isinstance(value, str) or not value.strip():
        raise AdapterError(f"{label} must be a non-empty relative path")
    raw = Path(value)
    if raw.is_absolute() or ".." in raw.parts:
        raise AdapterError(f"{label} must stay beneath the project root")
    path = (project_root / raw).resolve()
    if not is_descendant(path, project_root):
        raise AdapterError(f"{label} must stay beneath the project root")
    return path


def scopes_overlap(left: Path, right: Path) -> bool:
    return is_descendant(left, right) or is_descendant(right, left)


def write_new_json(path: Path, data: dict[str, Any]) -> None:
    if path.exists():
        raise AdapterError(f"refusing to overwrite existing output: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def write_json_atomic(path: Path, data: dict[str, Any]) -> None:
    if not path.is_file():
        raise AdapterError(f"Gauntlet-owned file is missing: {path}")
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def append_markdown_atomic(path: Path, line: str) -> None:
    if not path.is_file():
        raise AdapterError(f"Gauntlet-owned file is missing: {path}")
    content = path.read_text(encoding="utf-8")
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(content.rstrip() + "\n" + line.rstrip() + "\n", encoding="utf-8")
    temporary.replace(path)


def write_file_transaction(updates: dict[Path, bytes], *, new_paths: set[Path] | None = None) -> None:
    allowed_new = {path.resolve() for path in (new_paths or set())}
    originals: dict[Path, bytes | None] = {}
    staged: dict[Path, Path] = {}
    committed: list[Path] = []
    try:
        for index, (path, payload) in enumerate(updates.items()):
            is_new = path.resolve() in allowed_new
            if is_new:
                if path.exists():
                    raise AdapterError(f"refusing to overwrite existing output: {path}")
                if not path.parent.is_dir():
                    raise AdapterError(f"output parent directory is missing: {path.parent}")
                originals[path] = None
            else:
                if not path.is_file():
                    raise AdapterError(f"Gauntlet-owned file is missing: {path}")
                originals[path] = path.read_bytes()
            stage = path.with_name(f"{path.name}.sol-advisor-stage-{os.getpid()}-{index}")
            stage.write_bytes(payload)
            staged[path] = stage
    except (OSError, AdapterError) as exc:
        for stage in staged.values():
            stage.unlink(missing_ok=True)
        if isinstance(exc, AdapterError):
            raise
        raise AdapterError(f"Gauntlet registration transaction staging failed: {exc}") from exc
    try:
        for path, stage in staged.items():
            os.replace(stage, path)
            committed.append(path)
    except OSError as exc:
        rollback_errors: list[str] = []
        for index, path in enumerate(reversed(committed)):
            try:
                original = originals[path]
                if original is None:
                    path.unlink(missing_ok=True)
                else:
                    rollback = path.with_name(f"{path.name}.sol-advisor-rollback-{os.getpid()}-{index}")
                    rollback.write_bytes(original)
                    os.replace(rollback, path)
            except OSError as rollback_exc:
                rollback_errors.append(f"{path}: {rollback_exc}")
        for stage in staged.values():
            stage.unlink(missing_ok=True)
        suffix = f"; rollback failures: {'; '.join(rollback_errors)}" if rollback_errors else ""
        raise AdapterError(f"Gauntlet registration transaction failed and was rolled back: {exc}{suffix}") from exc


def protocol_validator(protocol_root: Path) -> ModuleType:
    path = protocol_root.resolve() / "skills" / "sol-advisor" / "scripts" / "validate_packets.py"
    if not path.is_file():
        raise AdapterError(f"canonical Sol Advisor packet validator is missing: {path}")
    specification = importlib.util.spec_from_file_location("sol_advisor_packet_validator", path)
    if specification is None or specification.loader is None:
        raise AdapterError(f"cannot load canonical Sol Advisor packet validator: {path}")
    module = importlib.util.module_from_spec(specification)
    specification.loader.exec_module(module)
    if not hasattr(module, "validate_packet"):
        raise AdapterError("canonical Sol Advisor packet validator does not export validate_packet")
    return module


def validate_packet(validator: ModuleType, packet: dict[str, Any], *, evidence_root: Path, label: str) -> None:
    errors = validator.validate_packet(packet, evidence_root)
    if errors:
        raise AdapterError(f"{label} failed canonical protocol validation: {'; '.join(errors)}")


def validate_program_graph(program: dict[str, Any]) -> None:
    workstreams = program.get("workstreams")
    if not isinstance(workstreams, list) or not workstreams:
        raise AdapterError("compiled Gauntlet program requires workstreams")
    ids: list[str] = []
    dependencies: dict[str, list[str]] = {}
    for item in workstreams:
        if not isinstance(item, dict) or not isinstance(item.get("id"), str) or not item["id"]:
            raise AdapterError("every compiled workstream requires a non-empty id")
        workstream_id = item["id"]
        ids.append(workstream_id)
        raw_dependencies = item.get("dependencies")
        if not isinstance(raw_dependencies, list) or any(not isinstance(dep, str) or not dep for dep in raw_dependencies):
            raise AdapterError(f"workstream {workstream_id} has invalid dependencies")
        dependencies[workstream_id] = raw_dependencies
    if len(ids) != len(set(ids)):
        raise AdapterError("compiled workstream IDs must be unique")
    known = set(ids)
    if any(dependency not in known for values in dependencies.values() for dependency in values):
        raise AdapterError("compiled workstream graph has an unknown dependency")
    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(workstream_id: str) -> None:
        if workstream_id in visiting:
            raise AdapterError(f"compiled workstream graph contains a cycle at {workstream_id}")
        if workstream_id in visited:
            return
        visiting.add(workstream_id)
        for dependency in dependencies[workstream_id]:
            visit(dependency)
        visiting.remove(workstream_id)
        visited.add(workstream_id)

    for workstream_id in ids:
        visit(workstream_id)


def validate_state_authority(state: dict[str, Any]) -> None:
    owner = state.get("owner")
    if owner is not None and owner != "gauntlet":
        raise AdapterError("canonical Gauntlet state has competing authority")
    authority = state.get("authority")
    if authority is not None:
        if not isinstance(authority, dict) or any(authority.get(surface) != "gauntlet" for surface in GAUNTLET_OWNED_SURFACES):
            raise AdapterError("canonical Gauntlet state has competing authority")


def validate_runtime_capabilities(capabilities: dict[str, Any]) -> None:
    support = capabilities.get("model_effort_support")
    if not isinstance(support, dict):
        raise AdapterError("runtime capability record omits model_effort_support")
    for model, efforts in MODEL_EFFORTS.items():
        available = support.get(model)
        if not isinstance(available, list) or not efforts.issubset(set(available)):
            raise AdapterError(f"runtime does not attest required {model} efforts: {sorted(efforts)}")


def positive_int(value: Any, label: str) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or value < 1:
        raise AdapterError(f"{label} must be a positive integer")
    return value


def validate_budget(program: dict[str, Any], ledger: dict[str, Any], *, reserve_launch: bool, reserve_elapsed_minutes: int) -> None:
    budget = program.get("budget")
    usage = ledger.get("usage")
    if not isinstance(budget, dict) or not isinstance(usage, dict):
        raise AdapterError("compiled program and budget ledger must contain budget objects")
    if ledger.get("limits") != budget:
        raise AdapterError("budget ledger limits are missing or stale")
    if not isinstance(reserve_elapsed_minutes, int) or reserve_elapsed_minutes < 0:
        raise AdapterError("reserved elapsed time must be a non-negative integer")
    usage_checks = (
        ("elapsed_minutes", "max_elapsed_minutes"),
        ("agent_launches", "max_agent_launches"),
        ("peak_concurrency", "max_concurrency"),
    )
    for usage_key, limit_key in usage_checks:
        value = usage.get(usage_key)
        limit = positive_int(budget.get(limit_key), f"budget limit {limit_key}")
        if not isinstance(value, int) or isinstance(value, bool) or value < 0:
            raise AdapterError(f"budget usage {usage_key} must be a non-negative integer")
        if value > limit:
            raise AdapterError(f"budget exhausted: {usage_key}={value} exceeds {limit_key}={limit}")
        if usage_key == "elapsed_minutes":
            if value >= limit:
                raise AdapterError(f"budget exhausted: {usage_key} has no remaining capacity")
            if value + reserve_elapsed_minutes > limit:
                raise AdapterError(f"budget exhausted: elapsed reservation exceeds {limit_key}")
        if usage_key == "agent_launches" and reserve_launch:
            if value >= limit or value + 1 > limit:
                raise AdapterError(f"budget exhausted: agent launch exceeds {limit_key}")
    rounds = usage.get("critic_rounds")
    round_limit = positive_int(budget.get("max_critic_rounds_per_workstream"), "budget max_critic_rounds_per_workstream")
    if not isinstance(rounds, dict):
        raise AdapterError("budget critic-round record is invalid")
    for workstream_id, count in rounds.items():
        if not isinstance(workstream_id, str) or not isinstance(count, int) or isinstance(count, bool) or count < 0:
            raise AdapterError("budget critic-round record is invalid")
        if count > round_limit:
            raise AdapterError(f"critic rounds exhausted for {workstream_id}: {count}>{round_limit}")


def load_context(project_root: Path, *, reserve_launch: bool, reserve_elapsed_minutes: int = 0) -> GauntletContext:
    project = project_root.resolve()
    gauntlet_root = project / ".gauntlet"
    if not project.is_dir() or not gauntlet_root.is_dir():
        raise AdapterError(f"project must contain a Gauntlet workspace: {project}")
    state = read_json(gauntlet_root / "state.json")
    program = read_json(gauntlet_root / "gauntlet.yaml")
    ledger = read_json(gauntlet_root / "budget-ledger.json")
    plan_path = gauntlet_root / "plan.md"
    capabilities = read_json(gauntlet_root / "runtime-capabilities.json")
    task_records_path = gauntlet_root / "runtime-task-records.json"
    task_records = read_json(task_records_path)
    if state.get("state") not in {"gauntlet_compiled", "executing"}:
        raise AdapterError("Sol Advisor composition requires Gauntlet state gauntlet_compiled or executing")
    if program.get("status") != "compiled":
        raise AdapterError("Sol Advisor composition requires a compiled Gauntlet program")
    if state.get("plan_version") != program.get("plan_version") or state.get("program_version") != program.get("version"):
        raise AdapterError("Gauntlet state and program versions are stale or disagree")
    if not plan_path.is_file() or "Status: approved" not in plan_path.read_text(encoding="utf-8"):
        raise AdapterError("Gauntlet plan is not approved")
    actual_plan_hash = sha256_file(plan_path)
    if not isinstance(program.get("plan_sha256"), str) or not SHA256.fullmatch(program["plan_sha256"]) or program["plan_sha256"] != actual_plan_hash:
        raise AdapterError("compiled Gauntlet program plan hash is missing or stale")
    if not isinstance(program.get("goal"), str) or not program["goal"].strip():
        raise AdapterError("compiled Gauntlet program goal is missing")
    panel = program.get("verification_panel")
    if not isinstance(panel, list) or len(panel) < 3 or len(panel) != len(set(panel)):
        raise AdapterError("compiled Gauntlet program must preserve three independent verification perspectives")
    decisions = gauntlet_root / "decisions.md"
    if not decisions.is_file() or "Approval:" not in decisions.read_text(encoding="utf-8"):
        raise AdapterError("Gauntlet approval record is missing")
    validate_state_authority(state)
    validate_program_graph(program)
    validate_budget(program, ledger, reserve_launch=reserve_launch, reserve_elapsed_minutes=reserve_elapsed_minutes)
    validate_runtime_capabilities(capabilities)
    return GauntletContext(
        project_root=project,
        gauntlet_root=gauntlet_root,
        state=state,
        program=program,
        budget_ledger=ledger,
        plan_path=plan_path,
        runtime_capabilities=capabilities,
        task_records_path=task_records_path,
        task_records=task_records,
    )


def find_workstream(program: dict[str, Any], workstream_id: str) -> dict[str, Any]:
    for item in program.get("workstreams", []):
        if isinstance(item, dict) and item.get("id") == workstream_id:
            return item
    raise AdapterError(f"unknown compiled workstream: {workstream_id}")


def plan_snapshot(context: GauntletContext) -> dict[str, Any]:
    return {
        "status": "approved",
        "version": context.program["plan_version"],
        "path": relative_project_path(context.plan_path, context.project_root, "approved plan"),
        "sha256": sha256_file(context.plan_path),
    }


def validate_manifest_budget(manifest: dict[str, Any], context: GauntletContext) -> None:
    manifest_budget = manifest.get("budget")
    program_budget = context.program.get("budget")
    if not isinstance(manifest_budget, dict) or not isinstance(program_budget, dict):
        raise AdapterError("RunManifest and compiled program require budgets")
    exact = (
        ("max_task_launches", "max_agent_launches"),
        ("max_concurrency", "max_concurrency"),
        ("max_critic_rounds_per_workstream", "max_critic_rounds_per_workstream"),
        ("max_elapsed_minutes", "max_elapsed_minutes"),
    )
    for manifest_key, program_key in exact:
        if manifest_budget.get(manifest_key) != program_budget.get(program_key):
            raise AdapterError(f"RunManifest budget {manifest_key} does not exactly match the compiled Gauntlet budget")
    if manifest_budget.get("max_repair_rounds_per_workstream") != program_budget.get("max_critic_rounds_per_workstream"):
        raise AdapterError("RunManifest repair limit does not exactly match the compiled Gauntlet critic-round limit")


def validate_composed_manifest(context: GauntletContext, manifest_path: Path, validator: ModuleType) -> dict[str, Any]:
    if not manifest_path.is_file():
        raise AdapterError(f"missing RunManifest: {manifest_path}")
    manifest = read_json(manifest_path)
    validate_packet(validator, manifest, evidence_root=context.project_root, label="RunManifest")
    if manifest.get("mode") != "gauntlet_composed":
        raise AdapterError("Gauntlet adapter accepts only gauntlet_composed RunManifest packets")
    if manifest.get("plan") != plan_snapshot(context):
        raise AdapterError("RunManifest plan version or hash is stale")
    if manifest.get("parent_runtime_attestation", {}).get("effective_model_source") != "host_metadata":
        raise AdapterError("RunManifest parent effective model evidence is unavailable or not host metadata")
    authority = manifest.get("authority", {})
    for surface in GAUNTLET_OWNED_SURFACES:
        if authority.get(surface) != "gauntlet":
            raise AdapterError(f"RunManifest has competing authority for {surface}")
    validate_manifest_budget(manifest, context)
    return manifest


def manifest_authorizations(manifest: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {item["task_id"]: item for item in manifest["task_authorization"]}


def relative_reference_if_present(value: Any, context: GauntletContext, label: str) -> Path | None:
    if value is None:
        return None
    path = resolve_project_reference(value, context.project_root, label)
    if not path.is_file():
        raise AdapterError(f"{label} must resolve to an existing file")
    return path


def validate_canonical_task_records(context: GauntletContext, manifest: dict[str, Any], validator: ModuleType) -> dict[str, dict[str, Any]]:
    records_doc = context.task_records
    required_doc = {"schema_version", "owner", "run_id", "plan_version", "plan_sha256", "records"}
    if set(records_doc) != required_doc:
        raise AdapterError("canonical Gauntlet task records have an unsupported authority shape")
    if records_doc.get("schema_version") != 1 or records_doc.get("owner") != "gauntlet":
        raise AdapterError("canonical Gauntlet task records have competing authority")
    if records_doc.get("run_id") != manifest.get("run_id"):
        raise AdapterError("canonical Gauntlet task records are for another run")
    if records_doc.get("plan_version") != context.program.get("plan_version") or records_doc.get("plan_sha256") != sha256_file(context.plan_path):
        raise AdapterError("canonical Gauntlet task records have a stale plan")
    raw_records = records_doc.get("records")
    if not isinstance(raw_records, list):
        raise AdapterError("canonical Gauntlet task records must contain a records list")
    authorizations = manifest_authorizations(manifest)
    result: dict[str, dict[str, Any]] = {}
    expected_fields = {
        "task_id",
        "run_id",
        "workstream_id",
        "classification",
        "dependencies",
        "status",
        "write_scope",
        "authorization",
        "runtime_attestation",
        "repair_round",
        "run_manifest_sha256",
        "task_packet_path",
        "task_packet_sha256",
        "return_packet_path",
        "return_packet_sha256",
        "actual_write_scope",
        "artifacts",
        "evidence",
        "compiled_at",
        "registered_at",
    }
    manifest_hash = sha256_file(Path(manifest.get("_path", ""))) if manifest.get("_path") else None
    for index, record in enumerate(raw_records):
        label = f"canonical Gauntlet task record {index}"
        if not isinstance(record, dict) or set(record) != expected_fields:
            raise AdapterError(f"{label} has an unsupported record shape")
        task_id = record.get("task_id")
        if not isinstance(task_id, str) or not task_id or task_id in result:
            raise AdapterError("canonical Gauntlet task records require unique task IDs")
        result[task_id] = record
        if record.get("run_id") != manifest.get("run_id"):
            raise AdapterError(f"{label} run_id does not match RunManifest")
        if record.get("status") not in TASK_RECORD_STATUSES:
            raise AdapterError(f"{label} has invalid status")
        if not isinstance(record.get("repair_round"), int) or isinstance(record.get("repair_round"), bool) or record["repair_round"] < 0:
            raise AdapterError(f"{label} repair_round is invalid")
        authorization = authorizations.get(task_id)
        if authorization is None or record.get("authorization") != authorization:
            raise AdapterError(f"{label} is not exactly authorized by the RunManifest")
        if record.get("workstream_id") != authorization.get("workstream_id") or record.get("classification") != authorization.get("classification"):
            raise AdapterError(f"{label} does not match its exact task authorization")
        if record.get("dependencies") != authorization.get("dependencies"):
            raise AdapterError(f"{label} dependencies do not match its exact task authorization")
        if record.get("write_scope") != authorization.get("allowed_write_paths"):
            raise AdapterError(f"{label} write scope does not match its exact task authorization")
        scopes = [normal_path(value, f"{label} write scope") for value in record["write_scope"]]
        for left_index, left in enumerate(scopes):
            for right in scopes[left_index + 1 :]:
                if scopes_overlap(left, right):
                    raise AdapterError(f"{label} write scope overlaps itself")
        runtime_errors: list[str] = []
        model = "gpt-5.6-luna" if record.get("classification") == "routine" else "gpt-5.6-terra"
        validator.validate_creation_attestation(
            record.get("runtime_attestation"),
            f"{label}.runtime_attestation",
            runtime_errors,
            context.project_root,
            run_id=manifest.get("run_id"),
            task_id=task_id,
            reviewer_id=None,
            role="worker",
            model=model,
            effort="max",
            target="codex_task",
        )
        if runtime_errors:
            raise AdapterError(f"{label} runtime evidence is missing or forged: {'; '.join(runtime_errors)}")
        if record.get("run_manifest_sha256") != manifest_hash:
            raise AdapterError(f"{label} RunManifest hash does not match canonical authority")
        task_path = relative_reference_if_present(record.get("task_packet_path"), context, f"{label}.task_packet_path")
        task_hash = record.get("task_packet_sha256")
        if (task_path is None) != (task_hash is None):
            raise AdapterError(f"{label} task packet path and hash must appear together")
        if task_path is not None:
            if not isinstance(task_hash, str) or not SHA256.fullmatch(task_hash) or sha256_file(task_path) != task_hash:
                raise AdapterError(f"{label} task packet hash is forged or stale")
            workstream_root = (context.gauntlet_root / "workstreams" / str(record.get("workstream_id"))).resolve()
            if not is_descendant(task_path, workstream_root):
                raise AdapterError(f"{label} task packet is outside its canonical workstream")
        return_path = relative_reference_if_present(record.get("return_packet_path"), context, f"{label}.return_packet_path")
        return_hash = record.get("return_packet_sha256")
        if (return_path is None) != (return_hash is None):
            raise AdapterError(f"{label} return packet path and hash must appear together")
        if return_path is not None and (not isinstance(return_hash, str) or not SHA256.fullmatch(return_hash) or sha256_file(return_path) != return_hash):
            raise AdapterError(f"{label} return packet hash is forged or stale")
        if record.get("status") == "authorized" and (task_path is not None or return_path is not None):
            raise AdapterError(f"{label} authorized task must not already have packets")
        if record.get("status") in OCCUPYING_TASK_STATUSES and task_path is None:
            raise AdapterError(f"{label} active task must have a canonical TaskPacket")
        if record.get("status") in TERMINAL_TASK_STATUSES and return_path is None:
            raise AdapterError(f"{label} terminal task must have a canonical ReturnPacket")
        for timestamp_key in ("compiled_at", "registered_at"):
            timestamp = record.get(timestamp_key)
            if timestamp is not None:
                if not isinstance(timestamp, str):
                    raise AdapterError(f"{label} {timestamp_key} must be an ISO timestamp or null")
                try:
                    datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
                except ValueError as exc:
                    raise AdapterError(f"{label} {timestamp_key} must be an ISO timestamp or null") from exc
    if set(result) != set(authorizations):
        raise AdapterError("canonical Gauntlet task records and RunManifest task authorization must name the same task IDs")
    return result


def safe_workstream_scopes(context: GauntletContext, workstream: dict[str, Any], selected_targets: list[str]) -> list[Path]:
    approved_raw = workstream.get("write_targets")
    if not isinstance(approved_raw, list) or not approved_raw:
        raise AdapterError(f"workstream {workstream.get('id')} has no approved write targets")
    approved = [normal_path(item, "compiled write target") for item in approved_raw]
    if not selected_targets:
        raise AdapterError("compile-task requires at least one --write-target")
    selected = [normal_path(item, "selected write target") for item in selected_targets]
    if len(selected) != len(set(selected)):
        raise AdapterError("selected write targets must be unique")
    for candidate in selected:
        if candidate not in approved:
            raise AdapterError(f"selected write target is outside the compiled workstream scope: {candidate}")
        if candidate in {context.project_root, context.gauntlet_root, context.project_root.parent}:
            raise AdapterError(f"selected write target is too broad: {candidate}")
    for index, left in enumerate(selected):
        for right in selected[index + 1 :]:
            if scopes_overlap(left, right):
                raise AdapterError("selected write targets overlap")
    return selected


def criteria_for_workstream(workstream: dict[str, Any]) -> list[dict[str, str]]:
    values = workstream.get("acceptance_criteria")
    if not isinstance(values, list) or not values or any(not isinstance(value, str) or not value.strip() for value in values):
        raise AdapterError(f"compiled workstream {workstream.get('id')} has invalid acceptance criteria")
    return [{"id": value, "description": value} for value in values]


def validate_task_record_for_workstream(
    context: GauntletContext,
    manifest: dict[str, Any],
    records: dict[str, dict[str, Any]],
    record: dict[str, Any],
    workstream: dict[str, Any],
    *,
    selected_scopes: list[Path],
) -> None:
    authorization = record["authorization"]
    if authorization.get("workstream_id") != workstream.get("id"):
        raise AdapterError("task authorization does not match the compiled workstream")
    if authorization.get("acceptance_criteria") != criteria_for_workstream(workstream):
        raise AdapterError("task authorization criteria do not exactly match the compiled workstream")
    actual_paths = [normal_path(value, "task authorization write scope") for value in authorization["allowed_write_paths"]]
    compiled_paths = safe_workstream_scopes(context, workstream, list(authorization["allowed_write_paths"]))
    if actual_paths != compiled_paths:
        raise AdapterError("task authorization write scope does not exactly match the compiled workstream")
    if actual_paths != selected_scopes:
        raise AdapterError("selected write targets do not exactly match the authorized task scope")
    if record.get("repair_round", 0) > manifest["budget"]["max_repair_rounds_per_workstream"]:
        raise AdapterError("repair budget is exhausted for the authorized task")
    dependencies = record.get("dependencies", [])
    for dependency in dependencies:
        dependency_record = records.get(dependency)
        if dependency_record is None or dependency_record.get("status") != "succeeded":
            raise AdapterError(f"task dependency is unresolved: {dependency}")
    expected_workstream_dependencies = set(workstream.get("dependencies", []))
    actual_workstream_dependencies = {records[dependency]["workstream_id"] for dependency in dependencies if dependency in records}
    if actual_workstream_dependencies != expected_workstream_dependencies:
        raise AdapterError("task dependencies do not exactly cover the compiled workstream dependencies")


def reject_active_overlap(context: GauntletContext, records: dict[str, dict[str, Any]], current_task_id: str, selected_scopes: list[Path], manifest: dict[str, Any]) -> None:
    active_count = sum(1 for record in records.values() if record.get("status") in ACTIVE_CONCURRENCY_STATUSES)
    if active_count + 1 > manifest["budget"]["max_concurrency"]:
        raise AdapterError("current concurrency budget is exhausted")
    for task_id, record in records.items():
        if task_id == current_task_id or record.get("status") not in OCCUPYING_TASK_STATUSES:
            continue
        existing = [normal_path(value, f"canonical active task {task_id} write scope") for value in record["write_scope"]]
        for selected in selected_scopes:
            if any(scopes_overlap(selected, scope) for scope in existing):
                raise AdapterError(f"selected write scope overlaps undisclosed canonical active task: {task_id}")


def non_authoritative_output(root: Path, output: Path, workstream_id: str) -> Path:
    path = output.resolve()
    allowed = (root / "workstreams" / workstream_id).resolve()
    if not is_descendant(path, allowed):
        raise AdapterError("adapter output must stay beneath the owning workstream directory, not canonical Gauntlet authority")
    protected_names = {
        "state.json",
        "gauntlet.yaml",
        "budget-ledger.json",
        "plan.md",
        "decisions.md",
        "runtime-task-records.json",
        "run-manifest.json",
        "review-packet.json",
        "return-packet.json",
        "final-answer.md",
        "terminal-verdict.json",
        "verdict.json",
    }
    if path.name in protected_names:
        raise AdapterError(f"adapter must not write canonical Gauntlet authority: {path.name}")
    return path


def task_output_authority(context: GauntletContext, task: dict[str, Any]) -> tuple[list[Path], list[str]]:
    raw_scopes = task.get("scope", {}).get("allowed_write_paths")
    if not isinstance(raw_scopes, list) or not raw_scopes:
        raise AdapterError("TaskPacket must declare non-empty allowed write paths")
    allowed = [normal_path(value, "TaskPacket write scope") for value in raw_scopes]
    expected = task.get("expected_output", {}).get("paths")
    if not isinstance(expected, list) or not expected or any(not isinstance(value, str) or not value.strip() for value in expected):
        raise AdapterError("TaskPacket expected output paths are invalid")
    for index, value in enumerate(expected):
        resolved = resolve_project_reference(value, context.project_root, f"TaskPacket expected output[{index}]")
        if not any(is_descendant(resolved, scope) for scope in allowed):
            raise AdapterError("TaskPacket expected output is outside its allowed write authority")
    return allowed, expected


def validate_artifact_authority(
    context: GauntletContext,
    task: dict[str, Any],
    artifacts: Any,
    *,
    label: str,
) -> None:
    allowed, expected = task_output_authority(context, task)
    if not isinstance(artifacts, list):
        raise AdapterError(f"{label} artifacts must be a list")
    actual = [item.get("path") for item in artifacts if isinstance(item, dict)]
    if len(actual) != len(artifacts) or actual != expected:
        raise AdapterError(f"{label} artifacts do not exactly match the authorized expected output paths")
    for index, value in enumerate(actual):
        resolved = resolve_project_reference(value, context.project_root, f"{label} artifact[{index}]")
        if not any(is_descendant(resolved, scope) for scope in allowed):
            raise AdapterError(f"{label} artifact is outside TaskPacket write authority")


def build_task_packet(context: GauntletContext, manifest_path: Path, manifest: dict[str, Any], record: dict[str, Any], workstream: dict[str, Any]) -> dict[str, Any]:
    authorization = copy.deepcopy(record["authorization"])
    return {
        "packet_type": "TaskPacket",
        "protocol_version": 1,
        "run_id": manifest["run_id"],
        "task_id": record["task_id"],
        "run_manifest_path": relative_project_path(manifest_path, context.project_root, "RunManifest"),
        "run_manifest_sha256": sha256_file(manifest_path),
        "plan": plan_snapshot(context),
        "task": {
            "classification": record["classification"],
            "objective": workstream["objective"],
            "dependencies": copy.deepcopy(record["dependencies"]),
        },
        "authorization": authorization,
        "worker": {
            "role": "worker",
            "model": authorization["model"],
            "reasoning_effort": authorization["reasoning_effort"],
            "fresh_task": True,
            "creation_method": "create_thread",
            "forked": False,
            "may_spawn_workers": False,
            "may_approve": False,
            "may_integrate": False,
            "may_issue_final_verdict": False,
        },
        "runtime_attestation": copy.deepcopy(record["runtime_attestation"]),
        "input_paths": copy.deepcopy(authorization["input_paths"]),
        "expected_output": copy.deepcopy(authorization["expected_output"]),
        "acceptance_criteria": copy.deepcopy(authorization["acceptance_criteria"]),
        "tools": copy.deepcopy(authorization["tools"]),
        "scope": {
            "workstream_id": authorization["workstream_id"],
            "allowed_write_paths": copy.deepcopy(authorization["allowed_write_paths"]),
            "read_paths": [item["path"] for item in authorization["input_paths"]],
        },
        "evidence_commands": copy.deepcopy(authorization["evidence_commands"]),
        "stop_conditions": copy.deepcopy(authorization["stop_conditions"]),
        "limits": copy.deepcopy(authorization["limits"]),
        "context": {
            "delivery": "bounded_packet_only",
            "include_parent_transcript": False,
            "include_hidden_reasoning": False,
            "reference_paths": [item["path"] for item in authorization["input_paths"]],
        },
    }


def command_compile_task(args: argparse.Namespace) -> dict[str, Any]:
    if getattr(args, "existing_task", None):
        raise AdapterError("caller-supplied active task lists are forbidden; use canonical Gauntlet task records")
    if not isinstance(args.max_elapsed_minutes, int) or args.max_elapsed_minutes < 1:
        raise AdapterError("max_elapsed_minutes must be a positive finite integer")
    if args.max_retries not in {0, 1}:
        raise AdapterError("max_retries must be 0 or 1")
    context = load_context(Path(args.project_root), reserve_launch=True, reserve_elapsed_minutes=args.max_elapsed_minutes)
    validator = protocol_validator(Path(args.protocol_root))
    manifest_path = Path(args.run_manifest).resolve()
    manifest = validate_composed_manifest(context, manifest_path, validator)
    manifest["_path"] = str(manifest_path)
    records = validate_canonical_task_records(context, manifest, validator)
    workstream = find_workstream(context.program, args.workstream_id)
    record = records.get(args.task_id)
    if record is None:
        raise AdapterError("task_id is not authorized by canonical Gauntlet task records")
    if record.get("status") != "authorized":
        raise AdapterError("task_id is already active, compiled, or completed in canonical Gauntlet task records")
    if args.classification != record.get("classification"):
        raise AdapterError("classification does not exactly match canonical task authorization")
    selected_scopes = safe_workstream_scopes(context, workstream, list(args.write_target))
    validate_task_record_for_workstream(context, manifest, records, record, workstream, selected_scopes=selected_scopes)
    reject_active_overlap(context, records, args.task_id, selected_scopes, manifest)
    output = non_authoritative_output(context.gauntlet_root, Path(args.output), args.workstream_id)
    if output.exists():
        raise AdapterError(f"refusing to overwrite existing output: {output}")
    task_packet = build_task_packet(context, manifest_path, manifest, record, workstream)
    if task_packet["limits"]["max_elapsed_minutes"] != args.max_elapsed_minutes or task_packet["limits"]["max_retries"] != args.max_retries:
        raise AdapterError("caller task limits do not exactly match canonical task authorization")
    validate_packet(validator, task_packet, evidence_root=context.project_root, label="compiled TaskPacket")
    task_packet_payload = json_bytes(task_packet)
    updated_records = copy.deepcopy(context.task_records)
    updated_record = next(
        (item for item in updated_records["records"] if item.get("task_id") == args.task_id),
        None,
    )
    if updated_record is None:
        raise AdapterError("canonical task record disappeared before compile transaction")
    updated_record["status"] = "compiled"
    updated_record["task_packet_path"] = relative_project_path(output, context.project_root, "TaskPacket output")
    updated_record["task_packet_sha256"] = sha256_bytes(task_packet_payload)
    updated_record["compiled_at"] = utcnow()
    write_file_transaction(
        {
            output: task_packet_payload,
            context.task_records_path: json_bytes(updated_records),
        },
        new_paths={output},
    )
    return {
        "valid": True,
        "operation": "compile-task",
        "task_packet": str(output),
        "run_id": manifest["run_id"],
        "task_id": args.task_id,
        "workstream_id": args.workstream_id,
        "state_mutated": True,
        "budget_mutated": False,
        "canonical_task_records": str(context.task_records_path),
    }


def validate_task_packet_against_record(
    context: GauntletContext,
    manifest: dict[str, Any],
    task_path: Path,
    task: dict[str, Any],
    records: dict[str, dict[str, Any]],
    record: dict[str, Any],
    workstream: dict[str, Any],
) -> None:
    canonical_task_path = resolve_project_reference(
        record.get("task_packet_path"),
        context.project_root,
        "canonical TaskPacket path",
    )
    if task_path.resolve() != canonical_task_path:
        raise AdapterError("supplied TaskPacket path does not match the canonical task record")
    if task.get("run_id") != manifest.get("run_id") or task.get("task_id") != record.get("task_id"):
        raise AdapterError("TaskPacket does not match canonical run and task authority")
    if task.get("run_manifest_sha256") != record.get("run_manifest_sha256"):
        raise AdapterError("TaskPacket RunManifest hash does not match canonical authority")
    if sha256_file(task_path) != record.get("task_packet_sha256"):
        raise AdapterError("TaskPacket hash does not match canonical task record")
    if task.get("plan") != plan_snapshot(context):
        raise AdapterError("TaskPacket plan is stale")
    if task.get("authorization") != record.get("authorization"):
        raise AdapterError("TaskPacket authorization does not match canonical task record")
    if task.get("task", {}).get("objective") != workstream.get("objective"):
        raise AdapterError("TaskPacket objective does not match the rechecked compiled workstream")
    selected_scopes = [normal_path(value, "TaskPacket write scope") for value in task.get("scope", {}).get("allowed_write_paths", [])]
    validate_task_record_for_workstream(context, manifest, records, record, workstream, selected_scopes=selected_scopes)
    task_output_authority(context, task)


def validate_return_against_task(context: GauntletContext, task: dict[str, Any], returned: dict[str, Any], workstream: dict[str, Any]) -> None:
    if returned.get("run_id") != task.get("run_id") or returned.get("task_id") != task.get("task_id"):
        raise AdapterError("TaskPacket and ReturnPacket must share the same run_id and task_id")
    if returned.get("task_packet_sha256") is None:
        raise AdapterError("ReturnPacket must bind the TaskPacket hash")
    if returned.get("plan") != task.get("plan") or returned.get("plan") != plan_snapshot(context):
        raise AdapterError("ReturnPacket plan is stale")
    if returned.get("scope", {}).get("allowed_write_paths") != task.get("scope", {}).get("allowed_write_paths"):
        raise AdapterError("ReturnPacket cannot widen or replace TaskPacket write authority")
    allowed = [normal_path(value, "TaskPacket write scope") for value in task["scope"]["allowed_write_paths"]]
    actual = [normal_path(value, "ReturnPacket actual write scope") for value in returned["scope"]["actual_write_paths"]]
    for path in actual:
        if not any(is_descendant(path, scope) for scope in allowed):
            raise AdapterError("ReturnPacket actual scope is outside TaskPacket authority")
    validate_artifact_authority(context, task, returned.get("artifacts"), label="ReturnPacket")
    expected_commands = task.get("evidence_commands")
    returned_commands = [item.get("command") for item in returned.get("commands", []) if isinstance(item, dict)]
    if returned_commands != expected_commands:
        raise AdapterError("ReturnPacket commands do not exactly match the authorized evidence commands")
    expected_criteria = {item["id"] for item in task["acceptance_criteria"]}
    actual_criteria = {item.get("criterion_id") for item in returned.get("criterion_to_evidence", []) if isinstance(item, dict)}
    if actual_criteria != expected_criteria or len(returned.get("criterion_to_evidence", [])) != len(actual_criteria):
        raise AdapterError("ReturnPacket criterion-to-evidence mapping does not exactly cover the authorized task criteria")
    if task["acceptance_criteria"] != criteria_for_workstream(workstream):
        raise AdapterError("TaskPacket criteria do not match the rechecked compiled workstream")


def validate_optional_review(
    review_path: Path | None,
    context: GauntletContext,
    manifest: dict[str, Any],
    task_path: Path,
    return_path: Path,
    task: dict[str, Any],
    returned: dict[str, Any],
    record: dict[str, Any],
    validator: ModuleType,
) -> None:
    if review_path is None:
        return
    review = read_json(review_path)
    validate_packet(validator, review, evidence_root=context.project_root, label="ReviewPacket")
    if review.get("run_id") != manifest.get("run_id") or review.get("task_id") != task.get("task_id"):
        raise AdapterError("ReviewPacket does not match the canonical run and task")
    if review.get("workstream_id") != record.get("workstream_id") or review.get("reviewer_id") != record["authorization"].get("reviewer_id"):
        raise AdapterError("ReviewPacket does not match the exact authorized reviewer")
    if review.get("plan") != plan_snapshot(context):
        raise AdapterError("ReviewPacket plan is stale")
    if review.get("task_packet_path") != relative_project_path(task_path, context.project_root, "TaskPacket") or review.get("task_packet_sha256") != sha256_file(task_path):
        raise AdapterError("ReviewPacket does not exactly bind the canonical TaskPacket")
    if review.get("return_packet_path") != relative_project_path(return_path, context.project_root, "ReturnPacket") or review.get("return_packet_sha256") != sha256_file(return_path):
        raise AdapterError("ReviewPacket does not exactly bind the supplied ReturnPacket")
    if review.get("artifacts_or_diffs") != returned.get("artifacts"):
        raise AdapterError("ReviewPacket artifacts do not exactly equal the supplied ReturnPacket artifacts")
    validate_artifact_authority(context, task, review.get("artifacts_or_diffs"), label="ReviewPacket")


def prepare_registration_updates(
    context: GauntletContext,
    task_path: Path,
    return_path: Path,
    record: dict[str, Any],
    returned: dict[str, Any],
) -> tuple[dict[Path, bytes], dict[str, str]]:
    required_markdown = {
        "artifact_register": context.gauntlet_root / "artifact-register.md",
        "source_register": context.gauntlet_root / "source-register.md",
        "progress": context.gauntlet_root / "progress.md",
    }
    for path in required_markdown.values():
        if not path.is_file():
            raise AdapterError(f"Gauntlet-owned registration file is missing: {path}")
    state_path = context.gauntlet_root / "state.json"
    state = read_json(state_path)
    validate_state_authority(state)
    if not isinstance(state.get("history"), list):
        raise AdapterError("canonical Gauntlet state history must be a list")
    task_relative = relative_project_path(task_path, context.project_root, "TaskPacket")
    return_relative = relative_project_path(return_path, context.project_root, "ReturnPacket")
    updated_records = copy.deepcopy(context.task_records)
    updated_record = next(
        (item for item in updated_records["records"] if item.get("task_id") == record.get("task_id")),
        None,
    )
    if updated_record is None:
        raise AdapterError("canonical task record disappeared before registration transaction")
    updated_record["status"] = returned["status"]
    updated_record["return_packet_path"] = return_relative
    updated_record["return_packet_sha256"] = sha256_file(return_path)
    updated_record["actual_write_scope"] = copy.deepcopy(returned["scope"]["actual_write_paths"])
    updated_record["artifacts"] = copy.deepcopy(returned["artifacts"])
    updated_record["evidence"] = copy.deepcopy(returned["evidence"])
    updated_record["registered_at"] = utcnow()
    markdown_updates = {path: path.read_text(encoding="utf-8").rstrip() for path in required_markdown.values()}
    for artifact in returned["artifacts"]:
        markdown_updates[required_markdown["artifact_register"]] += (
            f"\n- {record['task_id']} [{returned['status']}] artifact `{artifact['path']}` sha256 `{artifact['sha256']}`."
        )
    for evidence in returned["evidence"]:
        markdown_updates[required_markdown["source_register"]] += (
            f"\n- {record['task_id']} [{returned['status']}] evidence `{evidence['path']}` sha256 `{evidence['sha256']}`."
        )
    markdown_updates[required_markdown["progress"]] += (
        f"\n- {updated_record['task_id']} registered as `{returned['status']}` from `{return_relative}`; next action: {returned['next_action']}"
    )
    event = {
        "previous_state": state.get("state"),
        "new_state": state.get("state"),
        "timestamp": utcnow(),
        "actor": "gauntlet-sol-advisor-adapter",
        "reason": f"Registered bounded Sol Advisor return {updated_record['task_id']} with status {returned['status']}",
        "related_artifacts": [task_relative, return_relative, ".gauntlet/artifact-register.md", ".gauntlet/source-register.md", ".gauntlet/progress.md"],
        "required_next_action": returned["next_action"],
    }
    state["history"].append(event)
    state["updated_at"] = event["timestamp"]
    updates = {
        context.task_records_path: json_bytes(updated_records),
        required_markdown["artifact_register"]: (markdown_updates[required_markdown["artifact_register"]] + "\n").encode("utf-8"),
        required_markdown["source_register"]: (markdown_updates[required_markdown["source_register"]] + "\n").encode("utf-8"),
        required_markdown["progress"]: (markdown_updates[required_markdown["progress"]] + "\n").encode("utf-8"),
        state_path: json_bytes(state),
    }
    registered = {
        "runtime_task_records": str(context.task_records_path),
        "artifact_register": str(required_markdown["artifact_register"]),
        "source_register": str(required_markdown["source_register"]),
        "progress": str(required_markdown["progress"]),
        "state": str(state_path),
    }
    return updates, {key: sha256_bytes(updates[Path(value)]) for key, value in registered.items()}


def command_register_return(args: argparse.Namespace) -> dict[str, Any]:
    context = load_context(Path(args.project_root), reserve_launch=False)
    validator = protocol_validator(Path(args.protocol_root))
    manifest_path = Path(args.run_manifest).resolve()
    task_path = Path(args.task_packet).resolve()
    return_path = Path(args.return_packet).resolve()
    manifest = validate_composed_manifest(context, manifest_path, validator)
    manifest["_path"] = str(manifest_path)
    records = validate_canonical_task_records(context, manifest, validator)
    task = read_json(task_path)
    returned = read_json(return_path)
    validate_packet(validator, task, evidence_root=context.project_root, label="TaskPacket")
    validate_packet(validator, returned, evidence_root=context.project_root, label="ReturnPacket")
    record = records.get(task.get("task_id"))
    if record is None:
        raise AdapterError("TaskPacket task_id is not authorized by canonical Gauntlet task records")
    if record.get("status") not in OCCUPYING_TASK_STATUSES:
        raise AdapterError("TaskPacket is not active in canonical Gauntlet task records")
    workstream = find_workstream(context.program, record["workstream_id"])
    validate_task_packet_against_record(context, manifest, task_path, task, records, record, workstream)
    if returned.get("task_packet_sha256") != sha256_file(task_path):
        raise AdapterError("ReturnPacket TaskPacket hash does not match the supplied TaskPacket")
    validate_return_against_task(context, task, returned, workstream)
    review_argument = getattr(args, "review_packet", None)
    validate_optional_review(
        Path(review_argument).resolve() if review_argument else None,
        context,
        manifest,
        task_path,
        return_path,
        task,
        returned,
        record,
        validator,
    )
    output = non_authoritative_output(context.gauntlet_root, Path(args.output), record["workstream_id"])
    if output.exists():
        raise AdapterError(f"refusing to overwrite existing output: {output}")
    registration_updates, registered_hashes = prepare_registration_updates(context, task_path, return_path, record, returned)
    receipt = {
        "record_type": "SolAdvisorReturnRegistration",
        "protocol_version": 1,
        "run_id": manifest["run_id"],
        "task_id": task["task_id"],
        "workstream_id": record["workstream_id"],
        "plan": returned["plan"],
        "return_packet_sha256": sha256_file(return_path),
        "verified_evidence_count": len(returned["evidence"]),
        "registered_artifact_count": len(returned["artifacts"]),
        "registered_state_files": registered_hashes,
        "gauntlet_ownership": {surface: "gauntlet" for surface in GAUNTLET_OWNED_SURFACES},
        "state_mutated": True,
        "budget_mutated": False,
    }
    registration_updates[output] = json_bytes(receipt)
    write_file_transaction(registration_updates, new_paths={output})
    return {
        "valid": True,
        "operation": "register-return",
        "registration_receipt": str(output),
        "run_id": manifest["run_id"],
        "task_id": task["task_id"],
        "workstream_id": record["workstream_id"],
        "state_mutated": True,
        "budget_mutated": False,
        "registered_state_files": registered_hashes,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--protocol-root",
        type=Path,
        required=True,
        help="Explicit public Agent Ops root containing the canonical packet validator",
    )
    commands = parser.add_subparsers(dest="command", required=True)

    compile_task = commands.add_parser("compile-task")
    compile_task.add_argument("--project-root", required=True, type=Path)
    compile_task.add_argument("--run-manifest", required=True, type=Path)
    compile_task.add_argument("--workstream-id", required=True)
    compile_task.add_argument("--task-id", required=True)
    compile_task.add_argument("--classification", required=True, choices=["routine", "complex"])
    compile_task.add_argument("--write-target", action="append", default=[])
    compile_task.add_argument("--max-retries", type=int, default=0)
    compile_task.add_argument("--max-elapsed-minutes", type=int, default=60)
    compile_task.add_argument("--output", required=True, type=Path)
    compile_task.set_defaults(handler=command_compile_task)

    register_return = commands.add_parser("register-return")
    register_return.add_argument("--project-root", required=True, type=Path)
    register_return.add_argument("--run-manifest", required=True, type=Path)
    register_return.add_argument("--task-packet", required=True, type=Path)
    register_return.add_argument("--return-packet", required=True, type=Path)
    register_return.add_argument("--review-packet", type=Path)
    register_return.add_argument("--output", required=True, type=Path)
    register_return.set_defaults(handler=command_register_return)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        result = args.handler(args)
    except AdapterError as exc:
        print(json.dumps({"valid": False, "operation": args.command, "errors": [str(exc)]}, indent=2))
        return 1
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
