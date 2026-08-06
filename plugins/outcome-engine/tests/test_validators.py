import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


PLUGIN_ROOT = Path(__file__).resolve().parents[1]


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


brief_validator = load_module(
    "brief_validator",
    PLUGIN_ROOT
    / "skills"
    / "to-outcome-brief"
    / "scripts"
    / "validate_outcome_brief.py",
)
slices_validator = load_module(
    "slices_validator",
    PLUGIN_ROOT
    / "skills"
    / "to-action-slices"
    / "scripts"
    / "validate_action_slices.py",
)


VALID_BRIEF = """# Outcome Brief
## Outcome
Create a cited memo.
## Audience or user
The operating team.
## Success evidence
Each recommendation cites a source.
## Constraints
Use supplied research.
## Decisions
Use one recommendation.
## Blockers
None.
## Out of scope
External publishing.
## Next action
Draft the evidence table.
"""


def write_temp(content: str) -> Path:
    handle = tempfile.NamedTemporaryFile("w", delete=False)
    with handle:
        handle.write(content)
    return Path(handle.name)


class ValidatorTests(unittest.TestCase):
    def test_brief_validator_accepts_complete_brief(self):
        path = write_temp(VALID_BRIEF)
        try:
            self.assertEqual(brief_validator.validate(path), [])
        finally:
            path.unlink(missing_ok=True)

    def test_brief_validator_rejects_placeholder(self):
        path = write_temp(VALID_BRIEF + "\nTODO: add detail\n")
        try:
            self.assertTrue(brief_validator.validate(path))
        finally:
            path.unlink(missing_ok=True)

    def test_slice_validator_rejects_cycle(self):
        payload = {
            "slices": [
                {
                    "id": "S1",
                    "title": "First",
                    "outcome": "First result",
                    "proof": "First proof",
                    "acceptance_checks": ["First passes"],
                    "blocked_by": ["S2"],
                    "boundaries": {"in_scope": [], "out_of_scope": []},
                },
                {
                    "id": "S2",
                    "title": "Second",
                    "outcome": "Second result",
                    "proof": "Second proof",
                    "acceptance_checks": ["Second passes"],
                    "blocked_by": ["S1"],
                    "boundaries": {"in_scope": [], "out_of_scope": []},
                },
            ]
        }
        path = write_temp(json.dumps(payload))
        try:
            self.assertIn(
                "Dependency graph contains a cycle", slices_validator.validate(path)
            )
        finally:
            path.unlink(missing_ok=True)


if __name__ == "__main__":
    unittest.main()
