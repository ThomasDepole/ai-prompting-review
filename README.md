# AI Prompting Review

A structured workspace for analysing how developers use AI coding tools — and helping them get better at it.

Feed it a developer's session history and it produces a full narrative report, an interactive HTML scorecard, and a portable markdown scorecard. The analysis covers 9 prompting dimensions scored 1–5, with concrete examples pulled directly from their sessions and specific recommendations for improvement.

Works with any AI agent. Claude users get zero-friction setup — `CLAUDE.md` loads the process automatically. Everyone else can use `STARTER_PROMPT.md` to bootstrap in seconds.

---

## What You Get

| Output                         | Description                                                                               |
| ------------------------------ | ----------------------------------------------------------------------------------------- |
| `[Name]-Prompting-Analysis.md` | Deep narrative report — strengths, weaknesses, patterns by session type, standout prompts |
| `[Name]-Scorecard.html`        | Interactive single-page scorecard with click-to-expand category definitions               |
| `scorecard-template.md`        | Portable markdown version of the scorecard for sharing or printing                        |

All outputs land in `reports/[Developer-Name]/[YYYY-MM]/`.

---

## Quick Start

**1. Get the developer's session files**

For Cursor AI, sessions live at:

- **Windows:** `C:\Users\[username]\.cursor\projects\[project-slug]\agent-transcripts\`
- **macOS:** `~/.cursor/projects/[project-slug]/agent-transcripts/`

Not sure where they are? Open your AI agent in this folder and ask:

> "Can you find my Cursor session files on this computer?"

**2. Drop sessions into the ingestion folder**

```
ingestion/cursor-chats/[project-name]/[uuid]/[uuid].jsonl
```

See `ingestion/cursor-chats/README.md` for details. Aim for 10–15 sessions minimum.

**3. Run the analysis**

| Tool                              | How to start                                                                                     |
| --------------------------------- | ------------------------------------------------------------------------------------------------ |
| **Claude** (Cowork / Claude Code) | Open this folder — `CLAUDE.md` loads automatically. Say: *"Run a prompting analysis for [Name]"* |
| **Cursor**                        | Copy `CLAUDE.md` contents into `.cursorrules`, then ask the same                                 |
| **Any other agent**               | Paste the contents of `STARTER_PROMPT.md` as your first message                                  |

The full methodology is in `PROCESS.md`.

---

## Folder Structure

```
ai-prompting-review/
│
├── PROCESS.md              ← The process guide (start here)
├── CLAUDE.md               ← Auto-loads in Claude; points to PROCESS.md
├── STARTER_PROMPT.md       ← Paste into any other AI agent to begin
├── README.md               ← This file
├── .gitignore
│
├── ingestion/              ← Drop session files here before running
│   ├── cursor-chats/       ← Cursor AI .jsonl sessions
│   └── other-chats/        ← Placeholder for future sources
│
├── reports/                ← Generated outputs (gitignored)
│   └── [Developer-Name]/
│       └── [YYYY-MM]/
│
└── templates/              ← Master templates, copy per developer
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

Session files and generated reports are **excluded from git** (see `.gitignore`). Only the process guide, templates, and folder structure are committed. Session data stays on your machine.

---

## Contributing

Improvements to the rubric, new session source extractors, and template refinements are all welcome. See `PROCESS.md` for the full methodology and improvement log.
