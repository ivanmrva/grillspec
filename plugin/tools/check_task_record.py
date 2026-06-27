#!/usr/bin/env python3
# check_task_record.py - the per-task accountability backstop: reconcile a task's CLAIMED done against the
# OBLIGATIONS its own (frozen) spec references demand, so a task cannot be marked done without the evidence.
#
# Why this exists: "done" was self-attested - an agent could declare a task finished without ever writing a
# failing-first test or producing an independent conformance verdict, and nothing caught it. This makes the
# bookends mechanical. It does NOT re-run tests or compute coverage (the project's harness owns green); it
# reconciles the on-disk RECORDS against the task's frozen obligation set and fails the gate when:
#   - a record CLAIMS done (`status: done`) but an obligation row is PENDING/FAIL/blank;
#   - the record dropped an obligation the task references (you cannot shrink the bar by editing the record);
#   - the record OMITS any standard gate row (tests-first/tests:layers/coverage/mutation/fitness*/spec-lint/
#     deploy/traceability) — a required artifact or check silently dropped rather than shipped real or `N/A — why`;
#   - the conformance row is not PASS, or no independent `VERDICT: PASS` for this T- exists on disk;
#   - an AC-/API-/EVT- obligation has no passing row in the traceability matrix (tests-first, evidenced);
#   - an evidence cell points at a path that does not exist (fabricated evidence);
#   - a coverage/mutation number is below its stated bar.
# An in-progress record (`status: in-progress`) is reported, never blocked - mid-flight work is fine; only a
# DONE-CLAIM that isn't backed is an ERROR.
#
# The obligation set is REGENERATED from the task on every run, so the record cannot be authored to mark its
# own homework. What it cannot judge - whether a test genuinely pins the AC's behaviour, architecture health -
# stays the conformance review's semantic job; this checks the paperwork is complete and self-consistent.
#
# No-ops cleanly when there are no tasks/records yet (so CI never hard-fails on an early project). Usage:
#   python3 tools/check_task_record.py [spec_dir]                  # check every existing record
#   python3 tools/check_task_record.py [spec_dir] --task   T-014   # check one task's record
#   python3 tools/check_task_record.py [spec_dir] --init   T-014   # GENERATE the pre-impl checklist (PENDING rows)
#   python3 tools/check_task_record.py [spec_dir] --report [T-014] # render a readable, tool-VOUCHED completion report
import sys, re, pathlib

args = [a for a in sys.argv[1:] if not a.startswith("--")]
flags = [a for a in sys.argv[1:] if a.startswith("--")]
SPEC = pathlib.Path(args[0] if args else "spec")
ROOT = SPEC.parent                                              # the project root; evidence paths resolve here
WANT = None
for i, a in enumerate(sys.argv):
    if a in ("--task", "--init", "--report") and i + 1 < len(sys.argv) and not sys.argv[i + 1].startswith("--"):
        WANT = sys.argv[i + 1]
INIT = "--init" in flags
REPORT = "--report" in flags                                   # render a human-readable, tool-VOUCHED completion report

# Mirror lint_spec's type-prefix vocabulary (kept in sync via selfcheck).
TYPES = "UC|AC|CMD|EVT|AGG|VO|INV|HOT|POL|RM|ENTL|ENT|NFR|ASR|API|SEC|THR|DATA|OBL|SLO|EXP|DS|JRN|ML|FAC|REPO|SVC|IF|MOD|CA|ADR|T"
IDCORE = r"(?:" + TYPES + r")-[A-Za-z0-9._-]*[A-Za-z0-9]"
IDTOK = re.compile(r"(?<![A-Za-z0-9-])" + IDCORE)

def _verif_dir():
    for cand in (SPEC / "10-delivery" / "verification", SPEC / "delivery" / "verification"):
        if cand.exists():
            return cand
    return SPEC / "10-delivery" / "verification"

def _tasks_dir():
    for cand in (SPEC / "10-delivery" / "tasks", SPEC / "delivery" / "tasks"):
        if cand.exists():
            return cand
    return SPEC / "10-delivery" / "tasks"

TASKS = _tasks_dir()
VERIF = _verif_dir()
RECORDS = VERIF / "tasks"
TRACE = VERIF / "traceability.md"
REVIEW = VERIF / "review-report.md"

# dimensions that impose an OBLIGATION (an ID here must be realised, tested, evidenced) vs. dimensions that
# are context (depends -> other tasks; ux/placement/design/outcome -> not an ID-obligation of this task).
OBLIGATION_DIMS = ("behavior", "domain", "data", "api", "security", "nfr", "integration")
# standard gate rows every task carries, beyond its referenced IDs (from the engine's done-gate).
GATE_ROWS = [
    ("tests-first", "done-gate", "every AC- has a failing-capable test that drove the code"),
    ("tests:layers", "test-strategy", "every test level the slice touches per the test strategy exists & passes (unit/integration/contract/e2e/NFR-evidence as applicable)"),
    ("coverage", "test-strategy", ">= ratified coverage bar"),
    ("mutation", "test-strategy", ">= ratified mutation bar on changed logic"),
    ("fitness:no-fakes", "done-gate", "no stub/mock/double/canned-response/unwired-fallback in src/"),
    ("fitness:architecture", "done-gate", "architecture fitness functions green"),
    ("spec-lint", "done-gate", "spec-lint clean"),
    ("deploy", "infra-ops", "the slice deploys to the first env of the ratified promotion path and a green e2e/smoke ran AGAINST that deployed env (the behavioural proof — evidence is the run, not just that the deploy file exists); or 'N/A — no new deployable surface'. If the env can't run yet, 'blocked — <env> not provisioned' (escalated), never PASS and never silently skipped"),
    ("conformance", "review", "independent VERDICT: PASS for this T-"),
    ("traceability", "done-gate", "traceability matrix updated"),
]
# every standard gate row must be CARRIED by a done-claim (present + PASS/'N/A — why') - omitting a row is the
# silent scope reduction this gate exists to stop (the deploy script, the e2e layer, the traceability update, the
# fitness run quietly dropped). The bar can't be shrunk by leaving a row out of the record. `conformance` is
# excluded here only because it has its own richer check below (it needs an independent VERDICT on disk too).
REQUIRED_GATE_ROW_KEYS = [k for (k, _src, _req) in GATE_ROWS if k != "conformance"]
# evidence paths that must EXIST on disk when cited (a fabricated-evidence guard). Code/spec/test trees plus the
# deploy-artifact homes, so a deploy row can't cite a CI/IaC file that isn't there.
EVIDENCE_PREFIXES = ("src/", "tests/", "test/", "evidence/", "spec/",
                     ".github/", "deploy/", "ops/", "infra/", "iac/", "k8s/", "helm/", "charts/", "terraform/")

F = []
def add(sev, where, msg): F.append((sev, where, msg))

def task_file(tid):
    p = TASKS / (tid + ".md")
    return p if p.exists() else None

def task_obligations(tid):
    """Regenerate the obligation ID set from the task's frozen references - this is the un-gameable bar."""
    p = task_file(tid)
    if not p:
        return None
    obs = []  # preserve order, de-dup
    seen = set()
    for line in p.read_text(encoding="utf-8", errors="replace").splitlines():
        m = re.match(r"^\s*([A-Za-z][\w-]*)\s*:\s*(.*)$", line)
        if not m:
            continue
        dim, val = m.group(1).strip().lower(), m.group(2)
        if dim not in OBLIGATION_DIMS:
            continue
        for tok in IDTOK.findall(val):
            if tok.startswith(("T-", "ADR-")) or tok in seen:
                continue
            seen.add(tok)
            obs.append((tok, dim))
    return obs

def parse_record(p):
    """Return (status, {obligation_first_cell: (status_last_cell, evidence_cell)})."""
    status = None
    rows = {}
    for line in p.read_text(encoding="utf-8", errors="replace").splitlines():
        sm = re.match(r"^\s*status\s*:\s*(\S+)", line, re.I)
        if sm and status is None:
            status = sm.group(1).lower()
            continue
        if not line.lstrip().startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 5:
            continue
        key = cells[0].strip(" *`")
        if not key or key.lower() in ("obligation", "---") or set(key) <= set("-: "):
            continue
        rows[key] = (cells[-1].strip(" *`"), cells[3])   # (status, evidence)
    return status, rows

def is_pass(s):
    s = (s or "").strip().lower()
    return s in ("pass", "✓", "ok", "green") or s.startswith("n/a")

# ---------------------------------------------------------------------------------------------------------
# --init: generate the pre-implementation checklist (PENDING rows from the task's frozen references).
# ---------------------------------------------------------------------------------------------------------
if INIT:
    if not WANT:
        print("check_task_record: --init needs a task id (e.g. --init T-014).")
        sys.exit(2)
    obs = task_obligations(WANT)
    if obs is None:
        print("check_task_record: no task file %s/%s.md to generate a record from." % (TASKS, WANT))
        sys.exit(2)
    RECORDS.mkdir(parents=True, exist_ok=True)
    out = RECORDS / (WANT + ".md")
    if out.exists() and "--force" not in flags:
        print("check_task_record: %s already exists (use --force to overwrite)." % out)
        sys.exit(2)
    lines = [
        "<!-- scope: per-task verification record for %s | excludes: code | format: obligation table -->" % WANT,
        "# %s — Verification Record" % WANT,
        "",
        "status: in-progress   <!-- in-progress | done — set to 'done' ONLY when every row below is PASS or N/A -->",
        "task: %s" % WANT,
        "",
        "| Obligation | Source | Required | Evidence | Status |",
        "|---|---|---|---|---|",
    ]
    for tok, dim in obs:
        req = {"behavior": "failing-capable test, passing", "api": "contract test (provider/consumer)",
               "security": "enforced + evidenced", "nfr": "evidence test (measured, not asserted)",
               "data": "persistence + migration", "integration": "real-path integration test",
               "domain": "realised + behaviour-tested"}.get(dim, "implemented + tested")
        lines.append("| %s | %s | %s |  | PENDING |" % (tok, dim, req))
    for key, src, req in GATE_ROWS:
        lines.append("| %s | %s | %s |  | PENDING |" % (key, src, req))
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("check_task_record: wrote pre-implementation checklist %s (%d obligation rows + %d gate rows, all PENDING)."
          % (out, len(obs), len(GATE_ROWS)))
    print("Implement test-first; fill each Evidence cell and flip its Status to PASS; set 'status: done' only when all are PASS.")
    sys.exit(0)

# ---------------------------------------------------------------------------------------------------------
# default: check existing record(s).
# ---------------------------------------------------------------------------------------------------------
if not RECORDS.exists():
    if WANT:
        add("ERROR", "(records)", "no verification record %s/%s.md — run `--init %s` before claiming done." % (RECORDS, WANT, WANT))
    else:
        print("check_task_record: no %s — no per-task records to check yet." % RECORDS)
        sys.exit(0)

trace_txt = TRACE.read_text(encoding="utf-8", errors="replace") if TRACE.exists() else None
review_txt = REVIEW.read_text(encoding="utf-8", errors="replace") if REVIEW.exists() else None

# the test source tree - the un-gameable evidence for AC coverage (the `@covers AC-NNN` tag convention puts the
# AC id literally in the test that drives it, so it can't be claimed in a self-authored matrix without a tagged
# test actually existing in the tree).
TEST_DIRS = [d for d in (ROOT / "tests", ROOT / "test") if d.is_dir()]
_test_blob = None
def covered_in_source(tok):
    global _test_blob
    if not TEST_DIRS:
        return None                                            # no test tree to check against
    if _test_blob is None:
        parts = []
        for base in TEST_DIRS:
            for p in base.rglob("*"):
                if p.is_file():
                    try: parts.append(p.read_text(encoding="utf-8", errors="replace"))
                    except Exception: pass
        _test_blob = "\n".join(parts)
    return tok in _test_blob

def review_pass_for(tid):
    """An independent VERDICT: PASS for this T- on disk - in review-report.md or a per-task review file."""
    texts = []
    if review_txt:
        texts.append(review_txt)
    for cand in (VERIF / (tid + ".md"), VERIF / ("review-%s.md" % tid)):
        if cand.exists():
            texts.append(cand.read_text(encoding="utf-8", errors="replace"))
    for t in texts:
        for m in re.finditer(r"VERDICT:\s*PASS", t, re.I):
            window = t[max(0, m.start() - 400): m.end() + 400]
            if tid in window or len(texts) == 1 and tid in t:
                return True
        if re.search(r"VERDICT:\s*PASS", t, re.I) and tid in t:
            return True
    return False

records = []
if WANT:
    p = RECORDS / (WANT + ".md")
    if not p.exists():
        add("ERROR", WANT, "no verification record %s — run `--init %s` before claiming done." % (p, WANT))
    else:
        records = [p]
else:
    records = sorted(RECORDS.glob("T-*.md"))

for p in records:
    tid = p.stem
    status, rows = parse_record(p)
    where = tid
    if status not in ("done", "complete"):
        met = sum(1 for s, _ in rows.values() if is_pass(s))
        add("INFO", where, "in-progress (%d/%d obligations PASS) — not gating." % (met, len(rows)))
        continue

    # A record claiming DONE is held to the full bar.
    obs = task_obligations(tid)
    if obs is None:
        add("ERROR", where, "record claims done but no task file %s/%s.md to verify its obligations against." % (TASKS, tid))
        obs = []

    # 1. completeness - every referenced obligation has a row (the bar cannot be shrunk by omission).
    for tok, dim in obs:
        if tok not in rows:
            add("ERROR", where, "obligation %s (%s) referenced by the task is MISSING from the record — the bar cannot be shrunk." % (tok, dim))

    # 2. no unmet row in a done-claim.
    for key, (st, _ev) in rows.items():
        if not is_pass(st):
            add("ERROR", where, "row '%s' is '%s' but the record claims done — every row must be PASS or 'N/A — why'." % (key, st or "(blank)"))

    # 3. conformance - the row PASS AND an independent VERDICT: PASS on disk.
    conf = rows.get("conformance")
    if not conf or not is_pass(conf[0]):
        add("ERROR", where, "the conformance row is not PASS — an independent conformance review must record VERDICT: PASS.")
    elif not review_pass_for(tid):
        add("ERROR", where, "conformance row says PASS but no independent 'VERDICT: PASS' for %s found on disk (review-report.md / %s/%s.md)." % (tid, VERIF.name, tid))

    # 3b. no silent omission - a done-claim must CARRY every standard gate row. Omitting a row (rather than
    #     marking it 'N/A — why') is the exact cheat where a required artifact/check is quietly dropped; the row
    #     must be present and either PASS or an explained N/A (its value is then held by checks #2/#5/#6).
    for needed in REQUIRED_GATE_ROW_KEYS:
        if needed not in rows:
            add("ERROR", where, "a done-claim must carry the '%s' gate row (present + PASS or 'N/A — why') — it cannot be omitted." % needed)

    # 4. tests-first evidence - each AC-/API-/EVT- obligation traced to a passing row in the matrix, AND each
    #    AC- actually present in the TEST SOURCE (the `@covers AC-NNN` tag) so the matrix can't claim a test the
    #    tree doesn't contain.
    for tok, dim in obs:
        if tok.startswith("AC-"):
            src = covered_in_source(tok)
            if src is False:
                add("ERROR", where, "%s appears in no file under tests/ — no `@covers %s`-tagged test in the tree (a matrix row can't substitute for the actual test)." % (tok, tok))
        if not tok.startswith(("AC-", "API-", "EVT-")):
            continue
        if trace_txt is None:
            add("WARN", where, "no traceability matrix (%s) to confirm %s is covered by a passing test." % (TRACE, tok))
            continue
        traced = any(tok in ln and ("✓" in ln or re.search(r"\bpass\b", ln, re.I)) for ln in trace_txt.splitlines())
        if not traced:
            add("ERROR", where, "%s has no passing row in the traceability matrix — a back-filled or missing test, not test-first." % tok)

    # 5. evidence integrity - a path-like evidence cell must exist on disk.
    for key, (st, ev) in rows.items():
        for tok in re.findall(r"[\w./-]+/[\w./-]+", ev):
            tok = tok.rstrip(".,;:")
            if tok.startswith(EVIDENCE_PREFIXES) and not (ROOT / tok).exists():
                add("ERROR", where, "row '%s' cites evidence '%s' which does not exist on disk." % (key, tok))

    # 6. numeric bars - coverage/mutation measured >= stated bar.
    for key in ("coverage", "mutation"):
        if key in rows:
            ev = rows[key][1]
            nums = re.findall(r"(\d+(?:\.\d+)?)\s*%?", ev)
            bar_m = re.search(r"bar\D*(\d+(?:\.\d+)?)", ev, re.I)
            if nums and bar_m:
                measured, bar = float(nums[0]), float(bar_m.group(1))
                if measured < bar:
                    add("ERROR", where, "%s %.3g is below its bar %.3g." % (key, measured, bar))

    if not any(s == "ERROR" and w == where for s, w, _ in F):
        add("INFO", where, "done — %d obligations + %d gate rows all evidenced." % (len(obs), len(GATE_ROWS)))

e = sum(1 for x in F if x[0] == "ERROR")
w = sum(1 for x in F if x[0] == "WARN")

# ---------------------------------------------------------------------------------------------------------
# --report: render the VERIFIED state as a readable per-task completion report. The reassurance is that the
# tool re-checked first (the findings above), so a ✓ here is vouched, not just the agent's self-authored claim.
# ---------------------------------------------------------------------------------------------------------
if REPORT:
    def task_title(tid):
        p = task_file(tid)
        if not p: return ""
        first = p.read_text(encoding="utf-8", errors="replace").splitlines()[0]
        return first.split("|")[-1].strip() if "|" in first else ""
    def full_rows(p):
        out = []
        for line in p.read_text(encoding="utf-8", errors="replace").splitlines():
            if not line.lstrip().startswith("|"): continue
            c = [x.strip() for x in line.strip().strip("|").split("|")]
            if len(c) < 5: continue
            key = c[0].strip(" *`")
            if not key or key.lower() in ("obligation", "---") or set(key) <= set("-: "): continue
            out.append((key, c[1], c[3], c[-1].strip(" *`")))   # key, source, evidence, status
        return out
    for p in records:
        tid = p.stem
        status, _ = parse_record(p)
        errs = [m for s, wq, m in F if s == "ERROR" and wq == tid]
        badge = "✅ VERIFIED" if (status in ("done", "complete") and not errs) else \
                ("❌ %d ISSUE(S)" % len(errs) if errs else "… in-progress")
        print("\n%s — %s   [status: %s]  %s" % (tid, task_title(tid) or "(no task title)", status or "?", badge))
        groups = {}
        for key, src, ev, st in full_rows(p):
            groups.setdefault(src or "other", []).append((key, ev, st))
        for src in sorted(groups):
            print("  %s" % src)
            for key, ev, st in groups[src]:
                mark = "✓" if is_pass(st) else ("○" if st.lower() in ("pending", "") else "✗")
                print("    %s %-22s %s" % (mark, key, ev or st))
        if review_pass_for(tid):
            print("  conformance: independent VERDICT: PASS on disk ✓")
        for m in errs:
            print("    ✗ %s" % m)
    print("\n%d task(s) reported · %d error(s), %d warning(s)." % (len(records), e, w))
    sys.exit(1 if e else 0)

order = {"ERROR": 0, "WARN": 1, "INFO": 2}
for sev, where, msg in sorted(F, key=lambda x: (order[x[0]], x[1], x[2])):
    print("%-5s %-10s %s" % (sev, where, msg))
print("\n%d error(s), %d warning(s)." % (e, w))
sys.exit(1 if e else 0)
