import json
import subprocess
import tempfile
import unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1] / "skills/session-compounder"
class SessionPermissionsTests(unittest.TestCase):
    def test_unknown_permission_can_be_recorded_but_never_created(self):
        data = json.loads((ROOT / "assets/output-template.json").read_text())
        data["decisions"][0].update(reuse_permission="unknown", allowed_audience=[])
        data["recommended_outputs"][0]["permission_check"] = "unresolved"
        data["unresolved_gaps"] = [{"id":"gap-1","affected_source_item_ids":["decision-1"],"blocked_candidate_output_ids":["candidate-1"],"resolution_needed":"Obtain audience-specific permission."}]
        outputs = data["derivative_outputs"]
        data["derivative_outputs"] = []
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "record.json"
            p.write_text(json.dumps(data))
            result = subprocess.run(["python3", str(ROOT / "scripts/validate_output.py"), str(p)], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stdout)
            data["derivative_outputs"] = outputs
            p.write_text(json.dumps(data))
            result = subprocess.run(["python3", str(ROOT / "scripts/validate_output.py"), str(p)], capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
