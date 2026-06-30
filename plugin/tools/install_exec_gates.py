#!/usr/bin/env python3
"""Wire the project-local exec-loop gate into THIS repo's `.claude/settings.json`.

The walking-skeleton (derive-tasks T-001) runs this exactly as it `cp`s `spec_governance_hook.sh` into
`.git/hooks/`. It registers `gate_exec.py` as a PreToolUse hook scoped to Write/Edit/MultiEdit, so the
red→green ordering and the no-hollow-done-claim rule are enforced at tool-call time IN THIS PROJECT only.

PROJECT-LOCAL, like the git pre-commit hook: it writes only `<project>/.claude/settings.json`, never the
user's `~/.claude` config, and never fires on other projects. Idempotent — merges its block into an
existing settings.json (preserving the user's other keys/hooks) and no-ops if already present.

  python3 install_exec_gates.py [project_root]      # default: cwd / git toplevel
"""
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

HOOK_CMD = 'python3 "$CLAUDE_PROJECT_DIR/.claude/tools/gate_exec.py" --hook'
MATCHER = "Write|Edit|MultiEdit"
MARK = "grillspec-exec-gate"   # idempotency marker carried on our matcher block
VENDOR = ("gate_exec.py", "check_task_record.py")   # the hook resolves these from .claude/tools/


def root_dir(argv) -> Path:
    if len(argv) > 1 and Path(argv[1]).is_dir():
        return Path(argv[1])
    try:
        out = subprocess.run(["git", "rev-parse", "--show-toplevel"],
                             capture_output=True, text=True, check=True)
        return Path(out.stdout.strip())
    except Exception:
        return Path.cwd()


def our_block() -> dict:
    return {
        "matcher": MATCHER,
        "_source": MARK,
        "hooks": [{"type": "command", "command": HOOK_CMD}],
    }


def already_installed(pretooluse: list) -> bool:
    return any(isinstance(b, dict) and (
                  b.get("_source") == MARK
                  or any(h.get("command") == HOOK_CMD for h in b.get("hooks", []) if isinstance(h, dict)))
              for b in pretooluse)


def vendor_tools(root: Path) -> bool:
    """Copy the scripts the wired hook invokes into <root>/.claude/tools/. Returns True iff
    gate_exec.py is present afterward — the installer must NOT wire a hook whose command would hit a
    missing file (a PreToolUse command that exits non-zero BLOCKS the edit, bricking the editor)."""
    here = Path(__file__).resolve().parent
    dest = root / ".claude" / "tools"
    dest.mkdir(parents=True, exist_ok=True)
    for fn in VENDOR:
        src = here / fn
        if src.resolve() != (dest / fn).resolve() and src.is_file():
            shutil.copy2(src, dest / fn)
    return (dest / "gate_exec.py").is_file()


def main(argv) -> int:
    root = root_dir(argv)
    if not vendor_tools(root):
        print("install_exec_gates: gate_exec.py not found next to the installer and not already "
              "vendored — refusing to wire a hook that would block every edit. Vendor the tools "
              "into %s/.claude/tools/ first." % root, file=sys.stderr)
        return 1
    settings = root / ".claude" / "settings.json"
    settings.parent.mkdir(parents=True, exist_ok=True)

    data = {}
    if settings.is_file():
        try:
            data = json.loads(settings.read_text())
        except Exception as e:
            print("install_exec_gates: %s exists but isn't valid JSON (%s) — not touching it; "
                  "add the PreToolUse hook by hand." % (settings, e), file=sys.stderr)
            return 1
    if not isinstance(data, dict):
        print("install_exec_gates: %s isn't a JSON object — skipping." % settings, file=sys.stderr)
        return 1

    hooks = data.setdefault("hooks", {})
    pretooluse = hooks.setdefault("PreToolUse", [])
    if not isinstance(pretooluse, list):
        print("install_exec_gates: existing hooks.PreToolUse isn't a list — skipping.", file=sys.stderr)
        return 1
    if already_installed(pretooluse):
        print("install_exec_gates: exec gate already wired in %s — nothing to do." % settings)
        return 0

    pretooluse.append(our_block())
    settings.write_text(json.dumps(data, indent=2) + "\n")
    print("install_exec_gates: wired the project-local exec gate into %s "
          "(PreToolUse · %s)." % (settings, MATCHER))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
