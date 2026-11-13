#!/usr/bin/env python3
"""migrate_project.py - bring a project built with an earlier major version onto the current layout.

The mechanical part of adoption, in one command. It never touches code, and it changes spec content in
exactly one way: each task brief gains the `status` row that used to live in a separate record.

  1. writes the project settings (.grillspec/project.json);
  2. carries each task's status from its verification record into the brief's `status` row
     (record `done` -> `done`, any other record -> `in-progress`, no record -> `todo`);
  3. removes the verification ledger (spec/10-delivery/verification/), the derived and freshness locks,
     and host-directory links that point at files that no longer exist;
  4. replaces the vendored tools under .grillspec/tools/ with the current set.

What it leaves for a person (or the conductor) to judge is printed at the end: the linter's findings,
grouped by check, to be worked through by removing what has no reader.

Usage (run from the project root):
    python3 tools/migrate_project.py --profile standard --delivery trunk           # dry run: print the plan
    python3 tools/migrate_project.py --profile standard --delivery trunk --apply   # do it

Git is the undo: run it on a clean tree and review the diff. Stdlib only.
"""
import os
import pathlib
import re
import shutil
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import project_config  # noqa: E402

LOCKS = ("derived.lock", "freshness.lock")
STALE_TOOLS = ("check_task_record.py", "guard_derived.py", "check_freshness.py",
               "check_release_attestation.py", "check_operate_records.py")
HOST_DIRS = (".claude", ".codex")


def parse_args(argv):
    opts = {"root": ".", "apply": False, "profile": None, "delivery": None}
    i = 0
    while i < len(argv):
        a = argv[i]
        if a == "--apply":
            opts["apply"] = True; i += 1
        elif a in ("--root", "--profile", "--delivery") and i + 1 < len(argv):
            opts[a[2:]] = argv[i + 1]; i += 2
        else:
            print(__doc__.strip()); sys.exit(0 if a in ("-h", "--help") else 2)
    cur = project_config.load(opts["root"])
    for key, allowed in (("profile", project_config.PROFILES), ("delivery", project_config.DELIVERY)):
        if opts[key] is None and cur["explicit"]:
            opts[key] = cur[key]
        if opts[key] not in allowed:
            print("migrate_project: --%s is required, one of %s" % (key, " | ".join(allowed))); sys.exit(2)
    return opts


def record_status(path):
    """`done` when the record's own status line says so, else `in-progress`."""
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        m = re.match(r"^\s*status\s*:\s*([A-Za-z-]+)", line)
        if m:
            return "done" if m.group(1).lower() == "done" else "in-progress"
    return "in-progress"


def has_status_row(text):
    return re.search(r"(?mi)^\s*\|\s*[*`_]*status[*`_]*\s*\|", text) is not None


def add_status_row(text, status):
    """Insert `| status | <status> |` after the brief's `phase` row, else after the table's separator."""
    lines = text.splitlines()
    row = "| status | %s |" % status
    for i, l in enumerate(lines):
        if re.match(r"^\s*\|\s*[*`_]*phase[*`_]*\s*\|", l, re.I):
            return "\n".join(lines[:i + 1] + [row] + lines[i + 1:]) + "\n"
    for i, l in enumerate(lines):
        if re.match(r"^\s*\|[\s:|-]+\|\s*$", l) and "-" in l:
            return "\n".join(lines[:i + 1] + [row] + lines[i + 1:]) + "\n"
    return None


def main(argv):
    opts = parse_args(argv)
    root = pathlib.Path(opts["root"]).resolve()
    spec = root / "spec"
    if not spec.is_dir():
        print("migrate_project: no spec/ under %s - nothing to migrate." % root); return 2
    apply = opts["apply"]
    plan = []

    # 1. settings
    plan.append("write .grillspec/project.json: profile=%s delivery=%s" % (opts["profile"], opts["delivery"]))
    if apply:
        project_config.save(root, {"profile": opts["profile"], "delivery": opts["delivery"]})

    # 2. task status -> the brief
    tasks = spec / "10-delivery" / "tasks"
    verif = spec / "10-delivery" / "verification"
    counts, untouched = {}, []
    for brief in sorted(tasks.glob("T-*.md")) if tasks.is_dir() else []:
        text = brief.read_text(encoding="utf-8", errors="replace")
        if has_status_row(text):
            continue
        rec = verif / "tasks" / brief.name
        status = record_status(rec) if rec.is_file() else "todo"
        new = add_status_row(text, status)
        if new is None:
            untouched.append(brief.name); continue
        counts[status] = counts.get(status, 0) + 1
        if apply:
            brief.write_text(new, encoding="utf-8")
    if counts:
        plan.append("add a `status` row to %d brief(s): %s" % (
            sum(counts.values()), " · ".join("%s %d" % (k, counts[k]) for k in sorted(counts))))
    if untouched:
        plan.append("NOT changed (no field|value table to add a row to): %s" % ", ".join(untouched[:12]))

    # 3. the ledger, the locks, dangling host links
    if verif.exists():
        n = sum(1 for p in verif.rglob("*") if p.is_file())
        plan.append("remove spec/10-delivery/verification/ (%d file(s))" % n)
        if apply:
            shutil.rmtree(verif)
    state = root / ".grillspec"
    for name in LOCKS:
        if (state / name).exists():
            plan.append("remove .grillspec/%s" % name)
            if apply:
                (state / name).unlink()
    for host in HOST_DIRS:
        hd = root / host
        if not hd.is_dir():
            continue
        for p in sorted(hd.iterdir()):
            if p.is_symlink() and (p.name in LOCKS or (apply and not p.exists())
                                   or not (hd / os.readlink(p)).exists()):
                plan.append("remove dangling link %s/%s" % (host, p.name))
                if apply:
                    p.unlink()

    # 4. vendored tools
    vend = state / "tools"
    for name in STALE_TOOLS:
        if (vend / name).exists():
            plan.append("remove vendored .grillspec/tools/%s" % name)
            if apply:
                (vend / name).unlink()
    plan.append("vendor the current tools and hooks (install_exec_gates.py)")
    if apply:
        subprocess.run([sys.executable, str(HERE / "install_exec_gates.py"), str(root)],
                       capture_output=True, text=True)

    print("migrate_project (%s) - %s" % ("APPLIED" if apply else "dry run", root))
    for step in plan:
        print("  - " + step)

    # what is left to judge: the linter, grouped
    lint = subprocess.run([sys.executable, str(HERE / "lint_spec.py"), str(spec)], capture_output=True, text=True)
    groups = {}
    KEYS = (("edit-trace stamp", "40 edit-trace stamps (errors) - drop the stamp, keep the fact"),
            ("dated statement", "40 dated statements - remove change notes; mark real domain dates"),
            ("edit-history phrasing", "40 edit-history phrasing - state the current rule"),
            ("outside the project's", "41 areas beyond the profile - remove, or raise the profile"),
            ("full-mode artifact", "41 full-mode solution files - keep the decision; check no project script reads the file before removing it"),
            ("file outside the defined structure", "1 files outside the structure"),
            ("missing file header", "3 files without a header"),
            ("carries no `tier`", "42 open briefs without a tier"))
    other_err = 0
    for line in lint.stdout.splitlines():
        hit = next((label for key, label in KEYS if key in line), None)
        if hit:
            groups[hit] = groups.get(hit, 0) + 1
        elif line.startswith("ERROR"):
            other_err += 1
    print("\nleft to judge (lint_spec.py%s):" % ("" if apply else ", as the tree stands now"))
    for _key, label in KEYS:
        if label in groups:
            print("  %5d  check %s" % (groups[label], label))
    if other_err:
        print("  %5d  other errors" % other_err)
    if not groups and not other_err:
        print("  nothing - the spec is clean.")
    if not apply:
        print("\nre-run with --apply to perform the steps above.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
