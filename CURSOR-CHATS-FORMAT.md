# Cursor Chat Storage Format — Research Notes

**Discovered:** March 2026  
**Status:** Confirmed working via live database inspection

---

## Background

When attempting to extract chat history for a developer who did not use persistent Cursor workspace folders, the standard `agent-transcripts` JSONL approach yielded no data. Investigation of multiple developers' `.cursor` folders revealed that Cursor stores a second type of session in a completely separate location and format — but this store is **not present on all machines**.

---

## Two Storage Locations — Not Interchangeable

Cursor uses **two different storage mechanisms** for two different interaction modes. They are **additive, not overlapping** — a session UUID confirmed present in one store was confirmed absent from the other.

| Feature | Storage Location | Format |
|---|---|---|
| Cursor CLI chat sessions | `~/.cursor/chats/` | SQLite (`.db`) |
| Agent / background agent mode | `~/.cursor/projects/[slug]/agent-transcripts/` | JSONL |

### When each store is used

**`~/.cursor/chats/`** is written to when a developer uses **Cursor CLI** (`cursor` run from the terminal). It:
- Is only present on machines where Cursor CLI has been installed
- Spans all folders in a single store (keyed by workspace hash) — CLI usage is not tied to a specific codebase
- Stores full conversation threads: user prompts, assistant responses, and tool call results

**Evidence for the CLI hypothesis:**
- The `chats/` folder was absent on two developers' machines who do not have Cursor CLI installed
- The one developer who has `chats/` also has `cli-config.json` in their `.cursor/` folder — a file only created when the CLI is used
- The oldest chat session on that machine dates to the same day the developer researched how to install Cursor CLI (confirmed via browser history)
- All chat workspace paths reflect arbitrary folders (including `C:\temp`), consistent with CLI usage from any directory rather than IDE usage from a project workspace

**`agent-transcripts/`** is written to when agent / composer mode is triggered inside the Cursor IDE. It:
- Is always workspace-scoped — the agent operates on files and needs project context
- Represents fewer but typically more complex sessions (multi-step autonomous tasks)
- Lives inside `~/.cursor/projects/[slug]/` so sessions are tied to a specific project
- Only exists for persistent workspaces — temp-path projects won't accumulate transcripts

### Who has a `chats/` folder

**Not universal.** Only developers who have installed and used Cursor CLI will have `~/.cursor/chats/`. Developers who use Cursor exclusively through the IDE will have only `agent-transcripts/`. Always check for the folder's existence before assuming it contains data.

To detect it: look for `~/.cursor/chats/` (macOS) or `C:\Users\[username]\.cursor\chats\` (Windows). If the folder exists and is non-empty, ask the developer whether to include CLI chat sessions in the review.

### Value for the prompting review

Both stores contain the developer's actual prompt text and are equally scoreable against the 9-category rubric. The difference is in character, not quality:

| | `~/.cursor/chats/` | `agent-transcripts/` |
|---|---|---|
| Who has it | CLI users only | All Cursor IDE users |
| Volume | Varies — depends on CLI usage frequency | Depends on agent mode usage |
| Prompt character | Mixed — quick questions to full tasks, across any folder | Higher complexity on average — agent tasks tend to be multi-step |
| Signal for review | Breadth across ad-hoc usage | Depth — how the developer structures larger delegated tasks |

---

## Folder Structure — `~/.cursor/chats/`

```
~/.cursor/chats/
  └── [workspace-hash]/           ← hash of the workspace path
        └── [session-uuid]/       ← UUID for each individual chat session
              ├── store.db        ← SQLite database — all conversation data
              ├── store.db-shm    ← SQLite shared memory (WAL mode)
              └── store.db-wal    ← SQLite write-ahead log (may contain unflushed data)
```

**Windows path:** `C:\Users\[username]\.cursor\chats\`  
**macOS path:** `~/.cursor/chats/`

Each workspace hash folder maps to one workspace/project path. A single workspace can have multiple session UUIDs (one per conversation started). Multiple workspace hashes may be present — one per distinct project the developer has used.

---

## Database Schema

Each `store.db` has two tables:

```sql
CREATE TABLE blobs (
    id   TEXT,   -- SHA256 hex hash of the content
    data BLOB    -- raw content (JSON or Protocol Buffers)
);

CREATE TABLE meta (
    key   TEXT,
    value TEXT   -- hex-encoded JSON
);
```

---

## Meta Table

The `meta` table has a single row (key `0`) whose value is **hex-encoded JSON**:

```python
import sqlite3, json
conn = sqlite3.connect("store.db")
raw = conn.execute("SELECT value FROM meta WHERE key='0'").fetchone()[0]
meta = json.loads(bytes.fromhex(raw).decode("utf-8"))
```

Decoded structure:

```json
{
  "agentId": "014e9208-7db4-4706-844d-5b01df53f1cc",
  "latestRootBlobId": "7eb526f4c4dea28007249c13bb00d26cf3b13057f5665d5a3e74645cac2282bb",
  "name": "Raid Log Debugger",
  "mode": "default",
  "createdAt": 1773757901894,
  "lastUsedModel": "claude-4.6-sonnet-medium"
}
```

| Field | Description |
|---|---|
| `agentId` | UUID matching the session folder name |
| `latestRootBlobId` | Entry point into the blob graph — start here |
| `name` | Human-readable session title (auto-generated by Cursor) |
| `mode` | Chat mode (`"default"`, etc.) |
| `createdAt` | Unix timestamp in milliseconds |
| `lastUsedModel` | Last model used in this session |

---

## Blobs Table

The `blobs` table is a **content-addressable store** where each blob's `id` is the SHA256 hash of its `data`. Blobs come in two types:

### Type 1 — Root / Index Blob (Protocol Buffers)

The blob identified by `latestRootBlobId` is not JSON — it is a simple **Protocol Buffers** structure encoding a flat ordered list of blob IDs. Each entry references one conversation turn.

Wire format: repeated `0x0a` (field 1, wire type 2) + `0x20` (length = 32) + 32 raw bytes (the blob ID).

```python
def parse_root_blob(data):
    """Extract blob IDs from the protobuf root blob."""
    ids = []
    i = 0
    while i < len(data):
        if i + 2 > len(data):
            break
        if data[i] == 0x0a:          # field 1, length-delimited
            length = data[i + 1]     # always 32 for a SHA256 hash
            if i + 2 + length <= len(data):
                ids.append(data[i + 2 : i + 2 + length].hex())
                i += 2 + length
            else:
                break
        else:
            break
    return ids
```

### Type 2 — Message Blobs (JSON)

All other blobs are UTF-8 encoded JSON objects representing individual conversation turns. The `role` field determines the turn type:

| Role | Description |
|---|---|
| `"system"` | System prompt injected by Cursor — not user-authored, skip for analysis |
| `"user"` | User message — contains the developer's actual prompts |
| `"assistant"` | AI response |
| `"tool"` | Tool call result (file reads, shell commands, etc.) |

**User message structure:**
```json
{
  "role": "user",
  "content": "<user_info>\nOS Version: ...\n<user_query>\nThe actual prompt text here\n</user_query>"
}
```

The `content` field is a **plain string** (not an array). It contains the developer's prompt embedded within Cursor-injected XML blocks.

---

## Critical: Extracting the Actual Prompt Text

This is the most important parsing detail for producing clean analysis data.

Cursor prepends injected context to **every** user message in the chat format. The structure is:

```
<user_info>             ← always present — OS, workspace path, date, etc.
...
</user_info>

<open_and_recently_viewed_files>   ← often present
...
</open_and_recently_viewed_files>

<user_query>            ← the developer's actual prompt
...
</user_query>
```

**Always extract `<user_query>` content as the canonical prompt text.** Storing the full raw string will pollute analysis with repeated system context rather than the developer's actual words.

```python
import re

def extract_user_query(content):
    """
    Extract the developer's actual prompt from a user message blob.
    Falls back to the full content if no <user_query> tag is present
    (can happen on very short or single-turn sessions).
    """
    match = re.search(r"<user_query>(.*?)</user_query>", content, re.DOTALL)
    if match:
        return match.group(1).strip()
    # No tag — strip known injected blocks and return remainder
    content = re.sub(r"<user_info>.*?</user_info>", "", content, flags=re.DOTALL)
    content = re.sub(r"<open_and_recently_viewed_files>.*?</open_and_recently_viewed_files>", "", content, flags=re.DOTALL)
    return content.strip()
```

**Keep the raw content too** if you need to detect `@` file references, `<attached_files>`, or `<cursor_commands>` — those live in the injected wrapper, not inside `<user_query>`.

### Contrast with `agent-transcripts` format

The JSONL format used by `agent-transcripts` stores the user message text directly in a structured field, so the same `<user_query>` extraction applies but was already handled in the original `extract_sessions.py`. The key difference is the outer wrapping:

| Format | User message location |
|---|---|
| `.cursor/chats/` SQLite | `blob["content"]` — plain string with injected XML wrapper |
| `agent-transcripts/` JSONL | `obj["message"]["content"][n]["text"]` — structured list, same XML wrapper inside |

Both need `<user_query>` extraction. The structural path to get there differs.

---

## Complete Extraction Example

The goal is to produce output compatible with the existing `session_data.json` format so the rest of the analysis pipeline (`analyse_sessions.py` onwards) works unchanged.

```python
import sqlite3
import json
import os
import re


def extract_chat_sessions(chats_root):
    """
    Extract all user messages from ~/.cursor/chats/.

    chats_root: path to the .cursor/chats/ directory
    Returns: list of session dicts compatible with session_data.json format
    """
    sessions = []

    for workspace_hash in os.listdir(chats_root):
        workspace_dir = os.path.join(chats_root, workspace_hash)
        if not os.path.isdir(workspace_dir):
            continue

        for session_uuid in os.listdir(workspace_dir):
            session_dir = os.path.join(workspace_dir, session_uuid)
            db_path = os.path.join(session_dir, "store.db")
            if not os.path.exists(db_path):
                continue

            session = _extract_session(db_path, session_uuid, workspace_hash)
            if session and session["user_turns"] > 0:
                sessions.append(session)

    return sessions


def _extract_session(db_path, session_uuid, workspace_hash):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    try:
        raw = cur.execute("SELECT value FROM meta WHERE key='0'").fetchone()
        if not raw:
            return None
        meta = json.loads(bytes.fromhex(raw[0]).decode("utf-8"))
        root_id = meta.get("latestRootBlobId")
        if not root_id:
            return None

        root_data = cur.execute("SELECT data FROM blobs WHERE id=?", (root_id,)).fetchone()
        if not root_data:
            return None
        child_ids = _parse_root_blob(root_data[0])

        user_messages = []
        assistant_turns = 0

        for bid in child_ids:
            blob = cur.execute("SELECT data FROM blobs WHERE id=?", (bid,)).fetchone()
            if not blob:
                continue
            try:
                obj = json.loads(blob[0].decode("utf-8"))
                role = obj.get("role", "")
                if role == "user":
                    raw_content = obj.get("content", "")
                    # Store the extracted query — this is what analyse_sessions.py
                    # and the scoring rubric expect to read
                    user_messages.append(extract_user_query(raw_content))
                elif role == "assistant":
                    assistant_turns += 1
            except (UnicodeDecodeError, json.JSONDecodeError):
                pass  # protobuf / binary blobs — skip

        return {
            "project": workspace_hash,        # or derive a label from workspace path if available
            "id": session_uuid,
            "name": meta.get("name", ""),      # extra field — not in JSONL sessions
            "has_subagents": False,
            "subagent_count": 0,
            "total_lines": len(child_ids),
            "user_turns": len(user_messages),
            "assistant_turns": assistant_turns,
            "user_messages": user_messages,
        }

    finally:
        conn.close()


def extract_user_query(content):
    match = re.search(r"<user_query>(.*?)</user_query>", content, re.DOTALL)
    if match:
        return match.group(1).strip()
    content = re.sub(r"<user_info>.*?</user_info>", "", content, flags=re.DOTALL)
    content = re.sub(r"<open_and_recently_viewed_files>.*?</open_and_recently_viewed_files>", "", content, flags=re.DOTALL)
    return content.strip()


def _parse_root_blob(data):
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
```

---

## Practical Notes for Extraction

**WAL mode:** The `.db-wal` file may contain recently written data not yet checkpointed into the main `.db`. Python's `sqlite3` module handles WAL transparently — no special handling needed when reading.

**Copying for offline analysis:** Copy all three files (`store.db`, `store.db-shm`, `store.db-wal`) together. Copying only `store.db` may miss the most recent messages from active sessions.

**Session naming:** The `name` field in meta is auto-generated by Cursor (a short summary of the first exchange). Useful for labelling sessions in output — the JSONL format has no equivalent.

**Empty sessions:** Some sessions have 0 user turns (chat opened but nothing typed). Filter these out — `if session["user_turns"] > 0`.

**`project` field:** The workspace hash is not human-readable. A readable project label is derived from the `Workspace Path:` line inside the `<user_info>` block of the first user message — specifically the final path component (e.g. `MyProject` from `C:\Users\name\Projects\MyProject`). The workspace hash is used as a fallback if parsing fails. This is the canonical approach used by `extract_sessions.py`.

---

## What This Means for the Import Process

The goal is for `extract_sessions.py` to produce a single `session_data.json` that merges sessions from both sources. Since both produce the same output shape, `analyse_sessions.py` and the full scoring pipeline work unchanged.

Recommended approach for `extract_sessions.py`:

1. Accept a `--chats PATH` flag pointing to a `.cursor/chats/` directory (in addition to the existing `--source` and ingestion-folder modes)
2. When `--chats` is supplied, read SQLite sessions using the extractor above
3. Merge with any JSONL sessions from the same run into a single `session_data.json`
4. For ingested data (offline exports), support dropping the `chats/` folder alongside the existing `cursor-chats/` folder in `ingestion/`

Both formats are fully compatible with the 9-category scoring rubric — the extraction layer is the only part that differs.

---

## Open Questions

- Are there blob roles beyond the four (`system`, `user`, `assistant`, `tool`) observed here?
- Does agent mode triggered from the chat panel (rather than the background agent) write to `.cursor/chats/` or to `agent-transcripts/`?

**Resolved:**
- _Workspace hash → project name:_ Derived from `Workspace Path:` in the `<user_info>` block of the first user message. Final path component used as the label; hash is the fallback. Implemented in `extract_sessions.py` (`_derive_project_label`).
- _Why some developers have no `chats/` folder:_ Initially assumed to be about workspace type (persistent vs temp). **Revised:** the `chats/` folder is tied to **Cursor CLI installation**. Confirmed across three developers — the two without CLI have no `chats/` folder; the one with CLI does. The oldest chat session correlates to the day the CLI was installed (confirmed via browser history). The `cli-config.json` file in `.cursor/` is a secondary indicator but may be created later (on first terminal invocation) rather than at install time.
