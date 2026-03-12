"""
import_cursor.py
---------------
Copies Cursor agent sessions from a user's .cursor folder into the
ingestion/cursor-chats/ folder, ready for the analysis pipeline.

Run this after discover_cursor.py has shown you which projects are available
and you've decided which ones to import.

Usage (run from the project root):
    python scripts/import_cursor.py "PATH_TO_.CURSOR" "project-slug"
    python scripts/import_cursor.py "PATH_TO_.CURSOR" "project-slug" --days 30
    python scripts/import_cursor.py "PATH_TO_.CURSOR" "proj-a" "proj-b" --days 60

Arguments:
    PATH_TO_.CURSOR   Full path to the user's .cursor folder
    project-slug(s)   One or more project folder names (from discover_cursor.py output)

Options:
    --days N          Only import sessions modified in the last N days (default: all)
    --clear           Clear the ingestion folder for this project before importing
                      (use when replacing a previous import)

Examples:
    Windows: python scripts/import_cursor.py "C:\\Users\\Tom\\.cursor" "wellsky-project" --days 30
    macOS:   python scripts/import_cursor.py "/Users/tom/.cursor" "wellsky-project" --days 30
"""

import json
import os
import shutil
import sys
from datetime import datetime, timedelta, timezone


# ── Config ────────────────────────────────────────────────────────────────────

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INGESTION_DIR = os.path.join(BASE_DIR, "ingestion", "cursor-chats")


# ── Helpers ───────────────────────────────────────────────────────────────────

def parse_args(argv):
    args = argv[1:]  # drop script name

    if not args or args[0] in ("--help", "-h"):
        print(__doc__)
        sys.exit(0)

    cursor_path = args[0].strip().strip('"').strip("'")
    args = args[1:]

    days = None
    clear = False
    project_slugs = []

    i = 0
    while i < len(args):
        if args[i] == "--days" and i + 1 < len(args):
            try:
                days = int(args[i + 1])
            except ValueError:
                print(f"ERROR: --days requires an integer, got '{args[i+1]}'")
                sys.exit(1)
            i += 2
        elif args[i] == "--clear":
            clear = True
            i += 1
        elif not args[i].startswith("--"):
            project_slugs.append(args[i].strip().strip('"').strip("'"))
            i += 1
        else:
            print(f"Unknown option: {args[i]}")
            sys.exit(1)

    return cursor_path, project_slugs, days, clear


def cutoff_timestamp(days):
    if days is None:
        return None
    return (datetime.now(tz=timezone.utc) - timedelta(days=days)).timestamp()


def import_project(cursor_path, project_slug, cutoff_ts, clear):
    """Copy eligible sessions from a project into ingestion/cursor-chats/."""

    transcripts_dir = os.path.join(cursor_path, "projects", project_slug, "agent-transcripts")
    if not os.path.isdir(transcripts_dir):
        print(f"  ERROR: No agent-transcripts folder found for '{project_slug}'")
        print(f"         Expected: {transcripts_dir}")
        return 0, 0

    dest_dir = os.path.join(INGESTION_DIR, project_slug)

    if clear and os.path.isdir(dest_dir):
        shutil.rmtree(dest_dir)
        print(f"  Cleared existing ingestion folder for '{project_slug}'")

    os.makedirs(dest_dir, exist_ok=True)

    copied = 0
    skipped_age = 0
    skipped_exists = 0

    session_ids = sorted(os.listdir(transcripts_dir))

    for session_id in session_ids:
        src_session_dir = os.path.join(transcripts_dir, session_id)
        if not os.path.isdir(src_session_dir):
            continue

        jsonl_src = os.path.join(src_session_dir, f"{session_id}.jsonl")
        if not os.path.exists(jsonl_src):
            continue

        # Age filter
        if cutoff_ts is not None:
            mtime = os.stat(jsonl_src).st_mtime
            if mtime < cutoff_ts:
                skipped_age += 1
                continue

        dest_session_dir = os.path.join(dest_dir, session_id)

        # Skip if already imported (same file, no --clear)
        dest_jsonl = os.path.join(dest_session_dir, f"{session_id}.jsonl")
        if os.path.exists(dest_jsonl):
            skipped_exists += 1
            continue

        os.makedirs(dest_session_dir, exist_ok=True)
        shutil.copy2(jsonl_src, dest_jsonl)
        copied += 1

    return copied, skipped_age, skipped_exists


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    cursor_path, project_slugs, days, clear = parse_args(sys.argv)

    if not os.path.isdir(cursor_path):
        print(f"ERROR: Folder not found: {cursor_path}")
        print("Make sure you've granted folder access and the path is correct.")
        sys.exit(1)

    if not project_slugs:
        print("ERROR: No project slugs specified.")
        print("Run discover_cursor.py first to see available projects, then pass one or more project names.")
        print()
        print('Example: python scripts/import_cursor.py "PATH" "my-project" --days 30')
        sys.exit(1)

    cutoff_ts = cutoff_timestamp(days)
    date_filter_note = f"sessions from the last {days} days" if days else "all sessions"

    print(f"\nImporting {date_filter_note} from {len(project_slugs)} project(s)...\n")

    total_copied = 0
    results = []

    for slug in project_slugs:
        print(f"  [{slug}]")
        copied, skipped_age, skipped_exists = import_project(cursor_path, slug, cutoff_ts, clear)

        if copied > 0:
            print(f"    ✓ Copied {copied} session(s) to ingestion/cursor-chats/{slug}/")
        if skipped_age > 0:
            print(f"    – Skipped {skipped_age} session(s) outside the {days}-day window")
        if skipped_exists > 0:
            print(f"    – Skipped {skipped_exists} session(s) already in ingestion folder")
        if copied == 0 and skipped_age == 0 and skipped_exists == 0:
            print(f"    ! No sessions found for this project")

        total_copied += copied
        results.append({
            "project": slug,
            "copied": copied,
            "skipped_age": skipped_age,
            "skipped_exists": skipped_exists,
        })

    print(f"\n{'─' * 50}")
    print(f"Total sessions imported: {total_copied}")
    print(f"Ingestion folder: ingestion/cursor-chats/")

    if total_copied > 0:
        print()
        print("Next steps:")
        print("  1. python scripts/extract_sessions.py")
        print("  2. python scripts/analyse_sessions.py")
        print("  3. Ask the AI to run the prompting review")
    else:
        print()
        if days:
            print(f"No new sessions were imported. Try increasing --days (currently {days}),")
            print("or run without --days to import all sessions.")
        else:
            print("No sessions were imported. Check the project slug matches exactly")
            print("what discover_cursor.py showed (names are case-sensitive).")


if __name__ == "__main__":
    main()
