#!/usr/bin/env python3
# test_lint_spec.py - regression tests for the spec tools (lint_spec.py + check_contracts.py).
#
# Each scenario writes a tiny spec to a tempdir, runs the tool, and asserts which findings fire (must=) and
# which do NOT (forbid=) - locking every check's behaviour so a later edit can't silently regress one. Stdlib
# only; no network. Run:  python3 tools/test_lint_spec.py   (exit 0 = all pass, 1 = a regression).
import subprocess, sys, tempfile, shutil, pathlib

HERE = pathlib.Path(__file__).resolve().parent
LINT, CC = HERE / "lint_spec.py", HERE / "check_contracts.py"
HDR = "<!-- scope: x | excludes: y | format: z -->"
try:
    import yaml; HAVE_YAML = True
except ImportError:
    HAVE_YAML = False

def run(tool, files):
    d = pathlib.Path(tempfile.mkdtemp(prefix="spectest_"))
    try:
        for rel, content in files.items():
            p = d / "spec" / rel
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(content, encoding="utf-8")
        out = subprocess.run([sys.executable, str(tool), str(d / "spec")], capture_output=True, text=True)
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
    else:
        PASS += 1; print("ok    " + name)

def idtable(*rows):
    return HDR + "\n| ID | Name |\n|---|---|\n" + "".join("| %s | %s |\n" % r for r in rows)

# ── core invariants ────────────────────────────────────────────────────────
expect("clean-baseline", run(LINT, {"04-domain/ddd/a.md": idtable(("AGG-1", "Order"))}),
       must=["0 error(s)"])

expect("dangling-ref", run(LINT, {
    "04-domain/ddd/a.md": idtable(("CMD-1", "Create")),
    "05-functional-spec/uc.md": idtable(("UC-1", "Place")) + "\nUC-1 implements CMD-99\n",
}), must=["undefined ID 'CMD-99'"])

expect("upstream-only", run(LINT, {
    "04-domain/ddd/a.md": idtable(("AGG-1", "Order")) + "\nAGG-1 needs T-5\n",
    "10-delivery/tasks/T-5.md": idtable(("T-5", "build")) + "\nimplements AGG-1\n",
}), must=["illegal downward reference"])

expect("duplicate-id", run(LINT, {
    "04-domain/ddd/a.md": idtable(("AGG-1", "Order")),
    "04-domain/ddd/b.md": idtable(("AGG-1", "Order2")),
}), must=["defined in multiple files"])

# ── structured-fact checks (this session) ──────────────────────────────────
SM_BAD = HDR + "\n| ID | N |\n|---|---|\n| AGG-1 | Sub |\n\n### states\n" + \
    "| from | trigger | to | guard |\n|---|---|---|---|\n" + \
    "| (initial) | created | trial |  |\n| trial | act | active |  |\n" + \
    "| active | cancel | cancelled |  |\n| active | cancel | suspended |  |\n| archived | restore | active |  |\n"
expect("state-machine-bad", run(LINT, {"04-domain/ddd/s.md": SM_BAD}),
       must=["unreachable", "dead-end", "nondeterministic"])

SM_OK = HDR + "\n| ID | N |\n|---|---|\n| AGG-1 | Sub |\n\n### states\n" + \
    "| from | trigger | to | guard |\n|---|---|---|---|\n" + \
    "| (initial) | created | trial |  |\n| trial | act | active |  |\n" + \
    "| active | cancel | cancelled | by owner |\n| active | suspend | suspended |  |\n" + \
    "| suspended | reactivate | active |  |\n| cancelled | purge | — (terminal) |  |\n"
expect("state-machine-clean", run(LINT, {"04-domain/ddd/s.md": SM_OK}), forbid=["state-machine:"])

# a ddd from/to table that is NOT a transition table (no trigger/event column) must not be read as a state machine
expect("state-machine-not-a-transition-table", run(LINT, {
    "04-domain/ddd/ctx.md": HDR + "\n| from | to | type |\n|---|---|---|\n| Orders | Billing | customer-supplier |\n| Billing | Orders | conformist |\n",
}), forbid=["state-machine:"])

# a 'command'-headed table OUTSIDE 06-requirements/security must not be read as an authorization matrix
expect("authz-not-in-security", run(LINT, {
    "09-solution/arch/ops.md": HDR + "\n| command | latency | notes |\n|---|---|---|\n| GET /orders | 50ms |  |\n",
}), forbid=["authorization matrix", "has no decision"])

expect("authz-completeness", run(LINT, {
    "04-domain/ddd/c.md": idtable(("CMD-1", "A"), ("CMD-2", "B")),
    "06-requirements/security/z.md": HDR + "\n| command | admin | user |\n|---|---|---|\n| CMD-1 | allow |  |\n",
}), must=["has no decision", "has no rule/row"])

expect("typed-field", run(LINT, {
    "06-requirements/data/d.md": HDR + "\n| ID | Name | class | retention | residency |\n|---|---|---|---|---|\n"
    "| DATA-1 | Inv | conf | 7 years | EU |\n| DATA-2 | Tel | — | — | — |\n\nDATA-1 retention: 30 days trial.\n",
}), must=["conflicting values", "declares no class/retention/residency"])

expect("task-dag-cycle", run(LINT, {
    "10-delivery/tasks/T-1.md": idtable(("T-1", "a")) + "\ndepends-on: T-2\n",
    "10-delivery/tasks/T-2.md": idtable(("T-2", "b")) + "\ndepends-on: T-1\n",
}), must=["dependency cycle"])

expect("nfr-enforcement", run(LINT, {
    "06-requirements/quality/q.md": HDR + "\n| ID | attr | response | enforced-by |\n|---|---|---|---|\n"
    "| NFR-1 | lat | p95<200ms | gate |\n| NFR-2 | avail | 99.9% |  |\n",
}), must=["NFR-2 names no enforcement"], forbid=["NFR-1 names no enforcement"])

expect("module-role", run(LINT, {
    "09-solution/arch/m.md": HDR + "\n| module | role | direction | seam |\n|---|---|---|---|\n"
    "| Api | driving-port | in | x |\n| Worker |  | in | y |\n",
}), must=["module 'Worker' declares no role"], forbid=["module 'Api' declares no role"])

expect("threat-coverage", run(LINT, {"06-requirements/security/t.md": idtable(("THR-1", "Spoof"), ("SEC-1", "Sign"))}),
       must=["no mitigating control (SEC-)"])

# a contract YAML credits coverage: an EVT- consumed only by asyncapi.yaml must NOT false-WARN "no consumer"
expect("contract-coverage-credit", run(LINT, {
    "04-domain/ddd/a.md": HDR + "\n## AGG-1 X\n- **events:** EVT-9 Done\n",
    "05-functional-spec/uc.md": idtable(("UC-1", "V")),
    "09-solution/api/asyncapi.yaml": "asyncapi: 3.0.0\nchannels: {c: {x-grillspec-id: EVT-9}}\n",
}), forbid=["EVT-9"])

expect("task-traceability", run(LINT, {"10-delivery/tasks/T-9.md": idtable(("T-9", "x"))}),
       must=["cites no upstream spec ID"])

expect("adr-status", run(LINT, {"adr/ADR-DDD-1.md": "# ADR-DDD-1 thing\nDecision: do it.\n"}),
       must=["no recognized 'status:'"])

# ── check_contracts (needs PyYAML) ─────────────────────────────────────────
if HAVE_YAML:
    OAPI = ("openapi: 3.1.0\ninfo: {title: T, version: 1.0.0}\n"
            "paths: {/x: {post: {operationId: x, x-grillspec-id: API-1, x-serves: [%s], "
            "security: [{o: []}], responses: {'400': {description: e}}}}}\n")
    expect("contracts-undefined-ref", run(CC, {
        "05-functional-spec/uc.md": idtable(("UC-1", "P")),
        "09-solution/api/openapi.yaml": OAPI % "UC-99",
    }), must=["undefined grillspec id 'UC-99'"])
    expect("contracts-clean", run(CC, {
        "05-functional-spec/uc.md": idtable(("UC-1", "P")),
        "09-solution/api/openapi.yaml": OAPI % "UC-1",
    }), must=["0 error(s)"])
else:
    print("skip  contracts-* (PyYAML not installed)")

print("\n%d passed, %d failed." % (PASS, FAIL))
sys.exit(1 if FAIL else 0)
