from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "validate_release_evidence.py"
SPEC = importlib.util.spec_from_file_location("validate_release_evidence", SCRIPT)
assert SPEC and SPEC.loader
validator = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(validator)


class ReleaseEvidenceValidationTests(unittest.TestCase):
    profiles = {"profiles": {"test-profile": {"required_checks": ["bundle-validation"]}}}

    def make_repository(self, root: Path) -> tuple[Path, str]:
        source = root / "source"
        source.mkdir()
        subprocess.run(["git", "init", "--quiet", str(source)], check=True)
        subprocess.run(["git", "-C", str(source), "config", "user.email", "test@example.invalid"], check=True)
        subprocess.run(["git", "-C", str(source), "config", "user.name", "Release Evidence Test"], check=True)
        (source / "release.txt").write_text("release\n", encoding="utf-8")
        subprocess.run(["git", "-C", str(source), "add", "release.txt"], check=True)
        subprocess.run(["git", "-C", str(source), "commit", "--quiet", "-m", "release"], check=True)
        commit = subprocess.run(
            ["git", "-C", str(source), "rev-parse", "HEAD"], check=True, capture_output=True, text=True
        ).stdout.strip()
        return source, commit

    @staticmethod
    def write_json(path: Path, value: dict) -> str:
        path.write_text(json.dumps(value, sort_keys=True), encoding="utf-8")
        return hashlib.sha256(path.read_bytes()).hexdigest()

    def valid_receipt(self, root: Path) -> tuple[dict, Path]:
        source, commit = self.make_repository(root)
        stdout = root / "stdout.txt"
        stderr = root / "stderr.txt"
        stdout.write_text('{"valid": true}\n', encoding="utf-8")
        stderr.write_text("", encoding="utf-8")
        record_path = root / "command-evidence.json"
        record_hash = self.write_json(
            record_path,
            {
                "schema_version": 1,
                "record_type": "CapabilityReleaseEvidence",
                "commit": commit,
                "kind": "command-result",
                "value": "bundle validation passed",
                "command": "python3 verify_bundle.py",
                "exit_code": 0,
                "stdout_path": str(stdout),
                "stdout_sha256": hashlib.sha256(stdout.read_bytes()).hexdigest(),
                "stderr_path": str(stderr),
                "stderr_sha256": hashlib.sha256(stderr.read_bytes()).hexdigest(),
            },
        )
        receipt = {
            "schema_version": 1,
            "capability": "test-capability",
            "profile": "test-profile",
            "source": str(source),
            "version": "0.1.0",
            "commit": commit,
            "checks": [
                {
                    "id": "bundle-validation",
                    "status": "passed",
                    "evidence": {
                        "kind": "command-result",
                        "record_path": str(record_path),
                        "record_sha256": record_hash,
                    },
                }
            ],
        }
        return receipt, record_path

    def test_hash_bound_record_at_exact_commit_passes(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            receipt, _ = self.valid_receipt(Path(temp))
            self.assertEqual(validator.validate(self.profiles, receipt), [])

    def test_fabricated_receipt_fields_cannot_override_failed_record(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            receipt, record_path = self.valid_receipt(Path(temp))
            record = json.loads(record_path.read_text(encoding="utf-8"))
            record["exit_code"] = 1
            record["verified"] = True
            receipt["checks"][0]["evidence"].update(
                {"verified": True, "exit_code": 0, "value": "fabricated pass"}
            )
            receipt["checks"][0]["evidence"]["record_sha256"] = self.write_json(record_path, record)
            errors = validator.validate(self.profiles, receipt)
            self.assertTrue(any("may reference only a bound record" in error for error in errors), errors)
            self.assertIn("bundle-validation: evidence record may not use a caller-supplied verified flag", errors)
            self.assertIn("bundle-validation: command-result record exit_code must be 0", errors)

    def test_tampered_record_hash_cannot_be_overridden_by_receipt_fields(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            receipt, record_path = self.valid_receipt(Path(temp))
            record = json.loads(record_path.read_text(encoding="utf-8"))
            record["value"] = "fabricated pass"
            record_path.write_text(json.dumps(record, sort_keys=True), encoding="utf-8")
            receipt["checks"][0]["evidence"].update(
                {"verified": True, "exit_code": 0, "value": "fabricated pass"}
            )
            errors = validator.validate(self.profiles, receipt)
            self.assertTrue(any("record_sha256 does not match" in error for error in errors), errors)
            self.assertTrue(any("may reference only a bound record" in error for error in errors), errors)


if __name__ == "__main__":
    unittest.main()
