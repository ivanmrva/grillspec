#!/usr/bin/env python3
# tier_contract.py - shared parsing of the test-strategy tier contract + test-file tier classification, used by
# check_test_tiers.py / check_mock_budget.py / check_e2e_target.py (and audit-build's aggregate re-run). ONE
# source of truth so the three gates can't drift on how they read a real, human-authored levels.md or classify a
# co-located test file - the drift that let a parsing bug hide in three copies. Stdlib only; no side effects.
import os
import re
import pathlib

# canonical tier vocabulary + synonyms (journey/smoke/system/acceptance/nfr -> e2e; int -> integration; cdc -> contract)
TIER_TOKENS = ("unit", "integration", "int", "contract", "cdc", "e2e", "journey", "smoke", "system", "acceptance", "nfr")
_SYNONYM = {"journey": "e2e", "smoke": "e2e", "system": "e2e", "acceptance": "e2e", "nfr": "e2e",
            "int": "integration", "cdc": "contract"}

def canon(tok):
    return _SYNONYM.get(tok.lower(), tok.lower())

# A test DECLARATION the runner can execute and fail - the shared core check_task_record.py and
# check_orphan_tests.py both key on (ONE definition, so a framework added for one gate can't silently
# be invisible to the other). A helper/fixture file never declares one, so it is never flagged.
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

# a test's tier from a tests/<tier>/ directory, or from a tier token in the filename (foo.int.test.ts)
_TIER_SEG = re.compile(r"/(?:tests?|specs?|__tests__)/(?:.*/)?(unit|integration|contract|e2e|journey|smoke|system|acceptance|nfr)(?:/|_|-|\.|$)", re.I)
_FNAME_TIER = re.compile(r"(?:^|[._-])(unit|integration|int|contract|e2e|journey|smoke|system|acceptance|nfr)[._-]", re.I)
# is this file a TEST file at all - lets a co-located SOURCE root be scanned without counting production code
_TESTFILE = re.compile(r"[._](?:test|spec)s?\.|(?:^|/)test_|[._](?:e2e|int|integration|unit|contract|journey|smoke|nfr|acceptance|system)\.", re.I)
# the JVM/C#/PHP suffix convention (PayTest.java, PayTests.cs, PaySpec.kt) - case-SENSITIVE on purpose:
# a case-insensitive match would classify a production 'Latest.java' as a test and blind the gates to it.
_CAMEL_TEST = re.compile(r"[a-z0-9](?:Test|Tests|Spec|Specs)\.[a-z]+$")
# directories never worth walking (keeps a co-located src/ scan off vendored/build trees)
PRUNE = re.compile(r"/(?:node_modules|dist|build|out|coverage|vendor|\.git|\.grillspec|\.claude|\.codex|\.venv|venv|__pycache__|\.next|target|\.tox)/", re.I)
# default roots: test dirs AND common source roots (co-located tests) - the test-file filter keeps production out.
# A monorepo can root its tree under a wrapper dir the conventions choose (code/, services/, …) that none of the
# defaults name, which would make iter_test_files (root/<d> only) find NOTHING and every tier/mock/skip/orphan
# gate silently pass. GRILLSPEC_TEST_ROOTS (comma-separated) folds those wrapper roots into the default set so a
# project sets it ONCE for all six tools; an explicit --tests still overrides. (The per-tool --tests flag remains
# the ad-hoc escape; this is the persistent, project-level one shared with check_task_record's COLOCATED_ROOTS.)
DEFAULT_ROOTS = "tests,test,src,app,apps,lib,libs,packages,e2e"
_extra_roots = ",".join(r.strip() for r in os.environ.get("GRILLSPEC_TEST_ROOTS", "").split(",") if r.strip())
if _extra_roots:
    DEFAULT_ROOTS = DEFAULT_ROOTS + "," + _extra_roots
CODE_EXT = {".py", ".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs", ".go", ".java", ".kt", ".rb", ".cs", ".php",
            ".rs", ".scala", ".swift", ".json", ".feature"}

def classify(posix, name):
    """The canonical tier for a TEST file, or None if the file isn't a test (skips production code and helpers).
    tests/<tier>/… -> that tier; a co-located foo.int.test.ts -> integration; a bare foo.test.ts -> unit."""
    m = _TIER_SEG.search(posix)
    if m:
        return canon(m.group(1))
    if _TESTFILE.search(name) or _CAMEL_TEST.search(name):
        m2 = _FNAME_TIER.search(name)
        return canon(m2.group(1)) if m2 else "unit"
    return None

def iter_test_files(root, test_dirs):
    """Yield (posix, name, path) for every TEST file under the given roots, pruning vendor/build dirs and dups."""
    seen = set()
    for d in test_dirs:
        base = root / d
        if not base.is_dir():
            continue
        for p in sorted(base.rglob("*")):
            if not p.is_file() or p.suffix not in CODE_EXT:
                continue
            posix = "/" + p.as_posix().strip("/")
            if PRUNE.search(posix) or posix in seen:
                continue
            seen.add(posix)
            if classify(posix, p.name) is not None:
                yield posix, p.name, p

def load_contract(path):
    """{tier: {col: value}} from the levels.md tier-contract table. Robust to a real, human-authored table:
    skips the <!-- scope … --> comment (which also names the columns), requires a |---| separator UNDER the
    header row (so a prose line that merely mentions the columns isn't mistaken for the table), and strips
    markdown (bold/backtick) from column names, cell values, and the tier key (which may be bold + parenthetical,
    e.g. '**system / journey (e2e)**')."""
    path = pathlib.Path(path)
    if not path.exists():
        return {}
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    clean = lambda c: re.sub(r"[*`]", "", c).strip()
    for i, ln in enumerate(lines):
        s = ln.strip()
        if s.startswith("<!--") or "|" not in s:
            continue
        if not (re.search(r"\btier\b", s, re.I) and re.search(r"mock-?ceiling", s, re.I)):
            continue
        if i + 1 >= len(lines) or not (re.match(r"^\s*\|?[\s:|-]+\|?\s*$", lines[i + 1]) and "-" in lines[i + 1]):
            continue  # a real markdown table header is immediately followed by a |---| separator row
        cols = [clean(c).lower().replace(" ", "-") for c in s.strip("|").split("|")]
        out = {}
        for dl in lines[i + 2:]:
            t = dl.strip()
            if not t.startswith("|"):
                break
            if re.match(r"^\|?[\s:|-]+\|?$", t):
                continue
            cells = [clean(c) for c in t.strip("|").split("|")]
            if len(cells) < len(cols):
                continue
            row = dict(zip(cols, cells))
            tier = next((canon(tok) for tok in re.findall(r"[a-z0-9]+", row.get("tier", "").lower()) if tok in TIER_TOKENS), "")
            if tier:
                out[tier] = row
        return out
    return {}
