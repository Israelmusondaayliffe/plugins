from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "package-plugin.py"


class PackagePluginTests(unittest.TestCase):
    def test_build_is_deterministic_and_source_exact(self) -> None:
        for plugin_name in ("outcome-engine", "signal-to-system"):
            with self.subTest(plugin=plugin_name), tempfile.TemporaryDirectory() as directory:
                source = ROOT / "plugins" / plugin_name
                first = Path(directory) / "first.plugin"
                second = Path(directory) / "second.plugin"
                for output in (first, second):
                    subprocess.run(
                        [sys.executable, str(SCRIPT), "build", "--source", str(source), "--output", str(output)],
                        check=True,
                        capture_output=True,
                        text=True,
                    )
                self.assertEqual(first.read_bytes(), second.read_bytes())
                subprocess.run(
                    [sys.executable, str(SCRIPT), "verify", str(first), "--source", str(source)],
                    check=True,
                    capture_output=True,
                    text=True,
                )


if __name__ == "__main__":
    unittest.main()
