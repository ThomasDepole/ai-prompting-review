"""
analyse_sessions.py
-------------------
Step 2 of the AI Prompting Pattern Review process.

Reads session_data.json (produced by extract_sessions.py) and computes
quantitative signals across all sessions. Also classifies sessions by size
and recommends a balanced sample for the AI analysis step to focus on.

Usage (run from the project root):
    python scripts/analyse_sessions.py

Output:
    analysis_stats.json  — per-session stats, aggregate totals, and sample recommendation

The recommended sample (up to 6 large / 6 medium / 6 small sessions) is what
the reviewer should feed to the AI analysis step. If the sample doesn't produce
a clear enough picture, add 3 more from each tier until patterns are clear.
"""

import json
import os
import re
import sys
from collections import defaultdict

# ── Config ────────────────────────────────────────────────────────────────────

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INPUT_FILE = os.path.join(BASE_DIR, "session_data.json")
OUTPUT_FILE = os.path.join(BASE_DIR, "analysis_stats.json")

# Session size thresholds (by user turns)
SMALL_MAX = 3     # 1–3 turns
MEDIUM_MAX = 8    # 4–8 turns
# Large = 9+ turns

SAMPLE_PER_TIER = 6   # target per size tier

# ── Signal detection patterns ─────────────────────────────────────────────────

# Positive signals
AT_REF          = re.compile(r'@\S')                          # @ file reference
CURSOR_CMD      = re.compile(r'<cursor_commands', re.I)       # preloaded context command
ATTACHED_FILES  = re.compile(r'<attached_files', re.I)        # code attachment
IMAGE_FILES     = re.compile(r'<image_files', re.I)           # screenshot attachment
PLAN_REF        = re.compile(r'\.plan\.md|\.plan\b', re.I)    # plan file reference
MDC_REF         = re.compile(r'\.mdc\b', re.I)               # cursor rules file
VERIFICATION    = re.compile(                                  # success criteria / verify
    r"i'?ll know|success criteria|i will know|verify|verification|"
    r"how (should|would|do) (we|you|i) test|what test",
    re.I
)
CONSTRAINT_GUARD = re.compile(                                 # scope constraint
    r"don'?t change|do not change|leave .{1,30} (as|alone|unchanged)|"
    r"keep .{1,30} (as|intact|the same)|without (changing|modifying|touching)",
    re.I
)
DEBUG_STRUCTURE = re.compile(                                  # structured debug info
    r"\bexpected\b.{0,80}\bactual\b|\bactual\b.{0,80}\bexpected\b|"
    r"\btrigger\b|\bsteps to reproduce\b|reproduce the (bug|issue|error)|"
    r"\bstack trace\b|\bhere'?s the (log|error|trace|output)\b",
    re.I
)

# Watch-out signals
PASSIVE_OPENER  = re.compile(r'^(can you|could you|would you|is it possible)', re.I)
TYPO_CHARS      = re.compile(r'\b\w{3,}\w{2,}\b')            # crude; refined below

# Imperative openers (strong action verbs at start of message)
IMPERATIVE_VERBS = re.compile(
    r'^(create|update|fix|refactor|add|remove|delete|write|build|implement|'
    r'generate|replace|rename|move|extract|modify|convert|make|run|test|'
    r'check|review|read|look|find|show|display|ensure|set|use|deploy|'
    r'migrate|clean|format|merge|split|we need|let\'?s|now|next)',
    re.I
)


# ── Per-message analysis ──────────────────────────────────────────────────────

def analyse_message(text):
    """Return a dict of signal flags for a single user message."""
    return {
        "has_at_ref":          bool(AT_REF.search(text)),
        "has_cursor_cmd":      bool(CURSOR_CMD.search(text)),
        "has_attached_files":  bool(ATTACHED_FILES.search(text)),
        "has_image_files":     bool(IMAGE_FILES.search(text)),
        "has_plan_ref":        bool(PLAN_REF.search(text)),
        "has_mdc_ref":         bool(MDC_REF.search(text)),
        "has_verification":    bool(VERIFICATION.search(text)),
        "has_constraint_guard":bool(CONSTRAINT_GUARD.search(text)),
        "has_debug_structure": bool(DEBUG_STRUCTURE.search(text)),
        "has_passive_opener":  bool(PASSIVE_OPENER.match(text.strip())),
        "has_imperative_opener": bool(IMPERATIVE_VERBS.match(text.strip())),
    }


def classify_size(user_turns):
    if user_turns <= SMALL_MAX:
        return "small"
    elif user_turns <= MEDIUM_MAX:
        return "medium"
    else:
        return "large"


# ── Session analysis ──────────────────────────────────────────────────────────

def analyse_session(session):
    msgs = session.get("user_messages", [])
    per_msg = [analyse_message(m) for m in msgs]

    # Aggregate across messages
    totals = defaultdict(int)
    for m in per_msg:
        for k, v in m.items():
            if v:
                totals[k] += 1

    n = len(msgs) or 1  # avoid div/0

    # Detect command names used (extract from <cursor_commands> blocks)
    cmd_names = []
    for msg in msgs:
        for match in re.finditer(r'<cursor_commands[^>]*>(.*?)</cursor_commands>', msg, re.S | re.I):
            inner = match.group(1).strip()
            # Command names often appear as first word/line
            first_line = inner.split('\n')[0].strip()
            if first_line:
                cmd_names.append(first_line[:80])

    return {
        "project":            session["project"],
        "id":                 session["id"],
        "size":               classify_size(session["user_turns"]),
        "user_turns":         session["user_turns"],
        "assistant_turns":    session["assistant_turns"],
        "has_subagents":      session["has_subagents"],
        "subagent_count":     session["subagent_count"],
        # Counts
        "at_ref_count":       totals["has_at_ref"],
        "at_ref_pct":         round(totals["has_at_ref"] / n * 100),
        "cursor_cmd_count":   totals["has_cursor_cmd"],
        "cursor_cmd_names":   cmd_names,
        "attached_files_count": totals["has_attached_files"],
        "image_files_count":  totals["has_image_files"],
        "plan_ref_count":     totals["has_plan_ref"],
        "mdc_ref_count":      totals["has_mdc_ref"],
        "verification_count": totals["has_verification"],
        "constraint_guard_count": totals["has_constraint_guard"],
        "debug_structure_count": totals["has_debug_structure"],
        "passive_opener_count": totals["has_passive_opener"],
        "imperative_opener_count": totals["has_imperative_opener"],
    }


# ── Sampling ──────────────────────────────────────────────────────────────────

def build_sample(session_stats, n_per_tier=SAMPLE_PER_TIER):
    """
    Return up to n_per_tier sessions from each size tier.
    Within each tier, prioritise sessions with the most signals (richer data).
    """
    tiers = {"large": [], "medium": [], "small": []}
    for s in session_stats:
        tiers[s["size"]].append(s)

    sample = []
    for tier_name in ("large", "medium", "small"):
        tier = tiers[tier_name]
        # Score each session by number of distinct signal types present
        def richness(s):
            return (
                (1 if s["at_ref_count"] > 0 else 0) +
                (1 if s["cursor_cmd_count"] > 0 else 0) +
                (1 if s["attached_files_count"] > 0 else 0) +
                (1 if s["plan_ref_count"] > 0 else 0) +
                (1 if s["verification_count"] > 0 else 0) +
                (1 if s["debug_structure_count"] > 0 else 0) +
                (1 if s["has_subagents"] else 0) +
                s["user_turns"]  # longer sessions have more signal
            )
        ranked = sorted(tier, key=richness, reverse=True)
        picked = ranked[:n_per_tier]
        for s in picked:
            sample.append({
                "tier": tier_name,
                "project": s["project"],
                "id": s["id"],
                "user_turns": s["user_turns"],
                "why": _why_picked(s),
            })

    return sample


def _why_picked(s):
    reasons = []
    if s["user_turns"] >= 9:
        reasons.append(f"{s['user_turns']}-turn session")
    if s["cursor_cmd_count"] > 0:
        reasons.append("uses cursor commands")
    if s["attached_files_count"] > 0:
        reasons.append("has code attachments")
    if s["plan_ref_count"] > 0:
        reasons.append("references plan file")
    if s["has_subagents"]:
        reasons.append(f"spawned {s['subagent_count']} subagent(s)")
    if s["debug_structure_count"] > 0:
        reasons.append("contains debugging content")
    if s["verification_count"] > 0:
        reasons.append("has verification language")
    return ", ".join(reasons) if reasons else "selected for tier diversity"


# ── Aggregate stats ───────────────────────────────────────────────────────────

def compute_aggregate(session_stats):
    n = len(session_stats)
    total_user_turns = sum(s["user_turns"] for s in session_stats)
    if n == 0 or total_user_turns == 0:
        return {}

    def pct(field):
        count = sum(s[field] for s in session_stats)
        return {"count": count, "pct_of_user_turns": round(count / total_user_turns * 100)}

    sessions_with_subagents = sum(1 for s in session_stats if s["has_subagents"])
    all_cmd_names = []
    for s in session_stats:
        all_cmd_names.extend(s["cursor_cmd_names"])

    return {
        "total_sessions": n,
        "total_user_turns": total_user_turns,
        "total_assistant_turns": sum(s["assistant_turns"] for s in session_stats),
        "sessions_with_subagents": sessions_with_subagents,
        "subagents_pct_of_sessions": round(sessions_with_subagents / n * 100),
        "size_distribution": {
            "large":  sum(1 for s in session_stats if s["size"] == "large"),
            "medium": sum(1 for s in session_stats if s["size"] == "medium"),
            "small":  sum(1 for s in session_stats if s["size"] == "small"),
        },
        "at_refs":          pct("at_ref_count"),
        "cursor_commands":  pct("cursor_cmd_count"),
        "attached_files":   pct("attached_files_count"),
        "image_files":      pct("image_files_count"),
        "plan_refs":        pct("plan_ref_count"),
        "mdc_refs":         pct("mdc_ref_count"),
        "verification":     pct("verification_count"),
        "constraint_guards":pct("constraint_guard_count"),
        "debug_structure":  pct("debug_structure_count"),
        "passive_openers":  pct("passive_opener_count"),
        "imperative_openers": pct("imperative_opener_count"),
        "cursor_command_names_used": sorted(set(all_cmd_names)),
    }


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    if not os.path.exists(INPUT_FILE):
        print(f"ERROR: session_data.json not found at {INPUT_FILE}")
        print("Run extract_sessions.py first.")
        sys.exit(1)

    with open(INPUT_FILE, encoding="utf-8") as f:
        sessions = json.load(f)

    print(f"Analysing {len(sessions)} sessions...")

    session_stats = [analyse_session(s) for s in sessions]
    aggregate = compute_aggregate(session_stats)
    sample = build_sample(session_stats)

    output = {
        "aggregate": aggregate,
        "recommended_sample": sample,
        "sessions": session_stats,
    }

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    # ── Print summary ──────────────────────────────────────────────────────────
    ag = aggregate
    print(f"\n{'─' * 60}")
    print(f"AGGREGATE STATS  ({ag['total_sessions']} sessions · {ag['total_user_turns']} user turns)")
    print(f"{'─' * 60}")
    print(f"  @ file references       : {ag['at_refs']['count']} msgs  ({ag['at_refs']['pct_of_user_turns']}%)")
    print(f"  Cursor commands used    : {ag['cursor_commands']['count']} msgs  ({ag['cursor_commands']['pct_of_user_turns']}%)")
    if ag['cursor_command_names_used']:
        print(f"    Commands detected     : {', '.join(ag['cursor_command_names_used'])}")
    print(f"  Code attachments        : {ag['attached_files']['count']} msgs  ({ag['attached_files']['pct_of_user_turns']}%)")
    print(f"  Image/screenshot refs   : {ag['image_files']['count']} msgs  ({ag['image_files']['pct_of_user_turns']}%)")
    print(f"  Plan file references    : {ag['plan_refs']['count']} msgs  ({ag['plan_refs']['pct_of_user_turns']}%)")
    print(f"  .mdc rule references    : {ag['mdc_refs']['count']} msgs  ({ag['mdc_refs']['pct_of_user_turns']}%)")
    print(f"  Verification language   : {ag['verification']['count']} msgs  ({ag['verification']['pct_of_user_turns']}%)")
    print(f"  Constraint guards       : {ag['constraint_guards']['count']} msgs  ({ag['constraint_guards']['pct_of_user_turns']}%)")
    print(f"  Debug structure signals : {ag['debug_structure']['count']} msgs  ({ag['debug_structure']['pct_of_user_turns']}%)")
    print(f"  Imperative openers      : {ag['imperative_openers']['count']} msgs  ({ag['imperative_openers']['pct_of_user_turns']}%)")
    print(f"  Passive openers         : {ag['passive_openers']['count']} msgs  ({ag['passive_openers']['pct_of_user_turns']}%)")
    print(f"  Sessions with subagents : {ag['sessions_with_subagents']}  ({ag['subagents_pct_of_sessions']}% of sessions — positive signal)")
    print(f"  Size distribution       : large={ag['size_distribution']['large']}  medium={ag['size_distribution']['medium']}  small={ag['size_distribution']['small']}")

    print(f"\n{'─' * 60}")
    print(f"RECOMMENDED SAMPLE  (up to {SAMPLE_PER_TIER} per tier)")
    print(f"{'─' * 60}")
    for s in sample:
        print(f"  [{s['tier']:6}] {s['id'][:8]}... | {s['project']} | {s['user_turns']} user turns | {s['why']}")

    print(f"\nOutput written to: {OUTPUT_FILE}")
    print("\nNext step: load analysis_stats.json and the recommended sample sessions")
    print("into your AI analysis prompt (see PROCESS.md Step 3).")


if __name__ == "__main__":
    main()
