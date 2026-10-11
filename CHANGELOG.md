# Changelog

All notable changes to this project. Versions link to their GitHub releases.

## [1.0.1] - 2026-10-11

Documentation only. `SKILL.md`, `SKILL.ko.md` and `scripts/run-codex-review.sh` are unchanged, so the Codex consensus recorded for them still applies.

### Added
- README: Quick Start section.
- README: release and license badges.

## [1.0.0] - 2026-10-11

First public release.

### Added
- `skills/codex-consensus/SKILL.md`: English canonical skill (Codex-reviewed, 3 rounds, consensus on sha256 `c5b82327237e`).
- `skills/codex-consensus/SKILL.ko.md`: Korean translation (separately Codex-reviewed for equivalence, 3 rounds, consensus on `6d182193b4a2`).
- `scripts/run-codex-review.sh`: one review attempt with guards (no git-repo review dir, no overwrite, exit/verdict check).
- `examples/`: review prompt template and prompts/results of all real review rounds.
- `docs/consensus-log-example.md`: the protocol's own review log.

[1.0.1]: https://github.com/kseungyong/claude-codex-consensus/releases/tag/v1.0.1
[1.0.0]: https://github.com/kseungyong/claude-codex-consensus/releases/tag/v1.0.0
