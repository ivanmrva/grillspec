#!/usr/bin/env python3
"""Edit-time cheat tripwire - a PROJECT-LOCAL Claude Code/Codex PreToolUse hook.

The commit-time checkers catch a skipped test or a fake in the shipping tree after the fact; by then code
is usually built on top of it. This hook catches the same two things at the moment they are written:

  - a test edit that INTRODUCES a skip / xfail / `.only` marker (the edit-time twin of check_no_skips.py);
  - a production-tree edit that INTRODUCES a mock-library import or a Fake*/Stub* double (the edit-time
    twin of check_no_fakes.py).

Only newly introduced lines trigger it; a line carrying the inline waiver (`no-skips: allow <why>` /
`no-fakes: allow <why>`) passes. It keeps no state and knows nothing about tasks or branches.

It is PROJECT-LOCAL: `install_exec_gates.py` vendors it once under `.grillspec/tools/` and wires it into
THIS repo's `.claude/settings.json` and/or `.codex/hooks.json`. It is never a global hook.

  Fail-OPEN by design: any internal error allows the tool call (a bug here must never brick editing).
  It DENIES (exit 2) only on a clean, intended violation.
  Emergency override: set GRILLSPEC_GATE_OFF=1 (the tool-call analogue of `git commit --no-verify`).

Usage:
  --hook      PreToolUse entrypoint: reads the hook JSON on stdin, allow(0)/deny(2)
"""
import json
import os
import re
import subprocess
import sys
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


def project_root(anchor=None) -> Path:
    """Root of the tree being VALIDATED. Precedence: (1) the repository containing `anchor` —
    the file the hooked tool call touches; a session env var may point at a SIBLING worktree of
    the same repo, and validating that tree reads another checkout's gate state (a legitimate
    `status: done` then false-denies against a stale record); (2) GRILLSPEC_PROJECT_DIR /
    CLAUDE_PROJECT_DIR; (3) git toplevel of CWD; (4) CWD. CLI subcommands pass no anchor —
    they run from the project cwd, where the env/cwd fallback is the correct behaviour."""
    if anchor:
        d = Path(anchor)
        if not d.is_dir():                                       # a Write may target a file — or a
            d = d.parent                                         # directory — that doesn't exist yet,
        while not d.is_dir() and d != d.parent:                  # so climb to the first real ancestor
            d = d.parent
        try:
            out = subprocess.run(["git", "-C", str(d), "rev-parse", "--show-toplevel"],
                                 capture_output=True, text=True, check=True)
            return Path(out.stdout.strip())
        except Exception:
            pass
    env = os.environ.get("GRILLSPEC_PROJECT_DIR") or os.environ.get("CLAUDE_PROJECT_DIR")
    if env and Path(env).is_dir():
        return Path(env)
    try:
        out = subprocess.run(["git", "rev-parse", "--show-toplevel"],
                             capture_output=True, text=True, check=True)
        return Path(out.stdout.strip())
    except Exception:
        return Path.cwd()


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
    # anchor on the file this call actually touches — see project_root(). (Codex `apply_patch`
    # carries no file_path; it falls back to env/cwd, as before.)
    ti = payload.get("tool_input") or {}
    root = project_root(ti.get("file_path") or ti.get("notebook_path"))
    if not (root / "spec").is_dir():                             # not a grillspec project → no-op
        return 0
    edits = normalized_edits(payload, root)
    if not edits:                                                # unsupported input → fail open
        return 0

    for file_path, tool_input in edits:
        violation = content_violation(root, tool_input, file_path)
        if violation:
            return deny(violation)
    return 0


def main() -> int:
    if "--hook" in sys.argv[1:]:
        return cmd_hook()
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
