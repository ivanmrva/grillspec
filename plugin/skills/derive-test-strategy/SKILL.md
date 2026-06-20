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
A test's **source** is what it verifies; its **timing** is when its subject exists. **Tier A — per-slice** (unit/integration/contract/e2e for one slice) is produced *with each task* during implementation — defined here only as the *standard*, not enumerated. **Tier B — system/cross-cutting** is derived here from the spec:
1. **system/journey acceptance tests** from the UC- + UX journeys — outside-in/ATDD, authored before the code so they drive it, green incrementally as slices land
2. **architecture fitness functions** from the ASR- + architecture boundaries (dependency/layering incl. no-cycles + public-API-surface, coupling/modularity budgets, allowed-tech, design-token conformance for UI — semantic/component tokens only) — written when the boundary is decided, failing until the structure exists, then guarding continuously
3. the **contract suite** from the API contracts; async/job/scheduled/eventual-consistency behaviour gets real-path integration tests (real broker/worker, assert the eventual outcome, cover retry/idempotency/ordering/dead-letter — never assert mere enqueue)
4. **NFR-evidence tests** (load/stress/soak/chaos/resilience · pen/SAST/DAST/IAST · a11y) from the NFR- / SLO- / security requirements — authored early from the target, executed once a deployable system exists; add **shift-right** testing (synthetic monitoring · canary verification tied to a burn-rate · flag-gated experiments) that runs against the deployed system
5. **edge-discovery techniques** — boundary-value, equivalence partitioning, property-based, fuzzing — that *manufacture* edges instead of waiting for prod
6. a **test-data strategy** — synthetic generation · PII-safe masking/subsetting · fixtures-vs-factories · scale data for load tests
7. coverage + traceability; the harness (seeded by the walking-skeleton task)

## Rules
- this layer is *discovery* as much as verification — treat a surprising property/fitness failure with no governing rule as a **gap to resolve upstream**, not just a bug to patch
- every cross-feature journey has a system acceptance test; every load-bearing `ASR-`/boundary has a fitness function; every `NFR-`/`ASR-`/`SLO-` has an evidence test (not an assertion); contract suite covers every `API-`/`EVT-`
- **the test-distribution shape is chosen from the architecture**, not mandated: logic-heavy → a pyramid (many fast unit, fewer integration, a thin e2e top); integration-heavy / microservice / serverless → an integration-weighted shape (the middle tier carries the weight); either way avoid an e2e-top-heavy distribution; contract tests are **CDC** with provider verification
- **mutation testing gates test quality** — coverage % is gameable; a surviving mutant is a missing assertion
- tests are **deterministic** (control time/randomness/external deps); a flake is a bug, quarantine is not delete

## Output
Written under `solution/test/`:

| File | Captures | Format |
|---|---|---|
| `levels.md` | the two-tier test architecture + levels: level · scope · coverage target; the distribution shape chosen from the architecture (pyramid OR integration-weighted) | list: level · scope · coverage; CDC |
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
