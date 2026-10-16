---
name: claude-consensus
description: Codex-led cross-review with Claude for consensus before hard-to-reverse, production-touching, or design-locking work. Use for Codex-to-Claude consensus requests (including “concensus”). Codex drafts, Claude reviews, evidence resolves differences, and the human authorizes execution.
---

# Codex → Claude Consensus

The reverse entry point of Claude ↔ Codex Consensus. Codex leads and Claude independently reviews the same artifact. The existing `codex-consensus` skill remains the Claude-led entry point.

## Protocol

Applies to hard-to-reverse changes, production/live-system impact or decisions that lock a design. Applicability overrides the exclusions below.

1. Use the applicable stages: DIRECTION → SPEC → PLAN → CODE. Save the artifact; include diffs, necessary surrounding code, acceptance criteria fixed before observing results, and available test evidence. Read-only investigation, typos and comments do not need the loop unless an applicability condition above holds.
2. Prepare a UTF-8 review packet containing only necessary, sanitized material. Do not send secrets, real configuration values, personal memory, customer/financial data or raw identities. Read the entire packet before calling Claude. Do not ask the reviewer to discover files from the source project.
3. Record both original artifact and packet SHA-256 hashes, the masking transformation and their verified correspondence. Approval binds to the original artifact and execution scope. Changes to either require re-review from the affected stage.
4. Call the bundled helper below. Include review angles, previous findings and ID-by-ID responses in the packet. Each attempt gets a fresh directory with its packet hash, raw output and status.
5. Track stable finding IDs (`F-01` etc.), severity (high/blocker, medium, low), and evidence grade independently. Codex accepts and fixes or rebuts with evidence; then sends a revised packet for another review. Blind acceptance is not consensus.
6. Consensus requires no unresolved factual/code differences, no high findings and no unresolved Codex rebuttals. Record any agreed medium/low open items explicitly. Two models agreeing never substitutes for tests, builds or measurements.

Escalate judgment/fact disputes that evidence cannot resolve, disputed severity immediately, the same issue unresolved after 3 rounds, or an artifact not converged after 5 total rounds. Renaming findings does not reset these limits. Failed calls and malformed output are not consensus. Retry a failed call at most once per round, retaining both attempts.

## Calling Claude

```bash
python3 ~/.codex/skills/claude-consensus/scripts/review.py \
  --packet /tmp/review-packet.txt --output-dir /tmp/consensus-results
```

Use `--model` only for a requested model; otherwise use the current CLI default and record the actual `modelUsage`. Do not apply a Codex model slug to Claude or change global defaults.

Check local `claude --help` for supported flags. The helper uses safe mode, no built-in tools, no MCP, no skills and no saved session, passing the packet on stdin from a fresh working directory. It must not modify files, discover extra context, delegate or call another model recursively. Do not relax these restrictions to work around a failed call. Managed policy and normal authentication remain in force; `--bare` is not a replacement because it does not use existing OAuth authentication.

The reviewer emits `F-NN | severity | evidence grade | finding | suggestion` (Korean labels are accepted). With no findings it emits `지적 없음`. The final line is exactly `판정: 합의` or `판정: 미합의`. It must not claim it ran tests.

## Audit, verification and execution

Retain CLI version, invocation flags, `raw.json`, `stderr.log`, `status.json`, and the fresh review. Check successful exit, successful CLI result, expected verdict and tool-free invocation. The audit records invocation flags plus available turn-count/permission-denial metadata; JSON result output is not a complete tool trace. Missing turn count is unknown, not proof of zero tools. Missing or insufficient evidence makes a round unverified. Tool-enabled review requires a separately agreed scope; do not silently enable tools. Safe mode is not a claim that administrator-managed context is absent.

Log round, both hashes, actual model, attempt path, masking, findings/responses/status, tests, agreed open items and human decisions in the project's `docs/consensus-log.md` or designated work log. Do not copy private original data into logs.

Consensus and human execution approval are separate. Execute only within human-approved artifact/version and scope; existing explicit authorization and higher-priority instructions govern and do not need redundant confirmation. Prepare a concrete reviewable result before asking for any still-required approval. Checks needing gated access remain pending until authorized; failure or inconclusive results stop dependent actions and return to review or escalation. Never treat an approved plan as proof that pending checks passed.
