#!/usr/bin/env python3
"""Wire the project-local exec-loop gate for Claude Code, Codex, or both.

The walking-skeleton runs this beside the git pre-commit governance installer. It registers
`gate_exec.py` as a project-local PreToolUse hook for file edits, enforcing red-before-green and
blocking hollow done claims at tool-call time.

The default is deliberately `both`: a generated Grill Spec project remains governed when teammates
alternate between Claude Code and Codex. Pass `--host claude` or `--host codex` to install one side.

  python3 install_exec_gates.py [project_root] [--host both|claude|codex]
"""
import json
import shutil
import subprocess
import sys
from pathlib import Path

CLAUDE_HOOK_CMD = 'python3 "$CLAUDE_PROJECT_DIR/.claude/tools/gate_exec.py" --hook'
CODEX_HOOK_CMD = ('python3 "$(git rev-parse --show-toplevel)/.codex/tools/gate_exec.py" '
                  '--hook')
CLAUDE_MATCHER = "Write|Edit|MultiEdit"
CODEX_MATCHER = "apply_patch|Edit|Write"
MARK = "grillspec-exec-gate"
VENDOR = ("gate_exec.py", "check_task_record.py")


def root_dir(argv) -> Path:
    for arg in argv[1:]:
        if not arg.startswith("--") and arg not in {"both", "claude", "codex"} and Path(arg).is_dir():
            return Path(arg)
    try:
        out = subprocess.run(["git", "rev-parse", "--show-toplevel"],
                             capture_output=True, text=True, check=True)
        return Path(out.stdout.strip())
    except Exception:
        return Path.cwd()


def host_option(argv) -> str:
    if "--host" not in argv:
        return "both"
    i = argv.index("--host")
    return argv[i + 1] if i + 1 < len(argv) else ""


def hook_command(host: str) -> str:
    return CLAUDE_HOOK_CMD if host == "claude" else CODEX_HOOK_CMD


def matcher(host: str) -> str:
    return CLAUDE_MATCHER if host == "claude" else CODEX_MATCHER


def our_block(host: str) -> dict:
    handler = {"type": "command", "command": hook_command(host)}
    if host == "codex":
        handler["statusMessage"] = "Checking Grill Spec execution gates"
        return {"matcher": matcher(host), "hooks": [handler]}
    return {"matcher": matcher(host), "_source": MARK, "hooks": [handler]}


def already_installed(pretooluse: list, command: str) -> bool:
    return any(isinstance(block, dict) and (
        block.get("_source") == MARK or
        any(isinstance(hook, dict) and hook.get("command") == command
            for hook in block.get("hooks", [])))
        for block in pretooluse)


def vendor_tools(root: Path, host: str) -> bool:
    here = Path(__file__).resolve().parent
    dest = root / (".claude" if host == "claude" else ".codex") / "tools"
    dest.mkdir(parents=True, exist_ok=True)
    for filename in VENDOR:
        source = here / filename
        target = dest / filename
        if source.resolve() != target.resolve() and source.is_file():
            shutil.copy2(source, target)
    return (dest / "gate_exec.py").is_file()


def install_host(root: Path, host: str) -> int:
    if not vendor_tools(root, host):
        print("install_exec_gates: gate_exec.py is unavailable; refusing to wire a broken hook",
              file=sys.stderr)
        return 1

    settings = (root / ".claude" / "settings.json" if host == "claude"
                else root / ".codex" / "hooks.json")
    settings.parent.mkdir(parents=True, exist_ok=True)
    data = {}
    if settings.is_file():
        try:
            data = json.loads(settings.read_text())
        except Exception as exc:
            print("install_exec_gates: %s is not valid JSON (%s); not touching it"
                  % (settings, exc), file=sys.stderr)
            return 1
    if not isinstance(data, dict):
        print("install_exec_gates: %s is not a JSON object; not touching it" % settings,
              file=sys.stderr)
        return 1

    hooks = data.setdefault("hooks", {})
    pretooluse = hooks.setdefault("PreToolUse", [])
    if not isinstance(pretooluse, list):
        print("install_exec_gates: %s hooks.PreToolUse is not a list; not touching it" % settings,
              file=sys.stderr)
        return 1
    command = hook_command(host)
    if already_installed(pretooluse, command):
        print("install_exec_gates: %s gate already wired in %s" % (host, settings))
        return 0

    pretooluse.append(our_block(host))
    settings.write_text(json.dumps(data, indent=2) + "\n")
    print("install_exec_gates: wired %s PreToolUse gate in %s" % (host, settings))
    return 0


def main(argv) -> int:
    host = host_option(argv)
    if host not in {"both", "claude", "codex"}:
        print("install_exec_gates: --host must be both, claude, or codex", file=sys.stderr)
        return 2
    root = root_dir(argv)
    hosts = ("claude", "codex") if host == "both" else (host,)
    results = [install_host(root, item) for item in hosts]
    return 1 if any(results) else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
