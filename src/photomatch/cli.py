"""Command-line interface for Photo Match."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from photomatch.scanner import find_duplicate_photos


def _make_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="photomatch",
        description="Find exact duplicate photos without changing any files.",
    )
    parser.add_argument("folder", type=Path, help="folder to scan recursively")
    parser.add_argument(
        "--json",
        dest="json_path",
        type=Path,
        metavar="FILE",
        help="write the results to a JSON report",
    )
    return parser


def _report(root: Path, groups: list[list[Path]]) -> dict[str, object]:
    return {
        "root": str(root),
        "method": "exact_sha256",
        "duplicate_groups": [
            {
                "files": [str(path.relative_to(root)) for path in group],
            }
            for group in groups
        ],
    }


def main(argv: list[str] | None = None) -> int:
    parser = _make_parser()
    args = parser.parse_args(argv)
    root = args.folder.resolve()

    errors: list[tuple[Path, OSError]] = []

    def record_error(path: Path, error: OSError) -> None:
        errors.append((path, error))

    try:
        groups = find_duplicate_photos(root, on_error=record_error)
    except (NotADirectoryError, OSError) as error:
        parser.error(str(error))

    for path, error in errors:
        print(f"Error reading {path}: {error}", file=sys.stderr)

    if args.json_path is not None:
        try:
            args.json_path.write_text(
                json.dumps(_report(root, groups), indent=2) + "\n",
                encoding="utf-8",
            )
        except OSError as error:
            print(f"Error writing report {args.json_path}: {error}", file=sys.stderr)
            return 1

    if groups:
        print(f"Found {len(groups)} duplicate group(s):")
        for index, group in enumerate(groups, start=1):
            print(f"\nGroup {index}:")
            for path in group:
                print(f"  {path.relative_to(root)}")
    else:
        print("No exact duplicate photos found.")

    if args.json_path is not None:
        print(f"\nJSON report written to {args.json_path}")

    if errors:
        print(f"\nCompleted with {len(errors)} read error(s).", file=sys.stderr)
        return 1
    return 0
