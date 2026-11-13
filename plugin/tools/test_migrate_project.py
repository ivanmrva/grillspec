#!/usr/bin/env python3
# test_migrate_project.py - regression tests for migrate_project.py (adopting the current layout in a
# project built with an earlier major version). Stdlib only. Run: python3 tools/test_migrate_project.py
import json, os, subprocess, sys, tempfile, shutil, pathlib

HERE = pathlib.Path(__file__).resolve().parent
TOOL = HERE / "migrate_project.py"
HDR = "<!-- scope: x | excludes: y | format: z -->"
PASS = FAIL = 0

def check(name, cond, detail=""):
    global PASS, FAIL
    if cond: PASS += 1; print("ok    " + name)
    else: FAIL += 1; print("FAIL  " + name + ("\n        " + detail.replace("\n", "\n        ") if detail else ""))

def legacy(d):
    f = {
        "spec/05-functional-spec/uc.md": HDR + "\n| ID | Name |\n|---|---|\n| UC-1 | Pay |\n| AC-1a | paid |\n",
        "spec/10-delivery/tasks/T-001.md": HDR + "\n# T-001\n\n| field | value |\n|---|---|\n| phase | MVP · afk: eligible |\n| behavior | UC-1<br>AC-1a |\n",
        "spec/10-delivery/tasks/T-002.md": HDR + "\n# T-002\n\n| field | value |\n|---|---|\n| phase | MVP · afk: eligible |\n| behavior | UC-1 |\n",
        "spec/10-delivery/tasks/T-003.md": HDR + "\n# T-003\n\n| field | value |\n|---|---|\n| phase | near · afk: eligible |\n| behavior | UC-1 |\n",
        "spec/10-delivery/tasks/T-004.md": HDR + "\n# T-004\n\n| field | value |\n|---|---|\n| phase | MVP |\n| status | blocked — credential |\n",
        "spec/10-delivery/tasks/build-order.md": HDR + "\n| T- | slice |\n|---|---|\n| T-001 | skeleton |\n",
        "spec/10-delivery/verification/tasks/T-001.md": "status: done\ntask: T-001\n| Obligation | Source | Required | Evidence | Status |\n",
        "spec/10-delivery/verification/tasks/T-002.md": "status: in-progress   <!-- note -->\ntask: T-002\n",
        "spec/10-delivery/verification/traceability.md": "| spec ID | T- |\n",
        ".grillspec/derived.lock": "{}\n", ".grillspec/freshness.lock": "{}\n",
        ".grillspec/tools/check_task_record.py": "# old\n",
        ".grillspec/no-fakes-allow.txt": "# waivers stay\n",
    }
    for rel, content in f.items():
        p = d / rel; p.parent.mkdir(parents=True, exist_ok=True); p.write_text(content, encoding="utf-8")
    (d / ".claude").mkdir()
    os.symlink("../.grillspec/derived.lock", d / ".claude" / "derived.lock")
    os.symlink("../.grillspec/no-fakes-allow.txt", d / ".claude" / "no-fakes-allow.txt")

def run(d, *args):
    env = {k: v for k, v in os.environ.items() if k != "GRILLSPEC_TEST_ROOTS"}
    return subprocess.run([sys.executable, str(TOOL), "--root", str(d), *args], capture_output=True, text=True, env=env)

d = pathlib.Path(tempfile.mkdtemp(prefix="migrate_"))
try:
    legacy(d)
    r = run(d)
    check("settings are required", r.returncode == 2 and "--profile is required" in r.stdout, r.stdout + r.stderr)

    r = run(d, "--profile", "standard", "--delivery", "trunk")
    check("dry run prints the plan", r.returncode == 0 and "dry run" in r.stdout and "done 1 · in-progress 1 · todo 1" in r.stdout, r.stdout + r.stderr)
    check("dry run changes nothing", (d / "spec/10-delivery/verification").is_dir() and (d / ".grillspec/derived.lock").exists()
          and not (d / ".grillspec/project.json").exists() and "| status |" not in (d / "spec/10-delivery/tasks/T-001.md").read_text())

    r = run(d, "--profile", "standard", "--delivery", "trunk", "--apply")
    check("apply succeeds", r.returncode == 0 and "APPLIED" in r.stdout, r.stdout + r.stderr)
    check("settings written", json.loads((d / ".grillspec/project.json").read_text()) == {"delivery": "trunk", "profile": "standard"})
    t1 = (d / "spec/10-delivery/tasks/T-001.md").read_text()
    check("a done record becomes status done, after the phase row", "| phase | MVP · afk: eligible |\n| status | done |" in t1, t1)
    check("an unfinished record becomes in-progress", "| status | in-progress |" in (d / "spec/10-delivery/tasks/T-002.md").read_text())
    check("no record becomes todo", "| status | todo |" in (d / "spec/10-delivery/tasks/T-003.md").read_text())
    check("an existing status row is kept", (d / "spec/10-delivery/tasks/T-004.md").read_text().count("| status |") == 1
          and "blocked — credential" in (d / "spec/10-delivery/tasks/T-004.md").read_text())
    check("the build order is not a brief", "| status |" not in (d / "spec/10-delivery/tasks/build-order.md").read_text())
    check("the verification ledger is gone", not (d / "spec/10-delivery/verification").exists())
    check("both locks are gone", not (d / ".grillspec/derived.lock").exists() and not (d / ".grillspec/freshness.lock").exists())
    check("the dangling host link is gone, a live one stays",
          not os.path.lexists(d / ".claude" / "derived.lock") and (d / ".claude" / "no-fakes-allow.txt").exists())
    check("waivers are untouched", (d / ".grillspec/no-fakes-allow.txt").read_text() == "# waivers stay\n")
    tools = d / ".grillspec" / "tools"
    check("stale vendored tool removed, current set vendored",
          not (tools / "check_task_record.py").exists() and all((tools / f).is_file() for f in ("check_task.py", "lint_spec.py", "gate_exec.py")))
    check("the report groups what is left to judge", "left to judge" in r.stdout, r.stdout)

    r = run(d, "--apply")
    check("a second run needs no flags and is a no-op on briefs", r.returncode == 0 and "add a `status` row" not in r.stdout, r.stdout + r.stderr)
finally:
    shutil.rmtree(d, ignore_errors=True)

print("\n%d passed, %d failed" % (PASS, FAIL))
sys.exit(1 if FAIL else 0)
