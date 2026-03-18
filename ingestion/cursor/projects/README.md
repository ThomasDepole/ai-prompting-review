# ingestion/cursor/projects/

Drop zone for Cursor agent/composer session files (JSONL format).

This folder mirrors the structure of `~/.cursor/projects/` on the developer's machine.
Copy the entire contents of that folder here — the extraction script navigates into
each project's `agent-transcripts/` subfolder automatically.

## Expected structure

```
ingestion/cursor/projects/
  └── [project-slug]/              ← copy from ~/.cursor/projects/
        └── agent-transcripts/
              └── [uuid]/
                    └── [uuid].jsonl
```

## How to find your files

**Windows:** `C:\Users\[username]\.cursor\projects\`
**macOS:** `~/.cursor/projects/`

Copy the project slug folder(s) you want to include directly into this folder.
You do not need to copy every project — just the ones relevant to the review.

## When NOT to use this folder

If you are running the review inside Cursor on the developer's own machine, use the
`--source` flag instead — no file copying is needed:

```
python scripts/extract_sessions.py --source C:\Users\[username]\.cursor\projects
```

**These files are excluded from git.** Only this README is tracked.
