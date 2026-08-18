#!/usr/bin/env python3
# check_orphan_tests.py - the REVERSE direction of traceability: every behavioral test traces to a live
# spec driver.
#
# Why it exists (the missing half of @covers): check_task_record.py proves the forward direction - every
# task-declared AC- has a @covers-tagged, failing-capable test. Nothing proved the reverse: a test (and the
# behavior it drives) with NO spec driver passes every gate. That is exactly the shape of DRIFT - an ad-hoc
# instruction given mid-task in chat ("also make it do X") that was implemented directly, so the code grew
# past the spec and no upstream artifact ever learned about it. Chat is SPEC input, not code input: the
# behavior's ID (AC-/API-/DATA-/...) is minted or amended in its owning spec area FIRST, then the tagged
# test, then the code. This tripwire makes the untagged shortcut mechanically red - and on an EXISTING
# project its first run doubles as the drift detector: every finding is a behavior the spec never absorbed.
#
# ERROR:
#   - an ORPHAN test source: a failing-capable test file carrying not one driver tag
#     (`@covers <ID>` / `@state:<name>`) - behavior nothing in the spec demands;
#   - a DANGLING driver: a `@covers` ID that exists nowhere under spec/ - a tag minted to appease the
#     gate, or an ID the spec has since dropped;
#   - an OFF-GRAMMAR test file: a file in a dedicated test tree that DECLARES tests but matches no
#     recognized test-file naming pattern (test_* / *.test.* / *_test.* / *Spec.*) - the naming grammar
#     is the gates' visibility contract, so an off-grammar file silently escapes the tier/mock/skip/
#     orphan gates entirely (and the classifier can't tier it). Gherkin `.feature` files are recognized
#     by extension and exempt.
#
# Granularity is per FILE, on purpose: per-case parsing across every language is not tractable, and one
# tagged case per file is the workable mechanical bar - the conformance review owns the per-case judgment
# (does every behavior in the diff have a driving ID). Suppress with an inline `no-orphans: allow <reason>`
# comment (file-level for the orphan finding, line-level for a dangling tag) or a path/substring entry in
# `.grillspec/no-orphans-allow.txt` - the legit cases are the driver-free suites by design: architecture
# fitness functions, generated harnesses, the plugin's own tooling tests.
#
# No-ops cleanly when there is no spec/ tree (nothing to reconcile against) or no test files yet.
# Run from the project root:
#   python3 tools/check_orphan_tests.py [project_root] [--tests <roots>]
import sys, re, pathlib
from tier_contract import iter_test_files, classify, DEFAULT_ROOTS, CODE_EXT, PRUNE

args = [a for a in sys.argv[1:] if not a.startswith("--")]
ROOT = pathlib.Path(args[0] if args else ".")
def opt(flag, default):
    for i, a in enumerate(sys.argv):
        if a == flag and i + 1 < len(sys.argv):
            return sys.argv[i + 1]
    return default
TEST_DIRS = [s for s in opt("--tests", DEFAULT_ROOTS).split(",") if s]

SPEC = ROOT / "spec"
if not SPEC.is_dir():
    print("check_orphan_tests: no spec/ under %s - nothing to reconcile against." % ROOT)
    sys.exit(0)

# -- driver tags. An ID token is uppercase-prefixed (AC-001, API-002a, T-014) so prose like `user-123`
# -- on the same line never reads as a driver. Keep the tag semantics in sync with check_task_record.py
# -- (@covers) and its @state sibling.
COVERS = re.compile(r"@covers\b", re.I)
STATE_TAG = re.compile(r"@state:[A-Za-z0-9][A-Za-z0-9_-]*")
ID_TOKEN = re.compile(r"(?<![A-Za-z0-9-])[A-Z]{1,8}-[A-Za-z0-9][A-Za-z0-9._-]*")

# -- failing-capable: the file contains a runnable test DECLARATION (the mechanical proxy shared with
# -- check_task_record.py - keep the pattern cores in sync). A helper/fixture file never declares one,
# -- so it is never flagged.
from tier_contract import FAILING_CAPABLE

def _without_comments(text):
    """Strip common comments before looking for a test declaration; the driver tags themselves are read
    on raw text (they live in comments by convention)."""
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.S)
    code = []
    for line in text.splitlines():
        s = line.lstrip()
        if s.startswith(("//", "--")) or (s.startswith("#") and not s.startswith("#[")):
            continue
        line = re.sub(r"//.*$|--.*$", "", line)
        code.append(line)
    return "\n".join(code)

# -- the spec-ID universe: an ID "exists" when its token appears anywhere in the spec tree (definition or
# -- reference - the spec lint owns definition-site discipline; this only needs "the spec knows this ID").
SPEC_EXTS = {".md", ".yaml", ".yml", ".json"}
_spec_texts = []
for p in sorted(SPEC.rglob("*")):
    if p.is_file() and p.suffix.lower() in SPEC_EXTS:
        try:
            _spec_texts.append(p.read_text(encoding="utf-8", errors="replace"))
        except Exception:
            pass

_known = {}
def in_spec(tok):
    if tok not in _known:
        pat = re.compile(r"(?<![A-Za-z0-9-])" + re.escape(tok) + r"(?![A-Za-z0-9_-])")
        _known[tok] = any(pat.search(t) for t in _spec_texts)
    return _known[tok]

allow = []
allowf = ROOT / ".grillspec" / "no-orphans-allow.txt"
if allowf.exists():
    for ln in allowf.read_text(encoding="utf-8", errors="replace").splitlines():
        ln = ln.split("#", 1)[0].strip()
        if ln:
            allow.append(ln)

def allowed(where, msg):
    return any(a in where or a in msg for a in allow)

F = []
def add(sev, where, msg):
    if not allowed(where, msg):
        F.append((sev, where, msg))

ORPHAN = ("no spec driver in this failing-capable test source - behavior nothing in the spec demands is "
          "DRIFT. Chat is spec input: mint/amend the driving ID (AC-/API-/...) in its owning area first, "
          "then tag the test (`@covers <ID>` / `@state:<name>`). A legitimately driver-free suite "
          "(fitness functions, generated harness) carries `no-orphans: allow <reason>`.")

tested = 0
for posix, name, p in iter_test_files(ROOT, TEST_DIRS):
    tested += 1
    rel = p.relative_to(ROOT).as_posix()
    txt = p.read_text(encoding="utf-8", errors="replace")
    if not FAILING_CAPABLE.search(_without_comments(txt)):
        continue                                   # helper/fixture-shaped: declares no runnable test
    drivers = 0
    waived_file = False
    for n, line in enumerate(txt.splitlines(), 1):
        if "no-orphans: allow" in line:
            waived_file = True
            continue
        if STATE_TAG.search(line):
            drivers += 1
        m = COVERS.search(line)
        if not m:
            continue
        toks = ID_TOKEN.findall(line[m.end():])
        drivers += len(toks)
        for tok in toks:
            if not in_spec(tok):
                add("ERROR", "%s:%d" % (rel, n),
                    "dangling driver: @covers %s names an ID that exists nowhere under spec/ - a tag "
                    "must point at a live spec ID; mint/amend it in its owning area (or fix the tag)." % tok)
    if drivers == 0 and not waived_file:
        add("ERROR", rel, ORPHAN)

# -- the off-grammar sweep: files in a DEDICATED test tree (never co-located src - a production helper
# -- legitimately named test_connection() must not fire) that declare tests but that classify() cannot
# -- see. Being invisible to the classifier means being invisible to every gate built on it.
TEST_DIR_SEG = re.compile(r"/(?:tests?|__tests__|specs?|e2e)/", re.I)
misnamed = 0
_seen_offgrammar = set()
for d in TEST_DIRS:
    base = ROOT / d
    if not base.is_dir():
        continue
    for p in sorted(base.rglob("*")):
        if not p.is_file() or p.suffix not in CODE_EXT or p.suffix == ".feature":
            continue
        posix = "/" + p.as_posix().strip("/")
        if PRUNE.search(posix) or posix in _seen_offgrammar or not TEST_DIR_SEG.search(posix + "/"):
            continue
        _seen_offgrammar.add(posix)
        if classify(posix, p.name) is not None:
            continue                               # visible to the gates - the main loop handled it
        txt = p.read_text(encoding="utf-8", errors="replace")
        if "no-orphans: allow" in txt:
            continue
        if FAILING_CAPABLE.search(_without_comments(txt)):
            misnamed += 1
            add("ERROR", p.relative_to(ROOT).as_posix(),
                "unrecognized test naming - this file declares tests but matches no recognized "
                "test-file pattern, so it is INVISIBLE to the tier/mock/skip/orphan gates (they only "
                "see test_* / *.test.* / *_test.* / *Spec.*-shaped files). Rename it into the grammar "
                "(or `no-orphans: allow <reason>` for a deliberate exception).")

if tested == 0 and misnamed == 0 and not F:
    print("check_orphan_tests: no test files under %s - nothing to scan." % ROOT)
    sys.exit(0)

for sev, where, msg in sorted(F, key=lambda x: (x[0], x[1])):
    print("%-5s %-32s %s" % (sev, where, msg))
e = sum(1 for x in F if x[0] == "ERROR")
print("\n%d error(s) over %d test file(s)." % (e, tested))
sys.exit(1 if e else 0)
