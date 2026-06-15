#!/bin/sh
# Stop hook. Backstop: flag any derived artifact changed without going through its derive skill
# (the skill is what runs `guard_derived.py --record`). Check-only; does not block.
tmp=$(mktemp) || exit 0
trap 'rm -f "$tmp"' EXIT
python3 "${CLAUDE_PLUGIN_ROOT}/tools/guard_derived.py" >"$tmp" 2>&1
# exit 1 == an actual guard violation; any other non-zero is a run error (e.g. unset root) — stay quiet.
if [ "$?" -eq 1 ]; then
  echo "WARNING - derived-artifact guard:"
  cat "$tmp"
  echo "-> derived files are regenerate-only: change the UPSTREAM and re-run the derive skill."
fi
exit 0
