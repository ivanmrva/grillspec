#!/bin/sh
# Spec/doc governance — a PROJECT-LOCAL git pre-commit hook for a grillspec spec/ repo.
#
# This is the "framework-provided, ready-to-run" spec enforcer the walking-skeleton stands up: install it
# into <project>/.git/hooks/pre-commit (compose with the code pre-commit hooks; the code hooks govern
# src/+tests/, this governs spec/). It runs ONLY in this repo, on `git commit` — there is NOTHING global
# about it (it is not a Claude Code hook and never fires on unrelated projects or the user's own config).
#
# It blocks a commit that (1) breaks spec consistency or (2) hand-edits a derived artifact. It no-ops
# cleanly when there is no spec/ or the tools aren't vendored, so a stray install never interferes.
#
# Install (the walking-skeleton / derive-conventions does this):
#   cp .claude/tools/spec_governance_hook.sh .git/hooks/pre-commit && chmod +x .git/hooks/pre-commit
# Emergency override: git commit --no-verify.

root=$(git rev-parse --show-toplevel 2>/dev/null) || exit 0
[ -d "$root/spec" ] || exit 0                       # not a spec repo -> nothing to govern

# the governance tools, vendored into the project (see repo-layout); honor an explicit override
T="${GRILLSPEC_TOOLS:-$root/.claude/tools}"
[ -f "$T/lint_spec.py" ] || exit 0                  # tools not present here -> no-op, never error

# 1) spec consistency — blocks on ERROR (WARN/INFO are advisory and don't block)
if ! python3 "$T/lint_spec.py" "$root/spec"; then
  echo "spec-governance: spec-lint reported ERRORs — fix them, or commit with --no-verify." >&2
  exit 1
fi

# 2) derived artifacts are regenerate-only — blocks a hand-edit
if [ -f "$T/guard_derived.py" ] && ! python3 "$T/guard_derived.py" >/dev/null 2>&1; then
  python3 "$T/guard_derived.py" >&2
  echo "spec-governance: a derived artifact was hand-edited — edit its upstream and re-run the derive skill (or --no-verify)." >&2
  exit 1
fi

# 3) API/event contracts bind to the spec ID graph — blocks a contract referencing an undefined id.
#    No-ops cleanly without contracts or PyYAML; output is shown only on failure (no per-commit chatter).
#    (Contract STRUCTURE/style is the Spectral step in code-ci.yml; this is the cross-layer ID resolution.)
if [ -f "$T/check_contracts.py" ]; then
  cc_out=$(python3 "$T/check_contracts.py" "$root/spec" 2>&1) || {
    echo "$cc_out" >&2
    echo "spec-governance: a contract references an undefined spec id (or failed to parse) — fix the contract or its upstream (or --no-verify)." >&2
    exit 1
  }
fi

# 4) per-task accountability — a task's verification record that CLAIMS done must back every obligation its
#    own (frozen) spec references demand: tests-first traced, independent conformance VERDICT: PASS, no fakes,
#    no dropped/under-bar obligation. An in-progress record never blocks; only an unbacked done-claim does.
#    No-ops cleanly when there are no per-task records yet.
if [ -f "$T/check_task_record.py" ]; then
  tr_out=$(python3 "$T/check_task_record.py" "$root/spec" 2>&1) || {
    echo "$tr_out" >&2
    echo "spec-governance: a task is marked done without the evidence its obligations demand — fill the verification record (or --no-verify)." >&2
    exit 1
  }
fi

exit 0
