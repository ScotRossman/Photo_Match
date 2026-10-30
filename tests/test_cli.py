import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from photomatch.cli import main


class CommandLineTests(unittest.TestCase):
    def test_json_report_contains_duplicate_group(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            (root / "one.jpg").write_bytes(b"identical")
            (root / "two.jpg").write_bytes(b"identical")
            report_path = root / "report.json"

            with patch("sys.stdout"):
                result = main([str(root), "--json", str(report_path)])

            report = json.loads(report_path.read_text(encoding="utf-8"))
            self.assertEqual(result, 0)
            self.assertEqual(report["method"], "exact_sha256")
            self.assertEqual(
                report["duplicate_groups"][0]["files"],
                ["one.jpg", "two.jpg"],
            )

    def test_read_error_is_reported_with_nonzero_exit(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            (root / "one.jpg").write_bytes(b"photo")

            with (
                patch("photomatch.scanner._sha256", side_effect=PermissionError("denied")),
                patch("sys.stderr") as stderr,
                patch("sys.stdout"),
            ):
                result = main([str(root)])

            self.assertEqual(result, 1)
            self.assertIn("Error reading", "".join(call.args[0] for call in stderr.write.call_args_list))


if __name__ == "__main__":
    unittest.main()
