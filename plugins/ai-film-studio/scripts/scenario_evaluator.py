#!/usr/bin/env python3
"""Deterministic fixture-policy evaluator for AI Film Studio scenarios."""

from __future__ import annotations

from typing import Any, Dict

POLICY = {
    "failure_geography_drift": ("hold", {"AssetRecord", "ShotRecord", "AuditPacket"}),
    "failure_identity_drift": ("hold", {"AssetRecord", "AuditPacket", "FixPacket"}),
    "failure_implicit_activation": ("stopped", {"TaskPacket"}),
    "failure_stale_reference": ("failed", {"ShotRecord", "PromptPacket", "VerificationPacket"}),
    "failure_unapproved_paid_generation": ("stopped", {"PromptPacket", "GenerationAttempt"}),
    "failure_unverified_model_claim": ("blocked", {"PromptPacket", "VerificationPacket"}),
    "e2e_30_second_proof_of_concept": ("planning-ready", {"FilmBrief", "ProductionPlan", "AssetRecord", "ShotRecord", "PromptPacket", "GenerationAttempt", "VerificationPacket"}),
    "e2e_dialogue_short": ("dialogue planning passes", {"FilmBrief", "ProductionPlan", "AssetRecord", "ShotRecord", "PromptPacket", "AuditPacket", "FixPacket", "VerificationPacket"}),
    "e2e_simulated_95_minute_feature_plan": ("simulation only", {"FilmBrief", "ProductionPlan", "AssetRecord", "TaskPacket", "ShotRecord", "PromptPacket", "GenerationAttempt", "AuditPacket", "FixPacket", "VerificationPacket", "DeliveryReceipt"}),
}

def evaluate_scenario(fixture: Dict[str, Any]) -> Dict[str, Any]:
    fixture_id = fixture.get("id")
    if fixture_id not in POLICY:
        return {"status":"invalid","reason":"unknown_fixture"}
    expected_prefix, required_records = POLICY[fixture_id]
    chain = set(fixture.get("record_chain", []))
    if not required_records.issubset(chain):
        return {"status":"invalid","reason":"record_chain_incomplete"}
    if not fixture.get("evidence"):
        return {"status":"invalid","reason":"evidence_missing"}
    expected_status = fixture.get("expected_status", "")
    if not isinstance(expected_status, str) or not expected_status.startswith(expected_prefix):
        return {"status":"invalid","reason":"expected_status_mismatch"}
    return {"status":"passed","expected_status":expected_status}
