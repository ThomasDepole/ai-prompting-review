# AI Prompting Review

A structured workspace for analysing how developers use AI coding tools — and helping them get better at it.

Feed it a developer's session history and it produces a full narrative report, an interactive HTML scorecard, and a portable markdown scorecard. The analysis covers 9 prompting dimensions scored 1–5, with concrete examples pulled directly from their sessions and specific recommendations for improvement.

Works with any AI agent. **Cursor users** get native support — open this folder in Cursor and the workspace rule loads automatically, no setup required. Claude users have `CLAUDE.md` auto-loaded. Everyone else can use `STARTER_PROMPT.md` to bootstrap in seconds.

---

## Table of Contents

- [What You Get](#what-you-get)
- [Quick Start](#quick-start)
- [Starter Prompts](#starter-prompts)
- [Importing Sessions (Claude / Other Agents)](#importing-your-cursor-sessions)
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

**Option A — Open in Cursor or Claude and let the AI handle everything**

Open this folder in Cursor or Claude and say one of the [starter prompts](#starter-prompts) below. The AI will find your session history and walk you through selecting what to include. In Cursor, no import step is needed — sessions are read directly from your `.cursor` folder.

**Option B — Drop sessions in manually, then run the analysis**

If you already have the files, place them here:

```
ingestion/cursor-chats/[project-name]/[uuid]/[uuid].jsonl
```

Then tell the AI you're ready to run the analysis (see starter prompts below). Aim for 10–15 sessions minimum for a meaningful report.

**How to start the AI**

| Tool                              | How to start                                                                                      |
| --------------------------------- | ------------------------------------------------------------------------------------------------- |
| **Cursor**                        | Open this folder in Cursor — the workspace rule loads automatically. Use one of the Cursor starter prompts below. |
| **Claude** (Cowork / Claude Code) | Open this folder — `CLAUDE.md` loads automatically. Use one of the starter prompts below.        |
| **Any other agent**               | Paste the contents of `STARTER_PROMPT.md` as your first message, then use a starter prompt.      |

---

## Importing Your Cursor Sessions

> **Cursor users:** You don't need this section. The workspace rule reads your session history directly — no import step required. Just open this folder in Cursor and use one of the starter prompts above.

For Claude and other agents, Cursor stores your session history in a hidden `.cursor` folder on your computer. The AI can find and import your sessions automatically — you just need to give it the right folder path.

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

### Running inside Cursor

No setup needed — just open this folder in Cursor and send one of these. The workspace rule handles everything automatically, including finding your session history directly from your `.cursor` folder.

---

**Run a review on all your Cursor chats:**
> I would like to run a report on my past chats.

---

**Run a review limited to specific projects:**
> I'd like to run a prompting review. Please include only sessions from [project name] and [project name].

---

**Run a review for the last N days:**
> I want to review my prompting habits for the last 30 days across all my projects.

---

**Run a review for someone else:**
> I'd like to run a prompting report for [Full Name] — they're a developer on my team. Can you walk me through it?

---

**Re-run and build on a previous report:**
> I have a report from last month. Can you run a fresh analysis and build on the history?

---

### Running in Claude or another agent

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

**Review a specific project only:**
> Run a prompting analysis for [Name] using only the sessions from the [project name] project.

---

## Folder Structure

```
ai-prompting-review/
│
├── PROCESS.md              ← Process guide — setup and Steps 0–3
├── PROCESS.review.md       ← Stage 1: session scoring and scratch pad
├── PROCESS.report.md       ← Stage 2: report generation
├── CLAUDE.md               ← Auto-loads in Claude; bootstraps the process
├── STARTER_PROMPT.md       ← Paste into any other AI agent to begin
├── README.md               ← This file
├── ROADMAP.md              ← Planned improvements and completed changelog
├── .gitignore
│
├── .cursor/
│   └── rules/
│       └── prompting-review.mdc  ← Cursor workspace rule — loads automatically
│
├── ingestion/              ← Drop session files here (non-Cursor workflows)
│   ├── cursor-chats/       ← Cursor AI .jsonl sessions, one folder per project
│   └── other-chats/        ← Placeholder for future sources
│
├── reports/                ← Generated outputs (gitignored)
│   └── [Developer-Name]/
│       ├── history.json    ← Trend tracking across runs
│       └── [YYYY-MM]/
│           ├── [Name]-Prompting-Analysis.md
│           ├── [Name]-Scorecard.html
│           └── scorecard-template.md
│
├── scripts/                ← Python helper scripts (run from project root)
│   ├── extract_sessions.py ← Extracts user messages → temp/session_data.json
│   ├── analyse_sessions.py ← Computes signal stats + sample → temp/analysis_stats.json
│   ├── discover_cursor.py  ← Claude Cowork only: scans .cursor folder
│   └── import_cursor.py    ← Claude Cowork only: copies sessions into ingestion/
│
├── temp/                   ← Process artifacts — gitignored, deleted after each run
│   ├── session_data.json   ← Produced by extract_sessions.py
│   ├── analysis_stats.json ← Produced by analyse_sessions.py
│   └── scoring_scratch.json← Written during Stage 1, read by Stage 2
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
