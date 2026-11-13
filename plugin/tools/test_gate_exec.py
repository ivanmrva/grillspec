#!/usr/bin/env python3
"""Behavior tests for the edit-time cheat tripwire + its installer. Run: python3 tools/test_gate_exec.py"""
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


def mkproject():
    d = Path(tempfile.mkdtemp())
    (d / "spec").mkdir(parents=True)
    (d / "spec" / "acceptance.md").write_text("- AC-001 sample criterion\n")   # tracked, so a worktree has spec/
    (d / "src").mkdir()
    return d


def mkgitproject(branch):
    """A git project checked out on `branch`."""
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
    r = run_hook(empty, "Write", {"file_path": str(empty / "tests" / "a.test.js"),
                                  "content": "it.skip('x', () => {})\n"})
    check("no spec/ dir → allow", r.returncode == 0)

    # --- an ordinary production edit is never blocked -------------------------------------
    plain = mkproject()
    r = run_hook(plain, "Write", {"file_path": str(plain / "src" / "a.py"), "content": "print(1)\n"})
    check("ordinary src edit allowed", r.returncode == 0)
    r = run_hook(plain, "Write", {"file_path": str(plain / "spec" / "10-delivery" / "tasks" / "T-002.md"),
                                  "content": "| status | done |\n"})
    check("spec edits are not the hook's business", r.returncode == 0)
    check("the hook keeps no state in the project", not (plain / ".grillspec" / "gate").exists())

    # --- the production tree is configured under .grillspec (no host-specific fallback) ---
    configured = mkproject()
    (configured / ".grillspec").mkdir()
    (configured / ".grillspec" / "grillspec-gate.json").write_text(
        json.dumps({"production_globs": ["service/"]}))
    r = run_hook(configured, "Write", {"file_path": str(configured / "service" / "gw.py"),
                                       "content": "class FakeGateway:\n    pass\n"})
    check("shared .grillspec gate config is honored", r.returncode == 2)
    legacy_config = mkproject()
    (legacy_config / ".claude").mkdir()
    (legacy_config / ".claude" / "grillspec-gate.json").write_text(
        json.dumps({"production_globs": ["service/"]}))
    r = run_hook(legacy_config, "Write", {"file_path": str(legacy_config / "service" / "gw.py"),
                                          "content": "class FakeGateway:\n    pass\n"})
    check("legacy .claude gate config is not a fallback", r.returncode == 0)

    # --- the content tripwires: a cheat is denied at the keystroke ----------------------------
    g3 = mkproject()
    tf = g3 / "tests" / "pay.test.js"
    r = run_hook(g3, "Write", {"file_path": str(tf), "content": "it.skip('x', () => {})\n"})
    check("skip marker into a test file → DENIED", r.returncode == 2)
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
    check("installer vendored shared check_task.py",
          (fresh / ".grillspec" / "tools" / "check_task.py").is_file())
    check("installer vendored check_orphan_tests.py + its tier_contract.py helper",
          (fresh / ".grillspec" / "tools" / "check_orphan_tests.py").is_file()
          and (fresh / ".grillspec" / "tools" / "tier_contract.py").is_file())
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

    # --- sibling worktrees: the hook validates the tree being EDITED ----------------------
    # The session env var can point at a SIBLING worktree of the same repo; the file the hooked call
    # touches decides which project is checked.
    wt_a = mkgitproject("main-line")                         # env points HERE: default production tree
    wt_b = Path(tempfile.mkdtemp()).resolve() / "sibling"    # ...but the edit lands HERE
    subprocess.run(["git", "worktree", "add", "-q", "-b", "side", str(wt_b)],
                   cwd=wt_a, capture_output=True, text=True)
    check("sibling worktree created", (wt_b / "spec").is_dir())
    (wt_b / ".grillspec").mkdir(exist_ok=True)
    (wt_b / ".grillspec" / "grillspec-gate.json").write_text(json.dumps({"production_globs": ["service/"]}))
    r = run_hook(wt_a, "Write", {"file_path": str(wt_b / "service" / "gw.py"),
                                 "content": "class FakeGateway:\n    pass\n"})
    check("sibling worktree: the edited tree's config governs, not the env var's", r.returncode == 2)
    r = run_hook(wt_a, "Write", {"file_path": str(wt_b / "service" / "new" / "deep" / "gw.py"),
                                 "content": "class FakeGateway:\n    pass\n"})
    check("anchor resolves through a not-yet-created directory", r.returncode == 2)
    subprocess.run(["git", "worktree", "remove", "--force", str(wt_b)], cwd=wt_a, capture_output=True)

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
