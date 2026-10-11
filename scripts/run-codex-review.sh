#!/usr/bin/env bash
# Run one Codex review attempt for the consensus protocol.
#
# Usage: run-codex-review.sh <review_dir> <round> <attempt>
#   <review_dir>  directory holding prompt-<round>.md and the (masked) files to review.
#                 Must be OUTSIDE any git repository.
#   CODEX_MODEL   optional env var; passed as `-m` when set.
#   CODEX_TIMEOUT optional seconds (default 900).
#
# Outputs (never overwritten; bump <attempt> to retry):
#   round-<N>.<A>.md  Codex's final message
#   raw-<N>.<A>.log   full CLI log
#   exit-<N>.<A>      exit code
set -u

if [ $# -ne 3 ]; then
  echo "usage: $0 <review_dir> <round> <attempt>" >&2
  exit 64
fi
R=$1; N=$2; A=$3

[ -d "$R" ] || { echo "no such directory: $R" >&2; exit 66; }
[ -f "$R/prompt-$N.md" ] || { echo "missing $R/prompt-$N.md" >&2; exit 66; }

# Guard: a review dir inside a git repo makes Codex auto-load the repo's AGENTS.md.
if git -C "$R" rev-parse --git-dir >/dev/null 2>&1; then
  echo "refusing: $R is inside a git repository (instruction-file leak risk)" >&2
  exit 65
fi

# Guard: never overwrite a previous attempt (audit trail).
for f in "round-$N.$A.md" "raw-$N.$A.log" "exit-$N.$A"; do
  [ -e "$R/$f" ] && { echo "refusing: $R/$f exists; bump the attempt number" >&2; exit 65; }
done

MODEL_ARGS=()
[ -n "${CODEX_MODEL:-}" ] && MODEL_ARGS=(-m "$CODEX_MODEL")

perl -e 'alarm shift; exec @ARGV' "${CODEX_TIMEOUT:-900}" \
  codex exec ${MODEL_ARGS[@]+"${MODEL_ARGS[@]}"} -c project_doc_max_bytes=0 -s read-only \
  --skip-git-repo-check --ephemeral -C "$R" -o "$R/round-$N.$A.md" - \
  < "$R/prompt-$N.md" > "$R/raw-$N.$A.log" 2>&1
rc=$?
echo "exit=$rc" | tee "$R/exit-$N.$A"

# Accept only: exit 0, fresh non-empty output, and a verdict line.
if [ "$rc" -ne 0 ] || [ ! -s "$R/round-$N.$A.md" ]; then
  echo "attempt FAILED (exit=$rc or empty output); do not adopt" >&2
  exit 1
fi
if ! tail -n 3 "$R/round-$N.$A.md" | grep -Eqi '^(Verdict|판정):'; then
  echo "attempt FAILED (no verdict line); do not adopt" >&2
  exit 1
fi
grep -m1 -i '^model:' "$R/raw-$N.$A.log" || echo 'model: (not found in log)'
