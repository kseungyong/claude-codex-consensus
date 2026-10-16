# Bidirectional review — 2026-10-16

Codex led; Claude CLI 2.1.299 reviewed using the configured default model, reported as `claude-sonnet-5-5`. No global model setting was changed.

## Evidence

- Real synthetic defect smoke test: subtraction in an addition function correctly produced a high finding and no-consensus. The first sandboxed call timed out; a permitted retry succeeded.
- Round 1: five findings (one medium, four low), all accepted. See packet/review 1 in `examples/reverse-review/`.
- F-01: reject malformed/hidden findings and conflicting no-findings claims.
- F-02: recognize blocker severity.
- F-03: align applicability/exclusions/audit retention between languages.
- F-04: preserve exact UTF-8 packet bytes and hash; remove locale-dependent I/O.
- F-05: record turn-count/denial metadata, document audit limits, test model and invalid timeout.
- Round 2: no findings, consensus. Exit 0; one turn; no permission denials. See packet/review 2.
- Local offline tests: 7 passed (additional subcases include malformed JSON, nonzero exit, tool metadata, hidden high findings and timeouts).
- Skill validator and git diff whitespace check passed.

Invocation used safe mode, no tools, empty strict MCP configuration, disabled skills and no session persistence. Invocation and available response metadata were inspected locally. This is not a full tool trace or proof that managed policy cannot inject context. Raw local responses include session/runtime metadata and are not published; sanitized review packets and model review text are published. No source project or personal data was provided.

## Reviewed artifact hashes

- `skills/claude-consensus/SKILL.md`: `85b450389dcb7de4076c09ad89d3ca98a3c60c7c89ae3ed621491dfe3196364d`
- `skills/claude-consensus/SKILL.ko.md`: `8b6a64f89e73ffa5825a24c3069743a068b0cb9b93f1ba13a569a5c8e2ae4222`
- `skills/claude-consensus/scripts/review.py`: `427fa538d0871aa5c2dff721570a4575063d7efaddb24df70050286a26575361`
- `tests/test_claude_review.py`: `5177875994a92b2a522bf095d79148dbafce0ff68bae8572036fee7fd0f37bc4`

Round-2 packet SHA-256: `19f26583df31cfc047c786c86ed0e9241a30b2ca4aff45f5646fcdeb9a8916ed`. Packet contains the exact reviewed files plus prior feedback. No masking of these public artifacts was needed.

Remaining limitations: the reviewer has only packet context, no execution tools. Human review and actual tests remain necessary. Historical forward-direction examples are not evidence for reverse behavior. The user explicitly requested updating this GitHub repository; that authorization covers publication of this change.
