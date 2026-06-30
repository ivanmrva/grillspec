#!/usr/bin/env python3
"""Behavior tests for the exec-loop gate + its installer. Run: python3 tools/test_gate_exec.py"""
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
GATE = HERE / "gate_exec.py"
INSTALL = HERE / "install_exec_gates.py"


def run_hook(root, tool_name, tool_input, env_extra=None):
    env = dict(os.environ, CLAUDE_PROJECT_DIR=str(root))
    if env_extra:
        env.update(env_extra)
    payload = json.dumps({"hook_event_name": "PreToolUse",
                          "tool_name": tool_name, "tool_input": tool_input})
    return subprocess.run([sys.executable, str(GATE), "--hook"],
                          input=payload, capture_output=True, text=True, env=env)


def run_sub(root, *args, env_extra=None):
    env = dict(os.environ, CLAUDE_PROJECT_DIR=str(root))
    if env_extra:
        env.update(env_extra)
    return subprocess.run([sys.executable, str(GATE), *args],
                          capture_output=True, text=True, env=env, cwd=str(root))


def mkproject():
    d = Path(tempfile.mkdtemp())
    (d / "spec" / "10-delivery" / "verification").mkdir(parents=True)
    (d / "src").mkdir()
    return d


def mkgitproject(branch):
    """A git project checked out on `branch` — for the branch-derived (parallel-safe) active task."""
    d = mkproject()
    (d / "README").write_text("x\n")          # something to track so the initial commit isn't empty
    env = dict(os.environ, GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t",
               GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@t")
    for cmd in (["git", "init", "-q"], ["git", "add", "-A"],
                ["git", "commit", "-qm", "init"], ["git", "checkout", "-qb", branch]):
        subprocess.run(cmd, cwd=d, env=env, capture_output=True)
    return d


PASS = FAIL = 0


def check(name, cond):
    global PASS, FAIL
    if cond:
        PASS += 1
        print("  ok   " + name)
    else:
        FAIL += 1
        print("  FAIL " + name)


def main():
    # --- not a grillspec project → fail open --------------------------------------------
    empty = Path(tempfile.mkdtemp())
    r = run_hook(empty, "Edit", {"file_path": str(empty / "src" / "a.py"),
                                 "old_string": "x", "new_string": "y"})
    check("no spec/ dir → allow", r.returncode == 0)

    # --- src edit with NO active task → allow (not inside an exec loop) ------------------
    p = mkproject()
    src = p / "src" / "a.py"
    r = run_hook(p, "Write", {"file_path": str(src), "content": "print(1)"})
    check("no active task → src edit allowed", r.returncode == 0)

    # --- active task, no red-log → DENY -------------------------------------------------
    run_sub(p, "--start", "T-007")
    r = run_hook(p, "Write", {"file_path": str(src), "content": "print(1)"})
    check("active task + no red-log → src edit DENIED", r.returncode == 2)
    check("deny message mentions failing test", "failing test" in r.stderr.lower())

    # --- test file is never gated -------------------------------------------------------
    r = run_hook(p, "Write", {"file_path": str(p / "src" / "a.test.py"), "content": "t"})
    check("test file edit allowed even with active task", r.returncode == 0)

    # --- --red refuses a PASSING test command -------------------------------------------
    r = run_sub(p, "--red", "--test", "true")
    check("--red on a passing test is rejected", r.returncode == 1)
    r = run_hook(p, "Write", {"file_path": str(src), "content": "print(1)"})
    check("still denied after failed --red attempt", r.returncode == 2)

    # --- --red on a FAILING test records the log → src edit now allowed ------------------
    r = run_sub(p, "--red", "--test", "false")
    check("--red on a failing test recorded", r.returncode == 0)
    check("red-log file exists",
          (p / "spec" / "10-delivery" / "verification" / ".gate" / "red" / "T-007.json").is_file())
    check("gate dir self-ignores (transient state not committed)",
          (p / "spec" / "10-delivery" / "verification" / ".gate" / ".gitignore").read_text().strip().endswith("*"))
    r = run_hook(p, "Write", {"file_path": str(src), "content": "print(1)"})
    check("src edit allowed after red-log", r.returncode == 0)

    # --- override env bypasses the gate -------------------------------------------------
    p2 = mkproject()
    run_sub(p2, "--start", "T-009")
    r = run_hook(p2, "Write", {"file_path": str(p2 / "src" / "b.py"), "content": "x"},
                 env_extra={"GRILLSPEC_GATE_OFF": "1"})
    check("GRILLSPEC_GATE_OFF bypasses RED gate", r.returncode == 0)

    # --- done-claim gate: status: done with a failing record → DENY ---------------------
    rec_dir = p / "spec" / "10-delivery" / "verification" / "tasks"
    rec_dir.mkdir(parents=True, exist_ok=True)
    rec = rec_dir / "T-007.md"
    rec.write_text("status: in-progress\n\n| id | ... | status |\n|----|-----|--------|\n"
                   "| AC-1 | x | PENDING |\n")
    r = run_hook(p, "Edit", {"file_path": str(rec),
                             "old_string": "status: in-progress",
                             "new_string": "status: done"})
    check("flip to done with unmet obligations → DENIED", r.returncode == 2)

    # --- a non-done edit to the same record is not gated --------------------------------
    r = run_hook(p, "Edit", {"file_path": str(rec),
                             "old_string": "PENDING", "new_string": "PASS"})
    check("non-done edit to record allowed", r.returncode == 0)

    # --- branch-derived active task (parallel-safe, no --start needed) ------------------
    gb = mkgitproject("task/T-021-foo")
    bsrc = gb / "src" / "c.py"
    r = run_hook(gb, "Write", {"file_path": str(bsrc), "content": "x"})
    check("on a task branch + no red-log → src edit DENIED (branch is the signal)", r.returncode == 2)
    r = run_sub(gb, "--red", "--test", "false")          # no --start — task comes from the branch
    check("--red works with no --start (task derived from branch)", r.returncode == 0)
    check("red-log keyed by the branch task",
          (gb / "spec" / "10-delivery" / "verification" / ".gate" / "red" / "T-021.json").is_file())
    r = run_hook(gb, "Write", {"file_path": str(bsrc), "content": "x"})
    check("src edit allowed after branch-derived red-log", r.returncode == 0)

    # --- a real task branch beats a stale --start pointer -------------------------------
    run_sub(gb, "--start", "T-999")                       # stale/wrong explicit pointer
    r = run_sub(gb, "--red", "--test", "false")           # should still record under T-021 (the branch)
    check("branch task overrides a stale --start pointer",
          (gb / "spec" / "10-delivery" / "verification" / ".gate" / "red" / "T-021.json").is_file())

    # --- two parallel worktrees on different branches don't clobber ---------------------
    # (each worktree has its own local .gate/; the branch keys the red-log — simulate with 2 repos)
    wa = mkgitproject("task/T-030-a")
    wb = mkgitproject("task/T-031-b")
    run_sub(wa, "--red", "--test", "false")
    run_sub(wb, "--red", "--test", "false")
    # A's edit needs A's red-log; it must NOT be unblocked by B's, and vice-versa
    ra = run_hook(wa, "Write", {"file_path": str(wa / "src" / "a.py"), "content": "x"})
    rb = run_hook(wb, "Write", {"file_path": str(wb / "src" / "b.py"), "content": "x"})
    check("parallel worktree A enforces its own task", ra.returncode == 0)
    check("parallel worktree B enforces its own task", rb.returncode == 0)
    check("worktree A red-log is A's task only",
          (wa / "spec/10-delivery/verification/.gate/red/T-030.json").is_file()
          and not (wa / "spec/10-delivery/verification/.gate/red/T-031.json").is_file())

    # --- installer: fresh settings.json -------------------------------------------------
    fresh = Path(tempfile.mkdtemp())
    (fresh / "spec").mkdir()
    r = subprocess.run([sys.executable, str(INSTALL), str(fresh)], capture_output=True, text=True)
    s = json.loads((fresh / ".claude" / "settings.json").read_text())
    blocks = s["hooks"]["PreToolUse"]
    check("installer wrote a PreToolUse block", any(b.get("_source") == "grillspec-exec-gate" for b in blocks))
    check("installer vendored gate_exec.py", (fresh / ".claude" / "tools" / "gate_exec.py").is_file())
    check("installer vendored check_task_record.py",
          (fresh / ".claude" / "tools" / "check_task_record.py").is_file())

    # --- installer refuses to wire a hook it can't back with a script (anti-brick) -------
    isolated = Path(tempfile.mkdtemp())          # a copy of the installer with NO sibling gate_exec.py
    (isolated / "spec").mkdir()
    lone = isolated / "lonely_install.py"
    lone.write_text(INSTALL.read_text())
    r = subprocess.run([sys.executable, str(lone), str(isolated)], capture_output=True, text=True)
    check("installer refuses when gate_exec.py is unavailable", r.returncode == 1)
    check("no settings.json written on refusal",
          not (isolated / ".claude" / "settings.json").is_file())

    # --- installer is idempotent --------------------------------------------------------
    subprocess.run([sys.executable, str(INSTALL), str(fresh)], capture_output=True, text=True)
    s = json.loads((fresh / ".claude" / "settings.json").read_text())
    n = sum(1 for b in s["hooks"]["PreToolUse"] if b.get("_source") == "grillspec-exec-gate")
    check("installer is idempotent (one block)", n == 1)

    # --- installer preserves an existing unrelated hook + key ---------------------------
    pre = Path(tempfile.mkdtemp())
    (pre / "spec").mkdir()
    (pre / ".claude").mkdir()
    (pre / ".claude" / "settings.json").write_text(json.dumps({
        "model": "opus",
        "hooks": {"PreToolUse": [{"matcher": "Bash", "hooks": [{"type": "command", "command": "echo hi"}]}]},
    }))
    subprocess.run([sys.executable, str(INSTALL), str(pre)], capture_output=True, text=True)
    s = json.loads((pre / ".claude" / "settings.json").read_text())
    check("installer preserved unrelated key", s.get("model") == "opus")
    check("installer preserved unrelated hook",
          any(b.get("matcher") == "Bash" for b in s["hooks"]["PreToolUse"]))
    check("installer added our block alongside",
          any(b.get("_source") == "grillspec-exec-gate" for b in s["hooks"]["PreToolUse"]))

    print("\n%d passed, %d failed" % (PASS, FAIL))
    return 1 if FAIL else 0


if __name__ == "__main__":
    sys.exit(main())
