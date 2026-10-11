# Review prompt template (prompt-N.md)

You are the cross-reviewer in a Claude ↔ Codex consensus loop.

**Read scope:** read ONLY files inside this directory. Do not read anything outside it.

**Artifact:** `plan.md` (stage: PLAN) — version `sha256:<first 12 hex>`
**Review angle:** correctness, reversibility, blast radius, missing rollback, unverified assumptions.

**Previous round (omit in round 1):**
| ID | Your finding | Claude's response (accepted / rebutted + evidence) |
|---|---|---|
| F-01 | ... | ... |

**Rules**
- One finding per line, exactly: `F-NN | high/medium/low | primary-source/static-check/inference | finding | suggestion`
- Reuse existing IDs for the same point; new points get new IDs.
- "high" = blocker only. Do not invent blockers. Do not rubber-stamp.
- Severity and evidence grade are independent; state both.
- Last line must be `Verdict: consensus` or `Verdict: no-consensus`.
