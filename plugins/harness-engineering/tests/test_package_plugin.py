from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
import zipfile


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "package_plugin.py"
SPEC = importlib.util.spec_from_file_location("package_plugin", SCRIPT)
assert SPEC and SPEC.loader
package_plugin = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(package_plugin)


class PackagePluginTests(unittest.TestCase):
    def make_source(self, root: Path) -> Path:
        source = root / "plugin"
        (source / ".claude-plugin").mkdir(parents=True)
        (source / "skills" / "hello").mkdir(parents=True)
        (source / ".claude-plugin" / "plugin.json").write_text(
            json.dumps({"name": "example-plugin", "version": "1.2.3"}) + "\n",
            encoding="utf-8",
        )
        (source / "skills" / "hello" / "SKILL.md").write_text(
            "---\nname: hello\ndescription: Test skill.\n---\n\nHello.\n",
            encoding="utf-8",
        )
        (source / "README.md").write_text("Test plugin\n", encoding="utf-8")
        return source

    def test_builds_rooted_zip_with_exact_source_parity(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = self.make_source(root)
            archive = root / "example-plugin.zip"
            result = package_plugin.build_archive(source, archive)
            self.assertEqual(result["plugin"], "example-plugin")
            with zipfile.ZipFile(archive) as bundle:
                self.assertIn(".claude-plugin/plugin.json", bundle.namelist())
                self.assertNotIn("plugin/.claude-plugin/plugin.json", bundle.namelist())
            verified = package_plugin.archive_summary(archive, source)
            self.assertEqual(verified["sha256"], result["sha256"])

    def test_build_is_reproducible_for_the_same_source(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = self.make_source(root)
            first = package_plugin.build_archive(source, root / "first.zip")
            second = package_plugin.build_archive(source, root / "second.zip")
            self.assertEqual(first["sha256"], second["sha256"])

    def test_verify_rejects_archive_that_does_not_match_source(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = self.make_source(root)
            archive = root / "example-plugin.zip"
            package_plugin.build_archive(source, archive)
            with zipfile.ZipFile(archive, "a") as bundle:
                bundle.writestr("unexpected.txt", "not in source\n")
            with self.assertRaisesRegex(RuntimeError, "does not match source"):
                package_plugin.archive_summary(archive, source)

    def test_verify_rejects_content_tampering_with_the_same_member_name(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = self.make_source(root)
            archive = root / "example-plugin.zip"
            tampered = root / "tampered.zip"
            package_plugin.build_archive(source, archive)
            with zipfile.ZipFile(archive) as original, zipfile.ZipFile(tampered, "w") as replacement:
                for info in original.infolist():
                    content = original.read(info.filename)
                    if info.filename == "README.md":
                        content = b"tampered content\n"
                    replacement.writestr(info, content)
            with self.assertRaisesRegex(RuntimeError, "contents do not match source"):
                package_plugin.archive_summary(tampered, source)

    def test_build_rejects_unignored_archive_inside_source(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            source = self.make_source(Path(temp))
            with self.assertRaisesRegex(RuntimeError, "under dist"):
                package_plugin.build_archive(source, source / "example-plugin.zip")


if __name__ == "__main__":
    unittest.main()
