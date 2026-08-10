#!/usr/bin/env python3
"""Validate fail-closed Sol Advisor packets and their inspectable evidence."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any


PROTOCOL_VERSION = 1
SHA256 = re.compile(r"^[0-9a-f]{64}$")
AUTHORITY_SURFACES = (
    "state",
    "budget",
    "approval",
    "integration",
    "final_answer",
    "terminal_verdict",
)
EXPECTED_EDGES = {
    ("parent", "routine_worker"),
    ("parent", "complex_worker"),
    ("routine_worker", "reviewer"),
    ("complex_worker", "reviewer"),
}
RUNTIME_REQUIREMENTS = {
    "gpt-5.6-sol": ["high", "xhigh"],
    "gpt-5.6-luna": ["max"],
    "gpt-5.6-terra": ["max"],
}
PROHIBITED_ACTIONS = {
    "approve_work",
    "issue_final_answer",
    "issue_terminal_verdict",
    "mutate_gauntlet_budget",
    "mutate_gauntlet_state",
    "reviewer_repairs",
    "spawn_workers",
}
RETURN_STATUSES = {"succeeded", "blocked", "failed", "escalate"}
REVIEW_VERDICTS = {"accepted", "revise", "blocked", "unable_to_verify"}
CRITERION_RESULTS = {"met", "blocked", "failed", "escalate"}
FINDING_SEVERITIES = {"blocking", "major", "minor", "info"}
DEFAULT_MAX_TASK_LAUNCHES = 6
ABSOLUTE_MAX_TASK_LAUNCHES = 24
DEFAULT_MAX_CONCURRENCY = 4
ABSOLUTE_MAX_CONCURRENCY = 8


def add(errors: list[str], message: str) -> None:
    errors.append(message)


def require_object(value: Any, label: str, errors: list[str]) -> dict[str, Any]:
    if not isinstance(value, dict):
        add(errors, f"{label} must be an object")
        return {}
    return value


def require_keys(value: dict[str, Any], required: set[str], label: str, errors: list[str]) -> None:
    missing = sorted(required - set(value))
    extra = sorted(set(value) - required)
    if missing:
        add(errors, f"{label} missing keys: {missing}")
    if extra:
        add(errors, f"{label} has unsupported keys: {extra}")


def require_string(value: Any, label: str, errors: list[str]) -> None:
    if not isinstance(value, str) or not value.strip():
        add(errors, f"{label} must be a non-empty string")


def require_string_list(value: Any, label: str, errors: list[str], *, allow_empty: bool = False) -> list[str]:
    if not isinstance(value, list) or (not value and not allow_empty):
        add(errors, f"{label} must be a{' non-empty' if not allow_empty else ''} list of strings")
        return []
    if any(not isinstance(item, str) or not item.strip() for item in value):
        add(errors, f"{label} must be a list of non-empty strings")
        return []
    if len(value) != len(set(value)):
        add(errors, f"{label} must not contain duplicates")
    return value


def require_sha256(value: Any, label: str, errors: list[str]) -> None:
    if not isinstance(value, str) or not SHA256.fullmatch(value):
        add(errors, f"{label} must be a lowercase SHA-256")


def require_bool(value: Any, expected: bool, label: str, errors: list[str]) -> None:
    if value is not expected:
        add(errors, f"{label} must be {str(expected).lower()}")


def require_positive_int(value: Any, label: str, errors: list[str], *, minimum: int = 1) -> None:
    if not isinstance(value, int) or isinstance(value, bool) or value < minimum:
        add(errors, f"{label} must be a positive finite integer" if minimum == 1 else f"{label} must be an integer >= {minimum}")


def require_nonnegative_int(value: Any, label: str, errors: list[str]) -> None:
    if not isinstance(value, int) or isinstance(value, bool) or value < 0:
        add(errors, f"{label} must be a non-negative integer")


def require_iso_timestamp(value: Any, label: str, errors: list[str]) -> None:
    if not isinstance(value, str) or not value.strip():
        add(errors, f"{label} must be an ISO-8601 timestamp")
        return
    try:
        datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        add(errors, f"{label} must be an ISO-8601 timestamp")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def is_descendant(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
    except ValueError:
        return False
    return True


def normalized_scope_path(value: Any, label: str, errors: list[str]) -> Path | None:
    if not isinstance(value, str) or not value.strip():
        add(errors, f"{label} must be a non-empty path")
        return None
    raw = Path(value)
    if ".." in raw.parts:
        add(errors, f"{label} must not contain parent traversal")
        return None
    normalized = raw.resolve()
    if normalized == Path("/"):
        add(errors, f"{label} must not be the filesystem root")
        return None
    if len(normalized.parts) < 3:
        add(errors, f"{label} is too broad")
        return None
    return normalized


def paths_overlap(left: Path, right: Path) -> bool:
    return is_descendant(left, right) or is_descendant(right, left)


def validate_scope_paths(
    values: Any,
    label: str,
    errors: list[str],
    *,
    allow_empty: bool = False,
) -> list[Path]:
    if not isinstance(values, list) or (not values and not allow_empty):
        add(errors, f"{label} must be a non-empty list")
        return []
    paths: list[Path] = []
    for index, value in enumerate(values):
        path = normalized_scope_path(value, f"{label}[{index}]", errors)
        if path is not None:
            paths.append(path)
    for index, left in enumerate(paths):
        for right in paths[index + 1 :]:
            if paths_overlap(left, right):
                add(errors, f"{label} contains overlapping paths")
                return paths
    return paths


def resolve_file(
    path_value: Any,
    root: Path | None,
    label: str,
    errors: list[str],
    *,
    require_root: bool,
) -> Path | None:
    if not isinstance(path_value, str) or not path_value.strip():
        add(errors, f"{label}.path must be a non-empty relative path")
        return None
    candidate_input = Path(path_value)
    if candidate_input.is_absolute() or ".." in candidate_input.parts:
        add(errors, f"{label}.path must stay under the verification root")
        return None
    if root is None:
        if require_root:
            add(errors, f"{label} requires --root for evidence verification")
        return None
    resolved_root = root.resolve()
    candidate = (resolved_root / candidate_input).resolve()
    if not is_descendant(candidate, resolved_root) or not candidate.is_file():
        add(errors, f"{label}.path must resolve to an existing file beneath --root")
        return None
    return candidate


def resolve_root_relative_path(
    path_value: Any,
    root: Path | None,
    label: str,
    errors: list[str],
    *,
    require_root: bool,
) -> Path | None:
    if not isinstance(path_value, str) or not path_value.strip():
        add(errors, f"{label}.path must be a non-empty relative path")
        return None
    candidate_input = Path(path_value)
    if candidate_input.is_absolute() or ".." in candidate_input.parts:
        add(errors, f"{label}.path must stay under the verification root")
        return None
    if root is None:
        if require_root:
            add(errors, f"{label} requires --root for path authority verification")
        return None
    resolved_root = root.resolve()
    candidate = (resolved_root / candidate_input).resolve()
    if not is_descendant(candidate, resolved_root):
        add(errors, f"{label}.path must resolve beneath --root")
        return None
    return candidate


def validate_file_records(
    value: Any,
    label: str,
    errors: list[str],
    root: Path | None,
    *,
    require_kind: bool,
    require_root: bool,
    allow_empty: bool = False,
) -> dict[str, str]:
    if not isinstance(value, list) or (not value and not allow_empty):
        add(errors, f"{label} must be a non-empty list")
        return {}
    result: dict[str, str] = {}
    required = {"path", "sha256", "kind"} if require_kind else {"path", "sha256"}
    for index, item in enumerate(value):
        item_label = f"{label}[{index}]"
        record = require_object(item, item_label, errors)
        require_keys(record, required, item_label, errors)
        if require_kind:
            require_string(record.get("kind"), f"{item_label}.kind", errors)
        require_sha256(record.get("sha256"), f"{item_label}.sha256", errors)
        path = resolve_file(record.get("path"), root, item_label, errors, require_root=require_root)
        if path is not None and isinstance(record.get("sha256"), str):
            if sha256_file(path) != record["sha256"]:
                add(errors, f"{item_label}.sha256 does not match {record['path']}")
        path_value = record.get("path")
        if isinstance(path_value, str) and isinstance(record.get("sha256"), str):
            if path_value in result:
                add(errors, f"{label} must not repeat evidence paths")
            result[path_value] = record["sha256"]
    return result


def validate_artifact_records(
    value: Any,
    label: str,
    errors: list[str],
    root: Path | None,
    allowed_write_paths: list[Path],
    *,
    expected_paths: list[str] | None = None,
) -> list[str]:
    validate_file_records(value, label, errors, root, require_kind=True, require_root=True)
    if not isinstance(value, list):
        return []
    artifact_paths: list[str] = []
    for index, item in enumerate(value):
        item_label = f"{label}[{index}]"
        record = require_object(item, item_label, errors)
        path_value = record.get("path")
        if isinstance(path_value, str):
            artifact_paths.append(path_value)
        resolved = resolve_root_relative_path(path_value, root, item_label, errors, require_root=True)
        if resolved is not None and not any(is_descendant(resolved, allowed) for allowed in allowed_write_paths):
            add(errors, f"{item_label}.path must stay within TaskPacket allowed_write_paths")
    if expected_paths is not None and artifact_paths != expected_paths:
        add(errors, f"{label} must exactly match the TaskPacket expected output paths")
    return artifact_paths


def load_verified_json(path: Path, label: str, errors: list[str]) -> dict[str, Any] | None:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        add(errors, f"{label}.path must contain JSON evidence: {exc}")
        return None
    return require_object(data, f"{label}.path JSON", errors)


def validate_plan(value: Any, label: str, errors: list[str], root: Path | None) -> dict[str, Any]:
    plan = require_object(value, label, errors)
    require_keys(plan, {"status", "version", "path", "sha256"}, label, errors)
    if plan.get("status") != "approved":
        add(errors, f"{label}.status must be approved")
    require_positive_int(plan.get("version"), f"{label}.version", errors)
    require_string(plan.get("path"), f"{label}.path", errors)
    require_sha256(plan.get("sha256"), f"{label}.sha256", errors)
    plan_path = resolve_file(plan.get("path"), root, label, errors, require_root=True)
    if plan_path is not None and isinstance(plan.get("sha256"), str):
        if sha256_file(plan_path) != plan["sha256"]:
            add(errors, f"{label}.sha256 does not match the referenced approved plan")
    return plan


def validate_criteria(value: Any, label: str, errors: list[str]) -> list[dict[str, str]]:
    if not isinstance(value, list) or not value:
        add(errors, f"{label} must be a non-empty list")
        return []
    result: list[dict[str, str]] = []
    seen: set[str] = set()
    for index, item in enumerate(value):
        item_label = f"{label}[{index}]"
        criterion = require_object(item, item_label, errors)
        require_keys(criterion, {"id", "description"}, item_label, errors)
        require_string(criterion.get("id"), f"{item_label}.id", errors)
        require_string(criterion.get("description"), f"{item_label}.description", errors)
        criterion_id = criterion.get("id")
        if isinstance(criterion_id, str):
            if criterion_id in seen:
                add(errors, f"{label} criterion ids must be unique")
            seen.add(criterion_id)
        if isinstance(criterion.get("id"), str) and isinstance(criterion.get("description"), str):
            result.append({"id": criterion["id"], "description": criterion["description"]})
    return result


def validate_context_policy(value: Any, errors: list[str]) -> None:
    policy = require_object(value, "context_policy", errors)
    require_keys(
        policy,
        {
            "checkpoint_tokens",
            "checkpoint_type",
            "semantic_checkpoint",
            "numeric_occupancy_tokens",
            "configuration_change_allowed",
        },
        "context_policy",
        errors,
    )
    if policy.get("checkpoint_tokens") != 150000:
        add(errors, "context_policy.checkpoint_tokens must be exactly 150000")
    if policy.get("checkpoint_type") != "observation_checkpoint":
        add(errors, "context_policy.checkpoint_type must be observation_checkpoint")
    semantic = policy.get("semantic_checkpoint")
    if semantic not in {"below_checkpoint", "observed_above_without_crossing", "telemetry-unavailable"}:
        add(errors, "context_policy.semantic_checkpoint is invalid")
    numeric = policy.get("numeric_occupancy_tokens")
    if semantic == "telemetry-unavailable" and numeric is not None:
        add(errors, "telemetry-unavailable requires null numeric occupancy")
    if semantic == "below_checkpoint" and (
        not isinstance(numeric, int) or isinstance(numeric, bool) or numeric < 0
    ):
        add(errors, "below_checkpoint requires a non-negative numeric occupancy")
    elif semantic == "below_checkpoint" and numeric >= 150000:
        add(errors, "below_checkpoint numeric occupancy must be below 150000")
    if semantic == "observed_above_without_crossing" and numeric is not None and (
        not isinstance(numeric, int) or isinstance(numeric, bool) or numeric < 0
    ):
        add(errors, "observed_above_without_crossing numeric occupancy must be null or non-negative")
    elif semantic == "observed_above_without_crossing" and numeric is not None and numeric < 150000:
        add(errors, "observed_above_without_crossing numeric occupancy must be at least 150000")
    require_bool(policy.get("configuration_change_allowed"), False, "context_policy.configuration_change_allowed", errors)


def validate_runtime_requirements(value: Any, errors: list[str]) -> None:
    requirements = require_object(value, "runtime_requirements", errors)
    require_keys(requirements, {"fallback_allowed", "required_model_efforts"}, "runtime_requirements", errors)
    require_bool(requirements.get("fallback_allowed"), False, "runtime_requirements.fallback_allowed", errors)
    support = require_object(requirements.get("required_model_efforts"), "runtime_requirements.required_model_efforts", errors)
    if set(support) != set(RUNTIME_REQUIREMENTS):
        add(errors, "runtime_requirements.required_model_efforts must name the exact GPT-5.6 Sol, Luna, and Terra model IDs")
    for model, efforts in RUNTIME_REQUIREMENTS.items():
        if support.get(model) != efforts:
            add(errors, f"runtime_requirements.required_model_efforts.{model} must be {efforts}")


def validate_role(value: Any, label: str, expected: dict[str, Any], errors: list[str]) -> None:
    role = require_object(value, label, errors)
    require_keys(role, set(expected), label, errors)
    for key, expected_value in expected.items():
        if role.get(key) != expected_value:
            add(errors, f"{label}.{key} must be {expected_value!r}")


def validate_topology(value: Any, errors: list[str]) -> None:
    topology = require_object(value, "topology", errors)
    require_keys(topology, {"parent", "routine_worker", "complex_worker", "reviewer", "edges"}, "topology", errors)
    validate_role(
        topology.get("parent"),
        "topology.parent",
        {"role": "parent", "model": "gpt-5.6-sol", "reasoning_effort": "high", "may_dispatch_tasks": True},
        errors,
    )
    worker_base = {
        "role": "worker",
        "reasoning_effort": "max",
        "fresh_task": True,
        "creation_method": "create_thread",
        "forked": False,
        "may_spawn_workers": False,
    }
    validate_role(topology.get("routine_worker"), "topology.routine_worker", {**worker_base, "model": "gpt-5.6-luna"}, errors)
    validate_role(topology.get("complex_worker"), "topology.complex_worker", {**worker_base, "model": "gpt-5.6-terra"}, errors)
    validate_role(
        topology.get("reviewer"),
        "topology.reviewer",
        {
            "role": "workstream_critic",
            "model": "gpt-5.6-sol",
            "reasoning_effort": "xhigh",
            "fresh_task": True,
            "creation_method": "create_thread",
            "forked": False,
            "may_build": False,
            "may_repair": False,
            "may_write": False,
            "may_approve": False,
            "may_integrate": False,
            "may_update_state": False,
            "may_update_budget": False,
            "may_issue_final_verdict": False,
        },
        errors,
    )
    edges = topology.get("edges")
    if not isinstance(edges, list):
        add(errors, "topology.edges must be a list")
        return
    normalized_edges = {tuple(edge) for edge in edges if isinstance(edge, list) and len(edge) == 2}
    if len(normalized_edges) != len(edges) or normalized_edges != EXPECTED_EDGES:
        add(errors, "topology.edges must be the fixed acyclic Sol Advisor edges")


def validate_parent_runtime_attestation(value: Any, run_id: Any, errors: list[str], root: Path | None) -> None:
    attestation = require_object(value, "RunManifest.parent_runtime_attestation", errors)
    require_keys(
        attestation,
        {
            "run_id",
            "parent_id",
            "role",
            "model",
            "reasoning_effort",
            "target",
            "effective_model",
            "effective_model_source",
            "host_metadata",
            "unavailable_reason",
            "observed_at",
        },
        "RunManifest.parent_runtime_attestation",
        errors,
    )
    if attestation.get("run_id") != run_id:
        add(errors, "RunManifest.parent_runtime_attestation.run_id must match RunManifest.run_id")
    require_string(attestation.get("parent_id"), "RunManifest.parent_runtime_attestation.parent_id", errors)
    for field, expected in {"role": "parent", "model": "gpt-5.6-sol", "reasoning_effort": "high", "target": "parent_task"}.items():
        if attestation.get(field) != expected:
            add(errors, f"RunManifest.parent_runtime_attestation.{field} must be {expected!r}")
    source = attestation.get("effective_model_source")
    if source not in {"host_metadata", "explicitly_unavailable"}:
        add(errors, "RunManifest.parent_runtime_attestation.effective_model_source must be host_metadata or explicitly_unavailable")
    require_iso_timestamp(attestation.get("observed_at"), "RunManifest.parent_runtime_attestation.observed_at", errors)
    if source == "host_metadata":
        if attestation.get("effective_model") != "gpt-5.6-sol":
            add(errors, "RunManifest.parent_runtime_attestation.effective_model must be gpt-5.6-sol when host metadata is available")
        if attestation.get("unavailable_reason") is not None:
            add(errors, "RunManifest.parent_runtime_attestation.unavailable_reason must be null when host metadata is available")
        metadata = require_object(attestation.get("host_metadata"), "RunManifest.parent_runtime_attestation.host_metadata", errors)
        require_keys(metadata, {"path", "sha256", "thread_id", "host_id", "observed_at"}, "RunManifest.parent_runtime_attestation.host_metadata", errors)
        require_sha256(metadata.get("sha256"), "RunManifest.parent_runtime_attestation.host_metadata.sha256", errors)
        require_string(metadata.get("thread_id"), "RunManifest.parent_runtime_attestation.host_metadata.thread_id", errors)
        require_string(metadata.get("host_id"), "RunManifest.parent_runtime_attestation.host_metadata.host_id", errors)
        require_iso_timestamp(metadata.get("observed_at"), "RunManifest.parent_runtime_attestation.host_metadata.observed_at", errors)
        path = resolve_file(metadata.get("path"), root, "RunManifest.parent_runtime_attestation.host_metadata", errors, require_root=False)
        if path is not None and isinstance(metadata.get("sha256"), str):
            if sha256_file(path) != metadata["sha256"]:
                add(errors, "RunManifest.parent_runtime_attestation.host_metadata.sha256 does not match host metadata")
            data = load_verified_json(path, "RunManifest.parent_runtime_attestation.host_metadata", errors)
            if data is not None:
                expected = {
                    "run_id": run_id,
                    "parent_id": attestation.get("parent_id"),
                    "effective_model": "gpt-5.6-sol",
                    "threadId": metadata.get("thread_id"),
                    "hostId": metadata.get("host_id"),
                    "observed_at": metadata.get("observed_at"),
                }
                for key, expected_value in expected.items():
                    if data.get(key) != expected_value:
                        add(errors, f"RunManifest.parent_runtime_attestation.host_metadata evidence {key} does not bind the parent runtime")
    elif source == "explicitly_unavailable":
        if attestation.get("effective_model") is not None:
            add(errors, "RunManifest.parent_runtime_attestation.effective_model must be null when unavailable")
        if attestation.get("host_metadata") is not None:
            add(errors, "RunManifest.parent_runtime_attestation.host_metadata must be null when unavailable")
        require_string(attestation.get("unavailable_reason"), "RunManifest.parent_runtime_attestation.unavailable_reason", errors)


def validate_creation_attestation(
    value: Any,
    label: str,
    errors: list[str],
    root: Path | None,
    *,
    run_id: Any,
    task_id: Any,
    reviewer_id: Any,
    role: str,
    model: str,
    effort: str,
    target: str,
) -> None:
    attestation = require_object(value, label, errors)
    require_keys(
        attestation,
        {
            "run_id",
            "task_id",
            "reviewer_id",
            "role",
            "model",
            "reasoning_effort",
            "target",
            "fresh_task",
            "creation_method",
            "forked",
            "creation_request",
            "creation_response",
        },
        label,
        errors,
    )
    expected = {
        "run_id": run_id,
        "task_id": task_id,
        "reviewer_id": reviewer_id,
        "role": role,
        "model": model,
        "reasoning_effort": effort,
        "target": target,
        "fresh_task": True,
        "creation_method": "create_thread",
        "forked": False,
    }
    for field, expected_value in expected.items():
        if attestation.get(field) != expected_value:
            add(errors, f"{label}.{field} must be {expected_value!r}")

    request = require_object(attestation.get("creation_request"), f"{label}.creation_request", errors)
    require_keys(request, {"request_id", "path", "sha256", "created_at"}, f"{label}.creation_request", errors)
    require_string(request.get("request_id"), f"{label}.creation_request.request_id", errors)
    require_sha256(request.get("sha256"), f"{label}.creation_request.sha256", errors)
    require_iso_timestamp(request.get("created_at"), f"{label}.creation_request.created_at", errors)

    response = require_object(attestation.get("creation_response"), f"{label}.creation_response", errors)
    require_keys(
        response,
        {"request_id", "path", "sha256", "thread_id", "host_id", "successful", "responded_at"},
        f"{label}.creation_response",
        errors,
    )
    if response.get("request_id") != request.get("request_id"):
        add(errors, f"{label}.creation_response.request_id must match creation_request.request_id")
    require_sha256(response.get("sha256"), f"{label}.creation_response.sha256", errors)
    require_string(response.get("thread_id"), f"{label}.creation_response.thread_id", errors)
    require_string(response.get("host_id"), f"{label}.creation_response.host_id", errors)
    require_bool(response.get("successful"), True, f"{label}.creation_response.successful", errors)
    require_iso_timestamp(response.get("responded_at"), f"{label}.creation_response.responded_at", errors)

    request_path = resolve_file(request.get("path"), root, f"{label}.creation_request", errors, require_root=False)
    response_path = resolve_file(response.get("path"), root, f"{label}.creation_response", errors, require_root=False)
    if request_path is not None and isinstance(request.get("sha256"), str):
        if sha256_file(request_path) != request["sha256"]:
            add(errors, f"{label}.creation_request.sha256 does not match creation request evidence")
        request_data = load_verified_json(request_path, f"{label}.creation_request", errors)
        if request_data is not None:
            expected_request = {
                "request_id": request.get("request_id"),
                "run_id": run_id,
                "task_id": task_id,
                "reviewer_id": reviewer_id,
                "role": role,
                "tool": "codex_app__create_thread",
                "model": model,
                "thinking": effort,
                "fresh_task": True,
                "creation_method": "create_thread",
                "forked": False,
                "created_at": request.get("created_at"),
            }
            for key, expected_value in expected_request.items():
                if request_data.get(key) != expected_value:
                    add(errors, f"{label}.creation_request evidence {key} does not bind the runtime")
            request_target = request_data.get("target")
            if not isinstance(request_target, dict) or not request_target:
                add(errors, f"{label}.creation_request evidence target must be the structured create_thread target")
    if response_path is not None and isinstance(response.get("sha256"), str):
        if sha256_file(response_path) != response["sha256"]:
            add(errors, f"{label}.creation_response.sha256 does not match creation response evidence")
        response_data = load_verified_json(response_path, f"{label}.creation_response", errors)
        if response_data is not None:
            expected_response = {
                "request_id": request.get("request_id"),
                "run_id": run_id,
                "task_id": task_id,
                "reviewer_id": reviewer_id,
                "role": role,
                "tool": "codex_app__create_thread",
                "model": model,
                "thinking": effort,
                "fresh_task": True,
                "creation_method": "create_thread",
                "forked": False,
                "threadId": response.get("thread_id"),
                "hostId": response.get("host_id"),
                "successful": True,
                "responded_at": response.get("responded_at"),
            }
            for key, expected_value in expected_response.items():
                if response_data.get(key) != expected_value:
                    add(errors, f"{label}.creation_response evidence {key} does not bind the runtime")
            response_target = response_data.get("target")
            request_target = request_data.get("target") if request_path is not None and 'request_data' in locals() else None
            if not isinstance(response_target, dict) or not response_target or response_target != request_target:
                add(errors, f"{label}.creation_response evidence target must exactly match the structured creation request target")


def validate_expected_output(
    value: Any,
    label: str,
    errors: list[str],
    root: Path | None,
    allowed_write_paths: list[Path],
) -> list[str]:
    output = require_object(value, label, errors)
    require_keys(output, {"description", "paths"}, label, errors)
    require_string(output.get("description"), f"{label}.description", errors)
    paths = require_string_list(output.get("paths"), f"{label}.paths", errors)
    for index, path in enumerate(paths):
        candidate = resolve_root_relative_path(path, root, f"{label}.paths[{index}]", errors, require_root=True)
        if candidate is not None and not any(is_descendant(candidate, allowed) for allowed in allowed_write_paths):
            add(errors, f"{label}.paths[{index}] must stay within allowed_write_paths")
    return paths


def validate_task_limits(value: Any, label: str, errors: list[str]) -> None:
    limits = require_object(value, label, errors)
    require_keys(limits, {"max_attempts", "max_retries", "max_repair_rounds", "max_elapsed_minutes"}, label, errors)
    attempts = limits.get("max_attempts")
    retries = limits.get("max_retries")
    repairs = limits.get("max_repair_rounds")
    elapsed = limits.get("max_elapsed_minutes")
    if not isinstance(attempts, int) or isinstance(attempts, bool) or not 1 <= attempts <= 2:
        add(errors, f"{label}.max_attempts must be a finite integer from 1 to 2")
    if not isinstance(retries, int) or isinstance(retries, bool) or not 0 <= retries <= 1:
        add(errors, f"{label}.max_retries must be a finite integer from 0 to 1")
    elif isinstance(attempts, int) and attempts != retries + 1:
        add(errors, f"{label}.max_attempts must equal max_retries plus one")
    require_positive_int(repairs, f"{label}.max_repair_rounds", errors)
    require_positive_int(elapsed, f"{label}.max_elapsed_minutes", errors)


def validate_task_authorization(
    value: Any,
    label: str,
    errors: list[str],
    root: Path | None = None,
) -> dict[str, Any]:
    authorization = require_object(value, label, errors)
    required = {
        "task_id",
        "workstream_id",
        "classification",
        "role",
        "model",
        "reasoning_effort",
        "dependencies",
        "work_type",
        "expected_observable_delta",
        "unresolved_before",
        "support_artifact_limit",
        "immediate_decision",
        "allowed_write_paths",
        "input_paths",
        "expected_output",
        "acceptance_criteria",
        "tools",
        "evidence_commands",
        "stop_conditions",
        "limits",
        "reviewer_id",
        "target",
    }
    require_keys(authorization, required, label, errors)
    require_string(authorization.get("task_id"), f"{label}.task_id", errors)
    require_string(authorization.get("workstream_id"), f"{label}.workstream_id", errors)
    classification = authorization.get("classification")
    if classification not in {"routine", "complex"}:
        add(errors, f"{label}.classification must be routine or complex")
    expected_model = "gpt-5.6-luna" if classification == "routine" else "gpt-5.6-terra"
    if authorization.get("role") != "worker":
        add(errors, f"{label}.role must be worker")
    if authorization.get("model") != expected_model:
        add(errors, f"{label}.model must be {expected_model!r}")
    if authorization.get("reasoning_effort") != "max":
        add(errors, f"{label}.reasoning_effort must be 'max'")
    dependencies = require_string_list(authorization.get("dependencies"), f"{label}.dependencies", errors, allow_empty=True)
    if authorization.get("task_id") in dependencies:
        add(errors, f"{label}.dependencies must not contain its own task ID")
    work_type = authorization.get("work_type")
    if work_type not in {"implementation", "read_only"}:
        add(errors, f"{label}.work_type must be implementation or read_only")
    expected_delta = authorization.get("expected_observable_delta")
    if not isinstance(expected_delta, str):
        add(errors, f"{label}.expected_observable_delta must be a string")
    elif work_type == "implementation" and not expected_delta.strip():
        add(errors, f"{label}.expected_observable_delta must name the target-state change")
    require_nonnegative_int(authorization.get("unresolved_before"), f"{label}.unresolved_before", errors)
    support_limit = authorization.get("support_artifact_limit")
    require_nonnegative_int(support_limit, f"{label}.support_artifact_limit", errors)
    if isinstance(support_limit, int) and not isinstance(support_limit, bool) and support_limit > 2:
        add(errors, f"{label}.support_artifact_limit must not exceed 2")
    immediate_decision = authorization.get("immediate_decision")
    if work_type == "read_only":
        require_string(immediate_decision, f"{label}.immediate_decision", errors)
    elif immediate_decision is not None:
        add(errors, f"{label}.immediate_decision must be null for implementation work")
    allowed_write_paths = validate_scope_paths(authorization.get("allowed_write_paths"), f"{label}.allowed_write_paths", errors)
    validate_file_records(
        authorization.get("input_paths"),
        f"{label}.input_paths",
        errors,
        root,
        require_kind=False,
        require_root=False,
    )
    validate_expected_output(
        authorization.get("expected_output"),
        f"{label}.expected_output",
        errors,
        root,
        allowed_write_paths,
    )
    validate_criteria(authorization.get("acceptance_criteria"), f"{label}.acceptance_criteria", errors)
    require_string_list(authorization.get("tools"), f"{label}.tools", errors)
    require_string_list(authorization.get("evidence_commands"), f"{label}.evidence_commands", errors, allow_empty=True)
    require_string_list(authorization.get("stop_conditions"), f"{label}.stop_conditions", errors)
    validate_task_limits(authorization.get("limits"), f"{label}.limits", errors)
    require_string(authorization.get("reviewer_id"), f"{label}.reviewer_id", errors)
    if authorization.get("target") != "codex_task":
        add(errors, f"{label}.target must be 'codex_task'")
    return authorization


def validate_task_dag_and_authorization(
    data: dict[str, Any],
    criteria: list[dict[str, str]],
    errors: list[str],
    root: Path | None,
) -> None:
    raw_authorizations = data.get("task_authorization")
    if not isinstance(raw_authorizations, list) or not raw_authorizations:
        add(errors, "RunManifest.task_authorization must be a non-empty list")
        raw_authorizations = []
    authorizations: dict[str, dict[str, Any]] = {}
    root_criteria = {item["id"]: item["description"] for item in criteria}
    assigned_criteria: set[str] = set()
    all_scopes: list[tuple[str, Path]] = []
    for index, item in enumerate(raw_authorizations):
        authorization = validate_task_authorization(
            item,
            f"RunManifest.task_authorization[{index}]",
            errors,
            root,
        )
        task_id = authorization.get("task_id")
        if isinstance(task_id, str):
            if task_id in authorizations:
                add(errors, "RunManifest.task_authorization task ids must be unique")
            authorizations[task_id] = authorization
        reviewer_id = authorization.get("reviewer_id")
        if isinstance(reviewer_id, str):
            if reviewer_id == task_id:
                add(errors, "RunManifest task reviewer_id must not equal its builder task_id")
        for criterion in authorization.get("acceptance_criteria", []):
            if isinstance(criterion, dict) and root_criteria.get(criterion.get("id")) != criterion.get("description"):
                add(errors, "RunManifest.task_authorization criteria must be exact approved RunManifest criteria")
            elif isinstance(criterion, dict) and isinstance(criterion.get("id"), str):
                assigned_criteria.add(criterion["id"])
        scopes = validate_scope_paths(
            authorization.get("allowed_write_paths"),
            f"RunManifest.task_authorization[{index}].allowed_write_paths",
            errors,
        )
        all_scopes.extend((str(task_id), scope) for scope in scopes)
    if assigned_criteria != set(root_criteria):
        add(errors, "RunManifest every approved criterion must be assigned to at least one task authorization")

    raw_dag = data.get("task_dag")
    if not isinstance(raw_dag, list) or not raw_dag:
        add(errors, "RunManifest.task_dag must be a non-empty list")
        raw_dag = []
    dependencies: dict[str, list[str]] = {}
    for index, item in enumerate(raw_dag):
        label = f"RunManifest.task_dag[{index}]"
        node = require_object(item, label, errors)
        require_keys(node, {"task_id", "dependencies"}, label, errors)
        require_string(node.get("task_id"), f"{label}.task_id", errors)
        values = require_string_list(node.get("dependencies"), f"{label}.dependencies", errors, allow_empty=True)
        task_id = node.get("task_id")
        if task_id in dependencies:
            add(errors, "RunManifest.task_dag task ids must be unique")
        if isinstance(task_id, str):
            dependencies[task_id] = values
            authorization = authorizations.get(task_id)
            if authorization is None:
                add(errors, f"RunManifest.task_dag task_id is not authorized: {task_id}")
            elif values != authorization.get("dependencies"):
                add(errors, f"RunManifest.task_dag dependencies must exactly match task authorization for {task_id}")
    if set(dependencies) != set(authorizations):
        add(errors, "RunManifest.task_dag and task_authorization must name the same task ids")
    for task_id, values in dependencies.items():
        if task_id in values:
            add(errors, f"RunManifest.task_dag {task_id} must not depend on itself")
        for dependency in values:
            if dependency not in dependencies:
                add(errors, f"RunManifest.task_dag {task_id} has an unauthorized dependency: {dependency}")

    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(task_id: str) -> None:
        if task_id in visiting:
            add(errors, f"RunManifest.task_dag contains a cycle at {task_id}")
            return
        if task_id in visited:
            return
        visiting.add(task_id)
        for dependency in dependencies.get(task_id, []):
            visit(dependency)
        visiting.remove(task_id)
        visited.add(task_id)

    for task_id in dependencies:
        visit(task_id)

    policy = require_object(data.get("write_policy"), "RunManifest.write_policy", errors)
    require_keys(
        policy,
        {"mode", "active_scope_source", "require_disjoint_active_scopes", "allow_unlisted_writes", "allowed_write_roots"},
        "RunManifest.write_policy",
        errors,
    )
    if policy.get("mode") not in {"disjoint_targets", "separate_worktrees", "serialized"}:
        add(errors, "RunManifest.write_policy.mode is invalid")
    if policy.get("active_scope_source") != "canonical_gauntlet_task_records":
        add(errors, "RunManifest.write_policy.active_scope_source must be canonical_gauntlet_task_records")
    require_bool(
        policy.get("require_disjoint_active_scopes"),
        True,
        "RunManifest.write_policy.require_disjoint_active_scopes",
        errors,
    )
    require_bool(policy.get("allow_unlisted_writes"), False, "RunManifest.write_policy.allow_unlisted_writes", errors)
    roots = validate_scope_paths(policy.get("allowed_write_roots"), "RunManifest.write_policy.allowed_write_roots", errors)
    for _, scope in all_scopes:
        if not any(is_descendant(scope, root) for root in roots):
            add(errors, "RunManifest task authorization write scope must stay within write_policy.allowed_write_roots")
    if policy.get("mode") == "disjoint_targets":
        for index, (owner, left) in enumerate(all_scopes):
            for other_owner, right in all_scopes[index + 1 :]:
                if owner != other_owner and paths_overlap(left, right):
                    add(errors, "RunManifest task authorization scopes overlap under disjoint_targets policy")


def validate_run_authority(value: Any, mode: Any, errors: list[str]) -> None:
    authority = require_object(value, "authority", errors)
    require_keys(authority, set(AUTHORITY_SURFACES), "authority", errors)
    expected_owner = "parent" if mode == "standalone" else "gauntlet"
    for surface in AUTHORITY_SURFACES:
        if authority.get(surface) != expected_owner:
            add(errors, f"authority.{surface} must be {expected_owner} for {mode}")


def validate_run_manifest(data: dict[str, Any], errors: list[str], root: Path | None) -> None:
    required = {
        "packet_type",
        "protocol_version",
        "run_id",
        "mode",
        "run_type",
        "activation",
        "plan",
        "goal",
        "criteria",
        "topology",
        "parent_runtime_attestation",
        "runtime_requirements",
        "task_dag",
        "task_authorization",
        "budget",
        "write_policy",
        "prohibited_actions",
        "context_policy",
        "authority",
    }
    require_keys(data, required, "RunManifest", errors)
    if data.get("protocol_version") != PROTOCOL_VERSION:
        add(errors, "RunManifest.protocol_version is unsupported")
    require_string(data.get("run_id"), "RunManifest.run_id", errors)
    if data.get("mode") not in {"standalone", "gauntlet_composed"}:
        add(errors, "RunManifest.mode must be standalone or gauntlet_composed")
    run_type = data.get("run_type")
    if run_type not in {"implementation", "read_only"}:
        add(errors, "RunManifest.run_type must be implementation or read_only")
    if data.get("activation") != "explicit":
        add(errors, "RunManifest.activation must be explicit")
    validate_plan(data.get("plan"), "RunManifest.plan", errors, root)
    require_string(data.get("goal"), "RunManifest.goal", errors)
    criteria = validate_criteria(data.get("criteria"), "RunManifest.criteria", errors)
    validate_topology(data.get("topology"), errors)
    validate_parent_runtime_attestation(data.get("parent_runtime_attestation"), data.get("run_id"), errors, root)
    validate_runtime_requirements(data.get("runtime_requirements"), errors)
    validate_task_dag_and_authorization(data, criteria, errors, root)
    authorizations = [item for item in data.get("task_authorization", []) if isinstance(item, dict)]
    implementation_count = sum(item.get("work_type") == "implementation" for item in authorizations)
    read_only_count = sum(item.get("work_type") == "read_only" for item in authorizations)
    if run_type == "implementation":
        if implementation_count < 1:
            add(errors, "RunManifest implementation runs require an implementation worker")
        if read_only_count > implementation_count:
            add(errors, "RunManifest read-only workers cannot outnumber implementation workers")
    elif implementation_count:
        add(errors, "RunManifest read_only runs cannot authorize implementation workers")
    budget = require_object(data.get("budget"), "RunManifest.budget", errors)
    require_keys(
        budget,
        {
            "budget_scope",
            "max_task_launches",
            "max_concurrency",
            "max_critic_rounds_per_workstream",
            "max_repair_rounds_per_workstream",
            "max_critic_rounds_total",
            "max_repair_rounds_total",
            "max_final_verification_passes",
            "max_elapsed_minutes",
            "critic_scope",
            "high_cost_override_approved",
            "cost_warning",
        },
        "RunManifest.budget",
        errors,
    )
    if budget.get("budget_scope") != "full_user_request":
        add(errors, "RunManifest.budget.budget_scope must be full_user_request")
    launches = budget.get("max_task_launches")
    concurrency = budget.get("max_concurrency")
    if not isinstance(launches, int) or isinstance(launches, bool) or not 1 <= launches <= ABSOLUTE_MAX_TASK_LAUNCHES:
        add(errors, f"RunManifest.budget.max_task_launches must be from 1 to {ABSOLUTE_MAX_TASK_LAUNCHES}")
    if not isinstance(concurrency, int) or isinstance(concurrency, bool) or not 1 <= concurrency <= ABSOLUTE_MAX_CONCURRENCY:
        add(errors, f"RunManifest.budget.max_concurrency must be from 1 to {ABSOLUTE_MAX_CONCURRENCY}")
    for field in (
        "max_critic_rounds_per_workstream",
        "max_repair_rounds_per_workstream",
        "max_critic_rounds_total",
        "max_repair_rounds_total",
        "max_final_verification_passes",
        "max_elapsed_minutes",
    ):
        require_positive_int(budget.get(field), f"RunManifest.budget.{field}", errors)
    critic_rounds_total = budget.get("max_critic_rounds_total")
    repair_rounds_total = budget.get("max_repair_rounds_total")
    if (
        isinstance(critic_rounds_total, int)
        and not isinstance(critic_rounds_total, bool)
        and critic_rounds_total > 2
    ) or (
        isinstance(repair_rounds_total, int)
        and not isinstance(repair_rounds_total, bool)
        and repair_rounds_total > 2
    ):
        add(errors, "RunManifest.budget permits at most two approved critic or repair rounds")
    if budget.get("max_final_verification_passes") != 1:
        add(errors, "RunManifest.budget.max_final_verification_passes must be 1")
    if budget.get("critic_scope") != "integrated_run":
        add(errors, "RunManifest.budget.critic_scope must be integrated_run")
    if isinstance(launches, int) and not isinstance(launches, bool) and len(authorizations) + 1 > launches:
        add(errors, "RunManifest.budget.max_task_launches must cover workers plus the integrated critic")
    high_cost = (
        isinstance(launches, int) and launches > DEFAULT_MAX_TASK_LAUNCHES
    ) or (
        isinstance(concurrency, int) and concurrency > DEFAULT_MAX_CONCURRENCY
    ) or budget.get("max_critic_rounds_total") != 1 or budget.get("max_repair_rounds_total") != 1
    if high_cost:
        if budget.get("high_cost_override_approved") is not True:
            add(errors, "RunManifest.budget high-cost limits require explicit approval")
        require_string(budget.get("cost_warning"), "RunManifest.budget.cost_warning", errors)
    elif budget.get("high_cost_override_approved") is not False or budget.get("cost_warning") is not None:
        add(errors, "RunManifest.budget ordinary limits require high_cost_override_approved=false and cost_warning=null")
    prohibited = require_string_list(data.get("prohibited_actions"), "RunManifest.prohibited_actions", errors)
    if set(prohibited) != PROHIBITED_ACTIONS:
        add(errors, "RunManifest.prohibited_actions must be the exact bounded-worker prohibition set")
    validate_context_policy(data.get("context_policy"), errors)
    validate_run_authority(data.get("authority"), data.get("mode"), errors)


def validate_task_packet(data: dict[str, Any], errors: list[str], root: Path | None) -> None:
    required = {
        "packet_type",
        "protocol_version",
        "run_id",
        "task_id",
        "run_manifest_path",
        "run_manifest_sha256",
        "plan",
        "task",
        "authorization",
        "worker",
        "runtime_attestation",
        "input_paths",
        "expected_output",
        "acceptance_criteria",
        "tools",
        "scope",
        "evidence_commands",
        "stop_conditions",
        "limits",
        "context",
    }
    require_keys(data, required, "TaskPacket", errors)
    if data.get("protocol_version") != PROTOCOL_VERSION:
        add(errors, "TaskPacket.protocol_version is unsupported")
    require_string(data.get("run_id"), "TaskPacket.run_id", errors)
    require_string(data.get("task_id"), "TaskPacket.task_id", errors)
    require_string(data.get("run_manifest_path"), "TaskPacket.run_manifest_path", errors)
    require_sha256(data.get("run_manifest_sha256"), "TaskPacket.run_manifest_sha256", errors)
    plan = validate_plan(data.get("plan"), "TaskPacket.plan", errors, root)
    task = require_object(data.get("task"), "TaskPacket.task", errors)
    require_keys(task, {"classification", "objective", "dependencies"}, "TaskPacket.task", errors)
    classification = task.get("classification")
    if classification not in {"routine", "complex"}:
        add(errors, "TaskPacket.task.classification must be routine or complex")
    require_string(task.get("objective"), "TaskPacket.task.objective", errors)
    dependencies = require_string_list(task.get("dependencies"), "TaskPacket.task.dependencies", errors, allow_empty=True)
    if data.get("task_id") in dependencies:
        add(errors, "TaskPacket.task.dependencies must not contain its own task ID")

    authorization = validate_task_authorization(data.get("authorization"), "TaskPacket.authorization", errors, root)
    expected_model = "gpt-5.6-luna" if classification == "routine" else "gpt-5.6-terra"
    validate_role(
        data.get("worker"),
        "TaskPacket.worker",
        {
            "role": "worker",
            "model": expected_model,
            "reasoning_effort": "max",
            "fresh_task": True,
            "creation_method": "create_thread",
            "forked": False,
            "may_spawn_workers": False,
            "may_approve": False,
            "may_integrate": False,
            "may_issue_final_verdict": False,
        },
        errors,
    )
    validate_creation_attestation(
        data.get("runtime_attestation"),
        "TaskPacket.runtime_attestation",
        errors,
        root,
        run_id=data.get("run_id"),
        task_id=data.get("task_id"),
        reviewer_id=None,
        role="worker",
        model=expected_model,
        effort="max",
        target="codex_task",
    )
    expected_authorization = {
        "task_id": data.get("task_id"),
        "classification": classification,
        "role": "worker",
        "model": expected_model,
        "reasoning_effort": "max",
        "dependencies": dependencies,
        "target": "codex_task",
    }
    for field, expected_value in expected_authorization.items():
        if authorization.get(field) != expected_value:
            add(errors, f"TaskPacket.authorization.{field} must exactly match the task mapping")

    inputs = validate_file_records(
        data.get("input_paths"),
        "TaskPacket.input_paths",
        errors,
        root,
        require_kind=False,
        require_root=False,
    )
    criteria = validate_criteria(data.get("acceptance_criteria"), "TaskPacket.acceptance_criteria", errors)
    if criteria != authorization.get("acceptance_criteria"):
        add(errors, "TaskPacket.acceptance_criteria must exactly match TaskPacket.authorization.acceptance_criteria")
    for field in ("input_paths", "expected_output", "tools", "evidence_commands", "stop_conditions"):
        if data.get(field) != authorization.get(field):
            add(errors, f"TaskPacket.{field} must exactly match TaskPacket.authorization.{field}")
    require_string_list(data.get("tools"), "TaskPacket.tools", errors)
    scope = require_object(data.get("scope"), "TaskPacket.scope", errors)
    require_keys(scope, {"workstream_id", "allowed_write_paths", "read_paths"}, "TaskPacket.scope", errors)
    if scope.get("workstream_id") != authorization.get("workstream_id"):
        add(errors, "TaskPacket.scope.workstream_id must exactly match task authorization")
    scope_paths = validate_scope_paths(scope.get("allowed_write_paths"), "TaskPacket.scope.allowed_write_paths", errors)
    if [str(path) for path in scope_paths] != [str(path) for path in validate_scope_paths(authorization.get("allowed_write_paths"), "TaskPacket.authorization.allowed_write_paths", errors)]:
        add(errors, "TaskPacket.scope.allowed_write_paths must exactly match task authorization")
    validate_expected_output(data.get("expected_output"), "TaskPacket.expected_output", errors, root, scope_paths)
    if inputs.get(plan.get("path")) != plan.get("sha256"):
        add(errors, "TaskPacket.input_paths must bind the referenced approved plan path and SHA-256")
    read_paths = require_string_list(scope.get("read_paths"), "TaskPacket.scope.read_paths", errors)
    if not set(inputs).issubset(set(read_paths)):
        add(errors, "TaskPacket.input_paths must be declared in TaskPacket.scope.read_paths")
    validate_task_limits(data.get("limits"), "TaskPacket.limits", errors)
    if data.get("limits") != authorization.get("limits"):
        add(errors, "TaskPacket.limits must exactly match TaskPacket.authorization.limits")

    context = require_object(data.get("context"), "TaskPacket.context", errors)
    require_keys(context, {"delivery", "include_parent_transcript", "include_hidden_reasoning", "reference_paths"}, "TaskPacket.context", errors)
    if context.get("delivery") != "bounded_packet_only":
        add(errors, "TaskPacket.context.delivery must be bounded_packet_only")
    require_bool(context.get("include_parent_transcript"), False, "TaskPacket.context.include_parent_transcript", errors)
    require_bool(context.get("include_hidden_reasoning"), False, "TaskPacket.context.include_hidden_reasoning", errors)
    references = require_string_list(context.get("reference_paths"), "TaskPacket.context.reference_paths", errors)
    if not set(references).issubset(set(read_paths)):
        add(errors, "TaskPacket.context.reference_paths must be declared read paths")

    manifest_path = resolve_file(data.get("run_manifest_path"), root, "TaskPacket.run_manifest", errors, require_root=False)
    if manifest_path is not None and isinstance(data.get("run_manifest_sha256"), str):
        if sha256_file(manifest_path) != data["run_manifest_sha256"]:
            add(errors, "TaskPacket.run_manifest_sha256 does not match the referenced RunManifest")
        manifest = load_verified_json(manifest_path, "TaskPacket.run_manifest", errors)
        if manifest is not None:
            manifest_errors: list[str] = []
            validate_run_manifest(manifest, manifest_errors, root)
            if manifest_errors:
                add(errors, f"TaskPacket referenced RunManifest is invalid: {'; '.join(manifest_errors)}")
            if data.get("run_id") != manifest.get("run_id"):
                add(errors, "TaskPacket.run_id must exactly match the referenced RunManifest")
            if data.get("plan") != manifest.get("plan"):
                add(errors, "TaskPacket.plan must exactly match the referenced RunManifest")
            manifest_authorizations = {
                item.get("task_id"): item
                for item in manifest.get("task_authorization", [])
                if isinstance(item, dict) and isinstance(item.get("task_id"), str)
            }
            if manifest_authorizations.get(data.get("task_id")) != authorization:
                add(errors, "TaskPacket.authorization must exactly match its referenced RunManifest task authorization")
            manifest_dag = {
                item.get("task_id"): item.get("dependencies")
                for item in manifest.get("task_dag", [])
                if isinstance(item, dict) and isinstance(item.get("task_id"), str)
            }
            if manifest_dag.get(data.get("task_id")) != dependencies:
                add(errors, "TaskPacket dependencies must exactly match its referenced RunManifest task DAG")


def validate_command_records(
    value: Any,
    label: str,
    errors: list[str],
    evidence: dict[str, str],
    root: Path | None,
    *,
    run_id: Any,
    task_id: Any,
    task_packet_path: Any,
    task_packet_sha256: Any,
) -> list[int]:
    exit_codes: list[int] = []
    if not isinstance(value, list):
        add(errors, f"{label} must be a list")
        return exit_codes
    for index, item in enumerate(value):
        item_label = f"{label}[{index}]"
        command = require_object(item, item_label, errors)
        require_keys(command, {"command", "exit_code", "evidence_mode", "summary", "evidence_path", "evidence_sha256"}, item_label, errors)
        require_string(command.get("command"), f"{item_label}.command", errors)
        require_string(command.get("summary"), f"{item_label}.summary", errors)
        if not isinstance(command.get("exit_code"), int) or isinstance(command.get("exit_code"), bool):
            add(errors, f"{item_label}.exit_code must be an integer")
        else:
            exit_codes.append(command["exit_code"])
        evidence_mode = command.get("evidence_mode")
        if evidence_mode not in {"inline", "file"}:
            add(errors, f"{item_label}.evidence_mode must be inline or file")
        path = command.get("evidence_path")
        if evidence_mode == "inline":
            if path is not None or command.get("evidence_sha256") is not None:
                add(errors, f"{item_label} inline evidence must not create a separate evidence file")
            continue
        if not isinstance(path, str) or evidence.get(path) != command.get("evidence_sha256"):
            add(errors, f"{item_label} must reference a verified evidence record")
        require_sha256(command.get("evidence_sha256"), f"{item_label}.evidence_sha256", errors)
        evidence_path = resolve_file(path, root, f"{item_label}.evidence", errors, require_root=True)
        if evidence_path is None:
            continue
        command_evidence = load_verified_json(evidence_path, f"{item_label}.evidence", errors)
        if command_evidence is None:
            continue
        required_evidence = {
            "record_type",
            "protocol_version",
            "run_id",
            "task_id",
            "task_packet_path",
            "task_packet_sha256",
            "command",
            "exit_code",
            "stdout",
            "stdout_sha256",
            "stderr",
            "stderr_sha256",
        }
        require_keys(command_evidence, required_evidence, f"{item_label}.evidence JSON", errors)
        if command_evidence.get("record_type") != "SolAdvisorCommandEvidence":
            add(errors, f"{item_label}.evidence JSON record_type must be SolAdvisorCommandEvidence")
        if command_evidence.get("protocol_version") != PROTOCOL_VERSION:
            add(errors, f"{item_label}.evidence JSON protocol_version is unsupported")
        expected_bindings = {
            "run_id": run_id,
            "task_id": task_id,
            "task_packet_path": task_packet_path,
            "task_packet_sha256": task_packet_sha256,
            "command": command.get("command"),
            "exit_code": command.get("exit_code"),
        }
        for field, expected_value in expected_bindings.items():
            if command_evidence.get(field) != expected_value:
                add(errors, f"{item_label}.evidence JSON {field} does not bind the recorded command")
        for stream in ("stdout", "stderr"):
            stream_value = command_evidence.get(stream)
            if not isinstance(stream_value, str):
                add(errors, f"{item_label}.evidence JSON {stream} must be a string")
                continue
            hash_field = f"{stream}_sha256"
            require_sha256(command_evidence.get(hash_field), f"{item_label}.evidence JSON {hash_field}", errors)
            if isinstance(command_evidence.get(hash_field), str) and sha256_text(stream_value) != command_evidence[hash_field]:
                add(errors, f"{item_label}.evidence JSON {hash_field} does not match recorded {stream}")
    return exit_codes


def validate_return_packet(data: dict[str, Any], errors: list[str], root: Path | None) -> None:
    required = {
        "packet_type",
        "protocol_version",
        "run_id",
        "task_id",
        "task_packet_path",
        "task_packet_sha256",
        "plan",
        "status",
        "status_evidence",
        "scope",
        "artifacts",
        "evidence",
        "criterion_to_evidence",
        "commands",
        "observable_delta",
        "primary_output_count",
        "unresolved_before",
        "unresolved_after",
        "support_artifact_count",
        "uncertainties",
        "risks",
        "next_target_action",
        "authority",
    }
    require_keys(data, required, "ReturnPacket", errors)
    if data.get("protocol_version") != PROTOCOL_VERSION:
        add(errors, "ReturnPacket.protocol_version is unsupported")
    require_string(data.get("run_id"), "ReturnPacket.run_id", errors)
    require_string(data.get("task_id"), "ReturnPacket.task_id", errors)
    require_string(data.get("task_packet_path"), "ReturnPacket.task_packet_path", errors)
    require_sha256(data.get("task_packet_sha256"), "ReturnPacket.task_packet_sha256", errors)
    validate_plan(data.get("plan"), "ReturnPacket.plan", errors, root)
    status = data.get("status")
    if status not in RETURN_STATUSES:
        add(errors, "ReturnPacket.status must be succeeded, blocked, failed, or escalate")
    scope = require_object(data.get("scope"), "ReturnPacket.scope", errors)
    require_keys(scope, {"allowed_write_paths", "actual_write_paths"}, "ReturnPacket.scope", errors)
    allowed = validate_scope_paths(scope.get("allowed_write_paths"), "ReturnPacket.scope.allowed_write_paths", errors)
    actual = validate_scope_paths(scope.get("actual_write_paths"), "ReturnPacket.scope.actual_write_paths", errors, allow_empty=True)
    for path in actual:
        if not any(is_descendant(path, root_path) for root_path in allowed):
            add(errors, "ReturnPacket.scope.actual_write_paths must stay within allowed_write_paths")
            break
    returned_artifact_paths = validate_artifact_records(
        data.get("artifacts"),
        "ReturnPacket.artifacts",
        errors,
        root,
        allowed,
    )
    evidence = validate_file_records(data.get("evidence"), "ReturnPacket.evidence", errors, root, require_kind=True, require_root=True)
    status_evidence = require_object(data.get("status_evidence"), "ReturnPacket.status_evidence", errors)
    require_keys(status_evidence, {"summary", "evidence_path", "evidence_sha256"}, "ReturnPacket.status_evidence", errors)
    require_string(status_evidence.get("summary"), "ReturnPacket.status_evidence.summary", errors)
    if evidence.get(status_evidence.get("evidence_path")) != status_evidence.get("evidence_sha256"):
        add(errors, "ReturnPacket.status_evidence must reference verified evidence")
    require_sha256(status_evidence.get("evidence_sha256"), "ReturnPacket.status_evidence.evidence_sha256", errors)
    mappings = data.get("criterion_to_evidence")
    results: list[str] = []
    seen_criteria: set[str] = set()
    if not isinstance(mappings, list) or not mappings:
        add(errors, "ReturnPacket.criterion_to_evidence must be a non-empty list")
    else:
        for index, item in enumerate(mappings):
            item_label = f"ReturnPacket.criterion_to_evidence[{index}]"
            mapping = require_object(item, item_label, errors)
            require_keys(mapping, {"criterion_id", "result", "evidence_paths"}, item_label, errors)
            require_string(mapping.get("criterion_id"), f"{item_label}.criterion_id", errors)
            criterion_id = mapping.get("criterion_id")
            if isinstance(criterion_id, str):
                if criterion_id in seen_criteria:
                    add(errors, "ReturnPacket.criterion_to_evidence criterion ids must be unique")
                seen_criteria.add(criterion_id)
            result = mapping.get("result")
            if result not in CRITERION_RESULTS:
                add(errors, f"{item_label}.result is invalid")
            elif isinstance(result, str):
                results.append(result)
            paths = require_string_list(mapping.get("evidence_paths"), f"{item_label}.evidence_paths", errors)
            if any(path not in evidence for path in paths):
                add(errors, f"{item_label}.evidence_paths must reference verified evidence")
    command_exit_codes = validate_command_records(
        data.get("commands"),
        "ReturnPacket.commands",
        errors,
        evidence,
        root,
        run_id=data.get("run_id"),
        task_id=data.get("task_id"),
        task_packet_path=data.get("task_packet_path"),
        task_packet_sha256=data.get("task_packet_sha256"),
    )
    observable_delta = data.get("observable_delta")
    if not isinstance(observable_delta, str):
        add(errors, "ReturnPacket.observable_delta must be a string")
    for field in ("primary_output_count", "unresolved_before", "unresolved_after", "support_artifact_count"):
        require_nonnegative_int(data.get(field), f"ReturnPacket.{field}", errors)
    if isinstance(data.get("unresolved_before"), int) and isinstance(data.get("unresolved_after"), int) and data["unresolved_after"] > data["unresolved_before"]:
        add(errors, "ReturnPacket.unresolved_after cannot exceed unresolved_before")
    require_string_list(data.get("uncertainties"), "ReturnPacket.uncertainties", errors, allow_empty=True)
    require_string_list(data.get("risks"), "ReturnPacket.risks", errors, allow_empty=True)
    require_string(data.get("next_target_action"), "ReturnPacket.next_target_action", errors)
    if status == "succeeded" and any(result != "met" for result in results):
        add(errors, "ReturnPacket.status=succeeded requires every criterion mapping to be met")
    if status == "succeeded" and any(exit_code != 0 for exit_code in command_exit_codes):
        add(errors, "ReturnPacket.status=succeeded requires every evidence command to exit zero")
    expected_result = {"blocked": "blocked", "failed": "failed", "escalate": "escalate"}.get(status)
    if expected_result and expected_result not in results:
        add(errors, f"ReturnPacket.status={status} requires criterion evidence with result={expected_result}")
    authority = require_object(data.get("authority"), "ReturnPacket.authority", errors)
    required_authority = {"may_approve", "may_integrate", "may_update_state", "may_update_budget", "may_issue_final_verdict"}
    require_keys(authority, required_authority, "ReturnPacket.authority", errors)
    for field in required_authority:
        require_bool(authority.get(field), False, f"ReturnPacket.authority.{field}", errors)

    task_path = resolve_file(data.get("task_packet_path"), root, "ReturnPacket.task_packet", errors, require_root=True)
    if task_path is not None and isinstance(data.get("task_packet_sha256"), str):
        if sha256_file(task_path) != data["task_packet_sha256"]:
            add(errors, "ReturnPacket.task_packet_sha256 does not match the referenced TaskPacket")
        task_packet = load_verified_json(task_path, "ReturnPacket.task_packet", errors)
        if task_packet is not None:
            task_errors: list[str] = []
            validate_task_packet(task_packet, task_errors, root)
            if task_errors:
                add(errors, f"ReturnPacket referenced TaskPacket is invalid: {'; '.join(task_errors)}")
            for field in ("run_id", "task_id", "plan"):
                if data.get(field) != task_packet.get(field):
                    add(errors, f"ReturnPacket.{field} must exactly match the referenced TaskPacket")
            if scope.get("allowed_write_paths") != task_packet.get("scope", {}).get("allowed_write_paths"):
                add(errors, "ReturnPacket.scope.allowed_write_paths must exactly match the referenced TaskPacket")
            task_authorization = task_packet.get("authorization", {})
            if data.get("unresolved_before") != task_authorization.get("unresolved_before"):
                add(errors, "ReturnPacket.unresolved_before must match the TaskPacket authorization")
            support_limit = task_authorization.get("support_artifact_limit")
            if isinstance(data.get("support_artifact_count"), int) and isinstance(support_limit, int) and data["support_artifact_count"] > support_limit:
                add(errors, "ReturnPacket.support_artifact_count exceeds the TaskPacket limit")
            if status == "succeeded" and task_authorization.get("work_type") == "implementation":
                if not isinstance(observable_delta, str) or not observable_delta.strip():
                    add(errors, "ReturnPacket implementation success requires a non-empty observable_delta")
                if not isinstance(data.get("primary_output_count"), int) or data["primary_output_count"] < 1:
                    add(errors, "ReturnPacket implementation success requires primary_output_count >= 1")
                unresolved_before = data.get("unresolved_before")
                unresolved_after = data.get("unresolved_after")
                if isinstance(unresolved_before, int) and unresolved_before > 0 and isinstance(unresolved_after, int) and unresolved_after >= unresolved_before:
                    add(errors, "ReturnPacket implementation success must reduce unresolved work")
            task_allowed = validate_scope_paths(
                task_packet.get("scope", {}).get("allowed_write_paths"),
                "ReturnPacket referenced TaskPacket.scope.allowed_write_paths",
                errors,
            )
            expected_artifacts = task_packet.get("expected_output", {}).get("paths")
            if isinstance(expected_artifacts, list):
                validate_artifact_records(
                    data.get("artifacts"),
                    "ReturnPacket.artifacts",
                    errors,
                    root,
                    task_allowed,
                    expected_paths=expected_artifacts,
                )
            elif returned_artifact_paths:
                add(errors, "ReturnPacket referenced TaskPacket expected output paths are invalid")
            expected_commands = task_packet.get("evidence_commands")
            actual_commands = [item.get("command") for item in data.get("commands", []) if isinstance(item, dict)]
            if actual_commands != expected_commands:
                add(errors, "ReturnPacket commands must exactly match the referenced TaskPacket evidence commands")
            expected_criteria = {item.get("id") for item in task_packet.get("acceptance_criteria", []) if isinstance(item, dict)}
            if seen_criteria != expected_criteria:
                add(errors, "ReturnPacket criterion mapping must exactly cover the referenced TaskPacket criteria")


def validate_review_packet(data: dict[str, Any], errors: list[str], root: Path | None) -> None:
    required = {
        "packet_type",
        "protocol_version",
        "run_id",
        "task_id",
        "workstream_id",
        "reviewer_id",
        "task_packet_path",
        "task_packet_sha256",
        "return_packet_path",
        "return_packet_sha256",
        "plan",
        "reviewer",
        "runtime_attestation",
        "artifacts_or_diffs",
        "evidence",
        "reproduction_commands",
        "findings",
        "verdict",
        "uncertainties",
        "risks",
        "next_action",
        "authority",
    }
    require_keys(data, required, "ReviewPacket", errors)
    if data.get("protocol_version") != PROTOCOL_VERSION:
        add(errors, "ReviewPacket.protocol_version is unsupported")
    require_string(data.get("run_id"), "ReviewPacket.run_id", errors)
    require_string(data.get("task_id"), "ReviewPacket.task_id", errors)
    require_string(data.get("workstream_id"), "ReviewPacket.workstream_id", errors)
    require_string(data.get("reviewer_id"), "ReviewPacket.reviewer_id", errors)
    require_string(data.get("task_packet_path"), "ReviewPacket.task_packet_path", errors)
    require_sha256(data.get("task_packet_sha256"), "ReviewPacket.task_packet_sha256", errors)
    require_string(data.get("return_packet_path"), "ReviewPacket.return_packet_path", errors)
    require_sha256(data.get("return_packet_sha256"), "ReviewPacket.return_packet_sha256", errors)
    if data.get("reviewer_id") == data.get("task_id"):
        add(errors, "ReviewPacket.reviewer_id must not equal the builder task_id")
    validate_plan(data.get("plan"), "ReviewPacket.plan", errors, root)
    validate_role(
        data.get("reviewer"),
        "ReviewPacket.reviewer",
        {
            "role": "workstream_critic",
            "model": "gpt-5.6-sol",
            "reasoning_effort": "xhigh",
            "fresh_task": True,
            "creation_method": "create_thread",
            "forked": False,
            "may_build": False,
            "may_repair": False,
            "may_write": False,
            "may_approve": False,
            "may_integrate": False,
            "may_update_state": False,
            "may_update_budget": False,
            "may_issue_final_verdict": False,
        },
        errors,
    )
    validate_creation_attestation(
        data.get("runtime_attestation"),
        "ReviewPacket.runtime_attestation",
        errors,
        root,
        run_id=data.get("run_id"),
        task_id=data.get("task_id"),
        reviewer_id=data.get("reviewer_id"),
        role="workstream_critic",
        model="gpt-5.6-sol",
        effort="xhigh",
        target="codex_task",
    )
    validate_file_records(data.get("artifacts_or_diffs"), "ReviewPacket.artifacts_or_diffs", errors, root, require_kind=True, require_root=True)
    evidence = validate_file_records(data.get("evidence"), "ReviewPacket.evidence", errors, root, require_kind=True, require_root=True)
    reproduction_exit_codes = validate_command_records(
        data.get("reproduction_commands"),
        "ReviewPacket.reproduction_commands",
        errors,
        evidence,
        root,
        run_id=data.get("run_id"),
        task_id=data.get("task_id"),
        task_packet_path=data.get("task_packet_path"),
        task_packet_sha256=data.get("task_packet_sha256"),
    )
    findings = data.get("findings")
    severities: list[str] = []
    if not isinstance(findings, list):
        add(errors, "ReviewPacket.findings must be a list")
        findings = []
    seen: set[str] = set()
    for index, item in enumerate(findings):
        item_label = f"ReviewPacket.findings[{index}]"
        finding = require_object(item, item_label, errors)
        require_keys(finding, {"id", "severity", "criterion_id", "summary", "evidence_paths", "recommendation"}, item_label, errors)
        require_string(finding.get("id"), f"{item_label}.id", errors)
        finding_id = finding.get("id")
        if isinstance(finding_id, str):
            if finding_id in seen:
                add(errors, "ReviewPacket.finding ids must be unique")
            seen.add(finding_id)
        severity = finding.get("severity")
        if severity not in FINDING_SEVERITIES:
            add(errors, f"{item_label}.severity is invalid")
        elif isinstance(severity, str):
            severities.append(severity)
        require_string(finding.get("criterion_id"), f"{item_label}.criterion_id", errors)
        require_string(finding.get("summary"), f"{item_label}.summary", errors)
        paths = require_string_list(finding.get("evidence_paths"), f"{item_label}.evidence_paths", errors)
        if any(path not in evidence for path in paths):
            add(errors, f"{item_label}.evidence_paths must reference verified evidence")
        require_string(finding.get("recommendation"), f"{item_label}.recommendation", errors)
    verdict = data.get("verdict")
    if verdict not in REVIEW_VERDICTS:
        add(errors, "ReviewPacket.verdict must be accepted, revise, blocked, or unable_to_verify")
    if verdict == "accepted" and any(item in {"blocking", "major"} for item in severities):
        add(errors, "ReviewPacket.verdict=accepted cannot contain blocking or major findings")
    if verdict == "accepted" and any(exit_code != 0 for exit_code in reproduction_exit_codes):
        add(errors, "ReviewPacket.verdict=accepted requires every reproduction command to exit zero")
    if verdict == "revise" and not any(item in {"major", "minor"} for item in severities):
        add(errors, "ReviewPacket.verdict=revise requires a major or minor finding")
    if verdict == "blocked" and "blocking" not in severities:
        add(errors, "ReviewPacket.verdict=blocked requires a blocking finding")
    require_string_list(data.get("uncertainties"), "ReviewPacket.uncertainties", errors, allow_empty=True)
    require_string_list(data.get("risks"), "ReviewPacket.risks", errors, allow_empty=True)
    require_string(data.get("next_action"), "ReviewPacket.next_action", errors)
    authority = require_object(data.get("authority"), "ReviewPacket.authority", errors)
    required_authority = {
        "may_approve",
        "may_integrate",
        "may_update_state",
        "may_update_budget",
        "may_issue_final_verdict",
        "may_replace_verification_panel",
    }
    require_keys(authority, required_authority, "ReviewPacket.authority", errors)
    for field in required_authority:
        require_bool(authority.get(field), False, f"ReviewPacket.authority.{field}", errors)

    task_path = resolve_file(data.get("task_packet_path"), root, "ReviewPacket.task_packet", errors, require_root=True)
    return_path = resolve_file(data.get("return_packet_path"), root, "ReviewPacket.return_packet", errors, require_root=True)
    task_packet: dict[str, Any] | None = None
    returned_packet: dict[str, Any] | None = None
    if task_path is not None and isinstance(data.get("task_packet_sha256"), str):
        if sha256_file(task_path) != data["task_packet_sha256"]:
            add(errors, "ReviewPacket.task_packet_sha256 does not match the referenced TaskPacket")
        task_packet = load_verified_json(task_path, "ReviewPacket.task_packet", errors)
        if task_packet is not None:
            task_errors: list[str] = []
            validate_task_packet(task_packet, task_errors, root)
            if task_errors:
                add(errors, f"ReviewPacket referenced TaskPacket is invalid: {'; '.join(task_errors)}")
    if return_path is not None and isinstance(data.get("return_packet_sha256"), str):
        if sha256_file(return_path) != data["return_packet_sha256"]:
            add(errors, "ReviewPacket.return_packet_sha256 does not match the referenced ReturnPacket")
        returned_packet = load_verified_json(return_path, "ReviewPacket.return_packet", errors)
        if returned_packet is not None:
            return_errors: list[str] = []
            validate_return_packet(returned_packet, return_errors, root)
            if return_errors:
                add(errors, f"ReviewPacket referenced ReturnPacket is invalid: {'; '.join(return_errors)}")
    if task_packet is not None and returned_packet is not None:
        for field in ("run_id", "task_id", "plan"):
            if data.get(field) != task_packet.get(field):
                add(errors, f"ReviewPacket.{field} must exactly match the referenced TaskPacket")
            if data.get(field) != returned_packet.get(field):
                add(errors, f"ReviewPacket.{field} must exactly match the referenced ReturnPacket")
        if data.get("workstream_id") != task_packet.get("scope", {}).get("workstream_id"):
            add(errors, "ReviewPacket.workstream_id must exactly match the referenced TaskPacket")
        if data.get("reviewer_id") != task_packet.get("authorization", {}).get("reviewer_id"):
            add(errors, "ReviewPacket.reviewer_id must exactly match the referenced TaskPacket authorization")
        if returned_packet.get("task_packet_path") != data.get("task_packet_path") or returned_packet.get("task_packet_sha256") != data.get("task_packet_sha256"):
            add(errors, "ReviewPacket ReturnPacket must exactly bind the referenced TaskPacket")
        if data.get("artifacts_or_diffs") != returned_packet.get("artifacts"):
            add(errors, "ReviewPacket reviewed artifacts must exactly equal the referenced ReturnPacket artifacts")
        task_allowed = validate_scope_paths(
            task_packet.get("scope", {}).get("allowed_write_paths"),
            "ReviewPacket referenced TaskPacket.scope.allowed_write_paths",
            errors,
        )
        expected_artifacts = task_packet.get("expected_output", {}).get("paths")
        if isinstance(expected_artifacts, list):
            validate_artifact_records(
                data.get("artifacts_or_diffs"),
                "ReviewPacket.artifacts_or_diffs",
                errors,
                root,
                task_allowed,
                expected_paths=expected_artifacts,
            )


def validate_packet(data: Any, root: Path | None = None) -> list[str]:
    errors: list[str] = []
    packet = require_object(data, "packet", errors)
    packet_type = packet.get("packet_type")
    if packet_type == "RunManifest":
        validate_run_manifest(packet, errors, root)
    elif packet_type == "TaskPacket":
        validate_task_packet(packet, errors, root)
    elif packet_type == "ReturnPacket":
        validate_return_packet(packet, errors, root)
    elif packet_type == "ReviewPacket":
        validate_review_packet(packet, errors, root)
    else:
        add(errors, "packet_type must be RunManifest, TaskPacket, ReturnPacket, or ReviewPacket")
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, help="Root used to verify evidence files")
    parser.add_argument("packets", nargs="+", type=Path, help="Packet JSON files")
    args = parser.parse_args(argv)
    all_errors: list[str] = []
    results: list[dict[str, Any]] = []
    for path in args.packets:
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            errors = [f"invalid input: {exc}"]
            packet_type = None
        else:
            errors = validate_packet(data, args.root)
            packet_type = data.get("packet_type") if isinstance(data, dict) else None
        results.append({"path": str(path), "packet_type": packet_type, "valid": not errors, "errors": errors})
        all_errors.extend(errors)
    print(json.dumps({"valid": not all_errors, "packets": results}, indent=2))
    return 1 if all_errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
