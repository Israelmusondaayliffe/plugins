#!/usr/bin/env python3
"""Unit tests for Guide Production Studio validators."""

from __future__ import annotations

import copy
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
ROUTER = ROOT / "skills" / "guide-production-router"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


contract_validator = load_module(
    "contract_validator", ROUTER / "scripts" / "validate_guide_contract.py"
)
review_validator = load_module(
    "review_validator", ROUTER / "scripts" / "validate_guide_review.py"
)
public_validator = load_module(
    "public_validator", ROUTER / "scripts" / "validate_public_guide.py"
)


def valid_contract() -> dict:
    return {
        "schema_version": "guide-production-studio/guide-contract/v1",
        "id": "guide_example_v1",
        "title": "A Useful Guide",
        "audience": {
            "primary": "Creative practitioners",
            "starting_point": "New to the method",
            "expert_value": "Decision rules and source links",
        },
        "reader_job": "Use one controlled comparison to improve an image",
        "outcome": "A supported keep or revise decision",
        "format": "layered-page",
        "visual_requirement": "required",
        "sources": [{
            "id": "src1",
            "title": "Owned comparison",
            "location": "owned asset set",
            "classification": "user-owned",
            "authority": "Direct evidence",
            "permitted_public_use": True,
            "required_attribution": False,
            "current_verification": "Inspected 2026-08-24",
        }],
        "concepts": [{
            "term": "protected element",
            "plain_definition": "A visible part that must not change during the repair.",
            "source_ids": ["src1"],
        }],
        "evidence": [{
            "id": "ev1",
            "claim_or_method": "Compare the parent and revision at the same size.",
            "source_ids": ["src1"],
            "status": "observed",
            "public_use": True,
        }],
        "examples": [{
            "id": "ex1",
            "evidence_ids": ["ev1"],
            "kind": "real",
            "run_status": "observed",
            "public_use": True,
        }],
        "visuals": [{
            "id": "vis1",
            "kind": "comparison",
            "source_ids": ["src1"],
            "inspection_job": "Compare the protected subject and changed lighting.",
            "public_use": True,
        }],
        "architecture": {
            "mode": "layered-page",
            "pages": [{
                "id": "page1",
                "title": "Controlled image repair",
                "reader_job": "Make one supported repair decision",
            }],
            "components": [{
                "id": "comp1",
                "kind": "comparison",
                "reader_problem": "The reader cannot tell what changed.",
                "action_enabled": "Inspect parent and revision together.",
                "source_ids": ["src1"],
                "why_it_belongs": "The judgment is visual.",
                "required": True,
            }],
        },
        "boundaries": {
            "public_allowed": ["Owned comparison"],
            "private_excluded": ["Private paths"],
            "unsupported_forbidden": ["Unobserved result claims"],
        },
        "publication": {"authorized": False, "destination": None},
        "acceptance": {
            "human_owner": "Human reviewer",
            "required_gates": contract_validator.GATES,
            "cold_reader_required_before_scale": True,
            "bulk_scale_allowed": False,
        },
        "limits": {"max_internal_support_artifacts": 2, "max_repair_waves": 1},
    }


def valid_ready_review() -> dict:
    return {
        "schema_version": "guide-production-studio/guide-review/v1",
        "guide_contract_id": "guide_example_v1",
        "producer_id": "producer-a",
        "reviewer_id": "reviewer-b",
        "status": "ready_for_human_review",
        "gates": [
            {"id": gate, "passed": True, "evidence": f"Fresh evidence for {gate}."}
            for gate in review_validator.GATES
        ],
        "critical_failures": [],
        "first_confusion_point": None,
        "cold_reader": {"observed": False, "completed_first_action": False, "evidence": None},
        "human_approval": {
            "owner": "Human reviewer",
            "confirmed": False,
            "approved_at": None,
            "evidence": None,
        },
        "next_action": "Send the benchmark to the named human owner.",
    }


class ValidatorTests(unittest.TestCase):
    def test_valid_contract_passes(self):
        self.assertEqual(contract_validator.validate(valid_contract()), [])

    def test_contract_rejects_fake_scale_and_missing_visual(self):
        candidate = valid_contract()
        candidate["acceptance"]["bulk_scale_allowed"] = True
        candidate["visuals"] = []
        errors = contract_validator.validate(candidate)
        self.assertTrue(any("bulk scale" in item for item in errors))
        self.assertTrue(any("visual evidence" in item for item in errors))

    def test_ready_review_requires_independence(self):
        review = valid_ready_review()
        review["reviewer_id"] = review["producer_id"]
        self.assertTrue(any("different" in item for item in review_validator.validate(review)))

    def test_human_approval_requires_cold_reader(self):
        review = valid_ready_review()
        review["status"] = "human_approved"
        review["human_approval"] = {
            "owner": "Human reviewer",
            "confirmed": True,
            "approved_at": "2026-08-24T16:00:00-04:00",
            "evidence": "Explicit review approval.",
        }
        self.assertTrue(any("cold-reader" in item for item in review_validator.validate(review, True)))

    def test_public_scan_catches_internal_language(self):
        findings = public_validator.scan("The validator passed. Source: /Users/example/private.md")
        labels = {item["type"] for item in findings}
        self.assertIn("local user path", labels)
        self.assertIn("internal release evidence", labels)

    def test_public_scan_allows_normal_guide_text(self):
        self.assertEqual(public_validator.scan("Compare the parent image and revision at the same size."), [])


if __name__ == "__main__":
    unittest.main()
