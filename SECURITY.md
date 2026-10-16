# Security Policy

## Supported versions

Only the latest release receives fixes. See [Releases](https://github.com/kseungyong/claude-codex-consensus/releases).

## What counts as a security issue

This repo ships skills (instructions for AI agents), a shell helper and a Python helper. Relevant reports include:

- `scripts/run-codex-review.sh` bypassing its guards (reviewing from inside a git repo, overwriting earlier attempts, accepting a failed attempt).
- Skill instructions that would cause secrets, customer data or personal files to be sent to Codex or Claude, or that let an agent skip the human-approval gate.
- Command injection or unsafe handling of paths and environment variables in the helper.

Known, documented limits are not vulnerabilities: `codex exec -s read-only` does not restrict reads, and the protocol is a process guard, not a sandbox (see the README's Security notes).

## How to report

Use GitHub's private vulnerability reporting: open the [Security tab](https://github.com/kseungyong/claude-codex-consensus/security) and click **Report a vulnerability**, or go directly to https://github.com/kseungyong/claude-codex-consensus/security/advisories/new. Do **not** post exploit details in public issues.

This is a one-person project: expect an initial response within about a week, with no formal SLA.

The reverse Claude helper must remain tool-free, must not auto-load user/project customizations, and must reject failed or malformed results. Administrator-managed policy still applies. No helper makes the reviewer’s agreement proof of correctness.
