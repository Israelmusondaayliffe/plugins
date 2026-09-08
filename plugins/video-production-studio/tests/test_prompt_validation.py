import importlib.util
from pathlib import Path
import unittest
p=Path(__file__).resolve().parents[1]/"skills/video-prompt-builder/scripts/validate_video_prompt.py"
spec=importlib.util.spec_from_file_location("video_prompt_validator",p)
v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)
class PromptValidationTests(unittest.TestCase):
 def test_generic_model_does_not_require_seedance_fields(self):
  self.assertEqual(v.validate_generic("```text\nA single wide shot in natural light.\n```"),[])
 def test_timeline_gap_and_incomplete_duration_are_rejected(self):
  errors=[];v.check_timeline("Duration: 10 seconds. [0-3] End state: still. [4-9] End state: dark.",errors)
  self.assertTrue(any("gap" in e for e in errors));self.assertTrue(any("duration" in e for e in errors))
 def test_reference_needs_both_positive_and_negative_scope(self):
  errors=[];v.check_references("@Image1 defines the face.",errors);self.assertTrue(errors)
  errors=[];v.check_references("@Image1 defines only the face; do not use its background.",errors);self.assertEqual(errors,[])
if __name__=="__main__":unittest.main()
