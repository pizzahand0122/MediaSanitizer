import subprocess
import sys
import tempfile
import tomllib
import unittest
from pathlib import Path


class PackagingTests(unittest.TestCase):
    def test_project_declares_console_script(self):
        project_file = Path(__file__).parents[1] / "pyproject.toml"

        with project_file.open("rb") as file:
            configuration = tomllib.load(file)

        self.assertEqual(configuration["project"]["version"], "0.1.0")
        self.assertEqual(
            configuration["project"]["scripts"]["media-sanitizer"],
            "media_sanitizer.main:main",
        )

    def test_module_entrypoint_scans_a_directory(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "movie.mp4").write_bytes(b"media data")

            result = subprocess.run(
                [sys.executable, "-m", "media_sanitizer.main", directory],
                check=False,
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.returncode, 0)
            self.assertEqual(
                result.stdout,
                "Total files: 1\n"
                "Clean files: 1\n"
                "Files with issues: 0\n",
            )
            self.assertEqual(result.stderr, "")


if __name__ == "__main__":
    unittest.main()
