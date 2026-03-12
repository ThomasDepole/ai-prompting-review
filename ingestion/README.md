# ingestion/

This folder is where you drop session export files before running an analysis.

Organise files by source type using the subfolders below. Each source type may have its own file format and extraction process — see `CLAUDE.md` for details on each.

| Folder | For |
|---|---|
| `cursor-chats/` | Cursor AI session files (`.jsonl` format) |
| `other-chats/` | Future sources — ChatGPT exports, Copilot logs, etc. |

**These files are excluded from git** (see `.gitignore`). Session data is personal and should not be committed to the repository. Only the folder structure and READMEs are tracked.
