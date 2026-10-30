"""Find byte-identical image files beneath a directory."""

from __future__ import annotations

import hashlib
import os
from collections import defaultdict
from pathlib import Path
from typing import Callable

IMAGE_EXTENSIONS = frozenset(
    {
        ".3fr",
        ".arw",
        ".avif",
        ".bmp",
        ".cr2",
        ".cr3",
        ".dng",
        ".erf",
        ".gif",
        ".heic",
        ".heif",
        ".iiq",
        ".jpe",
        ".jpeg",
        ".jpg",
        ".kdc",
        ".mef",
        ".mos",
        ".mrw",
        ".nef",
        ".nrw",
        ".orf",
        ".pef",
        ".png",
        ".raf",
        ".rw2",
        ".srw",
        ".tif",
        ".tiff",
        ".webp",
    }
)
CHUNK_SIZE = 1024 * 1024


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as photo:
        for chunk in iter(lambda: photo.read(CHUNK_SIZE), b""):
            digest.update(chunk)
    return digest.hexdigest()


def find_duplicate_photos(
    root: Path,
    on_error: Callable[[Path, OSError], None] | None = None,
) -> list[list[Path]]:
    """Return groups of photo paths with identical SHA-256 content."""
    root = root.resolve()
    if not root.is_dir():
        raise NotADirectoryError(f"Not a directory: {root}")

    def report_walk_error(error: OSError) -> None:
        if on_error is not None:
            on_error(Path(error.filename or root), error)
        else:
            raise error

    by_digest: dict[str, list[Path]] = defaultdict(list)
    for current, _, filenames in os.walk(root, onerror=report_walk_error):
        directory = Path(current)
        for filename in filenames:
            path = directory / filename
            if path.suffix.casefold() not in IMAGE_EXTENSIONS:
                continue
            try:
                by_digest[_sha256(path)].append(path)
            except OSError as error:
                if on_error is not None:
                    on_error(path, error)
                else:
                    raise

    groups = [
        sorted(paths, key=lambda path: str(path).casefold())
        for paths in by_digest.values()
        if len(paths) > 1
    ]
    return sorted(groups, key=lambda group: str(group[0]).casefold())
