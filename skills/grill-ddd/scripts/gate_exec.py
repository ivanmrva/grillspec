#!/usr/bin/env python3
"""Exec-loop process gate — a PROJECT-LOCAL Claude Code/Codex PreToolUse hook.

This is the tool-call-time sibling of the commit-time `spec_governance_hook.sh`. The commit/CI
checkers verify the END STATE of a task; this gate verifies the ORDER of the work WHILE it happens,
which is the only thing a commit-time check structurally cannot see (exec-engine.md: "Temporal order
on its own can't be proven after the fact"). It enforces three transitions of the per-task loop:

  1. RED-before-GREEN — a production-tree edit (`src/**`, non-test) is blocked while a task is active
     UNLESS a real failing-test run was recorded for that task. Kills the "skip the tests / write all
     the code, back-fill tests after" batching the engine forbids.
  2. No hollow done-claim — an edit that flips a task's `status:` to `done` is blocked unless
     `check_task_record.py --task T-NNN` is already green. Promotes the existing commit-time check to
     the moment the claim is made, instead of discovering it at commit.
  3. No cheat at the keystroke — an edit that INTRODUCES a skip/xfail/.only marker into a test file,
     or a mock-library import / Fake*-double definition into the production tree, is blocked the
     moment it is written. This is the edit-time twin of `check_no_skips.py` + `check_no_fakes.py`:
     the commit-time tripwires catch the end state, but mid-task is where the rationalization happens
     ("the broker isn't ready, skip the test for now") and by commit time code is built on top of it.
     Unlike gates 1-2 it needs NO active task — the cheat is wrong at any time, including setup/
     bootstrap work before the first task branch. Only newly-introduced lines trigger it; a line
     carrying the inline waiver (`no-skips: allow …` / `no-fakes: allow …`) passes.

It is PROJECT-LOCAL: the walking-skeleton vendors it once under `.grillspec/tools/`, then wires it
into THIS repo's `.claude/settings.json` and/or `.codex/hooks.json` (see `install_exec_gates.py`),
like the git pre-commit hook in `.git/hooks/`.
It is NOT a global hook and never fires on other projects or the user's `~/.claude` config.

  Fail-OPEN by design: any internal error allows the tool call (a bug in the gate must never brick the
  user's ability to edit). It DENIES (exit 2) only on a clean, intended gate violation.
  Emergency override: set GRILLSPEC_GATE_OFF=1 (the tool-call analogue of `git commit --no-verify`).

The active task is derived from the **git branch** (`task/T-NNN-…`, which the engineering workflow
already mandates per task). That makes the gate **parallel-safe**: an AFK wave runs each task in its
own branch/worktree, so nothing shares a pointer to clobber, and each worktree's `.grillspec/gate/` is local
(git-ignored, never carried between worktrees). `--start` writes an explicit pointer only as a
fallback for flows that don't branch-per-task; a stale pointer can't override a real task branch.

Subcommands the exec loop calls (the engine instructs it; the gate enforces it):
  --red   --test "<cmd>" --covers "AC-NNN ..."
                             run <cmd>, REQUIRE it to fail, record the red-log for the active task.
                             --covers names the spec ID(s) this failing test drives and each must exist
                             under spec/ - the mechanical edge of "chat is spec input, not code input":
                             an ad-hoc mid-task instruction gets its ID minted/amended in the owning
                             spec area FIRST, which makes the spec update a hard precondition of the
                             code change instead of a follow-up promise. (Opt out for a project via
                             `"red_requires_covers": false` in .grillspec/grillspec-gate.json.)
  --start T-NNN              (fallback) set the active task when NOT on a `task/T-NNN` branch
  --done  [T-NNN]            clear the explicit pointer (no-op when the branch is the signal)
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

# ---- gate-3 content tripwires (the edit-time twins of check_no_skips.py / check_no_fakes.py — keep the
# ---- pattern cores in sync with those tools; this is the high-precision ERROR subset only, never the WARNs,
# ---- because a PreToolUse deny is disruptive and must fire only on the unambiguous cheat).
SKIP_NEW = re.compile(
    r"\b(?:it|test|describe|context|suite)\s*\.\s*(?:skip|only|fixme|failing)\s*\(|"
    r"(?<![.\w])[xf](?:it|describe|context)\s*\(|(?<![.\w])xtest\s*\(|\bthis\.skip\s*\(|"
    r"pytest\.mark\.(?:skip|skipif|xfail)|\bpytest\.(?:skip|xfail|importorskip)\s*\(|"
    r"@unittest\.skip|@skip(?:If|Unless)?\s*\(|\bskipTest\s*\(|"
    r"\b[tb]\.Skip(?:f|Now)?\s*\(|#\[\s*ignore|@(?:Disabled|Ignore)\b|"
    r"\[\s*Ignore\s*[\]\(]|\bSkip\s*=\s*\"|->markTestSkipped\s*\(")
FAKE_NEW = re.compile(
    r"\b(?:class|def|func|function|type|interface|struct|record|object|trait)\s+"
    r"(?:(?:Fake|Stub|Mock|Dummy)[A-Z0-9_]\w*|(?:fake|stub|mock|dummy)_\w+)\b|"
    r"\b(?:unittest\.mock|from\s+mock\b|import\s+mock\b|sinon|testdouble|@?jest|nock|"
    r"org\.mockito|mockito|easymock|moq|nsubstitute|fakeiteasy|gomock|golang/mock|testify/mock|mockk)\b")
# camel-case test names are case-SENSITIVE (a production `Latest.java` must stay gated as production)
TEST_NAME = re.compile(r"^test_|_test\.|\.test\.|\.spec\.|_spec\.", re.I)
CAMEL_TEST = re.compile(r"[a-z0-9](?:Test|Tests|Spec|Specs)\.\w+$")


def project_root() -> Path:
    env = os.environ.get("GRILLSPEC_PROJECT_DIR") or os.environ.get("CLAUDE_PROJECT_DIR")
    if env and Path(env).is_dir():
        return Path(env)
    try:
        out = subprocess.run(["git", "rev-parse", "--show-toplevel"],
                             capture_output=True, text=True, check=True)
        return Path(out.stdout.strip())
    except Exception:
        return Path.cwd()


def gate_dir(root: Path) -> Path:
    return root / ".grillspec" / "gate"


def ensure_gate_dir(root: Path) -> Path:
    """mkdir the gate dir and make it self-ignoring — the active-task pointer and red-logs are
    transient per-session build state, never committed (and they'd churn/conflict if they were)."""
    g = gate_dir(root)
    g.mkdir(parents=True, exist_ok=True)
    gi = g / ".gitignore"
    if not gi.is_file():
        gi.write_text("# transient exec-gate state — not version-controlled\n*\n")
    return g


def config(root: Path) -> dict:
    p = root / ".grillspec" / "grillspec-gate.json"
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


def branch_task(root: Path):
    """The active task derived from the current git branch (`task/T-NNN-…`). This is the PRIMARY
    signal because it is **parallel-safe**: AFK runs each task in its own branch/worktree, so the
    branch identifies the task with no shared pointer to clobber — and a worktree's `.grillspec/gate/` is local
    (it's git-ignored, so it never travels between worktrees). Returns None off a task branch."""
    try:
        out = subprocess.run(["git", "-C", str(root), "rev-parse", "--abbrev-ref", "HEAD"],
                             capture_output=True, text=True, check=True)
    except Exception:
        return None
    m = re.search(r"T-\d+", out.stdout.strip())
    return m.group(0) if m else None


def active_task(root: Path):
    """Branch-derived task first (parallel-safe), then an explicit `--start` pointer as a fallback for
    flows that don't branch-per-task. A stale pointer can't override a real task branch."""
    bt = branch_task(root)
    if bt:
        return bt
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
    g = ensure_gate_dir(root)
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


SPEC_ID = re.compile(r"^[A-Z]{1,8}-[A-Za-z0-9][A-Za-z0-9._-]*$")


def missing_in_spec(root: Path, tokens: list) -> list:
    """The given spec-ID tokens that appear NOWHERE under spec/ — unknown IDs. Fail-open: an unreadable
    file is skipped; no spec/ tree at all returns [] (nothing to validate against)."""
    spec = root / "spec"
    if not spec.is_dir():
        return []
    missing = set(tokens)
    pats = {t: re.compile(r"(?<![A-Za-z0-9-])" + re.escape(t) + r"(?![A-Za-z0-9_-])") for t in tokens}
    for p in sorted(spec.rglob("*")):
        if not missing:
            break
        if not p.is_file() or p.suffix.lower() not in (".md", ".yaml", ".yml", ".json"):
            continue
        try:
            txt = p.read_text(encoding="utf-8", errors="replace")
        except Exception:
            continue
        for t in list(missing):
            if pats[t].search(txt):
                missing.discard(t)
    return sorted(missing)


def cmd_red(test_cmd: str, covers: str) -> int:
    """Run the test command, REQUIRE it to fail, then record the red-log for the active task.

    A red-log written only after a real non-zero (failing) test run is what makes the RED gate mean
    'a failing test was actually seen', not 'the model asserted it ran one'. The --covers check is the
    drift tripwire at the earliest possible moment: before any code exists, the failing test must name
    the spec ID(s) that demand it — and they must exist — so an ad-hoc mid-task instruction is forced
    through the spec (mint/amend the ID first) instead of straight into the code."""
    root = project_root()
    task = active_task(root)
    if not task:
        print("gate --red: no active task — call `--start T-NNN` first", file=sys.stderr)
        return 1
    if not test_cmd:
        print("gate --red: pass the failing-test command via --test \"...\"", file=sys.stderr)
        return 1
    tokens = [t for t in re.split(r"[,\s]+", covers or "") if t]
    if config(root).get("red_requires_covers", True):
        if not tokens:
            print("gate --red: name the spec ID(s) this failing test drives via --covers \"AC-NNN …\".\n"
                  "Chat is spec input, not code input: a behavior with no driving spec ID — an ad-hoc\n"
                  "mid-task instruction included — gets its ID minted or amended in the owning spec area\n"
                  "FIRST, then the tagged failing test, then the code. A pure refactor or spike needs no\n"
                  "red at all (GRILLSPEC_GATE_OFF=1 for the sanctioned non-TDD edit); a project can opt\n"
                  "out via `\"red_requires_covers\": false` in .grillspec/grillspec-gate.json.",
                  file=sys.stderr)
            return 1
        bad = [t for t in tokens if not SPEC_ID.match(t)]
        if bad:
            print("gate --red: --covers takes bare spec IDs like AC-012 (uppercase type prefix) — not: %s"
                  % ", ".join(bad), file=sys.stderr)
            return 1
        unknown = missing_in_spec(root, tokens)
        if unknown:
            print("gate --red: %s exist(s) nowhere under spec/ — a failing test may only be driven by a\n"
                  "LIVE spec ID. If this behavior came from an ad-hoc instruction, that instruction is\n"
                  "spec input: mint or amend the ID in its owning spec area (and the task's manifest\n"
                  "cell) first, then re-run. Never invent an ID to appease the gate."
                  % ", ".join(unknown), file=sys.stderr)
            return 1
    proc = subprocess.run(test_cmd, shell=True, cwd=root, capture_output=True, text=True)
    if proc.returncode == 0:
        print("gate --red: that test command PASSED (exit 0) — RED needs a test that FAILS for the "
              "right reason before you write the code. Write the failing test first.", file=sys.stderr)
        return 1
    g = ensure_gate_dir(root)
    (g / "red").mkdir(parents=True, exist_ok=True)
    (g / "red" / (task + ".json")).write_text(json.dumps({
        "task": task, "test_cmd": test_cmd, "covers": tokens, "recorded_at": now_iso(),
        "exit_code": proc.returncode,
    }, indent=2) + "\n")
    print("gate --red: recorded failing test for %s%s — src/** edits for this task are now unblocked."
          % (task, (" (covers %s)" % ", ".join(tokens)) if tokens else ""))
    return 0


# ---- the PreToolUse hook entrypoint ----------------------------------------------------

def deny(reason: str) -> int:
    print("grillspec exec-gate: " + reason, file=sys.stderr)
    return 2


def codex_patch_edits(command: str, root: Path) -> list:
    """Translate Codex `apply_patch` input into the edit shape used by the Claude hook path.

    Codex sends one patch command that may touch several files. Only added lines participate in the
    skip/fake/done checks, while every touched production path participates in RED-before-GREEN.
    """
    edits = []
    current = None
    added = []

    def flush():
        nonlocal current, added
        if current:
            path = Path(current)
            if not path.is_absolute():
                path = root / path
            edits.append((str(path), {
                "old_string": "",
                "new_string": "\n".join(added),
                "_codex_patch": True,
            }))
        current, added = None, []

    for line in (command or "").splitlines():
        match = re.match(r"^\*\*\* (?:Add|Update|Delete) File: (.+?)\s*$", line)
        if match:
            flush()
            current = match.group(1).strip()
            continue
        if current and line.startswith("+") and not line.startswith("+++"):
            added.append(line[1:])
    flush()
    return edits


def normalized_edits(payload: dict, root: Path) -> list:
    """Return `(absolute file path, Claude-shaped tool input)` entries for either host."""
    tool_input = payload.get("tool_input", {}) or {}
    if payload.get("tool_name") == "apply_patch" and isinstance(tool_input.get("command"), str):
        return codex_patch_edits(tool_input["command"], root)
    file_path = tool_input.get("file_path", "") or ""
    return [(file_path, tool_input)] if file_path else []


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


def is_test_path(file_path: str) -> bool:
    norm = "/" + os.path.abspath(file_path or "").replace(os.sep, "/").lstrip("/")
    name = os.path.basename(norm)
    return any(m in norm for m in TEST_MARKERS) or bool(TEST_NAME.search(name)) or bool(CAMEL_TEST.search(name))


def introduced_lines(tool_input: dict, file_path: str) -> list:
    """The lines this Write/Edit/MultiEdit INTRODUCES — a line-set diff against the text it replaces,
    so editing near a pre-existing (possibly waived) marker never re-triggers the gate."""
    if "content" in tool_input:                                  # Write: diff against the on-disk file
        old = ""
        try:
            p = Path(file_path)
            if file_path and p.is_file():
                old = p.read_text(encoding="utf-8", errors="replace")
        except Exception:
            old = ""
        seen = set(old.splitlines())
        return [l for l in (tool_input.get("content", "") or "").splitlines() if l not in seen]
    edits = tool_input.get("edits") if isinstance(tool_input.get("edits"), list) else [tool_input]
    out = []
    for e in edits:                                              # Edit / MultiEdit: diff new vs old string
        seen = set((e.get("old_string", "") or "").splitlines())
        out.extend(l for l in (e.get("new_string", "") or "").splitlines() if l not in seen)
    return out


def content_violation(root: Path, tool_input: dict, file_path: str):
    """Gate 3 — the reason string when this edit introduces a test-skip into a test file or a
    fake/mock-import into the production tree; None when clean. Comment-only lines are ignored for
    the production check (a comment MENTIONING a mock library is not an import)."""
    lines = introduced_lines(tool_input, file_path)
    if not lines:
        return None
    if is_test_path(file_path):
        for l in lines:
            if ("no-skips: allow" not in l) and SKIP_NEW.search(l):
                return ("this edit introduces a skip/only/xfail/disable marker into a test file:\n"
                        "    %s\n"
                        "A skipped test reads green while asserting nothing, and .only silently shrinks "
                        "the suite. If the dependency isn't ready, let the test FAIL — red is the "
                        "truthful signal — and record the blocker (spec/_human-input.md), or mark the "
                        "task `blocked`. A genuinely legitimate case carries an inline "
                        "`no-skips: allow <reason>`. Override: GRILLSPEC_GATE_OFF=1." % l.strip())
        return None
    if is_production_path(root, file_path):
        for l in lines:
            if l.lstrip().startswith(("#", "//", "*")) or "no-fakes: allow" in l:
                continue
            if FAKE_NEW.search(l):
                return ("this edit introduces a test double / mocking-library import into the "
                        "production tree:\n"
                        "    %s\n"
                        "Production code is production-only from the very first line — doubles live "
                        "under tests/. If the real dependency isn't wired yet, keep the adapter real "
                        "and let its test fail (red is the truthful signal), or mark the task "
                        "`blocked` and escalate. A genuinely legitimate case carries an inline "
                        "`no-fakes: allow <reason>`. Override: GRILLSPEC_GATE_OFF=1." % l.strip())
    return None


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
    edits = normalized_edits(payload, root)
    if not edits:                                                # unsupported input → fail open
        return 0

    for file_path, tool_input in edits:
        # Gate 2 — no hollow done-claim.
        if "verification" in file_path.replace(os.sep, "/") and introduces_done(tool_input):
            tid = task_id_from_path(file_path)
            if tid:
                checker = root / ".grillspec" / "tools" / "check_task_record.py"
                if not checker.is_file():
                    checker = Path(__file__).resolve().parent / "check_task_record.py"
                spec = root / "spec"
                res = subprocess.run([sys.executable, str(checker), str(spec), "--task", tid,
                                      "--assume-done"], capture_output=True, text=True)
                if res.returncode != 0:
                    return deny(
                        "%s is being marked `status: done` but its Verification Record is not green:\n%s\n"
                        "Fill the unmet obligations (tests-first traced · independent VERDICT: PASS · "
                        "no fakes) before claiming done, or override with GRILLSPEC_GATE_OFF=1."
                        % (tid, (res.stdout + res.stderr).strip()))
            continue

        # Gate 3 — no cheat at the keystroke.
        violation = content_violation(root, tool_input, file_path)
        if violation:
            return deny(violation)

        # Gate 1 — RED before GREEN.
        if is_production_path(root, file_path):
            task = active_task(root)
            if not task:
                continue
            red = gate_dir(root) / "red" / (task + ".json")
            if red.is_file():
                continue
            return deny(
                "no failing test recorded for the active task %s — write ONE small failing test for "
                "the next behavior and watch it fail (`python3 %s/tools/gate_exec.py --red --test "
                "\"<your test command>\" --covers \"<the spec IDs it drives>\"`) BEFORE writing "
                "production code in %s. This is the red→green micro-cycle; don't batch all code then "
                "back-fill tests. Override: GRILLSPEC_GATE_OFF=1."
                % (task, ".grillspec", os.path.relpath(file_path, root) if file_path else "src/"))
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
        test = covers = ""
        if "--test" in args:
            j = args.index("--test")
            test = args[j + 1] if j + 1 < len(args) else ""
        if "--covers" in args:
            j = args.index("--covers")
            covers = args[j + 1] if j + 1 < len(args) else ""
        return cmd_red(test, covers)
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
