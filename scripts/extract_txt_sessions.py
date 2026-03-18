"""
extract_txt_sessions.py
-----------------------
Fallback extraction script for when ingestion sessions are in plain-text (.txt) format
rather than the standard JSONL format expected by extract_sessions.py.

When to use:
  Run extract_sessions.py first (default). If it reports "Total sessions: 0" but files
  are clearly present in ingestion/cursor/projects/, check whether those files are .txt
  (Format B) rather than [uuid]/[uuid].jsonl subdirectories (Format A). If .txt files
  are found, run this script instead.

Expected ingestion structure (Format B):
  ingestion/cursor/projects/[slug]/agent-transcripts/[uuid].txt

File format:
  user:
  <user_query>
  [prompt text]
  </user_query>

  assistant:
  [response...]

  user:
  <user_query>
  [next prompt]
  </user_query>
  ...

Usage (run from the project root):

  All sessions, no time filter:
    python scripts/extract_txt_sessions.py

  Last 30 days only:
    python scripts/extract_txt_sessions.py --days 30

  Specific projects only:
    python scripts/extract_txt_sessions.py --projects slug-a slug-b

  Combined:
    python scripts/extract_txt_sessions.py --days 30 --projects slug-a slug-b

Arguments:
  --days N         Only include sessions whose file was modified in the last N days.
  --projects ...   One or more project slugs to include. Omit to include all projects.

Output:
  temp/session_data.json — identical format to extract_sessions.py output.
  All downstream steps (analyse_sessions.py, scoring, report generation) are unchanged.
"""

import argparse
import json
import os
import re
import sys
from datetime import datetime, timedelta, timezone


# ── Config ────────────────────────────────────────────────────────────────────

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INGESTION_PROJECTS_DIR = os.path.join(BASE_DIR, "ingestion", "cursor", "projects")
TEMP_DIR = os.path.join(BASE_DIR, "temp")
OUTPUT_FILE = os.path.join(TEMP_DIR, "session_data.json")


# ── Helpers ───────────────────────────────────────────────────────────────────

def extract_user_queries(text):
    return re.findall(r"<user_query>(.*?)</user_query>", text, re.DOTALL)


def count_assistant_turns(text):
    return len(re.findall(r"\nassistant:", text))


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Extract user messages from .txt format Cursor session transcripts."
    )
    parser.add_argument(
        "--days",
        type=int,
        metavar="N",
        help="Only include sessions whose file was modified in the last N days.",
    )
    parser.add_argument(
        "--projects",
        nargs="+",
        metavar="SLUG",
        help="One or more project slugs to include. Omit to include all projects.",
    )
    args = parser.parse_args()

    cutoff = None
    if args.days:
        cutoff = datetime.now(tz=timezone.utc) - timedelta(days=args.days)
        print(f"Filtering to sessions from the last {args.days} days (since {cutoff.date()}).")

    if args.projects:
        print(f"Project filter: {', '.join(args.projects)}")

    if not os.path.isdir(INGESTION_PROJECTS_DIR):
        print(f"ERROR: Ingestion projects directory not found: {INGESTION_PROJECTS_DIR}")
        sys.exit(1)

    all_sessions = []

    for slug in sorted(os.listdir(INGESTION_PROJECTS_DIR)):
        if args.projects and slug not in args.projects:
            continue

        project_path = os.path.join(INGESTION_PROJECTS_DIR, slug)
        if not os.path.isdir(project_path):
            continue

        transcripts_dir = os.path.join(project_path, "agent-transcripts")
        if not os.path.isdir(transcripts_dir):
            continue

        slug_sessions = []
        for fname in sorted(os.listdir(transcripts_dir)):
            if not fname.endswith(".txt"):
                continue

            session_id = fname[:-4]  # strip .txt
            fpath = os.path.join(transcripts_dir, fname)

            if cutoff is not None:
                mtime = datetime.fromtimestamp(os.stat(fpath).st_mtime, tz=timezone.utc)
                if mtime < cutoff:
                    continue

            with open(fpath, encoding="utf-8", errors="replace") as f:
                content = f.read()

            queries = [q.strip() for q in extract_user_queries(content) if q.strip()]
            if not queries:
                continue

            asst_turns = count_assistant_turns(content)
            slug_sessions.append({
                "project": slug,
                "id": session_id,
                "source": "agent-transcripts",
                "has_subagents": False,
                "subagent_count": 0,
                "total_lines": content.count("\n"),
                "user_turns": len(queries),
                "assistant_turns": asst_turns,
                "user_messages": queries,
            })

        if slug_sessions:
            all_sessions.extend(slug_sessions)
            print(f"\n=== {slug} ===")
            print(f"  {len(slug_sessions)} sessions extracted")
            for s in slug_sessions:
                print(
                    f"  {s['id'][:8]}... | user: {s['user_turns']} "
                    f"| asst: {s['assistant_turns']}"
                )

    os.makedirs(TEMP_DIR, exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(all_sessions, f, indent=2, ensure_ascii=False)

    total_user = sum(s["user_turns"] for s in all_sessions)
    total_asst = sum(s["assistant_turns"] for s in all_sessions)
    print(f"\n{'-' * 50}")
    print(f"Total sessions   : {len(all_sessions)}")
    print(f"Total user turns : {total_user}")
    print(f"Total asst turns : {total_asst}")
    print(f"\nOutput written to: {OUTPUT_FILE}")
    print("Next step: python scripts/analyse_sessions.py")


if __name__ == "__main__":
    main()
