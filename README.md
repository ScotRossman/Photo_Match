# Photo Match

Photo Match is a small, local command-line tool for finding exact duplicate
photos. The first version identifies byte-for-byte copies using SHA-256; it
does not modify or delete any files.

## Requirements

- Python 3.10 or newer

## Install

From the project directory:

```powershell
python -m pip install -e .
```

## Use

Scan a folder and all of its subfolders:

```powershell
photomatch "C:\Users\you\Pictures"
```

Write the results to a JSON report as well:

```powershell
photomatch "C:\Users\you\Pictures" --json duplicates.json
```

Or run it without installing the command:

```powershell
python -m photomatch "C:\Users\you\Pictures"
```

The scanner checks common raster and camera RAW photo extensions. Files with
other extensions are ignored. If a file cannot be read, the tool reports the
error, continues scanning, and exits with a nonzero status.

## Current scope and next steps

This version finds exact file copies only. Copies that were resized, edited, or
re-encoded are not considered duplicates yet. A sensible next stage is visual
similarity matching, followed by AI-assisted grouping of burst photos. The
current scanner is read-only and its JSON report can serve as an initial
integration point for a future interface.

## Tests

```powershell
python -m unittest discover -s tests -v
```
