from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skills" / "sol-advisor" / "scripts" / "activation.py"
SPEC = importlib.util.spec_from_file_location("sol_advisor_activation", SCRIPT)
assert SPEC and SPEC.loader
activation = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(activation)


class SolAdvisorRoutingTests(unittest.TestCase):
    def test_direct_imperative_activates(self) -> None:
        self.assertTrue(activation.is_explicit_activation("Use Sol Advisor for this bounded task."))

    def test_incidental_mention_does_not_activate(self) -> None:
        self.assertFalse(activation.is_explicit_activation("I read about Sol Advisor yesterday."))

    def test_quoted_mention_does_not_activate(self) -> None:
        self.assertFalse(activation.is_explicit_activation('The guide contains the phrase "use Sol Advisor".'))

    def test_conditional_mention_does_not_activate(self) -> None:
        self.assertFalse(activation.is_explicit_activation("If we use Sol Advisor, what will happen?"))

    def test_negated_mention_does_not_activate(self) -> None:
        self.assertFalse(activation.is_explicit_activation("Do not use Sol Advisor for this task."))

    def test_revoked_activation_does_not_activate(self) -> None:
        self.assertFalse(activation.is_explicit_activation("Use Sol Advisor. Actually, no, do not activate it."))

    def test_codex_metadata_disables_implicit_invocation(self) -> None:
        metadata = ROOT / "skills" / "sol-advisor" / "agents" / "openai.yaml"
        self.assertIn("allow_implicit_invocation: false", metadata.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
