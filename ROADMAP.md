# AI Prompting Review — Roadmap

Future improvements identified during development. Items are loosely prioritised.

---

## In Progress / Next Up

Nothing currently in progress.

---

## Planned

### Context Optimisation — Remaining Ideas

The core optimisations (session_data.json mandate, PROCESS.md split, scoring scratch pad, subagent split) are now implemented. The following remain for future consideration as session history grows.

**Embed sampled messages in `analysis_stats.json`**
Update `analyse_sessions.py` to pull the actual user messages for the recommended sample sessions directly from `session_data.json` and embed them in `analysis_stats.json`. The agent would then load one pre-assembled file instead of opening `analysis_stats.json` plus each sampled session separately. Most useful when the sample grows beyond 8–10 sessions or if single-file loading becomes a constraint.

**Session count warnings and recommended batch sizes**
As session history grows, large sample sizes will create context pressure even with the current optimisations. Planned: add a warning to `analyse_sessions.py` output when the recommended sample exceeds a safe threshold (e.g. 15 sessions / ~150 user turns), suggesting the user split the review into smaller passes. Since the history tracking system already supports building on past reports, the natural workflow would be: run a focused review on a subset (e.g. last 30 days), build on it next month with another focused pass. This avoids the need for a single monster session while still producing a complete picture over time. The warning should be advisory, not a hard limit — let the user decide.

---

### Other Chat Source Workflows
Currently "other chats" lands in `ingestion/other-chats/` with no extraction script.
Planned: add guided workflow and extraction support for:
- ChatGPT JSON exports
- GitHub Copilot logs
- Windsurf / other AI IDEs (TBD format)

Each source needs its own extraction script feeding into the same `session_data.json`
format so `analyse_sessions.py` and the scoring rubric are unchanged.

### Tool-Specific Starter Prompts
`STARTER_PROMPT.md` is currently generic. Planned: tool-specific versions for
OpenClaw, Windsurf, and other agents that don't auto-load a rules file.

### "Other Chats" Guided Workflow in Cursor
When the user picks "other chats" in the Cursor session, walk them through
locating and exporting their chat history from whichever tool they used.
Currently just directs to the drop zone with no further guidance.

### Team Review Mode
Currently the ingestion folder is a single-person drop zone — one developer at a time.
Planned: batch mode to run reviews for multiple developers in sequence and produce
a team-level summary alongside individual reports.

---

## Completed

| Date | Item |
|---|---|
| March 2026 v1 | Initial process, rubric, folder structure, scorecard HTML + MD |
| March 2026 v2 | Python extraction scripts, tiered sampling, subagent guidance |
| March 2026 v3 | `.cursor` folder discovery UX, overwrite/version guard in Step 0 |
| March 2026 v4 | History tracking system, trend indicators, persistent pattern detection |
| March 2026 v5 | Cursor-native rule, `--source` parameter for direct `.cursor` reading |
| March 2026 v6 | Context optimisation: `session_data.json` mandate — PROCESS.md and cursor rule updated to read extracted user messages instead of raw JSONL files |
| March 2026 v7 | Split PROCESS.md into three phase-scoped files. Added `scoring_scratch.json` as the Stage 1→2 handoff artifact. Each phase loads only the instructions it needs. Tool-agnostic: subagent used for Stage 2 when supported, otherwise same context with scratch pad as safety net. |
| March 2026 v8 | Moved all intermediate files into `temp/` folder. Scripts auto-create it. Gitignored and deleted at end of process (Step 11). Step 0 detects stale temp folder and offers resume or fresh start. |
| March 2026 v9 | Added `cross_session_patterns` field to scratch pad schema in PROCESS.review.md. Written before per-category scoring to capture habits and patterns that only become visible across multiple sessions. Addresses gap identified in first end-to-end diagnostic. |
| March 2026 v9 | Moved all "In Progress" items (Cursor-native rule, `--source` parameter, PROCESS.md Claude-specific cleanup) to Completed — all shipped as part of v5–v8. |
