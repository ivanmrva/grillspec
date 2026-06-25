#!/usr/bin/env python3
# check_no_fakes.py - a coarse, high-precision tripwire against non-production code shipped in the source tree.
#
# Why a generic tripwire AND a per-language fitness function: the most ACCURATE no-fakes check is language-
# specific (a real import-graph rule via ArchUnit / ts-arch / import-linter, which the test strategy derives).
# But that fitness function is authored per project and can simply never be written - the same adherence gap
# that lets a fake reach production in the first place. THIS ships in the box and fires even when no fitness
# function exists: a cross-language backstop, not a replacement. It is deliberately conservative - it flags the
# signals that are almost always wrong in production, and supports an allowlist for the rare legitimate case,
# because a noisy gate gets `--no-verify`d and takes the good gates down with it.
#
# ERROR (a test double or a fake wired into the shipping path):
#   - a class/def/type DEFINED under src/ whose name is Fake*/Stub*/Mock*/Dummy* (or fake_/stub_/mock_/dummy_);
#   - an IMPORT of a known mocking/test-double library from production code.
# WARN (a likely placeholder - review, don't necessarily block):
#   - an identifier containing hardcoded/canned/placeholder; a NotImplemented/"not implemented" body on a
#     non-abstract path; an unconfigured-fallback guard ("if ... not configured: return <literal>").
# Suppress a finding with an inline `no-fakes: allow <reason>` comment on the line, or a path/symbol/substring
# entry in `.claude/no-fakes-allow.txt`.
#
# No-ops cleanly when no production source dir exists. Run from the project root:
#   python3 tools/check_no_fakes.py [project_root] [--src src,app,lib] [--strict]   (--strict: WARN -> ERROR)
import sys, re, pathlib

args = [a for a in sys.argv[1:] if not a.startswith("--")]
ROOT = pathlib.Path(args[0] if args else ".")
SRC_DIRS = ["src"]
for i, a in enumerate(sys.argv):
    if a == "--src" and i + 1 < len(sys.argv):
        SRC_DIRS = [s for s in sys.argv[i + 1].split(",") if s]
STRICT = "--strict" in sys.argv

CODE_EXT = {".py", ".js", ".jsx", ".ts", ".tsx", ".go", ".java", ".kt", ".rb", ".cs", ".php", ".rs", ".scala", ".swift"}
# a file is a TEST file (doubles are legitimate here) - never scanned.
TEST_PARTS = ("/tests/", "/test/", "/__tests__/", "/spec/", "/specs/", "/testing/", "/__mocks__/")
TEST_NAME = re.compile(r"(^test_|_test\.|\.test\.|\.spec\.|_spec\.|Test\.|Tests\.|Spec\.)", re.I)

DEF_FAKE = re.compile(
    r"\b(?:class|def|func|function|type|interface|struct|record|object|trait)\s+"
    r"(?P<name>(?:Fake|Stub|Mock|Dummy)[A-Z0-9_]\w*|(?:fake|stub|mock|dummy)_\w+)\b")
MOCK_IMPORT = re.compile(
    r"\b(?:unittest\.mock|from\s+mock\b|import\s+mock\b|sinon|testdouble|@?jest|nock|"
    r"org\.mockito|mockito|easymock|moq|nsubstitute|fakeiteasy|gomock|golang/mock|testify/mock|mockk)\b", re.I)
WARN_IDENT = re.compile(r"\b\w*(?:hardcoded|canned|placeholder)\w*\b", re.I)
WARN_NOTIMPL = re.compile(r"\b(?:raise\s+NotImplementedError|NotImplementedError\(|throw\s+new\s+Error\(\s*['\"]not implemented|TODO:?\s*implement)\b", re.I)
WARN_FALLBACK = re.compile(r"\bif\b[^\n]*\b(?:not\s+configured|unconfigured|no\s+\w*\s*(?:key|credential|token)|missing\s+\w*\s*(?:key|credential|config))\b", re.I)

allow = []
allowf = ROOT / ".claude" / "no-fakes-allow.txt"
if allowf.exists():
    for ln in allowf.read_text(encoding="utf-8", errors="replace").splitlines():
        ln = ln.split("#", 1)[0].strip()
        if ln:
            allow.append(ln)

def allowed(where, msg):
    return any(a in where or a in msg for a in allow)

F = []
def add(sev, where, msg):
    if sev == "WARN" and STRICT:
        sev = "ERROR"
    if not allowed(where, msg):
        F.append((sev, where, msg))

roots = [ROOT / d for d in SRC_DIRS if (ROOT / d).is_dir()]
if not roots:
    print("check_no_fakes: no production source dir (%s) under %s - nothing to scan." % ("/".join(SRC_DIRS), ROOT))
    sys.exit(0)

scanned = 0
for base in roots:
    for p in sorted(base.rglob("*")):
        if not p.is_file() or p.suffix not in CODE_EXT:
            continue
        posix = "/" + p.as_posix().strip("/")
        if any(part in posix for part in TEST_PARTS) or TEST_NAME.search(p.name):
            continue
        scanned += 1
        rel = p.relative_to(ROOT).as_posix()
        for n, line in enumerate(p.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
            if "no-fakes: allow" in line:
                continue
            where = "%s:%d" % (rel, n)
            m = DEF_FAKE.search(line)
            if m:
                add("ERROR", where, "defines '%s' - a test double in the production tree (move it under tests/)." % m.group("name"))
            if MOCK_IMPORT.search(line) and not line.lstrip().startswith(("#", "//", "*")):
                add("ERROR", where, "imports a mocking/test-double library into production code.")
            if WARN_NOTIMPL.search(line):
                add("WARN", where, "an unimplemented/placeholder body on a production path.")
            elif WARN_IDENT.search(line):
                add("WARN", where, "a hardcoded/canned/placeholder identifier in production code.")
            if WARN_FALLBACK.search(line):
                add("WARN", where, "an 'unconfigured -> fallback' guard - an absent dependency should fail the test, not be coded around.")

order = {"ERROR": 0, "WARN": 1}
for sev, where, msg in sorted(F, key=lambda x: (order[x[0]], x[1])):
    print("%-5s %-32s %s" % (sev, where, msg))
e = sum(1 for x in F if x[0] == "ERROR")
w = len(F) - e
print("\n%d error(s), %d warning(s) over %d production file(s)." % (e, w, scanned))
sys.exit(1 if e else 0)
