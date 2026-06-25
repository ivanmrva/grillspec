#!/usr/bin/env python3
# test_check_config_drift.py - regression tests for check_config_drift.py (code-reads vs spec-declares config).
# Stdlib only; no network. Run:  python3 tools/test_check_config_drift.py
import subprocess, sys, tempfile, shutil, pathlib

HERE = pathlib.Path(__file__).resolve().parent
TOOL = HERE / "check_config_drift.py"
ENVHDR = "<!-- scope: x | excludes: y | format: matrix -->\n| Key | Purpose | dev | prod |\n|---|---|---|---|\n"

def matrix(*keys):
    return ENVHDR + "".join("| %s | p | a | b |\n" % k for k in keys)

def run(files, args=()):
    d = pathlib.Path(tempfile.mkdtemp(prefix="cdrifttest_"))
    try:
        for rel, content in files.items():
            p = d / rel; p.parent.mkdir(parents=True, exist_ok=True); p.write_text(content, encoding="utf-8")
        out = subprocess.run([sys.executable, str(TOOL), str(d), *args], capture_output=True, text=True)
        return out.stdout + out.stderr
    finally:
        shutil.rmtree(d, ignore_errors=True)

ENV = "spec/09-solution/infra-ops/environments.md"
PASS = FAIL = 0
def expect(name, output, must=(), forbid=()):
    global PASS, FAIL
    probs = [("missing: " + s) for s in must if s not in output] + \
            [("unexpected: " + s) for s in forbid if s in output]
    if probs:
        FAIL += 1; print("FAIL  " + name)
        for pr in probs: print("        " + pr)
        print("        --- output ---\n" + "\n".join("        " + l for l in output.splitlines()))
    else:
        PASS += 1; print("ok    " + name)

# every read key is declared -> clean
expect("all-declared-clean", run({ENV: matrix("DATABASE_URL", "STRIPE_API_KEY"),
        "src/a.py": "import os\nos.getenv('DATABASE_URL')\nos.environ['STRIPE_API_KEY']\n"}),
       must=["0 error(s)"], forbid=["ERROR"])

# a code-read key missing from the matrix -> ERROR (the outage case)
expect("undeclared-read-errors", run({ENV: matrix("DATABASE_URL"),
        "src/a.py": "import os\nos.environ.get('STRIPE_WEBHOOK_SECRET')\n"}),
       must=["ERROR", "STRIPE_WEBHOOK_SECRET", "can't provision"])

# node process.env.X is detected too
expect("node-process-env", run({ENV: matrix("DATABASE_URL"),
        "src/a.js": "const r = process.env.AWS_REGION;\n"}),
       must=["ERROR", "AWS_REGION"])

# a declared env-var-shaped key no code reads -> WARN (not ERROR)
expect("dead-declared-warns", run({ENV: matrix("DATABASE_URL", "LEGACY_FLAG"),
        "src/a.py": "import os\nos.getenv('DATABASE_URL')\n"}),
       must=["WARN", "LEGACY_FLAG"], forbid=["ERROR"])

# reads in TEST files don't force declaration
expect("test-reads-ignored", run({ENV: matrix("DATABASE_URL"),
        "src/a.py": "import os\nos.getenv('DATABASE_URL')\n",
        "tests/t.py": "import os\nos.getenv('TEST_ONLY_TOKEN')\n"}),
       must=["0 error(s)"], forbid=["ERROR", "TEST_ONLY_TOKEN"])

# inline waiver suppresses an undeclared read
expect("inline-waiver", run({ENV: matrix("DATABASE_URL"),
        "src/a.py": "import os\nos.getenv('DEBUG_SECRET')  # config-drift: allow tooling-only\n"}),
       must=["0 error(s)"], forbid=["ERROR"])

# allowlist file suppresses by key
expect("allowlist-file", run({ENV: matrix("DATABASE_URL"),
        "src/a.js": "process.env.AWS_REGION\n", ".claude/config-drift-allow.txt": "AWS_REGION\n"}),
       must=["0 error(s)"], forbid=["ERROR"])

# no environments.md -> clean no-op
expect("no-matrix-noop", run({"src/a.py": "import os\nos.getenv('X')\n"}),
       must=["nothing to reconcile"], forbid=["ERROR", "Traceback"])

# custom --src
expect("custom-src", run({ENV: matrix("DATABASE_URL"), "app/a.py": "import os\nos.getenv('OTHER_KEY')\n"}, args=("--src", "app")),
       must=["ERROR", "OTHER_KEY"])

print("\n%d passed, %d failed" % (PASS, FAIL))
sys.exit(1 if FAIL else 0)
