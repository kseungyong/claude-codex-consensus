F-01 | high | static-check | RESOLVED: Required verdict is now `Verdict: consensus|no-consensus`; the Korean helper allowance does not replace it. | No further change.
F-02 | high | static-check | RESOLVED: Escalation C now matches disagreement over what counts as fact. | No further change.
F-03 | medium | static-check | RESOLVED: `scripts/run-codex-review.sh` reference is restored. | No further change.
F-04 | low | static-check | RESOLVED: The provenance note identifies this as a translation of SKILL.md and removes ORCA attribution. | No further change.
F-05 | high | static-check | Korean places model-header recording under “재현성이 필요하면,” making it conditional; English requires checking and recording the model every round regardless of optional pinning. | Separate optional model pinning from unconditional per-round model verification and recording.
F-06 | high | static-check | Korean adds “이 잔여 위험을 수용하는 것은 사용자의 결정,” assigning residual-risk acceptance to the user; English specifies audit obligations without this additional decision requirement. | Remove the added sentence clause.
F-07 | high | static-check | The Korean shell comment additionally requires confirming failure of `git -C "$R" rev-parse`; English requires an outside-repository directory without prescribing this check. | Remove the parenthetical check to preserve the canonical requirement.
F-08 | low | static-check | The heading still calls this “한국어 원본,” contradicting its translation status and the English canonical designation. | Change it to “한국어 번역.”
Verdict: no-consensus