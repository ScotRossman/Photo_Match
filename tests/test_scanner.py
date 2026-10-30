import tempfile
import unittest
from pathlib import Path

from photomatch.scanner import find_duplicate_photos


class FindDuplicatePhotosTests(unittest.TestCase):
    def test_finds_exact_duplicates_recursively_and_ignores_non_photos(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            nested = root / "nested"
            nested.mkdir()
            first = root / "first.JPG"
            second = nested / "copy.jpg"
            first.write_bytes(b"same photo bytes")
            second.write_bytes(b"same photo bytes")
            (root / "notes.txt").write_bytes(b"same photo bytes")

            groups = find_duplicate_photos(root)

            self.assertEqual(groups, [[first, second]])

    def test_does_not_group_different_content_or_single_files(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            (root / "one.png").write_bytes(b"first")
            (root / "two.png").write_bytes(b"second")
            (root / "readme.txt").write_bytes(b"ignored")

            self.assertEqual(find_duplicate_photos(root), [])

    def test_rejects_missing_or_non_directory_path(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            file_path = root / "photo.jpg"
            file_path.write_bytes(b"photo")

            with self.assertRaises(NotADirectoryError):
                find_duplicate_photos(root / "missing")
            with self.assertRaises(NotADirectoryError):
                find_duplicate_photos(file_path)


if __name__ == "__main__":
    unittest.main()
