---
name: derive-test-strategy
description: >-
  Derive the two-tier test architecture — levels, coverage, traceability — and make testing an active edge-case discovery engine, not just verification. Use when the spec exists and you need the test strategy defined. Loads the shared derive engine.
disable-model-invocation: true
argument-hint: a recorded spec or design docs
---

# derive-test-strategy

**Load `${CLAUDE_PLUGIN_ROOT}/grill-shared/derive-engine.md` first and follow it.** This skill applies that method to **Test strategy** — verification AND active edge-case discovery, across two tiers.

## Method
A test's **source** is what it verifies; its **timing** is when its subject exists. A test's **target** is the system it runs against — **unit/integration/contract run locally** (integration is where test containers / `docker-compose` belong), but **e2e, system-journey, NFR-evidence, and smoke tests run against a REAL deployed environment**, never a local stack. **Tier A — per-slice** (unit/integration/contract/e2e for one slice) is produced *with each task* during implementation — defined here only as the *standard*, not enumerated. **For a UI slice the Tier-A standard includes its rendered-surface checks:** state-coverage tests (every interaction state the task's `ux` cell names), the per-slice **a11y scan** (axe or equivalent — zero critical/serious, keyboard/focus path asserted), and the **breakpoint render check** against the frozen prototype — these gate with the slice, so the first feature's screens meet the bar the day they land; the Tier-B a11y run attests the released *system* and never substitutes for them. **Tier B — system/cross-cutting** is derived here from the spec:
1. **system/journey acceptance tests** from the UC- + UX journeys — outside-in/ATDD, authored before the code so they drive it, green incrementally as slices land
2. **architecture fitness functions** from the ASR- + architecture boundaries (dependency/layering incl. no-cycles + public-API-surface, coupling/modularity budgets, allowed-tech, design-token conformance for UI — semantic/component tokens only, and a **no-fakes-in-production** guard: no test-double/stub/mock/canned-response symbol reachable from a production entrypoint, so non-production code can't ship in `src/` — author it as a real import-graph rule in the project's language; the shipped `check_no_fakes.py` tripwire is the coarse cross-language backstop that fires even before this fitness function exists) — written when the boundary is decided, failing until the structure exists, then guarding continuously
3. the **contract suite** from the API contracts; async/job/scheduled/eventual-consistency behaviour gets real-path integration tests (real broker/worker, assert the eventual outcome, cover retry/idempotency/ordering/dead-letter — never assert mere enqueue)
4. **NFR-evidence tests** (load/stress/soak/chaos/resilience · pen/SAST/DAST/IAST · a11y) from the NFR- / SLO- / security requirements — authored early from the target, executed once a deployable system exists; add **shift-right** testing (synthetic monitoring · canary verification tied to a burn-rate · flag-gated experiments) that runs against the deployed system
5. **edge-discovery techniques** — boundary-value, equivalence partitioning, property-based, fuzzing — that *manufacture* edges instead of waiting for prod
6. a **test-data strategy** — synthetic generation · PII-safe masking/subsetting · fixtures-vs-factories · scale data for load tests
7. coverage + traceability; the harness (seeded by the walking-skeleton task)

## Rules
- this layer is *discovery* as much as verification — treat a surprising property/fitness failure with no governing rule as a **gap to resolve upstream**, not just a bug to patch
- every cross-feature journey has a system acceptance test; every load-bearing `ASR-`/boundary has a fitness function; every `NFR-`/`ASR-`/`SLO-` has an evidence test (not an assertion); contract suite covers every `API-`/`EVT-`
- **cross-cutting cells gate per-slice, not only at release** — a slice's referenced `SEC-` deny rules / `ENTL-` gates each get a **deny-path (over-limit / lapsed-billing) test** in that slice's Tier-A set; every `obs`-cell signal (`SLO-`-backing telemetry · `AEV-` analytics event) gets an **emission assertion**; a `DATA-` retention/TTL/deletion trigger is exercised by the slice that owns it; when i18n is in scope, add a **string-externalization fitness check** (no user-facing literal outside the i18n layer) and render touched screens in a pseudo-locale — the Tier-B pen/a11y/load runs attest the system, they never substitute for these
- **the test-distribution shape is chosen from the architecture**, not mandated: logic-heavy → a pyramid (many fast unit, fewer integration, a thin e2e top); integration-heavy / microservice / serverless → an integration-weighted shape (the middle tier carries the weight); either way avoid an e2e-top-heavy distribution; contract tests are **CDC** with provider verification
- **e2e/journey/smoke/NFR-evidence run against a REAL deployed environment, never a local stack** — `docker-compose`/testcontainers is the **integration** tier. The **default e2e target is an ephemeral per-PR preview environment** (real infra + isolated + deterministic, so the shared-staging-is-flaky objection doesn't apply); a reserved e2e/staging env is the fallback. **Name the e2e target environment in the strategy** (and reference the `infra-ops` environment set / promotion path that provides it). A green e2e/smoke against that deployed env **is the behavioural proof the deploy pipeline shipped** — the authoritative deploy check, with `check_deploy_real.py` only the static backstop for the pre-provision window
- **mutation testing gates test quality** — coverage % is gameable; a surviving mutant is a missing assertion. The technique is decided; **the passing bars (coverage % and mutation score) are rigor thresholds the org owns → a ratify-point:** propose recommended bars (concrete numbers + one-line why — e.g. "≥80% line coverage, ≥70% mutation score on changed domain logic") for the human to agree/override, never silently set. **The per-task enforcement of both bars is DIFF-scoped** (every changed `src/**` line test-executed at 100%; mutation over the changed files at the bar) — a whole-tree % lets a small untested snippet hide in its slack, so the diff numbers are the **per-task** gate; the whole-tree numbers remain the trend metric per commit AND the ratified aggregate bar the whole-build audit re-checks at release (a per-slice pass can still leave a system-level hole).
- **the tier contract is machine-readable, not prose** — a mock/real policy left in a paragraph can't be verified, so `levels.md` carries a fixed-column row PER tier: `tier · real-deps` (what MUST run real) `· may-mock` (the only doubles allowed here) `· mock-ceiling` (`none`/`boundary-only`/`n-a`) `· target-env · coverage-bar · mutation-bar`. This table is the **ground truth** the downstream verifiers (`check_mock_budget.py`, `check_test_tiers.py`, and the whole-build audit) read — nothing checks a policy that lives only in prose. Propose the contract; the ceilings ratify with the bars above. **The default contract (best practice — propose it, don't invent per project):** **unit** → pure, no I/O, `mock-ceiling: none` (a mock here means the "unit" is doing integration work — push it down to a pure function or up to the integration tier); **integration** → real DB/broker/filesystem via testcontainers, `may-mock: third-party network at the boundary only`, `mock-ceiling: boundary-only`; **contract** → real CDC provider/consumer verification, `mock-ceiling: none` (no stubbed counterparty schema); **e2e/journey/smoke/NFR-evidence** → nothing mocked, `mock-ceiling: none`, `target-env:` the named deployed env. A test that breaches its tier's ceiling (a mock under `tests/e2e/`, a mocked DB in an integration test the contract says runs real) is a defect the verifier flags.
- tests are **deterministic** (control time/randomness/external deps); quarantine is not delete

## Output
Written under `solution/test/`:

| File | Captures | Format |
|---|---|---|
| `levels.md` | the two-tier test architecture + levels: level · scope · **target environment** (local for unit/integration/contract; the named deployed env — preview/e2e/staging — for e2e/journey/smoke/NFR-evidence) · coverage target; the distribution shape chosen from the architecture (pyramid OR integration-weighted); **+ the machine-readable tier contract** (a row per tier: `tier · real-deps · may-mock · mock-ceiling · target-env · coverage-bar · mutation-bar`) that the downstream verifiers read as ground truth | list: level · scope · target-env · coverage; CDC; **tier-contract table** |
| `traceability.md` | requirement/ASR → test-level matrix | matrix |
| `edge-discovery.md` | edge-discovery techniques: boundary-value · equivalence partitioning · property-based · fuzzing · mutation testing | prose |
| `nfr-evidence.md` | NFR-evidence test plan (load/stress/soak/chaos · pen/SAST/DAST/IAST · a11y) + shift-right (synthetic monitoring · canary verification ⇄ burn-rate · flag-gated experiments) → the target each must measure against | prose |
| `test-data.md` | test-data strategy: synthetic generation · PII-safe masking/subsetting · fixtures-vs-factories · scale data for load tests | prose |

ADRs → `adr/ADR-TEST-NNN.md`
Consumes: the functional use-cases + UX journeys, the architecture boundaries + ASRs, the API contracts, and the quality NFRs / observability SLOs / security requirements.

## Excludes
test implementation code (the Tier-B suites + harness)

## Resources
- `${CLAUDE_PLUGIN_ROOT}/grill-shared/derive-engine.md`
- Worked example: `examples.md`
