---
name: codex-consensus
description: Use before doing anything hard to reverse, production-touching, or design-fixing (deploys, upgrades, migrations, schema/config changes, merges into live branches, specs and plans that lock a design) — even when it feels "safe enough to skip review" or the user is waiting. Claude drafts, Codex cross-reviews by severity, they converge on evidence, and a human approves before execution.
---

# Claude ↔ Codex Consensus Protocol

Direction: **Claude leads → Codex reviews**. For Codex-led work, install the sibling `claude-consensus` skill; do not recursively invoke both skills.

## Core idea

Claude (lead) produces an artifact. Codex (cross-reviewer) critiques **the same artifact** by severity. They negotiate on evidence until the disagreement is zero.
Claude executes only with **consensus AND human approval**. The human is the tiebreaker on judgment calls and the approver of execution.

**Breaking the letter of this protocol breaks its purpose.**

## When it applies

**Applies** if any of these is true: hard to reverse · touches production/live systems · locks a design. **Applicability beats exclusion.**
**Excluded** (only when none of the applicability conditions hold): typos/comments, read-only investigation, pre-verification.

**Pre-verification** means fact-gathering on existing targets only: attempting a merge, building, or running tests in an isolated worktree/branch to list conflicts and failures. Conditions: no production credentials, no external writes (push, deploy, messages, production DB), no contact with live processes or paths.
Conflict resolution, new implementation and config changes are **not** pre-verification — they are PLAN/CODE artifacts and go through the loop.

## Artifact stages

DIRECTION → SPEC → PLAN → CODE (diff). Only the stages that apply; each stage must reach consensus before the next.
Record an artifact **version** every round (commit hash or `shasum -a 256`). Consensus and approval are bound to that version and execution scope. If the artifact changes afterwards, re-review from the affected stage.

If the reviewed copy is masked, record **both** hashes (original and masked copy) plus the masking transformation (what was replaced, how). Before asking for approval, verify locally that the masked copy equals the original apart from that recorded transformation. Approval binds to the **original** hash; if either hash changes, approval is void.

## Round loop

1. Claude writes/revises → saves the artifact file, records the version.
2. Codex reviews → every finding gets a **stable ID (F-01…)**, a severity (high = blocker / medium / low), and an evidence grade (primary-source doc / static check / inference-unverified). Severity and evidence grade are independent.
3. Claude answers each ID: **accept (fix)** or **rebut with evidence**. Blind acceptance is capitulation, not consensus.
4. Re-review with prior findings and responses attached → repeat.

**Consensus =** zero factual/code differences · zero Codex "high" · zero unresolved Claude rebuttals. Remaining medium/low items are recorded explicitly as **agreed open items** — never silently dropped.

**Facts are closed by execution, not agreement** — measurement, tests, builds, real data. Two LLMs agreeing is not verification. Fix acceptance criteria and thresholds **before** looking at data, and run them immediately against data already in hand (local or isolated copies) to catch self-contradiction. Checks that need gated access (production data, live systems, external writes) are not run here: record them as **pending verification** and run them only after approval, within the approved scope. A pending check is a **gate**: the dependent action runs only if the check passes. A failed or inconclusive result halts that action and returns to review or human escalation. Never proceed on the approved plan alone.

## Escalate to the human immediately

- **A** A judgment difference (values, investment, design choice) that evidence doesn't narrow — never paper over it with false consensus.
- **B** The same point isn't narrowed within 3 rounds. Renaming, splitting or merging IDs does **not** reset the count.
- **C** What counts as a fact is itself disputed.
- **D** Severity itself is disputed — escalate at once, no round spent.
- **E** An artifact reaches 5 total rounds without consensus (prevents endless new-finding loops).

## Data egress (your own security rules take precedence)

Send: schemas, code, diffs, metrics, plans. **Do not send:** secrets/tokens/real config values, customer/CRM/financial data, personal memory files or raw real names.
- Copy only the needed files into the review directory and mask sensitive values; **read the entire copy yourself before the call** (running a masking command ≠ de-identification).
- Log what was masked. Don't close judgments that depend on masked information by consensus — verify locally or escalate.
- **Limitation:** `-s read-only` only blocks writes; it does not restrict what Codex can read. Controls are an explicit read scope in the prompt plus post-hoc audit. If the audit shows access outside the directory, void the round and report it. Skipping the audit breaks the risk acceptance.
- **Audit evidence:** a round is accepted only with a recorded audit: the list of commands/file reads taken from `raw-N.A.log`, each checked to be inside the review directory. If the log is missing, truncated, or does not show tool activity well enough to judge, the round is **unverified**: do not adopt it; retry (new attempt) or escalate to the human.

## How to call Codex

**Default: `codex exec` (non-interactive).** Use `scripts/run-codex-review.sh`, or the equivalent:

```bash
R="$(mktemp -d "${TMPDIR:-/tmp}/codex-review.XXXXXX")" || exit 1   # must be OUTSIDE any git repo
# copy artifact + target files → mask → read everything → write "$R/prompt-1.md"
N=1; A=1   # N = round, A = attempt within the round (increment on retry; never overwrite)
perl -e 'alarm 900; exec @ARGV' codex exec -c project_doc_max_bytes=0 -s read-only \
  --skip-git-repo-check --ephemeral -C "$R" -o "$R/round-$N.$A.md" - \
  < "$R/prompt-$N.md" > "$R/raw-$N.$A.log" 2>&1
echo "exit=$?" | tee "$R/exit-$N.$A"
```

Pin a model with `-m <slug>` if you want reproducibility (the helper script reads `CODEX_MODEL`); check the `model:` header in `raw-N.A.log` and record it per round. Flags were verified against `codex exec --help` (codex-cli 0.155–0.162); re-check if your version differs.

**Instruction-file leak guard:** if the review directory is inside a git repo, Codex auto-loads that repo root's `AGENTS.md` as instructions, transmits it, and follows it (e.g. "read my memory files"). Observed in practice. Apply **both**: a directory outside any repo **and** `-c project_doc_max_bytes=0`.

**Accepting a result:** exit code 0, a `round-N.A.md` freshly created by *this* attempt, the requested format satisfied, and a passing scope audit (see Data egress). If any fails, log it as a failure, bump A and retry, or tell the user. Keep every attempt's result, raw log and exit code (audit trail).

**Required prompt contents:** read-scope restriction to the review directory, artifact path and version, review angle, prior findings and responses, output format (`F-NN | severity | evidence grade | finding | suggestion`), no rubber-stamping and no invented blockers, last line `Verdict: consensus|no-consensus`. See `examples/review-prompt.md`.

**Alternative:** any orchestration layer that can run a Codex worker works, provided the same rules hold (same artifact, stable IDs, version binding, logging). If a Codex worker fails readiness checks, inspect the actual wait reason before assuming a cause; update the CLI only after the user confirms.

## Record keeping

Keep a `consensus-log.md` (project `docs/` or the work output directory):
- per round: number, artifact version, per-ID finding / response / status, verdict, masked items;
- open items and human decisions.

When reporting to the user, present consensus status together with open items and **request execution approval for that specific version**.

## Red flags — stop and run the loop

| Rationalization | Reality |
|---|---|
| "It's small, no review needed" | If an applicability condition holds, size is irrelevant |
| "I did it on a branch, so it's pre-verification" | Conflict resolution, implementation, config changes are artifacts |
| "The user seems in a hurry" | Executing without approval causes bigger delays |
| "Codex is wrong, ignore it" | Rebut with evidence and log it. Ignoring ≠ rebutting |
| "Accepting everything Codex says is faster" | Blind acceptance = false consensus |
| "Consensus reached, run it" | Consensus ≠ approval. Human approval required |
| "Tweaked it a bit after approval, same thing" | Version changed → re-review |
| "Result is in; a slight criteria change would pass" | No post-hoc criteria changes → escalate |
| "Codex call failed, skip it" | Tell the user and get a decision |
