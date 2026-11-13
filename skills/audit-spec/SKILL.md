---
name: audit-spec
description: >-
  Audit an existing spec for consistency, completeness against its project profile, leanness, and whether an agent can build from it without guessing — the judgment above the linter. Report-only by default; --fix remediates, --loop repeats until a pass finds nothing. Loads the shared exec engine.
---

<!-- grillspec-portable-resources -->
> Resource paths in this skill are relative to this installed skill directory. Resolve `references/...` and `scripts/...` from that directory, not from the project working directory; use an absolute path when executing a bundled script.

# audit-spec

**Load `references/exec-engine.md` first and follow it.** This skill is the whole-spec audit: one pass across every area that asks whether the spec is consistent, complete for its profile, no larger than it needs to be, and buildable. The tools decide everything mechanical. Run them, take their output as given, and spend your effort on what a script cannot judge: meaning.

Keep two questions apart in everything you report. Spec health: is the spec consistent and complete enough? Bet health: do the product's bets hold? A clean spec beside an untested bet is a normal and useful result, and merging the two hides it.

The per-task conformance review checks code against the spec, one task at a time. This skill checks the spec itself, whole, whether or not anything has been built.

## Audit against the profile
Read the project settings first: `python3 scripts/project_config.py`. The `profile` records how much spec the project chose to carry, and the audit holds the spec to that choice, not to the largest one. With no settings file the tools assume `regulated`; say so in the report, because every "missing" finding then rests on an assumption the owner can correct in one line.

| Profile | Areas in scope | The solution layer is |
|---|---|---|
| `lite` | problem validation · product vision · constraints · domain model · functional spec · quality · architecture · conventions · tasks | the architecture only; the few decisions the other solution areas would own are rows in `arch/solution-strategy.md` |
| `standard` | `lite` plus goals · system context · data · security · compliance · entitlements · integration · ML requirements (AI products) · design system and UX (UI products) | the architecture plus seven decision records |
| `regulated` | every area | the architecture plus the seven areas written in full |

- An empty area outside the profile is not a finding. An in-profile area that is empty, or inconsistent with its neighbours, is.
- Market, customer discovery, monetization, go-to-market and growth are optional at every profile. They are not required; audit them for consistency only when they exist.
- Below `regulated`, the seven solution areas (data, API contracts, security, observability, infrastructure and operations, test strategy, ML) are decision records. Judge whether each decision the build depends on has been made: the store and its tenancy, the seam list with its versioning and error policy, where authorization is enforced and how keys are held, the objectives that page someone, the environments and promotion path with the configuration each needs, the tier contract in `test/levels.md`, a model's fallback and the gate it must pass. A missing table design, OpenAPI document, control register or runbook is not a gap at these profiles, because the schema, the contract package, the policy code and the alert configuration state those better than a document can.
- When the product has outgrown its profile — it handles personal data, money or paid tiers at `lite`, or its documents have become a deliverable for an auditor at `standard` — report that as one finding that recommends the larger profile, not as a list of missing areas.

## What the tools already decide
`lint_spec.py` settles structure and the ID graph. None of this is yours to re-derive:

| Group | What the linter settles |
|---|---|
| structure | files only at allowed paths · file headers · placeholders · dangling links |
| ID graph | every reference resolves · one definition per ID, in its owning area · references point upstream only |
| coverage | each element has its downstream: a command its use-case, a use-case its criteria, a criterion exactly one owning task, a threat its control, an obligation its control, an NFR its evidence |
| structured facts | state machines · authorization completeness · a typed fact stated twice agrees · every NFR names its enforcement |
| tasks | no unresolved gap · acyclic dependencies · a risk tier · criteria text inline · UI slices carry their journey, states, accessibility cell and a reviewed prototype · credentials provisioned for unattended work |
| ratification | a value still marked `unconfirmed` |
| lean and timeless | edit-trace stamps, dates and edit-history phrasing · content in an area outside the profile · a full-mode file below `regulated` |

Severity carries over unchanged. A linter ERROR is a `blocking` finding, quoted as the tool printed it. A WARN is an `important` candidate that you confirm or dismiss with a reason. An INFO is a candidate the linter flagged because it could not decide it, so the decision is yours.

## Modes
| `--depth` | Runs | Verdict it may issue |
|---|---|---|
| `consistency` | Phases 0–2: cheap and repeatable | at best `CONSISTENT (domain not assessed)` — it cannot declare readiness |
| `full` (default) | adds Phase 3 (domain and usage completeness) and Phase 4 (code-gen readiness, bets) | `CODE-GEN READINESS: READY` or `NOT-READY` |

`--scope all` audits the whole spec. `--scope <area>` reads one area and the areas it references or is referenced by, for a focused re-check after a change.

Report-only is the default. Two modes edit the spec:

| Mode | Does | Ends when |
|---|---|---|
| `--fix` | one audit pass, then fixes every finding in the area that owns it and works through the impact set in the same session | findings fixed · impact set worked through · mechanical baseline green |
| `--loop` | repeats full-depth `--fix` passes with parallel read-only auditors — load `remediation-loop.md` (beside this file) and follow it | two consecutive rounds find nothing new, a final full sweep is clean, and the baseline is green |

**What "fixed" means.** A fix is finished when everything that depended on the changed fact agrees with it. After the last edit, run `python3 scripts/impact.py <changed-IDs…>` (or `--since <ref>` to collect the IDs from the git diff). It prints every spec file, task brief and test that references those IDs, upstream first. Re-read each one against the changed fact and edit the ones it invalidates. The task briefs and the conventions come last in that order and are the ones a partial pass leaves behind. The root `AGENTS.md` sits outside `spec/`, so the tool does not list it; re-read it whenever the conventions change. Then run the Phase 0 baseline again. Report "fixed" only when the impact set has been worked through and the baseline is green. An item you cannot settle because it needs a decision only the user holds is listed in the report as an open hand-off.

## Ground rules
- Audit the working tree as it is (the engine's source-of-truth rule). A missing artifact is a finding to report, not something to reconstruct.
- In report-only mode, edit nothing under `spec/` and no code. The read-only auditors a loop spawns edit nothing in any mode.
- Every finding carries a severity: `blocking` (the build would be wrong, or a hard invariant is broken) · `important` (a gap or ambiguity that forces a guess) · `nit` (style) · `suggestion` (a deepening). Verdicts gate on `blocking` alone.
- Ground each finding before it enters the report: read the artifact and quote `file:line` or the stable ID. Drop what you cannot ground, because an ungrounded finding applied in `--fix` damages a correct spec.
- A defect is fixed where the fact is owned. Every file under `spec/` is an authored document, edited in place under the rules of the skill for its area: the smallest change in meaning, re-authored so the file reads as written in one pass. When a downstream file is wrong because its upstream is wrong or silent, the fix goes upstream and the downstream follows through the impact set; patching only the downstream leaves the two disagreeing. When spec and code disagree, decide which is right before touching either, so the spec is not bent to match a bug. Name the owning area in each finding.

## Phase 0 — mechanical baseline
Run these from the project root and record the raw counts.

| Tool | Gives you |
|---|---|
| `python3 scripts/lint_spec.py` | ERROR, WARN and INFO findings over `spec/` |
| `…/spec_status.py` | the profile, element counts, use-cases with criteria, task status, mechanical blockers |
| `…/check_contracts.py` | whether the IDs in the machine contracts resolve |
| `…/impact.py <ID…>` | the files that depend on an ID you suspect |

`check_contracts.py` applies where `spec/09-solution/api` holds an OpenAPI or AsyncAPI file (normally the `regulated` profile). An ID a contract references that is defined nowhere is an ERROR; an operation without its traceability fields, a security scope on a mutation, or an error response is a WARN. It exits cleanly when there are no contracts or PyYAML is not installed, so it is safe to run always.

If a tool is missing from this install (a standalone copy of the skill carries only some of them), report it as not run; do not approximate its result by hand.

## Phase 1 — consistency judgment
These questions are about meaning, so no script answers them soundly.
- **Contradictions.** The same number, policy or boundary stated in two places that disagree (retention of 30 days in the data area, 90 days in compliance); a term used two ways inside one bounded context; an actor named differently across areas. The linter sees a dangling ID; it cannot see two resolving IDs that state conflicting facts. `blocking`.
- **The right type.** An item filed as `NFR-` that is really an obligation (`OBL-`), or a "requirement" that is a domain rule. The linter checks the folder; you check the concept.
- **Scope.** Content that breaks its own file header's `scope` or `excludes`; in-scope and out-of-scope kept consistent from the vision through the functional spec to the tasks, so nothing excluded is built and nothing required is excluded.
- **Decisions.** Each deliberate, costly-to-reverse decision or exclusion has an ADR; no two ADRs contradict; no artifact contradicts a live ADR.
- **Bars with teeth.** Each requirement is a measurable bar with a named enforcement that can actually fail (a test, a gate, a lint rule, an infrastructure setting, a review), not a number nothing checks.
- **Adequacy, beyond presence.** The linter confirms that a `THR-` threat links to a `SEC-` control. You judge whether that control mitigates that threat. The same holds for an obligation and its control, and for an NFR and its evidence.

## Phase 2 — fit: leanness, readiness, drift
**Leanness.** An area, a file, a rule or a gate earns its place by having a reader: a later step, a tool, or a person who will act on it. Content with no reader is a finding whose fix is to remove it, not to complete it. Look for:
- the same fact stated in two areas — keep it in the area that owns it and reference the ID elsewhere, with a few words saying what the ID is;
- a full-mode artifact below `regulated` (a table-by-table schema, a hand-written OpenAPI document, a control register, a runbook) that restates what code states;
- a table cell holding a paragraph — either the item needs its own short section, or most of the cell has no reader;
- narrative about how the document changed: dates, resolved-on stamps, "previously", "this round";
- a rule, gate or fitness function that nothing enforces and nobody would miss, or a catalogue written up front for concerns the product does not have.

The linter's timeless-artifact and profile checks (its checks 40 and 41) flag the mechanical half of this list; confirm those and find the rest by reading. Rate a leanness finding `important` when the duplicate can drift into a contradiction or the excess hides a decision a reader needs, otherwise `nit`. Report these under their own heading so that "remove" is not mistaken for "complete".

**Readiness gates.** Report each gate as met or not met, with what blocks it. Count only in-profile areas.

| Gate | Met when |
|---|---|
| desirability (soft) | the riskiest desirability bets are named, each with a test plan |
| architecture-readiness | the in-profile foundation and requirement areas (design system and UX for a UI product) are consistent and hold no unresolved gap, so the solution layer can be trusted |
| implementation-readiness | the in-profile solution areas are consistent and hold the decisions the conventions and tasks build on, including the module map |
| delivery-readiness | conventions exist; every in-scope use-case is covered by a task and every criterion owned by exactly one; the tasks can name what they deploy to and test against |

What the tasks deploy to and test against is the environments and promotion path, the test tiers with their bars, and the e2e target environment. At `standard` and above those decisions live in `infra-ops/topology.md`, `infra-ops/environments.md`, `infra-ops/cicd.md` and `test/levels.md`. At `lite` they are rows in `arch/solution-strategy.md` and the conventions. A task that deploys to "the first environment of the promotion path" when no promotion path is recorded is a delivery-readiness blocker.

**Drift.** Does each artifact still follow from its current upstream? No tool decides this. When the audit follows a known change, `impact.py --since <ref>` lists the files to re-read. Otherwise check the places where one area quotes or projects another: the use-cases against the domain model, the criterion text quoted in each task brief against the functional spec, the conventions and `AGENTS.md` against the architecture and the stack. A downstream statement that does not follow from its current upstream is `blocking` when a task builds on it and `important` otherwise. A difference you judge immaterial (a typo fix upstream) is dismissed with a note.

## Phase 3 — domain and usage completeness *(`--depth full` only)*
A spec in which every reference resolves can still omit a whole category of real behaviour, and no reference check finds something that is missing. You find it by building your own model of the domain and comparing. This phase is the reason the skill exists; do it for real.

Start with the blind model, before reading the domain area closely, because reading it first anchors you to its blind spots. From discovery, the vision and your own knowledge of this domain, write down the real entities, each entity's full lifecycle, the core business rules, the money, time and identity mechanics, the regulatory facts, and every actor with their real goal. Then compare with the spec. Each item in your model with no home in the spec is a candidate missing branch.

Then apply the lenses that fit the product. A product that handles no money has no rounding edge to find.
- **Lifecycle.** For each entity, the states the business needs, especially the abnormal endings products forget: cancel · refund · dispute · expire · suspend · reactivate · merge · split · delete or erase · archive · account closure · fraud hold.
- **Journeys.** For each persona and job, the unglamorous steps: first run and empty state · abandon and return · permission changed mid-action · offline or flaky · many at once · undo · hitting a limit · blocked by another actor. At each step ask what the system does. No answer is a gap.
- **Rule collisions.** For each rule, its exceptions and exact boundary, and what happens when it meets another rule: a refund on a partly shipped order, two promotions stacking, a downgrade with usage already over the new limit.
- **Edge generators.** Money (rounding, currency, zero and negative, tax, partial) · time (time zone, DST, ordering, retroactive change, expiry, clock skew) · identity (duplicates, merges, renames, deletion of something referenced) · quantity (zero, one, maximum, fractional, oversell) · concurrency (two actors on one resource, lost update) · dependents (what happens to children when the parent goes).
- **Is the model right, not only consistent?** Do the bounded contexts match how the business divides its world? Do the aggregate boundaries sit where the real transactional invariants are? Is the language the domain expert's own? A consistent model of the wrong thing yields correct code for the wrong product, which is the most expensive failure.

Where the domain is specialised and you cannot check a claim from first principles (clinical logic, tax or financial regulation, safety rules), mark it `important: needs-domain-validation` and route it to a domain expert or a throwaway spike. Confirming a rule you cannot check is worse than flagging it.

## Phase 4 — code-gen readiness and bets *(`--depth full` only)*
**Each task brief.** Could an agent build the slice from the brief and the code alone? The linter checks the form. You judge the content:
- the criteria the brief quotes still match the functional spec, and together they deliver the outcome the brief states;
- `touches` names real modules and seams from the architecture;
- `rules` carries every cross-cutting obligation that binds the slice: an authorization rule, an entitlement limit, a retention trigger, a quality target, an emitted signal. An obligation defined upstream that reaches no brief's `rules` cell will not be built, so it is `important`;
- the tier matches the risk. A slice with a schema or data migration, an authentication, authorization, erasure or billing path, a model seam or another one-way door is `critical`, and a `critical` brief names its design note and carries a `review` row. A brief tiered below its risk is `important`, because the lighter tier skips the design note and the independent review that risk calls for;
- a UI slice marked eligible for unattended work has a prototype a human reviewed, or a recorded waiver;
- every human prerequisite is provisioned in `spec/_provisioning.md` or the task is marked blocked. A slice that cannot be built without an unmet human action is `blocking`;
- every decision the code needs is in the spec or an ADR.

**Unratified values.** Some values belong to the user or organisation: quality and SLA numbers, retention and residency, jurisdiction, prices and tier limits, the environment set, vendor and region commitments, the accessibility level, test-rigor bars, authorization allow-rules, the MVP cut. One still marked `unconfirmed` is a default the human has not seen, so it is not a settled requirement. Flag each one a slice builds on: `blocking` on a critical path (a number a slice is built to, a price, a residency footprint), otherwise `important`, routed to "surface for ratification". Consider only the values the product actually has.

**Bets (kept separate from spec health).** Every bet has a validation status. Every critical bet is Validated or Accepted-risk; an Invalidated critical bet is a high-priority open point. Kill-criteria exist and are measurable. Each recorded risk has an owner and a mitigation.

## Output
Write `spec-audit-report.md` at the project root, beside `spec/`. It is a transient session report about the spec, not part of the spec, so it stays out of `spec/` and is git-ignored. Print a summary to the session.

In the summary and in "Top fixes", give each fix as a chain in dependency order: where the symptom shows → the edit in the owning area → the files `impact.py` says depend on it → how to verify. Order the chains so that an upstream edit comes before the work that depends on it.

| Section | Contents |
|---|---|
| Verdict header | `CODE-GEN READINESS: READY` or `NOT-READY` (or `CONSISTENT (domain not assessed)`) · the blocking count · each readiness gate · `profile:` · `depth:` · `commit: <HEAD sha>` of the tree audited, so a reader can tell whether the report still covers the current spec |
| Findings | sorted `blocking` → `important` → `nit` → `suggestion`: severity · area · location · what is wrong · where the fix goes |
| Contradictions | each with both locations quoted |
| Missing branches | from Phase 3, each concrete: "X exists but Y is missing" |
| To remove | the leanness findings |
| Drift | statements that do not follow from their current upstream |
| Bets | bet health, visibly apart from spec health |
| Top fixes | the must-fix-before-build chains, in dependency order |

In `--fix` and `--loop` the same report is joined by `audit-fixes-log.md` (the fixes applied per pass and the findings-per-round trend) and `human-decisions-needed.md` (items parked for the user). All three sit at the project root, are transient and git-ignored, and the loop deletes `spec-audit-report.md` after each pass it has fully remediated.

Before you call an area clean, check its invariants against the content yourself; a file that looks complete has not thereby been checked. A defect in this system itself (a check that is wrong, a rule that cannot be satisfied) goes to `scripts/plugin_feedback.py`, not into the audit report.

## Resources
- `references/exec-engine.md`
- The `--loop` protocol: `remediation-loop.md` (beside this file; load it only in loop mode)
- Worked example: `examples.md`
