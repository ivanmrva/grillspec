#!/usr/bin/env python3
"""Regression tests for the neutral project-state and canonical-guide invariants."""
import json
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
GUARD = HERE / "guard_derived.py"
FRESHNESS = HERE / "check_freshness.py"
PASS = FAIL = 0


def run(tool, root, *args):
    return subprocess.run([sys.executable, str(tool), *args], cwd=root,
                          capture_output=True, text=True)


def check(name, condition, detail=""):
    global PASS, FAIL
    if condition:
        PASS += 1
        print("  ok   " + name)
    else:
        FAIL += 1
        print("  FAIL " + name)
        if detail:
            print("       " + detail.replace("\n", "\n       "))


def write(root, rel, text):
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def main():
    with tempfile.TemporaryDirectory(prefix="grillspec_state_") as td:
        root = Path(td)
        write(root, "AGENTS.md", "# Project guide\n\nRun the tests.\n")
        write(root, "CLAUDE.md", "@AGENTS.md\n")
        write(root, "spec/05-functional-spec/use-cases.md", "AC-001 does the thing.\n")
        result = run(GUARD, root, "--record")
        lock = root / ".grillspec" / "derived.lock"
        check("derived lock is written under .grillspec", result.returncode == 0 and lock.is_file(),
              result.stdout + result.stderr)
        check("derived lock contains both project guides",
              set(json.loads(lock.read_text(encoding="utf-8"))) >= {"AGENTS.md", "CLAUDE.md"})
        check("guard never creates legacy .claude state", not (root / ".claude").exists())

        write(root, "CLAUDE.md", "# copied guide\n\nRun the tests.\n")
        result = run(GUARD, root, "--record")
        check("duplicate CLAUDE guide is rejected",
              result.returncode == 1 and "must contain only @AGENTS.md" in result.stdout,
              result.stdout + result.stderr)

    with tempfile.TemporaryDirectory(prefix="grillspec_legacy_") as td:
        root = Path(td)
        write(root, "AGENTS.md", "# Project guide\n")
        write(root, "CLAUDE.md", "@AGENTS.md\n")
        write(root, ".claude/derived.lock", "{}\n")
        result = run(GUARD, root)
        check("legacy .claude derived lock is not a fallback",
              result.returncode == 1 and "UNREGISTERED" in result.stdout,
              result.stdout + result.stderr)

    with tempfile.TemporaryDirectory(prefix="grillspec_guides_missing_") as td:
        root = Path(td)
        write(root, "spec/10-delivery/conventions/workflow.md", "# Workflow\n")
        result = run(GUARD, root, "--record")
        check("a derived conventions area requires both guide entry points",
              result.returncode == 1 and "AGENTS.md" in result.stdout and "CLAUDE.md" in result.stdout,
              result.stdout + result.stderr)

    with tempfile.TemporaryDirectory(prefix="grillspec_freshness_") as td:
        root = Path(td)
        write(root, "spec/04-domain/ddd/model.md", "UC-001 original behavior\n")
        write(root, "spec/05-functional-spec/use-cases.md", "AC-001 realizes UC-001\n")
        result = run(FRESHNESS, root, "--record")
        lock = root / ".grillspec" / "freshness.lock"
        check("freshness lock is written under .grillspec",
              result.returncode == 0 and lock.is_file(), result.stdout + result.stderr)
        check("freshness never creates legacy .claude state", not (root / ".claude").exists())
        write(root, "spec/04-domain/ddd/model.md", "UC-001 changed behavior\n")
        result = run(FRESHNESS, root, "--strict")
        check("neutral freshness lock still detects upstream drift",
              result.returncode == 1 and "STALE CANDIDATES" in result.stdout,
              result.stdout + result.stderr)

    with tempfile.TemporaryDirectory(prefix="grillspec_freshness_legacy_") as td:
        root = Path(td)
        write(root, "spec/04-domain/ddd/model.md", "UC-001 behavior\n")
        write(root, ".claude/freshness.lock", "{}\n")
        result = run(FRESHNESS, root)
        check("legacy .claude freshness lock is not a fallback",
              result.returncode == 0 and "no .grillspec/freshness.lock" in result.stdout,
              result.stdout + result.stderr)

    print("\n%d passed, %d failed" % (PASS, FAIL))
    return 1 if FAIL else 0


if __name__ == "__main__":
    sys.exit(main())
