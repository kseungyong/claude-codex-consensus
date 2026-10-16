# Claude ↔ Codex Consensus Protocol

[![Release](https://img.shields.io/github/v/release/kseungyong/claude-codex-consensus)](https://github.com/kseungyong/claude-codex-consensus/releases/latest) [![ShellCheck](https://github.com/kseungyong/claude-codex-consensus/actions/workflows/shellcheck.yml/badge.svg)](https://github.com/kseungyong/claude-codex-consensus/actions/workflows/shellcheck.yml) [![License: MIT](https://img.shields.io/github/license/kseungyong/claude-codex-consensus)](LICENSE)

Bidirectional cross-review skills for **Claude Code and Codex**. The leading agent drafts; the other reviews the same version; disagreements are resolved using evidence; human execution authorization remains separate.

| Lead | Reviewer | Skill | Install location |
|---|---|---|---|
| Claude | Codex | `codex-consensus` | `~/.claude/skills/codex-consensus/` |
| Codex | Claude | `claude-consensus` | `~/.codex/skills/claude-consensus/` |

**한국어:** 기존 Claude → Codex 흐름에 Codex → Claude 흐름을 추가했습니다. 주도 에이전트에 맞는 스킬 하나를 사용하며, 두 스킬을 재귀 호출하지 않습니다. 기존 설치 경로와 명령은 유지됩니다. 새 역방향 스킬의 한국어판은 [SKILL.ko.md](skills/claude-consensus/SKILL.ko.md)입니다.

## Quick Start

Install and authenticate the reviewer CLI (`codex` for the forward direction, `claude` for reverse).

```bash
git clone https://github.com/kseungyong/claude-codex-consensus.git
cd claude-codex-consensus
# Claude leads → Codex reviews (existing entry point)
mkdir -p ~/.claude/skills/codex-consensus
cp skills/codex-consensus/SKILL.md ~/.claude/skills/codex-consensus/
# Codex leads → Claude reviews (copy the helper too)
mkdir -p ~/.codex/skills/claude-consensus
cp -R skills/claude-consensus/. ~/.codex/skills/claude-consensus/
```

In Claude: “Use codex-consensus to review this plan.”
In Codex: “Use $claude-consensus to review this plan.”
Restart the host or start a new session if it has not discovered a newly installed skill.

The protocol tracks stable findings and artifact hashes, accepts fixes or evidence-backed rebuttals, and caps unresolved disagreements at 3 rounds per point / 5 rounds per artifact. Agreement is not test evidence or new execution permission. Historical examples below cover the original forward workflow only.

## Why

A single model reviewing its own plan rubber-stamps it. Two models agreeing with each other is also not verification. This protocol forces:

- **Same artifact, versioned** — consensus is bound to a hash, so "I tweaked it after approval" voids it.
- **Stable finding IDs + severity + evidence grade** — disagreements are traceable, not vibes.
- **Rebut or accept, never fold** — blind acceptance is treated as capitulation, not consensus.
- **Facts closed by execution** (tests, builds, measurements), not by two LLMs nodding.
- **Hard escalation rules** — unresolved after 3 rounds on one point, disputed severity, 5 rounds total → human decides.
- **Human approval is separate from consensus.**

## When it triggers

Anything hard to reverse, production-touching, or design-locking (deploys, migrations, schema/config changes, merges into live branches, specs/plans that fix a design). Typos, comments and read-only investigation are excluded; applicability always beats exclusion.

## Install

```bash
# Claude Code (user-level)
mkdir -p ~/.claude/skills/codex-consensus
cp skills/codex-consensus/SKILL.md ~/.claude/skills/codex-consensus/
```

The forward direction requires the [Codex CLI](https://github.com/openai/codex) (`codex exec`). Developed against codex-cli 0.155–0.162; re-check flags with `codex exec --help` on your version.

Optionally add a pointer in your `CLAUDE.md`:

```markdown
Before any hard-to-reverse / production-touching / design-fixing work, load the `codex-consensus` skill and follow it. Execute only after consensus + my approval.
```

## Repo layout

| Path | What |
|---|---|
| `skills/codex-consensus/SKILL.md` | The skill (English) |
| `skills/codex-consensus/SKILL.ko.md` | Korean translation (separately Codex-reviewed against `SKILL.md`) |
| `skills/claude-consensus/SKILL.md` | Reverse skill: Codex leads, Claude reviews |
| `skills/claude-consensus/SKILL.ko.md` | Korean reverse skill |
| `skills/claude-consensus/scripts/review.py` | Tool-free Claude review helper with unique attempt logs |
| `scripts/run-codex-review.sh` | One review attempt with guards (git-repo check, no overwrite, verdict check) |
| `examples/review-prompt.md` | Prompt template for Codex |
| `docs/consensus-log-example.md` | The protocol's own review log |
| `examples/run-1..3/` | Prompt and raw result of each review round of `SKILL.md` |
| `examples/ko-run-1..3/` | Same, for the Korean translation `SKILL.ko.md` |

## Usage of the helper

```bash
R="$(mktemp -d)"            # must NOT be inside a git repo
# copy + mask files, read them all yourself, write $R/prompt-1.md
CODEX_MODEL=<optional-slug> scripts/run-codex-review.sh "$R" 1 1
```

Reverse implementation validation: [review log](docs/bidirectional-review.md) and [actual review packets/results](examples/reverse-review/). Seven offline helper tests passed; the final Claude review had no findings.

## Reverse helper

```bash
python3 skills/claude-consensus/scripts/review.py \
  --packet /tmp/review-packet.txt --output-dir /tmp/consensus-results
```

The packet includes the sanitized artifact, version, acceptance criteria and prior findings/responses. The helper hashes and preserves that packet, uses Claude with no tools/MCP/skills and safe mode, and stores `raw.json`, `stderr.log`, `status.json`, and a validated `review.md` in a new attempt directory. `reviewed` means a valid review, **not** consensus or permission to execute. `--model` is optional; the CLI default is preserved. Requires Python 3 and a Claude CLI supporting the listed flags (tested with 2.1.299). Each real round uses your Claude authentication and may incur model usage costs.

## Example run (round 1, real output, unedited)

One round of `scripts/run-codex-review.sh` against this repo's own `SKILL.md` (sha256 `4583e8afb896`). Codex CLI 0.162.1, model `gpt-6-astra`, reasoning effort low, exit code 0. Prompt and full result: [`examples/run-1/`](examples/run-1/). Rounds 2–3 follow below the output.

```text
F-01 | medium | static-check | Version binding does not specify how the masked review copy maps to the original execution artifact; hashing either alone cannot establish that the approved artifact is the one reviewed. | Record both hashes and the masking transformation, verify their correspondence locally, and invalidate approval when either artifact changes.
F-02 | medium | static-check | "Run them against existing data immediately" is unconditional and can require live-system access or execution before consensus and approval, conflicting with the execution gate and pre-verification restrictions. | Limit immediate verification to permitted isolated checks; defer checks requiring gated access until explicitly approved and record pending verification.
F-03 | medium | static-check | The mandatory read-scope audit has no defined evidence requirements or handling for incomplete visibility; exit code, fresh output, and valid format can pass while scope compliance remains unverifiable. | Require a documented scope audit before accepting a round and treat missing or insufficient access evidence as an unverified round requiring escalation.
Verdict: no-consensus
```

What this shows: round 1 was **no-consensus** (3 medium, 0 high). Claude accepted all three, edited `SKILL.md`, and re-ran:

| Round | Artifact sha256 | Result |
|---|---|---|
| 1 | `4583e8afb896` | no-consensus: F-01, F-02, F-03 (medium) |
| 2 | `b9d417ecf665` | no-consensus: F-01~F-03 RESOLVED; new F-04 (medium): pending verification had no outcome gate |
| 3 | `c5b82327237e` | **consensus**: F-04 RESOLVED, no open findings |

Prompts and results for each round are in `examples/run-1/`, `run-2/`, `run-3/`. Scope audit: in every round the log shows only in-directory commands (`ls`/`rg --files`/`cat SKILL.md`/`shasum`), so all rounds are valid. Consensus is bound to `c5b82327237e`; the Korean `SKILL.ko.md` was synced by hand afterwards and then reviewed separately for normative equivalence with `SKILL.md`: 3 rounds, 8 findings (as labeled by Codex: 5 high, 1 medium, 2 low; the author considered F-05..F-07 medium), all accepted and fixed, consensus on `6d182193b4a2` (prompts/results in `examples/ko-run-1..3/`). Caveat: this is a single reviewer at low reasoning effort; per the protocol, facts are closed by execution, not by two models agreeing.

## Security notes — read before use

- `codex exec -s read-only` blocks **writes only**; Codex can still read outside the review directory. Mitigation here is a prompt-level read scope plus post-hoc audit of the log. Treat it as residual risk.
- If the review directory is inside a git repo, Codex auto-loads that repo's `AGENTS.md` and follows it. The skill requires a directory outside any repo **and** `-c project_doc_max_bytes=0`.
- Reverse calls use `--safe-mode --tools "" --strict-mcp-config --mcp-config '{"mcpServers":{}}' --disable-slash-commands --no-session-persistence`. Managed policy still applies. Review only the explicitly prepared packet; do not enable tools as a retry workaround.
- Never send secrets, customer or financial data. Masking by command is not de-identification: read the whole copy before sending.
- To report a vulnerability, see [SECURITY.md](SECURITY.md).

## Limits (honest)

- Not battle-tested at scale: it was developed by one person for one workflow and reviewed by the protocol itself (see the example log).
- Cost: each round is a real model call; the 3/5-round caps exist partly for this reason.
- It's a process guard, not a sandbox. A determined agent can ignore it; it relies on the agent loading and following the skill.

## Contributing

Issues and PRs are welcome; this is a one-person project, so expect slow replies.

- **Bugs, questions, ideas:** open an [issue](https://github.com/kseungyong/claude-codex-consensus/issues). For vulnerabilities, use [SECURITY.md](SECURITY.md), not a public issue.
- **Scripts:** `scripts/*.sh` must pass ShellCheck; the reverse helper must pass `python3 -m unittest discover -s tests -v` (both run in CI).
- **Changes to the rules in `SKILL.md`** (what the protocol requires or forbids) are design changes, so the protocol applies to them too. Describe the problem and the evidence, and expect the maintainer to run the opposite reviewer on the new version before merging. Wording-only fixes don't need this.
- **Keep both languages in sync:** a rule change in `SKILL.md` needs the matching change in `SKILL.ko.md`; the two are reviewed for equivalence.
- Don't commit review artifacts that contain secrets, customer data or personal files. Mask them first and read the whole copy.

## Changelog

See [CHANGELOG.md](CHANGELOG.md) and the [Releases](https://github.com/kseungyong/claude-codex-consensus/releases) page.

## License

MIT
