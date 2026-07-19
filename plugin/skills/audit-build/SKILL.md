---
name: audit-build
description: >-
  The whole-build audit — the independent, release-time attestation that the BUILD was done according to the spec's own process, not just that each task self-reported PASS. It judges the built system against the spec the way the whole-spec audit judges the spec. Owns the three things no per-task review can see: the evidence-ledger itself (did every gate really run, is every recorded VERDICT backed), cross-task emergent properties (suite shape vs the declared distribution, an AC- whose covering test a later task weakened, aggregate coverage/mutation), and the operate-ledger reconciliation. Distrusts the accumulated per-task verdicts on purpose. The judgment phases run as a parallel read-only multi-lens fan-out; report-only with NO fix/loop mode by design — fixes route to the task machinery and a fresh re-audit follows them. Loads the shared exec engine.
argument-hint: "[--depth attest|deep] [--scope release|all] — default: --depth attest --scope release"
---

# audit-build

**Load `${CLAUDE_PLUGIN_ROOT}/grill-shared/exec-engine.md` first and follow it.** This skill is the
**whole-build audit**: the independent, retrospective attestation that the built system was produced
**according to the spec's declared process** — the **judgment layer above the per-task gates**. It is to the
built system what the whole-spec audit is to the spec: a cross-cutting verification, run whole and
independent of any single task.

**It is an external audit, not inline QA.** The per-task conformance review is self-certifying — its own
`VERDICT: PASS` becomes the task's `conformance` gate row. This is the opposite posture: **periodic,
whole-system, and adversarial — it distrusts the accumulated self-reports** and re-checks that they
collectively hold and were honestly produced. The skill that certifies a build must not also be the one that
audits it; that separation is the reason this exists.

## What this skill uniquely does
The per-task conformance review already covers **code ↔ spec** for each task. This does **not** repeat that
per-task judgment — it does the three things that do not exist at any single task and that a self-certifying
review structurally cannot make:
- **1 · The evidence ledger itself.** Did every gate genuinely RUN and pass, or does a record merely *say*
  so? Is every recorded `VERDICT: PASS` physically present and backed? Were any Verification Records
  rubber-stamped? A per-task review *produces* these records, so it cannot audit its own output — this can.
- **2 · Cross-task / emergent properties.** Defects that live *between* tasks and are invisible to a per-task
  review even at full scope: an `AC-` whose covering test a *later* task weakened or deleted; the actual
  test-suite **distribution shape** vs the `pyramid`/`integration-weighted` shape the strategy declared;
  aggregate coverage/mutation across the whole suite (not per-slice); a fitness rule that was green per task
  but is now bypassed system-wide.
- **3 · Operate-ledger reconciliation.** Do the append-only `12-operate/` records correspond to the spec
  they enacted (a deploy record → the release's `T-`s and the ratified promotion path; a migration record →
  its `DATA-` change; an incident/diagnosis → the `NFR-`/`SEC-` it touched)? Nothing else checks this.

Everything of the form "does this module match its `role:`", "is this `SEC-` enforced", "is this NFR
evidenced" is the per-task conformance review's concern; here it appears only as an independent second look
(Phase 3), never as this skill's primary work.

## The two boundaries this skill lives between
- **Below it — the per-task gates.** The failing-test gate, the Verification Record checker, the fitness
  functions, the recorded per-task conformance verdict. **Trust each task's verdict as produced — then audit
  that they COLLECTIVELY hold and were honestly produced.** Do not re-litigate a single task's design; find
  where the *set* of them drifted, self-certified hollowly, or left an emergent gap. Your job starts where
  the per-task gate's per-task soundness ends.
- **Beside it — the whole-spec audit.** That judges the SPEC (is it consistent, complete, buildable); this
  judges the BUILD against that spec. **A clean whole-spec audit is a precondition** — you cannot attest a
  build against a spec that is itself broken; if the spec carries open `blocking` findings, say so and stop
  at `NOT-ATTESTABLE (spec not clean)`.

## Modes (depth)
| `--depth` | Runs | Max verdict it may issue |
|---|---|---|
| `attest` (default) | Phases 0–2 + 4 (the ledger/emergent/operate audit + a SAMPLED independent second-pass) — interim confidence between releases | `ATTESTED` / `NOT-ATTESTED` |
| `deep` | adds Phase 3 at FULL scope (an independent code-vs-spec re-judgment of every task) | `ATTESTED` / `NOT-ATTESTED` |

`--scope release` audits the tasks in the release/wave under attestation + everything they touch; `--scope all`
audits the whole built system.

**The release bar is a `--deep` run.** `attest` (sampled) is for cheap interim confidence; it is NOT the
ship gate — a sampled second-pass can miss the very task that overfit its visible tests (the risk is highest
in solo, non-orchestrated builds where no `AC-` was held out from the implementer). Before a release, run
`--deep`; the report records which depth it was so a release gate can require the full pass. The header
carries a machine-readable **`depth: deep`** or **`depth: attest (sampled N of M)`** marker for exactly that,
plus a **`commit: <HEAD sha>`** stamp of the tree you audited so a stale attestation (HEAD moved since) can be
rejected — record the current HEAD when you write the report.

## Ground rules
- **Source-of-truth fence (from the engine).** Audit the CURRENT working tree only — the built code, the
  test suite, the Verification Records, the `12-operate/` ledger. A missing artifact is a FINDING, never
  something to reconstruct.
- **Audit, don't mutate — and no `--fix`/`--loop` exists here, by design (see *The re-audit cycle*).**
  Report-only. If asked to fix, route each fix to its owner (a hollow record → back
  to that task's conformance review; a spec defect surfaced → the whole-spec audit; a real code gap → a
  focused-change `T-`). Never edit a Verification Record to make it pass, never touch `src/`.
- **Distrust by default.** A green record is a claim to verify, not a fact to accept. Where a claim can't be
  grounded from the working tree, that IS the finding — `important: unverifiable-claim`.
- **Severity on every finding:** `blocking` (the build was NOT done to process — a hollow gate, a lost `AC-`,
  a fake that shipped) · `important` (a real drift that will bite) · `nit` · `suggestion`. The attestation
  gates on `blocking` only.
- **Verify before flagging.** Quote `file:line`, the `T-` id, or the record path. A finding you can't ground
  is a guess — drop it.

## The judgment phases fan out — parallel read-only auditors, divergent lenses
Phases 1–3 are model judgment with variance: two independent reads of the same record disagree, one judge
misses what another catches. The object here is **finite and enumerable** (the done `T-` records, the test
tree, the ledger), so the recall remedy is **more independent judges within ONE pass** — never more passes
(that is the whole-spec audit's economics, where the blind-spot space is unbounded; here enumeration
dominates repeated sampling). Spawn **N=3 read-only auditors** (the `Explore` agent type — no Edit/Write;
they return findings tables only, never touch the tree), each with a distinct lens over the same scope:
- **evidence-backing** — does every cited artifact exist, and does it actually back the claim on its row
  (the `VERDICT: PASS` on disk, the test at the evidence path, the number vs its bar)?
- **test-bites** — would the covering test FAIL if the behavior broke? Assertion strength, interaction-only
  smells, mutation signal on the changed logic — the rubber-stamp detector.
- **cross-task drift** — did a LATER task weaken an EARLIER task's guarantee (a loosened assertion, a
  rescoped test, a bypassed fitness rule) that each per-task review, seeing only its own slice, missed?
Union the tables, dedup, then **ground every finding yourself** before it enters the report
(verify-before-flagging above). In `deep` each lens covers the full scope; in `attest` each lens covers the
risk-weighted sample. The fan-out buys back the judgment variance a single reader leaves on the table — at
one pass's cost.

## Phase 0 — mechanical aggregate baseline (run across ALL tasks, don't duplicate)
Run the deterministic tools at aggregate scope and record raw counts:
`python3 ${CLAUDE_PLUGIN_ROOT}/tools/check_task_record.py` per `T-` in scope (every gate row present +
PASS/`N/A`, evidence paths real, an independent `VERDICT: PASS` on disk) · `…/check_mock_budget.py` and
`…/check_test_tiers.py --require --require-all-tiers` (the tier contract from `test/levels.md` vs the actual
test tree — over-mocking, wrong-tier placement, a declared tier with no suite; **`--require` makes a test
tree with NO tier contract a blocking finding** — the strategy was never derived, so silence would be false
assurance — and **`--require-all-tiers`** makes a declared-but-unbuilt tier blocking too, which is correct
at release: the build is complete, so every tier must exist. The per-commit gate omits `--require-all-tiers`
because mid-build a tier legitimately hasn't landed yet). These gates classify tests by directory
(`tests/<tier>/`) OR filename (`foo.int.test.ts`; a bare `foo.test.ts` = unit) and read a real human-authored
`levels.md` (bold/parenthetical tier names, a scope comment above the table), so a **co-located** source-root
layout is handled — point `--tests` at the source roots if they're non-standard. If the project wired its OWN
equivalent tier/mock/e2e fitness against the same contract (e.g. a native pnpm check), prefer consuming that
gate's result over re-running the reference tools · `…/check_e2e_target.py` (e2e tests hit the named
deployed env, not a local stack) · `…/check_no_skips.py --strict` (no skipped/xfail'd/`.only`-focused test,
no CI test step that swallows a red — at release every declared deferral has expired, so WARNs are promoted)
· `…/check_no_fakes.py` / `…/check_deploy_real.py` /
`…/check_migration_real.py` over the whole tree · `…/check_operate_records.py` (Phase 4). Every ERROR →
`blocking`; every WARN → an `important` candidate to confirm. **Don't re-do what these decide mechanically —
run them, trust the output, spend your effort on the meaning below.**

## Phase 1 — ledger integrity (was the evidence real?)
The predicate here is "did the process actually happen", which no per-task self-report can answer about
itself. Walk each:
- **Backed, not asserted.** For a sample (in `deep`, all) of done `T-`: does the `conformance` gate row's
  cited `VERDICT: PASS` physically exist under `spec/10-delivery/verification/`, and does the record's
  evidence actually back it — the `@covers AC-`-tagged test exists and passes, the NFR row cites a
  *measurement* not a restated target, the `deploy` row's evidence is a real deployed-env run? A row that
  says PASS with evidence that isn't there is `blocking` — a rubber-stamp.
- **No silent scope reduction across the set.** A gate row quietly dropped, an `AC-` present in the task
  package but in no record, a `deploy`/`mutation` row uniformly `N/A` across many tasks with no stated
  reason — a pattern a per-task checker can't see because it only sees one record.
- **Gate freshness.** Run `…/check_freshness.py` — a task whose upstream spec drifted after its verdict was
  recorded has a *stale* PASS; route to re-run its conformance review.
- **The Tier-B release verdict exists and is backed.** A release in scope has a persisted
  `verification/test-run.md` whose per-NFR/SLO rows each cite a *measured* value against the bar
  `test/nfr-evidence.md` states — a missing Tier-B verdict, or one whose rows restate targets instead of
  measurements, is `blocking` (the release gate that never ran).

## Phase 2 — cross-task emergent properties (defects that live BETWEEN tasks)
- **Coverage survives, not just existed.** An `AC-` a task recorded as covered whose test a LATER task
  weakened, deleted, or `skip`ped. Re-run the aggregate suite and confirm every `AC-` still has a *passing*
  `@covers` test NOW — a per-task green at merge time does not prove it is green after the next merge.
- **Suite shape vs declared distribution.** Compute the actual tier counts and compare to the
  `pyramid`/`integration-weighted` shape `test/levels.md` declared. An e2e-top-heavy suite, or a "pyramid"
  that is 90% e2e, is a `blocking` process divergence even if every test is green.
- **Aggregate bars.** Whole-suite coverage/mutation against the ratified bars (a per-slice pass can still
  leave a system-level hole); the tier-contract ceilings holding across the WHOLE test tree, not just one
  slice.
- **Fitness bypass.** A fitness rule green per task but disabled/allow-listed system-wide, or an
  architecture rule the accumulated diffs eroded.
- **Dimension blindness.** A whole requirement class quietly dropped: a manifest dimension (`ux`/`a11y`/
  `obs`/`security` incl. `ENTL-`/`OBL-`/`ml`/`data` retention) whose gate rows read `N/A` **pervasively across
  tasks that plainly touch that surface** (UI tasks all `N/A — headless`, an instrumented product with every
  `obs` row `N/A`) — the signature of an obligation being waved through rather than genuinely inapplicable.
  Sample the N/As against the code the tasks shipped and flag each false one; one false `N/A` is a task
  defect, a pattern of them is a `blocking` process divergence.

## Phase 3 — independent second-pass judgment  *(--depth deep only — full re-judgment)*
The semantic checks that are model-judgment even for a per-task review — mock placement vs each tier's
purpose, right-tier logic, real-path-where-required, interaction-only assertions, semantic conventions
adherence (`coding-standards`: error handling, ubiquitous-language naming, prescribed patterns). This
re-runs the code-vs-spec conformance review **independently and adversarially over the whole build** —
defense in depth against a weak or skipped per-task judgment. In `attest` mode this is SAMPLED (the risky
slice — new seams, the tasks with the thinnest records, anything a Phase-0 tool warned on); `deep` runs it
over every task. Sampling is a stated limit, never a silent one — record what was sampled and what was
skipped.

## Phase 4 — operate-ledger reconciliation
For each `12-operate/` record in scope, confirm it corresponds to the spec it enacted (it is an append-only
log of reality, so this is *reconciliation*, not re-derivation — never rewrite a record to match the spec):
- a `deploy-<env>-<version>.md` names real `T-`s in the release and an env on the ratified promotion path
  (`infra-ops/topology.md`); a `migration-*.md` cites the `DATA-` change it enacted; an
  `incident-<id>.md`/`diagnosis-<id>.md` references the `NFR-`/`SEC-`/`SLO-` it touched **and carries a
  learnings row whose gap/assumption actually landed in the spec** (the propagation promise, audited — an
  incident whose postmortem says "route to discovery" with nothing routed is an unclosed loop); a first prod
  promotion has its `production-readiness.md` with a go/no-go verdict and *verified* (rehearsed) evidence
  per item; the deploy records' change-failed/recovery-time fields roll up against the
  `infra-ops/delivery-metrics.md` targets.
- **a record that references a spec ID that doesn't resolve**, or **a release whose deploy record is
  missing entirely**, is `important` (a gap in the operational trail); a record that *contradicts* the spec
  it claims to enact (deployed to an env not on the promotion path) is `blocking`.

## The re-audit cycle (fixes never happen here)
This skill must never gain a `--fix`/`--loop`: **the attestor cannot fix what it attests** — editing a
record or a test to satisfy the audit is the exact fraud Phase 1 hunts — and build fixes run through the
engineering workflow (a `needs-rework`/focused-change `T-` → implement → run-tests → conformance-review →
CI → merge), which is asynchronous and branch-shaped, not an in-session edit. The cycle is therefore:
**`NOT-ATTESTED` + routed findings → the owning machinery lands the rework waves → a FRESH audit.** The
`commit:` stamp plus the release gate's `--require-fresh` already invalidate an attestation the moment HEAD
moves, so every fix forces the re-audit mechanically. On a re-audit after a remediation wave, you may scope
the **Phase 1** re-checks to the tasks touched since the last report (the ledger is enumerable — re-check
what changed); **Phases 2 and 4 always run full** (emergent properties and the operate trail don't scope
down). The `ATTESTED` that gates a release is always a **fresh, full `--deep`** pass — never a scoped
re-round promoted to a verdict.

## Output
Write **`build-audit-report.md` at the PROJECT ROOT** (a sibling of `spec/`, like `spec-audit-report.md` —
meta-commentary, not timeless project documentation, so it never goes inside the closed-world `spec/`).
Print a summary to the session. The report contains:

| Section | Contents |
|---|---|
| Attestation header | **BUILD ATTESTATION: ATTESTED / NOT-ATTESTED** (or `NOT-ATTESTABLE (spec not clean)` if the whole-spec audit has open blockers) + the release/wave scope + the blocking count + the **`depth: deep` / `depth: attest (sampled N of M)`** marker + a **`commit: <HEAD sha>`** stamp of the exact tree you audited (so a release gate can confirm the attestation still covers HEAD and reject a stale one) |
| Ledger findings | rubber-stamped records, unbacked `VERDICT`s, dropped gate rows, stale PASSes — each `T- · record path · claim · what's missing` |
| Emergent findings | lost/weakened `AC-` coverage, suite-shape divergence, aggregate-bar misses, fitness bypasses — each grounded in the aggregate run |
| Operate reconciliation | operate records that dangle or contradict the spec they enacted |
| Independent second-pass | the sampled (or full) re-judgment deltas vs the recorded per-task verdicts — where an independent look disagrees |
| Top fixes | must-fix-before-release items, each routed to its owner (re-run the task's conformance review · surface to the whole-spec audit · a new focused-change `T-`) |

The `BUILD ATTESTATION:` verdict line in this report is the artifact an opt-in release gate
(`check_release_attestation.py`) reads — so an `ATTESTED` here can be made a required check before a
release ships, if the team chooses to enforce release gating.

No code, no `spec/` edits, no record edits. **Never claim "attested" on a sampled slice as if it were
full** — state the sample. A defect in THIS SYSTEM (a wrong check, an unsatisfiable rule) is routed via
`${CLAUDE_PLUGIN_ROOT}/tools/plugin_feedback.py`, never into the audit report.

## Resources
- `${CLAUDE_PLUGIN_ROOT}/grill-shared/exec-engine.md`
- Worked example: `examples.md`
