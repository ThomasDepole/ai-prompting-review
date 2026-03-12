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
│   │   └── [project-name]/       ← One folder per project
│   │       └── [uuid]/
│   │           └── [uuid].jsonl
│   └── other-chats/              ← Placeholder for future chat sources
│                                    (e.g. ChatGPT exports, Copilot logs, etc.)
│
├── reports/                      ← All analysis outputs go here
│   └── [Developer-Name]/         ← Subfolder per developer
│       └── [YYYY-MM]/            ← Subfolder per month/run
│           ├── [Name]-Prompting-Analysis.md
│           ├── [Name]-Scorecard.html
│           └── scorecard-template.md
│
└── templates/                    ← Master templates (never edit directly — copy per developer)
    ├── analysis-report-template.md
    ├── scorecard-mockup.html
    └── scorecard-template.md
```

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
Cursor rules stored in `.cursor/rules/*.mdc` with a `globs:` scope pattern are automatically injected by Cursor before the session starts. They do not appear anywhere in the session file. The AI silently follows them without attribution. You would only know they existed if:

- The AI explicitly reads or creates a rule file (detectable via `.mdc` references in assistant responses)
- The developer tells you about them during the review

**What this means for the analysis:** Session files give a true picture of the developer's *chat prompting style* but an incomplete picture of their total *context engineering*. A developer who has invested heavily in `.cursor/rules/` files may look like they're giving sparse prompts, when in fact they've front-loaded architectural guidance invisibly.

**Recommendation:** Always ask the developer to share their `.cursor/rules/` directory alongside their session files. Review the rules as part of the analysis.

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

### Step 0 — Confirm the Developer's Name

Before doing anything else, confirm the full name of the developer being reviewed. This name is used as the folder name under `reports/` and as the label throughout all three output files.

If the name was not supplied with the initial request, ask: **"What is the full name of the developer we're reviewing?"**

Use the name exactly as provided (e.g. `Jane Smith`, not `jane-smith` or `JaneSmith`). The folder should be created at `reports/[Developer-Name]/[YYYY-MM]/` before writing any output files.

---

### Step 1 — Load the Session Files

Place the session folders in `ingestion/cursor-chats/[project-name]/`. The expected path is:

```
ingestion/cursor-chats/[project-name]/[uuid]/[uuid].jsonl
```

You can group sessions by project to keep the analysis scoped.

---

### Step 2 — Extract User Messages

Run the following Python script to extract all user messages from all sessions into a structured JSON file for analysis. Update the `base` path to point to the project you're analysing.

```python
import json, os

base = "ingestion/cursor-chats/project-name"
sessions = []

for session_id in sorted(os.listdir(base)):
    fpath = os.path.join(base, session_id, f"{session_id}.jsonl")
    if not os.path.exists(fpath):
        continue

    with open(fpath) as f:
        lines = f.readlines()

    user_msgs = []
    assistant_turns = 0

    for line in lines:
        obj = json.loads(line)
        role = obj.get('role', '')
        if role == 'user':
            content = obj['message']['content']
            for c in content:
                if c.get('type') == 'text':
                    user_msgs.append(c['text'])
        elif role == 'assistant':
            assistant_turns += 1

    sessions.append({
        'id': session_id,
        'total_lines': len(lines),
        'user_turns': len(user_msgs),
        'assistant_turns': assistant_turns,
        'user_messages': user_msgs
    })

with open('session_data.json', 'w') as f:
    json.dump(sessions, f, indent=2)

print(f"Extracted {len(sessions)} sessions")
for s in sessions:
    print(f"  {s['id'][:8]}... | user: {s['user_turns']} | assistant: {s['assistant_turns']}")
```

---

### Step 3 — Read the Data

The analysis reads the raw text of every user message. Key things to look for:

- **Structural tags used:** `<user_query>`, `<attached_files>`, `<cursor_commands>`, `<image_files>`
- **Context injection methods:** `@` file references, embedded documentation, plan file references
- **Session opening style:** Does the first message establish clear context, or dive straight to a request?
- **Follow-up patterns:** How does the developer respond to AI questions or incomplete outputs?
- **Debugging behavior:** What information do they share when something isn't working?
- **Session length and scope:** How many turns per session? Are sessions focused or sprawling?

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
6. Update the Overall score and progress bar percentage (`(total/45)*100`)
7. Update Quick Take: 3 strengths and 3 watch outs (one sentence each)
8. Update Top 3 Recommendations (numbered, one to two sentences each)
9. The Reference Guide section at the bottom is **static** — do not change it

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

Not all sessions are equally useful for analysis. When selecting sessions to review:

- **Include:** Architecture sessions, complex feature implementation sessions, debugging sessions with multiple turns
- **De-prioritize:** Very short sessions (1–2 turns), sessions that are clearly one-off lookups, sessions where the developer is exploring the AI tool itself
- **Watch for:** Sessions where the developer mentions switching tools mid-way (ChatGPT, another model) — these reveal gaps in their current workflow

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

---

## Improvement Log

| Date       | Change                                                                                                                                                                                                                                                                                                                                                                                                                          |
| ---------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| March 2026 | Initial process established. Python extraction script developed. Rubric v1 created. Folder structure defined: `ingestion/cursor-chats/`, `ingestion/other-chats/`, `reports/[Name]/[YYYY-MM]/`. Scorecard HTML and MD generation steps added. Step 0 added: confirm developer name before starting. PROCESS.md introduced as tool-agnostic process guide; CLAUDE.md and STARTER_PROMPT.md become thin bootstraps pointing here. |

---

*The goal of this process is not uniformity — different developers will have different strengths — but deliberate, evidence-based improvement.*
