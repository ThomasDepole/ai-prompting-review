"""
extract_sessions.py
-------------------
Step 1 of the AI Prompting Pattern Review process.

Reads all Cursor session JSONL files from ingestion/cursor-chats/ and
produces session_data.json in the project root, ready for analyse_sessions.py.

Usage (run from the project root):
    python scripts/extract_sessions.py

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

import json
import os
import sys

# ── Config ────────────────────────────────────────────────────────────────────

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INGESTION_DIR = os.path.join(BASE_DIR, "ingestion", "cursor-chats")
OUTPUT_FILE = os.path.join(BASE_DIR, "session_data.json")


# ── Helpers ───────────────────────────────────────────────────────────────────

def extract_project(project_path, project_name):
    """Extract all sessions from a single project directory."""
    sessions = []

    for session_id in sorted(os.listdir(project_path)):
        session_dir = os.path.join(project_path, session_id)
        if not os.path.isdir(session_dir):
            continue

        fpath = os.path.join(session_dir, f"{session_id}.jsonl")
        if not os.path.exists(fpath):
            continue

        # Count subagent directories (auto-spawned by Cursor agent)
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


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    if not os.path.isdir(INGESTION_DIR):
        print(f"ERROR: Ingestion directory not found: {INGESTION_DIR}")
        sys.exit(1)

    all_sessions = []
    project_names = sorted(os.listdir(INGESTION_DIR))

    for project_name in project_names:
        project_path = os.path.join(INGESTION_DIR, project_name)
        if not os.path.isdir(project_path):
            continue
        # Skip the README file
        if project_name.upper().startswith("README"):
            continue

        sessions = extract_project(project_path, project_name)
        all_sessions.extend(sessions)

        print(f"\n=== {project_name} ===")
        print(f"  {len(sessions)} sessions extracted")
        for s in sessions:
            sub_note = f" | subagents: {s['subagent_count']}" if s["has_subagents"] else ""
            print(f"  {s['id'][:8]}... | user: {s['user_turns']} | assistant: {s['assistant_turns']}{sub_note}")

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
