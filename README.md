# AI Prompting Review

A structured workspace for analysing how developers use AI coding tools — and helping them get better at it.

Feed it a developer's session history and it produces a full narrative report, an interactive HTML scorecard, and a portable markdown scorecard. The analysis covers 9 prompting dimensions scored 1–5, with concrete examples pulled directly from their sessions and specific recommendations for improvement.

Works with any AI agent. Claude users get zero-friction setup — `CLAUDE.md` loads the process automatically. Everyone else can use `STARTER_PROMPT.md` to bootstrap in seconds.

---

## Table of Contents

- [What You Get](#what-you-get)
- [Quick Start](#quick-start)
- [Importing Your Cursor Sessions](#importing-your-cursor-sessions)
- [Starter Prompts](#starter-prompts)
- [Folder Structure](#folder-structure)
- [The Scoring Rubric](#the-scoring-rubric)
- [Supported Sources](#supported-sources)
- [Privacy](#privacy)
- [Contributing](#contributing)

---

## What You Get

| Output                         | Description                                                                               |
| ------------------------------ | ----------------------------------------------------------------------------------------- |
| `[Name]-Prompting-Analysis.md` | Deep narrative report — strengths, weaknesses, patterns by session type, standout prompts |
| `[Name]-Scorecard.html`        | Interactive single-page scorecard with click-to-expand category definitions               |
| `scorecard-template.md`        | Portable markdown version of the scorecard for sharing or printing                        |

All outputs land in `reports/[Developer-Name]/[YYYY-MM]/`. If a report already exists for that person in the current month, you'll be asked whether to overwrite it or save a new versioned copy alongside it.

---

## Quick Start

**Option A — Let the AI find and import your sessions automatically**

Open this folder in Claude and say one of the [starter prompts](#starter-prompts) below. The AI will walk you through locating your `.cursor` folder and importing the sessions you want.

**Option B — Drop sessions in manually, then run the analysis**

If you already have the files, place them here:

```
ingestion/cursor-chats/[project-name]/[uuid]/[uuid].jsonl
```

Then tell the AI you're ready to run the analysis (see starter prompts below). Aim for 10–15 sessions minimum for a meaningful report.

**How to start the AI**

| Tool                              | How to start                                                                                      |
| --------------------------------- | ------------------------------------------------------------------------------------------------- |
| **Claude** (Cowork / Claude Code) | Open this folder — `CLAUDE.md` loads automatically. Use one of the starter prompts below.        |
| **Cursor**                        | Copy `CLAUDE.md` contents into `.cursorrules`, then use one of the starter prompts below.        |
| **Any other agent**               | Paste the contents of `STARTER_PROMPT.md` as your first message, then use a starter prompt.      |

---

## Importing Your Cursor Sessions

Cursor stores your session history in a hidden `.cursor` folder on your computer. The AI can find and import your sessions automatically — you just need to give it the right folder path.

**When you ask to import sessions, the AI will give you three options:**

**Option A — Give your user folder path** and the AI will find `.cursor` from there.
- Windows example: `C:\Users\YourName`
- macOS example: `/Users/yourname`

**Option B — Give the full path to `.cursor` directly.**
- Windows example: `C:\Users\YourName\.cursor`
- macOS example: `/Users/yourname/.cursor`

**Option C — Drop sessions manually** into `ingestion/cursor-chats/` and tell the AI they're ready. Useful if you've already located the files or exported them from another machine.

**How to find your user folder if you're not sure:**
- **Windows:** Open File Explorer and paste `%USERPROFILE%` into the address bar, then press Enter. That opens your user folder — copy the full path from the address bar.
- **macOS:** Open Finder and press `Cmd+Shift+H` to go to your home folder. Right-click the folder name in the title bar to copy the path. Note: `.cursor` is a hidden folder — press `Cmd+Shift+.` to show hidden files if you want to confirm it's there.

Once the AI has access, it will show you a table of all your Cursor projects with session counts and dates, and let you choose which ones to import and how far back to go.

---

## Starter Prompts

Copy and paste any of these to get started. Replace `[Name]` with the developer's full name.

---

**Run a full review (sessions already in the ingestion folder):**
> Run a prompting analysis for [Name].

---

**Import sessions first, then run a review:**
> I'd like to run a prompting review for [Name]. Can you help me import my Cursor session history first?

---

**Import sessions from a specific time window:**
> I want to review my prompting habits for the last 30 days. Can you help me import my recent Cursor sessions and run an analysis for [Name]?

---

**Re-run an existing review with new sessions:**
> I have a report from last month for [Name]. I've added new sessions — can you run a fresh analysis and create a new version of the report?

---

**Quick import only (no analysis yet):**
> Can you help me find and import my Cursor session history into the ingestion folder? I'll run the analysis after.

---

**Review a specific project only:**
> Run a prompting analysis for [Name] using only the sessions from the [project name] project.

---

## Folder Structure

```
ai-prompting-review/
│
├── PROCESS.md              ← The process guide (full methodology)
├── CLAUDE.md               ← Auto-loads in Claude; bootstraps the process
├── STARTER_PROMPT.md       ← Paste into any other AI agent to begin
├── README.md               ← This file
├── .gitignore
│
├── ingestion/              ← Drop session files here before running
│   ├── cursor-chats/       ← Cursor AI .jsonl sessions, one folder per project
│   └── other-chats/        ← Placeholder for future sources
│
├── reports/                ← Generated outputs (gitignored)
│   └── [Developer-Name]/
│       └── [YYYY-MM]/
│           ├── [Name]-Prompting-Analysis.md
│           ├── [Name]-Scorecard.html
│           └── scorecard-template.md
│
├── scripts/                ← Python helper scripts (run from project root)
│   ├── discover_cursor.py  ← Scans .cursor folder, lists available projects
│   ├── import_cursor.py    ← Copies chosen sessions into ingestion/
│   ├── extract_sessions.py ← Extracts user messages → session_data.json
│   └── analyse_sessions.py ← Computes signal stats + sample → analysis_stats.json
│
└── templates/              ← Master templates, never edit directly
    ├── analysis-report-template.md
    ├── scorecard-mockup.html
    └── scorecard-template.md
```

---

## The Scoring Rubric

Nine categories, each scored 1–5. Total out of 45.

| Category               | What It Measures                                 |
| ---------------------- | ------------------------------------------------ |
| Context Engineering    | File references, docs, role-setting              |
| Instruction Quality    | Clarity, action verbs, specificity               |
| Example-Based Guidance | Mocks, reference files, few-shot patterns        |
| Scope Definition       | In/out-of-scope boundaries, constraint guards    |
| Debugging Discipline   | Triggering action → expected → actual → logs     |
| Session Management     | Context window awareness, fresh-start discipline |
| Reusability Investment | Rules, commands, prompt templates                |
| Verification Habits    | Upfront success criteria                         |
| Plan-Before-Build      | Scoping before implementation, plan files        |

**Maturity levels:** Conversational (1) → Task-Oriented (2) → Context-Aware (3) → Systematic (4) → Expert (5)

Full scoring definitions and methodology are in `PROCESS.md`.

---

## Supported Sources

| Source         | Format               | Status      |
| -------------- | -------------------- | ----------- |
| Cursor AI      | `.jsonl` per session | ✅ Supported |
| ChatGPT        | `.json` export       | 🔜 Planned  |
| GitHub Copilot | TBD                  | 🔜 Planned  |
| Other AI IDEs  | TBD                  | 🔜 Planned  |

The scoring rubric and output format are tool-agnostic. Only the data extraction step varies by source.

---

## Privacy

Session files and generated reports are **excluded from git** (see `.gitignore`). Only the process guide, templates, scripts, and folder structure are committed. Session data stays on your machine.

---

## Contributing

Improvements to the rubric, new session source extractors, and template refinements are all welcome. See `PROCESS.md` for the full methodology and improvement log.
