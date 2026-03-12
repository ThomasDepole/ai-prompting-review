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

## Folder Structure

```
ai-prompting-review/
│
├── PROCESS.md                    ← This file (the process guide)
├── CLAUDE.md                     ← Thin bootstrap for Claude (auto-loaded)
├── STARTER_PROMPT.md             ← Thin bootstrap for any other AI agent
├── README.md                     ← Human-facing project overview
│
├── ingestion/                    ← Drop session files here before running analysis
│   ├── cursor-chats/             ← Cursor AI session JSONL files
│   │   └── [project-name]/       ← One folder per Cursor project (use the Cursor
│   │       └── [uuid]/              project folder name — useful context in reports)
│   │           └── [uuid].jsonl
│   └── other-chats/              ← Placeholder for future chat sources
│                                    (e.g. ChatGPT exports, Copilot logs, etc.)
│
├── reports/                      ← All analysis outputs go here (gitignored)
│   └── [Developer-Name]/         ← Subfolder per developer
│       └── [YYYY-MM]/            ← Subfolder per month/run
│           ├── [Name]-Prompting-Analysis.md
│           ├── [Name]-Scorecard.html
│           └── scorecard-template.md
│
├── scripts/                      ← Python helper scripts (run from project root)
│   ├── discover_cursor.py        ← Import step 1: scans .cursor folder, lists available projects
│   ├── import_cursor.py          ← Import step 2: copies chosen sessions into ingestion/
│   ├── extract_sessions.py       ← Analysis step 1: extracts user messages → session_data.json
│   └── analyse_sessions.py       ← Analysis step 2: computes stats + recommends sample → analysis_stats.json
│
└── templates/                    ← Master templates (never edit directly — copy per developer)
    ├── analysis-report-template.md
    ├── scorecard-mockup.html
    └── scorecard-template.md
```

**Note on the ingestion folder:** The ingestion folder is a single-person drop zone — it holds sessions for one developer at a time. To run a review for a different developer, clear the ingestion folder and drop in their sessions. The `[project-name]` subfolder should match the developer's Cursor project folder name (found at `~/.cursor/projects/` on macOS or `C:\Users\[username]\.cursor\projects\` on Windows) — this name carries useful context when reading the analysis.

---

## Supported Session Sources

This process currently supports:

| Source         | Format                              | Location                                                    |
| -------------- | ----------------------------------- | ----------------------------------------------------------- |
| Cursor AI      | `.jsonl` (one JSON object per line) | `ingestion/cursor-chats/[project-name]/[uuid]/[uuid].jsonl` |
| Other (future) | TBD                                 | `ingestion/other-chats/`                                    |

The analysis framework is tool-agnostic — the 9 scoring categories and 5 maturity levels apply regardless of which AI coding tool was used. Only the **data extraction step** (Step 2) varies by source. Future sources may require different extraction scripts but feed into the same scoring rubric.

---

## Understanding What Session Files Can and Cannot See

Before collecting data, it's important to understand that AI coding tools often have **multiple layers of context** that influence AI behavior — and session files only directly expose some of them.

### For Cursor AI (three layers):

**Layer 1 — Chat messages (fully visible in `.jsonl`):**
Everything typed by the user in the chat, including `<user_query>` blocks, `@` file references, and `<attached_files>` code selections. This is what session files capture.

**Layer 2 — Context commands (`<cursor_commands>`, visible):**
When a developer triggers a saved command (e.g., `context-humdrum-data`), the full contents of that command are embedded directly in the user message. These are fully readable in the `.jsonl` file and look like a `<cursor_commands>` block at the top of a user turn.

**Layer 3 — Auto-scoped `.mdc` rules (invisible — the blind spot):**
Cursor rules stored in `.cursor/rules/*.mdc` with a `globs:` scope pattern are automatically injected by Cursor before the session starts. They do not appear anywhere in the session file. The AI silently follows them without attribution.

**What this means for the analysis:** Session files give a true picture of the developer's *chat prompting style* but an incomplete picture of their total *context engineering*. A developer who has invested heavily in `.cursor/rules/` files may look like they're giving sparse prompts, when in fact they've front-loaded architectural guidance invisibly.

**How to detect cursor rules usage in session files — look for these signals:**

- References to `.mdc` files anywhere in user or assistant messages (the `analyse_sessions.py` script flags these automatically)
- AI responses that apply conventions or constraints the developer never stated in the current session — this suggests auto-injected rules are in effect
- The developer referencing `.cursor/rules/` explicitly in conversation
- A `<cursor_commands>` block that points to or configures rules

**Scoring note:** When Reusability Investment appears low based on session files alone, note this limitation explicitly. A developer with substantial `.mdc` rules may deserve a higher score than session files suggest. Flag it and ask the developer to confirm during the review.

**Layer 4 — Subagents (auto-spawned, not user-controlled):**
When a Cursor agent determines that a task benefits from parallel execution, it automatically spawns subagents — independent agents with their own context window. Subagents are *not* created by the user directly; they are launched by the orchestrating agent based on task complexity. The presence of subagents in a session is therefore a **positive signal about the user's prompting**: it means their prompt was well-scoped and complex enough to trigger agent decomposition.

Subagent sessions appear as a `subagents/` subdirectory inside a session folder. The `extract_sessions.py` script counts them but does not extract their content — the subagent JSONL files reflect the AI's internal work, not the developer's prompting behavior, so they are not relevant to the analysis.

---

## Prerequisites

### What You Need From the Developer

#### Cursor AI Sessions

Cursor stores session history as `.jsonl` files. Each session is a UUID-named subdirectory containing one `.jsonl` file of the same name.

**Where to find Cursor session files (Windows):**

```
C:\Users\[username]\.cursor\projects\[project-slug]\agent-transcripts\
```

**Where to find Cursor session files (macOS):**

```
~/.cursor/projects/[project-slug]/agent-transcripts/
```

Each subfolder inside `agent-transcripts` is one session:

```
agent-transcripts/
  [uuid-1]/
    [uuid-1].jsonl
  [uuid-2]/
    [uuid-2].jsonl
  ...
```

**How to collect:**

1. Ask the developer to zip their `agent-transcripts` folder (or a representative subset of recent sessions)
2. Place extracted sessions in `ingestion/cursor-chats/[project-name]/`
3. Organize by project if they work across multiple codebases
4. Aim for at least 10–15 sessions for meaningful pattern analysis

---

## File Format Reference

### Cursor `.jsonl` Format

Each `.jsonl` file contains one JSON object per line:

```json
{ "role": "user", "message": { "content": [{ "type": "text", "text": "..." }] } }
{ "role": "assistant", "message": { "content": [{ "type": "text", "text": "..." }] } }
```

Additional user message types:

- `<user_query>` tags wrapping the main prompt text
- `<attached_files>` blocks containing code selections with file paths and line numbers
- `<cursor_commands>` blocks containing pre-loaded context commands
- `<image_files>` references to screenshots attached by the user
- `@` references embedded in text pointing to files, docs, or other projects

---

## Running the Analysis

### Step 0 — Confirm the Developer's Name and Check for History

Before doing anything else, confirm the full name of the developer being reviewed. This name is used as the folder name under `reports/` and as the label throughout all three output files.

If the name was not supplied with the initial request, ask: **"What is the full name of the developer we're reviewing?"**

Use the name exactly as provided (e.g. `Jane Smith`, not `jane-smith` or `JaneSmith`).

---

**Check for a history file.** Look for `reports/[Developer-Name]/history.json`. If it exists and has entries, read it and show the user a brief summary:

> *"I found [N] previous report(s) for [Name]:*
> *— [Month Year]: [total]/45 · Level [N] [Level Name] · [N] sessions · [N] user turns*
> *(one line per report)*
>
> *Would you like to:*
> *A) Start fresh — analyse only the sessions in the ingestion folder, no trend comparison*
> *B) Build on history — use prior report data to show trends, flag persistent patterns, and contextualise any score changes"*

If the user chooses **B (build on history)**:

- Read the most recent history entry before scoring to calibrate expectations
- After scoring, compute delta indicators for each category (↑ if current > previous, ↓ if lower, → if unchanged)
- Include the "Progress Since Last Review" section in the analysis report (see template)
- In the scorecard, populate the trend indicators and Trend section (see scorecard instructions)
- Flag categories where a score change may reflect sample size rather than genuine shift — use the `sample_note` from the most recent history entry as a guide
- Call out confirmed persistent patterns: a weakness that scores low across 2+ reports is a real gap, not a sampling artifact

If the user chooses **A (fresh start)**, omit the "Progress Since Last Review" section and Trend section from both outputs.

---

**Check for an existing report for this month.** Look for a folder at `reports/[Developer-Name]/[YYYY-MM]/` where `[YYYY-MM]` is the current month. If that folder already exists and contains output files, tell the user:

> *"I also found an existing report for [Name] from [Month Year]. Would you like to overwrite it, or save this as a new version alongside it?"*

- **Overwrite:** Proceed normally — the new outputs will replace the existing files.
- **New version:** Create output files with a version suffix, e.g. `[Name]-Prompting-Analysis-v2.md`, `[Name]-Scorecard-v2.html`, `scorecard-template-v2.md`. Increment the version number if v2 already exists.

If no existing report is found, create the folder at `reports/[Developer-Name]/[YYYY-MM]/` and proceed.

---

### Step 1 — Load the Session Files

Place the session folders in `ingestion/cursor-chats/[project-name]/`. The expected path is:

```
ingestion/cursor-chats/[project-name]/[uuid]/[uuid].jsonl
```

You can group sessions by project to keep the analysis scoped.

---

### Step 2 — Extract User Messages

Run the extraction script from the project root. It scans all projects under `ingestion/cursor-chats/`, extracts user messages, and records subagent presence.

```
python scripts/extract_sessions.py
```

Output: `session_data.json` in the project root (gitignored).

The script prints a summary of all sessions found, including subagent counts. Review this output before proceeding — if session counts look wrong, check that files are placed at the correct path (`ingestion/cursor-chats/[project-name]/[uuid]/[uuid].jsonl`).

---

### Step 3 — Compute Pre-Analysis Stats and Select a Sample

Run the analysis script from the project root:

```
python scripts/analyse_sessions.py
```

Output: `analysis_stats.json` in the project root (gitignored).

This script computes quantitative signals across every session and classifies sessions by size:

| Tier | User Turns | What it represents |
|---|---|---|
| **Large** | 9+ turns | Complex, multi-step work — most signal-rich |
| **Medium** | 4–8 turns | Average sessions — typical prompting habits |
| **Small** | 1–3 turns | Either very efficient sessions or abandoned attempts |

**Recommended sample:** The script outputs up to 6 sessions from each tier (large / medium / small), ranked by richness. Read the sampled sessions in full — don't try to read every session. If the sample doesn't produce a clear enough picture of a particular habit (e.g., no debugging sessions in the sample), add 3 more from the relevant tier until the pattern is clear.

**What the stats tell you before you read a single session:**

- `at_refs` — what percentage of messages use `@` file references
- `cursor_commands` — whether the developer uses preloaded context commands (and which ones)
- `attached_files` — how often they attach code selections
- `plan_refs` — whether plan files are being referenced in prompts
- `mdc_refs` — whether `.mdc` cursor rules files are mentioned anywhere
- `verification` — presence of success criteria language
- `constraint_guards` — presence of "don't change X" scope boundaries
- `debug_structure` — presence of structured debugging language
- `sessions_with_subagents` — how many sessions triggered agent decomposition (positive signal)

Use the aggregate stats to form a hypothesis about each scoring category *before* reading sessions. Then use the sampled sessions to validate or revise that hypothesis with qualitative evidence.

**Key things to look for when reading the sampled sessions:**

- **Structural tags used:** `<user_query>`, `<attached_files>`, `<cursor_commands>`, `<image_files>`
- **Session opening style:** Does the first message establish clear context, or dive straight to a request?
- **Follow-up patterns:** How does the developer respond when AI output is incomplete or wrong?
- **Debugging behavior:** What information do they share when something isn't working?
- **Tone and precision:** Directive vs passive; specific vs vague; typos in technical terms

---

### Step 4 — Score Against the Rubric

Use the rubric below to evaluate patterns. Note each as: **Present / Partial / Absent**

**Context & Setup**

- [ ] Uses `@` references (or equivalent) to point AI at relevant files
- [ ] References existing documentation or architecture guides
- [ ] Uses session-opening context commands or preambles
- [ ] Shares prior session context when starting a new related session

**Scope & Clarity**

- [ ] Defines in-scope and out-of-scope in complex feature prompts
- [ ] Separates planning from implementation (plan first, then execute)
- [ ] Avoids ambiguous pronouns and implicit references ("it", "that", "the thing")
- [ ] Includes verification criteria ("I'll know it works when...")

**Debugging**

- [ ] Provides triggering action (what they did to cause the issue)
- [ ] Distinguishes expected vs actual behavior
- [ ] Shares raw logs or error output
- [ ] Knows when to start a fresh session vs continue iterating

**Session Management**

- [ ] Monitors context window usage
- [ ] Breaks large tasks into focused sessions
- [ ] Uses plan files for complex multi-step work
- [ ] Avoids mixing architectural pivots with bug fixes in the same message

**Reusability**

- [ ] Creates rules or conventions for patterns that repeat
- [ ] Creates context commands or presets for architecture and conventions
- [ ] Uses a mock/reference project as a "show don't tell" pattern

---

### Step 5 — Identify Session-Level Examples

For each area of strength and weakness, identify 2–3 specific quotes from the session data that illustrate the pattern. This makes the report concrete rather than abstract. Use the exact wording from the user's messages when possible.

---

### Step 6 — Write the Full Analysis Report

Use `templates/analysis-report-template.md` as the starting point. Save the new report to `reports/[Developer-Name]/[YYYY-MM]/[Name]-Prompting-Analysis.md`.

The report should contain:

1. **Executive Summary** — 2–3 sentences characterizing the developer's overall prompting maturity
2. **Session Inventory** — table of *key and notable sessions only* (not every session). Include sessions directly referenced in findings, representing a clear strength or weakness, or the best/worst examples. For large sample sizes (20+ sessions), aim for 8–12 highlighted sessions.
3. **What You're Doing Well** — 5–8 strengths with specific examples and explanation of why each matters
4. **What Could Be Better** — 5–7 weaknesses with concrete recommendations for each
5. **Patterns by Session Type** — breakout by the types of work they use AI for (architecture, debugging, implementation, etc.)
6. **Top 5 Recommendations** — prioritized, actionable, specific to this developer
7. **Standout Prompts** — 3–5 specific prompts from their history worth repeating as templates

---

### Step 7 — Produce the Scorecard HTML

The HTML scorecard is an interactive single-page report. Use `templates/scorecard-mockup.html` as the master template.

**How to generate a new scorecard:**

1. Copy `templates/scorecard-mockup.html` to `reports/[Developer-Name]/[YYYY-MM]/[Name]-Scorecard.html`
2. Remove the mock callout banner (the `<div class="mock-banner">` block at the top)
3. Update the header section:
   - Developer name (`<h1>`)
   - Project tags (one `<span class="tag">` per project reviewed)
   - Analysis date, session count, user turn count
   - Link to the full analysis report
4. Update the Maturity Level section:
   - Set the level number and level name
   - Fill the maturity pips (filled = `●`, empty = `○`) to reflect the correct level (e.g., Level 3 = `●●●○○`)
5. Update the Category Scores table:
   - Set the score (X/5) for each of the 9 categories
   - Set the rating dots: filled `●` for earned points, empty `○` for remaining (5 dots per row)
   - Color coding: blue (`dot-blue`) for 4–5, orange (`dot-orange`) for 3, red (`dot-red`) for 1–2
   - If building on history (Step 0 choice B): add the delta indicator (`↑`, `↓`, or `→`) next to each score using the `.delta-up`, `.delta-down`, `.delta-flat` CSS classes
6. Update the Overall score and progress bar percentage (`(total/45)*100`)
7. **Trend section** (only when building on history): populate the Trend vs Last Report section — list categories that moved up or down, overall delta, and any sample-size caveats. Remove this section entirely if starting fresh.
8. Update Quick Take: 3 strengths and 3 watch outs (one sentence each)
9. Update Top 3 Recommendations (numbered, one to two sentences each)
10. The Reference Guide section at the bottom is **static** — do not change it

**Category IDs for the click-to-expand links** (used in `onclick="openDef('def-X')"` and `id="def-X"`):

- `def-context` — Context Engineering
- `def-instruction` — Instruction Quality
- `def-example` — Example-Based Guidance
- `def-scope` — Scope Definition
- `def-debug` — Debugging Discipline
- `def-session` — Session Management
- `def-reuse` — Reusability Investment
- `def-verify` — Verification Habits
- `def-plan` — Plan-Before-Build

---

### Step 8 — Produce the Scorecard MD

The markdown scorecard is a portable version of the scorecard. Use `templates/scorecard-template.md` as the master template.

**How to generate a new scorecard MD:**

1. Copy `templates/scorecard-template.md` to `reports/[Developer-Name]/[YYYY-MM]/scorecard-template.md` (or rename to `[Name]-Scorecard.md` if preferred)
2. Update the header: developer name, projects reviewed, analysis date, session stats, link to full report
3. Set the Maturity Level: number and name. Bold the correct level name in the maturity level row
4. Fill in the Category Scores table: score (X/5) and rating dots for each of the 9 categories
5. Update Overall score total (XX / 45)
6. Fill in Quick Take: 3 strengths, 3 watch outs
7. Fill in Top 3 Recommendations
8. The Reference Guide section at the bottom is **static** — leave it unchanged

---

### Step 9 — Calibrate Tone

All outputs are coaching tools, not performance reviews. Keep the tone:

- Specific and evidence-based (quote from actual sessions)
- Constructive on weaknesses (explain the failure mode, not just the gap)
- Respectful of the developer's existing habits (don't dismiss what's working)
- Practical (every recommendation should be actionable next session)

---

### Step 10 — Update the History File

After all three output files are saved, update `reports/[Developer-Name]/history.json`. If the file doesn't exist, create it. Append a new entry to the `reports` array:

```json
{
  "developer": "[Developer Full Name]",
  "reports": [
    {
      "date": "YYYY-MM-DD",
      "month": "YYYY-MM",
      "session_count": 0,
      "user_turns": 0,
      "scores": {
        "context_engineering": 0,
        "instruction_quality": 0,
        "example_based": 0,
        "scope_definition": 0,
        "debugging": 0,
        "session_management": 0,
        "reusability": 0,
        "verification": 0,
        "plan_before_build": 0
      },
      "total": 0,
      "maturity_level": 0,
      "maturity_name": "[Level Name]",
      "strengths": ["Category Name", "Category Name"],
      "weaknesses": ["Category Name", "Category Name"],
      "sample_note": "Brief note on sample size, projects covered, or any thin-sample caveats that may have affected scores."
    }
  ]
}
```

**Notes on the history file:**

- If the file already exists, preserve existing entries and append the new one — never overwrite the array
- `history.json` lives at `reports/[Developer-Name]/history.json`, one level above the monthly subfolders
- It is gitignored along with all other content under `reports/` — it is a local record only. If the reports folder is cleared, the history is lost; users who want long-term tracking should back it up separately
- The `sample_note` field is important: future runs use it to distinguish genuine score changes from sample-size variation

---

## Scoring Guide

### Nine Categories (each scored 1–5)

| Category               | What It Measures                                                                |
| ---------------------- | ------------------------------------------------------------------------------- |
| Context Engineering    | Use of references, docs, examples, and role-setting to give AI accurate context |
| Instruction Quality    | Clarity, action verbs, specificity, avoidance of ambiguity                      |
| Example-Based Guidance | Shows AI what's wanted via mocks, reference files, or sample output (few-shot)  |
| Scope Definition       | In/out-of-scope boundaries, constraint guards, edge case handling               |
| Debugging Discipline   | Structured bug reports: triggering action → expected → actual → logs            |
| Session Management     | Context window awareness, fresh-start discipline, cross-session continuity      |
| Reusability Investment | Rules, context commands, and prompt templates to reduce repeated setup          |
| Verification Habits    | Upfront success criteria and explicit verification requests                     |
| Plan-Before-Build      | Scoping and proposing before implementation; plan files for complex work        |

**Total: X / 45**

### Score Level Definitions

Use these definitions to anchor scores consistently. Every score should be justifiable with evidence from the session data.

**Context Engineering**
- **1** — No file references. All prompts describe what they want in prose. AI infers project structure from scratch every session.
- **2** — Occasional file references, inconsistently applied. Some sessions are grounded; many aren't.
- **3** — File references in most sessions but not every message. Documentation referenced on complex tasks; lighter requests proceed without context anchors.
- **4** — File references in nearly every message. Architecture docs and plan files used as session openers. Sessions rarely start cold.
- **5** — Systematic context injection via preloaded commands. AI never needs clarifying questions about the codebase.

**Instruction Quality**
- **1** — Passive and vague ("can you look at this?", "any ideas?"). Multiple concerns bundled without priority. Typos in technical identifiers.
- **2** — Mix of passive and directive. Some clear task statements; vague follow-ups and ambiguous pronouns appear regularly.
- **3** — Mostly directive with occasional passive requests. Generally specific but sometimes bundles multiple concerns. Typos appear in prose, rarely in identifiers.
- **4** — Consistently action-oriented. Single clear outcome per prompt. File paths and method names used precisely.
- **5** — Every prompt is tightly scoped, precisely worded, and contains a single clear outcome. Identifiers always exact. No ambiguity.

**Example-Based Guidance**
- **1** — Always describes desired output in prose. AI generates from scratch using its defaults. No reference files or mocks.
- **2** — Occasionally attaches code or references an existing file, but most requests are prose descriptions.
- **3** — Sometimes uses code attachments or reference files, particularly on complex tasks. Relies on prose for simpler requests.
- **4** — Regularly shows the AI what's wanted via attached code, reference files, or "build it like X" patterns. AI matches conventions immediately.
- **5** — Every non-trivial request includes a reference implementation or expected output. Few-shot prompting is the default approach.

**Scope Definition**
- **1** — No scope boundaries stated. AI modifies whatever it thinks is relevant. Frequent unwanted changes to adjacent files.
- **2** — Scope occasionally mentioned but not systematically. Some constraint guards in some sessions; most have none.
- **3** — Scope often implicit (defined by which files are referenced) but rarely stated explicitly. Constraint guards appear on some complex tasks.
- **4** — Complex tasks include explicit in/out-of-scope statements. Constraint guards appear on most multi-file tasks.
- **5** — Every complex prompt has an explicit scope boundary. Out-of-scope items are always listed. AI never makes unwanted changes.

**Debugging Discipline**
- **1** — Bug reports are vague ("it's broken", "this doesn't work"). No trigger, expected, actual, or logs. AI needs many follow-up questions.
- **2** — Some context provided (error message or code snippet) but triggering action and expected behavior are missing or implicit.
- **3** — Provides what went wrong and usually the error output, but trigger and expected behavior are often implicit. Structured format used occasionally.
- **4** — Most bug reports include trigger, expected, actual, and a log reference. AI can diagnose in 1–2 turns.
- **5** — Every debugging session opens with the full format: trigger → expected → actual → logs. AI diagnoses in one turn. Fresh-start discipline is applied when sessions run long.

**Session Management**
- **1** — Sessions continue until AI output degrades. No strategy for starting fresh or carrying context across sessions.
- **2** — Some awareness of session scope but no systematic strategy. Long sessions run without recap or reset. New sessions start cold.
- **3** — Sessions are generally focused (3–8 turns on average). Occasional long sessions without reset. Some cross-session continuity via file references but no explicit recaps.
- **4** — Proactively splits work into focused sessions. Inserts context recap when sessions run long. New sessions open with a summary of prior work.
- **5** — Every session is deliberately scoped. Cross-session handoffs are explicit. Context window is actively monitored and reset before drift occurs.

**Reusability Investment**
- **1** — No reusable commands, rules, or templates. Same context re-explained in every session.
- **2** — One or two context commands exist but are rarely used. Most sessions start from scratch.
- **3** — Has created a small number of context commands and uses them in some sessions. Rules or templates may exist but aren't systematically applied.
- **4** — Active library of context commands covering the main project areas. Commands are used at session open. Some Cursor rules (`.mdc`) exist.
- **5** — Comprehensive command library. Every session type has a matching command. Cursor rules enforce patterns automatically. Setup time is near zero.

*Note: Auto-scoped `.mdc` rules are invisible in session files. If signals suggest rules are in use (see the Understanding section above), score accordingly and note the limitation.*

**Verification Habits**
- **1** — No success criteria ever stated. Verification is entirely reactive — run the app, see what breaks, loop back.
- **2** — Success criteria appear very rarely. Occasionally mentions how something will be tested, but after the fact.
- **3** — Occasionally states how a feature will be tested, or mentions a specific expected outcome. Not a consistent habit.
- **4** — Most complex prompts include "I'll know this is done when..." or a specific verification step. AI is sometimes asked to confirm output meets criteria.
- **5** — Every implementation prompt has explicit success criteria upfront. AI is always asked to self-check against stated criteria before finishing.

**Plan-Before-Build**
- **1** — Always jumps straight to implementation. No planning step for any complexity level.
- **2** — Occasionally asks for a plan on very complex features, but most implementation work starts without scoping. Plan files exist but are rarely referenced.
- **3** — Sometimes requests a plan first, particularly on larger features. Plan files are created and referenced in some sessions but not consistently at session open.
- **4** — Complex features consistently start with a plan review. Plan files are used as session openers. Execution sessions reference the plan as a source of truth.
- **5** — No multi-file change begins without an approved plan. Planning and execution are always separate sessions. Plans are living documents updated as work progresses.

### Maturity Levels

| Level | Name           | Description                                                                                                                                                             |
| ----- | -------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1     | Conversational | Treats AI like a chat interface. No file references, relies on AI to infer all context. High back-and-forth, frequent corrections.                                      |
| 2     | Task-Oriented  | Gives the AI clear tasks but doesn't pre-load context. Uses some file references but inconsistently. Debugging is trial-and-error.                                      |
| 3     | Context-Aware  | Consistently uses file references and docs. Has discovered some reusable patterns. Good architectural collaboration but ad-hoc session management.                      |
| 4     | Systematic     | Has a library of context commands. Every session opens with context-setting. Debugging follows a structured format. Plans and executes in separate sessions by default. |
| 5     | Expert         | Designs prompts as reusable templates. Uses AI for verification as well as generation. Creates and maintains team-wide prompt libraries. Actively coaches others.       |

---

## Common Patterns Across Developers

Based on patterns observed across initial analyses, these are worth looking for in every developer's sessions:

**Universal strengths to praise if present:**

- Using file references (`@` in Cursor, or equivalent in other tools)
- Sharing raw logs during debugging
- Working iteratively on architecture rather than asking for a complete solution upfront

**Universal weaknesses to check for:**

- Missing triggering action in bug reports
- No explicit success criteria
- Long single sessions on the same problem
- Dense multi-concern opening prompts

**The "typos in technical prompts" issue:**
Most developers type quickly in AI sessions and have higher-than-normal typo rates. For domain-specific terms (class names, variable names, file paths), typos can cause the AI to misidentify a class or file name. Mention this gently — it's not about grammar, it's about precision in the terms that matter.

---

## Notes on Session Selection

The `analyse_sessions.py` script produces a recommended sample of up to 6 sessions per size tier (large / medium / small). Use that as the starting point. Manual guidance:

- **Large sessions (9+ turns):** Highest priority — complex work reveals the most about context habits, debugging style, and session management. Always read these.
- **Medium sessions (4–8 turns):** Represent the developer's average working style. Read at least 4–5 to establish baseline patterns.
- **Small sessions (1–3 turns):** Can be efficient (developer got what they needed quickly) or abandoned (developer gave up). Read a sample of 3–4 to calibrate which it is. One-off lookup sessions add little signal and can be skipped.
- **Watch for:** Sessions where the developer mentions switching tools mid-way (ChatGPT, another model) — these reveal gaps in their current workflow.

If the initial sample doesn't give a clear picture of a specific habit (e.g., no debugging sessions in the sample), add 3 more sessions from the relevant tier until the pattern becomes clear.

---

## Files Produced

Each team member's analysis produces the following files in `reports/[Developer-Name]/[YYYY-MM]/`:

| File                           | Description                    |
| ------------------------------ | ------------------------------ |
| `[Name]-Prompting-Analysis.md` | Full narrative analysis report |
| `[Name]-Scorecard.html`        | Interactive HTML scorecard     |
| `scorecard-template.md`        | Portable markdown scorecard    |

Master templates — never edit directly, always copy to `reports/[Developer-Name]/[YYYY-MM]/` first:

| File                                    | Description                          |
| --------------------------------------- | ------------------------------------ |
| `templates/analysis-report-template.md` | Full analysis report template        |
| `templates/scorecard-mockup.html`       | Interactive HTML scorecard template  |
| `templates/scorecard-template.md`       | Portable markdown scorecard template |
| `PROCESS.md`                            | This process guide                   |

Helper scripts (run from project root, outputs are gitignored):

| File                          | Description                                                    |
| ----------------------------- | -------------------------------------------------------------- |
| `scripts/discover_cursor.py`  | Scans .cursor folder and lists available projects + session counts |
| `scripts/import_cursor.py`    | Copies chosen sessions from .cursor into ingestion/ (supports --days filter) |
| `scripts/extract_sessions.py` | Extracts all user messages from ingestion → `session_data.json`  |
| `scripts/analyse_sessions.py` | Computes signal stats + recommends sample → `analysis_stats.json` |

---

## Improvement Log

| Date          | Change                                                                                                                                                                                                                                                                                                                                                                                                                          |
| ------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| March 2026 v1 | Initial process established. Python extraction script developed. Rubric v1 created. Folder structure defined: `ingestion/cursor-chats/`, `ingestion/other-chats/`, `reports/[Name]/[YYYY-MM]/`. Scorecard HTML and MD generation steps added. Step 0 added: confirm developer name before starting. PROCESS.md introduced as tool-agnostic process guide; CLAUDE.md and STARTER_PROMPT.md become thin bootstraps pointing here. |
| March 2026 v2 | Added `scripts/` folder with `extract_sessions.py` (replaces inline extraction code block) and `analyse_sessions.py` (new pre-analysis stats script). Added tiered sampling strategy (6 large / 6 medium / 6 small sessions). Added score 3 definitions for all 9 categories. Updated subagent guidance: subagents are auto-spawned by Cursor agent, their presence is a positive signal, their content is not reviewed. Updated cursor rules section: explains what session-file signals indicate rules usage rather than directing reviewer to request the rules files. Clarified ingestion folder as single-person drop zone; project folder name = Cursor project slug. Fixed `CONTEXT.md` reference bug in analysis-report-template.md footer. |
| March 2026 v3 | Improved `.cursor` folder discovery UX in CLAUDE.md: replaced "ask for username" with a three-option prompt (A: user folder path, B: full .cursor path, C: manual drop into ingestion). Added step-by-step instructions for Windows (`%USERPROFILE%`) and macOS (`Cmd+Shift+H`, hidden files tip). Added Step 0 guard in PROCESS.md: checks for an existing report for the current developer and month before starting — prompts user to overwrite or create a versioned copy (v2, v3, etc.). |
| March 2026 v4 | Added history tracking system. New `reports/[Developer-Name]/history.json` file stores a lightweight summary of every completed report (scores, session count, maturity level, strengths, weaknesses, sample note). Step 0 expanded: checks for history.json and asks user whether to start fresh or build on prior reports. Step 10 added: write/append history.json after every completed analysis. Analysis report template gains optional "Progress Since Last Review" section with category delta table and trend narrative. HTML and markdown scorecard templates gain optional Trend vs Last Report section with ↑/↓/→ indicators per category and overall delta. Sample-size caveat logic added: persistent low scores flagged as confirmed patterns; single-report drops flagged as potential sample artifacts. |

---

*The goal of this process is not uniformity — different developers will have different strengths — but deliberate, evidence-based improvement.*
