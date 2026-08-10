from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import tempfile
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "harnessctl.py"
SPEC = importlib.util.spec_from_file_location("harnessctl", SCRIPT)
assert SPEC and SPEC.loader
harnessctl = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(harnessctl)


class HarnessCtlTests(unittest.TestCase):
    def test_profile_validation(self) -> None:
        harnessctl.validate_profile({"schema_version": 1, "user": {}, "scope": {}, "decisions": []})
        with self.assertRaises(harnessctl.HarnessError):
            harnessctl.validate_profile({"schema_version": 1})

    def test_config_audit_redacts_values(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            config = Path(temp) / "config.toml"
            config.write_text('[mcp_servers.example]\napi_token = "do-not-record"\nenabled = true\n', encoding="utf-8")
            result = harnessctl.parse_config_keys(config)
            rendered = json.dumps(result)
            self.assertNotIn("do-not-record", rendered)
            self.assertIn("redacted-sensitive-key", result["keys"])
            self.assertIn("enabled", result["keys"])

    def test_plugin_inventory_reads_registry_and_nested_cache(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            home = Path(temp)
            registry = home / "plugins" / "installed_plugins.json"
            registry.parent.mkdir(parents=True)
            registry.write_text(
                json.dumps(
                    {
                        "version": 2,
                        "plugins": {
                            "agent-ops@israel-plugins": [
                                {"scope": "user", "installPath": "/x/agent-ops/0.5.0", "version": "0.5.0"}
                            ]
                        },
                    }
                ),
                encoding="utf-8",
            )
            installed = harnessctl.installed_plugin_inventory(home)
            self.assertEqual(
                [(item["name"], item["marketplace"], item["version"]) for item in installed],
                [("agent-ops", "israel-plugins", "0.5.0")],
            )

            nested = home / "plugins" / "cache" / "israel-plugins" / "agent-ops" / "0.5.0" / ".claude-plugin"
            nested.mkdir(parents=True)
            (nested / "plugin.json").write_text(json.dumps({"name": "agent-ops", "version": "0.5.0"}), encoding="utf-8")
            scanned = harnessctl.directory_plugin_inventory(home / "plugins" / "cache")
            self.assertEqual([(item["name"], item["version"]) for item in scanned], [("agent-ops", "0.5.0")])

    def test_dry_run_apply_and_rollback(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "workspace"
            root.mkdir()
            existing = root / "existing.md"
            existing.write_text("before\n", encoding="utf-8")
            created = root / "new.md"
            plan = {
                "schema_version": 1,
                "run_id": "test-run",
                "allowed_roots": [str(root)],
                "approval_groups": ["workspace"],
                "operations": [
                    {
                        "id": "update-existing",
                        "action": "update",
                        "target": str(existing),
                        "content": "after\n",
                        "expected_sha256": harnessctl.sha256_file(existing),
                        "approval_group": "workspace",
                    },
                    {
                        "id": "create-new",
                        "action": "create",
                        "target": str(created),
                        "content": "new\n",
                        "expected_sha256": None,
                        "approval_group": "workspace",
                    },
                ],
            }
            dry_receipt = root / "dry.json"
            harnessctl.apply_plan(plan, "dry-run", {"workspace"}, dry_receipt)
            self.assertEqual(existing.read_text(encoding="utf-8"), "before\n")
            self.assertFalse(created.exists())

            backup_dir = root / "backups"
            manifest_path = root / "manifest.json"
            apply_receipt = root / "apply.json"
            harnessctl.apply_plan(plan, "apply", {"workspace"}, apply_receipt, backup_dir, manifest_path)
            self.assertEqual(existing.read_text(encoding="utf-8"), "after\n")
            self.assertEqual(created.read_text(encoding="utf-8"), "new\n")

            rollback_receipt = root / "rollback.json"
            harnessctl.rollback_manifest(harnessctl.load_json(manifest_path), rollback_receipt)
            self.assertEqual(existing.read_text(encoding="utf-8"), "before\n")
            self.assertFalse(created.exists())

    def test_update_rejects_hash_drift(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            target = root / "file.md"
            target.write_text("current\n", encoding="utf-8")
            plan = {
                "schema_version": 1,
                "run_id": "drift",
                "allowed_roots": [str(root)],
                "approval_groups": ["global"],
                "operations": [
                    {
                        "id": "drifted",
                        "action": "update",
                        "target": str(target),
                        "content": "changed\n",
                        "expected_sha256": "0" * 64,
                        "approval_group": "global",
                    }
                ],
            }
            with self.assertRaises(harnessctl.HarnessError):
                harnessctl.apply_plan(plan, "dry-run", {"global"}, root / "receipt.json")

    def test_rejects_target_outside_root(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            parent = Path(temp)
            root = parent / "allowed"
            root.mkdir()
            target = parent / "outside.md"
            with self.assertRaises(harnessctl.HarnessError):
                harnessctl.check_target(target, [root])

    def test_rejects_symlink_escape(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            parent = Path(temp)
            root = parent / "allowed"
            outside = parent / "outside"
            root.mkdir()
            outside.mkdir()
            link = root / "link"
            try:
                link.symlink_to(outside, target_is_directory=True)
            except OSError:
                self.skipTest("symbolic links are unavailable")
            with self.assertRaises(harnessctl.HarnessError):
                harnessctl.check_target(link / "file.md", [root])

    def test_operation_needs_one_content_source(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            base = {
                "schema_version": 1,
                "run_id": "shape",
                "allowed_roots": [str(root)],
                "approval_groups": ["workspace"],
                "operations": [
                    {
                        "id": "bad",
                        "action": "create",
                        "target": str(root / "file.md"),
                        "approval_group": "workspace",
                    }
                ],
            }
            with self.assertRaises(harnessctl.HarnessError):
                harnessctl.validate_operations(base)


if __name__ == "__main__":
    unittest.main()
