#!/usr/bin/env python3
"""Behavior tests for the exec-loop gate + its installer. Run: python3 tools/test_gate_exec.py"""
import json
import os
import shutil
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
          (p / ".grillspec" / "gate" / "red" / "T-007.json").is_file())
    check("gate dir self-ignores (transient state not committed)",
          (p / ".grillspec" / "gate" / ".gitignore").read_text().strip().endswith("*"))
    r = run_hook(p, "Write", {"file_path": str(src), "content": "print(1)"})
    check("src edit allowed after red-log", r.returncode == 0)

    # --- override env bypasses the gate -------------------------------------------------
    p2 = mkproject()
    run_sub(p2, "--start", "T-009")
    r = run_hook(p2, "Write", {"file_path": str(p2 / "src" / "b.py"), "content": "x"},
                 env_extra={"GRILLSPEC_GATE_OFF": "1"})
    check("GRILLSPEC_GATE_OFF bypasses RED gate", r.returncode == 0)

    # --- gate configuration is shared under .grillspec (no host-specific fallback) ------
    configured = mkproject()
    (configured / ".grillspec").mkdir()
    (configured / ".grillspec" / "grillspec-gate.json").write_text(
        json.dumps({"production_globs": ["service/"]}))
    run_sub(configured, "--start", "T-010")
    r = run_hook(configured, "Write",
                 {"file_path": str(configured / "service" / "api.py"), "content": "x"})
    check("shared .grillspec gate config is honored", r.returncode == 2)

    legacy_config = mkproject()
    (legacy_config / ".claude").mkdir()
    (legacy_config / ".claude" / "grillspec-gate.json").write_text(
        json.dumps({"production_globs": ["service/"]}))
    run_sub(legacy_config, "--start", "T-011")
    r = run_hook(legacy_config, "Write",
                 {"file_path": str(legacy_config / "service" / "api.py"), "content": "x"})
    check("legacy .claude gate config is not a fallback", r.returncode == 0)

    # --- Codex apply_patch payload: same RED gate, including multi-file normalization ---
    patch = """*** Begin Patch
*** Update File: src/b.py
@@
+print('production')
*** End Patch"""
    r = run_hook(p2, "apply_patch", {"command": patch})
    check("Codex apply_patch + active task + no red-log → DENIED", r.returncode == 2)
    check("Codex deny message points at shared gate", ".grillspec/tools/gate_exec.py" in r.stderr)

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
          (gb / ".grillspec" / "gate" / "red" / "T-021.json").is_file())
    r = run_hook(gb, "Write", {"file_path": str(bsrc), "content": "x"})
    check("src edit allowed after branch-derived red-log", r.returncode == 0)

    # --- a real task branch beats a stale --start pointer -------------------------------
    run_sub(gb, "--start", "T-999")                       # stale/wrong explicit pointer
    r = run_sub(gb, "--red", "--test", "false")           # should still record under T-021 (the branch)
    check("branch task overrides a stale --start pointer",
          (gb / ".grillspec" / "gate" / "red" / "T-021.json").is_file())

    # --- two parallel worktrees on different branches don't clobber ---------------------
    # (each worktree has its own local .grillspec/gate/; branch keys the red-log — simulate with 2 repos)
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
          (wa / ".grillspec/gate/red/T-030.json").is_file()
          and not (wa / ".grillspec/gate/red/T-031.json").is_file())

    # --- gate 3: content tripwires — fire with NO active task (the bootstrap window) -----
    g3 = mkproject()
    tf = g3 / "tests" / "pay.test.js"
    r = run_hook(g3, "Write", {"file_path": str(tf), "content": "it.skip('x', () => {})\n"})
    check("skip marker into a test file → DENIED (no task needed)", r.returncode == 2)
    check("deny message says red is the truthful signal", "truthful signal" in r.stderr)
    r = run_hook(g3, "Write", {"file_path": str(tf), "content": "it('x', () => { expect(1).toBe(1) })\n"})
    check("clean test write allowed", r.returncode == 0)
    r = run_hook(g3, "Edit", {"file_path": str(tf), "old_string": "it('x', () => {",
                              "new_string": "it.only('x', () => {"})
    check(".only introduced by Edit → DENIED", r.returncode == 2)
    r = run_hook(g3, "Write", {"file_path": str(g3 / "tests" / "test_pay.py"),
                               "content": "@pytest.mark.skipif(no_db, reason='db not ready')\ndef test_p(): ...\n"})
    check("pytest skipif into a test file → DENIED", r.returncode == 2)
    r = run_hook(g3, "Write", {"file_path": str(tf),
                               "content": "it.skip('q', () => {}) // no-skips: allow flaky FLK-2\n"})
    check("inline-waived skip line allowed", r.returncode == 0)
    # a PRE-EXISTING skip is not re-triggered by an edit that merely keeps it (line-set diff)
    tf2 = g3 / "tests" / "legacy.test.js"
    tf2.parent.mkdir(parents=True, exist_ok=True)
    tf2.write_text("it.skip('legacy', () => {})\n")
    r = run_hook(g3, "Write", {"file_path": str(tf2),
                               "content": "it.skip('legacy', () => {})\nit('new', () => {})\n"})
    check("rewrite keeping a pre-existing skip → allowed (only NEW lines gate)", r.returncode == 0)
    # production side: a fake/mock-import is denied at the keystroke, comments are not
    ps = g3 / "src" / "gw.py"
    r = run_hook(g3, "Write", {"file_path": str(ps), "content": "class FakeGateway:\n    pass\n"})
    check("Fake* class into src/ → DENIED", r.returncode == 2)
    r = run_hook(g3, "Write", {"file_path": str(ps), "content": "from unittest.mock import MagicMock\n"})
    check("mock import into src/ → DENIED", r.returncode == 2)
    r = run_hook(g3, "Write", {"file_path": str(ps),
                               "content": "# never use unittest.mock here\nclass Gateway:\n    pass\n"})
    check("comment mentioning a mock lib allowed", r.returncode == 0)
    r = run_hook(g3, "Write", {"file_path": str(tf), "content": "it.skip('x', () => {})\n"},
                 env_extra={"GRILLSPEC_GATE_OFF": "1"})
    check("GRILLSPEC_GATE_OFF bypasses the content gate", r.returncode == 0)
    codex_skip = """*** Begin Patch
*** Add File: tests/codex.test.js
+it.skip('codex', () => {})
*** End Patch"""
    r = run_hook(g3, "apply_patch", {"command": codex_skip})
    check("Codex apply_patch skip marker → DENIED", r.returncode == 2)

    # --- installer: fresh settings.json -------------------------------------------------
    fresh = Path(tempfile.mkdtemp())
    (fresh / "spec").mkdir()
    r = subprocess.run([sys.executable, str(INSTALL), str(fresh)], capture_output=True, text=True)
    s = json.loads((fresh / ".claude" / "settings.json").read_text())
    blocks = s["hooks"]["PreToolUse"]
    check("installer wrote a PreToolUse block", any(b.get("_source") == "grillspec-exec-gate" for b in blocks))
    check("installer vendored shared gate_exec.py",
          (fresh / ".grillspec" / "tools" / "gate_exec.py").is_file())
    check("installer vendored shared check_task_record.py",
          (fresh / ".grillspec" / "tools" / "check_task_record.py").is_file())
    check("Claude hook targets shared gate",
          any(h.get("command") == 'python3 "$CLAUDE_PROJECT_DIR/.grillspec/tools/gate_exec.py" --hook'
              for b in blocks for h in b.get("hooks", [])))
    codex_hooks = json.loads((fresh / ".codex" / "hooks.json").read_text())
    check("installer wrote Codex PreToolUse block",
          any(b.get("matcher") == "apply_patch|Edit|Write"
              for b in codex_hooks["hooks"]["PreToolUse"]))
    check("Codex hook targets shared gate",
          any('.grillspec/tools/gate_exec.py' in h.get("command", "")
              for b in codex_hooks["hooks"]["PreToolUse"] for h in b.get("hooks", [])))
    check("installer does not duplicate tools under host state",
          not (fresh / ".claude" / "tools").exists() and not (fresh / ".codex" / "tools").exists())

    # --- installer refuses to wire a hook it can't back with a script (anti-brick) -------
    isolated = Path(tempfile.mkdtemp())          # a copy of the installer with NO sibling gate_exec.py
    (isolated / "spec").mkdir()
    lone = isolated / "lonely_install.py"
    lone.write_text(INSTALL.read_text())
    r = subprocess.run([sys.executable, str(lone), str(isolated)], capture_output=True, text=True)
    check("installer refuses when required gate tools are unavailable", r.returncode == 1)
    check("no settings.json written on refusal",
          not (isolated / ".claude" / "settings.json").is_file())
    check("no Codex hooks.json written on refusal",
          not (isolated / ".codex" / "hooks.json").is_file())
    check("refused install leaves no partial shared tool tree",
          not (isolated / ".grillspec").exists())

    missing_checker = Path(tempfile.mkdtemp())
    shutil.copy2(INSTALL, missing_checker / "install_exec_gates.py")
    shutil.copy2(GATE, missing_checker / "gate_exec.py")
    target = missing_checker / "project"
    target.mkdir()
    r = subprocess.run([sys.executable, str(missing_checker / "install_exec_gates.py"), str(target)],
                       capture_output=True, text=True)
    check("installer refuses a partial source toolset", r.returncode == 1)
    check("partial source toolset writes no host configs",
          not (target / ".claude").exists() and not (target / ".codex").exists())

    # --- installer is idempotent --------------------------------------------------------
    subprocess.run([sys.executable, str(INSTALL), str(fresh)], capture_output=True, text=True)
    s = json.loads((fresh / ".claude" / "settings.json").read_text())
    n = sum(1 for b in s["hooks"]["PreToolUse"] if b.get("_source") == "grillspec-exec-gate")
    check("installer is idempotent (one block)", n == 1)
    s_codex = json.loads((fresh / ".codex" / "hooks.json").read_text())
    codex_n = sum(1 for b in s_codex["hooks"]["PreToolUse"]
                  if any(h.get("command", "").endswith('.grillspec/tools/gate_exec.py\" --hook')
                         for h in b.get("hooks", [])))
    check("Codex installer is idempotent (one block)", codex_n == 1)

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
