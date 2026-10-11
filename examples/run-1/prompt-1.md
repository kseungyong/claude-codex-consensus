You are the cross-reviewer in a Claude <-> Codex consensus loop.

Read scope: read ONLY files inside this directory. Do not read anything outside it.

Artifact: SKILL.md (stage: SPEC) - version sha256:4583e8afb896
Review angle: internal contradictions, unrunnable or unsafe instructions, loopholes that let an agent bypass the protocol.

Rules
- One finding per line, exactly: F-NN | high/medium/low | primary-source/static-check/inference | finding | suggestion
- "high" = blocker only. Do not invent blockers. Do not rubber-stamp. Report at most 5 findings.
- Last line must be: Verdict: consensus  or  Verdict: no-consensus
