# Version Management System

A lightweight **command-line tool** for tracking software releases using **Semantic Versioning** (SemVer).
It stores version history + release notes in SQLite and automatically maintains a Markdown `CHANGELOG.md`.

Current script version: **0.2.0**

## What's New in v0.2.0

- **Path safety** — all files (DB, changelog, log) are anchored to the script's directory via `pathlib.Path`, so the tool works correctly regardless of the working directory you run it from.
- **Connection safety** — database connections are managed with a `get_db()` context manager, ensuring connections are always closed even if an error occurs.
- **Robust version parsing** — `parse_version()` now raises a clear `ValueError` for malformed version strings instead of crashing with an `IndexError`.
- **ISO timestamps** — timestamps are stored as `YYYY-MM-DD HH:MM:SS` strings, eliminating a fragile `.split('.')` workaround.
- **Markdown changelog** — `CHANGELOG.md` is now written in proper Keep-a-Changelog format with auto-categorized sections (Added / Changed / Fixed / Other).

## Features

- Semantic versioning (major.minor.patch)
- Sequential 3-digit version IDs (`001` → `002` → …)
- Interactive version increment choice (major / minor / patch / auto)
- Required release notes for every version
- SQLite storage (`version_notes.db`)
- Auto-generated Markdown changelog (`CHANGELOG.md`)
- View full version history
- Edit notes of existing releases
- Activity logging (`version_management.log`)

## Files Created/Used

| File                        | Purpose                                     |
|-----------------------------|---------------------------------------------|
| `version_notes.db`          | SQLite database – all releases              |
| `CHANGELOG.md`              | Human-readable Markdown changelog (auto-generated) |
| `version_management.log`    | Debug / activity log                        |

## Requirements

- Python **3.10+**
- Only **standard library** modules are used:
  - `sqlite3`, `datetime`, `logging`, `pathlib`, `contextlib`

No external dependencies.

## Installation

Just save the script:

```bash
# example name — feel free to rename
mv software.version.0.1.0.py version-manager.py
```

## Usage

```bash
python version-manager.py
```

Then follow the interactive menu:

```
--- Version Management System ---

1. Add New Version Notes (Auto-Increment)
2. View All Version History
3. Edit Existing Version Notes
0. Exit
```

## Menu Options

| Option | Description |
|--------|-------------|
| **1**  | Bump the version (major / minor / patch) and record release notes |
| **2**  | Print all stored versions with notes and timestamps |
| **3**  | Update the notes for an existing version |
| **0**  | Exit the application |
