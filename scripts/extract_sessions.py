"""
extract_sessions.py
-------------------
Step 1 of the AI Prompting Pattern Review process.

Reads Cursor session files and produces session_data.json in temp/, ready for
analyse_sessions.py. Supports two source formats:

  1. agent-transcripts JSONL  — ~/.cursor/projects/[slug]/agent-transcripts/
  2. Regular chats SQLite     — ~/.cursor/chats/[workspace-hash]/[uuid]/store.db

Both can be combined in a single run. The output format is identical for both
sources so the rest of the pipeline (analyse_sessions.py onwards) is unchanged.

Usage (run from the project root):

  Default — reads from ingestion/cursor/projects/ (JSONL) and ingestion/cursor/chats/ (SQLite):
    python scripts/extract_sessions.py

  Direct from .cursor — agent-transcripts only:
    python scripts/extract_sessions.py --source /Users/name/.cursor/projects
    python scripts/extract_sessions.py --source /Users/name/.cursor/projects --days 30
    python scripts/extract_sessions.py --source /Users/name/.cursor/projects --projects slug-a slug-b

  Direct from .cursor — regular chats only:
    python scripts/extract_sessions.py --chats /Users/name/.cursor/chats
    python scripts/extract_sessions.py --chats C:\\Users\\name\\.cursor\\chats --days 30

  Both sources combined:
    python scripts/extract_sessions.py --source ~/.cursor/projects --chats ~/.cursor/chats
    python scripts/extract_sessions.py --source ~/.cursor/projects --chats ~/.cursor/chats --days 30

Arguments:
  --source PATH    Path to a .cursor/projects/ directory. Reads agent-transcripts
                   JSONL files directly, skipping the ingestion folder.
  --chats PATH     Path to a .cursor/chats/ directory. Reads regular Ctrl+L chat
                   sessions from SQLite store.db files.
  --days N         Only include sessions modified/created in the last N days.
                   Works with both --source and --chats.
  --projects ...   One or more project slugs to include (applies to --source only).

Output:
  temp/session_data.json  — one entry per session, per project/workspace

Session structure in output:
  {
    "project": "project-name-or-workspace-label",
    "id": "uuid",
    "name": "Auto-generated title (chats source only)",
    "source": "agent-transcripts" | "chats",
    "has_subagents": true,
    "subagent_count": 3,
    "total_lines": 45,
    "user_turns": 10,
    "assistant_turns": 27,
    "user_messages": ["...", "..."]
  }

  Note: "name" and "source" are additive fields not present in older output.
  analyse_sessions.py and downstream scoring ignore them safely.
"""

import argparse
import json
import os
import re
import sqlite3
import sys
from datetime import datetime, timedelta, timezone


# ── Config ────────────────────────────────────────────────────────────────────

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INGESTION_PROJECTS_DIR = os.path.join(BASE_DIR, "ingestion", "cursor", "projects")
INGESTION_CHATS_DIR = os.path.join(BASE_DIR, "ingestion", "cursor", "chats")
TEMP_DIR = os.path.join(BASE_DIR, "temp")
OUTPUT_FILE = os.path.join(TEMP_DIR, "session_data.json")


# ── JSONL extraction (agent-transcripts) ──────────────────────────────────────

def extract_project_jsonl(project_path, project_name, cutoff=None):
    """Extract all sessions from a single agent-transcripts project directory."""
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
            "source": "agent-transcripts",
            "has_subagents": has_subagents,
            "subagent_count": subagent_count,
            "total_lines": len(lines),
            "user_turns": len(user_msgs),
            "assistant_turns": assistant_turns,
            "user_messages": user_msgs,
        })

    return sessions


def collect_from_ingestion_jsonl(cutoff=None):
    """
    Read JSONL sessions from the default ingestion/cursor/projects/ directory.

    Expected structure mirrors ~/.cursor/projects/:
      ingestion/cursor/projects/[project-slug]/agent-transcripts/[uuid]/[uuid].jsonl
    """
    if not os.path.isdir(INGESTION_PROJECTS_DIR):
        return []

    all_sessions = []
    for slug in sorted(os.listdir(INGESTION_PROJECTS_DIR)):
        project_path = os.path.join(INGESTION_PROJECTS_DIR, slug)
        if not os.path.isdir(project_path):
            continue

        transcripts_dir = os.path.join(project_path, "agent-transcripts")
        if not os.path.isdir(transcripts_dir):
            continue

        sessions = extract_project_jsonl(transcripts_dir, slug, cutoff=cutoff)
        if sessions:
            all_sessions.extend(sessions)
            _print_project_summary(slug, sessions, source="agent-transcripts")

    return all_sessions


def collect_from_source(source_path, project_filter=None, cutoff=None):
    """
    Read JSONL sessions directly from a .cursor/projects/ directory.

    Expected structure:
      [source_path]/[project-slug]/agent-transcripts/[uuid]/[uuid].jsonl
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

        sessions = extract_project_jsonl(transcripts_dir, slug, cutoff=cutoff)
        if sessions:
            all_sessions.extend(sessions)
            _print_project_summary(slug, sessions, source="agent-transcripts")

    return all_sessions


# ── SQLite extraction (.cursor/chats/) ────────────────────────────────────────

def _parse_root_blob(data):
    """
    Extract ordered blob IDs from the protobuf root blob.

    Wire format: repeated field 1 (length-delimited), each entry is a 32-byte
    SHA256 hash. Tag byte 0x0a (field 1, wire type 2) followed by length byte
    (always 0x20 = 32 for SHA256), followed by 32 raw bytes.
    """
    ids = []
    i = 0
    while i < len(data):
        if i + 2 > len(data):
            break
        if data[i] == 0x0a:
            length = data[i + 1]
            if i + 2 + length <= len(data):
                ids.append(data[i + 2 : i + 2 + length].hex())
                i += 2 + length
            else:
                break
        else:
            break
    return ids


def _extract_user_query(content):
    """
    Extract the developer's actual prompt from a Cursor user message.

    Cursor wraps every user message with injected context blocks. The canonical
    prompt text lives inside <user_query>...</user_query>. Falls back to stripping
    known injected blocks if the tag is absent (very short / single-turn sessions).
    """
    match = re.search(r"<user_query>(.*?)</user_query>", content, re.DOTALL)
    if match:
        return match.group(1).strip()
    content = re.sub(r"<user_info>.*?</user_info>", "", content, flags=re.DOTALL)
    content = re.sub(
        r"<open_and_recently_viewed_files>.*?</open_and_recently_viewed_files>",
        "", content, flags=re.DOTALL
    )
    return content.strip()


def _derive_project_label(first_user_content, fallback):
    """
    Derive a human-readable project label from the <user_info> block in the
    first user message. The block contains the workspace path — we take the
    last two path components as a readable label (e.g. "Claude Workspaces/MyProject").
    Falls back to the workspace hash if parsing fails.
    """
    match = re.search(r"Workspace Path:\s*(.+)", first_user_content)
    if match:
        raw_path = match.group(1).strip()
        parts = re.split(r"[\\/]", raw_path)
        parts = [p for p in parts if p]
        if parts:
            return parts[-1]
    return fallback


def _extract_sqlite_session(db_path, session_uuid, workspace_hash, cutoff):
    """
    Extract user messages from a single store.db chat session.

    Returns a session dict compatible with session_data.json, or None if the
    session should be skipped (empty, unreadable, or outside the cutoff window).
    """
    try:
        conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
    except sqlite3.OperationalError:
        # Fall back to read-write connection if read-only URI is not supported
        conn = sqlite3.connect(db_path)

    try:
        cur = conn.cursor()

        raw = cur.execute("SELECT value FROM meta WHERE key='0'").fetchone()
        if not raw:
            return None
        try:
            meta = json.loads(bytes.fromhex(raw[0]).decode("utf-8"))
        except (ValueError, UnicodeDecodeError):
            return None

        root_id = meta.get("latestRootBlobId")
        if not root_id:
            return None

        # Respect cutoff using createdAt (milliseconds epoch in meta)
        if cutoff is not None:
            created_at_ms = meta.get("createdAt")
            if created_at_ms is not None:
                created_at = datetime.fromtimestamp(
                    created_at_ms / 1000, tz=timezone.utc
                )
                if created_at < cutoff:
                    return None

        root_row = cur.execute(
            "SELECT data FROM blobs WHERE id=?", (root_id,)
        ).fetchone()
        if not root_row:
            return None

        child_ids = _parse_root_blob(root_row[0])

        user_messages = []
        assistant_turns = 0
        first_raw_content = None

        for bid in child_ids:
            blob_row = cur.execute(
                "SELECT data FROM blobs WHERE id=?", (bid,)
            ).fetchone()
            if not blob_row:
                continue
            try:
                obj = json.loads(blob_row[0].decode("utf-8"))
            except (UnicodeDecodeError, json.JSONDecodeError):
                continue

            role = obj.get("role", "")
            if role == "user":
                raw_content = obj.get("content", "")
                # content can be a plain string or an array of typed blocks
                if isinstance(raw_content, list):
                    raw_content = " ".join(
                        c.get("text", "") for c in raw_content
                        if isinstance(c, dict) and c.get("type") == "text"
                    )
                if first_raw_content is None:
                    first_raw_content = raw_content
                extracted = _extract_user_query(raw_content)
                if extracted:
                    user_messages.append(extracted)
            elif role == "assistant":
                assistant_turns += 1

        if not user_messages:
            return None

        project_label = _derive_project_label(
            first_raw_content or "", fallback=workspace_hash
        )

        return {
            "project": project_label,
            "id": session_uuid,
            "name": meta.get("name", ""),
            "source": "chats",
            "has_subagents": False,
            "subagent_count": 0,
            "total_lines": len(child_ids),
            "user_turns": len(user_messages),
            "assistant_turns": assistant_turns,
            "user_messages": user_messages,
        }

    finally:
        conn.close()


def collect_from_chats(chats_path, cutoff=None):
    """
    Read sessions from a ~/.cursor/chats/ directory (regular Ctrl+L chats).

    Expected structure:
      [chats_path]/[workspace-hash]/[session-uuid]/store.db
    """
    if not os.path.isdir(chats_path):
        print(f"ERROR: Chats path not found: {chats_path}")
        sys.exit(1)

    all_sessions = []
    workspace_session_map = {}  # workspace_hash -> list of sessions (for summary)

    for workspace_hash in sorted(os.listdir(chats_path)):
        workspace_dir = os.path.join(chats_path, workspace_hash)
        if not os.path.isdir(workspace_dir):
            continue

        for session_uuid in sorted(os.listdir(workspace_dir)):
            session_dir = os.path.join(workspace_dir, session_uuid)
            db_path = os.path.join(session_dir, "store.db")
            if not os.path.exists(db_path):
                continue

            session = _extract_sqlite_session(
                db_path, session_uuid, workspace_hash, cutoff
            )
            if session is None:
                continue

            all_sessions.append(session)
            workspace_session_map.setdefault(session["project"], []).append(session)

    for project_label, sessions in sorted(workspace_session_map.items()):
        _print_project_summary(project_label, sessions, source="chats")

    return all_sessions


def collect_from_ingestion_sqlite(cutoff=None):
    """
    Read SQLite sessions from the offline drop-zone ingestion/cursor/chats/.

    Expected structure mirrors ~/.cursor/chats/:
      ingestion/cursor/chats/[workspace-hash]/[session-uuid]/store.db

    Sessions here are treated identically to --chats live sessions.
    """
    if not os.path.isdir(INGESTION_CHATS_DIR):
        return []

    # Check if there are any store.db files at all before announcing
    has_dbs = any(
        fname == "store.db"
        for _, _, files in os.walk(INGESTION_CHATS_DIR)
        for fname in files
    )
    if not has_dbs:
        return []

    print(f"Reading SQLite sessions from ingestion: {INGESTION_CHATS_DIR}")
    return collect_from_chats(INGESTION_CHATS_DIR, cutoff=cutoff)


# ── Shared helpers ────────────────────────────────────────────────────────────

def _print_project_summary(project_name, sessions, source="agent-transcripts"):
    source_tag = f" [{source}]"
    print(f"\n=== {project_name}{source_tag} ===")
    print(f"  {len(sessions)} sessions extracted")
    for s in sessions:
        sub_note = f" | subagents: {s['subagent_count']}" if s.get("has_subagents") else ""
        name_note = f" | \"{s['name']}\"" if s.get("name") else ""
        print(
            f"  {s['id'][:8]}... | user: {s['user_turns']} "
            f"| assistant: {s['assistant_turns']}{sub_note}{name_note}"
        )


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Extract user messages from Cursor sessions into session_data.json."
    )
    parser.add_argument(
        "--source",
        metavar="PATH",
        help="Path to a .cursor/projects/ directory. Reads agent-transcripts JSONL "
             "files directly, skipping the ingestion folder.",
    )
    parser.add_argument(
        "--chats",
        metavar="PATH",
        help="Path to a .cursor/chats/ directory. Reads regular Ctrl+L chat sessions "
             "from SQLite store.db files. Can be combined with --source.",
    )
    parser.add_argument(
        "--days",
        type=int,
        metavar="N",
        help="Only include sessions modified/created in the last N days. "
             "Works with both --source and --chats.",
    )
    parser.add_argument(
        "--projects",
        nargs="+",
        metavar="SLUG",
        help="One or more project slugs to include (applies to --source only). "
             "Omit to include all projects.",
    )
    args = parser.parse_args()

    if args.projects and not args.source:
        print("ERROR: --projects requires --source.")
        sys.exit(1)

    cutoff = None
    if args.days:
        cutoff = datetime.now(tz=timezone.utc) - timedelta(days=args.days)
        print(f"Filtering to sessions from the last {args.days} days (since {cutoff.date()}).")

    all_sessions = []

    if not args.source and not args.chats:
        # Default mode — read from both ingestion drop-zones
        print(f"Reading JSONL sessions from ingestion: {INGESTION_PROJECTS_DIR}")
        jsonl_sessions = collect_from_ingestion_jsonl(cutoff=cutoff)
        all_sessions.extend(jsonl_sessions)

        sqlite_sessions = collect_from_ingestion_sqlite(cutoff=cutoff)
        all_sessions.extend(sqlite_sessions)
    else:
        if args.source:
            print(f"Reading agent-transcripts from: {args.source}")
            if args.projects:
                print(f"Project filter: {', '.join(args.projects)}")
            jsonl_sessions = collect_from_source(
                args.source, project_filter=args.projects, cutoff=cutoff
            )
            all_sessions.extend(jsonl_sessions)

        if args.chats:
            print(f"Reading regular chats from: {args.chats}")
            chat_sessions = collect_from_chats(args.chats, cutoff=cutoff)
            all_sessions.extend(chat_sessions)

    os.makedirs(TEMP_DIR, exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(all_sessions, f, indent=2, ensure_ascii=False)

    total_user = sum(s["user_turns"] for s in all_sessions)
    total_asst = sum(s["assistant_turns"] for s in all_sessions)
    sessions_with_subagents = sum(1 for s in all_sessions if s.get("has_subagents"))
    from_agent = sum(1 for s in all_sessions if s.get("source") == "agent-transcripts")
    from_chats = sum(1 for s in all_sessions if s.get("source") == "chats")

    print(f"\n{'-' * 50}")
    print(f"Total sessions   : {len(all_sessions)}")
    if from_agent or from_chats:
        print(f"  agent-transcripts : {from_agent}")
        print(f"  chats (SQLite)    : {from_chats}")
    print(f"Total user turns : {total_user}")
    print(f"Total asst turns : {total_asst}")
    if sessions_with_subagents:
        print(f"With subagents   : {sessions_with_subagents}  (positive signal — prompt triggered agent decomposition)")
    print(f"\nOutput written to: {OUTPUT_FILE}")
    print("Next step: python scripts/analyse_sessions.py")


if __name__ == "__main__":
    main()
