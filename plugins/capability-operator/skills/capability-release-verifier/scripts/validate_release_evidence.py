#!/usr/bin/env python3
"""Validate hash-bound capability-release evidence against one acceptance profile."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path


ALLOWED_STATUS = {"passed", "failed", "blocked"}
ALLOWED_EVIDENCE_KIND = {"command-result", "machine-result", "path", "url", "hash"}
EVIDENCE_REFERENCE_FIELDS = {"kind", "record_path", "record_sha256"}
COMMIT_PATTERN = re.compile(r"[0-9a-f]{40}")
SHA256_PATTERN = re.compile(r"[0-9a-f]{64}")


def load(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def release_head(receipt: dict, errors: list[str]) -> str | None:
    source = receipt.get("source")
    if not isinstance(source, str) or not source.strip():
        errors.append("source must be a non-empty string")
        return None
    source_path = Path(source).expanduser()
    if not source_path.is_absolute() or not source_path.is_dir():
        errors.append("source must be an existing absolute directory")
        return None
    completed = subprocess.run(
        ["git", "-C", str(source_path), "rev-parse", "HEAD"],
        capture_output=True,
        text=True,
        check=False,
    )
    if completed.returncode != 0:
        errors.append("source must resolve an exact Git HEAD commit")
        return None
    head = completed.stdout.strip()
    if not COMMIT_PATTERN.fullmatch(head):
        errors.append("source Git HEAD must be a 40-character lowercase commit")
        return None
    return head


def bound_record(
    evidence: dict, expected_commit: str | None, check_id: str, errors: list[str]
) -> tuple[str | None, dict | None]:
    unexpected = sorted(set(evidence) - EVIDENCE_REFERENCE_FIELDS)
    if unexpected:
        errors.append(f"{check_id}: receipt evidence may reference only a bound record, not {', '.join(unexpected)}")
    missing = sorted(EVIDENCE_REFERENCE_FIELDS - set(evidence))
    if missing:
        errors.append(f"{check_id}: receipt evidence is missing {', '.join(missing)}")
        return None, None
    kind = evidence.get("kind")
    if kind not in ALLOWED_EVIDENCE_KIND:
        errors.append(f"{check_id}: invalid evidence kind")
        return None, None
    record_path_value = evidence.get("record_path")
    if not isinstance(record_path_value, str):
        errors.append(f"{check_id}: record_path must be a string")
        return None, None
    record_path = Path(record_path_value).expanduser()
    if not record_path.is_absolute() or not record_path.is_file():
        errors.append(f"{check_id}: record_path must be an existing absolute file")
        return None, None
    record_hash = evidence.get("record_sha256")
    if not isinstance(record_hash, str) or not SHA256_PATTERN.fullmatch(record_hash):
        errors.append(f"{check_id}: record_sha256 must be a lowercase SHA-256")
        return None, None
    if sha256_file(record_path) != record_hash:
        errors.append(f"{check_id}: record_sha256 does not match record_path")
        return None, None
    try:
        record = load(record_path)
    except (OSError, json.JSONDecodeError, ValueError) as error:
        errors.append(f"{check_id}: invalid evidence record: {error}")
        return None, None
    if record.get("schema_version") != 1:
        errors.append(f"{check_id}: evidence record schema_version must be 1")
    if record.get("record_type") != "CapabilityReleaseEvidence":
        errors.append(f"{check_id}: evidence record type is invalid")
    if "verified" in record:
        errors.append(f"{check_id}: evidence record may not use a caller-supplied verified flag")
    if record.get("commit") != expected_commit:
        errors.append(f"{check_id}: evidence record commit does not match the exact source commit")
    if record.get("kind") != kind:
        errors.append(f"{check_id}: evidence record kind does not match the receipt reference")
    value = record.get("value")
    if not isinstance(value, str) or not value.strip():
        errors.append(f"{check_id}: evidence record value must be a non-empty string")
        return kind, record
    if kind == "command-result":
        command = record.get("command")
        if not isinstance(command, str) or not command.strip():
            errors.append(f"{check_id}: command-result record requires command")
        if record.get("exit_code") != 0:
            errors.append(f"{check_id}: command-result record exit_code must be 0")
        for stream in ("stdout", "stderr"):
            path_value = record.get(f"{stream}_path")
            digest = record.get(f"{stream}_sha256")
            if not isinstance(path_value, str):
                errors.append(f"{check_id}: command-result record requires {stream}_path")
                continue
            stream_path = Path(path_value).expanduser()
            if not stream_path.is_absolute() or not stream_path.is_file():
                errors.append(f"{check_id}: {stream}_path must be an existing absolute file")
                continue
            if not isinstance(digest, str) or not SHA256_PATTERN.fullmatch(digest):
                errors.append(f"{check_id}: {stream}_sha256 must be a lowercase SHA-256")
                continue
            if sha256_file(stream_path) != digest:
                errors.append(f"{check_id}: {stream}_sha256 does not match {stream}_path")
    elif kind == "machine-result":
        if not isinstance(record.get("result"), (dict, list)):
            errors.append(f"{check_id}: machine-result record requires structured result")
    elif kind == "path":
        value_path = Path(value).expanduser()
        if not value_path.is_absolute() or not value_path.exists():
            errors.append(f"{check_id}: evidence record path must exist and be absolute")
    elif kind == "url" and not value.startswith("https://"):
        errors.append(f"{check_id}: evidence record URL must use https")
    elif kind == "hash" and not SHA256_PATTERN.fullmatch(value):
        errors.append(f"{check_id}: evidence record hash must be a lowercase SHA-256")
    return kind, record


def validate(profiles: dict, receipt: dict) -> list[str]:
    errors: list[str] = []
    profile_name = receipt.get("profile")
    profile = profiles.get("profiles", {}).get(profile_name)
    if not profile:
        return [f"unknown profile: {profile_name}"]
    if receipt.get("schema_version") != 1:
        errors.append("receipt schema_version must be 1")
    for field in ("capability", "version"):
        if not isinstance(receipt.get(field), str) or not receipt[field].strip():
            errors.append(f"{field} must be a non-empty string")
    expected_commit = receipt.get("commit")
    if not isinstance(expected_commit, str) or not COMMIT_PATTERN.fullmatch(expected_commit):
        errors.append("commit must be a 40-character lowercase Git commit")
        expected_commit = None
    head = release_head(receipt, errors)
    if expected_commit is not None and head is not None and expected_commit != head:
        errors.append("receipt commit does not match the exact source Git HEAD commit")
    checks = receipt.get("checks")
    if not isinstance(checks, list):
        return errors + ["checks must be a list"]
    by_id: dict[str, dict] = {}
    for index, check in enumerate(checks):
        if not isinstance(check, dict):
            errors.append(f"checks[{index}] must be an object")
            continue
        check_id = check.get("id")
        if not isinstance(check_id, str) or not check_id:
            errors.append(f"checks[{index}].id must be a non-empty string")
            continue
        if check_id in by_id:
            errors.append(f"duplicate check: {check_id}")
        by_id[check_id] = check
        if check.get("status") not in ALLOWED_STATUS:
            errors.append(f"{check_id}: invalid status")
        evidence = check.get("evidence")
        if not isinstance(evidence, dict):
            errors.append(f"{check_id}: evidence must be an object")
            continue
        bound_record(evidence, expected_commit, check_id, errors)
    for check_id in profile.get("required_checks", []):
        check = by_id.get(check_id)
        if not check:
            errors.append(f"missing required check: {check_id}")
        elif check.get("status") != "passed":
            errors.append(f"required check did not pass: {check_id}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--profiles", type=Path, required=True)
    parser.add_argument("--receipt", type=Path, required=True)
    args = parser.parse_args()
    try:
        profiles = load(args.profiles)
        receipt = load(args.receipt)
        errors = validate(profiles, receipt)
    except (OSError, json.JSONDecodeError, ValueError) as error:
        errors = [str(error)]
        receipt = {}
    result = {
        "valid": not errors,
        "capability": receipt.get("capability"),
        "profile": receipt.get("profile"),
        "errors": errors,
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
