"""Tests for scripts/blind_pair.py: the map never reaches critic-visible
output, seed determinism, neutral copies, and metadata stripping."""

import json
import os
import subprocess
import sys
import tempfile
import unittest

SCRIPT = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "scripts", "blind_pair.py")

OURS_BODY = "Ours body line, the candidate argument."
REF_BODY = "Reference body line, the comparator argument."


def run_script(*args):
    return subprocess.run(
        [sys.executable, SCRIPT] + list(args),
        capture_output=True, text=True)


class BlindPairTest(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.gauntlet = os.path.join(self.tmp.name, ".gauntlet")
        self.run_id = "20260729-1200-demo"
        self.run_dir = os.path.join(self.gauntlet, "runs", self.run_id)
        os.makedirs(self.run_dir)
        src = os.path.join(self.tmp.name, "src")
        os.makedirs(src)
        self.ours = os.path.join(src, "ours-draft.md")
        with open(self.ours, "w", encoding="utf-8") as handle:
            handle.write("---\nauthor: Israel\ndate: 2026-07-29\n---\n"
                         + OURS_BODY + "\n")
        self.reference = os.path.join(src, "reference-sample.md")
        with open(self.reference, "w", encoding="utf-8") as handle:
            handle.write("Source: bar/refs/reference-openings.md\n"
                         + REF_BODY + "\n")

    def pair(self, run_dir=None, seed="42", round_number="1"):
        args = ["--run-dir", run_dir or self.run_dir,
                "--piece", "opening-section",
                "--round", round_number,
                "--ours", self.ours,
                "--reference", self.reference]
        if seed is not None:
            args += ["--seed", seed]
        return run_script(*args)

    def sealed_map_path(self, round_label="001"):
        return os.path.join(self.gauntlet, "sealed", self.run_id,
                            "opening-section", round_label, "map.json")

    def read_map(self, round_label="001"):
        with open(self.sealed_map_path(round_label), encoding="utf-8") as handle:
            return json.load(handle)

    def test_neutral_paths_printed_and_files_created(self):
        proc = self.pair()
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        out = json.loads(proc.stdout)
        self.assertEqual(sorted(out.keys()), ["item_a", "item_b"])
        self.assertTrue(os.path.basename(out["item_a"]).startswith("item-a"))
        self.assertTrue(os.path.basename(out["item_b"]).startswith("item-b"))
        for path in out.values():
            self.assertTrue(os.path.isfile(path))
            # Neutral copies live inside the run directory.
            self.assertTrue(path.startswith(self.run_dir))

    def test_mapping_never_in_critic_visible_output(self):
        proc = self.pair()
        self.assertEqual(proc.returncode, 0)
        # Stdout carries no provenance: no source filenames, no label
        # mapping, no seed. Strip the random tempdir prefix first so its
        # characters cannot collide with the substring checks.
        sanitized = proc.stdout.replace(self.tmp.name, "<tmp>")
        self.assertNotIn("ours-draft", sanitized)
        self.assertNotIn("reference-sample", sanitized)
        self.assertNotIn("ours_label", sanitized)
        self.assertNotIn("seed", sanitized)
        self.assertNotIn("42", sanitized)
        self.assertNotIn("map.json", sanitized)
        # No map file anywhere under runs/, where critic paths live.
        for root, _dirs, files in os.walk(self.run_dir):
            self.assertNotIn("map.json", files,
                             "sealed map leaked into the run directory")
        # The sealed map exists outside runs/.
        self.assertTrue(os.path.isfile(self.sealed_map_path()))
        # The blind dir holds only the two neutral items.
        out = json.loads(proc.stdout)
        blind_dir = os.path.dirname(out["item_a"])
        self.assertEqual(sorted(os.listdir(blind_dir)),
                         ["item-a.md", "item-b.md"])

    def test_sealed_map_records_seed_and_mapping(self):
        proc = self.pair()
        self.assertEqual(proc.returncode, 0)
        mapping = json.loads(json.dumps(self.read_map()))
        self.assertEqual(sorted(mapping.keys()),
                         ["a", "b", "ours_label", "seed"])
        self.assertEqual(mapping["seed"], 42)
        self.assertIn(mapping["ours_label"], ("A", "B"))
        sources = {mapping["a"], mapping["b"]}
        self.assertEqual(sources, {self.ours, self.reference})
        ours_slot = "a" if mapping["ours_label"] == "A" else "b"
        self.assertEqual(mapping[ours_slot], self.ours)

    def test_neutral_copies_match_the_sealed_mapping(self):
        proc = self.pair()
        self.assertEqual(proc.returncode, 0)
        out = json.loads(proc.stdout)
        mapping = self.read_map()
        with open(out["item_a"], encoding="utf-8") as handle:
            a_text = handle.read()
        with open(out["item_b"], encoding="utf-8") as handle:
            b_text = handle.read()
        if mapping["ours_label"] == "A":
            self.assertIn(OURS_BODY, a_text)
            self.assertIn(REF_BODY, b_text)
        else:
            self.assertIn(REF_BODY, a_text)
            self.assertIn(OURS_BODY, b_text)

    def test_metadata_lines_are_stripped(self):
        proc = self.pair()
        self.assertEqual(proc.returncode, 0)
        out = json.loads(proc.stdout)
        for path in out.values():
            with open(path, encoding="utf-8") as handle:
                text = handle.read()
            self.assertNotIn("author:", text)
            self.assertNotIn("Israel", text)
            self.assertNotIn("Source:", text)
            self.assertNotIn("---", text)
        # Bodies survive the strip.
        combined = ""
        for path in out.values():
            with open(path, encoding="utf-8") as handle:
                combined += handle.read()
        self.assertIn(OURS_BODY, combined)
        self.assertIn(REF_BODY, combined)

    def test_seed_determinism(self):
        proc_one = self.pair()
        self.assertEqual(proc_one.returncode, 0)
        first = self.read_map()
        # Fresh run directory, same seed: identical assignment.
        other_run = os.path.join(self.gauntlet, "runs", "20260729-1300-demo2")
        os.makedirs(other_run)
        proc_two = self.pair(run_dir=other_run)
        self.assertEqual(proc_two.returncode, 0)
        with open(os.path.join(self.gauntlet, "sealed", "20260729-1300-demo2",
                               "opening-section", "001", "map.json"),
                  encoding="utf-8") as handle:
            second = json.load(handle)
        self.assertEqual(first["ours_label"], second["ours_label"])
        self.assertEqual(first["seed"], second["seed"])

    def test_seed_generated_when_omitted(self):
        proc = self.pair(seed=None)
        self.assertEqual(proc.returncode, 0)
        mapping = self.read_map()
        self.assertIsInstance(mapping["seed"], int)

    def test_missing_artifact_is_a_validation_failure(self):
        self.ours = os.path.join(self.tmp.name, "src", "does-not-exist.md")
        proc = self.pair()
        self.assertEqual(proc.returncode, 1)
        self.assertIn("error", json.loads(proc.stdout))


if __name__ == "__main__":
    unittest.main()
