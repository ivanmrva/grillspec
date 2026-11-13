---
name: derive-test-strategy
description: >-
  Decide the test strategy — the tier contract: what each tier covers, runs real, may mock, where it runs, and its coverage and mutation bars; at the regulated profile also traceability, edge discovery, NFR evidence and test data. Use when the spec and architecture exist.
disable-model-invocation: true
argument-hint: a recorded spec or design docs
---

# derive-test-strategy

**Load `${CLAUDE_PLUGIN_ROOT}/grill-shared/derive-engine.md` first and follow it.** This skill applies that method to the **test strategy**: which tests exist, what each tier may and may not do, and where each runs.

## Depth by profile
How much is written follows the project's profile:

| Profile | Mode | Written |
|---|---|---|
| `lite` | N/A | nothing here — the test tiers and their bars are a row in `arch/solution-strategy.md`, the runner setup is in the conventions |
| `standard` | decision mode | `levels.md` |
| `regulated` | full mode | `levels.md` plus `traceability.md`, `edge-discovery.md`, `nfr-evidence.md`, `test-data.md` |

Decisions live in the spec; the description lives in the artifact that enforces it — here the test configuration and the project's gate — and once code exists they are the source of truth for how the suites are built. Decision mode therefore records only the tiers, what must run real in each, where each runs, and the bars a change must clear; full mode also writes the test plans, because at `regulated` they are deliverables auditors and other teams read.

## The two tiers
A test's source is what it verifies; its timing is when its subject exists.
- **Tier A — per slice.** The unit, integration, contract and e2e tests of one slice, written with its task. This skill sets the standard they follow and does not enumerate them.
- **Tier B — system and cross-cutting.** Derived here from the spec, so that every requirement has a test that can fail:
  - a system acceptance test for every cross-feature journey, from the use-cases and UX journeys — written outside-in before the code so it drives it, and going green as slices land;
  - a fitness function for every load-bearing `ASR-` and architecture boundary — written when the boundary is decided, failing until the structure exists, then guarding it;
  - the contract suite, covering every `API-` and `EVT-`;
  - an evidence test for every `NFR-`, `ASR-` and `SLO-` — authored early from the target, executed once a deployable system exists.

Where a test runs follows its tier. Unit, integration and contract tests run locally; containers and compose files belong to the integration tier. E2e, journey, smoke and NFR-evidence tests run against a real deployed environment, because a local stack proves nothing about the deployed one.

## Decision record
`levels.md` is written in both modes and carries:
- the two tiers and the Tier-B suites, in a few lines;
- the distribution shape, chosen from the architecture: logic-heavy → a pyramid (many fast unit tests, fewer integration, a thin e2e top); integration-heavy, microservice or serverless → an integration-weighted shape. Either way the suite is not e2e-top-heavy;
- the e2e target environment, by name, taken from the infrastructure area's environment set: an isolated per-change preview environment where the project has one (real infrastructure, isolated, deterministic), otherwise a reserved e2e or staging environment. A green e2e or smoke run against it is the proof that the deploy pipeline shipped (`check_deploy_real.py` is the static backstop until the environment exists);
- the tier contract table.

### The tier contract
One row per tier with exactly these column names. The verifiers (`check_mock_budget.py`, `check_test_tiers.py`, `check_e2e_target.py` and the whole-build audit) parse the table as ground truth, and a mock policy that lives only in prose is checked by nothing.

`tier · scope · real-deps · may-mock · mock-ceiling · target-env · coverage-bar · mutation-bar`

`real-deps` is what must run real, `may-mock` the only doubles allowed, and `mock-ceiling` is `none`, `boundary-only` or `n-a`. Propose this default contract instead of inventing one per project:

| tier | scope | real-deps | may-mock | mock-ceiling | target-env |
|---|---|---|---|---|---|
| unit | pure logic, no I/O | — | — | none | local |
| integration | a module with its real collaborators | database, broker, filesystem (in containers) | third-party network at the boundary | boundary-only | local |
| contract | every `API-`/`EVT-` seam, consumer-driven with provider verification | all | — | none | local |
| e2e (journey · smoke · NFR evidence) | the deployed system | all | — | none | the named deployed environment |

Each row also carries `coverage-bar` and `mutation-bar`: the ratified numbers on the tiers they apply to, `—` elsewhere. A mock in a unit test means the unit is doing integration work: push the logic down into a pure function or the test up to the integration tier. A test that breaches its tier's ceiling is a defect the verifiers flag.

The coverage and mutation bars are rigor thresholds the organisation owns, so they are a ratify-point: propose concrete numbers with a one-line reason, for example ≥80% line coverage and ≥70% mutation score on changed domain logic. Mutation score is the quality bar because a coverage percentage can be met without assertions, while a surviving mutant is a missing one. The project's own gate enforces both bars through the test runner's configuration, on the changed code as well as the whole tree; a whole-tree percentage alone lets a small untested change hide in its slack.

## Rules
- **Cross-cutting obligations are tested in the slice that carries them.** The Tier-B penetration, accessibility and load runs attest the released system and come too late to gate a slice. So a slice's Tier-A set includes:
  - a deny-path test (over-limit, lapsed billing) for each `SEC-` deny rule and `ENTL-` gate its task brief lists;
  - an emission assertion for each `SLO-`-backing signal and `AEV-` analytics event;
  - a test that exercises a `DATA-` retention, TTL or deletion trigger, in the slice that owns it;
  - with i18n in scope, a string-externalisation fitness check and a pseudo-locale render of the touched screens.
- **A UI slice's Tier-A set includes its rendered-surface checks.** State-coverage tests for every interaction state the brief's `ux` field names, an accessibility scan (axe or equivalent: zero critical or serious findings, keyboard and focus path asserted), and a breakpoint render check against the frozen prototype. They gate with the slice, so the first feature's screens meet the bar the day they land.
- **Async behaviour is tested on the real path.** Jobs, schedules and eventually consistent flows get integration tests with the real broker and worker. They assert the eventual outcome and cover retry, idempotency, ordering and dead-lettering; asserting that a message was enqueued says nothing about the behaviour.
- **Fitness functions** cover dependency direction and layering (no cycles, the public API surface), coupling budgets, allowed technology, design-token conformance for a UI (semantic and component tokens only), and a no-fakes-in-production guard: no test double, stub or canned response is reachable from a production entrypoint. Author the guard as an import-graph rule in the project's language; `check_no_fakes.py` is the coarse cross-language backstop that fires before that rule exists.
- **Tests are deterministic.** Time, randomness and external dependencies are controlled. A flaky test is quarantined and fixed, not deleted.
- **Testing is discovery as well as verification.** A surprising property or fitness failure that no rule governs is a gap to resolve upstream, not only a bug to patch.

## Output
Written under `solution/test/`. The rows marked `full` are written only at `regulated`; in decision mode their content is not raised.

| File | Mode | Captures | Format |
|---|---|---|---|
| `levels.md` | decision | the decision record above | short prose, then the tier-contract table |
| `traceability.md` | full | which test level evidences each requirement and `ASR-` (the criterion-to-test trace is computed from the code, so it is not stored) | matrix |
| `edge-discovery.md` | full | the techniques that manufacture edges before production finds them: boundary-value · equivalence partitioning · property-based · fuzzing · mutation testing | short sections |
| `nfr-evidence.md` | full | the evidence plan (load/stress/soak/chaos · pen/SAST/DAST/IAST · a11y) with the target each test measures against · shift-right testing on the deployed system (synthetic monitoring · canary verification tied to a burn rate · flag-gated experiments) | table: requirement · evidence test · target |
| `test-data.md` | full | synthetic generation · PII-safe masking and subsetting · fixtures versus factories · scale data for load tests | short sections |

ADRs → `adr/ADR-TEST-NNN.md`
Consumes: the functional use-cases and UX journeys · the architecture boundaries and ASRs · the API contracts · the quality NFRs, observability SLOs and security requirements.

## Excludes
test implementation code — the Tier-B suites and the harness, which the walking-skeleton task seeds

## Resources
- `${CLAUDE_PLUGIN_ROOT}/grill-shared/derive-engine.md`
- Worked example: `examples.md`
