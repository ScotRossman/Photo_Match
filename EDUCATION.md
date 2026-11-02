# Photo Match: Application Guide

This guide explains what Photo Match does, how its parts fit together, and how
to try it safely. It is written as Markdown so you can open and read it in a
code editor.

## What the application does

Photo Match is a local command-line program that searches a folder and its
subfolders for groups of photo files with matching SHA-256 content hashes. It
prints the groups it finds and can optionally save them as a JSON report.

The scanner does not rename, move, edit, or delete photos. A match means the
files have the same content hash; resized, edited, or re-encoded versions will
usually have different hashes and are not matched.

## How a scan works

1. The command-line program resolves the folder path and checks that it is a
   directory.
2. The scanner walks through that folder recursively.
3. It considers files whose extensions are in the scanner's supported image
   extension list. Extension matching is case-insensitive.
4. It reads each eligible file in 1 MiB chunks and updates a SHA-256 hash.
   Chunking avoids loading an entire large photo into memory at once.
5. Files with the same hash are collected into a duplicate group. Groups with
   only one file are left out of the results.
6. Results are sorted for consistent output, printed to the terminal, and
   optionally written to JSON.

SHA-256 is a content fingerprint, not a visual comparison. Hash collisions are
theoretically possible, though extremely unlikely; this program groups by hash
and does not perform a second byte-by-byte comparison.

## Run the application

You need Python 3.10 or newer. From the project folder, install the app in
editable mode:

```powershell
python -m pip install -e .
```

Scan a folder:

```powershell
photomatch "C:\Users\you\Pictures"
```

Save a JSON report as well:

```powershell
photomatch "C:\Users\you\Pictures" --json duplicates.json
```

You can also run the package without installing its command:

```powershell
python -m photomatch "C:\Users\you\Pictures"
```

Quote paths that contain spaces. The report path is interpreted relative to the
current working directory unless you provide an absolute path.

## Understand the output

Terminal output lists each duplicate group and the paths of its files, relative
to the folder being scanned. If there are no matches, the program says so.

The JSON report has this general structure:

```json
{
  "root": "C:\\Users\\you\\Pictures",
  "method": "exact_sha256",
  "duplicate_groups": [
    {
      "files": [
        "Family\\photo.jpg",
        "Backup\\photo-copy.jpg"
      ]
    }
  ]
}
```

- `root` is the resolved folder that was scanned.
- `method` identifies the matching method used by this version.
- `duplicate_groups` contains groups of two or more matching paths. The paths
  inside each group are relative to `root`.

## Errors and exit status

If a photo cannot be read, Photo Match reports the problem, continues scanning
other files, and exits with status `1`. It also exits with status `1` if it
cannot write the requested JSON report. A successful scan exits with status
`0`. An invalid scan folder is reported as a command-line error.

## Project map

| File | Responsibility |
| --- | --- |
| `src/photomatch/scanner.py` | Finds supported photo files, hashes their content, and returns duplicate groups. |
| `src/photomatch/cli.py` | Defines command-line arguments, displays results, writes JSON, and handles scan errors. |
| `src/photomatch/__main__.py` | Enables running the package with `python -m photomatch`. |
| `tests/test_scanner.py` | Tests recursive scanning, extension filtering, duplicate grouping, and invalid folders. |
| `tests/test_cli.py` | Tests JSON output and reporting of read errors. |
| `pyproject.toml` | Defines package metadata, Python requirements, and the `photomatch` command. |

## Run the tests

From the project folder:

```powershell
python -m unittest discover -s tests -v
```

The tests use temporary folders and sample bytes, so they do not need your
personal photo collection.

## Current limitations and learning opportunities

- Matching is based on file content, not appearance. A future visual similarity
  feature could compare resized or edited copies.
- The extension list is finite. Files with unlisted extensions are ignored,
  even if their contents are images.
- The JSON report is a simple starting point for another tool or a future user
  interface; this version has no graphical interface.
- The scanner reads and hashes every supported file it encounters. Large
  collections can take time, depending on storage speed and file sizes.

Good places to explore the code are the `IMAGE_EXTENSIONS` set and `_sha256`
function in `scanner.py`, then `find_duplicate_photos`, followed by `main` and
`_report` in `cli.py`.
