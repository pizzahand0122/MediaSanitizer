# MediaSanitizer

MediaSanitizer is a command-line application that recursively scans a directory
and reports how many supported media files are clean or have issues. It does not
modify or delete files.

Repair mode is under development. Its first safety boundary is now represented
by `MkvRepairPlan`: plans accept only Matroska track UIDs and changes to default
flags, names, and BCP 47 language tags. They can produce a quoted dry-run preview
or a metadata-only `mkvpropedit` argument list; they do not execute it. Track
removal, media remuxing, and re-encoding cannot be expressed by the plan model.

`MkvRepairExecutor` provides the guarded application layer for those plans. It
requires the caller to pass `confirmed=True`, verifies the target is a file,
and refuses to overwrite an existing sibling `.mediasanitizer.bak` file. It
copies the original to that backup before running the metadata-only command,
then validates the requested metadata with `mkvmerge`. After successful
validation the backup is removed by default; pass `--keep-backup` to retain it.
If execution or validation fails, the backup is atomically restored over the
target. Call `plan.preview()` before asking a user to confirm.

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

### Repair preview and confirmation

The CLI can build a repair plan for one MKV track UID. Preview it without
changing the file by adding `--dry-run`:

```bash
media-sanitizer repair movie.mkv 42 --default true \
  --name "Main Audio" --language en-US --dry-run
```

Omit `--dry-run` to apply the plan. The exact metadata-only `mkvpropedit`
command is printed first, and execution occurs only if the confirmation response
is the full word `yes` (case-insensitive). Any other response, including `y` or
end-of-input, cancels without invoking the repair executor. At least one of
`--default`, `--name`, or `--language` is required. The executor uses a sibling
`.mediasanitizer.bak` rollback copy and removes it after validation. Add
`--keep-backup` to retain that copy explicitly.

## Development

Run the test suite from the repository root:

```bash
python3 -m unittest discover -v
```
