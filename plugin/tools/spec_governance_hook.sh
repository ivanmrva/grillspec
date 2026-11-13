#!/bin/sh
# Spec/doc governance — a PROJECT-LOCAL git pre-commit hook for a grillspec spec/ repo.
#
# This is the "framework-provided, ready-to-run" spec enforcer the walking-skeleton stands up: install it
# into <project>/.git/hooks/pre-commit (compose with the code pre-commit hooks; the code hooks govern
# src/+tests/, this governs spec/). It runs ONLY in this repo, on `git commit` — there is NOTHING global
# about it (it is not a Claude Code hook and never fires on unrelated projects or the user's own config).
#
# It blocks a commit that breaks spec consistency, binds a contract to an undefined id, claims a task done
# without the tests that back it, or adds a test nothing in the spec drives. It no-ops cleanly when there
# is no spec/ or the tools aren't vendored, so a stray install never interferes.
#
# Install (the walking-skeleton / derive-conventions does this):
#   cp .grillspec/tools/spec_governance_hook.sh .git/hooks/pre-commit && chmod +x .git/hooks/pre-commit
# Emergency override: git commit --no-verify.

root=$(git rev-parse --show-toplevel 2>/dev/null) || exit 0
[ -d "$root/spec" ] || exit 0                       # not a spec repo -> nothing to govern

# the governance tools, vendored into the project (see repo-layout); honor an explicit override
T="${GRILLSPEC_TOOLS:-$root/.grillspec/tools}"
[ -f "$T/lint_spec.py" ] || exit 0                  # tools not present here -> no-op, never error

# 1) spec consistency — blocks on ERROR (WARN/INFO are advisory and don't block)
if ! python3 "$T/lint_spec.py" "$root/spec"; then
  echo "spec-governance: spec-lint reported ERRORs — fix them, or commit with --no-verify." >&2
  exit 1
fi

# 2) API/event contracts bind to the spec ID graph — blocks a contract referencing an undefined id.
#    No-ops cleanly without contracts or PyYAML; output is shown only on failure (no per-commit chatter).
#    (Contract STRUCTURE/style is the Spectral step in code-ci.yml; this is the cross-layer ID resolution.)
if [ -f "$T/check_contracts.py" ]; then
  cc_out=$(python3 "$T/check_contracts.py" "$root/spec" 2>&1) || {
    echo "$cc_out" >&2
    echo "spec-governance: a contract references an undefined spec id (or failed to parse) — fix the contract or its upstream (or --no-verify)." >&2
    exit 1
  }
fi

# 3) a task that claims done is backed by the tree — every acceptance criterion in its brief has an
#    `@covers` test, every named UI state a `@state:` test, no unresolved gap, its dependencies done, and a
#    `critical` task its review. An in-progress task never blocks. No-ops cleanly with no task briefs.
if [ -f "$T/check_task.py" ]; then
  tr_out=$(python3 "$T/check_task.py" "$root/spec" 2>&1) || {
    echo "$tr_out" >&2
    echo "spec-governance: a task is marked done but the tree does not back it — add the missing tests/review, or set its status back (or --no-verify)." >&2
    exit 1
  }
fi

# 4) reverse traceability — every behavioral test traces to a LIVE spec driver (@covers/@state). The
#    drift tripwire: an ad-hoc mid-task instruction implemented straight into code shows up here as an
#    orphan test (or a dangling @covers) — chat is spec input; the driving ID is minted in the spec first.
#    No-ops cleanly without the tool or a test tree.
if [ -f "$T/check_orphan_tests.py" ]; then
  ot_out=$(python3 "$T/check_orphan_tests.py" "$root" 2>&1) || {
    echo "$ot_out" >&2
    echo "spec-governance: a test has no live spec driver — the code grew past the spec; mint/amend the driving ID in its owning area, tag the test, and re-commit (or --no-verify)." >&2
    exit 1
  }
fi

exit 0
