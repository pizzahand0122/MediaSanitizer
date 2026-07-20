# MediaSanitizer

MediaSanitizer is a command-line application that recursively scans a directory
and reports how many supported media files are clean or have issues. It does not
modify or delete files.

## Requirements

- Python 3.13 or newer

## Installation

Clone the repository, change into its directory, and install the project in a
virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install .
```

For development, install an editable copy instead:

```bash
python -m pip install -e .
```

## Supported media formats

Files are recognized by extension. Extension matching is case-insensitive.

| Format | Extensions |
| --- | --- |
| Matroska Video | `.mkv` |
| MPEG-4 Video | `.mp4`, `.m4v` |
| Audio Video Interleave | `.avi` |
| QuickTime Video | `.mov` |

## CLI usage

After installation, pass one directory to `media-sanitizer`:

```bash
media-sanitizer <directory>
```

For example:

```bash
media-sanitizer ~/Videos
```

The directory and all of its subdirectories are scanned. A successful scan
prints a summary of matching files. Empty media files and files whose metadata
cannot be read from the filesystem are counted as files with issues:

```text
Total files: 12
Clean files: 12
Files with issues: 0
```

The CLI can also be run from the repository without installing the console
script:

```bash
python -m media_sanitizer.main <directory>
```

The command exits with status `0` after a successful scan, `1` when the supplied
path is not a directory, and `2` when it is given anything other than one
directory argument.

## Development

Run the test suite from the repository root:

```bash
python3 -m unittest discover -v
```
