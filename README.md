# Claude ↔ Codex Consensus Protocol

[![Release](https://img.shields.io/github/v/release/kseungyong/claude-codex-consensus)](https://github.com/kseungyong/claude-codex-consensus/releases/latest) [![License: MIT](https://img.shields.io/github/license/kseungyong/claude-codex-consensus)](LICENSE)

A Claude Code skill that gates an LLM agent's irreversible actions behind cross-review consensus and human approval.
Claude drafts → Codex cross-reviews by severity → they converge on **evidence** → a **human approves** → only then does Claude execute.

> **한국어 요약**
> Claude가 산출물을 만들고, Codex가 심각도별로 교차검증하고, 둘이 **근거**로 차이를 좁힌 뒤, **사람이 승인**해야만 실행하는 Claude Code 스킬입니다. 되돌리기 어렵거나 · 프로덕션에 닿거나 · 설계를 고정하는 작업에 적용합니다.
> - 같은 산출물을 해시로 버전 고정하고, 합의·승인은 그 버전에 묶입니다.
> - 지적마다 안정 ID · 심각도 · 근거등급을 붙이고, 수용하거나 근거로 반박합니다(맹종 금지).
> - 사실은 두 LLM의 동의가 아니라 실행(테스트·측정)으로 닫습니다.
> - 한 지점이 3라운드, 총 5라운드 안에 안 좁혀지거나 심각도가 다투어지면 사람에게 에스컬레이션합니다.
> - 합의 ≠ 승인: 합의 후에도 사람의 승인이 있어야 실행합니다.
>
> 필요 조건: [Codex CLI](https://github.com/openai/codex)(`codex exec`)가 설치돼 있어야 합니다.
>
> 설치: `skills/codex-consensus/SKILL.md`(영문 정본) 또는 [`SKILL.ko.md`](skills/codex-consensus/SKILL.ko.md)(한국어 판)를 `~/.claude/skills/codex-consensus/SKILL.md`로 복사하세요. 한국어 판은 영문 정본과의 규범 일치 여부를 Codex가 3라운드로 따로 검토했습니다(`6d182193b4a2`, `examples/ko-run-1..3/`). 보안 주의(`read-only`는 읽기를 막지 않음, `AGENTS.md` 자동 로드)는 아래 Security notes를 꼭 읽으세요.
>
> 한계: 실전 검증이 부족합니다(한 사람의 워크플로용으로 만들고 이 프로토콜로 자체 검토만 함). 라운드마다 실제 모델 호출 비용이 들고, 샌드박스가 아니라 프로세스 가드라서 에이전트가 스킬을 따를 때만 작동합니다.

## Quick Start

1. Install and log in to the [Codex CLI](https://github.com/openai/codex) (`codex exec` must work).
2. Install the skill:
   ```bash
   git clone https://github.com/kseungyong/claude-codex-consensus.git
   mkdir -p ~/.claude/skills/codex-consensus
   cp claude-codex-consensus/skills/codex-consensus/SKILL.md ~/.claude/skills/codex-consensus/
   ```
3. In Claude Code, ask for a risky change and name the skill, e.g. *"Use the codex-consensus skill before you migrate this schema."* (Or add the pointer from [Install](#install) to your `CLAUDE.md` so it triggers on its own.)
4. Claude then saves the artifact and records its hash, sends a masked copy to Codex, answers each `F-NN` finding (fix or rebut with evidence), and repeats until consensus or escalation.
5. Claude reports consensus status and open items and asks you to approve **that exact version**. Nothing executes before you do.

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

Requires the [Codex CLI](https://github.com/openai/codex) (`codex exec`). Developed against codex-cli 0.155–0.162; re-check flags with `codex exec --help` on your version.

Optionally add a pointer in your `CLAUDE.md`:

```markdown
Before any hard-to-reverse / production-touching / design-fixing work, load the `codex-consensus` skill and follow it. Execute only after consensus + my approval.
```

## Repo layout

| Path | What |
|---|---|
| `skills/codex-consensus/SKILL.md` | The skill (English) |
| `skills/codex-consensus/SKILL.ko.md` | Korean translation (separately Codex-reviewed against `SKILL.md`) |
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
- Never send secrets, customer or financial data. Masking by command is not de-identification: read the whole copy before sending.

## Limits (honest)

- Not battle-tested at scale: it was developed by one person for one workflow and reviewed by the protocol itself (see the example log).
- Cost: each round is a real model call; the 3/5-round caps exist partly for this reason.
- It's a process guard, not a sandbox. A determined agent can ignore it; it relies on the agent loading and following the skill.

## License

MIT
