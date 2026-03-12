"""
discover_cursor.py
------------------
Scans a user's .cursor folder and produces a human-readable report of all
available Cursor projects and their agent-transcript sessions.

Run this after granting the AI access to your .cursor folder. It reads the
folder structure but does NOT copy or modify anything.

Usage (run from the project root):
    python scripts/discover_cursor.py "C:\\Users\\YourName\\.cursor"
    python scripts/discover_cursor.py "/Users/yourname/.cursor"

Output:
    Prints a project/session summary to the terminal
    Writes discovery_report.json to the project root (gitignored)
"""

import json
import os
import sys
from datetime import datetime, timezone


def get_session_info(session_dir, session_id):
    """Return metadata for a single session folder."""
    jsonl_path = os.path.join(session_dir, f"{session_id}.jsonl")
    if not os.path.exists(jsonl_path):
        return None

    stat = os.stat(jsonl_path)
    size_bytes = stat.st_size
    modified = datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc)

    # Count lines (turns) without loading the whole file
    line_count = 0
    user_turns = 0
    try:
        with open(jsonl_path, encoding="utf-8", errors="replace") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                line_count += 1
                try:
                    obj = json.loads(line)
                    if obj.get("role") == "user":
                        user_turns += 1
                except json.JSONDecodeError:
                    pass
    except OSError:
        pass

    # Check for subagents
    subagents_dir = os.path.join(session_dir, "subagents")
    subagent_count = 0
    if os.path.isdir(subagents_dir):
        subagent_count = sum(1 for f in os.listdir(subagents_dir) if f.endswith(".jsonl"))

    return {
        "id": session_id,
        "modified": modified.isoformat(),
        "modified_ts": stat.st_mtime,
        "size_bytes": size_bytes,
        "total_turns": line_count,
        "user_turns": user_turns,
        "has_subagents": subagent_count > 0,
        "subagent_count": subagent_count,
    }


def scan_project(project_path, project_slug):
    """Scan all sessions in a project's agent-transcripts folder."""
    transcripts_dir = os.path.join(project_path, "agent-transcripts")
    if not os.path.isdir(transcripts_dir):
        return None

    sessions = []
    for session_id in os.listdir(transcripts_dir):
        session_dir = os.path.join(transcripts_dir, session_id)
        if not os.path.isdir(session_dir):
            continue
        info = get_session_info(session_dir, session_id)
        if info:
            sessions.append(info)

    if not sessions:
        return None

    sessions.sort(key=lambda s: s["modified_ts"], reverse=True)

    newest_ts = max(s["modified_ts"] for s in sessions)
    oldest_ts = min(s["modified_ts"] for s in sessions)
    total_size = sum(s["size_bytes"] for s in sessions)

    return {
        "project_slug": project_slug,
        "session_count": len(sessions),
        "newest_session": datetime.fromtimestamp(newest_ts, tz=timezone.utc).strftime("%Y-%m-%d"),
        "oldest_session": datetime.fromtimestamp(oldest_ts, tz=timezone.utc).strftime("%Y-%m-%d"),
        "total_size_kb": round(total_size / 1024),
        "sessions": sessions,
    }


def format_size(kb):
    if kb >= 1024:
        return f"{kb / 1024:.1f} MB"
    return f"{kb} KB"


def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts/discover_cursor.py PATH_TO_DOT_CURSOR_FOLDER")
        print()
        print("Examples:")
        print('  Windows: python scripts/discover_cursor.py "C:\\Users\\YourName\\.cursor"')
        print('  macOS:   python scripts/discover_cursor.py "/Users/yourname/.cursor"')
        sys.exit(1)

    cursor_path = sys.argv[1].strip().strip('"').strip("'")

    if not os.path.isdir(cursor_path):
        print(f"ERROR: Folder not found: {cursor_path}")
        print("Make sure you've granted access to the .cursor folder and the path is correct.")
        sys.exit(1)

    projects_path = os.path.join(cursor_path, "projects")
    if not os.path.isdir(projects_path):
        print(f"ERROR: No 'projects' folder found inside {cursor_path}")
        print("This doesn't look like a Cursor data folder.")
        sys.exit(1)

    print(f"\nScanning: {cursor_path}")
    print("─" * 60)

    project_slugs = sorted(os.listdir(projects_path))
    projects = []

    for slug in project_slugs:
        project_path = os.path.join(projects_path, slug)
        if not os.path.isdir(project_path):
            continue
        info = scan_project(project_path, slug)
        if info:
            projects.append(info)

    if not projects:
        print("No Cursor agent sessions found in this folder.")
        sys.exit(0)

    # Sort by most recently active
    projects.sort(key=lambda p: p["newest_session"], reverse=True)

    print(f"\nFound {len(projects)} project(s) with agent sessions:\n")
    print(f"  {'#':<4} {'Project':<45} {'Sessions':>8} {'Last Active':>12} {'Size':>8}")
    print(f"  {'─'*4} {'─'*45} {'─'*8} {'─'*12} {'─'*8}")

    for i, p in enumerate(projects, 1):
        print(
            f"  {i:<4} {p['project_slug'][:45]:<45} "
            f"{p['session_count']:>8} "
            f"{p['newest_session']:>12} "
            f"{format_size(p['total_size_kb']):>8}"
        )

    # Stats
    total_sessions = sum(p["session_count"] for p in projects)
    total_size_kb = sum(p["total_size_kb"] for p in projects)
    print(f"\n  Total: {total_sessions} sessions across {len(projects)} projects  ({format_size(total_size_kb)})")

    # Write report
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    report_path = os.path.join(base_dir, "discovery_report.json")
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump({
            "cursor_path": cursor_path,
            "scanned_at": datetime.now(tz=timezone.utc).isoformat(),
            "projects": projects
        }, f, indent=2, ensure_ascii=False)

    print(f"\nFull report saved to: discovery_report.json")
    print()
    print("Next step: choose which project(s) to import, then run:")
    print('  python scripts/import_cursor.py "PATH_TO_.CURSOR" "project-slug"')
    print('  Add --days 30 to import only sessions from the last 30 days.')


if __name__ == "__main__":
    main()
