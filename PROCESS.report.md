# AI Prompting Pattern Review — Stage 2: Report Generation

**When to load this file:** After Stage 1 is complete and `temp/scoring_scratch.json` has been written. This file covers generating all three output files and updating the history record. No session content is needed — everything required is in `temp/scoring_scratch.json`.

---

## Starting Stage 2

Read `temp/scoring_scratch.json`. This file contains all scores, evidence quotes, strengths, weaknesses, standout prompts, and recommendations produced in Stage 1. Use it as the sole source of truth for all report content.

If this is a history-aware run (`build_on_history: true` in the scratch pad), also read `reports/[Developer-Name]/history.json` to populate trend indicators and delta comparisons.

---

## Step 6 — Write the Full Analysis Report

Use `templates/analysis-report-template.md` as the starting point. Save the new report to `reports/[Developer-Name]/[YYYY-MM]/[Name]-Prompting-Analysis.md`.

The report should contain:

1. **Executive Summary** — 2–3 sentences characterizing the developer's overall prompting maturity
2. **Session Inventory** — table of *key and notable sessions only* (not every session). Include sessions directly referenced in findings, representing a clear strength or weakness, or the best/worst examples. Use `sessions_reviewed` and `session_refs` from the scratch pad to identify these. For large sample sizes (20+ sessions), aim for 8–12 highlighted sessions.
3. **What You're Doing Well** — 5–8 strengths with specific examples and explanation of why each matters. Use the `strengths` array and `evidence` quotes from the scratch pad.
4. **What Could Be Better** — 5–7 weaknesses with concrete recommendations for each. Use the `weaknesses` array from the scratch pad.
5. **Patterns by Session Type** — breakout by the types of work they use AI for (architecture, debugging, implementation, etc.). Use `session_type_patterns` from the scratch pad.
6. **Top 5 Recommendations** — use `top_recommendations` from the scratch pad, prioritized and specific.
7. **Standout Prompts** — 3–5 specific prompts worth repeating as templates. Use `standout_prompts` from the scratch pad (verbatim text).

If `build_on_history` is true, include a **Progress Since Last Review** section with a category delta table using the `history_deltas` values.

---

## Step 7 — Produce the Scorecard HTML

Use `templates/scorecard-mockup.html` as the master template.

**How to generate:**

1. Copy `templates/scorecard-mockup.html` to `reports/[Developer-Name]/[YYYY-MM]/[Name]-Scorecard.html`
2. Remove the mock callout banner (the `<div class="mock-banner">` block at the top)
3. Update the header section:
   - Developer name (`<h1>`)
   - Project tags (one `<span class="tag">` per project in `projects_reviewed`)
   - Analysis date, session count (`total_sessions`), user turn count (`total_user_turns`)
   - Link to the full analysis report
4. Update the Maturity Level section:
   - Set the level number (`maturity_level`) and level name (`maturity_name`)
   - Fill the maturity pips: filled = `●`, empty = `○` (e.g., Level 3 = `●●●○○`)
5. Update the Category Scores table using `category_scores` from the scratch pad:
   - Set the score (X/5) for each of the 9 categories
   - Set rating dots: filled `●` for earned points, empty `○` for remaining
   - Color coding: blue (`dot-blue`) for 4–5, orange (`dot-orange`) for 3, red (`dot-red`) for 1–2
   - If `build_on_history` is true: add delta indicator (`↑`, `↓`, or `→`) using `.delta-up`, `.delta-down`, `.delta-flat` CSS classes
6. Update the Overall score (`total_score`) and progress bar percentage (`(total_score/45)*100`)
7. **Trend section** (only when `build_on_history` is true): populate Trend vs Last Report — list categories that moved, overall delta, sample-size caveats. Remove this section entirely if starting fresh.
8. Update Quick Take: 3 strengths and 3 watch outs (one sentence each) from `strengths` and `weaknesses`
9. Update Top 3 Recommendations from `top_recommendations` (first three entries)
10. The Reference Guide section at the bottom is **static** — do not change it

**Category IDs for the click-to-expand links:**
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

## Step 8 — Produce the Scorecard MD

Use `templates/scorecard-template.md` as the master template.

**How to generate:**

1. Copy `templates/scorecard-template.md` to `reports/[Developer-Name]/[YYYY-MM]/scorecard-template.md`
2. Update the header: developer name, projects reviewed, analysis date, session stats, link to full report
3. Set the Maturity Level: number and name. Bold the correct level name in the maturity level row.
4. Fill in the Category Scores table: score (X/5) and rating dots for each of the 9 categories using `category_scores` from the scratch pad
5. Update Overall score total (`total_score` / 45)
6. Fill in Quick Take: 3 strengths, 3 watch outs from `strengths` and `weaknesses`
7. Fill in Top 3 Recommendations from `top_recommendations` (first three entries)
8. The Reference Guide section at the bottom is **static** — leave it unchanged

---

## Step 9 — Calibrate Tone

All outputs are coaching tools, not performance reviews. Keep the tone:

- Specific and evidence-based (quote from actual sessions via scratch pad)
- Constructive on weaknesses (explain the failure mode, not just the gap)
- Respectful of the developer's existing habits (don't dismiss what's working)
- Practical (every recommendation should be actionable next session)

---

## Step 10 — Update the History File

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
      "sample_note": "Use the sample_note value from scoring_scratch.json — written by Stage 1 which had full visibility of the dataset."
    }
  ]
}
```

**Notes on the history file:**
- If the file already exists, preserve existing entries and append the new one — never overwrite the array
- `history.json` lives at `reports/[Developer-Name]/history.json`, one level above the monthly subfolders
- It is gitignored along with all other content under `reports/` — local record only
- The `sample_note` field is important: future runs use it to distinguish genuine score changes from sample-size variation

---

## Step 11 — Clean Up the Temp Folder

After `history.json` is updated, delete the `temp/` folder and all its contents. The report files are safely saved in `reports/[Developer-Name]/[YYYY-MM]/` and the temp artifacts are no longer needed.

```
# macOS / Linux
rm -rf temp/

# Windows
rmdir /s /q temp
```

Tell the user: *"All done — reports saved to `reports/[Developer-Name]/[YYYY-MM]/`. Temp files have been cleaned up."*
