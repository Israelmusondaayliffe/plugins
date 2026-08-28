#!/usr/bin/env python3
"""Exercise Guide Production Studio's real capability-routing boundary."""

from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path


def load_evaluator(path: Path):
    spec = importlib.util.spec_from_file_location("guide_trigger_evaluator", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--results", type=Path)
    args = parser.parse_args()

    plugin_root = Path(__file__).resolve().parent.parent
    evaluator_path = plugin_root / "scripts" / "evaluate_guide_trigger.py"
    cases = json.loads((plugin_root / "tests" / "trigger-cases.json").read_text(encoding="utf-8"))["cases"]
    results: list[dict[str, object]] = []
    errors: list[str] = []

    if not evaluator_path.is_file():
        errors.append(f"local trigger evaluator not found: {evaluator_path}")
    else:
        evaluator = load_evaluator(evaluator_path)
        for case in cases:
            route = evaluator.evaluate(case["query"])
            selected = route["should_trigger"] is True
            passed = selected is case["should_trigger"]
            evidence = (
                f"local_should_trigger={selected} "
                f"expected_guide_route={case['should_trigger']} "
                f"signals={route['evidence']}"
            )
            results.append({"id": case["id"], "passed": passed, "evidence": evidence})
            if not passed:
                errors.append(f"{case['id']}: {evidence}")

    payload = {
        "schema_version": "guide-production-studio/trigger-results/v1",
        "results": results,
        "summary": {
            "total": len(results),
            "passed": sum(item["passed"] is True for item in results),
            "failed": sum(item["passed"] is False for item in results),
        },
        "errors": errors,
    }
    rendered = json.dumps(payload, indent=2) + "\n"
    if args.results:
        args.results.parent.mkdir(parents=True, exist_ok=True)
        args.results.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
