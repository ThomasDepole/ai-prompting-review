# ingestion/cursor/chats/

Drop zone for Cursor CLI chat sessions (SQLite format).

**This folder is only relevant for developers who have Cursor CLI installed.** The
`~/.cursor/chats/` directory on a developer's machine is created by the Cursor CLI
(`cursor` run from a terminal) and is not present on machines without it.

This folder mirrors the structure of `~/.cursor/chats/` on the developer's machine.
Copy the workspace hash folder(s) here — the extraction script reads the SQLite
`store.db` files directly.

## Expected structure

```
ingestion/cursor/chats/
  └── [workspace-hash]/            ← copy from ~/.cursor/chats/
        └── [session-uuid]/
              ├── store.db         ← required
              ├── store.db-shm     ← copy if present
              └── store.db-wal     ← copy if present
```

Copy all three files together (`store.db`, `store.db-shm`, `store.db-wal`) to avoid
missing recently written messages from active sessions.

## How to find your files

**Windows:** `C:\Users\[username]\.cursor\chats\`
**macOS:** `~/.cursor/chats/`

If the folder does not exist on the developer's machine, they do not have Cursor CLI
installed and this ingestion path is not applicable.

## When NOT to use this folder

If you are running the review inside Cursor on the developer's own machine, use the
`--chats` flag instead — no file copying is needed:

```
python scripts/extract_sessions.py --chats C:\Users\[username]\.cursor\chats
```

**These files are excluded from git.** Only this README is tracked.
