#!/usr/bin/env python3
"""Regression tests for the neutral project-state and canonical-guide invariants."""
import json
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
CONFIG = HERE / "project_config.py"
LINT = HERE / "lint_spec.py"
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
        result = run(CONFIG, root)
        check("no settings file -> the widest reading (regulated + pr)",
              result.returncode == 0 and "profile: regulated" in result.stdout and "delivery: pr" in result.stdout,
              result.stdout + result.stderr)
        check("reading never creates project state", not (root / ".grillspec").exists())

        result = run(CONFIG, root, "--set", "profile=standard", "--set", "delivery=trunk")
        settings = root / ".grillspec" / "project.json"
        check("settings are written under .grillspec", result.returncode == 0 and settings.is_file(),
              result.stdout + result.stderr)
        check("settings carry both keys",
              json.loads(settings.read_text(encoding="utf-8")) == {"delivery": "trunk", "profile": "standard"})
        check("settings never create host-specific state",
              not (root / ".claude").exists() and not (root / ".codex").exists())

        result = run(CONFIG, root, "--json")
        check("--json reports the effective settings",
              json.loads(result.stdout) == {"delivery": "trunk", "explicit": True, "profile": "standard"},
              result.stdout + result.stderr)

        result = run(CONFIG, root, "--set", "profile=enterprise")
        check("an unknown profile is rejected", result.returncode == 2 and "must be one of" in result.stdout,
              result.stdout + result.stderr)
        check("a rejected value leaves the file unchanged",
              json.loads(settings.read_text(encoding="utf-8"))["profile"] == "standard")

        write(root, ".grillspec/project.json", "{not json")
        result = run(CONFIG, root)
        check("an unreadable settings file falls back to the defaults",
              result.returncode == 0 and "profile: regulated" in result.stdout, result.stdout + result.stderr)

    with tempfile.TemporaryDirectory(prefix="grillspec_guide_") as td:
        root = Path(td)
        write(root, "spec/04-domain/ddd/a.md",
              "<!-- scope: x | excludes: y | format: z -->\n| ID | Name |\n|---|---|\n| AGG-1 | Order |\n")
        write(root, "AGENTS.md", "# Project guide\n\nRun the tests.\n")
        write(root, "CLAUDE.md", "@AGENTS.md\n")
        result = run(LINT, root, "spec")
        check("import-only CLAUDE.md passes", "CLAUDE.md must contain only" not in result.stdout,
              result.stdout + result.stderr)

        write(root, "CLAUDE.md", "# copied guide\n\nRun the tests.\n")
        result = run(LINT, root, "spec")
        check("a duplicated CLAUDE guide is rejected",
              result.returncode == 1 and "CLAUDE.md must contain only @AGENTS.md" in result.stdout,
              result.stdout + result.stderr)

        (root / "CLAUDE.md").unlink()
        result = run(LINT, root, "spec")
        check("AGENTS.md alone is fine", "CLAUDE.md must contain only" not in result.stdout,
              result.stdout + result.stderr)

    print("\n%d passed, %d failed" % (PASS, FAIL))
    return 1 if FAIL else 0


if __name__ == "__main__":
    sys.exit(main())
