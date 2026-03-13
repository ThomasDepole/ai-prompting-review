# AI Prompting Review — Claude Bootstrap

> **This file is intended for Claude (Cowork / Claude Code) only.**
> If you are unsure which tool you are running in, ask the user to confirm before proceeding.
> If you are running in Cursor, stop reading this file and follow `.cursor/rules/prompting-review.mdc` instead.

This is an AI prompting pattern analysis workspace.

Read `PROCESS.md` before doing anything else. It covers setup and Steps 0–3. The process is split across three files — load each only when you reach that stage:

| File | Load when |
|---|---|
| `PROCESS.md` | At session start — setup, Steps 0–3 |
| `PROCESS.review.md` | After Step 3 — Stage 1: scoring and scratch pad |
| `PROCESS.report.md` | After Stage 1 — Stage 2: report generation |

When ready, follow Step 0 in `PROCESS.md` — confirm the developer's name before starting.

---

## Importing Cursor Chat History

If the user says they want to find their Cursor chats, import sessions, or doesn't have anything in the ingestion folder yet, follow this flow:

### Step A — Find out their OS

Ask whether they're on **Windows** or **macOS** if it isn't already obvious from context.

### Step B — Get the path to their .cursor folder

Before calling `request_cowork_directory`, you need to know the path. Give the user three options and let them pick whichever is easiest:

---

> **To import your Cursor session history, I need the path to your `.cursor` folder. Pick whichever option is easiest:**
>
> **Option A — Give me your user folder path** (I'll find `.cursor` from there)
> - Windows example: `C:\Users\YourName`
> - macOS example: `/Users/yourname`
>
> **Option B — Give me the full path to `.cursor` directly**
> - Windows example: `C:\Users\YourName\.cursor`
> - macOS example: `/Users/yourname/.cursor`
>
> **Option C — Drop your sessions manually** — if you've already located the files, just copy your session folders into the `ingestion/cursor-chats/` folder in this workspace and let me know. I'll skip the import step and go straight to analysis.
>
> **How to find your user folder if you're not sure:**
> - **Windows:** Open File Explorer and paste `%USERPROFILE%` into the address bar, then press Enter. That opens your user folder — copy the full path from the address bar.
> - **macOS:** Open Finder and press `Cmd+Shift+H` to go to your home folder. The path shows in the title bar (right-click the folder name to copy it). Note: `.cursor` is a hidden folder — press `Cmd+Shift+.` to show hidden files if you want to confirm it's there.

---

Once you have the path:

- If they gave **Option A** (user folder), append `\.cursor` (Windows) or `/.cursor` (macOS) to construct the full path.
- If they gave **Option B** (full path ending in `.cursor`), use it directly.
- If they chose **Option C**, skip to Step F — the sessions are already in `ingestion/cursor-chats/`.

Then call `request_cowork_directory` with the `.cursor` path and tell the user: *"I'm going to ask for access to your .cursor folder — that's where Cursor stores all your agent session history. You'll see a permission prompt to approve it."*

### Step C — Run the discovery script

Once access is granted, run:

```
python scripts/discover_cursor.py "MOUNTED_PATH_TO_.CURSOR"
```

The mounted path will be the path that was granted — use it exactly as provided by the user or as shown in the directory access confirmation.

Show the user the output table. It lists every Cursor project with session counts, last-active date, and size.

### Step D — Ask which projects to import

Ask the user: *"Which of these projects would you like to import for the review? You can pick one, several, or all of them. If you only want recent sessions, I can filter to the last N days."*

### Step E — Run the import script

Once they've chosen, run:

```
python scripts/import_cursor.py "MOUNTED_PATH_TO_.CURSOR" "project-slug" --days N
```

Omit `--days` if they want all sessions. Use multiple project slugs separated by spaces if they chose more than one.

### Step F — Proceed with the analysis

After import, the sessions are in `ingestion/cursor-chats/` and the normal analysis workflow applies. Ask for the developer's name (Step 0 in PROCESS.md) and continue from there.

---

## Quick Reference — Script Order

```
1. scripts/discover_cursor.py    ← find available sessions in .cursor
2. scripts/import_cursor.py      ← copy chosen sessions into ingestion/
3. scripts/extract_sessions.py   ← extract user messages → session_data.json
4. scripts/analyse_sessions.py   ← compute stats + sample → analysis_stats.json
5. Load PROCESS.review.md        ← Stage 1: read sessions from session_data.json, score, write scoring_scratch.json
6. Load PROCESS.report.md        ← Stage 2: generate 3 output files from scoring_scratch.json
```
