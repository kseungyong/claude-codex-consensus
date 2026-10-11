# consensus-log — example (the protocol reviewing itself)

Artifact: `SKILL.md`. Real log from the protocol's own review, translated.

| Round | Version (sha256) | Verdict |
|---|---|---|
| 1 | (draft) | no consensus — 4 high, 5 medium |
| 2 | 193a37fcacc8 | no consensus — F-05, F-07 unresolved |
| 3 | 1931cf5ca84f | **consensus** |

| ID | Severity | Finding | Response | Status |
|---|---|---|---|---|
| F-01 | high | Exclusions shrink the principle; no precedence | Applicability beats exclusion; removed "one-line constant" exclusion | resolved |
| F-02 | high | "Pre-live gate" is a bypass | Pre-verification limited to fact-gathering; conflict resolution/implementation are artifacts | resolved |
| F-03 | high | 3-round rule can be gamed | Per-point counting + renaming doesn't reset; 5-round total cap | resolved |
| F-04 | medium | Example command not runnable | mktemp, quoting, N; flags checked against `--help` | resolved |
| F-05 | high | `read-only` doesn't isolate reads | Limitation documented + read scope in prompt + post-hoc audit | **human decision: risk accepted** |
| F-06 | medium | Masking makes reviewed copy ≠ original | Log masked items; dependent judgments verified locally or escalated | resolved |
| F-07 | medium | Retries overwrite logs | Per round.attempt files, never overwritten | resolved |
| F-08 | medium | Readiness cause asserted; auto-update | Check actual wait reason; update only after user confirms | resolved |
| F-09 | medium | Consensus not bound to a version | Per-round hash; re-review on change | resolved |

Open items: none. Audit: in all 3 rounds Codex read nothing outside the review directory.
