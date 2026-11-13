#!/usr/bin/env python3
"""check_task.py - a task's status and done-claim, computed from the tree. Nothing is stored.

A task brief (`spec/10-delivery/tasks/T-NNN.md`, one `field | value` table) says what the slice must do
and carries one `status` row. Whether that claim holds is read from the working tree:

  - every acceptance criterion in the brief's `behavior` cell has a literal `@covers AC-...` tag in a test
    source that declares a runnable test;
  - every interaction state the `ux` cell names has a `@state:<name>` tag in such a source;
  - no `GAP ... UNRESOLVED` remains in the brief;
  - a `critical` task carries `review | PASS` (written by the fresh-context reviewer), and the design
    note a `design-first` task names exists.

A dependency whose own status is not `done` is reported beside the task as a note: it means one of the
two status rows is out of date, which is for a person to settle, not evidence missing from the tree.

Whether the tests PASS, and coverage/mutation bars, belong to the project's own gate (the test runner and
its config) - this tool never parses a number someone typed.

Usage (run from the project root):
    python3 tools/check_task.py [spec_dir]                  # status table + gate every `done` task
    python3 tools/check_task.py [spec_dir] --task T-014     # gate one task as if it claimed done
    python3 tools/check_task.py [spec_dir] --json           # the status as JSON (for dashboards)
    python3 tools/check_task.py [spec_dir] --trace          # AC -> task -> covering test files

Exit 0 = every done-claim holds (or there are no tasks yet); 1 = a done-claim is not backed. Stdlib only.
"""
import json
import os
import pathlib
import re
import sys

_argv = sys.argv[1:]
WANT = None
if "--task" in _argv:
    i = _argv.index("--task")
    if i + 1 < len(_argv) and not _argv[i + 1].startswith("--"):
        WANT = _argv[i + 1]
    else:
        print("check_task: --task needs a task id (e.g. --task T-014)."); sys.exit(2)
_pos = [a for a in _argv if not a.startswith("--") and a != WANT]
AS_JSON = "--json" in _argv
TRACE = "--trace" in _argv
if "-h" in _argv or "--help" in _argv:
    print(__doc__.strip()); sys.exit(0)

SPEC = pathlib.Path(_pos[0] if _pos else "spec")
ROOT = SPEC.resolve().parent


def _tasks_dir():
    for cand in (SPEC / "10-delivery" / "tasks", SPEC / "delivery" / "tasks"):
        if cand.exists():
            return cand
    return SPEC / "10-delivery" / "tasks"


TASKS = _tasks_dir()

# Mirror lint_spec's type-prefix vocabulary (kept in sync via selfcheck).
TYPES = "UC|AC|CMD|EVT|AGG|VO|INV|HOT|POL|RM|ENTL|ENT|NFR|ASR|API|SEC|THR|DATA|OBL|SLO|EXP|AEV|DS|JRN|SCR|ML|FAC|REPO|SVC|IF|MOD|CA|ADR|T"
IDCORE = r"(?:" + TYPES + r")-[A-Za-z0-9._-]*[A-Za-z0-9]"
IDTOK = re.compile(r"(?<![A-Za-z0-9-])" + IDCORE)
TASK_ID = re.compile(r"(?<![A-Za-z0-9-])T-\d+[A-Za-z0-9]*")
TIERS = ("routine", "feature", "critical")
STATUSES = ("todo", "in-progress", "done", "blocked")

# --- the brief ------------------------------------------------------------------------------------------
def _clean(cell):
    return re.sub(r"[*`_]", "", cell or "").strip()


def is_na(cell):
    c = _clean(cell).lower()
    return c in ("", "-", "—", "–") or re.match(r"n/?a\b|none\b", c) is not None


def task_fields(path):
    """{field: value} from the brief's `field | value` table (also accepts plain `field: value` lines)."""
    out = {}
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        s = line.strip()
        if s.startswith("|"):
            cells = [c.strip() for c in s.strip("|").split("|")]
            if len(cells) < 2:
                continue
            key, val = cells[0], "|".join(cells[1:]).strip()
        else:
            m = re.match(r"^\s*([A-Za-z][\w-]*)\s*:\s*(.*)$", line)
            if not m:
                continue
            key, val = m.group(1), m.group(2)
        key = re.sub(r"[\s_]", "-", _clean(key).lower())
        if not key or key in ("field", "dimension") or set(key) <= set("-: "):
            continue
        out.setdefault(key, val)
    return out


def task_files():
    if not TASKS.exists():
        return []
    return sorted(p for p in TASKS.glob("T-*.md"))


def status_of(fields):
    """The brief's status token; a brief with no status row is `todo`."""
    val = _clean(fields.get("status", "")).lower()
    for st in STATUSES:
        if val.startswith(st):
            return st
    return "todo" if not val else val.split()[0]


def tier_of(fields):
    val = _clean(fields.get("tier", "")).lower()
    return next((t for t in TIERS if re.match(t + r"\b", val)), None)


def acs_of(fields):
    """The acceptance criteria this task owns: every AC- id in its `behavior` (and `tests`) cell."""
    seen, out = set(), []
    for dim in ("behavior", "tests"):
        for tok in IDTOK.findall(fields.get(dim, "")):
            if tok.startswith("AC-") and tok not in seen:
                seen.add(tok); out.append(tok)
    return out


def ux_states(cell):
    """Interaction states named by a ux cell's `states: a · b · c` list (empty for N/A or no list)."""
    if is_na(cell):
        return []
    m = re.search(r"(?i)\bstates?\s*[:\-—]\s*([^|]*)", cell or "")
    if not m:
        return []
    seg = re.split(r"(?i)<br\s*/?>|→", m.group(1))[0]
    return [s for s in (_clean(t).lower() for t in re.split(r"[·,;/]", seg))
            if re.fullmatch(r"[a-z0-9][a-z0-9 _-]*", s)]


def depends_of(fields):
    val = fields.get("depends", fields.get("deps", fields.get("depends-on", fields.get("dependencies", ""))))
    return [] if is_na(val) else TASK_ID.findall(val)


# --- the tree: test sources that can fail -----------------------------------------------------------------
TEST_SOURCE_EXTS = {".py", ".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs", ".go", ".java", ".kt",
                    ".rb", ".cs", ".php", ".rs", ".scala", ".swift", ".feature", ".bats", ".exs",
                    ".dart", ".c", ".cc", ".cpp", ".cxx", ".fs", ".fsx", ".clj", ".cljs", ".groovy",
                    ".lua", ".sh", ".ps1", ".r", ".hs"}
TEST_PATH_PARTS = {"test", "tests", "__tests__", "e2e"}
COLOCATED_ROOTS = {"src", "app", "apps", "lib", "libs", "packages", "spec"}
# GRILLSPEC_TEST_ROOTS (comma-separated) names extra source-root directory names - the same lever
# tier_contract honours, so a monorepo that nests its code under a wrapper directory sets it once.
COLOCATED_ROOTS |= {r.strip().lower() for r in os.environ.get("GRILLSPEC_TEST_ROOTS", "").split(",") if r.strip()}
PRUNE_PARTS = {".git", ".grillspec", ".claude", ".codex", ".venv", "venv", "node_modules", "vendor", "dist",
               "build", "out", "coverage", "target", "__pycache__", ".next", ".tox"}
TEST_NAME = re.compile(r"(?:^test_|_test\.|[._](?:test|spec)s?\.|[._](?:e2e|int|integration|unit|contract)\.)", re.I)
CAMEL_TEST = re.compile(r"[a-z0-9](?:Test|Tests|Spec|Specs)\.[A-Za-z0-9]+$")
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from tier_contract import FAILING_CAPABLE  # noqa: E402  (one definition of "a test the runner can fail")


def _is_test_source(p):
    try:
        rel = p.relative_to(ROOT)
    except ValueError:
        return False
    parts = [x.lower() for x in rel.parts]
    if p.suffix.lower() not in TEST_SOURCE_EXTS or any(x in PRUNE_PARTS for x in parts[:-1]):
        return False
    if parts and parts[0] == SPEC.name.lower() and (ROOT / parts[0]).resolve() == SPEC.resolve():
        return False                                            # the spec tree itself is never a test source
    in_test_tree = any(x in TEST_PATH_PARTS for x in parts[:-1])
    colocated = bool(any(x in COLOCATED_ROOTS for x in parts[:-1]) and
                     (TEST_NAME.search(p.name) or CAMEL_TEST.search(p.name)))
    return in_test_tree or colocated


def _without_comments(text):
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.S)
    code = []
    for line in text.splitlines():
        s = line.lstrip()
        if s.startswith(("//", "--")) or (s.startswith("#") and not s.startswith("#[")):
            continue
        code.append(re.sub(r"//.*$|--.*$", "", line))
    return "\n".join(code)


_sources = None


def test_sources():
    """[(relative posix path, text)] for every test source that declares a runnable test."""
    global _sources
    if _sources is None:
        _sources = []
        for base, dirs, files in os.walk(ROOT):
            dirs[:] = sorted(d for d in dirs if d.lower() not in PRUNE_PARTS)
            for name in sorted(files):
                p = pathlib.Path(base) / name
                if not _is_test_source(p):
                    continue
                try:
                    txt = p.read_text(encoding="utf-8", errors="replace")
                except OSError:
                    continue
                if FAILING_CAPABLE.search(_without_comments(txt)):
                    _sources.append((p.relative_to(ROOT).as_posix(), txt))
    return _sources


def covering_files(tok):
    """Test sources carrying a literal `@covers <tok>` tag (the tag and the id on one line)."""
    token = re.compile(r"(?<![A-Za-z0-9-])" + re.escape(tok) + r"(?![A-Za-z0-9._-])", re.I)
    hits = []
    for rel, txt in test_sources():
        for line in txt.splitlines():
            tag = re.search(r"@covers\b", line, re.I)
            if tag and token.search(line[tag.end():]):
                hits.append(rel); break
    return hits


def state_covered(name):
    token = re.compile(r"@state:\s*" + re.escape(name) + r"(?![A-Za-z0-9_-])", re.I)
    return any(token.search(txt) for _rel, txt in test_sources())


# --- evaluate ---------------------------------------------------------------------------------------------
def evaluate(path, all_status):
    f = task_fields(path)
    tid = path.stem
    acs = acs_of(f)
    uncovered = [a for a in acs if not covering_files(a)]
    states = ux_states(f.get("ux", ""))
    missing_states = [s for s in states if not state_covered(s)]
    text = path.read_text(encoding="utf-8", errors="replace")
    gaps = sum(1 for l in text.splitlines() if re.search(r"\bGAP\b", l) and re.search(r"\bUNRESOLVED\b", l, re.I))
    deps = depends_of(f)
    open_deps = [d for d in deps if all_status.get(d, "todo") != "done"]
    tier = tier_of(f)
    review = _clean(f.get("review", "")).lower()
    design = _clean(f.get("design", "")).lower()

    problems = []
    if uncovered:
        problems.append("no `@covers` test for %s" % ", ".join(uncovered))
    if missing_states:
        problems.append("no `@state:` test for %s" % ", ".join(missing_states))
    if gaps:
        problems.append("%d unresolved GAP(s)" % gaps)
    notes = []
    if open_deps:
        notes.append("depends on %s (not marked done)" % ", ".join(open_deps))
    if tier == "critical" and not review.startswith("pass"):
        problems.append("`critical` task without `review | PASS` (the fresh-context review)")
    if design.startswith("design-first"):
        m = re.search(r"([\w./-]+\.md)", f.get("design", ""))
        note = m.group(1) if m else None
        # Checked only when the brief names the note: a named file that is absent is evidence missing from
        # the tree. Whether an open brief names one at all is the linter's question, not a done-claim's.
        if note and not any((base / note).is_file() for base in (ROOT, SPEC, SPEC / "10-delivery" / "impl-design")):
            problems.append("`design-first` task whose design note is missing: " + note)
    return {
        "task": tid, "tier": tier or "-", "phase": (_clean(f.get("phase", "")).split("·")[0].strip() or "-"),
        "status": status_of(f), "acs": len(acs), "acs_covered": len(acs) - len(uncovered),
        "states": len(states), "states_covered": len(states) - len(missing_states),
        "review": (review.split()[0] if review else "-"), "problems": problems, "notes": notes,
    }


def main():
    files = task_files()
    if WANT:
        files = [p for p in files if p.stem == WANT]
        if not files:
            print("check_task: no task brief %s/%s.md." % (TASKS, WANT)); return 2
    if not files:
        if AS_JSON:
            print("[]")
        else:
            print("check_task: no task briefs under %s yet - nothing to check." % TASKS)
        return 0
    all_status = {p.stem: status_of(task_fields(p)) for p in task_files()}

    if TRACE:
        print("| AC | task | covering tests |\n|---|---|---|")
        for p in files:
            for ac in acs_of(task_fields(p)):
                print("| %s | %s | %s |" % (ac, p.stem, ", ".join(covering_files(ac)) or "—"))
        return 0

    rows = [evaluate(p, all_status) for p in files]
    failing = [r for r in rows if r["problems"] and (WANT or r["status"] == "done")]
    if AS_JSON:
        print(json.dumps(rows, indent=2))
        return 1 if failing else 0

    print("| task | tier | phase | status | ACs covered | states covered | review | open |\n|---|---|---|---|---|---|---|---|")
    for r in rows:
        print("| %s | %s | %s | %s | %d/%d | %s | %s | %s |" % (
            r["task"], r["tier"], r["phase"], r["status"], r["acs_covered"], r["acs"],
            ("%d/%d" % (r["states_covered"], r["states"])) if r["states"] else "—",
            r["review"], "; ".join(r["problems"] + ["note: " + n for n in r["notes"]]) or "—"))
    counts = {}
    for r in rows:
        counts[r["status"]] = counts.get(r["status"], 0) + 1
    print("\n%d task(s): %s." % (len(rows), " · ".join("%s %d" % (k, counts[k]) for k in sorted(counts))))
    for r in failing:
        claim = "is checked as done" if WANT and r["status"] != "done" else "claims done"
        for pr in r["problems"]:
            print("ERROR %s %s but: %s" % (r["task"], claim, pr))
    if failing:
        print("\n%d done-claim(s) not backed by the tree." % len(failing))
    return 1 if failing else 0


if __name__ == "__main__":
    sys.exit(main())
