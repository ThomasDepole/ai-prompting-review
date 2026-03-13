# Post-Test Diagnostic — AI Prompting Review Process

**Purpose:** Supply this file to a new session after running a fresh report test. The session should read this file, locate the test run transcript, and work through the checklist below to evaluate how the optimisations performed.

---

## Background — What Was Optimised

The first end-to-end test run (session `d2ae932a`) revealed significant context window bloat. The following changes were made before this test:

### v6 — Read `temp/session_data.json`, not raw JSONL files
**Problem:** The agent read raw source JSONL files for each session. These contain full assistant responses (multi-paragraph reasoning, code blocks) that are irrelevant to scoring. Only user messages are needed.
**Fix:** PROCESS.review.md and the cursor rule now explicitly mandate `temp/session_data.json`. The instruction now says "do not open raw JSONL files."
**What to check:** Did the agent read `temp/session_data.json` or did it open files from `~/.cursor/projects/`?

### v7 — Three-file PROCESS split + scoring scratch pad
**Problem:** The agent loaded all 650 lines of PROCESS.md at the start and held that context through scoring and report writing. Scoring and report generation happened in the same context window with no handoff point.
**Fix:** PROCESS.md split into three phase-scoped files. `temp/scoring_scratch.json` introduced as the Stage 1→2 handoff artifact. Each phase loads only what it needs.
**What to check:**
- Did the agent load PROCESS.review.md only after Step 3 (not at the start)?
- Did the agent write `temp/scoring_scratch.json` before moving to report generation?
- Was the scratch pad rich enough (scores + evidence quotes + recommendations)?
- Did the agent load PROCESS.report.md for Stage 2 rather than re-reading PROCESS.review.md?

### v8 — `temp/` folder for process artifacts
**Problem:** Intermediate files (`session_data.json`, `analysis_stats.json`, `scoring_scratch.json`) lived in the project root, weren't cleaned up, and could accumulate.
**Fix:** All intermediate files now go to `temp/`. Scripts create it automatically. Step 11 deletes it at the end. Step 0 detects stale temp folders and offers resume or fresh start.
**What to check:**
- Was `temp/` created by the scripts?
- Did the agent delete `temp/` at the end (Step 11)?
- If the test session ended abruptly, does `temp/` still exist with the right files?

---

## How to Run the Diagnostic

1. Locate the transcript for the test run. It will be in:
   ```
   ~/.cursor/projects/Users-tdepole-Cowork-Spaces-Ai-Prompting-Review/agent-transcripts/
   ```
   Find the most recent session UUID and read the JSONL file.

2. Work through each checklist item below. For each one, note: **Pass**, **Fail**, or **Partial** with a brief observation.

3. At the end, summarise findings and recommend next steps.

---

## Diagnostic Checklist

### File Access Patterns

- [ ] **Raw JSONL files not opened** — the agent should have read `temp/session_data.json`, not any file path containing `agent-transcripts` or `.cursor/projects`. *Look for: file read tool calls pointing to `~/.cursor/projects/.../*.jsonl`*

- [ ] **`temp/session_data.json` used for session content** — the agent should have loaded this file and looked up sessions by `id`. *Look for: a single read of `temp/session_data.json` followed by per-session lookup, not multiple JSONL reads.*

- [ ] **`temp/analysis_stats.json` used for aggregate signals** — the stats file should have been read once, early, before session reading. *Look for: a single read of `temp/analysis_stats.json`.*

- [ ] **`temp/` folder created and cleaned up** — `temp/` should have been created by the script run and deleted in Step 11. *Check the filesystem: does `temp/` still exist? If so, either cleanup was skipped or the session ended early.*

---

### Phase Loading Order

- [ ] **PROCESS.md read at start only** — the agent should have read PROCESS.md for setup (Steps 0–3) and not re-read it during scoring or report writing. *Look for: PROCESS.md read calls after Step 3.*

- [ ] **PROCESS.review.md loaded after Step 3** — not at session start. *Look for: when PROCESS.review.md was first read relative to when `analyse_sessions.py` was run.*

- [ ] **PROCESS.report.md loaded after scoring complete** — not before `temp/scoring_scratch.json` was written. *Look for: when PROCESS.report.md was first read.*

---

### Scratch Pad Quality

- [ ] **`temp/scoring_scratch.json` was written** — Stage 1 should have produced this file before any report writing began. *Look for: a file write to `temp/scoring_scratch.json`.*

- [ ] **Scratch pad contains verbatim quotes** — the `evidence` arrays should contain actual quoted text from user messages, not paraphrases. *Read the scratch pad if it still exists, or look for quoted evidence in the session transcript.*

- [ ] **All 9 categories scored** — check the scratch pad has a score and rationale for each: `context_engineering`, `instruction_quality`, `example_based_guidance`, `scope_definition`, `debugging_discipline`, `session_management`, `reusability_investment`, `verification_habits`, `plan_before_build`.

- [ ] **`projects_reviewed` populated** — should be a list of project slug names, not UUIDs. *Check the scratch pad or the HTML scorecard tags.*

- [ ] **`sample_note` populated** — should be a brief, specific note about the dataset size and any caveats.

---

### Report Quality

- [ ] **All three output files produced** — `[Name]-Prompting-Analysis.md`, `[Name]-Scorecard.html`, `scorecard-template.md` all exist in `reports/[Name]/[YYYY-MM]/`.

- [ ] **HTML scorecard project tags populated** — open the HTML file and check the tag pills in the header reflect the actual projects reviewed, not placeholder text.

- [ ] **Standout prompts are verbatim** — check the analysis report's "Standout Prompts" section. Quotes should match actual session content.

- [ ] **`history.json` updated** — `reports/[Developer-Name]/history.json` should exist with an entry for this run.

---

### Subjective Assessment

- [ ] **Context window headroom** — compare to the first run (session `d2ae932a`) which felt very full. Did this run feel lighter? Was there any context warning or degradation in output quality toward the end?

- [ ] **Report quality parity** — does the report produced in this run match the depth and specificity of the first run? If the scratch pad was thin, Stage 2 may have produced more generic output.

- [ ] **No instructions ignored** — were there any moments where the agent clearly bypassed an instruction (e.g. read PROCESS.md when it shouldn't have, or opened a JSONL file despite the warning)?

---

## What to Report Back

After working through the checklist, produce a short summary in this format:

```
PASS:   [list items that worked correctly]
FAIL:   [list items that failed, with brief description of what happened instead]
PARTIAL: [list items that partially worked, with what was missing]

CONTEXT WINDOW: [Better / Same / Worse compared to first run, and any observations]
REPORT QUALITY: [Better / Same / Worse, and any observations]

RECOMMENDED NEXT STEPS:
1. [Most important fix or follow-up]
2. [Second priority]
3. [etc.]
```

---

## Known Remaining Optimisation (for reference)

One item was deferred to the roadmap — if the test still shows context pressure, this is the next lever:

**Embed sampled messages in `temp/analysis_stats.json`**
Update `analyse_sessions.py` to pull the actual `user_messages` for the recommended sample sessions from `session_data.json` and embed them directly in `analysis_stats.json`. The agent would then load one file instead of loading `analysis_stats.json` plus separately reading `session_data.json` for each sampled session. Most useful when the session sample grows beyond 10–12 sessions.
