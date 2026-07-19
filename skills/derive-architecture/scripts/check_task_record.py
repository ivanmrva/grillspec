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
#     deploy/ux:states/a11y/ux:rendered/prototype-review/obs/traceability) — a required artifact or check
#     silently dropped rather than shipped real or `N/A — why`;
#   - the conformance row is not PASS, or no independent `VERDICT: PASS` for this T- exists on disk;
#   - an AC-/API-/EVT- obligation has no passing row in the traceability matrix (tests-first, evidenced), or a
#     task-declared AC has no `@covers AC-...` tag in a failing-capable test source;
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
import sys, re, os, pathlib

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
ASSUME_DONE = "--assume-done" in flags                         # gate a record as if it claimed done (for the
#   tool-call-time exec gate: PreToolUse fires BEFORE the `status: done` edit lands, so the on-disk record
#   still says in-progress — this evaluates "would the done-claim hold?" against the unchanged obligation rows.

# Mirror lint_spec's type-prefix vocabulary (kept in sync via selfcheck).
TYPES = "UC|AC|CMD|EVT|AGG|VO|INV|HOT|POL|RM|ENTL|ENT|NFR|ASR|API|SEC|THR|DATA|OBL|SLO|EXP|AEV|DS|JRN|SCR|ML|FAC|REPO|SVC|IF|MOD|CA|ADR|T"
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
# are context (depends -> other tasks; placement/design/outcome -> not an ID-obligation of this task).
# ux/obs/ml carry obligations too, but only for their OWN id types (a `N/A — reuses DS-001` ux cell or an
# incidental cross-ref must not mint a spurious obligation row) - see OBLIGATION_DIM_PREFIXES.
OBLIGATION_DIMS = ("behavior", "domain", "data", "api", "security", "nfr", "integration", "ux", "obs", "ml")
# per-dimension allow-list of obligation ID prefixes; a dim absent here accepts any spec ID.
OBLIGATION_DIM_PREFIXES = {"ux": ("JRN-", "SCR-"), "obs": ("SLO-", "EXP-", "AEV-"), "ml": ("ML-",), "tests": ("AC-",)}
# standard gate rows every task carries, beyond its referenced IDs (from the engine's done-gate).
GATE_ROWS = [
    ("tests-first", "done-gate", "every AC- has a failing-capable test that drove the code"),
    ("tests:layers", "test-strategy", "every test level the slice touches per the test strategy exists & passes (unit/integration/contract/e2e/NFR-evidence as applicable)"),
    ("coverage", "test-strategy", ">= ratified coverage bar, DIFF-scoped: every changed src/** line executed by a test (a whole-tree % hides a small untested snippet in its slack; the diff scope removes the slack); or 'N/A — no src change'"),
    ("mutation", "test-strategy", ">= ratified mutation bar, DIFF-scoped: mutants on the changed logic killed (the mechanical proxy for 'the new assertions bite'); or 'N/A — no logic change'"),
    ("fitness:no-fakes", "done-gate", "no stub/mock/double/canned-response/unwired-fallback in src/"),
    ("fitness:architecture", "done-gate", "architecture fitness functions green"),
    ("spec-lint", "done-gate", "spec-lint clean"),
    ("deploy", "infra-ops", "the slice deploys to the first env of the ratified promotion path and a green e2e/smoke ran AGAINST that deployed env (the behavioural proof — evidence is the run, not just that the deploy file exists); or 'N/A — no new deployable surface'. If the env can't run yet, 'blocked — <env> not provisioned' (escalated), never PASS and never silently skipped"),
    ("ux:states", "ux", "every interaction state the task's ux cell names is exercised by a failing-capable state-tagged test; or 'N/A — headless'"),
    ("a11y", "ux", "per-slice accessibility scan (axe or equivalent) over every touched screen — zero critical/serious, the WCAG target named — plus the a11y cell's keyboard/focus path asserted; or 'N/A — headless'"),
    ("ux:rendered", "ux", "the touched screens rendered at each design-system breakpoint and conformant to the frozen prototype (evidence: the render/screenshot run); or 'N/A — headless'"),
    ("prototype-review", "ux", "the slice's prototype was human-reviewed at finalization ('frozen — <path>') or explicitly 'waived — <why>'; or 'N/A — headless'"),
    ("obs", "obs", "every obs-cell signal (SLO- telemetry · AEV- analytics event) emitted AND asserted by a test; or 'N/A — no observable surface'"),
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

def task_fields(tid):
    """Read both legacy `field: value` manifests and the current two-column `field | value` table."""
    p = task_file(tid)
    if not p:
        return None
    fields = []
    for line in p.read_text(encoding="utf-8", errors="replace").splitlines():
        s = line.strip()
        if s.startswith("|"):
            cells = [c.strip() for c in s.strip("|").split("|")]
            if len(cells) < 2:
                continue
            dim, val = cells[0], cells[1]
        else:
            m = re.match(r"^\s*([A-Za-z][\w-]*)\s*:\s*(.*)$", line)
            if not m:
                continue
            dim, val = m.group(1), m.group(2)
        dim = dim.strip(" *`_").lower()
        if not dim or dim in ("field", "dimension", "---") or set(dim) <= set("-: "):
            continue
        fields.append((dim, val))
    return fields

def task_obligations(tid):
    """Regenerate the obligation ID set from the task's frozen references - this is the un-gameable bar."""
    fields = task_fields(tid)
    if fields is None:
        return None
    obs = []  # preserve order, de-dup
    seen = set()
    for dim, val in fields:
        # The tests cell is an AC-keyed declaration in current task manifests. Pull ACs from it explicitly,
        # while ignoring incidental API-/T- ids in test intent; every declared AC must remain accountable even
        # if a malformed task omitted it from behavior. ux/obs/ml likewise admit only their own id types.
        if dim not in OBLIGATION_DIMS and dim != "tests":
            continue
        allowed = OBLIGATION_DIM_PREFIXES.get(dim)
        # an N/A cell imposes nothing — a cross-ref named inside its explanation ('N/A — headless, JRN-9
        # handled by T-020') must not mint an obligation. Scoped to the prefix-filtered dims (ux/obs/ml);
        # the classic dims keep their historic behaviour.
        if allowed and dim != "tests" and re.match(r"\s*[*`_]*\s*n/?a\b", val, re.I):
            continue
        for tok in IDTOK.findall(val):
            if allowed and not tok.startswith(allowed):
                continue
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
        req = {"behavior": "failing-capable test, passing", "tests": "failing-capable @covers-tagged test, passing",
               "api": "contract test (provider/consumer)",
               "security": "enforced + deny/over-limit path exercised by a test + evidenced",
               "nfr": "evidence test (measured, not asserted)",
               "data": "persistence + migration + owned retention/deletion trigger exercised",
               "integration": "real-path integration test (incl. failure/degradation path)",
               "domain": "realised + behaviour-tested",
               "ux": "every named interaction state realised + rendered vs the frozen prototype",
               "obs": "signal emitted + asserted by a test",
               "ml": "eval-harness evidence measured vs the stated bar (offline + online), incl. confidence-threshold/fallback + guardrail behaviour exercised"}.get(dim, "implemented + tested")
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

# The source tree is the un-gameable evidence for AC coverage. A raw AC token in a README, fixture, or comment
# is not coverage: the literal `@covers AC-NNN` tag must live in a recognizable test source that also contains
# a runnable test declaration (the mechanical proxy for "failing-capable"). Besides tests/, include common
# co-located layouts, while excluding vendored/build/tooling trees that could accidentally echo an AC id.
TEST_SOURCE_EXTS = {".py", ".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs", ".go", ".java", ".kt",
                    ".rb", ".cs", ".php", ".rs", ".scala", ".swift", ".feature", ".bats", ".exs",
                    ".dart", ".c", ".cc", ".cpp", ".cxx", ".fs", ".fsx", ".clj", ".cljs", ".groovy",
                    ".lua", ".sh", ".ps1", ".r", ".hs"}
TEST_PATH_PARTS = {"test", "tests", "__tests__", "e2e"}
COLOCATED_ROOTS = {"src", "app", "apps", "lib", "libs", "packages", "spec"}
# A monorepo may nest its source roots under a wrapper directory the conventions choose (code/apps/*/src/…),
# so a recognized source root can appear at ANY depth, not only position 0 — keying on parts[0] silently
# blinded the @covers evidence scan to every co-located test in a `code/`-rooted layout. The membership test
# below walks every path component, and GRILLSPEC_TEST_ROOTS (comma-separated) extends the recognized set for a
# genuinely non-standard LEAF source-dir name — the same lever tier_contract honors, so a project sets it once.
COLOCATED_ROOTS |= {r.strip().lower() for r in os.environ.get("GRILLSPEC_TEST_ROOTS", "").split(",") if r.strip()}
PRUNE_PARTS = {".git", ".grillspec", ".claude", ".codex", ".venv", "venv", "node_modules", "vendor", "dist", "build",
               "out", "coverage", "target", "__pycache__", ".next", ".tox"}
TEST_NAME = re.compile(r"(?:^test_|_test\.|[._](?:test|spec)s?\.|[._](?:e2e|int|integration|unit|contract)\.)", re.I)
CAMEL_TEST = re.compile(r"[a-z0-9](?:Test|Tests|Spec|Specs)\.[A-Za-z0-9]+$")
FAILING_CAPABLE = re.compile(
    r"\b(?:it|test|specify)(?:\s*\.\s*[A-Za-z_]\w*)*\s*\(|"
    r"\bTEST(?:_F|_P|_CASE)?\s*\(|"
    r"(?:^|\s)(?:async\s+)?def\s+test_[A-Za-z0-9_]*\s*\(|"
    r"(?:^|\s)func\s+test[A-Za-z0-9_]*\s*\(|"
    r"@\s*(?:[A-Za-z_]\w*\.)*(?:Test|ParameterizedTest|RepeatedTest|TestFactory)\b|"
    r"\[\s*(?:Fact|Theory|Test|TestCase|TestMethod)\b|"
    r"#\[\s*(?:test|tokio::test|async_std::test)\b|"
    r"\bfunction\s+test[A-Za-z0-9_]*\s*\(|"
    r"\((?:deftest|facts?)\s+|"
    r"\btest_(?:that|case)\s*\(|"
    r"^\s*(?:Scenario(?:\s+Outline)?):|"
    r"^\s*@test\s+[\"']|"
    r"^\s*(?:it|specify|test)\s+[\"'].*(?:do|\{|\$)",
    re.I | re.M)

def _test_source(p):
    try:
        rel = p.relative_to(ROOT)
    except ValueError:
        return False
    parts = [x.lower() for x in rel.parts]
    if not p.is_file() or p.suffix.lower() not in TEST_SOURCE_EXTS or any(x in PRUNE_PARTS for x in parts[:-1]):
        return False
    in_test_tree = any(x in TEST_PATH_PARTS for x in parts[:-1])
    colocated = bool(any(x in COLOCATED_ROOTS for x in parts[:-1]) and
                     (TEST_NAME.search(p.name) or CAMEL_TEST.search(p.name)))
    return in_test_tree or colocated

def _without_comments(text):
    """Remove common comments before looking for a test declaration; @covers itself is checked on raw text."""
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.S)
    code = []
    for line in text.splitlines():
        s = line.lstrip()
        if s.startswith(("//", "--")) or (s.startswith("#") and not s.startswith("#[")):
            continue
        line = re.sub(r"//.*$|--.*$", "", line)
        code.append(line)
    return "\n".join(code)

_test_sources = None
def _load_test_sources():
    global _test_sources
    if _test_sources is None:
        _test_sources = []
        # os.walk lets us prune vendor/build trees before descending; ROOT.rglob would still traverse every
        # node_modules entry even if _test_source later rejected it.
        for base, dirs, files in os.walk(ROOT):
            dirs[:] = sorted(d for d in dirs if d.lower() not in PRUNE_PARTS)
            for name in sorted(files):
                p = pathlib.Path(base) / name
                if not _test_source(p):
                    continue
                try:
                    txt = p.read_text(encoding="utf-8", errors="replace")
                except Exception:
                    continue
                _test_sources.append((txt, FAILING_CAPABLE.search(_without_comments(txt)) is not None))
    return _test_sources

def covered_in_source(tok):
    token = re.compile(r"(?<![A-Za-z0-9-])" + re.escape(tok) + r"(?![A-Za-z0-9._-])", re.I)
    for txt, capable in _load_test_sources():
        if not capable:
            continue
        for line in txt.splitlines():
            tag = re.search(r"@covers\b", line, re.I)
            if tag and token.search(line[tag.end():]):
                return True
    return False

# The state sibling of @covers: a UI slice's interaction states are covered only by a literal `@state:<name>`
# tag in a failing-capable test source — the mechanical teeth behind the ux:states gate row (without it the
# row is PASS-by-assertion). Names come from the task's own ux cell.
def ux_cell_states(cell):
    m = re.search(r"(?i)\bstates?\s*[:\-—]\s*([^|]*)", cell or "")
    if not m:
        return []
    seg = re.split(r"[→|]", m.group(1))[0]                     # stop at the prototype pointer
    return [s for s in (t.strip(" *`_").lower() for t in re.split(r"[·,;/]", seg)) if re.fullmatch(r"[a-z0-9][a-z0-9 _-]*", s)]

def state_covered(name):
    tag = re.compile(r"@state:\s*" + re.escape(name.replace(" ", "-")) + r"(?![A-Za-z0-9_-])", re.I)
    for txt, capable in _load_test_sources():
        if capable and tag.search(txt):
            return True
    return False

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
    if ASSUME_DONE:
        status = "done"
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

    # 3c. a false N/A cannot discharge a gate row the task's own manifest says applies: a slice whose `ux` cell
    #     is non-N/A cannot mark ux:states/a11y/ux:rendered "N/A — headless", and a slice whose `obs` cell names
    #     signals cannot mark the obs row N/A. The record checker sees both files, so the contradiction is
    #     mechanically visible - this is the record-level sibling of the spec-lint ux/a11y consistency check.
    def _dim_cell(name):
        for dim, val in (task_fields(tid) or []):
            if dim == name:
                return val
        return None
    def _cell_na(val):
        c = re.sub(r"[*`_]", "", val or "").strip().lower()
        return not c or re.match(r"n/?a\b|none\b|[-—]+$", c) is not None
    ux_cell = _dim_cell("ux")
    if ux_cell is not None and not _cell_na(ux_cell):
        for k in ("ux:states", "a11y", "ux:rendered"):
            st, ev = rows.get(k, ("", ""))
            if re.match(r"\s*n/?a\b", st or "", re.I):
                add("ERROR", where, "row '%s' is N/A but the task's ux cell is non-N/A (\"%s…\") — a UI slice cannot discharge its rendered-surface gate with 'N/A — headless'." % (k, ux_cell.strip()[:40]))
            elif is_pass(st) and not re.search(r"[\w.-]+/[\w./-]+", ev or ""):
                add("ERROR", where, "row '%s' is PASS with no on-disk evidence path — a pathless PASS is an assertion, not evidence; cite the state-tagged test / scan output / render run." % k)
        # the prototype-review row must POSITIVELY read frozen/reviewed or waived for a UI slice — the
        # record-level sibling of spec-lint's afk gate, so a solo run can't merge a never-reviewed screen.
        pst, pev = rows.get("prototype-review", ("", ""))
        if not re.search(r"\b(frozen|reviewed|waiv)", (pst + " " + pev), re.I):
            add("ERROR", where, "the prototype-review row does not read 'frozen — <path>' / 'reviewed' / 'waived — <why>' but the task's ux cell is non-N/A — an unreviewed screen cannot ride a done-claim.")
        # state teeth: every state the ux cell names has a literal @state:<name> tag in a failing-capable
        # test source (the state sibling of the @covers AC check — without it ux:states is unverifiable).
        for sname in ux_cell_states(ux_cell):
            if not state_covered(sname):
                add("ERROR", where, "ux-cell state '%s' has no failing-capable test source carrying an `@state:%s` tag — every named interaction state needs its state-tagged test." % (sname, sname.replace(" ", "-")))
    obs_cell = _dim_cell("obs")
    if obs_cell is not None and not _cell_na(obs_cell):
        st, ev = rows.get("obs", ("", ""))
        if re.match(r"\s*n/?a\b", st or "", re.I):
            add("ERROR", where, "row 'obs' is N/A but the task's obs cell names signals (\"%s…\") — every named signal must be emitted and asserted by a test." % obs_cell.strip()[:40])
        elif is_pass(st) and not re.search(r"[\w.-]+/[\w./-]+", ev or ""):
            add("ERROR", where, "row 'obs' is PASS with no on-disk evidence path — cite the test(s) asserting the emissions; a pathless PASS is an assertion, not evidence.")

    # 4. tests-first evidence - each AC-/API-/EVT- obligation traced to a passing row in the matrix, AND each
    #    task-declared AC has a literal `@covers AC-NNN` tag in a failing-capable TEST SOURCE, so neither a
    #    self-authored matrix nor an incidental source comment can claim a test the tree doesn't contain.
    for tok, dim in obs:
        if tok.startswith("AC-"):
            src = covered_in_source(tok)
            if src is False:
                add("ERROR", where, "%s has no failing-capable test source carrying an `@covers %s` tag in the project test tree (a matrix row or incidental source comment can't substitute for the actual test)." % (tok, tok))
        if not tok.startswith(("AC-", "API-", "EVT-")):
            continue
        if trace_txt is None:
            add("WARN", where, "no traceability matrix (%s) to confirm %s is covered by a passing test." % (TRACE, tok))
            continue
        traced = any(tok in ln and ("✓" in ln or re.search(r"\bpass\b", ln, re.I)) for ln in trace_txt.splitlines())
        if not traced:
            add("ERROR", where, "%s has no passing row in the traceability matrix — a back-filled or missing test, not test-first." % tok)

    # 4b. an NFR obligation row claiming PASS must cite a MEASUREMENT against its bar, not an assertion -
    #     "load test looks good" is exactly how an NFR ships unmeasured. Unit-agnostic (ms/rps/%/min all
    #     legal), so the rule is loose: the evidence needs at least one number AND a bar/comparator cue
    #     (bar · target · threshold · vs · within · >= / <= / < / > / >=-glyphs). N/A-with-reason passes as
    #     everywhere; the numeric coverage/mutation rows keep their stricter %-parser below.
    for tok, dim in obs:
        if dim != "nfr" or tok not in rows:
            continue
        st, ev = rows[tok]
        if not is_pass(st) or re.match(r"\s*n/?a\b", st or "", re.I) or re.match(r"\s*n/?a\b", ev or "", re.I):
            continue
        if not (re.search(r"\d", ev or "") and re.search(r"(?i)>=|<=|≥|≤|<|>|\b(bar|target|threshold|budget|vs|within)\b", ev or "")):
            add("ERROR", where, "NFR row '%s' is PASS but its evidence (\"%s\") cites no measurement against a bar - state the measured value and its target (e.g. 'p95 212ms vs target 300ms'); an unmeasured NFR PASS is an assertion." % (tok, (ev or "").strip()[:50]))

    # 5. evidence integrity - a path-like evidence cell must exist on disk.
    for key, (st, ev) in rows.items():
        for tok in re.findall(r"[\w./-]+/[\w./-]+", ev):
            tok = tok.rstrip(".,;:")
            if tok.startswith(EVIDENCE_PREFIXES) and not (ROOT / tok).exists():
                add("ERROR", where, "row '%s' cites evidence '%s' which does not exist on disk." % (key, tok))

    # 6. numeric bars - coverage/mutation measured >= stated bar. A present, non-N/A row MUST cite a measured
    #    value AND its bar in a parseable form, else the gate is unverifiable - free-form evidence ("looks good")
    #    is exactly how a mutation/coverage gate gets silently bypassed. (N/A - e.g. no domain-logic change - is
    #    a legitimate skip and carries its reason.)
    for key in ("coverage", "mutation"):
        if key in rows:
            st, ev = rows[key]
            if re.match(r"\s*n/?a\b", st, re.I) or re.match(r"\s*n/?a\b", ev, re.I):
                # an N/A must justify itself - a bare "N/A"/"—" silently skips the assertion-quality gate
                # (mutation especially: it's the one mechanical proxy for "the tests actually bite").
                leftover = re.sub(r"n/?a|—|[-:\s]", "", st + " " + ev, flags=re.I)
                if not leftover:
                    add("ERROR", where, "row '%s' is N/A but states no reason - a bare N/A silently skips the "
                                        "%s gate; state why (e.g. 'N/A — no domain-logic change')." % (key, key))
                continue
            # the measured value is the first PERCENT-tagged number that is NOT the bar. Requiring the '%'
            # excludes task-ids / versions / per-file digits ('T-002', 'v1.2'), and skipping the bar's own
            # position stops the threshold being read as the metric. (The prior nums[0] grabbed the first digit
            # ANYWHERE - so 'T-002 ... 82% ≥ 70%' read '002' as the score and false-failed a passing row.)
            # Word keywords cannot be preceded by an identifier/path char (word, dot, slash, or hyphen): a
            # plain \b still matches the `floor` segment in `promotion-floor.ts` and hijacks the following
            # module percentage as the bar. Symbols stay unanchored (a boundary is meaningless beside them).
            bar_m = re.search(r"(?:(?<![\w./-])(?:bar|threshold|target|min(?:imum)?|floor)\b|>=|≥|⩾)\D*(\d+(?:\.\d+)?)", ev, re.I)
            pcts = [(m.start(1), float(m.group(1))) for m in re.finditer(r"(\d+(?:\.\d+)?)\s*%", ev)]
            measured = next((v for pos, v in pcts if not bar_m or pos != bar_m.start(1)), None) if bar_m else None
            if measured is None or not bar_m:
                add("ERROR", where, "row '%s' must cite a measured value AND its bar as %%-tagged numbers (e.g. "
                                    "'86%% (bar 80%%)', or 'threshold'/'target'/'>='/'≥') so the gate is checkable - "
                                    "free-form evidence can't be verified." % key)
            else:
                bar = float(bar_m.group(1))
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
