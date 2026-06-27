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

# universal upstream-only (definition-anchored): an UNREGISTERED id-shape defined downstream (a 'BR-' boundary
# rule in L6 conventions) and cited UPWARD from L2 requirements is a downward violation — WARN, no registration
# needed. This is the BR- bug the IDTOK-only direction check missed.
expect("unregistered-id-downward", run(LINT, {
    "10-delivery/conventions/boundary-rules.md": HDR + "\n| rule | constraint |\n|---|---|\n| BR-16 | Scheduling must not import FieldWork |\n",
    "06-requirements/quality/q.md": HDR + "\n- this is enforced-by BR-16\n" + idtable(("NFR-1", "X")),
}), must=["illegal downward reference", "BR-16"])
# a free LOCAL id used within/above its own layer, and a standard cited in prose, must NOT warn
expect("unregistered-id-local-ok", run(LINT, {
    "04-domain/ddd/a.md": idtable(("AGG-1", "Order")),
    "01-discovery/d.md": HDR + "\n| id | pain |\n|---|---|\n| PN-1 | slow onboarding |\n",
    "02-product/vision/v.md": HDR + "\n- addresses PN-1; transport follows RFC-7231\n",
}), forbid=["illegal downward reference"])
# a newly-REGISTERED type obeys the ERROR-level direction check: an L5 module cited from L1 ddd is downward
expect("registered-newtype-direction", run(LINT, {
    "09-solution/arch/a.md": HDR + "\n| id | module |\n|---|---|\n| MOD-1 | UI |\n",
    "04-domain/ddd/d.md": idtable(("AGG-1", "Order")) + "- AGG-1 is realized in MOD-1\n",
}), must=["illegal downward reference", "MOD-1"])

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

# a per-task Verification Record REFERENCES ids (its H1 leads with the T-, obligation rows key on the AC-/… it
# verifies); it never DEFINES them, so it must NOT register as a duplicate / out-of-area definition.
expect("verification-record-not-a-defsite", run(LINT, {
    "05-functional-spec/uc.md": idtable(("UC-001", "Login"), ("AC-001a", "Valid login")),
    "10-delivery/tasks/T-001.md": HDR + "\n# T-001 — Walking skeleton\nbehavior: AC-001a\n",
    "10-delivery/verification/tasks/T-001.md":
        HDR + "\n# T-001 — Verification Record\n\nstatus: in-progress\ntask: T-001\n\n"
        "| Obligation | Source | Required | Evidence | Status |\n|---|---|---|---|---|\n"
        "| AC-001a | behavior | test | tests/e2e/login.test.js | PASS |\n"
        "| deploy | infra-ops | real | .github/workflows/deploy.yml | PASS |\n",
}), must=["0 error(s)"], forbid=["defined in multiple files", "outside its owning area"])

# a downstream TRACE/EVIDENCE table keyed on an UPSTREAM id (09-solution/arch/quality.md keying its rows on the
# ASR- it realizes, the same shape traceability.md uses) is a row-key REFERENCE, not a re-definition — it must
# NOT false-fire 'defined in multiple files' / 'outside its owning area'. The id resolves to its upstream def.
expect("foreign-leading-id-is-a-reference", run(LINT, {
    "06-requirements/quality/q.md": HDR + "\n| ID | attr | response | enforced-by |\n|---|---|---|---|\n"
        "| NFR-3 | scale | 10x | load test |\n| ASR-3 | scale | 10x | load test |\n",
    "09-solution/arch/quality.md": HDR + "\n| ASR | Tactic | C4 location | Fitness function |\n|---|---|---|---|\n"
        "| ASR-3 | bulkhead | service X | p95<200ms load test |\n",
    "10-delivery/tasks/T-1.md": HDR + "\n# T-1\nverifies ASR-3 and NFR-3\n",
}), must=["0 error(s)"], forbid=["defined in multiple files", "outside its owning area", "undefined ID"])
# but a foreign id leading a row that resolves to NOTHING upstream is still caught — now as a precise
# 'undefined ID' (the misplaced-definition hole stays closed).
expect("foreign-leading-id-undefined-still-errors", run(LINT, {
    "06-requirements/quality/q.md": idtable(("NFR-1", "lat")),
    "09-solution/arch/quality.md": HDR + "\n| ASR | Tactic | Fitness function |\n|---|---|---|\n| ASR-77 | bulkhead | load test |\n",
}), must=["undefined ID 'ASR-77'"])

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

# a compound 'A / B' from-cell is shorthand for two source states sharing the row's trigger/to — both must
# register, so neither 'running' nor 'awaiting-retry' is falsely flagged unreachable/dead-end
SM_COMPOUND = HDR + "\n| ID | N |\n|---|---|\n| AGG-1 | Job |\n\n### states\n" + \
    "| from | trigger | to | guard |\n|---|---|---|---|\n" + \
    "| pending (initial) | start | running |  |\n| running | retry | awaiting-retry | attempts left |\n" + \
    "| awaiting-retry | resume | running |  |\n| running / awaiting-retry | exhausted | dead-lettered (terminal) |  |\n" + \
    "| running | finish | done (terminal) |  |\n"
expect("state-machine-compound-from-cell", run(LINT, {"04-domain/ddd/s.md": SM_COMPOUND}), forbid=["state-machine:"])

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
       must=["no mitigating control (SEC-/ADR-/OBL-/DATA-)"])

# a THR is covered when its OWN row forward-cites a non-SEC control (ADR-/OBL-/DATA- near a mitigation cue)
# or is marked accepted-risk - none of which back-reference the THR, so the refset test alone false-WARNed.
expect("threat-coverage-nonsec-controls", run(LINT, {"06-requirements/security/t.md":
    HDR + "\n| ID | threat | mitigation |\n|---|---|---|\n" +
    "| THR-1 | spoof | ADR-SREQ-3 structural auth boundary |\n" +
    "| THR-2 | leak | OBL-12 retention obligation |\n" +
    "| THR-3 | tamper | control: DATA-Ledger append-only |\n" +
    "| THR-4 | minor dos | accepted-risk: edge rate-limit suffices |\n" +
    "| THR-9 | UNMITIGATED | (none) |\n| SEC-1 | Sign |\n"}),
    must=["'THR-9' has no downstream"], forbid=["'THR-1' has no downstream", "'THR-2' has no downstream", "'THR-3' has no downstream", "'THR-4' has no downstream"])

# an EVT is covered by a cross-context 'whenever EVT-' POL- reaction (even a deferred context) or when it is
# an intentional audit-only / operator-console-internal sink; only a true orphan still WARNs.
expect("event-consumer-policy-and-sinks", run(LINT, {
    "05-functional-spec/uc.md": idtable(("UC-1", "V")),
    "04-domain/ddd/strat/policies.md": HDR + "\nPOL-1 Ship: whenever EVT-701 then CMD-2 (Fulfillment, deferred)\n",
    "04-domain/ddd/tac/events.md": HDR + "\n| ID | name | note |\n|---|---|---|\n" +
        "| EVT-701 | Placed | core |\n| EVT-208 | Audited | audit-only |\n| EVT-110 | Nudged | operator-console-internal |\n| EVT-999 | Orphan | core |\n"}),
    must=["'EVT-999' has no downstream"], forbid=["'EVT-701' has no downstream", "'EVT-208' has no downstream", "'EVT-110' has no downstream"])

# a sink marker on a NON-first event in a '·'-joined inline list must attribute to that event, not the first:
# EVT-208 (audit-only, 2nd of three) is a sink; the bare siblings still WARN.
expect("event-sink-non-first-in-joined-list", run(LINT, {
    "05-functional-spec/uc.md": idtable(("UC-1", "V")),
    "04-domain/ddd/a.md": HDR + "\n## AGG-1 X\n- **events:** EVT-207 Placed · EVT-208 Audited audit-only · EVT-209 Shipped\n",
}), must=["'EVT-207' has no downstream", "'EVT-209' has no downstream"], forbid=["'EVT-208' has no downstream"])

# a 'whenever' reaction whose events sit in a SEPARATE '·'-joined cell from the keyword must credit every
# joined event (REFMARK only sees ids after the keyword); both EVT-704 and EVT-705 are consumed by POL-704.
expect("event-consumer-joined-whenever-cell", run(LINT, {
    "05-functional-spec/uc.md": idtable(("UC-1", "V")),
    "04-domain/ddd/e.md": HDR + "\n## AGG-1 X\n- **events:** EVT-704 A · EVT-705 B\n",
    "04-domain/ddd/p.md": HDR + "\n| reaction | events | trigger |\n|---|---|---|\n| POL-704 | EVT-704 · EVT-705 | whenever the operator escalates |\n",
}), forbid=["'EVT-704' has no downstream", "'EVT-705' has no downstream"])

# a POL- row that lists its trigger events in a 'trigger'/'when' column with NO 'whenever' keyword -
# '·'-joined and/or parenthetically annotated - still consumes every event named on it.
expect("event-consumer-policy-trigger-column-no-keyword", run(LINT, {
    "05-functional-spec/uc.md": idtable(("UC-1", "V")),
    "04-domain/ddd/ev.md": HDR + "\n## AGG-1 X\n- **events:** EVT-704 CreatorAccountSuspended · EVT-705 CreatorAccountClosed · EVT-510 CohortReleased\n",
    "04-domain/ddd/pol.md": HDR + "\n| policy | trigger | command |\n|---|---|---|\n" +
        "| POL-704 | EVT-704 CreatorAccountSuspended · EVT-705 CreatorAccountClosed | CMD-9 Notify |\n" +
        "| POL-510 | EVT-510 CohortReleased (operator releases the cohort) | CMD-9 Notify |\n",
}), forbid=["'EVT-704' has no downstream", "'EVT-705' has no downstream", "'EVT-510' has no downstream"])

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

# ── 13b context-namespaced IDs: literal external-vendor identifiers shaped like <lead>-<TYPE>-… (Alpaca's
#    APCA-API-KEY-ID header: lead APCA, type API) are flagged in PROSE but must be writable verbatim inside a
#    code fence or an inline `code` span — the ID grammar must not claim literal code content. ──────────────
expect("ns-vendor-id-bare-fires", run(LINT, {"12-operate/rb.md": HDR + "\nSet the APCA-API-KEY-ID header.\n"}),
       must=["context-namespaced ID", "APCA-API-KEY-ID"])
expect("ns-vendor-id-fenced-ok", run(LINT, {"12-operate/rb.md": HDR + "\n```\nAPCA-API-KEY-ID: <key>\n```\n"}),
       forbid=["context-namespaced ID"])
expect("ns-vendor-id-inline-ok", run(LINT, {"12-operate/rb.md": HDR + "\nSet the `APCA-API-KEY-ID` header.\n"}),
       forbid=["context-namespaced ID"])

# ── placeholder {{ }}: a real vendor template ({{user.public_metadata.role}} — Clerk session-token claims) is
#    flagged in prose but exempt inside a fence or inline `code`. ─────────────────────────────────────────
expect("tok-curly-bare-fires", run(LINT, {"12-operate/rb.md": HDR + "\nrole is {{user.role}} here\n"}),
       must=["placeholder/stale token"])
expect("tok-curly-fenced-ok", run(LINT, {"12-operate/rb.md": HDR + "\n```\n{{user.public_metadata.role}}\n```\n"}),
       forbid=["placeholder/stale token"])
expect("tok-curly-inline-ok", run(LINT, {"12-operate/rb.md": HDR + "\nclaim `{{user.role}}` in config\n"}),
       forbid=["placeholder/stale token"])

# ── 11d illegal downward PATH reference: an upstream file pointing at a downstream area by path/link (the ID
#    direction checks only see id tokens; this catches 'infra-ops/prerequisites.md' cited from a requirement). ──
expect("path-downward-bare-warns", run(LINT, {"06-requirements/quality/nfrs.md": HDR + "\nRPO target owned by infra-ops/test.\n" + idtable(("NFR-1", "x"))}),
       must=["illegal downward path reference", "infra-ops/test"])
expect("path-downward-link-warns", run(LINT, {"06-requirements/security/authz.md": HDR + "\nSee [creds](09-solution/infra-ops/prerequisites.md).\n" + idtable(("SEC-1", "x"))}),
       must=["illegal downward path reference"])
expect("path-upstream-ok", run(LINT, {"09-solution/infra-ops/topology.md": HDR + "\nRealises 06-requirements/quality/nfrs.md.\n" + idtable(("MOD-1", "x"))}),
       forbid=["illegal downward path reference"])
expect("path-downward-fenced-ok", run(LINT, {"06-requirements/quality/nfrs.md": HDR + "\n```\ninfra-ops/prerequisites.md\n```\n" + idtable(("NFR-1", "x"))}),
       forbid=["illegal downward path reference"])
expect("path-adr-exempt", run(LINT, {"adr/ADR-SEC-4.md": "# ADR-SEC-4 thing\nStatus: accepted\nSee 09-solution/infra-ops/cicd.md.\n"}),
       forbid=["illegal downward path reference"])
expect("path-nonspec-ignored", run(LINT, {"06-requirements/quality/nfrs.md": HDR + "\nCode in src/billing/charge.py, docs at https://stripe.com/api/keys.\n" + idtable(("NFR-1", "x"))}),
       forbid=["illegal downward path reference"])

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
