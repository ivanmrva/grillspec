#!/usr/bin/env python3
"""Exec-loop process gate — a PROJECT-LOCAL Claude Code PreToolUse hook for a grillspec project.

This is the tool-call-time sibling of the commit-time `spec_governance_hook.sh`. The commit/CI
checkers verify the END STATE of a task; this gate verifies the ORDER of the work WHILE it happens,
which is the only thing a commit-time check structurally cannot see (exec-engine.md: "Temporal order
on its own can't be proven after the fact"). It enforces exactly two transitions of the per-task loop:

  1. RED-before-GREEN — a production-tree edit (`src/**`, non-test) is blocked while a task is active
     UNLESS a real failing-test run was recorded for that task. Kills the "skip the tests / write all
     the code, back-fill tests after" batching the engine forbids.
  2. No hollow done-claim — an edit that flips a task's `status:` to `done` is blocked unless
     `check_task_record.py --task T-NNN` is already green. Promotes the existing commit-time check to
     the moment the claim is made, instead of discovering it at commit.

It is PROJECT-LOCAL: the walking-skeleton wires it into THIS repo's `.claude/settings.json` (see
`install_exec_gates.py`), exactly like the git pre-commit hook is wired into THIS repo's `.git/hooks/`.
It is NOT a global hook and never fires on other projects or the user's `~/.claude` config.

  Fail-OPEN by design: any internal error allows the tool call (a bug in the gate must never brick the
  user's ability to edit). It DENIES (exit 2) only on a clean, intended gate violation.
  Emergency override: set GRILLSPEC_GATE_OFF=1 (the tool-call analogue of `git commit --no-verify`).

Subcommands the exec loop calls (the engine instructs it; the gate enforces it):
  --start T-NNN              mark T-NNN the active task (gate engages for it; off when no task active)
  --red   --test "<cmd>"     run <cmd>, REQUIRE it to fail, record the red-log for the active task
  --done  [T-NNN]            clear the active task (after merge)
  --hook                     PreToolUse entrypoint: reads the hook JSON on stdin, allow(0)/deny(2)
"""
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

TEST_MARKERS = (".test.", ".spec.", "_test.", "test_", "/tests/", "/__tests__/", "/test/")
DEFAULT_PRODUCTION_GLOBS = ["src/"]   # relative-path prefixes that count as the shipping tree


def project_root() -> Path:
    env = os.environ.get("CLAUDE_PROJECT_DIR")
    if env and Path(env).is_dir():
        return Path(env)
    try:
        out = subprocess.run(["git", "rev-parse", "--show-toplevel"],
                             capture_output=True, text=True, check=True)
        return Path(out.stdout.strip())
    except Exception:
        return Path.cwd()


def gate_dir(root: Path) -> Path:
    for cand in (root / "spec" / "10-delivery" / "verification",
                 root / "spec" / "delivery" / "verification"):
        if cand.exists():
            return cand / ".gate"
    return root / "spec" / "10-delivery" / "verification" / ".gate"


def config(root: Path) -> dict:
    p = root / ".claude" / "grillspec-gate.json"
    if p.is_file():
        try:
            return json.loads(p.read_text())
        except Exception:
            pass
    return {}


def production_globs(root: Path) -> list:
    return config(root).get("production_globs", DEFAULT_PRODUCTION_GLOBS)


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def active_task(root: Path):
    p = gate_dir(root) / "active-task"
    if p.is_file():
        t = p.read_text().strip()
        return t or None
    return None


def is_production_path(root: Path, file_path: str) -> bool:
    """A shipping-tree code file the RED gate governs — under a production glob, not a test file."""
    if not file_path:
        return False
    try:
        rel = os.path.relpath(os.path.abspath(file_path), root).replace(os.sep, "/")
    except Exception:
        return False
    if rel.startswith(".."):           # outside the repo — not ours to gate
        return False
    norm = "/" + rel
    if any(m in norm for m in TEST_MARKERS):
        return False
    return any(rel == g.rstrip("/") or rel.startswith(g if g.endswith("/") else g + "/")
               for g in production_globs(root))


# ---- subcommands the exec loop drives -------------------------------------------------

def cmd_start(task: str) -> int:
    root = project_root()
    if not re.fullmatch(r"T-\d+", task or ""):
        print("gate: --start needs a task id like T-014", file=sys.stderr)
        return 1
    g = gate_dir(root)
    g.mkdir(parents=True, exist_ok=True)
    (g / "active-task").write_text(task + "\n")
    print("gate: active task = %s (RED gate engaged for src/** edits)" % task)
    return 0


def cmd_done(task: str) -> int:
    root = project_root()
    p = gate_dir(root) / "active-task"
    if p.is_file():
        p.unlink()
    print("gate: active task cleared")
    return 0


def cmd_red(test_cmd: str) -> int:
    """Run the test command, REQUIRE it to fail, then record the red-log for the active task.

    A red-log written only after a real non-zero (failing) test run is what makes the RED gate mean
    'a failing test was actually seen', not 'the model asserted it ran one'."""
    root = project_root()
    task = active_task(root)
    if not task:
        print("gate --red: no active task — call `--start T-NNN` first", file=sys.stderr)
        return 1
    if not test_cmd:
        print("gate --red: pass the failing-test command via --test \"...\"", file=sys.stderr)
        return 1
    proc = subprocess.run(test_cmd, shell=True, cwd=root, capture_output=True, text=True)
    if proc.returncode == 0:
        print("gate --red: that test command PASSED (exit 0) — RED needs a test that FAILS for the "
              "right reason before you write the code. Write the failing test first.", file=sys.stderr)
        return 1
    g = gate_dir(root)
    (g / "red").mkdir(parents=True, exist_ok=True)
    (g / "red" / (task + ".json")).write_text(json.dumps({
        "task": task, "test_cmd": test_cmd, "recorded_at": now_iso(),
        "exit_code": proc.returncode,
    }, indent=2) + "\n")
    print("gate --red: recorded failing test for %s — src/** edits for this task are now unblocked." % task)
    return 0


# ---- the PreToolUse hook entrypoint ----------------------------------------------------

def deny(reason: str) -> int:
    print("grillspec exec-gate: " + reason, file=sys.stderr)
    return 2


def introduces_done(tool_input: dict) -> bool:
    """True if this Write/Edit/MultiEdit sets `status: done` where it wasn't already."""
    pat = re.compile(r"status\s*:\s*(done|complete)\b", re.I)
    if "content" in tool_input:                                  # Write
        return bool(pat.search(tool_input.get("content", "")))
    edits = tool_input.get("edits")
    if isinstance(edits, list):                                  # MultiEdit
        return any(pat.search(e.get("new_string", "")) and not pat.search(e.get("old_string", ""))
                   for e in edits)
    return bool(pat.search(tool_input.get("new_string", ""))     # Edit
                and not pat.search(tool_input.get("old_string", "")))


def task_id_from_path(file_path: str):
    m = re.search(r"(T-\d+)", os.path.basename(file_path or ""))
    return m.group(1) if m else None


def cmd_hook() -> int:
    try:
        payload = json.load(sys.stdin)
    except Exception:
        return 0                                                 # unparseable → fail open
    if os.environ.get("GRILLSPEC_GATE_OFF"):
        return 0
    root = project_root()
    if not (root / "spec").is_dir():                             # not a grillspec project → no-op
        return 0
    tool_input = payload.get("tool_input", {}) or {}
    file_path = tool_input.get("file_path", "") or ""

    # Gate 2 — no hollow done-claim. A task record flipped to `status: done` must already pass its
    # verification record. Runs the existing checker; denies on any non-zero.
    if "verification" in file_path.replace(os.sep, "/") and introduces_done(tool_input):
        tid = task_id_from_path(file_path)
        if tid:
            checker = root / ".claude" / "tools" / "check_task_record.py"
            if not checker.is_file():
                checker = Path(__file__).resolve().parent / "check_task_record.py"
            spec = root / "spec"
            res = subprocess.run([sys.executable, str(checker), str(spec), "--task", tid,
                                  "--assume-done"], capture_output=True, text=True)
            if res.returncode != 0:
                return deny(
                    "%s is being marked `status: done` but its Verification Record is not green:\n%s\n"
                    "Fill the unmet obligations (tests-first traced · independent VERDICT: PASS · no "
                    "fakes) before claiming done, or override with GRILLSPEC_GATE_OFF=1."
                    % (tid, (res.stdout + res.stderr).strip()))
        return 0

    # Gate 1 — RED before GREEN. A production-tree edit needs a recorded failing test for the active
    # task. No active task → not inside an exec loop → not gated (walking-skeleton/ad-hoc edits pass).
    if is_production_path(root, file_path):
        task = active_task(root)
        if not task:
            return 0
        red = gate_dir(root) / "red" / (task + ".json")
        if red.is_file():
            return 0
        return deny(
            "no failing test recorded for the active task %s — write ONE small failing test for the "
            "next behavior and watch it fail (`python3 .claude/tools/gate_exec.py --red --test "
            "\"<your test command>\"`) BEFORE writing production code in %s. This is the red→green "
            "micro-cycle; don't batch all code then back-fill tests. Override: GRILLSPEC_GATE_OFF=1."
            % (task, os.path.relpath(file_path, root) if file_path else "src/"))
    return 0


def main() -> int:
    args = sys.argv[1:]
    if "--hook" in args:
        return cmd_hook()
    if "--start" in args:
        i = args.index("--start")
        return cmd_start(args[i + 1] if i + 1 < len(args) else "")
    if "--done" in args:
        i = args.index("--done")
        return cmd_done(args[i + 1] if i + 1 < len(args) and not args[i + 1].startswith("--") else "")
    if "--red" in args:
        test = ""
        if "--test" in args:
            j = args.index("--test")
            test = args[j + 1] if j + 1 < len(args) else ""
        return cmd_red(test)
    print(__doc__)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except SystemExit:
        raise
    except Exception as e:                                        # fail-open backstop
        print("grillspec exec-gate: internal error, allowing (%s)" % e, file=sys.stderr)
        sys.exit(0)
