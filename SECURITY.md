# Security Policy

## Supported versions

Only the latest release receives fixes. See [Releases](https://github.com/kseungyong/claude-codex-consensus/releases).

## What counts as a security issue

This repo ships a skill (instructions for an AI agent) and a small shell helper. Relevant reports include:

- `scripts/run-codex-review.sh` bypassing its guards (reviewing from inside a git repo, overwriting earlier attempts, accepting a failed attempt).
- Skill instructions that would cause secrets, customer data or personal files to be sent to Codex, or that let an agent skip the human-approval gate.
- Command injection or unsafe handling of paths and environment variables in the helper.

Known, documented limits are not vulnerabilities: `codex exec -s read-only` does not restrict reads, and the protocol is a process guard, not a sandbox (see the README's Security notes).

## How to report

Do **not** post exploit details publicly. Open an issue at https://github.com/kseungyong/claude-codex-consensus/issues titled `Security: please contact me`, with no technical details, and the maintainer will arrange a private channel. If GitHub private vulnerability reporting is enabled for this repo, use the *Report a vulnerability* button on the Security tab instead.

This is a one-person project: expect an initial response within about a week, with no formal SLA.
