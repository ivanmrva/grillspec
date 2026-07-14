#!/usr/bin/env python3
"""Regression test: the auxiliary standalone emitter produces a portable dual-host plugin."""
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent


def main():
    with tempfile.TemporaryDirectory(prefix="grillspec_emit_") as td:
        root = Path(td)
        installed = root / "plugin"
        shutil.copytree(HERE.parent, installed, ignore=shutil.ignore_patterns("__pycache__"))
        emitter = installed / "tools" / "emit-standalone.py"
        out = root / "bundle"
        result = subprocess.run(
            [sys.executable, str(emitter), "--public", "--out", str(out),
             "grill-ddd", "implement-task"],
            capture_output=True, text=True)
        if result.returncode:
            print(result.stdout + result.stderr)
            return 1

        claude = json.loads((out / ".claude-plugin" / "plugin.json").read_text())
        codex = json.loads((out / ".codex-plugin" / "plugin.json").read_text())
        assert claude["name"] == codex["name"] == "grill-spec-bundle"
        assert codex["skills"] == "./skills/"
        assert (out / "skills/grill-ddd/references/grill-engine.md").is_file()
        assert (out / "skills/grill-ddd/agents/openai.yaml").is_file()
        assert (out / "skills/implement-task/scripts/install_exec_gates.py").is_file()
        for path in out.rglob("*.md"):
            assert "${CLAUDE_PLUGIN_ROOT}" not in path.read_text(encoding="utf-8")

        # The marketplace carries already-portable skills beside this emitter. Re-emitting one must
        # preserve its Codex policy metadata and remain portable without the source-only build tree.
        shutil.rmtree(installed / "skills" / "implement-task")
        shutil.copytree(out / "skills" / "implement-task",
                        installed / "skills" / "implement-task")
        second = root / "rebundled"
        result = subprocess.run(
            [sys.executable, str(emitter), "--public", "--out", str(second),
             "implement-task"], capture_output=True, text=True)
        assert result.returncode == 0, result.stdout + result.stderr
        first_policy = (out / "skills/implement-task/agents/openai.yaml").read_text()
        second_policy = (second / "skills/implement-task/agents/openai.yaml").read_text()
        assert first_policy == second_policy
        for path in second.rglob("*.md"):
            assert "${CLAUDE_PLUGIN_ROOT}" not in path.read_text(encoding="utf-8")
        print("standalone emitter dual-host regression: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
