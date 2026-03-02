import sqlite3
from datetime import datetime
import logging
from pathlib import Path
from contextlib import contextmanager

BASE_DIR = Path(__file__).parent
DATABASE_NAME = BASE_DIR / 'version_notes.db'
CHANGELOG_FILE = BASE_DIR / 'CHANGELOG.md'
LOG_FILE = BASE_DIR / 'version_management.log'

# --- Logging Setup ---
def setup_logging():
    """Initializes logging to a file in the same directory."""
    logging.basicConfig(
        filename=LOG_FILE,
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    logging.info("Logging initialized.")

# --- Database Setup and Core Functions ---

@contextmanager
def get_db():
    conn = sqlite3.connect(DATABASE_NAME)
    try:
        yield conn
    finally:
        conn.close()

def setup_database():
    """Initializes the SQLite database and creates the 'releases' table."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS releases (
                id TEXT PRIMARY KEY,
                version_number TEXT NOT NULL UNIQUE,
                notes TEXT,
                timestamp TEXT
            )
        ''')
        conn.commit()
    logging.info("Database initialized with 'releases' table.")

def get_latest_version_data():
    """Fetches the highest version number and ID from the database."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, version_number FROM releases ORDER BY id DESC LIMIT 1"
        )
        latest = cursor.fetchone()
    logging.info("Fetched latest version data: %s", latest)
    return latest

def parse_version(version_str: str) -> tuple[int, int, int]:
    """Parse version string like '1.2.3' into tuple of integers."""
    parts = version_str.split('.')
    if len(parts) != 3:
        raise ValueError(f"Invalid version format: '{version_str}' — expected X.Y.Z")
    logging.info("Parsed version %s into %s", version_str, parts)
    return int(parts[0]), int(parts[1]), int(parts[2])

def generate_next_version(latest_version_data):
    """
    Generates the next version ID and SemVer number based on user choice.
    Options: 1 (major), 2 (minor), 3 (patch), Enter (auto patch), c (cancel).
    """
    if latest_version_data is None:
        # Initial values
        new_id = "001"
        new_version = "0.0.1"
        logging.info("No previous version found. Using initial ID: %s, Version: %s", new_id, new_version)
    else:
        latest_id, latest_version = latest_version_data
        # Generate Next ID (e.g., '001' -> '002')
        next_id_int = int(latest_id) + 1
        new_id = f"{next_id_int:03d}"

        # Parse current version
        major, minor, patch = parse_version(latest_version)

        # Display increment options
        print(f"\nCurrent version: {latest_version}")
        print("Select increment type:")
        print("1) Major (reset minor & patch)")
        print("2) Minor (reset patch)")
        print("3) Patch")
        print("Enter) Auto-increment patch")
        print("c/C) Cancel")

        choice = input("\nEnter choice (1/2/3/Enter/c): ").strip().lower()

        if choice == 'c' or choice == 'cancel':
            logging.info("Version increment cancelled by user.")
            return None, None  # Cancel operation
        elif choice == '1':
            new_version = f"{major + 1}.0.0"
        elif choice == '2':
            new_version = f"{major}.{minor + 1}.0"
        elif choice == '3' or choice == '':
            new_version = f"{major}.{minor}.{patch + 1}"
        else:
            print("Invalid choice. Defaulting to patch increment.")
            new_version = f"{major}.{minor}.{patch + 1}"
        logging.info("Generated new version: %s from choice: %s", new_version, choice)

    return new_id, new_version

def update_changelog():
    """Regenerates CHANGELOG.md in clean Keep-a-Changelog style Markdown format."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, version_number, notes, timestamp
            FROM releases
            ORDER BY id DESC
        """)
        releases = cursor.fetchall()

    try:
        with open(CHANGELOG_FILE, 'w', encoding='utf-8') as f:
            # Header (standard Keep a Changelog preamble)
            f.write("# Changelog\n\n")
            f.write("All notable changes to this project will be documented in this file.\n\n")
            f.write("The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),\n")
            f.write("and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).\n\n")

            if not releases:
                f.write("> No releases have been recorded yet.\n")
                logging.info("CHANGELOG.md generated – no releases yet.")
                return

            for rel_id, version, notes, ts in releases:
                # ISO timestamps are stored as 'YYYY-MM-DD HH:MM:SS' — grab date part
                date_str = ts[:10] if ts else 'unknown'

                f.write(f"## [{version}] - {date_str}\n\n")

                if not notes or not notes.strip():
                    f.write("No release notes provided.\n\n")
                    continue

                # Split notes into lines and clean them
                lines = [line.strip() for line in notes.splitlines() if line.strip()]

                # Simple heuristic classification
                categorized = {'Added': [], 'Changed': [], 'Fixed': [], 'Other': []}

                for line in lines:
                    lower = line.lower()
                    if any(word in lower for word in ['add', 'new', 'implement', 'feat', 'create']):
                        categorized['Added'].append(line)
                    elif any(word in lower for word in ['fix', 'bug', 'correct', 'resolve', 'hotfix']):
                        categorized['Fixed'].append(line)
                    elif any(word in lower for word in ['change', 'update', 'refactor', 'improv', 'modify']):
                        categorized['Changed'].append(line)
                    else:
                        categorized['Other'].append(line)

                # Write categorized sections only if they have content
                for category, items in categorized.items():
                    if items:
                        f.write(f"### {category}\n\n")
                        for item in items:
                            text = item[0].upper() + item[1:] if item else item
                            f.write(f"- {text}\n")
                        f.write("\n")

                # Fallback: if no categories matched, show as plain list
                if all(len(lst) == 0 for lst in categorized.values()) and lines:
                    f.write("### Notes\n\n")
                    for line in lines:
                        f.write(f"- {line}\n")
                    f.write("\n")

            f.write("\n<!-- Generated by version-management tool -->\n")

        print(f"[SUCCESS] Updated {CHANGELOG_FILE} with {len(releases)} release(s).")
        logging.info("Successfully updated CHANGELOG.md with %d releases.", len(releases))

    except Exception as e:
        print(f"[ERROR] Could not write {CHANGELOG_FILE}: {str(e)}")
        logging.error("Failed to update CHANGELOG.md: %s", str(e))

def add_version_notes():
    """Prompts the user to add notes and records a new version in the DB."""

    # Generate new ID and version number
    latest_data = get_latest_version_data()
    version_id, version_number = generate_next_version(latest_data)

    if version_id is None and version_number is None:
        print("\n[INFO] Operation cancelled.")
        logging.info("Version addition cancelled.")
        return

    print("\n--- Add New Release ---")
    print(f"Generated Version ID: {version_id}")
    print(f"Generated Version Number: {version_number}")

    notes = ""
    while not notes:
        notes = input("Enter release notes (required): ").strip()

    timestamp = datetime.now().isoformat(sep=' ', timespec='seconds')

    with get_db() as conn:
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO releases (id, version_number, notes, timestamp) VALUES (?, ?, ?, ?)",
                (version_id, version_number, notes, timestamp)
            )
            conn.commit()
            print(f"\n[SUCCESS] Version {version_number} (ID: {version_id}) added to history.")
            logging.info("Added version %s (ID: %s) to database.", version_number, version_id)

            # Update changelog after successful DB insert
            update_changelog()
        except sqlite3.IntegrityError as e:
            print(f"\n[ERROR] Failed to add version. A record with version number {version_number} already exists. ({e})")
            logging.error("Failed to add version %s: %s", version_number, str(e))

def view_version_history():
    """Fetches and prints all release history."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, version_number, notes, timestamp FROM releases ORDER BY id DESC")
        releases = cursor.fetchall()

    print("\n--- Full Version History ---")
    if not releases:
        print("No versions recorded yet.")
        logging.info("Viewed version history: No entries found.")
        return

    for release in releases:
        version_id, version_number, notes, timestamp = release
        print(f"\nID: {version_id} | Version: {version_number}")
        print(f"  Notes: {notes}")
        print(f"  Released: {timestamp}")
    print("----------------------------")
    logging.info("Viewed version history: %d entries displayed.", len(releases))

def edit_notes():
    """Allows a user to update the notes for an existing version."""
    version = input("\nEnter the version number to edit (e.g., 0.0.1): ").strip()

    with get_db() as conn:
        cursor = conn.cursor()

        cursor.execute("SELECT notes FROM releases WHERE version_number = ?", (version,))
        result = cursor.fetchone()

        if result is None:
            print(f"[ERROR] Version {version} not found.")
            logging.warning("Attempted to edit notes for non-existent version: %s", version)
            return

        current_notes = result[0]
        print(f"\nCurrent Notes for {version}: {current_notes}")

        new_notes = input("Enter the new, updated notes: ").strip()

        if new_notes:
            timestamp = datetime.now().isoformat(sep=' ', timespec='seconds')
            cursor.execute(
                "UPDATE releases SET notes = ?, timestamp = ? WHERE version_number = ?",
                (new_notes, timestamp, version)
            )
            conn.commit()
            print(f"[SUCCESS] Notes for version {version} updated.")
            logging.info("Updated notes for version %s.", version)

            # Update changelog after editing notes
            update_changelog()
        else:
            print("[INFO] Edit cancelled. Notes were not changed.")
            logging.info("Edit notes cancelled for version %s.", version)

# --- Main Application Loop ---

def display_menu():
    """Displays the main menu options to the user."""
    print("\n--- Version Management System ---")
    print("\n ")
    print("1. Add New Version Notes (Auto-Increment)")
    print("2. View All Version History")
    print("3. Edit Existing Version Notes")
    print("0. Exit")
    print("\n ")
    return input("Enter your choice (0-3): ")

def main():
    setup_logging()
    setup_database()

    while True:
        choice = display_menu()

        if choice == '1':
            add_version_notes()
        elif choice == '2':
            view_version_history()
        elif choice == '3':
            edit_notes()
        elif choice == '0':
            print("\nExiting. Database connection closed. 👋")
            logging.info("Application exited.")
            break
        else:
            print("[ERROR] Invalid choice. Please try again.")
            logging.warning("Invalid menu choice entered: %s", choice)

if __name__ == "__main__":
    main()
