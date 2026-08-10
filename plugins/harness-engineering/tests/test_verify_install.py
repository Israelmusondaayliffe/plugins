from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import tempfile
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "verify_install.py"
SPEC = importlib.util.spec_from_file_location("verify_install", SCRIPT)
assert SPEC and SPEC.loader
verify_install = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(verify_install)


class VerifyInstallTests(unittest.TestCase):
    def make_source_and_cache(self, root: Path, marketplace: str = "community-agent-plugins") -> tuple[Path, Path]:
        source = root / "plugin"
        cache = root / "cache" / marketplace / "harness-engineering" / "2.3.0"
        (source / ".codex-plugin").mkdir(parents=True)
        cache.mkdir(parents=True)
        files = {
            ".codex-plugin/plugin.json": '{"name": "harness-engineering", "version": "2.3.0"}\n',
            "README.md": "public plugin\n",
        }
        for relative, content in files.items():
            source_path = source / relative
            source_path.parent.mkdir(parents=True, exist_ok=True)
            source_path.write_text(content, encoding="utf-8")
            cache_path = cache / relative
            cache_path.parent.mkdir(parents=True, exist_ok=True)
            cache_path.write_text(content, encoding="utf-8")
        return source, root / "cache"

    def listing(self, *marketplaces: str) -> dict[str, list[dict[str, object]]]:
        return {
            "installed": [
                {
                    "name": "harness-engineering",
                    "marketplaceName": marketplace,
                    "version": "2.3.0",
                    "enabled": True,
                }
                for marketplace in marketplaces
            ]
        }

    def test_public_marketplace_and_explicit_cache_root_pass(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            source, cache_root = self.make_source_and_cache(Path(temp))
            result = verify_install.verify_install(
                source,
                self.listing("community-agent-plugins"),
                marketplace="community-agent-plugins",
                cache_root=cache_root,
            )
            self.assertEqual(result["marketplace"], "community-agent-plugins")
            self.assertTrue(result["parity"])

    def test_single_matching_marketplace_is_inferred(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            source, cache_root = self.make_source_and_cache(Path(temp), marketplace="public-source")
            result = verify_install.verify_install(source, self.listing("public-source"), cache_root=cache_root)
            self.assertEqual(result["marketplace"], "public-source")

    def test_claude_listing_reads_registry_and_enabled_map(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            home = Path(temp)
            (home / "plugins").mkdir(parents=True)
            (home / "plugins" / "installed_plugins.json").write_text(
                json.dumps(
                    {
                        "version": 2,
                        "plugins": {
                            "harness-engineering@public-source": [
                                {"scope": "user", "installPath": "/x", "version": "2.5.1"}
                            ],
                            "other@public-source": [
                                {"scope": "user", "installPath": "/y", "version": "1.0.0"}
                            ],
                        },
                    }
                ),
                encoding="utf-8",
            )
            (home / "settings.json").write_text(
                json.dumps({"enabledPlugins": {"harness-engineering@public-source": True, "other@public-source": False}}),
                encoding="utf-8",
            )
            listing = verify_install.claude_listing(home)
            rows = {(item["name"], item["marketplaceName"], item["version"], item["enabled"]) for item in listing["installed"]}
            self.assertIn(("harness-engineering", "public-source", "2.5.1", True), rows)
            self.assertIn(("other", "public-source", "1.0.0", False), rows)
            self.assertEqual(verify_install.claude_cache_root(home), home / "plugins" / "cache")

    def test_ambiguous_marketplaces_require_selection(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            source, cache_root = self.make_source_and_cache(Path(temp))
            with self.assertRaisesRegex(RuntimeError, "pass --marketplace"):
                verify_install.verify_install(
                    source,
                    self.listing("first-source", "second-source"),
                    cache_root=cache_root,
                )


if __name__ == "__main__":
    unittest.main()
