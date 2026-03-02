# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - 2026-03-01

### Added

- `pathlib.Path`-based constants (`BASE_DIR`, `DATABASE_NAME`, `CHANGELOG_FILE`, `LOG_FILE`) so all files are anchored to the script's directory regardless of the working directory
- `get_db()` context manager (`contextlib.contextmanager`) for safe, automatic database connection cleanup across all 6 database functions

### Changed

- `CHANGELOG_FILE` renamed from `changelog.txt` to `CHANGELOG.md`
- `update_changelog()` now writes proper Keep-a-Changelog Markdown with auto-categorized sections (Added / Changed / Fixed / Other)
- Timestamps stored as ISO 8601 strings (`YYYY-MM-DD HH:MM:SS`) instead of raw `datetime` objects, removing the fragile `.split('.')` workaround in `update_changelog()` and `view_version_history()`
- All six database functions refactored to use `with get_db() as conn:` instead of manual `connect` / `close` calls

### Fixed

- `parse_version()` now raises a clear `ValueError` for malformed version strings instead of crashing with an `IndexError` on bad input

## [0.1.3] - 2025-04-12

### Added
- Dark mode toggle in user settings
- Remember-me option on login screen

### Fixed
- Login timeout issue on slow mobile networks

## [0.1.2] - 2025-03-29

### Changed
- Updated primary button colors to match brand guidelines

## [0.1.1] - 2025-03-15

### Notes
- Initial implementation of version tracking system
- Basic SQLite storage for release history