#!/usr/bin/env python3
# check_config_drift.py - the deploy-side accountability check: the config the CODE reads at runtime must match
# the config the spec DECLARES for operators to provision. Drift here is the classic "works on my machine,
# missing env var in prod" outage: a developer reads a new env var in code but never adds it to the environment
# matrix, so the operator never provisions it and the app crashes on first run in the new environment.
#
# It reconciles two sides:
#   code-reads (os.getenv / process.env / ENV[...] / System.getenv / ...) under the production source tree, and
#   spec-declares (the key column of infra-ops/environments.md).
# ERROR: the code reads a key the matrix does not declare - the operator cannot provision what isn't written down.
# WARN:  the matrix declares an env-var-shaped key no code reads - dead/stale config (or consumed by infra, not
#        app code: PORT, DATABASE_URL injected by the platform) - suppress those via the allowlist.
# Suppress with an inline `config-drift: allow` comment, or a key/substring in `.claude/config-drift-allow.txt`.
#
# No-ops cleanly when there is no environments.md or no source dir. Run from the project root:
#   python3 tools/check_config_drift.py [project_root] [--src src,app,lib] [--spec spec]
import sys, re, pathlib

args = [a for a in sys.argv[1:] if not a.startswith("--")]
ROOT = pathlib.Path(args[0] if args else ".")
SRC_DIRS = ["src"]
SPEC_DIR = "spec"
for i, a in enumerate(sys.argv):
    if a == "--src" and i + 1 < len(sys.argv):
        SRC_DIRS = [s for s in sys.argv[i + 1].split(",") if s]
    if a == "--spec" and i + 1 < len(sys.argv):
        SPEC_DIR = sys.argv[i + 1]

# locate the environment matrix (the declared side).
ENV_MD = None
for cand in [ROOT / SPEC_DIR / "09-solution" / "infra-ops" / "environments.md",
             ROOT / SPEC_DIR / "delivery" / "infra-ops" / "environments.md"]:
    if cand.exists():
        ENV_MD = cand; break
if ENV_MD is None:
    for cand in (ROOT / SPEC_DIR).rglob("infra-ops/environments.md"):
        ENV_MD = cand; break
if ENV_MD is None:
    print("check_config_drift: no infra-ops/environments.md under %s/%s - nothing to reconcile." % (ROOT, SPEC_DIR))
    sys.exit(0)

CODE_EXT = {".py", ".js", ".jsx", ".ts", ".tsx", ".go", ".java", ".kt", ".rb", ".cs", ".php", ".rs", ".scala", ".swift"}
TEST_PARTS = ("/tests/", "/test/", "/__tests__/", "/spec/", "/specs/", "/testing/", "/__mocks__/")
TEST_NAME = re.compile(r"(^test_|_test\.|\.test\.|\.spec\.|_spec\.|Test\.|Tests\.|Spec\.)", re.I)
ENVVAR = re.compile(r"^[A-Z][A-Z0-9]*(?:_[A-Z0-9]+)+$|^[A-Z][A-Z0-9_]{3,}$")   # UPPER_SNAKE-ish key shapes

# every way code reads an env var, capturing the key name.
READERS = [
    re.compile(r"os\.environ(?:\.get)?\(\s*['\"]([A-Za-z_][\w]*)['\"]"),     # python os.environ['X'] / .get('X')
    re.compile(r"os\.environ\[\s*['\"]([A-Za-z_][\w]*)['\"]\s*\]"),
    re.compile(r"os\.getenv\(\s*['\"]([A-Za-z_][\w]*)['\"]"),                 # python os.getenv('X')
    re.compile(r"process\.env\.([A-Za-z_][\w]*)"),                            # node process.env.X
    re.compile(r"process\.env\[\s*['\"]([A-Za-z_][\w]*)['\"]\s*\]"),
    re.compile(r"import\.meta\.env\.([A-Za-z_][\w]*)"),                       # vite
    re.compile(r"Deno\.env\.get\(\s*['\"]([A-Za-z_][\w]*)['\"]"),            # deno
    re.compile(r"os\.(?:Getenv|LookupEnv)\(\s*\"([A-Za-z_][\w]*)\""),        # go
    re.compile(r"System\.getenv\(\s*\"([A-Za-z_][\w]*)\""),                  # java
    re.compile(r"ENV\s*(?:\.fetch)?\[\s*['\"]([A-Za-z_][\w]*)['\"]"),        # ruby ENV['X'] / ENV.fetch('X')[
    re.compile(r"ENV\.fetch\(\s*['\"]([A-Za-z_][\w]*)['\"]"),
    re.compile(r"Environment\.GetEnvironmentVariable\(\s*\"([A-Za-z_][\w]*)\""),  # c#
    re.compile(r"getenv\(\s*['\"]([A-Za-z_][\w]*)['\"]"),                     # php / c
    re.compile(r"\$_ENV\[\s*['\"]([A-Za-z_][\w]*)['\"]"),                     # php
]

allow = []
allowf = ROOT / ".claude" / "config-drift-allow.txt"
if allowf.exists():
    for ln in allowf.read_text(encoding="utf-8", errors="replace").splitlines():
        ln = ln.split("#", 1)[0].strip()
        if ln: allow.append(ln)
def allowed(key, msg):
    return any(a == key or a in msg for a in allow)

# declared side: the whole matrix text (for the "is it declared at all" test) + env-var-shaped key tokens.
decl_text = ENV_MD.read_text(encoding="utf-8", errors="replace")
declared_tokens = set(re.findall(r"\b[A-Z][A-Z0-9_]{2,}\b", decl_text))
def is_declared(key):
    return key in declared_tokens or re.search(r"(?<![\w])" + re.escape(key) + r"(?![\w])", decl_text) is not None

# code side: scan production source.
roots = [ROOT / d for d in SRC_DIRS if (ROOT / d).is_dir()]
F = []
def add(sev, where, msg, key=""):
    if not allowed(key, msg):
        F.append((sev, where, msg))

code_keys = {}     # key -> first where
code_blob_parts = []
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
            code_blob_parts.append(line)
            if "config-drift: allow" in line:
                continue
            for rx in READERS:
                for m in rx.finditer(line):
                    key = m.group(1)
                    code_keys.setdefault(key, "%s:%d" % (rel, n))
code_blob = "\n".join(code_blob_parts)

if not roots:
    print("check_config_drift: no production source dir (%s) under %s - nothing to scan." % ("/".join(SRC_DIRS), ROOT))
    sys.exit(0)

# ERROR: code reads a key the matrix does not declare.
for key, where in sorted(code_keys.items()):
    if not is_declared(key):
        add("ERROR", where, "code reads env var '%s' but infra-ops/environments.md does not declare it — the operator can't provision what isn't in the matrix." % key, key)
# WARN: matrix declares an env-var-shaped key no code reads (dead/stale, or infra-consumed).
declared_keys = set()
for line in decl_text.splitlines():
    if line.lstrip().startswith("|"):
        cells = [c.strip(" *`") for c in line.strip().strip("|").split("|")]
        if cells and ENVVAR.match(cells[0]):
            declared_keys.add(cells[0])
for key in sorted(declared_keys):
    if key not in code_keys and not re.search(r"(?<![\w])" + re.escape(key) + r"(?![\w])", code_blob):
        add("WARN", ENV_MD.name, "environments.md declares '%s' but no code reads it — dead/stale config, or infra-consumed (allowlist it)." % key, key)

order = {"ERROR": 0, "WARN": 1}
for sev, where, msg in sorted(F, key=lambda x: (order[x[0]], x[1])):
    print("%-5s %-28s %s" % (sev, where, msg))
e = sum(1 for x in F if x[0] == "ERROR")
w = len(F) - e
print("\n%d error(s), %d warning(s) — %d code key(s), %d declared key(s), %d file(s)." %
      (e, w, len(code_keys), len(declared_keys), scanned))
sys.exit(1 if e else 0)
