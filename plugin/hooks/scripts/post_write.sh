#!/bin/sh
# PostToolUse (Edit|Write). When a spec/ file changes: lint the spec and surface the downstream
# impact set — so consistency-checking and propagation are automatic, not "remember to run it".
fp=$(python3 -c "import sys,json;print(json.load(sys.stdin).get('tool_input',{}).get('file_path',''))" 2>/dev/null)
case "$fp" in
  *spec/*)
    python3 "${CLAUDE_PLUGIN_ROOT}/tools/lint_spec.py" 2>/dev/null || true
    if git rev-parse --git-dir >/dev/null 2>&1; then
      echo "--- propagation: downstream of your spec change (re-derive these) ---"
      python3 "${CLAUDE_PLUGIN_ROOT}/tools/impact.py" --since HEAD 2>/dev/null || true
    fi
    ;;
esac
exit 0
