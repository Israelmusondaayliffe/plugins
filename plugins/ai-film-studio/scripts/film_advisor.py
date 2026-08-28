#!/usr/bin/env python3
"""Deterministic, non-mutating Film Advisor packet evaluator."""

from __future__ import annotations

import json
import hashlib
import re
import sys
from pathlib import Path
from typing import Any, Dict

ROUTES = {"concept":"film-wayfinder","brief":"ai-film-studio","architecture":"production-architect","assets":"asset-bible-director","performance":"performance-director","geography":"visual-development-director","shots":"shot-continuity-director","adapter":"film-prompt-director","iteration":"iteration-supervisor","finish":"post-delivery-director"}
PLANNING_ACTIONS = {"plan","draft","validate"}
EXTERNAL_ACTIONS = {"paid_generation","account_authentication","upload","purchase","destructive_replacement","publication","material_scope_expansion"}
ALL_ACTIONS = PLANNING_ACTIONS | EXTERNAL_ACTIONS
REQUIRED_EVIDENCE = {
    "paid_generation": ("cost_preview",),
    "account_authentication": ("account",),
    "upload": ("destination", "files"),
    "purchase": ("cost_preview", "vendor"),
    "destructive_replacement": ("recovery_plan",),
    "publication": ("destination", "visibility"),
    "material_scope_expansion": ("scope_delta", "cost_preview"),
}

FILM_GRILL_FIELDS = (
    "intent",
    "audience",
    "story",
    "runtime",
    "visual_language",
    "sound_language",
    "resources",
    "budget",
    "schedule",
    "rights",
    "target_models",
    "distribution",
    "risk",
    "approval_policy",
    "smallest_test_scene",
)
ENHANCED_TOPOLOGY_CAPABILITIES = {
    "sol_high_planner",
    "terra_max_builder",
    "sol_xhigh_reviewers",
    "fresh_nonforked_tasks",
    "bounded_write_authority",
    "runtime_receipts",
}
SHOT_PACKET_FIELDS = (
    "id",
    "scene_id",
    "purpose",
    "duration_seconds",
    "status",
    "target_model",
    "active_references",
    "geography",
    "first_frame",
    "action_beats",
    "performance",
    "camera",
    "lens",
    "light",
    "physics",
    "dialogue",
    "sound",
    "constraints",
)


def build_local_grill_state(decisions: Dict[str, Any]) -> Dict[str, Any]:
    """Build the local film decision record without a companion plugin."""
    if not isinstance(decisions, dict):
        return _stopped("film_grill", "decisions_must_be_object")
    decided: Dict[str, Any] = {}
    alternatives: Dict[str, Any] = {}
    decision_reasons: Dict[str, Any] = {}
    source_evidence: Dict[str, Any] = {}
    next_proof: Dict[str, Any] = {}
    open_fields: list[str] = []
    for field in FILM_GRILL_FIELDS:
        entry = decisions.get(field)
        if not isinstance(entry, dict) or not _nonempty(entry.get("decision")):
            open_fields.append(field)
            continue
        decided[field] = entry["decision"].strip()
        alternatives[field] = entry.get("alternatives", [])
        decision_reasons[field] = entry.get("reason", "")
        source_evidence[field] = entry.get("source", "user decision")
        next_proof[field] = entry.get("next_proof", "")
    assumptions = decisions.get("_assumptions", {})
    if not isinstance(assumptions, dict):
        assumptions = {}
    return {
        "protocol": "film-wayfinder/local-grill/v1",
        "status": "ready" if not open_fields else "needs_input",
        "decided": decided,
        "assumed": assumptions,
        "open": open_fields,
        "alternatives": alternatives,
        "decision_reasons": decision_reasons,
        "source_evidence": source_evidence,
        "next_proof": next_proof,
        "next_question": open_fields[0] if open_fields else None,
    }


def resolve_host_topology(available_capabilities: Any) -> Dict[str, Any]:
    """Choose the enhanced topology only when the host proves every requirement."""
    if not isinstance(available_capabilities, (list, set, tuple)):
        available: set[str] = set()
    else:
        available = {value for value in available_capabilities if isinstance(value, str)}
    missing = sorted(ENHANCED_TOPOLOGY_CAPABILITIES - available)
    if not missing:
        return {
            "protocol": "film-advisor/topology-resolution/v1",
            "status": "enhanced_topology_proved",
            "mode": "sol-terra-bounded",
            "missing": [],
        }
    return {
        "protocol": "film-advisor/topology-resolution/v1",
        "status": "local_core_available",
        "mode": "local-bounded-planner",
        "missing": missing,
        "phases": ["plan", "draft", "audit", "one_bounded_repair", "verify"],
        "claims_limit": "Do not claim model or fresh-task independence that the host did not prove.",
    }


def build_unsupported_topology_handoff(
    topology_resolution: Dict[str, Any],
    completed_local_work: list[str],
    unresolved_proof: str,
    next_action: str,
) -> Dict[str, Any]:
    """Return the exact stop packet for work that requires unavailable host proof."""
    missing = topology_resolution.get("missing", []) if isinstance(topology_resolution, dict) else []
    return {
        "protocol": "film-advisor/unsupported-topology/v1",
        "status": "stopped",
        "reason": "unsupported_topology",
        "missing_capability": missing,
        "completed_local_work": completed_local_work,
        "unresolved_proof": unresolved_proof,
        "next_action": next_action,
    }


def build_model_neutral_shot_packet(
    shot_record: Dict[str, Any],
    profile: Dict[str, Any],
    formatter_available: bool = False,
) -> Dict[str, Any]:
    """Return a complete normalized packet and an honest optional-formatter state."""
    if not isinstance(shot_record, dict) or not isinstance(profile, dict):
        return _stopped("prompt_packet", "shot_and_profile_must_be_objects")
    missing = [field for field in SHOT_PACKET_FIELDS if field not in shot_record]
    if missing:
        return _stopped("prompt_packet", "shot_record_incomplete", missing_fields=missing)
    shot_id = str(shot_record.get("id", ""))
    if not re.fullmatch(r"shot_[a-z0-9_]+", shot_id):
        return _stopped("prompt_packet", "invalid_shot_id")
    model_id = profile.get("model_id")
    profile_version = profile.get("profile_version")
    if not _nonempty(model_id) or not _nonempty(profile_version):
        return _stopped("prompt_packet", "profile_identity_incomplete")
    canonical_shot = json.dumps(shot_record, sort_keys=True, separators=(",", ":")).encode("utf-8")
    shot_sha256 = hashlib.sha256(canonical_shot).hexdigest()
    optional_owner = str(profile.get("prompt_formatter", "unassigned")).removeprefix("optional:")
    if formatter_available and optional_owner == "unassigned":
        return _stopped("prompt_packet", "model_specific_formatter_unassigned")
    local_owner = "ai-film-studio:film-prompt-director"
    prompt_packet = {
        "schema_version": "ai-film-studio/PromptPacket/v1",
        "id": f"prompt_{shot_id.removeprefix('shot_')}",
        "shot_record_id": shot_id,
        "shot_record_sha256": shot_sha256,
        "model_profile_id": model_id,
        "model_profile_version": profile_version,
        "status": "delegated" if formatter_available else "draft",
        "format_owner": optional_owner if formatter_available else local_owner,
        "normalized_shot_record": {field: shot_record[field] for field in SHOT_PACKET_FIELDS},
        "compiled_prompt": "",
        "validator_result": {
            "status": "delegated" if formatter_available else "unrun",
            "validator": optional_owner if formatter_available else "ai-film-studio:local-record-validator",
            "evidence": [],
        },
        "source_references": [
            {"path": f"records/{shot_id}.json", "sha256": shot_sha256}
        ],
        "prompt_sha256": "",
        "external_action_policy": "approval-required",
    }
    return {
        "protocol": "film-prompt-director/model-neutral/v1",
        "status": "ready_for_optional_formatter" if formatter_available else "complete_model_neutral",
        "prompt_packet": prompt_packet,
        "formatter_handoff": None if formatter_available else {
            "requested_model": model_id,
            "missing_optional_formatter": optional_owner,
            "selected_surface_questions": ["surface", "version", "controls", "availability", "cost"],
            "validation_required": "Model-specific syntax and selected-surface controls remain unverified.",
        },
    }

def _stopped(packet_id: str, reason: str, **details: Any) -> Dict[str, Any]:
    return {"protocol":"film-advisor/v1","packet_id":packet_id,"status":"stopped","reason":reason,"details":details}

def _nonempty(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())

def _validate_packet(packet: Any) -> str | None:
    if not isinstance(packet, dict): return "packet_must_be_object"
    required = {"schema_version","packet_id","activation","route","project_root","production_contract","requested_actions"}
    if set(packet) != required: return "packet_keys_invalid"
    if packet.get("schema_version") != "ai-film-studio/film-advisor-packet/v1": return "invalid_schema_version"
    if not isinstance(packet.get("packet_id"), str) or not re.fullmatch(r"film_packet_[a-z0-9_]+", packet["packet_id"]): return "invalid_packet_id"
    activation = packet.get("activation")
    if not isinstance(activation, dict) or set(activation) != {"mode","invocation"} or activation.get("mode") != "explicit" or activation.get("invocation") != "film-advisor": return "activation_not_explicit"
    if packet.get("route") not in ROUTES: return "unknown_route"
    if not _nonempty(packet.get("project_root")): return "invalid_project_root"
    contract = packet.get("production_contract")
    if not isinstance(contract, dict) or set(contract) != {"status","film_brief_id","film_brief_sha256"}: return "invalid_production_contract"
    if contract.get("status") not in {"draft","approved"}: return "invalid_production_contract"
    if packet["route"] not in {"concept","brief"} and (contract.get("status") != "approved" or not re.fullmatch(r"[a-f0-9]{64}", str(contract.get("film_brief_sha256", "")))): return "production_contract_not_approved"
    actions = packet.get("requested_actions")
    if not isinstance(actions, list): return "invalid_requested_actions"
    for action in actions:
        if not isinstance(action, dict) or set(action) != {"type","target","approval"}: return "invalid_action"
        if action.get("type") not in ALL_ACTIONS or not _nonempty(action.get("target")): return "invalid_action"
        approval = action.get("approval")
        if not isinstance(approval, dict) or set(approval) != {"status","id","action_type","target","evidence"}: return "invalid_approval"
        if approval.get("status") not in {"not_granted","approved"} or not isinstance(approval.get("evidence"), dict): return "invalid_approval"
    return None

def _approval_error(action: Dict[str, Any]) -> str | None:
    action_type, target, approval = action["type"], action["target"], action["approval"]
    if approval.get("status") != "approved" or not _nonempty(approval.get("id")): return "approval_not_granted"
    if approval.get("action_type") != action_type or approval.get("target") != target: return "approval_scope_mismatch"
    evidence = approval["evidence"]
    for field in REQUIRED_EVIDENCE[action_type]:
        value = evidence.get(field)
        if isinstance(value, list):
            if not value: return f"missing_{field}"
        elif not _nonempty(value): return f"missing_{field}"
    return None

def evaluate_packet(packet: Dict[str, Any]) -> Dict[str, Any]:
    """Return a route or a stop. This function never performs an external action."""
    packet_id = str(packet.get("packet_id", "unknown")) if isinstance(packet, dict) else "unknown"
    error = _validate_packet(packet)
    if error: return _stopped(packet_id, error)
    for action in packet["requested_actions"]:
        if action["type"] in EXTERNAL_ACTIONS:
            approval_error = _approval_error(action)
            if approval_error:
                return _stopped(packet_id,"external_action_requires_approval",action_type=action["type"],target=action["target"],approval_error=approval_error,required_evidence=list(REQUIRED_EVIDENCE[action["type"]]))
    return {"protocol":"film-advisor/v1","packet_id":packet_id,"status":"accepted","route":packet["route"],"skill":ROUTES[packet["route"]],"authority":["route","request_record","validate","stop_on_gate"],"prohibited":sorted(EXTERNAL_ACTIONS)}

def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("usage: film_advisor.py PACKET.json", file=sys.stderr); return 2
    try: packet = json.loads(Path(argv[1]).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        print(f"film-advisor: unable to read packet: {error}", file=sys.stderr); return 2
    print(json.dumps(evaluate_packet(packet), indent=2, sort_keys=True)); return 0

if __name__ == "__main__": raise SystemExit(main(sys.argv))
