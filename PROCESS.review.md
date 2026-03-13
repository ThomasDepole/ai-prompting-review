# AI Prompting Pattern Review — Stage 1: Analysis & Scoring

**When to load this file:** After running `analyse_sessions.py` (Step 3 in `PROCESS.md`). This file covers reading sessions, scoring all 9 categories, and writing the scoring scratch pad. When Stage 1 is complete, proceed to `PROCESS.report.md`.

---

## Understanding What Session Files Can and Cannot See

Before scoring, understand that AI coding tools have **multiple layers of context** — session files only expose some of them.

### For Cursor AI (four layers):

**Layer 1 — Chat messages (fully visible in `.jsonl`):**
Everything typed by the user: `<user_query>` blocks, `@` file references, `<attached_files>` code selections. This is what session files capture.

**Layer 2 — Context commands (`<cursor_commands>`, visible):**
When a developer triggers a saved command, the full contents are embedded directly in the user message as a `<cursor_commands>` block. Fully readable.

**Layer 3 — Auto-scoped `.mdc` rules (invisible — the blind spot):**
Cursor rules in `.cursor/rules/*.mdc` with a `globs:` scope are automatically injected before the session starts. They do not appear in the session file. The AI follows them silently.

**What this means for scoring:** Session files give a true picture of chat prompting style but an incomplete picture of total context engineering. A developer with substantial `.mdc` rules may look like they're giving sparse prompts when they've actually front-loaded architectural guidance invisibly.

**How to detect cursor rules usage — look for:**
- References to `.mdc` files anywhere in user or assistant messages (`analyse_sessions.py` flags these)
- AI responses applying conventions the developer never stated — suggests auto-injected rules
- The developer referencing `.cursor/rules/` explicitly in conversation

**Scoring note:** When Reusability Investment appears low based on session files alone, note this limitation. Flag it and ask the developer to confirm during the review.

**Layer 4 — Subagents (auto-spawned, not user-controlled):**
Subagents are launched automatically by the orchestrating agent — not by the user. Their presence is a **positive signal about the user's prompting**: it means their prompt was well-scoped and complex enough to trigger decomposition. Subagent content is not reviewed; only their presence is counted.

---

## Step 3 (continued) — Read the Sampled Sessions

`analyse_sessions.py` has already identified the recommended sample. Now read those sessions.

**Read from `temp/session_data.json` — not the raw source JSONL files.**

Load `temp/session_data.json` (produced by `extract_sessions.py`) and look up each sampled session by its `id`. The `user_messages` array contains the complete ordered sequence of user turns — this is everything needed for scoring.

Do **not** open raw JSONL files from `~/.cursor/projects/` or `ingestion/cursor-chats/`. Those files include full assistant responses which are not relevant to scoring prompting habits and will consume significant context. `temp/session_data.json` was built to give you the signal without the noise.

**Known limitation:** Reading only user messages means you can observe how a developer follows up, but not what the AI said that prompted the follow-up. For scoring the 9 rubric categories (which are all about developer behavior, not AI quality), this is sufficient. For deeper analysis of specific follow-up patterns, this is a blind spot — note it if relevant to your findings.

**What to look for in each session:**
- **Structural tags used:** `<user_query>`, `<attached_files>`, `<cursor_commands>`, `<image_files>`
- **Session opening style:** Does the first message establish context, or dive straight to a request?
- **Follow-up patterns:** How does the developer respond when AI output is incomplete or wrong? The sequence of user turns reveals this — the follow-up IS the reaction.
- **Debugging behavior:** What information do they share when something isn't working?
- **Tone and precision:** Directive vs passive; specific vs vague; typos in technical terms

---

## Step 4 — Score Against the Rubric

Use the checklist below to evaluate patterns. Mark each as **Present / Partial / Absent**, then assign a score from the definitions below.

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

## Step 5 — Identify Session-Level Examples

For each area of strength and weakness, identify 2–3 specific quotes from the session data that illustrate the pattern. Use the exact wording from the user's messages. This makes the report concrete rather than abstract.

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

*Note: Auto-scoped `.mdc` rules are invisible in session files. If signals suggest rules are in use, score accordingly and note the limitation.*

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

## Notes on Session Selection

The `analyse_sessions.py` script produces a recommended sample of up to 6 sessions per size tier. Use that as the starting point.

- **Large sessions (9+ turns):** Highest priority — complex work reveals the most about context habits, debugging style, and session management. Always read these.
- **Medium sessions (4–8 turns):** Represent the developer's average working style. Read at least 4–5 to establish baseline patterns.
- **Small sessions (1–3 turns):** Can be efficient (developer got what they needed quickly) or abandoned. Read a sample of 3–4. One-off lookup sessions add little signal and can be skipped.
- **Watch for:** Sessions where the developer mentions switching tools mid-way — these reveal gaps in their current workflow.

If the initial sample doesn't give a clear picture of a specific habit (e.g., no debugging sessions in the sample), add 3 more sessions from the relevant tier until the pattern becomes clear.

---

## Common Patterns Across Developers

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

## Step 6 — Write the Scoring Scratch Pad

After scoring all 9 categories and identifying examples, write `temp/scoring_scratch.json`. This file is the complete handoff to Stage 2. Write it with enough detail that Stage 2 can produce a high-quality report without reading any session content.

**Be thorough in this file.** Use verbatim quotes, not paraphrases. Include specific session IDs. The report quality in Stage 2 is entirely dependent on the richness of what you write here.

```json
{
  "developer": "Full Name",
  "reviewed_at": "YYYY-MM-DD",
  "total_sessions": 0,
  "total_user_turns": 0,
  "sessions_reviewed": ["session_id_1", "session_id_2"],
  "projects_reviewed": ["project-slug-1", "project-slug-2"],
  "build_on_history": false,
  "history_deltas": {},
  "sample_note": "Brief note on sample size, projects covered, or thin-sample caveats — e.g. 'First report; 14 sessions across 9 projects, all within one week. Small dataset — scores may shift as history grows.'"

  "aggregate_observations": "Free text: overall impression from the stats and sessions. What stands out across the dataset before individual scoring.",

  "cross_session_patterns": "Write this BEFORE scoring individual categories. Free text capturing patterns that span multiple sessions and don't fit neatly into one category. Examples: a constraint the developer applies consistently across all sessions (e.g. 'always asks for a proposal before executing'), a habit that only becomes visible when sessions are compared side by side (e.g. 'invites pushback in every design conversation'), or a thinking style that cuts across session types. These observations are easily lost when attention shifts to per-category scoring — record them here first so Stage 2 can surface them in the report.",

  "category_scores": {
    "context_engineering": {
      "score": 0,
      "rationale": "1–2 sentences anchored to specific evidence. Quote the session or stat.",
      "evidence": [
        "Verbatim quote from user_messages, e.g. '@GoSocialMauiApp can you review the folder structure'",
        "Second verbatim quote"
      ],
      "session_refs": ["session_id"]
    },
    "instruction_quality": { "score": 0, "rationale": "", "evidence": [], "session_refs": [] },
    "example_based_guidance": { "score": 0, "rationale": "", "evidence": [], "session_refs": [] },
    "scope_definition": { "score": 0, "rationale": "", "evidence": [], "session_refs": [] },
    "debugging_discipline": { "score": 0, "rationale": "", "evidence": [], "session_refs": [] },
    "session_management": { "score": 0, "rationale": "", "evidence": [], "session_refs": [] },
    "reusability_investment": { "score": 0, "rationale": "", "evidence": [], "session_refs": [] },
    "verification_habits": { "score": 0, "rationale": "", "evidence": [], "session_refs": [] },
    "plan_before_build": { "score": 0, "rationale": "", "evidence": [], "session_refs": [] }
  },

  "total_score": 0,
  "maturity_level": 0,
  "maturity_name": "Level Name",

  "strengths": [
    {
      "category": "Category Name",
      "summary": "One sentence description of the strength",
      "example": "Verbatim quote or specific session description that illustrates it"
    }
  ],

  "weaknesses": [
    {
      "category": "Category Name",
      "summary": "One sentence description of the gap",
      "recommendation": "Specific, actionable recommendation tailored to this developer's actual usage"
    }
  ],

  "standout_prompts": [
    {
      "text": "Verbatim prompt text — copy exactly from user_messages",
      "session_id": "uuid",
      "why_notable": "One sentence: what makes this prompt worth repeating as a template"
    }
  ],

  "top_recommendations": [
    "Prioritized recommendation 1 — most impactful, specific to this developer",
    "Prioritized recommendation 2",
    "Prioritized recommendation 3",
    "Prioritized recommendation 4",
    "Prioritized recommendation 5"
  ],

  "session_type_patterns": {
    "architecture": "Observations about how they approach architecture sessions",
    "debugging": "Observations about debugging sessions",
    "implementation": "Observations about implementation sessions",
    "other": "Any other session type patterns worth noting"
  }
}
```

---

## Transition to Stage 2

Once `temp/scoring_scratch.json` is written, Stage 1 is complete. Load `PROCESS.report.md` for report generation instructions.

**If your tool supports subagents:** spawn a fresh subagent for Stage 2. Pass it only `temp/scoring_scratch.json` and instruct it to read `PROCESS.report.md`. It does not need `temp/session_data.json`, `temp/analysis_stats.json`, or any session content.

**If your tool does not support subagents:** continue in the current context. `temp/scoring_scratch.json` is the complete record — you do not need to re-read session content during Stage 2. Load `PROCESS.report.md` and proceed.
