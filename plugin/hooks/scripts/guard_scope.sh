#!/bin/sh
# PreToolUse guard (Bash|Edit|Write|NotebookEdit). Keeps autonomous/AFK runs INSIDE the project root and
# OFF destructive/privileged commands. Reads the tool-call JSON on stdin. Exit 2 = DENY the call.
in=$(cat)
tool=$(printf '%s' "$in" | python3 -c "import sys,json;print(json.load(sys.stdin).get('tool_name',''))" 2>/dev/null)
root=$(pwd)
if [ "$tool" = "Bash" ]; then
  cmd=$(printf '%s' "$in" | python3 -c "import sys,json;print(json.load(sys.stdin).get('tool_input',{}).get('command',''))" 2>/dev/null)
  if printf '%s' "$cmd" | grep -Eqi 'sudo |rm +(-[a-z]*r[a-z]*f|-[a-z]*f[a-z]*r)[a-z]* +(/|~|\$home)|rm .*--no-preserve-root|:\(\)\{|mkfs|dd +if=|chmod +(-[a-z]+ +)?0?777|>+ */dev/sd|git +push +(-f|--force)|git +push +[^|&;]*[+][A-Za-z0-9]'; then
    echo "guard_scope: destructive/privileged command blocked" >&2; exit 2
  fi
elif [ "$tool" = "Edit" ] || [ "$tool" = "Write" ] || [ "$tool" = "NotebookEdit" ]; then
  fp=$(printf '%s' "$in" | python3 -c "import sys,json;print(json.load(sys.stdin).get('tool_input',{}).get('file_path',''))" 2>/dev/null)
  case "$fp" in
    "") : ;;
    */../*|../*|*/..) echo "guard_scope: parent-escape path blocked ($fp)" >&2; exit 2 ;;
    /*) case "$fp" in "$root"/*) : ;; *) echo "guard_scope: write outside project root blocked ($fp)" >&2; exit 2 ;; esac ;;
  esac
fi
exit 0
