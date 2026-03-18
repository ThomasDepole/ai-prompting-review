# ingestion/

Drop zone for session files when running the review offline (e.g. in Claude Cowork,
or when reviewing someone else's sessions on a different machine).

If you are running the review inside Cursor on the developer's own machine, use the
`--source` and `--chats` flags instead — no files need to be copied here.

## Folder structure

```
ingestion/
  ├── cursor/
  │   ├── projects/   ← Cursor agent/composer sessions (JSONL)
  │   │               Mirror of ~/.cursor/projects/ — copy project slug folders here
  │   │
  │   └── chats/      ← Cursor CLI chat sessions (SQLite store.db files)
  │                   Only present for developers with Cursor CLI installed.
  │                   Mirror of ~/.cursor/chats/ — copy workspace hash folders here
  │
  └── other-chats/    ← Future: ChatGPT exports, Windsurf, Copilot, etc.
```

## What to copy where

| What to copy | From | Drop into | Who has it |
|---|---|---|---|
| Agent/composer sessions | `~/.cursor/projects/[slug]/` | `ingestion/cursor/projects/[slug]/` | All Cursor IDE users |
| CLI chat sessions | `~/.cursor/chats/[hash]/` | `ingestion/cursor/chats/[hash]/` | Cursor CLI users only |

**These files are excluded from git** (see `.gitignore`). Session data is personal
and should not be committed to the repository. Only the folder structure and READMEs
are tracked.
