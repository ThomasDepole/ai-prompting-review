"""
extract_sessions.py
-------------------
Step 1 of the AI Prompting Pattern Review process.

By default, reads all Cursor session JSONL files from ingestion/cursor-chats/ and
produces session_data.json in the project root, ready for analyse_sessions.py.

Optionally, use --source to read directly from a .cursor/projects/ directory,
skipping the ingestion import step entirely (used by the Cursor-native workflow).

Usage (run from the project root):

  Default — reads from ingestion/cursor-chats/:
    python scripts/extract_sessions.py

  Direct from .cursor — skips ingestion entirely:
    python scripts/extract_sessions.py --source /Users/name/.cursor/projects
    python scripts/extract_sessions.py --source /Users/name/.cursor/projects --days 30
    python scripts/extract_sessions.py --source /Users/name/.cursor/projects --projects slug-a slug-b
    python scripts/extract_sessions.py --source /Users/name/.cursor/projects --days 30 --projects slug-a

Arguments:
  --source PATH    Path to a .cursor/projects/ directory. When supplied, reads
                   agent-transcripts directly from there instead of ingestion/.
  --days N         Only include sessions modified in the last N days (requires --source).
  --projects ...   One or more project slugs to include (requires --source).
                   Omit to include all projects found at the source path.

Output:
  session_data.json  — one entry per session, per project

Session structure in output:
  {
    "project": "project-name",
    "id": "uuid",
    "has_subagents": true,
    "subagent_count": 3,
    "total_lines": 45,
    "user_turns": 10,
    "assistant_turns": 27,
    "user_messages": ["...", "..."]
  }
"""

import argparse
import json
import os
import sys
from datetime import datetime, timedelta, timezone


# ── Config ────────────────────────────────────────────────────────────────────

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INGESTION_DIR = os.path.join(BASE_DIR, "ingestion", "cursor-chats")
TEMP_DIR = os.path.join(BASE_DIR, "temp")
OUTPUT_FILE = os.path.join(TEMP_DIR, "session_data.json")


# ── Helpers ───────────────────────────────────────────────────────────────────

def extract_project(project_path, project_name, cutoff=None):
    """Extract all sessions from a single project directory."""
    sessions = []

    for session_id in sorted(os.listdir(project_path)):
        session_dir = os.path.join(project_path, session_id)
        if not os.path.isdir(session_dir):
            continue

        fpath = os.path.join(session_dir, f"{session_id}.jsonl")
        if not os.path.exists(fpath):
            continue

        if cutoff is not None:
            mtime = datetime.fromtimestamp(os.stat(fpath).st_mtime, tz=timezone.utc)
            if mtime < cutoff:
                continue

        subagents_dir = os.path.join(session_dir, "subagents")
        has_subagents = os.path.isdir(subagents_dir)
        subagent_count = 0
        if has_subagents:
            subagent_count = sum(
                1 for f in os.listdir(subagents_dir)
                if f.endswith(".jsonl")
            )

        with open(fpath, encoding="utf-8") as f:
            lines = f.readlines()

        user_msgs = []
        assistant_turns = 0

        for line in lines:
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                continue

            role = obj.get("role", "")
            if role == "user":
                content = obj.get("message", {}).get("content", [])
                for c in content:
                    if c.get("type") == "text":
                        user_msgs.append(c["text"])
            elif role == "assistant":
                assistant_turns += 1

        sessions.append({
            "project": project_name,
            "id": session_id,
            "has_subagents": has_subagents,
            "subagent_count": subagent_count,
            "total_lines": len(lines),
            "user_turns": len(user_msgs),
            "assistant_turns": assistant_turns,
            "user_messages": user_msgs,
        })

    return sessions


def collect_from_ingestion(cutoff=None):
    """Read sessions from the default ingestion/cursor-chats/ directory."""
    if not os.path.isdir(INGESTION_DIR):
        print(f"ERROR: Ingestion directory not found: {INGESTION_DIR}")
        sys.exit(1)

    all_sessions = []
    for project_name in sorted(os.listdir(INGESTION_DIR)):
        project_path = os.path.join(INGESTION_DIR, project_name)
        if not os.path.isdir(project_path):
            continue
        if project_name.upper().startswith("README"):
            continue

        sessions = extract_project(project_path, project_name, cutoff=cutoff)
        all_sessions.extend(sessions)
        _print_project_summary(project_name, sessions)

    return all_sessions


def collect_from_source(source_path, project_filter=None, cutoff=None):
    """
    Read sessions directly from a .cursor/projects/ directory.

    Expected structure:
      [source_path]/[project-slug]/agent-transcripts/[uuid]/[uuid].jsonl

    project_filter: list of project slugs to include, or None for all.
    cutoff: datetime — skip sessions modified before this date.
    """
    if not os.path.isdir(source_path):
        print(f"ERROR: Source path not found: {source_path}")
        sys.exit(1)

    all_sessions = []

    for slug in sorted(os.listdir(source_path)):
        if project_filter and slug not in project_filter:
            continue

        transcripts_dir = os.path.join(source_path, slug, "agent-transcripts")
        if not os.path.isdir(transcripts_dir):
            continue

        sessions = extract_project(transcripts_dir, slug, cutoff=cutoff)
        if sessions:
            all_sessions.extend(sessions)
            _print_project_summary(slug, sessions)

    return all_sessions


def _print_project_summary(project_name, sessions):
    print(f"\n=== {project_name} ===")
    print(f"  {len(sessions)} sessions extracted")
    for s in sessions:
        sub_note = f" | subagents: {s['subagent_count']}" if s["has_subagents"] else ""
        print(f"  {s['id'][:8]}... | user: {s['user_turns']} | assistant: {s['assistant_turns']}{sub_note}")


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Extract user messages from Cursor sessions into session_data.json."
    )
    parser.add_argument(
        "--source",
        metavar="PATH",
        help="Path to a .cursor/projects/ directory. Reads agent-transcripts directly, "
             "skipping the ingestion folder.",
    )
    parser.add_argument(
        "--days",
        type=int,
        metavar="N",
        help="Only include sessions modified in the last N days (requires --source).",
    )
    parser.add_argument(
        "--projects",
        nargs="+",
        metavar="SLUG",
        help="One or more project slugs to include (requires --source). "
             "Omit to include all projects.",
    )
    args = parser.parse_args()

    if args.days and not args.source:
        print("ERROR: --days requires --source.")
        sys.exit(1)
    if args.projects and not args.source:
        print("ERROR: --projects requires --source.")
        sys.exit(1)

    cutoff = None
    if args.days:
        cutoff = datetime.now(tz=timezone.utc) - timedelta(days=args.days)
        print(f"Filtering to sessions modified in the last {args.days} days (since {cutoff.date()}).")

    if args.source:
        print(f"Reading directly from: {args.source}")
        if args.projects:
            print(f"Project filter: {', '.join(args.projects)}")
        all_sessions = collect_from_source(args.source, project_filter=args.projects, cutoff=cutoff)
    else:
        print(f"Reading from ingestion: {INGESTION_DIR}")
        all_sessions = collect_from_ingestion(cutoff=cutoff)

    os.makedirs(TEMP_DIR, exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(all_sessions, f, indent=2, ensure_ascii=False)

    total_user = sum(s["user_turns"] for s in all_sessions)
    total_asst = sum(s["assistant_turns"] for s in all_sessions)
    sessions_with_subagents = sum(1 for s in all_sessions if s["has_subagents"])

    print(f"\n{'─' * 50}")
    print(f"Total sessions   : {len(all_sessions)}")
    print(f"Total user turns : {total_user}")
    print(f"Total asst turns : {total_asst}")
    print(f"With subagents   : {sessions_with_subagents}  (positive signal — prompt triggered agent decomposition)")
    print(f"\nOutput written to: {OUTPUT_FILE}")
    print("Next step: python scripts/analyse_sessions.py")


if __name__ == "__main__":
    main()
