"""Unit tests for scripts/claim_audit.py. Always run with --skip-network."""

import json
import os
import subprocess
import sys
import tempfile
import unittest

PLUGIN_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPT = os.path.join(PLUGIN_ROOT, "scripts", "claim_audit.py")


def run_script(*args):
    return subprocess.run(
        [sys.executable, SCRIPT] + list(args),
        capture_output=True, text=True,
    )


def checks(payload):
    return {f["check"] for f in payload["findings"]}


def row(claim, support_type, source, quote="", location="drafts/out.md:L1"):
    return {
        "claim_text": claim,
        "location": location,
        "support_type": support_type,
        "source": source,
        "supporting_quote": quote,
        "confidence": "high",
    }


class ClaimAuditTest(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.run_dir = os.path.join(
            self.tmp.name, ".gauntlet", "runs", "20260729-1200-test")
        os.makedirs(os.path.join(self.run_dir, "claims", "p1"))

    def tearDown(self):
        self.tmp.cleanup()

    def write_ledger(self, rows, piece="p1"):
        path = os.path.join(self.run_dir, "claims", piece, "ledger.json")
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(rows, fh)

    def write_source(self, rel, content):
        path = os.path.join(self.run_dir, rel)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(content)

    def audit(self, piece="p1"):
        proc = run_script("--run-dir", self.run_dir, "--piece", piece,
                          "--skip-network")
        return proc, json.loads(proc.stdout)

    def test_supported_ledger_passes_and_writes_audit(self):
        self.write_source(
            "sources/report.md",
            "Findings: coverage increased from 41% to 58% in the sample.\n")
        self.write_ledger([
            row("Coverage rose across the sample.", "primary",
                "sources/report.md",
                quote="coverage increased from 41% to 58%"),
            row("This matches the prior wave.", "own-analysis",
                "sources/report.md"),
        ])
        proc, payload = self.audit()
        self.assertEqual(proc.returncode, 0, proc.stdout)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["total_claims"], 2)
        self.assertEqual(payload["unsupported_count"], 0)
        self.assertEqual(payload["rows"][0]["reachability"], "reachable")
        self.assertIs(payload["rows"][0]["quote_present"], True)
        audit_path = os.path.join(
            self.run_dir, "claims", "p1", "audit.json")
        self.assertTrue(os.path.isfile(audit_path))
        with open(audit_path, "r", encoding="utf-8") as fh:
            written = json.load(fh)
        self.assertEqual(written["total_claims"], 2)

    def test_unsupported_row_exits_1(self):
        self.write_source("sources/report.md", "Real source text.\n")
        self.write_ledger([
            row("A supported claim.", "primary", "sources/report.md"),
            row("An invented statistic.", "unsupported", ""),
        ])
        proc, payload = self.audit()
        self.assertEqual(proc.returncode, 1, proc.stdout)
        self.assertFalse(payload["ok"])
        self.assertEqual(payload["unsupported_count"], 1)
        self.assertIn("unsupported-claim", checks(payload))

    def test_invalid_support_type_exits_1(self):
        self.write_ledger([
            row("A claim.", "vibes", "sources/report.md"),
        ])
        proc, payload = self.audit()
        self.assertEqual(proc.returncode, 1, proc.stdout)
        self.assertIn("invalid-support-type", checks(payload))
        self.assertFalse(payload["rows"][0]["support_type_valid"])

    def test_unreachable_file_source_reported(self):
        self.write_ledger([
            row("A claim citing a missing file.", "primary",
                "sources/missing.pdf#p12"),
        ])
        proc, payload = self.audit()
        # Reachability is reported for verifiers to act on; only
        # unsupported or invalid rows fail the audit itself.
        self.assertEqual(proc.returncode, 0, proc.stdout)
        self.assertEqual(payload["rows"][0]["reachability"], "unreachable")
        self.assertIn("source-unreachable", checks(payload))

    def test_url_source_skipped_without_network(self):
        self.write_ledger([
            row("A claim citing the web.", "secondary",
                "https://example.com/report"),
        ])
        proc, payload = self.audit()
        self.assertEqual(proc.returncode, 0, proc.stdout)
        self.assertEqual(payload["rows"][0]["reachability"],
                         "unchecked-network-skipped")
        self.assertFalse(payload["network_checked"])

    def test_quote_absent_from_source_reported(self):
        self.write_source("sources/report.md", "Nothing relevant here.\n")
        self.write_ledger([
            row("A claim.", "primary", "sources/report.md",
                quote="coverage increased from 41% to 58%"),
        ])
        proc, payload = self.audit()
        self.assertEqual(proc.returncode, 0, proc.stdout)
        self.assertIs(payload["rows"][0]["quote_present"], False)
        self.assertIn("quote-missing-from-source", checks(payload))

    def test_citation_ratio_and_concentration(self):
        self.write_source("sources/one.md", "Alpha.\n")
        self.write_ledger([
            row("c1", "primary", "sources/one.md"),
            row("c2", "secondary", "sources/one.md"),
            row("c3", "primary", "sources/one.md"),
            row("c4", "own-analysis", ""),
        ])
        proc, payload = self.audit()
        self.assertEqual(proc.returncode, 0, proc.stdout)
        self.assertAlmostEqual(payload["claim_to_citation_ratio"], 0.75)
        conc = payload["duplicate_source_concentration"]
        self.assertEqual(conc["distinct_sources"], 1)
        self.assertEqual(conc["top_source"], "sources/one.md")
        self.assertAlmostEqual(conc["top_source_share"], 0.75)

    def test_missing_ledger_exits_1(self):
        proc, payload = self.audit(piece="ghost")
        self.assertEqual(proc.returncode, 1, proc.stdout)
        self.assertIn("ledger-missing", checks(payload))

    def test_rows_wrapper_object_accepted(self):
        self.write_source("sources/report.md", "Real source text.\n")
        path = os.path.join(self.run_dir, "claims", "p1", "ledger.json")
        with open(path, "w", encoding="utf-8") as fh:
            json.dump({"rows": [
                row("A claim.", "primary", "sources/report.md"),
            ]}, fh)
        proc, payload = self.audit()
        self.assertEqual(proc.returncode, 0, proc.stdout)
        self.assertEqual(payload["total_claims"], 1)

    def test_missing_run_dir_is_usage_error(self):
        proc = run_script("--run-dir", os.path.join(self.tmp.name, "nope"),
                          "--piece", "p1", "--skip-network")
        self.assertEqual(proc.returncode, 2, proc.stdout)


if __name__ == "__main__":
    unittest.main()
