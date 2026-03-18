# AI Prompting Pattern Review — Process Guide

**Purpose:** How to run a prompting analysis for any team member using their AI session history
**Intended audience:** Team leads, developers onboarding new engineers, or anyone running this review for a team member

---

## What This Process Does

This process reads a developer's historical AI session files and produces three structured outputs:

1. **Full Analysis Report** (`[Name]-Prompting-Analysis.md`) — deep narrative report with examples and recommendations
2. **Scorecard HTML** (`[Name]-Scorecard.html`) — interactive visual scorecard for sharing and presenting
3. **Scorecard MD** (`scorecard-template.md`) — portable markdown version of the scorecard

The analysis covers:

- How they structure prompts (structure, clarity, use of references)
- What prompting habits are working well
- Where prompts are causing unnecessary back-and-forth
- Session-level patterns (debugging, architecture, implementation)
- Specific, actionable recommendations tailored to their actual usage

The output is suitable for 1:1 coaching, team training, or self-directed improvement.

---

## Process Overview — Three Files

This process is split across three files to keep each phase's context load small:

| File | When to read | What it covers |
|---|---|---|
| `PROCESS.md` *(this file)* | At session start | Setup, scripts, Step 0–3 |
| `PROCESS.review.md` | After Step 3 | Stage 1: reading sessions, scoring, writing scratch pad |
| `PROCESS.report.md` | After Stage 1 | Stage 2: writing the three output files and history |

**Do not load `PROCESS.review.md` or `PROCESS.report.md` until you reach those stages.** Loading them early wastes context window on content that isn't needed yet.

---

## Folder Structure

```
ai-prompting-review/
│
├── PROCESS.md                    ← This file (setup + entry point)
├── PROCESS.review.md             ← Stage 1: analysis and scoring
├── PROCESS.report.md             ← Stage 2: report generation
├── CLAUDE.md                     ← Thin bootstrap for Claude (auto-loaded)
├── STARTER_PROMPT.md             ← Thin bootstrap for any other AI agent
├── README.md                     ← Human-facing project overview
│
├── ingestion/                    ← Drop session files here before running analysis
│   ├── cursor/
│   │   ├── projects/             ← Mirror of ~/.cursor/projects/ (JSONL agent sessions)
│   │   │   └── [project-slug]/
│   │   │       └── agent-transcripts/
│   │   │           └── [uuid]/
│   │   │               └── [uuid].jsonl
│   │   └── chats/                ← Mirror of ~/.cursor/chats/ (SQLite regular chats)
│   │       └── [workspace-hash]/
│   │           └── [uuid]/
│   │               └── store.db
│   └── other-chats/              ← Placeholder for future chat sources
│
├── reports/                      ← All analysis outputs go here (gitignored)
│   └── [Developer-Name]/
│       ├── history.json          ← Trend tracking across runs
│       └── [YYYY-MM]/
│           ├── [Name]-Prompting-Analysis.md
│           ├── [Name]-Scorecard.html
│           └── scorecard-template.md
│
├── scripts/
│   ├── extract_sessions.py       ← Step 2: extracts user messages → temp/session_data.json
│   ├── analyse_sessions.py       ← Step 3: computes stats + sample → temp/analysis_stats.json
│   ├── import_cursor.py          ← Claude Cowork only: copies sessions into ingestion/
│   └── discover_cursor.py        ← Claude Cowork only: scans .cursor folder
│
├── templates/
│   ├── analysis-report-template.md
│   ├── scorecard-mockup.html
│   └── scorecard-template.md
│
└── temp/                         ← Process artifacts — gitignored, deleted after each run
    ├── session_data.json         ← Produced by extract_sessions.py
    ├── analysis_stats.json       ← Produced by analyse_sessions.py
    └── scoring_scratch.json      ← Written by the LLM during Stage 1
```

---

## Supported Session Sources

| Source | Format | Ingestion drop-zone | Direct flag |
|---|---|---|---|
| Cursor agent / composer | `.jsonl` (one JSON object per line) | `ingestion/cursor/projects/[slug]/agent-transcripts/[uuid]/[uuid].jsonl` | `--source ~/.cursor/projects` |
| Cursor regular chats (Ctrl+L) | SQLite (`store.db`) | `ingestion/cursor/chats/[hash]/[uuid]/store.db` | `--chats ~/.cursor/chats` |
| Other tools (future) | TBD | `ingestion/other-chats/` | — |

The analysis framework is tool-agnostic — the 9 scoring categories and 5 maturity levels apply regardless of which AI coding tool was used.

---

## Prerequisites

### Cursor AI Sessions

Cursor stores chat history in two separate locations. Both are valuable and should be included when available.

**Agent / composer sessions (`.jsonl`):**

| OS | Path |
|---|---|
| macOS | `~/.cursor/projects/[project-slug]/agent-transcripts/` |
| Windows | `C:\Users\[username]\.cursor\projects\[project-slug]\agent-transcripts\` |

**Regular Ctrl+L chats (SQLite):**

| OS | Path |
|---|---|
| macOS | `~/.cursor/chats/` |
| Windows | `C:\Users\[username]\.cursor\chats\` |

**How to collect:**

| Method | When to use |
|---|---|
| **Direct flags** (`--source` + `--chats`) | Running in Cursor or any agent with filesystem access. No file copying needed. |
| **Import scripts** (`import_cursor.py`) | Running in Claude Cowork or another tool that needs files placed in `ingestion/` first. See `CLAUDE.md`. |
| **Manual drop** | You already have the files. Copy project slug folders into `ingestion/cursor/projects/` and workspace hash folders into `ingestion/cursor/chats/`. |

Aim for at least 10–15 sessions for meaningful pattern analysis.

---

## File Format Reference

Each Cursor `.jsonl` file contains one JSON object per line:

```json
{ "role": "user", "message": { "content": [{ "type": "text", "text": "..." }] } }
{ "role": "assistant", "message": { "content": [{ "type": "text", "text": "..." }] } }
```

User message types to be aware of:
- `<user_query>` — the main prompt text
- `<attached_files>` — code selections with file paths and line numbers
- `<cursor_commands>` — pre-loaded context commands
- `<image_files>` — screenshots attached by the user
- `@` — file references embedded in text

---

## Running the Analysis

### Step 0 — Confirm the Developer's Name and Check for History

**First — check for a leftover `temp/` folder.** If `temp/` exists, a previous session may have ended before the process completed. Tell the user:

> *"I found a `temp/` folder from a previous run containing: [list files present]. Would you like to:*
> *A) Resume — skip the extraction steps and continue from where it left off*
> *B) Start fresh — delete the temp folder and run the full process again"*

- **Resume (A):** If `temp/session_data.json` and `temp/analysis_stats.json` exist, skip Steps 1–3 and go straight to `PROCESS.review.md`. If `temp/scoring_scratch.json` also exists, skip straight to `PROCESS.report.md`.
- **Fresh start (B):** Delete `temp/` and all its contents before proceeding.

If no `temp/` folder exists, proceed normally.

---

Before doing anything else, confirm the full name of the developer being reviewed. This name is used as the folder name under `reports/` and as the label throughout all three output files.

If the name was not supplied with the initial request, ask: **"What is the full name of the developer we're reviewing?"**

Use the name exactly as provided (e.g. `Jane Smith`, not `jane-smith` or `JaneSmith`).

---

**Check for a history file.** Look for `reports/[Developer-Name]/history.json`. If it exists and has entries, read it and show the user a brief summary:

> *"I found [N] previous report(s) for [Name]:*
> *— [Month Year]: [total]/45 · Level [N] [Level Name] · [N] sessions · [N] user turns*
>
> *Would you like to:*
> *A) Start fresh — analyse only the sessions in the ingestion folder, no trend comparison*
> *B) Build on history — use prior report data to show trends, flag persistent patterns, and contextualise any score changes"*

If the user chooses **B (build on history)**:
- Read the most recent history entry before scoring to calibrate expectations
- After scoring, compute delta indicators for each category (↑ / ↓ / →)
- Include the "Progress Since Last Review" section in the analysis report
- In the scorecard, populate the trend indicators and Trend section
- Flag categories where a score change may reflect sample size rather than genuine shift
- Call out confirmed persistent patterns: a weakness that scores low across 2+ reports is a real gap

If the user chooses **A (fresh start)**, omit the "Progress Since Last Review" and Trend sections from both outputs.

---

**Check for an existing report for this month.** Look for `reports/[Developer-Name]/[YYYY-MM]/`. If that folder already exists and contains output files, tell the user:

> *"I also found an existing report for [Name] from [Month Year]. Would you like to overwrite it, or save this as a new version alongside it?"*

- **Overwrite:** Proceed normally.
- **New version:** Create output files with a version suffix, e.g. `[Name]-Prompting-Analysis-v2.md`. Increment the version number if v2 already exists.

If no existing report is found, create the folder at `reports/[Developer-Name]/[YYYY-MM]/` and proceed.

---

### Step 1 — Load the Session Files

**If using direct extraction (`--source` or `--chats` flags), skip this step** — no files need to be copied.

For manual drop, mirror the `.cursor/` folder structure into the `ingestion/cursor/` folder:

| What to copy | From | Into |
|---|---|---|
| Agent/composer sessions | `~/.cursor/projects/[slug]/` | `ingestion/cursor/projects/[slug]/` |
| Regular chats | `~/.cursor/chats/[hash]/` | `ingestion/cursor/chats/[hash]/` |

The script navigates `agent-transcripts/` automatically — copy the entire project slug folder, not just the transcripts subfolder.

---

### Step 2 — Extract User Messages

Cursor stores chat history in **two separate locations** that are not interchangeable:

| Source | What it contains | Location |
|---|---|---|
| Agent / composer sessions | Multi-step agent tasks (less frequent, higher complexity) | `.cursor/projects/[slug]/agent-transcripts/` |
| Regular Ctrl+L chats | Day-to-day chat history (most developers' primary usage) | `.cursor/chats/` |

For most developers, **regular chats contain the majority of their prompting history**. Always use both sources when available.

Run the extraction script from the project root:

**Default — reads from both ingestion drop-zones:**
```
python scripts/extract_sessions.py
```

> **If this returns `Total sessions: 0` and files are clearly present in the ingestion folder**, the sessions may be in plain-text `.txt` format rather than JSONL. See the **Ingestion Format Detection** note below.

**Both sources combined (recommended for Cursor workflow):**
```
python scripts/extract_sessions.py --source ~/.cursor/projects --chats ~/.cursor/chats
python scripts/extract_sessions.py --source ~/.cursor/projects --chats ~/.cursor/chats --days 30
```

**Agent-transcripts only:**
```
python scripts/extract_sessions.py --source ~/.cursor/projects
python scripts/extract_sessions.py --source ~/.cursor/projects --days 30
python scripts/extract_sessions.py --source ~/.cursor/projects --projects project-slug-a project-slug-b
```

**Regular chats only** (for developers who rarely use agent mode):
```
python scripts/extract_sessions.py --chats ~/.cursor/chats
python scripts/extract_sessions.py --chats ~/.cursor/chats --days 30
```

On Windows, replace `~/.cursor/` with `C:\Users\[username]\.cursor\` in all paths.

| Flag | Description |
|---|---|
| `--source PATH` | Path to a `.cursor/projects/` directory. Reads `agent-transcripts` JSONL files. |
| `--chats PATH` | Path to a `.cursor/chats/` directory. Reads regular chat SQLite databases. |
| `--days N` | Only include sessions modified/created in the last N days. Works with both flags. |
| `--projects SLUG...` | One or more project slugs to include (applies to `--source` only). |

Output: `temp/session_data.json`. Contains only user messages from all sources merged together — this is the file used for all session reading in Stage 1. The `temp/` folder is created automatically if it doesn't exist.

---

### Ingestion Format Detection — Two Possible Formats

When sessions are manually dropped into `ingestion/cursor/projects/`, they may be in one of two formats. `extract_sessions.py` only handles Format A. If it returns 0 sessions when files are clearly present, check for Format B.

**Format A — JSONL (standard, expected by `extract_sessions.py`):**
```
ingestion/cursor/projects/[slug]/agent-transcripts/[uuid]/[uuid].jsonl
```
Each session is a subdirectory named by UUID containing a `.jsonl` file. Each line is a JSON object with `role` and `message` fields.

**Format B — Plain-text transcripts (`.txt`):**
```
ingestion/cursor/projects/[slug]/agent-transcripts/[uuid].txt
```
Each session is a single `.txt` file directly inside `agent-transcripts/` with no subdirectory. Uses `user:` / `assistant:` blocks with `<user_query>...</user_query>` tags. `extract_sessions.py` will silently return 0 sessions for this format.

**To detect Format B**, check for `.txt` files in the ingestion projects folder:
- Windows: `Get-ChildItem -Recurse ingestion\cursor\projects -Filter "*.txt" | Select-Object -First 3`
- macOS/Linux: `find ingestion/cursor/projects -name "*.txt" | head -3`

**If Format B is detected**, use the fallback script instead. It accepts the same `--days` and `--projects` flags as `extract_sessions.py`:
```
python scripts/extract_txt_sessions.py
python scripts/extract_txt_sessions.py --days 30
python scripts/extract_txt_sessions.py --days 30 --projects slug-a slug-b
```
The output is identical `temp/session_data.json` — all downstream steps (`analyse_sessions.py` onwards) are unchanged.

---

### Step 3 — Compute Pre-Analysis Stats and Select a Sample

```
python scripts/analyse_sessions.py
```

Output: `temp/analysis_stats.json`.

This script computes quantitative signals across every session and classifies sessions by size:

| Tier | User Turns | What it represents |
|---|---|---|
| **Large** | 9+ turns | Complex, multi-step work — most signal-rich |
| **Medium** | 4–8 turns | Average sessions — typical prompting habits |
| **Small** | 1–3 turns | Either very efficient sessions or abandoned attempts |

**What the stats tell you before reading a single session:**
- `at_refs` — percentage of messages using `@` file references
- `cursor_commands` — whether the developer uses preloaded context commands
- `attached_files` — how often they attach code selections
- `plan_refs` — whether plan files are being referenced
- `mdc_refs` — whether `.mdc` cursor rules files are mentioned
- `verification` — presence of success criteria language
- `constraint_guards` — presence of "don't change X" scope boundaries
- `debug_structure` — presence of structured debugging language
- `sessions_with_subagents` — how many sessions triggered agent decomposition (positive signal)

Use the aggregate stats to form a hypothesis about each scoring category *before* reading sessions.

---

**→ Proceed to `PROCESS.review.md` for Stage 1 (session reading, scoring, and scratch pad).**

---

## Files Produced

Each developer's analysis produces the following files in `reports/[Developer-Name]/[YYYY-MM]/`:

| File                           | Description                    |
| ------------------------------ | ------------------------------ |
| `[Name]-Prompting-Analysis.md` | Full narrative analysis report |
| `[Name]-Scorecard.html`        | Interactive HTML scorecard     |
| `scorecard-template.md`        | Portable markdown scorecard    |

Intermediate files (all in `temp/`, gitignored, deleted at end of process):

| File                        | Produced by             | Used by       |
|-----------------------------|-------------------------|---------------|
| `temp/session_data.json`    | `extract_sessions.py`   | Stage 1       |
| `temp/analysis_stats.json`  | `analyse_sessions.py`   | Stage 1       |
| `temp/scoring_scratch.json` | Stage 1 (LLM writes it) | Stage 2       |

Master templates — never edit directly, always copy to the report folder first:

| File                                    | Description                          |
| --------------------------------------- | ------------------------------------ |
| `templates/analysis-report-template.md` | Full analysis report template        |
| `templates/scorecard-mockup.html`       | Interactive HTML scorecard template  |
| `templates/scorecard-template.md`       | Portable markdown scorecard template |

---

## Improvement Log

| Date          | Change |
| ------------- | ------ |
| March 2026 v1 | Initial process established. Python extraction script developed. Rubric v1 created. Folder structure defined: `ingestion/cursor-chats/`, `ingestion/other-chats/`, `reports/[Name]/[YYYY-MM]/`. Scorecard HTML and MD generation steps added. Step 0 added: confirm developer name before starting. PROCESS.md introduced as tool-agnostic process guide; CLAUDE.md and STARTER_PROMPT.md become thin bootstraps pointing here. |
| March 2026 v2 | Added `scripts/` folder with `extract_sessions.py` and `analyse_sessions.py`. Added tiered sampling strategy (6 large / 6 medium / 6 small sessions). Added score 3 definitions for all 9 categories. Updated subagent guidance. Clarified ingestion folder as single-person drop zone. |
| March 2026 v3 | Improved `.cursor` folder discovery UX in CLAUDE.md. Added Step 0 guard for existing monthly reports — prompts user to overwrite or create a versioned copy. |
| March 2026 v4 | Added history tracking system (`history.json`). Step 0 expanded with history check. Step 10 added: write/append history.json. Analysis report and scorecard templates gain trend sections with ↑/↓/→ indicators. Sample-size caveat logic added. |
| March 2026 v5 | Added Cursor-native support. Created `.cursor/rules/prompting-review.mdc`. Added `--source`, `--days`, `--projects` flags to `extract_sessions.py`. Added `ROADMAP.md`. |
| March 2026 v6 | Context optimisation: PROCESS.md and cursor rule updated to mandate `session_data.json` for session reading instead of raw JSONL files. |
| March 2026 v7 | Split PROCESS.md into three phase-scoped files: `PROCESS.md` (setup, Steps 0–3), `PROCESS.review.md` (Stage 1: scoring + scratch pad), `PROCESS.report.md` (Stage 2: report generation). Added `scoring_scratch.json` as handoff artifact between stages. Each phase loads only the instructions it needs. |
| March 2026 v8 | Moved all intermediate files (`session_data.json`, `analysis_stats.json`, `scoring_scratch.json`) into a `temp/` folder. Scripts updated to write there. Temp folder is gitignored and deleted at end of process (Step 11). Step 0 now checks for a stale `temp/` folder and offers resume or fresh start. |

---

*The goal of this process is not uniformity — different developers will have different strengths — but deliberate, evidence-based improvement.*
