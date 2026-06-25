#!/usr/bin/env python3
# test_check_deploy_real.py - regression tests for check_deploy_real.py (the fake-deploy tripwire).
#
# Each scenario writes a tiny project, runs the tool, asserts which findings fire (must=) and which do NOT
# (forbid=) - locking the precision so a later edit can't make it noisier or blind. Stdlib only; no network.
# Run:  python3 tools/test_check_deploy_real.py
import subprocess, sys, tempfile, shutil, pathlib

HERE = pathlib.Path(__file__).resolve().parent
TOOL = HERE / "check_deploy_real.py"

def run(files, args=()):
    d = pathlib.Path(tempfile.mkdtemp(prefix="deploytest_"))
    try:
        for rel, content in files.items():
            p = d / rel; p.parent.mkdir(parents=True, exist_ok=True); p.write_text(content, encoding="utf-8")
        out = subprocess.run([sys.executable, str(TOOL), str(d), *args], capture_output=True, text=True)
        return out.stdout + out.stderr
    finally:
        shutil.rmtree(d, ignore_errors=True)

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

REAL_WF = ("name: deploy\n"
           "on: { push: { branches: [main] } }\n"
           "jobs:\n  deploy:\n    runs-on: ubuntu-latest\n"
           "    steps:\n      - run: helm upgrade --install app ./chart\n")
REAL_SH = "#!/usr/bin/env bash\nset -euo pipefail\nkubectl apply -f k8s/\n"

# a real deploy workflow (invokes helm) is clean
expect("real-workflow-clean", run({".github/workflows/deploy.yml": REAL_WF}),
       must=["0 error(s)"], forbid=["ERROR"])

# a real deploy script (invokes kubectl) is clean
expect("real-script-clean", run({"deploy/deploy.sh": REAL_SH}),
       must=["0 error(s)"], forbid=["ERROR"])

# a TODO placeholder in a deploy workflow is an ERROR
expect("placeholder-todo", run({".github/workflows/deploy.yml":
        "jobs:\n  deploy:\n    steps:\n      - run: echo TODO implement real deploy\n"}),
       must=["ERROR", "placeholder"])

# an echo-only deploy script (no recognized deploy command) is a WARN
expect("echo-only-script-warn", run({"deploy/release.sh": '#!/bin/bash\necho "deploying..."\nexit 0\n'}),
       must=["WARN", "no recognized deploy"], forbid=["ERROR"])

# --strict promotes the echo-only WARN to ERROR (the build-gate stance)
expect("echo-only-strict", run({"deploy/release.sh": '#!/bin/bash\necho "deploying..."\nexit 0\n'}, args=("--strict",)),
       must=["ERROR"])

# a disabled deploy job (if: false) is a WARN
expect("disabled-job-warn", run({".github/workflows/deploy.yml":
        "jobs:\n  deploy:\n    if: false\n    steps:\n      - run: helm upgrade app .\n"}),
       must=["WARN", "disabled deploy"], forbid=["ERROR"])

# a NON-deploy workflow (test/lint only, no deploy command) is left alone - no false positive on test logs
expect("non-deploy-workflow-ignored", run({".github/workflows/ci.yml":
        "jobs:\n  test:\n    steps:\n      - run: echo running tests\n"}),
       must=["nothing to scan"], forbid=["ERROR", "WARN"])

# inline waiver suppresses a per-line finding (a real-deploy line carrying an annotated TODO)
expect("inline-waiver", run({".github/workflows/deploy.yml":
        "jobs:\n  deploy:\n    steps:\n      - run: helm upgrade app .  # TODO tune chart  # deploy-real: allow tracked\n"}),
       must=["0 error(s)"], forbid=["ERROR"])

# allowlist file suppresses by path substring
expect("allowlist-file", run({".github/workflows/deploy.yml": "jobs:\n  deploy:\n    steps:\n      - run: echo TODO\n",
        ".claude/deploy-real-allow.txt": ".github/workflows/deploy.yml\n"}),
       must=["0 error(s)"], forbid=["ERROR"])

# ── expanded coverage: other CI providers, Dockerfile, package.json, Makefile ──

# a GitLab CI deploy job with a placeholder is an ERROR
expect("gitlab-placeholder", run({".gitlab-ci.yml":
        "deploy:\n  stage: deploy\n  script:\n    - echo TODO real deploy\n"}),
       must=["ERROR", "placeholder"])

# a real GitLab deploy job (kubectl) is clean
expect("gitlab-real-clean", run({".gitlab-ci.yml":
        "deploy:\n  stage: deploy\n  script:\n    - kubectl apply -f k8s/\n"}),
       must=["0 error(s)"], forbid=["ERROR"])

# a Jenkinsfile deploy stage that's echo-only is a WARN
expect("jenkins-echo-warn", run({"Jenkinsfile":
        "pipeline { stages { stage('Deploy') { steps { sh 'echo deploying' } } } }"}),
       must=["WARN", "no recognized deploy"], forbid=["ERROR"])

# a Dockerfile with a placeholder is an ERROR; a real one is clean (no no-op WARN for Dockerfiles)
expect("dockerfile-placeholder", run({"Dockerfile": "FROM node:20\n# TODO real entrypoint\nCMD [\"node\",\"x\"]\n"}),
       must=["ERROR", "placeholder"])
expect("dockerfile-real-clean", run({"Dockerfile": "FROM node:20\nCOPY . .\nCMD [\"node\",\"server.js\"]\n"}),
       must=["0 error(s)"], forbid=["ERROR", "WARN"])

# a package.json deploy script that's a placeholder is an ERROR; echo-only is a WARN; real is clean
expect("pkgjson-placeholder", run({"package.json":
        '{\n  "scripts": {\n    "deploy": "echo TODO"\n  }\n}\n'}),
       must=["ERROR", "placeholder"])
expect("pkgjson-echo-warn", run({"package.json":
        '{\n  "scripts": {\n    "deploy": "exit 0"\n  }\n}\n'}),
       must=["WARN", "echo-only"], forbid=["ERROR"])
expect("pkgjson-real-clean", run({"package.json":
        '{\n  "scripts": {\n    "deploy": "vercel --prod"\n  }\n}\n'}),
       must=["0 error(s)"], forbid=["ERROR", "WARN"])
# a package.json with no deploy-ish script is left alone (not scanned)
expect("pkgjson-no-deploy-script", run({"package.json":
        '{\n  "scripts": {\n    "test": "jest"\n  }\n}\n'}),
       must=["nothing to scan"], forbid=["ERROR", "WARN"])

# a Makefile deploy target that's a placeholder is an ERROR; echo-only is a WARN; real is clean
expect("makefile-placeholder", run({"Makefile": "deploy:\n\t# TODO implement\n"}),
       must=["ERROR", "placeholder"])
expect("makefile-echo-warn", run({"Makefile": "deploy:\n\techo deploying\n"}),
       must=["WARN", "no recognized deploy"], forbid=["ERROR"])
expect("makefile-real-clean", run({"Makefile": "deploy:\n\thelm upgrade --install app ./chart\n"}),
       must=["0 error(s)"], forbid=["ERROR", "WARN"])

# an in-house deployer the built-in list doesn't know: WARNs by default, but recognised once added to config
expect("unknown-deployer-warns", run({"deploy/release.sh": "#!/bin/bash\nmycorp-deployer ship --prod\n"}),
       must=["WARN", "no recognized deploy"], forbid=["ERROR"])
expect("config-extends-recognition", run({"deploy/release.sh": "#!/bin/bash\nmycorp-deployer ship --prod\n",
        ".claude/deploy-real-commands.txt": "mycorp-deployer\n"}),
       must=["0 error(s)"], forbid=["ERROR", "WARN"])

# no deploy artifact at all = clean no-op (an early project that hasn't wired CI yet)
expect("no-deploy-artifact-noop", run({"src/app.py": "print('hi')\n", "README.md": "hi\n"}),
       must=["nothing to scan"], forbid=["ERROR", "Traceback"])

print("\n%d passed, %d failed" % (PASS, FAIL))
sys.exit(1 if FAIL else 0)
