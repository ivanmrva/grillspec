---
name: audit-build
description: >-
  Check the whole build against the spec before a release, from the tree: done-claims hold, every acceptance criterion still has a real test, nothing faked or skipped ships. Short at the lite and standard profiles, exhaustive at regulated. Report-only. Loads the shared exec engine.
argument-hint: "[--depth attest|deep] [--scope release|all] — default: --depth attest --scope release"
---

# audit-build

**Load `${CLAUDE_PLUGIN_ROOT}/grill-shared/exec-engine.md` first and follow it.** This skill is the whole-build audit: before a release, it checks that what was built is what the spec asked for and that it was built honestly. Its evidence is the working tree — the task briefs, the code, the tests, the configuration — read by the tools and by you. A task marked `done` is a claim to check, not a fact to accept.

It looks at what no single task can show. A per-task check sees one slice at the moment it lands; this audit sees the whole tree as it is now, including what later tasks did to earlier ones. It does not re-argue one task's design. It is report-only: an audit that edits a test or a brief to satisfy itself has stopped being an audit.

## How much to run
Read the settings first: `python3 ${CLAUDE_PLUGIN_ROOT}/tools/project_config.py`. With no settings file the tools assume `regulated` and `pr`.

| Profile | Depth for a release | What that is |
|---|---|---|
| `lite` · `standard` | `attest` (the default) | a short check one person can run in one sitting: the mechanical baseline, then sampled reading, by this session alone |
| `regulated` | `deep` | the exhaustive attestation: every done task read against its criteria, three independent read-only auditors, the operations records reconciled |

| `--depth` | Runs |
|---|---|
| `attest` | Phases 0–2 and 4, with the reading in Phases 1–2 done on a risk-weighted sample |
| `deep` | the same over every task, plus Phase 3 (an independent reading of all code against the criteria) |

`--scope release` covers the tasks finished since the last release and everything they touch; `--scope all` covers the whole built system. An `attest` run at `regulated` is useful between releases, but it is not that profile's release bar; say so in the report.

**The spec must be fit to audit against.** At every profile, `python3 ${CLAUDE_PLUGIN_ROOT}/tools/lint_spec.py` reports no ERROR. At `regulated`, the release also needs a full-depth `spec-audit-report.md` whose `commit:` stamp is the current HEAD and whose blocking count is zero; that report is transient, so when it is absent or stale, run the spec audit first. If the spec is not clean, stop with `NOT-ATTESTABLE (spec not clean)` and say what blocks it.

## Ground rules
- Audit the working tree as it is (the engine's source-of-truth rule). A missing artifact is a finding, not something to reconstruct.
- Edit nothing: no code, no test, no brief, nothing under `spec/`. Each finding names who fixes it (see *After the audit*).
- Every finding carries a severity: `blocking` (the build was not done as claimed: a done-claim with nothing behind it, a criterion with no real test, a fake that ships) · `important` (a drift that will cause a defect) · `nit` · `suggestion`. The verdict gates on `blocking` alone.
- Ground each finding before it enters the report: quote `file:line`, the task id or the criterion id. Where a claim cannot be checked from the tree, that is the finding: `important: unverifiable-claim`.
- Say plainly what was sampled and what was not read. A sampled pass reported as a full one is the audit's own version of an unbacked done-claim.

## Phase 0 — mechanical baseline, over the whole tree
Run from the project root and record the raw counts. Every ERROR is `blocking`. Every WARN is an `important` candidate you confirm or dismiss with a reason. These tools decide what they check; run them, take the output as given, and spend your effort on the reading below.

| Command (under `python3 ${CLAUDE_PLUGIN_ROOT}/tools/`) | What it decides |
|---|---|
| `check_task.py spec` | the status of every task, and whether each `done` claim holds: a `@covers` test for every criterion in the brief, a `@state:` test for every named UI state, no unresolved gap, dependencies done, `review \| PASS` on a `critical` task, the design note of a design-first task present |
| `check_task.py spec --trace` | the criterion → task → test-file matrix, for Phase 1 |
| `check_no_fakes.py --strict` | no test double or mocking-library import in the production tree |
| `check_no_skips.py --strict` | no skipped, expected-to-fail or focused test, and no CI test step that swallows a failure |
| `check_orphan_tests.py` | every test file carries a spec driver tag, and every `@covers` id exists in the spec |
| `check_deploy_real.py --strict` · `check_migration_real.py --strict` | the deploy pipeline really deploys; each migration really migrates |
| `check_config_drift.py` | every environment variable the code reads is declared in `infra-ops/environments.md` |
| `check_mock_budget.py` · `check_e2e_target.py` | no test mocks beyond its tier's ceiling; no e2e test points at a local stack |
| `check_test_tiers.py --require --require-all-tiers` | every tier the contract declares has a suite; prints the per-tier file counts |

`--strict` promotes each tool's review-later warnings to errors, which is right at a release: nothing deferred should still be waiting. `--require-all-tiers` makes a declared tier with no suite an error, for the same reason.

The last two rows read the tier contract in `spec/09-solution/test/levels.md`, and `check_config_drift.py` reads the environment matrix. Both files exist at `standard` and above. At `lite` those four tools have nothing to read and exit cleanly, so leave out `--require` (it fails a project that has tests but no tier contract) and rely on the project's own gate for the test bars.

If a tool is missing from this install (a standalone copy of the skill carries only some of them), list it as not run; do not approximate its result by hand.

Then run the project's own gate, whole, with the command its conventions name (the root `AGENTS.md` states it). The gate carries what these tools do not: format, lint, types, build, the test suites actually passing, the coverage and mutation bars, and the architecture fitness functions. Where the project has ported one of the checks above into its gate, use the gate's result for it.

Two settings decide what the tools can see. `check_no_fakes.py` and `check_config_drift.py` scan `src/` unless given `--src <dirs>`. A monorepo that keeps its code under a wrapper directory sets `GRILLSPEC_TEST_ROOTS` so the test-facing tools find its tests. When a tool reports nothing to scan in a project that plainly has code and tests, fix the roots before trusting a clean result.

**Jobs that do not run on every push.** In `trunk` delivery, CI only deploys the default branch and smokes it; the full gate in CI, the integration suite, the security and dependency scan, the accessibility check, the visual baseline and the mutation run are dispatch-only. This audit is where they run once before a production release. Dispatch each job the project's conventions define and read its result. A job you cannot dispatch from this session is listed as not run, with the command the operator needs. In `pr` delivery these jobs ran on each pull request, so confirm they are green on the commit being released.

## Phase 1 — do the done-claims hold?
`check_task.py` proves that a tagged test exists for every criterion. It cannot tell whether that test would fail if the behaviour broke. Read for that. At `attest`, sample by risk: every `critical` task, the tasks with the thinnest tests, anything a Phase 0 tool warned about. At `deep`, read every done task.

- **The test bites.** For each criterion, open the tests the trace lists and check that they assert the criterion's outcome through the public interface. A test that carries the tag but asserts nothing, asserts only that a collaborator was called, or checks a weaker condition than the criterion states is `blocking`: the criterion is unproven.
- **The obligations in `rules` were built.** `check_task.py` tracks criteria and UI states, not the cross-cutting obligations a brief lists. For each one — an authorization rule, an entitlement limit, a retention trigger, a quality target, an emitted signal — find the test in the slice that proves it: the deny path, the over-limit path, the measured number. None found is `important`, and `blocking` when the obligation guards money, personal data or access.
- **The tier was honest.** A done task whose change includes a schema or data migration, an authentication, authorization, erasure or billing path, a model seam or another one-way door, but whose brief says `feature` or `routine`, skipped the design note and the independent review. `important`; the fix is to raise the tier and run the review. You can see that a `critical` brief carries `review | PASS`; you cannot see who wrote it, so where the review matters most, read the code as the reviewer would.
- **UI slices were classified as UI.** A brief with `ux: N/A` whose `touches` names screens or components escaped the state, accessibility and prototype checks. Compare a sample against the code the task shipped.

## Phase 2 — what only the whole tree shows
- **Coverage still holds.** A criterion covered when its task landed can lose its test to a later refactor. The gate run and the trace together show it: every criterion of a done task has a test that exists and passes now.
- **Present is not executed.** A test file the tools see but the runner never runs counts for `@covers` while asserting nothing. Read the runner configuration for exclusions (ignored paths, a glob that misses a directory). Where the runner emits a list of executed files, compare it with the test tree. A test that is present and never executed is `blocking`.
- **The bars are the ratified ones.** The coverage and mutation thresholds in the test-runner configuration equal the bars the spec records (the tier contract, or the solution strategy at `lite`). A threshold lowered in configuration is `blocking`.
- **Suite shape.** Where the tier contract declares a shape, compare it with the per-tier counts from `check_test_tiers.py`. A suite that is mostly e2e under a declared pyramid is an `important` divergence even when every test passes.
- **Waivers.** Every `.grillspec/*-allow.txt` entry and every inline `allow` comment silences a check even under `--strict`. Read each one: it needs a reason that is still true. An entry whose reason has expired, or that appeared with a task which would otherwise have failed, is a `blocking` bypass.
- **Fitness functions and gates are intact.** A rule disabled or allow-listed for the whole project; a test step removed from the gate or the CI workflow; a hook configuration that stopped pointing at `.grillspec/tools/gate_exec.py`. Removal is the one change the content checks cannot see, so a removed or disabled check is `blocking` until it is restored and green.
- **The deployed system matches.** The smoke check against the deployed environment is green on the commit being released, and the e2e suite ran against the environment the spec names, in this audit or in an operator run you can cite.

## Phase 3 — independent reading of all code *(`--depth deep` only)*
Read every done task's code against its criteria and the project's conventions, as a reviewer who did not write it: behaviour matches each criterion, module boundaries hold, tests sit in the right tier and mock only what that tier allows, errors and naming follow the conventions. Report where your reading disagrees with the task's done-claim.

At `deep`, spread the reading in Phases 1–3 over three read-only auditors (the `Explore` agent type; they return findings tables and edit nothing), each with a different lens over the same scope, because two independent reads of one test disagree often enough to matter:

| Lens | Asks |
|---|---|
| test strength | would this test fail if the behaviour broke? |
| later damage | did a later task weaken an earlier task's guarantee: a loosened assertion, a narrowed test, a bypassed rule? |
| obligations | is every rule a brief lists, and every criterion, visible in the code and proven by a test? |

Union their tables, remove duplicates, and confirm each finding yourself before it enters the report. One pass with several readers is enough: the set of tasks is finite, so more readers help and more rounds do not. At `attest`, do the reading yourself.

## Phase 4 — operations records
`spec/12-operate/` holds dated records of what happened to the running system. For the release in scope (at `regulated`, for every record), read each against the spec it refers to:
- a deploy record names tasks that exist and an environment on the recorded promotion path;
- a migration record names the `DATA-` change it carried out;
- an incident or diagnosis record names the requirement it touched, and the lesson it records has reached the spec area that owns it;
- a first production release has its production-readiness record, with evidence that was exercised and a go or no-go.

A record that points at an ID that does not exist, or a release with no deploy record, is `important`. A record that contradicts the spec (a deploy to an environment off the promotion path) is `blocking`. These records log what happened, so the fix is a new or corrected entry going forward, and the report says which.

## After the audit
Route each finding to its owner, then audit again:

| Finding | Goes to |
|---|---|
| a criterion without a real test, a weakened test, a missing obligation test | the task: set its status back to `in-progress`, or a `routine` fix with a failing test first |
| an under-tiered task | raise the tier in the brief and run the fresh-context conformance review |
| the spec is wrong or silent | the spec area that owns the fact (the spec audit, or the conductor) |
| a lowered bar, a removed gate, an unjustified waiver | restore it, then fix what it was hiding |

A verdict covers the tree it was run on, which is why the report records the commit. After fixes land, run the audit again; on that run you may limit Phase 1 to the tasks that changed, while Phases 0 and 2 always cover the whole tree. A release verdict comes from a complete run at the profile's release depth.

## Output
Write `build-audit-report.md` at the project root, beside `spec/`. It is a transient session report: git-ignored, and not written under `spec/`. Print a summary to the session.

| Section | Contents |
|---|---|
| Header | `BUILD ATTESTATION: ATTESTED` or `NOT-ATTESTED` (or `NOT-ATTESTABLE (spec not clean)`) · the blocking count · scope · `profile:` and `delivery:` · `depth: deep` or `depth: attest (read N of M tasks)` · `commit: <HEAD sha>` · what showed the spec clean |
| Mechanical baseline | each Phase 0 tool and the gate: its counts, or "not run" with the reason |
| Done-claims | unproven criteria, weak tests, missing obligation tests, under-tiered tasks — each with task · criterion · file |
| Whole-tree findings | lost coverage, unexecuted tests, lowered bars, waivers, removed gates |
| Dispatched jobs | each job, its result, or "not run" with the command |
| Operations records | records that dangle or contradict the spec |
| Top fixes | what must be fixed before the release, each with its owner |

A defect in this system itself (a check that is wrong, a rule that cannot be satisfied) goes to `${CLAUDE_PLUGIN_ROOT}/tools/plugin_feedback.py`, not into the audit report.

## Resources
- `${CLAUDE_PLUGIN_ROOT}/grill-shared/exec-engine.md`
- Worked example: `examples.md`
