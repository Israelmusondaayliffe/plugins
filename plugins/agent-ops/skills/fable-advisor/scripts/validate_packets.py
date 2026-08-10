#!/usr/bin/env python3
"""Validate fail-closed Fable Advisor packets and their inspectable evidence.

Claude-native adaptation of the Sol Advisor packet validator: adaptive topology,
exact-model worker authorizations, Agent-tool or headless spawn evidence, and
fresh-reviewer attestation. Validation checks records; it never executes commands.
"""

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

PARENT_MODEL = "claude-fable-5"
REVIEWER_MODEL = "claude-fable-5"
REVIEWER_EFFORT = "xhigh"
REVIEWER_DEFINITION = "fa-reviewer"

LIGHT_MODELS = {"claude-sonnet-5": {"low", "medium"}}
COMPLEX_MODELS = {
    "claude-opus-4-8": {"xhigh"},
    "claude-opus-5": {"xhigh"},
    "claude-opus-4-6": {"high"},
}
AGENT_DEFINITIONS = {
    "fa-worker-light": {"claude-sonnet-5"},
    "fa-worker-complex": {"claude-opus-4-8"},
    "fa-worker-complex-opus5": {"claude-opus-5"},
    "fa-worker-complex-46": {"claude-opus-4-6"},
}
SPAWN_MECHANISMS = {"agent_tool", "headless"}

AUTHORITY_SURFACES = (
    "state",
    "budget",
    "approval",
    "integration",
    "final_answer",
    "terminal_verdict",
)
PROHIBITED_ACTIONS = {
    "approve_work",
    "issue_final_answer",
    "issue_terminal_verdict",
    "reviewer_repairs",
    "spawn_peer_workers",
    "contact_user",
    "integrate_workstreams",
    "modify_run_state",
}
RETURN_STATUSES = {"succeeded", "blocked", "failed", "escalate"}
REVIEW_VERDICTS = {"accepted", "revise", "blocked", "unable_to_verify"}
CRITERION_RESULTS = {"met", "blocked", "failed", "escalate"}
FINDING_SEVERITIES = {"blocking", "major", "minor", "info"}
WRITE_POLICY_MODES = {"disjoint_targets", "separate_worktrees", "serialized"}
ATTESTATION_STATES = {"verified", "partially-verified"}


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
        add(errors, f"{label} must be a{'' if allow_empty else ' non-empty'} list of strings")
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


def require_positive_int(value: Any, label: str, errors: list[str], *, maximum: int | None = None) -> None:
    if not isinstance(value, int) or isinstance(value, bool) or value < 1:
        add(errors, f"{label} must be a positive finite integer")
    elif maximum is not None and value > maximum:
        add(errors, f"{label} must be at most {maximum}")


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


def resolve_file(path_value: Any, root: Path, label: str, errors: list[str]) -> Path | None:
    """Resolve a root-relative path to an existing file beneath the run root."""
    if not isinstance(path_value, str) or not path_value.strip():
        add(errors, f"{label}.path must be a non-empty relative path")
        return None
    candidate_input = Path(path_value)
    if candidate_input.is_absolute() or ".." in candidate_input.parts:
        add(errors, f"{label}.path must stay under the run root")
        return None
    resolved_root = root.resolve()
    candidate = (resolved_root / candidate_input).resolve()
    if not is_descendant(candidate, resolved_root) or not candidate.is_file():
        add(errors, f"{label}.path must resolve to an existing file beneath --root")
        return None
    return candidate


def normalized_scope(value: Any, root: Path, label: str, errors: list[str]) -> Path | None:
    """Resolve a root-relative scope path (need not exist yet)."""
    if not isinstance(value, str) or not value.strip():
        add(errors, f"{label} must be a non-empty relative path")
        return None
    raw = Path(value)
    if raw.is_absolute() or ".." in raw.parts:
        add(errors, f"{label} must stay under the run root")
        return None
    resolved_root = root.resolve()
    candidate = (resolved_root / raw).resolve()
    if candidate == resolved_root:
        add(errors, f"{label} must not be the run root itself")
        return None
    if not is_descendant(candidate, resolved_root):
        add(errors, f"{label} must resolve beneath the run root")
        return None
    return candidate


def paths_overlap(left: Path, right: Path) -> bool:
    return is_descendant(left, right) or is_descendant(right, left)


def validate_scope_paths(values: Any, root: Path, label: str, errors: list[str]) -> list[Path]:
    if not isinstance(values, list) or not values:
        add(errors, f"{label} must be a non-empty list")
        return []
    paths: list[Path] = []
    for index, value in enumerate(values):
        path = normalized_scope(value, root, f"{label}[{index}]", errors)
        if path is not None:
            paths.append(path)
    for index, left in enumerate(paths):
        for right in paths[index + 1:]:
            if paths_overlap(left, right):
                add(errors, f"{label} contains overlapping paths")
                return paths
    return paths


def load_verified_json(path: Path, label: str, errors: list[str]) -> dict[str, Any] | None:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        add(errors, f"{label} must contain JSON: {exc}")
        return None
    return require_object(data, f"{label} JSON", errors)


def validate_file_ref(value: Any, root: Path, label: str, errors: list[str]) -> tuple[dict[str, Any], Path | None]:
    """Validate a {path, sha256} record whose hash must match the file."""
    record = require_object(value, label, errors)
    require_keys(record, {"path", "sha256"}, label, errors)
    require_sha256(record.get("sha256"), f"{label}.sha256", errors)
    path = resolve_file(record.get("path"), root, label, errors)
    if path is not None and isinstance(record.get("sha256"), str):
        if sha256_file(path) != record["sha256"]:
            add(errors, f"{label}.sha256 does not match {record.get('path')}")
    return record, path


def validate_plan(value: Any, root: Path, label: str, errors: list[str]) -> dict[str, Any]:
    plan = require_object(value, label, errors)
    require_keys(plan, {"status", "version", "path", "sha256"}, label, errors)
    if plan.get("status") != "approved":
        add(errors, f"{label}.status must be approved")
    require_positive_int(plan.get("version"), f"{label}.version", errors)
    require_sha256(plan.get("sha256"), f"{label}.sha256", errors)
    path = resolve_file(plan.get("path"), root, label, errors)
    if path is not None and isinstance(plan.get("sha256"), str):
        if sha256_file(path) != plan["sha256"]:
            add(errors, f"{label}.sha256 does not match the referenced approved plan")
    return plan


def validate_criteria(value: Any, label: str, errors: list[str]) -> dict[str, str]:
    result: dict[str, str] = {}
    if not isinstance(value, list) or not value:
        add(errors, f"{label} must be a non-empty list")
        return result
    for index, item in enumerate(value):
        item_label = f"{label}[{index}]"
        criterion = require_object(item, item_label, errors)
        require_keys(criterion, {"id", "description"}, item_label, errors)
        require_string(criterion.get("id"), f"{item_label}.id", errors)
        require_string(criterion.get("description"), f"{item_label}.description", errors)
        criterion_id = criterion.get("id")
        if isinstance(criterion_id, str):
            if criterion_id in result:
                add(errors, f"{label} criterion ids must be unique")
            if isinstance(criterion.get("description"), str):
                result[criterion_id] = criterion["description"]
    return result


def worker_role_check(classification: Any, model: Any, effort: Any, definition: Any, label: str, errors: list[str]) -> None:
    if classification == "light":
        allowed = LIGHT_MODELS
    elif classification == "complex":
        allowed = COMPLEX_MODELS
    else:
        add(errors, f"{label}.classification must be light or complex")
        return
    if model not in allowed:
        add(errors, f"{label}.model {model!r} is not an authorized {classification} worker model")
        return
    if effort not in allowed[model]:
        add(errors, f"{label}.effort {effort!r} is not authorized for {model}")
    if definition not in AGENT_DEFINITIONS or model not in AGENT_DEFINITIONS.get(definition, set()):
        add(errors, f"{label}.agent_definition {definition!r} does not pin {model}")


def validate_task_limits(value: Any, label: str, errors: list[str]) -> None:
    limits = require_object(value, label, errors)
    require_keys(limits, {"max_attempts", "max_turns", "max_elapsed_minutes"}, label, errors)
    require_positive_int(limits.get("max_attempts"), f"{label}.max_attempts", errors, maximum=3)
    require_positive_int(limits.get("max_turns"), f"{label}.max_turns", errors)
    require_positive_int(limits.get("max_elapsed_minutes"), f"{label}.max_elapsed_minutes", errors)


def validate_task_authorization(value: Any, root: Path, label: str, errors: list[str]) -> dict[str, Any]:
    authorization = require_object(value, label, errors)
    required = {
        "task_id",
        "classification",
        "role",
        "agent_definition",
        "model",
        "effort",
        "dependencies",
        "allowed_write_paths",
        "input_paths",
        "expected_output",
        "acceptance_criteria",
        "tools",
        "evidence_commands",
        "stop_conditions",
        "limits",
    }
    require_keys(authorization, required, label, errors)
    require_string(authorization.get("task_id"), f"{label}.task_id", errors)
    if authorization.get("role") != "worker":
        add(errors, f"{label}.role must be worker")
    worker_role_check(
        authorization.get("classification"),
        authorization.get("model"),
        authorization.get("effort"),
        authorization.get("agent_definition"),
        label,
        errors,
    )
    dependencies = require_string_list(authorization.get("dependencies"), f"{label}.dependencies", errors, allow_empty=True)
    if authorization.get("task_id") in dependencies:
        add(errors, f"{label}.dependencies must not contain its own task ID")
    write_paths = validate_scope_paths(authorization.get("allowed_write_paths"), root, f"{label}.allowed_write_paths", errors)
    inputs = authorization.get("input_paths")
    if not isinstance(inputs, list) or not inputs:
        add(errors, f"{label}.input_paths must be a non-empty list")
    else:
        seen: set[str] = set()
        for index, item in enumerate(inputs):
            record, _ = validate_file_ref(item, root, f"{label}.input_paths[{index}]", errors)
            path_value = record.get("path")
            if isinstance(path_value, str):
                if path_value in seen:
                    add(errors, f"{label}.input_paths must not repeat paths")
                seen.add(path_value)
    output = require_object(authorization.get("expected_output"), f"{label}.expected_output", errors)
    require_keys(output, {"description", "paths"}, f"{label}.expected_output", errors)
    require_string(output.get("description"), f"{label}.expected_output.description", errors)
    for index, path_value in enumerate(require_string_list(output.get("paths"), f"{label}.expected_output.paths", errors)):
        candidate = normalized_scope(path_value, root, f"{label}.expected_output.paths[{index}]", errors)
        if candidate is not None and not any(is_descendant(candidate, allowed) for allowed in write_paths):
            add(errors, f"{label}.expected_output.paths[{index}] must stay within allowed_write_paths")
    validate_criteria(authorization.get("acceptance_criteria"), f"{label}.acceptance_criteria", errors)
    require_string_list(authorization.get("tools"), f"{label}.tools", errors)
    require_string_list(authorization.get("evidence_commands"), f"{label}.evidence_commands", errors)
    require_string_list(authorization.get("stop_conditions"), f"{label}.stop_conditions", errors)
    validate_task_limits(authorization.get("limits"), f"{label}.limits", errors)
    return authorization


def validate_run_manifest(data: dict[str, Any], errors: list[str], root: Path) -> None:
    required = {
        "packet_type",
        "protocol_version",
        "run_id",
        "mode",
        "activation",
        "plan",
        "goal",
        "criteria",
        "runtime",
        "task_dag",
        "task_authorization",
        "budget",
        "write_policy",
        "prohibited_actions",
        "authority",
    }
    require_keys(data, required, "RunManifest", errors)
    if data.get("packet_type") != "FableAdvisorRunManifest":
        add(errors, "RunManifest.packet_type must be FableAdvisorRunManifest")
    if data.get("protocol_version") != PROTOCOL_VERSION:
        add(errors, "RunManifest.protocol_version is unsupported")
    require_string(data.get("run_id"), "RunManifest.run_id", errors)
    if data.get("mode") not in {"standalone", "composed"}:
        add(errors, "RunManifest.mode must be standalone or composed")

    activation = require_object(data.get("activation"), "RunManifest.activation", errors)
    require_keys(activation, {"type", "quoted_request", "recorded_at"}, "RunManifest.activation", errors)
    if activation.get("type") != "explicit":
        add(errors, "RunManifest.activation.type must be explicit")
    require_string(activation.get("quoted_request"), "RunManifest.activation.quoted_request", errors)
    require_iso_timestamp(activation.get("recorded_at"), "RunManifest.activation.recorded_at", errors)

    validate_plan(data.get("plan"), root, "RunManifest.plan", errors)
    require_string(data.get("goal"), "RunManifest.goal", errors)
    criteria = validate_criteria(data.get("criteria"), "RunManifest.criteria", errors)

    runtime = require_object(data.get("runtime"), "RunManifest.runtime", errors)
    require_keys(
        runtime,
        {"claude_code_version", "entrypoint", "parent_session_id", "parent_model", "spawn_mechanism"},
        "RunManifest.runtime",
        errors,
    )
    require_string(runtime.get("claude_code_version"), "RunManifest.runtime.claude_code_version", errors)
    require_string(runtime.get("entrypoint"), "RunManifest.runtime.entrypoint", errors)
    require_string(runtime.get("parent_session_id"), "RunManifest.runtime.parent_session_id", errors)
    if runtime.get("parent_model") != PARENT_MODEL:
        add(errors, f"RunManifest.runtime.parent_model must be {PARENT_MODEL}")
    if runtime.get("spawn_mechanism") not in SPAWN_MECHANISMS:
        add(errors, "RunManifest.runtime.spawn_mechanism must be agent_tool or headless")

    raw_authorizations = data.get("task_authorization")
    if not isinstance(raw_authorizations, list) or not raw_authorizations:
        add(errors, "RunManifest.task_authorization must be a non-empty list")
        raw_authorizations = []
    authorizations: dict[str, dict[str, Any]] = {}
    assigned_criteria: set[str] = set()
    all_scopes: list[tuple[str, Path]] = []
    for index, item in enumerate(raw_authorizations):
        authorization = validate_task_authorization(item, root, f"RunManifest.task_authorization[{index}]", errors)
        task_id = authorization.get("task_id")
        if isinstance(task_id, str):
            if task_id in authorizations:
                add(errors, "RunManifest.task_authorization task ids must be unique")
            authorizations[task_id] = authorization
        for criterion in authorization.get("acceptance_criteria", []) if isinstance(authorization.get("acceptance_criteria"), list) else []:
            if isinstance(criterion, dict):
                if criteria.get(criterion.get("id")) != criterion.get("description"):
                    add(errors, "RunManifest.task_authorization criteria must be exact approved RunManifest criteria")
                elif isinstance(criterion.get("id"), str):
                    assigned_criteria.add(criterion["id"])
        for scope in validate_scope_paths(authorization.get("allowed_write_paths"), root, f"RunManifest.task_authorization[{index}].allowed_write_paths", []):
            all_scopes.append((str(task_id), scope))
    if criteria and assigned_criteria != set(criteria):
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
        visiting.discard(task_id)
        visited.add(task_id)

    for task_id in dependencies:
        visit(task_id)

    budget = require_object(data.get("budget"), "RunManifest.budget", errors)
    require_keys(
        budget,
        {"max_task_launches", "max_concurrency", "max_review_rounds", "max_repair_rounds", "max_elapsed_minutes"},
        "RunManifest.budget",
        errors,
    )
    for field in ("max_task_launches", "max_concurrency", "max_review_rounds", "max_repair_rounds", "max_elapsed_minutes"):
        require_positive_int(budget.get(field), f"RunManifest.budget.{field}", errors)
    require_positive_int(budget.get("max_concurrency"), "RunManifest.budget.max_concurrency", errors, maximum=20)

    policy = require_object(data.get("write_policy"), "RunManifest.write_policy", errors)
    require_keys(
        policy,
        {"mode", "require_disjoint_active_scopes", "allow_unlisted_writes", "allowed_write_roots"},
        "RunManifest.write_policy",
        errors,
    )
    if policy.get("mode") not in WRITE_POLICY_MODES:
        add(errors, "RunManifest.write_policy.mode is invalid")
    require_bool(policy.get("require_disjoint_active_scopes"), True, "RunManifest.write_policy.require_disjoint_active_scopes", errors)
    require_bool(policy.get("allow_unlisted_writes"), False, "RunManifest.write_policy.allow_unlisted_writes", errors)
    roots = validate_scope_paths(policy.get("allowed_write_roots"), root, "RunManifest.write_policy.allowed_write_roots", errors)
    for _, scope in all_scopes:
        if roots and not any(is_descendant(scope, allowed) for allowed in roots):
            add(errors, "RunManifest task authorization write scope must stay within write_policy.allowed_write_roots")
    if policy.get("mode") == "disjoint_targets":
        for index, (owner, left) in enumerate(all_scopes):
            for other_owner, right in all_scopes[index + 1:]:
                if owner != other_owner and paths_overlap(left, right):
                    add(errors, "RunManifest task authorization scopes overlap under disjoint_targets policy")

    prohibited = require_string_list(data.get("prohibited_actions"), "RunManifest.prohibited_actions", errors)
    if set(prohibited) != PROHIBITED_ACTIONS:
        add(errors, "RunManifest.prohibited_actions must be the exact bounded-worker prohibition set")

    authority = require_object(data.get("authority"), "RunManifest.authority", errors)
    require_keys(authority, set(AUTHORITY_SURFACES), "RunManifest.authority", errors)
    expected_owner = "parent" if data.get("mode") == "standalone" else "gauntlet"
    for surface in AUTHORITY_SURFACES:
        if authority.get(surface) != expected_owner:
            add(errors, f"RunManifest.authority.{surface} must be {expected_owner} for {data.get('mode')}")


def load_and_validate(path: Path, root: Path, label: str, errors: list[str], validator: Any) -> dict[str, Any] | None:
    data = load_verified_json(path, label, errors)
    if data is None:
        return None
    nested: list[str] = []
    validator(data, nested, root)
    if nested:
        add(errors, f"{label} is invalid: {'; '.join(nested)}")
    return data


def validate_task_packet(data: dict[str, Any], errors: list[str], root: Path) -> None:
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
    if data.get("packet_type") != "FableAdvisorTaskPacket":
        add(errors, "TaskPacket.packet_type must be FableAdvisorTaskPacket")
    if data.get("protocol_version") != PROTOCOL_VERSION:
        add(errors, "TaskPacket.protocol_version is unsupported")
    require_string(data.get("run_id"), "TaskPacket.run_id", errors)
    require_string(data.get("task_id"), "TaskPacket.task_id", errors)

    plan = validate_plan(data.get("plan"), root, "TaskPacket.plan", errors)
    task = require_object(data.get("task"), "TaskPacket.task", errors)
    require_keys(task, {"classification", "objective", "dependencies"}, "TaskPacket.task", errors)
    require_string(task.get("objective"), "TaskPacket.task.objective", errors)
    dependencies = require_string_list(task.get("dependencies"), "TaskPacket.task.dependencies", errors, allow_empty=True)
    if data.get("task_id") in dependencies:
        add(errors, "TaskPacket.task.dependencies must not contain its own task ID")

    authorization = validate_task_authorization(data.get("authorization"), root, "TaskPacket.authorization", errors)
    for field, expected_value in {
        "task_id": data.get("task_id"),
        "classification": task.get("classification"),
        "dependencies": dependencies,
    }.items():
        if authorization.get(field) != expected_value:
            add(errors, f"TaskPacket.authorization.{field} must exactly match the task mapping")

    worker = require_object(data.get("worker"), "TaskPacket.worker", errors)
    require_keys(
        worker,
        {"role", "agent_definition", "model", "effort", "fresh_instance", "mechanism"},
        "TaskPacket.worker",
        errors,
    )
    if worker.get("role") != "worker":
        add(errors, "TaskPacket.worker.role must be worker")
    require_bool(worker.get("fresh_instance"), True, "TaskPacket.worker.fresh_instance", errors)
    if worker.get("mechanism") not in SPAWN_MECHANISMS:
        add(errors, "TaskPacket.worker.mechanism must be agent_tool or headless")
    for field in ("agent_definition", "model", "effort"):
        if worker.get(field) != authorization.get(field):
            add(errors, f"TaskPacket.worker.{field} must exactly match the task authorization")

    for field in ("input_paths", "expected_output", "acceptance_criteria", "tools", "evidence_commands", "stop_conditions", "limits"):
        if data.get(field) != authorization.get(field):
            add(errors, f"TaskPacket.{field} must exactly match TaskPacket.authorization.{field}")

    scope = require_object(data.get("scope"), "TaskPacket.scope", errors)
    require_keys(scope, {"allowed_write_paths", "read_paths"}, "TaskPacket.scope", errors)
    if scope.get("allowed_write_paths") != authorization.get("allowed_write_paths"):
        add(errors, "TaskPacket.scope.allowed_write_paths must exactly match task authorization")
    read_paths = require_string_list(scope.get("read_paths"), "TaskPacket.scope.read_paths", errors)
    input_paths = {
        item.get("path")
        for item in data.get("input_paths", [])
        if isinstance(item, dict) and isinstance(item.get("path"), str)
    }
    if not input_paths.issubset(set(read_paths)):
        add(errors, "TaskPacket.input_paths must be declared in TaskPacket.scope.read_paths")
    plan_bound = any(
        isinstance(item, dict) and item.get("path") == plan.get("path") and item.get("sha256") == plan.get("sha256")
        for item in data.get("input_paths", [])
        if isinstance(data.get("input_paths"), list)
    ) if isinstance(data.get("input_paths"), list) else False
    if not plan_bound:
        add(errors, "TaskPacket.input_paths must bind the referenced approved plan path and SHA-256")

    context = require_object(data.get("context"), "TaskPacket.context", errors)
    require_keys(
        context,
        {"delivery", "include_parent_transcript", "include_hidden_reasoning", "reference_paths"},
        "TaskPacket.context",
        errors,
    )
    if context.get("delivery") != "bounded_packet_only":
        add(errors, "TaskPacket.context.delivery must be bounded_packet_only")
    require_bool(context.get("include_parent_transcript"), False, "TaskPacket.context.include_parent_transcript", errors)
    require_bool(context.get("include_hidden_reasoning"), False, "TaskPacket.context.include_hidden_reasoning", errors)
    references = require_string_list(context.get("reference_paths"), "TaskPacket.context.reference_paths", errors, allow_empty=True)
    if not set(references).issubset(set(read_paths)):
        add(errors, "TaskPacket.context.reference_paths must be declared read paths")

    require_sha256(data.get("run_manifest_sha256"), "TaskPacket.run_manifest_sha256", errors)
    manifest_path = resolve_file(data.get("run_manifest_path"), root, "TaskPacket.run_manifest", errors)
    if manifest_path is not None and isinstance(data.get("run_manifest_sha256"), str):
        if sha256_file(manifest_path) != data["run_manifest_sha256"]:
            add(errors, "TaskPacket.run_manifest_sha256 does not match the referenced RunManifest")
        manifest = load_and_validate(manifest_path, root, "TaskPacket referenced RunManifest", errors, validate_run_manifest)
        if manifest is not None:
            if data.get("run_id") != manifest.get("run_id"):
                add(errors, "TaskPacket.run_id must exactly match the referenced RunManifest")
            if data.get("plan") != manifest.get("plan"):
                add(errors, "TaskPacket.plan must exactly match the referenced RunManifest")
            manifest_authorizations = {
                item.get("task_id"): item
                for item in manifest.get("task_authorization", [])
                if isinstance(item, dict) and isinstance(item.get("task_id"), str)
            }
            if manifest_authorizations.get(data.get("task_id")) != data.get("authorization"):
                add(errors, "TaskPacket.authorization must exactly match its referenced RunManifest task authorization")
            manifest_dag = {
                item.get("task_id"): item.get("dependencies")
                for item in manifest.get("task_dag", [])
                if isinstance(item, dict) and isinstance(item.get("task_id"), str)
            }
            if manifest_dag.get(data.get("task_id")) != dependencies:
                add(errors, "TaskPacket dependencies must exactly match its referenced RunManifest task DAG")


def validate_spawn_record(
    value: Any,
    root: Path,
    label: str,
    errors: list[str],
    *,
    run_id: Any,
    subject_type: str,
    subject_id: Any,
    agent_definition: Any,
    requested_model: Any,
    requested_effort: Any,
    runtime_id: Any,
) -> None:
    record_ref, path = validate_file_ref(value, root, label, errors)
    if path is None:
        return
    record = load_verified_json(path, label, errors)
    if record is None:
        return
    require_keys(
        record,
        {
            "record_type",
            "protocol_version",
            "run_id",
            "subject_type",
            "subject_id",
            "agent_definition",
            "requested_model",
            "requested_effort",
            "mechanism",
            "runtime_id",
            "spawned_at",
        },
        f"{label} JSON",
        errors,
    )
    expected = {
        "record_type": "FableAdvisorSpawnRecord",
        "protocol_version": PROTOCOL_VERSION,
        "run_id": run_id,
        "subject_type": subject_type,
        "subject_id": subject_id,
        "agent_definition": agent_definition,
        "requested_model": requested_model,
        "requested_effort": requested_effort,
        "runtime_id": runtime_id,
    }
    for field, expected_value in expected.items():
        if record.get(field) != expected_value:
            add(errors, f"{label} JSON {field} does not bind the spawn")
    if record.get("mechanism") not in SPAWN_MECHANISMS:
        add(errors, f"{label} JSON mechanism must be agent_tool or headless")
    require_iso_timestamp(record.get("spawned_at"), f"{label} JSON spawned_at", errors)


def validate_model_record(
    value: Any,
    root: Path,
    label: str,
    errors: list[str],
    *,
    run_id: Any,
    subject_type: str,
    subject_id: Any,
    requested_model: Any,
) -> None:
    record_ref, path = validate_file_ref(value, root, label, errors)
    if path is None:
        return
    record = load_verified_json(path, label, errors)
    if record is None:
        return
    require_keys(
        record,
        {
            "record_type",
            "protocol_version",
            "run_id",
            "subject_type",
            "subject_id",
            "requested_model",
            "observed_models",
            "attestation",
            "source",
            "reason",
        },
        f"{label} JSON",
        errors,
    )
    expected = {
        "record_type": "FableAdvisorModelRecord",
        "protocol_version": PROTOCOL_VERSION,
        "run_id": run_id,
        "subject_type": subject_type,
        "subject_id": subject_id,
        "requested_model": requested_model,
    }
    for field, expected_value in expected.items():
        if record.get(field) != expected_value:
            add(errors, f"{label} JSON {field} does not bind the attestation")
    attestation = record.get("attestation")
    if attestation not in ATTESTATION_STATES:
        add(errors, f"{label} JSON attestation must be verified or partially-verified")
    observed = record.get("observed_models")
    if not isinstance(observed, list) or any(not isinstance(item, str) for item in observed):
        add(errors, f"{label} JSON observed_models must be a list of strings")
        observed = []
    require_string(record.get("source"), f"{label} JSON source", errors)
    if attestation == "verified":
        if requested_model not in observed:
            add(errors, f"{label} JSON verified attestation requires the requested model among observed_models")
        if record.get("reason") is not None:
            add(errors, f"{label} JSON reason must be null when attestation is verified")
    elif attestation == "partially-verified":
        require_string(record.get("reason"), f"{label} JSON reason", errors)
    if observed and requested_model not in observed:
        add(errors, f"{label} JSON observed_models contradict the requested model")


def validate_command_records(
    value: Any,
    root: Path,
    label: str,
    errors: list[str],
    *,
    run_id: Any,
    subject_type: str,
    subject_id: Any,
    bound_packet_path: Any,
    bound_packet_sha256: Any,
) -> list[int]:
    exit_codes: list[int] = []
    if not isinstance(value, list) or not value:
        add(errors, f"{label} must be a non-empty list")
        return exit_codes
    for index, item in enumerate(value):
        item_label = f"{label}[{index}]"
        command = require_object(item, item_label, errors)
        if command.get("risk") == "low":
            # Ordinary low-risk commands inline their result; separate evidence
            # files are reserved for destructive, security, release, or
            # installation commands.
            require_keys(command, {"command", "exit_code", "risk", "summary"}, item_label, errors)
            require_string(command.get("command"), f"{item_label}.command", errors)
            require_string(command.get("summary"), f"{item_label}.summary", errors)
            if not isinstance(command.get("exit_code"), int) or isinstance(command.get("exit_code"), bool):
                add(errors, f"{item_label}.exit_code must be an integer")
            else:
                exit_codes.append(command["exit_code"])
            continue
        require_keys(command, {"command", "exit_code", "evidence_path", "evidence_sha256"}, item_label, errors)
        require_string(command.get("command"), f"{item_label}.command", errors)
        if not isinstance(command.get("exit_code"), int) or isinstance(command.get("exit_code"), bool):
            add(errors, f"{item_label}.exit_code must be an integer")
        else:
            exit_codes.append(command["exit_code"])
        require_sha256(command.get("evidence_sha256"), f"{item_label}.evidence_sha256", errors)
        evidence_path = resolve_file(command.get("evidence_path"), root, f"{item_label}.evidence", errors)
        if evidence_path is None:
            continue
        if isinstance(command.get("evidence_sha256"), str) and sha256_file(evidence_path) != command["evidence_sha256"]:
            add(errors, f"{item_label}.evidence_sha256 does not match the evidence file")
        evidence = load_verified_json(evidence_path, f"{item_label}.evidence", errors)
        if evidence is None:
            continue
        require_keys(
            evidence,
            {
                "record_type",
                "protocol_version",
                "run_id",
                "subject_type",
                "subject_id",
                "bound_packet_path",
                "bound_packet_sha256",
                "command",
                "exit_code",
                "stdout",
                "stdout_sha256",
                "stderr",
                "stderr_sha256",
            },
            f"{item_label}.evidence JSON",
            errors,
        )
        expected = {
            "record_type": "FableAdvisorCommandEvidence",
            "protocol_version": PROTOCOL_VERSION,
            "run_id": run_id,
            "subject_type": subject_type,
            "subject_id": subject_id,
            "bound_packet_path": bound_packet_path,
            "bound_packet_sha256": bound_packet_sha256,
            "command": command.get("command"),
            "exit_code": command.get("exit_code"),
        }
        for field, expected_value in expected.items():
            if evidence.get(field) != expected_value:
                add(errors, f"{item_label}.evidence JSON {field} does not bind the recorded command")
        for stream in ("stdout", "stderr"):
            stream_value = evidence.get(stream)
            if not isinstance(stream_value, str):
                add(errors, f"{item_label}.evidence JSON {stream} must be a string")
                continue
            hash_field = f"{stream}_sha256"
            require_sha256(evidence.get(hash_field), f"{item_label}.evidence JSON {hash_field}", errors)
            if isinstance(evidence.get(hash_field), str) and sha256_text(stream_value) != evidence[hash_field]:
                add(errors, f"{item_label}.evidence JSON {hash_field} does not match recorded {stream}")
    return exit_codes


def validate_return_packet(data: dict[str, Any], errors: list[str], root: Path) -> None:
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
        "criterion_results",
        "commands",
        "work_report",
        "runtime_attestation",
        "uncertainties",
        "risks",
        "next_action",
    }
    require_keys(data, required, "ReturnPacket", errors)
    if data.get("packet_type") != "FableAdvisorReturnPacket":
        add(errors, "ReturnPacket.packet_type must be FableAdvisorReturnPacket")
    if data.get("protocol_version") != PROTOCOL_VERSION:
        add(errors, "ReturnPacket.protocol_version is unsupported")
    require_string(data.get("run_id"), "ReturnPacket.run_id", errors)
    require_string(data.get("task_id"), "ReturnPacket.task_id", errors)
    status = data.get("status")
    if status not in RETURN_STATUSES:
        add(errors, "ReturnPacket.status must be succeeded, blocked, failed, or escalate")
    require_string(data.get("status_evidence"), "ReturnPacket.status_evidence", errors)
    validate_plan(data.get("plan"), root, "ReturnPacket.plan", errors)

    require_sha256(data.get("task_packet_sha256"), "ReturnPacket.task_packet_sha256", errors)
    packet_path = resolve_file(data.get("task_packet_path"), root, "ReturnPacket.task_packet", errors)
    packet: dict[str, Any] | None = None
    if packet_path is not None and isinstance(data.get("task_packet_sha256"), str):
        if sha256_file(packet_path) != data["task_packet_sha256"]:
            add(errors, "ReturnPacket.task_packet_sha256 does not match the referenced TaskPacket")
        packet = load_and_validate(packet_path, root, "ReturnPacket referenced TaskPacket", errors, validate_task_packet)
    if packet is not None:
        if data.get("run_id") != packet.get("run_id"):
            add(errors, "ReturnPacket.run_id must exactly match the referenced TaskPacket")
        if data.get("task_id") != packet.get("task_id"):
            add(errors, "ReturnPacket.task_id must exactly match the referenced TaskPacket")
        if data.get("plan") != packet.get("plan"):
            add(errors, "ReturnPacket.plan must exactly match the referenced TaskPacket")

    packet_scope = packet.get("scope", {}).get("allowed_write_paths") if isinstance(packet, dict) else None
    allowed = validate_scope_paths(packet_scope, root, "ReturnPacket allowed write paths", []) if isinstance(packet_scope, list) else []
    scope = require_object(data.get("scope"), "ReturnPacket.scope", errors)
    require_keys(scope, {"allowed_write_paths", "writes_observed"}, "ReturnPacket.scope", errors)
    if packet is not None and scope.get("allowed_write_paths") != packet_scope:
        add(errors, "ReturnPacket.scope.allowed_write_paths must exactly match the TaskPacket scope")
    for index, path_value in enumerate(require_string_list(scope.get("writes_observed"), "ReturnPacket.scope.writes_observed", errors, allow_empty=True)):
        candidate = normalized_scope(path_value, root, f"ReturnPacket.scope.writes_observed[{index}]", errors)
        if candidate is not None and allowed and not any(is_descendant(candidate, item) for item in allowed):
            add(errors, f"ReturnPacket.scope.writes_observed[{index}] must stay within the TaskPacket scope")

    artifacts = data.get("artifacts")
    artifact_paths: list[str] = []
    if not isinstance(artifacts, list) or not artifacts:
        add(errors, "ReturnPacket.artifacts must be a non-empty list")
    else:
        for index, item in enumerate(artifacts):
            item_label = f"ReturnPacket.artifacts[{index}]"
            record = require_object(item, item_label, errors)
            require_keys(record, {"path", "sha256", "kind"}, item_label, errors)
            require_string(record.get("kind"), f"{item_label}.kind", errors)
            require_sha256(record.get("sha256"), f"{item_label}.sha256", errors)
            path = resolve_file(record.get("path"), root, item_label, errors)
            if path is not None and isinstance(record.get("sha256"), str):
                if sha256_file(path) != record["sha256"]:
                    add(errors, f"{item_label}.sha256 does not match {record.get('path')}")
            path_value = record.get("path")
            if isinstance(path_value, str):
                artifact_paths.append(path_value)
                candidate = normalized_scope(path_value, root, item_label, errors)
                if candidate is not None and allowed and not any(is_descendant(candidate, item) for item in allowed):
                    add(errors, f"{item_label} must stay within the TaskPacket allowed write paths")
    if packet is not None:
        expected_paths = packet.get("expected_output", {}).get("paths")
        if isinstance(expected_paths, list) and artifact_paths != expected_paths:
            add(errors, "ReturnPacket.artifacts must exactly match the TaskPacket expected output paths")

    results = data.get("criterion_results")
    result_map: dict[str, str] = {}
    if not isinstance(results, list) or not results:
        add(errors, "ReturnPacket.criterion_results must be a non-empty list")
    else:
        for index, item in enumerate(results):
            item_label = f"ReturnPacket.criterion_results[{index}]"
            record = require_object(item, item_label, errors)
            require_keys(record, {"id", "result", "evidence"}, item_label, errors)
            require_string(record.get("id"), f"{item_label}.id", errors)
            if record.get("result") not in CRITERION_RESULTS:
                add(errors, f"{item_label}.result must be met, blocked, failed, or escalate")
            require_string(record.get("evidence"), f"{item_label}.evidence", errors)
            if isinstance(record.get("id"), str):
                if record["id"] in result_map:
                    add(errors, "ReturnPacket.criterion_results ids must be unique")
                if isinstance(record.get("result"), str):
                    result_map[record["id"]] = record["result"]
    if packet is not None:
        packet_criteria = {
            item.get("id")
            for item in packet.get("acceptance_criteria", [])
            if isinstance(item, dict) and isinstance(item.get("id"), str)
        }
        if packet_criteria and set(result_map) != packet_criteria:
            add(errors, "ReturnPacket.criterion_results must cover exactly the TaskPacket acceptance criteria")

    exit_codes = validate_command_records(
        data.get("commands"),
        root,
        "ReturnPacket.commands",
        errors,
        run_id=data.get("run_id"),
        subject_type="task",
        subject_id=data.get("task_id"),
        bound_packet_path=data.get("task_packet_path"),
        bound_packet_sha256=data.get("task_packet_sha256"),
    )
    work_report = require_object(data.get("work_report"), "ReturnPacket.work_report", errors)
    require_keys(
        work_report,
        {
            "observable_delta",
            "primary_output_count",
            "unresolved_before",
            "unresolved_after",
            "support_artifact_count",
            "next_target_action",
        },
        "ReturnPacket.work_report",
        errors,
    )
    delta = require_string_list(
        work_report.get("observable_delta"), "ReturnPacket.work_report.observable_delta", errors, allow_empty=True
    )
    for field in ("primary_output_count", "unresolved_before", "unresolved_after", "support_artifact_count"):
        value = work_report.get(field)
        if not isinstance(value, int) or isinstance(value, bool) or value < 0:
            add(errors, f"ReturnPacket.work_report.{field} must be a non-negative integer")
    require_string(work_report.get("next_target_action"), "ReturnPacket.work_report.next_target_action", errors)

    if status == "succeeded":
        if result_map and any(result != "met" for result in result_map.values()):
            add(errors, "ReturnPacket.status succeeded requires every criterion met")
        if any(code != 0 for code in exit_codes):
            add(errors, "ReturnPacket.status succeeded requires every evidence command to exit 0")
        if not delta:
            add(errors, "ReturnPacket.status succeeded requires a non-empty work_report.observable_delta")
        before = work_report.get("unresolved_before")
        after = work_report.get("unresolved_after")
        if isinstance(before, int) and isinstance(after, int) and not isinstance(before, bool) and not isinstance(after, bool):
            if not (after < before or (before == 0 and after == 0)):
                add(errors, "ReturnPacket.status succeeded requires unresolved required work to improve")
    elif status in {"blocked", "failed", "escalate"}:
        expected_result = "escalate" if status == "escalate" else status
        if result_map and expected_result not in result_map.values():
            add(errors, f"ReturnPacket.status {status} requires at least one criterion marked {expected_result}")

    attestation = require_object(data.get("runtime_attestation"), "ReturnPacket.runtime_attestation", errors)
    require_keys(
        attestation,
        {"agent_definition", "requested_model", "requested_effort", "runtime_id", "spawn_record", "model_record"},
        "ReturnPacket.runtime_attestation",
        errors,
    )
    if packet is not None:
        worker = packet.get("worker", {}) if isinstance(packet.get("worker"), dict) else {}
        for field, packet_field in (("agent_definition", "agent_definition"), ("requested_model", "model"), ("requested_effort", "effort")):
            if attestation.get(field) != worker.get(packet_field):
                add(errors, f"ReturnPacket.runtime_attestation.{field} must exactly match the TaskPacket worker")
    require_string(attestation.get("runtime_id"), "ReturnPacket.runtime_attestation.runtime_id", errors)
    validate_spawn_record(
        attestation.get("spawn_record"),
        root,
        "ReturnPacket.runtime_attestation.spawn_record",
        errors,
        run_id=data.get("run_id"),
        subject_type="task",
        subject_id=data.get("task_id"),
        agent_definition=attestation.get("agent_definition"),
        requested_model=attestation.get("requested_model"),
        requested_effort=attestation.get("requested_effort"),
        runtime_id=attestation.get("runtime_id"),
    )
    validate_model_record(
        attestation.get("model_record"),
        root,
        "ReturnPacket.runtime_attestation.model_record",
        errors,
        run_id=data.get("run_id"),
        subject_type="task",
        subject_id=data.get("task_id"),
        requested_model=attestation.get("requested_model"),
    )

    require_string_list(data.get("uncertainties"), "ReturnPacket.uncertainties", errors, allow_empty=True)
    require_string_list(data.get("risks"), "ReturnPacket.risks", errors, allow_empty=True)
    require_string(data.get("next_action"), "ReturnPacket.next_action", errors)


def validate_review_packet(data: dict[str, Any], errors: list[str], root: Path) -> None:
    required = {
        "packet_type",
        "protocol_version",
        "run_id",
        "review_round",
        "verdict",
        "reviewed",
        "plan",
        "candidate",
        "reproduction_commands",
        "findings",
        "reviewer_attestation",
        "uncertainties",
        "next_action",
    }
    require_keys(data, required, "ReviewPacket", errors)
    if data.get("packet_type") != "FableAdvisorReviewPacket":
        add(errors, "ReviewPacket.packet_type must be FableAdvisorReviewPacket")
    if data.get("protocol_version") != PROTOCOL_VERSION:
        add(errors, "ReviewPacket.protocol_version is unsupported")
    require_string(data.get("run_id"), "ReviewPacket.run_id", errors)
    require_positive_int(data.get("review_round"), "ReviewPacket.review_round", errors)
    verdict = data.get("verdict")
    if verdict not in REVIEW_VERDICTS:
        add(errors, "ReviewPacket.verdict must be accepted, revise, blocked, or unable_to_verify")
    validate_plan(data.get("plan"), root, "ReviewPacket.plan", errors)

    reviewed = data.get("reviewed")
    return_artifacts: dict[str, str] = {}
    if not isinstance(reviewed, list) or not reviewed:
        add(errors, "ReviewPacket.reviewed must be a non-empty list")
    else:
        for index, item in enumerate(reviewed):
            item_label = f"ReviewPacket.reviewed[{index}]"
            pair = require_object(item, item_label, errors)
            require_keys(pair, {"task_packet", "return_packet"}, item_label, errors)
            validate_file_ref(pair.get("task_packet"), root, f"{item_label}.task_packet", errors)
            _, return_path = validate_file_ref(pair.get("return_packet"), root, f"{item_label}.return_packet", errors)
            if return_path is not None:
                return_data = load_and_validate(return_path, root, f"{item_label}.return_packet", errors, validate_return_packet)
                if return_data is not None:
                    if return_data.get("run_id") != data.get("run_id"):
                        add(errors, f"{item_label}.return_packet run_id must match the review run")
                    for artifact in return_data.get("artifacts", []) if isinstance(return_data.get("artifacts"), list) else []:
                        if isinstance(artifact, dict) and isinstance(artifact.get("path"), str) and isinstance(artifact.get("sha256"), str):
                            return_artifacts[artifact["path"]] = artifact["sha256"]

    candidate = data.get("candidate")
    candidate_map: dict[str, str] = {}
    if not isinstance(candidate, list) or not candidate:
        add(errors, "ReviewPacket.candidate must be a non-empty list")
    else:
        for index, item in enumerate(candidate):
            record, _ = validate_file_ref(item, root, f"ReviewPacket.candidate[{index}]", errors)
            if isinstance(record.get("path"), str) and isinstance(record.get("sha256"), str):
                if record["path"] in candidate_map:
                    add(errors, "ReviewPacket.candidate must not repeat paths")
                candidate_map[record["path"]] = record["sha256"]
    if return_artifacts and candidate_map and candidate_map != return_artifacts:
        add(errors, "ReviewPacket.candidate must exactly equal the reviewed ReturnPacket artifact set")

    exit_codes = validate_command_records(
        data.get("reproduction_commands"),
        root,
        "ReviewPacket.reproduction_commands",
        errors,
        run_id=data.get("run_id"),
        subject_type="review",
        subject_id=f"round-{data.get('review_round')}",
        bound_packet_path=None,
        bound_packet_sha256=None,
    )

    findings = data.get("findings")
    severities: list[str] = []
    if not isinstance(findings, list):
        add(errors, "ReviewPacket.findings must be a list")
    else:
        for index, item in enumerate(findings):
            item_label = f"ReviewPacket.findings[{index}]"
            finding = require_object(item, item_label, errors)
            require_keys(finding, {"id", "severity", "description"}, item_label, errors)
            require_string(finding.get("id"), f"{item_label}.id", errors)
            require_string(finding.get("description"), f"{item_label}.description", errors)
            if finding.get("severity") not in FINDING_SEVERITIES:
                add(errors, f"{item_label}.severity must be blocking, major, minor, or info")
            elif isinstance(finding.get("severity"), str):
                severities.append(finding["severity"])
    if verdict == "accepted":
        if any(code != 0 for code in exit_codes):
            add(errors, "ReviewPacket.verdict accepted requires every reproduction command to exit 0")
        if "blocking" in severities:
            add(errors, "ReviewPacket.verdict accepted must not carry blocking findings")
    if verdict == "revise" and not any(severity in {"blocking", "major"} for severity in severities):
        add(errors, "ReviewPacket.verdict revise requires at least one blocking or major finding")

    attestation = require_object(data.get("reviewer_attestation"), "ReviewPacket.reviewer_attestation", errors)
    require_keys(
        attestation,
        {
            "agent_definition",
            "model",
            "effort",
            "runtime_id",
            "fresh_instance",
            "spawn_record",
            "prior_review_runtime_ids",
        },
        "ReviewPacket.reviewer_attestation",
        errors,
    )
    if attestation.get("agent_definition") != REVIEWER_DEFINITION:
        add(errors, f"ReviewPacket.reviewer_attestation.agent_definition must be {REVIEWER_DEFINITION}")
    if attestation.get("model") != REVIEWER_MODEL:
        add(errors, f"ReviewPacket.reviewer_attestation.model must be {REVIEWER_MODEL}")
    if attestation.get("effort") != REVIEWER_EFFORT:
        add(errors, f"ReviewPacket.reviewer_attestation.effort must be {REVIEWER_EFFORT}")
    require_bool(attestation.get("fresh_instance"), True, "ReviewPacket.reviewer_attestation.fresh_instance", errors)
    require_string(attestation.get("runtime_id"), "ReviewPacket.reviewer_attestation.runtime_id", errors)
    prior = require_string_list(
        attestation.get("prior_review_runtime_ids"),
        "ReviewPacket.reviewer_attestation.prior_review_runtime_ids",
        errors,
        allow_empty=True,
    )
    if isinstance(attestation.get("runtime_id"), str) and attestation.get("runtime_id") in prior:
        add(errors, "ReviewPacket.reviewer_attestation.runtime_id must never repeat a prior review round instance")
    validate_spawn_record(
        attestation.get("spawn_record"),
        root,
        "ReviewPacket.reviewer_attestation.spawn_record",
        errors,
        run_id=data.get("run_id"),
        subject_type="review",
        subject_id=f"round-{data.get('review_round')}",
        agent_definition=REVIEWER_DEFINITION,
        requested_model=REVIEWER_MODEL,
        requested_effort=REVIEWER_EFFORT,
        runtime_id=attestation.get("runtime_id"),
    )

    require_string_list(data.get("uncertainties"), "ReviewPacket.uncertainties", errors, allow_empty=True)
    require_string(data.get("next_action"), "ReviewPacket.next_action", errors)


VALIDATORS = {
    "FableAdvisorRunManifest": validate_run_manifest,
    "FableAdvisorTaskPacket": validate_task_packet,
    "FableAdvisorReturnPacket": validate_return_packet,
    "FableAdvisorReviewPacket": validate_review_packet,
}


def validate_packet_file(path: Path, root: Path) -> list[str]:
    errors: list[str] = []
    data = load_verified_json(path, str(path), errors)
    if data is None:
        return errors
    packet_type = data.get("packet_type")
    validator = VALIDATORS.get(packet_type)
    if validator is None:
        add(errors, f"{path}: unsupported packet_type {packet_type!r}")
        return errors
    validator(data, errors, root)
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", required=True, type=Path, help="run root for root-relative packet paths")
    parser.add_argument("packets", nargs="+", type=Path)
    args = parser.parse_args(argv)
    if not args.root.is_dir():
        print(f"error: --root {args.root} is not a directory")
        return 1
    failed = False
    for packet in args.packets:
        errors = validate_packet_file(packet, args.root)
        if errors:
            failed = True
            print(f"INVALID {packet}")
            for error in errors:
                print(f"  - {error}")
        else:
            print(f"valid {packet}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
