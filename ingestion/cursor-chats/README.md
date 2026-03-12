# ingestion/cursor-chats/

Drop Cursor AI session files here before running an analysis.

## Expected Structure

```
cursor-chats/
└── [project-name]/          ← One folder per project (e.g. my-app)
    └── [uuid]/              ← One folder per session (UUID named by Cursor)
        └── [uuid].jsonl     ← The session file
```

## Finding Your Session Files

Not sure where Cursor stores your sessions? Just ask Claude:

> "Can you find my Cursor session files on this computer?"

Claude can search your file system and locate the `agent-transcripts` folder for you. Once found, it can help you copy the relevant sessions into this folder.

If you prefer to find them manually, the default location on Windows is:

```
C:\Users\[username]\.cursor\projects\[project-slug]\agent-transcripts\
```

And on macOS:

```
~/.cursor/projects/[project-slug]/agent-transcripts/
```

Each subfolder inside `agent-transcripts` is one session. Copy the relevant session folders into a named project subfolder here.

## Tips

- Aim for at least 10–15 sessions for a meaningful analysis.
- Group sessions by project if the developer works across multiple codebases.
- If possible, also collect the `.cursor/rules/` directory from the developer's project — cursor rules are injected silently and won't appear in the session files themselves. See `CLAUDE.md` for details.

**These files are excluded from git.** Only this README is tracked.
