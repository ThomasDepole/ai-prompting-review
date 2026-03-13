# AI Prompting Score Card — [Developer Name]

**Projects Reviewed:** [Project A] · [Project B] · [Project C]
**Analysis Date:** [Month Year]
**Sessions:** [N] sessions · [N] user turns
**Full Report:** [Developer-Name]-Prompting-Analysis.md

---

## Maturity Level: [N] — [Level Name]

> Level 1 Conversational · Level 2 Task-Oriented · **Level 3 Context-Aware** · Level 4 Systematic · Level 5 Expert

---

## Category Scores

*When building on history, fill in the Previous and Δ columns. Remove both columns if this is the first report or the user chose to start fresh.*

| Category | Previous | Current | Δ | Rating | Definition |
|---|---|---|---|---|---|
| Context Engineering | X/5 | X/5 | ↑/↓/→ | ○○○○○ | Use of @ refs, docs, examples, reference projects, and role-setting to give AI accurate context |
| Instruction Quality | X/5 | X/5 | ↑/↓/→ | ○○○○○ | Clarity, action verbs ("make X" vs "can you suggest"), specificity, and avoidance of ambiguity |
| Example-Based Guidance | X/5 | X/5 | ↑/↓/→ | ○○○○○ | Shows AI what's wanted via mocks, reference implementations, or sample output (few-shot technique) |
| Scope Definition | X/5 | X/5 | ↑/↓/→ | ○○○○○ | In/out-of-scope boundaries, constraint guards ("don't change X"), and edge case handling |
| Debugging Discipline | X/5 | X/5 | ↑/↓/→ | ○○○○○ | Structured bug reports: triggering action → expected → actual → logs |
| Session Management | X/5 | X/5 | ↑/↓/→ | ○○○○○ | Context window awareness, fresh-start discipline, cross-session continuity and handoffs |
| Reusability Investment | X/5 | X/5 | ↑/↓/→ | ○○○○○ | Cursor rules, context commands, and prompt templates built to reduce repetitive setup work |
| Verification Habits | X/5 | X/5 | ↑/↓/→ | ○○○○○ | Upfront success criteria — "I'll verify by seeing X" — and explicit verification requests |
| Plan-Before-Build | X/5 | X/5 | ↑/↓/→ | ○○○○○ | Scoping and proposing before implementation; plan files for complex multi-step work |

**Overall: XX / 45** *(Previous: XX / 45 · Δ ↑/↓/→ N)*

*Sample note (if applicable): [Flag any categories where a score change may reflect thin sample rather than genuine shift. Remove if no caveats apply.]*

---

## Quick Take

**Strengths**
- [Strength 1 — one sentence, specific]
- [Strength 2 — one sentence, specific]
- [Strength 3 — one sentence, specific]

**Watch Outs**
- [Watch out 1 — one sentence, specific]
- [Watch out 2 — one sentence, specific]
- [Watch out 3 — one sentence, specific]

---

## Top Recommendations

1. **[Recommendation title].** [One to two sentences explaining the change and expected impact.]
2. **[Recommendation title].** [One to two sentences explaining the change and expected impact.]
3. **[Recommendation title].** [One to two sentences explaining the change and expected impact.]

---

*Process guide → CONTEXT.md*

---

## Reference Guide
*Static content — identical across all score cards.*

### Maturity Levels

| Level | Name | Description |
|---|---|---|
| 1 | Conversational | Treats AI like a chat interface. No file references, relies on AI to infer all context. High back-and-forth, frequent corrections. |
| 2 | Task-Oriented | Gives the AI clear tasks but doesn't pre-load context. Uses some file references but inconsistently. Debugging is trial-and-error. |
| 3 | Context-Aware | Consistently uses file references and docs. Has discovered some reusable patterns. Good architectural collaboration but ad-hoc session management. |
| 4 | Systematic | Has a library of context commands. Every session opens with context-setting. Debugging follows a structured format. Plans and executes in separate sessions by default. |
| 5 | Expert | Designs prompts as reusable templates. Uses AI for verification as well as generation. Creates and maintains team-wide prompt libraries. Actively coaches others. |

---

### Category Definitions

**Context Engineering**
What it measures: How well the developer gives the AI accurate, complete context before asking it to act — using file references, documentation, role-setting, and reference projects.
Low (1–2): Describes what they want in prose, no file references. AI has to guess at project structure, existing patterns, and conventions.
High (4–5): Uses `@` references consistently, injects architecture docs, points to wiki pages. AI rarely needs to ask clarifying questions about the codebase.
To improve: Before every session, ask "Does the AI know where to look?" Add `@` references to the key files, the relevant docs, and any existing patterns to follow.

---

**Instruction Quality**
What it measures: Clarity of the prompt itself — specific outcomes, action-oriented language, and avoidance of ambiguity. "Make X" outperforms "can you suggest X" in agentic coding contexts.
Low (1–2): Passive requests, vague goals, typos in class/file names, multiple concerns bundled without priority.
High (4–5): Action verbs ("create", "update", "fix"), single clear outcome per prompt, specific file paths and method names.
To improve: Re-read each prompt before sending. Replace "can you..." with the direct action. If a prompt has more than one goal, consider splitting it.

---

**Example-Based Guidance**
What it measures: Does the developer show the AI what they want via examples, mock implementations, or reference projects rather than only describing it in words? (Few-shot prompting.)
Low (1–2): Always describes desired output in prose. AI generates from scratch using its defaults, which may not match team patterns.
High (4–5): Regularly points to a working example or reference file. AI matches style, structure, and conventions immediately.
To improve: When asking for something new, find the closest existing example and reference it. "Build X like we did Y" is more reliable than describing X from scratch.

---

**Scope Definition**
What it measures: Does the developer define what is in-scope and out-of-scope? Do they add constraint guards to prevent AI from touching adjacent code?
Low (1–2): No boundaries stated. AI makes reasonable-but-unwanted changes to related files or builds more than was needed.
High (4–5): Explicit in/out-of-scope lists for complex tasks. Constraint guards like "don't change the public API of X" prevent scope creep.
To improve: Add one line to complex prompts: "Don't change [X]." For feature work, list what is explicitly out of scope.

---

**Debugging Discipline**
What it measures: Quality of information shared when something is broken. Effective format: triggering action → expected behavior → actual behavior → relevant logs.
Low (1–2): "It's not working" or a log paste with no context. AI needs multiple follow-ups before it can diagnose.
High (4–5): Every bug report includes what was done, what was expected, what happened, and the log. AI diagnoses in one turn.
To improve: Three short lines before the log is all that's needed — no paragraph walkthrough required. Template: "I [did X]. I expected [Y]. Instead: [Z]. Here's the log:" For build/compile errors, ask the AI to run the build directly so it sees the output first-hand. Reserve the three-line format for behavioral and environment errors where the AI can't observe the result itself.

---

**Session Management**
What it measures: Awareness of context window limits, ability to recognise when a fresh session is needed, and quality of cross-session handoffs.
Low (1–2): Sessions run until AI produces degraded output. No strategy for starting fresh or reorienting between sessions.
High (4–5): Proactively splits long tasks. Opens new sessions with a clear recap. Monitors context usage and resets before drift occurs.
To improve: After 3–4 failed turns on the same bug, summarise what's been ruled out and start fresh. Open each new session with a 2–3 sentence recap of prior work.

---

**Reusability Investment**
What it measures: Has the developer built reusable context commands, Cursor rules (.mdc), and prompt templates that reduce repeated setup work?
Low (1–2): Re-explains the same conventions in every session. No rules or commands exist.
High (4–5): Architecture docs are wrapped in reusable commands. Cursor rules enforce patterns automatically. A new session can be fully oriented in one command invocation.
To improve: Any time you paste the same context into a second session, that content belongs in a command. Wrap the highest-frequency pattern first.

---

**Verification Habits**
What it measures: Does the developer define what success looks like before the AI builds? Do prompts include a verification line, and does the developer ask the AI to self-check?
Low (1–2): No success criteria. Verification is entirely reactive — run the app, see what breaks, loop back.
High (4–5): Every implementation prompt ends with "I'll verify by [X]." AI is asked to confirm builds pass or check output against stated criteria.
To improve: Add one sentence to every implementation prompt: "I'll know this works when [specific observable outcome]."

---

**Plan-Before-Build**
What it measures: Does the developer scope and review a plan before the AI writes code? Are complex features broken into a plan file before execution?
Low (1–2): Jumps straight to implementation. When output isn't right, cost is a full rewrite rather than a plan correction.
High (4–5): Complex features get a plan reviewed before a single file is changed. Execution sessions reference the plan as a source of truth.
To improve: For any task touching more than two files, ask for a plan first: "Review X and propose the changes you'll make. Don't write any code yet." Approve the plan, then execute.
