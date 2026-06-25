---
name: audit-spec
description: >-
  The whole-spec audit — verify an EXISTING spec is complete, internally consistent, contradiction-free, covers all branches (product · domain · software), and is good enough that a coding agent can build from it WITHOUT guessing. Two depths: `consistency` (the judgment the linter can't make — semantic contradictions, scope adherence, decision coherence) and `full` (adds the domain/usage completeness pass that finds what's MISSING). Only `full` can declare code-gen readiness. The judgment layer ABOVE the mechanical tools, distinct from the per-task code-vs-spec conformance review. Loads the shared exec engine.
argument-hint: "[--depth consistency|full] [--scope all|<area>] — default: --depth full --scope all"
---

# audit-spec

**Load `${CLAUDE_PLUGIN_ROOT}/grill-shared/exec-engine.md` first and follow it.** This skill is the
**whole-spec audit**: a cross-area verification that the spec is complete, consistent, and buildable —
the **judgment layer above the deterministic tools**. The tools (`lint_spec.py`, `spec_status.py`,
`guard_derived.py`, `impact.py`, and — when API contracts exist — `check_contracts.py`) decide everything
mechanical; this skill makes only the calls a sound
script cannot. **Do not re-do what the tools already do** — run them, trust their output, and spend your
effort on meaning.

Two things stay separate throughout (the engine's two axes): **Axis 1 — is the spec consistent &
complete-enough?** vs **Axis 2 — do the BETS hold?** A green spec next to a red bet is the point; never
conflate them.

## The two boundaries this skill lives between
- **Below it — the linter.** Already enforces (don't repeat): closed-world & paths · file headers ·
  placeholders · dangling links · stable-ID resolution · **upstream-only reference direction** ·
  define-once · stage-purity · namespaced-ID ban · the `CMD-→UC-→AC-→T-` coverage chain · `THR-→SEC-` ·
  child→parent keying (`AC-`→`UC-`, `ASR-`→`NFR-`) · per-`T-` unresolved-gap (ERROR) · task-graph
  acyclicity (the `depends-on` DAG, ERROR) · task→upstream traceability · NFR `enforced-by` · module `role:` ·
  ADR status · **state-machine integrity (unreachable / dead-end / nondeterministic states)** ·
  **authorization completeness (every command has a rule; no blank decision cell)** · **typed-field
  consistency (a `retention`/`residency`/`class`/`SLA`/`price` stated twice must agree; every `DATA-` carries
  class/retention/residency)** · and the INFO heuristics for dev-trace language, skill/tool-name leaks, and
  adjective-without-a-bar. **Treat every linter ERROR as a `blocking` finding and move on** — your job
  starts where its soundness ends.
- **Beside it — the per-task code-conformance review.** That checks generated CODE against the spec, per task, after a
  build. This checks the SPEC itself, whole, independent of any build. Complementary, not overlapping.

## Modes (depth)
| `--depth` | Runs | Max verdict it may issue |
|---|---|---|
| `consistency` | Phases 0–2 (mechanical baseline + the Class-3 judgment checks) — cheap, repeatable, gate/CI-friendly | `CONSISTENT (domain not assessed)` — **may not** declare readiness |
| `full` (default) | adds Phase 3 (domain & usage completeness) + Phase 4 (bet/risk axis) | `CODE-GEN READY` / `NOT-READY` |

`--scope all` audits the whole spec; `--scope <area>` limits the read to one area + its reference
neighbours (for a focused re-check after a change).

## Ground rules
- **Source-of-truth fence (from the engine).** Audit the CURRENT working tree only — never git history,
  never outside the project folder. A missing artifact is a FINDING, never something to reconstruct.
- **Audit, don't mutate.** Default is report-only. If asked to fix, route every fix correctly (below);
  never bend the spec to match code, nor edit a derived artifact by hand to mask an upstream gap.
- **Severity on every finding:** `blocking` (breaks build-correctness or a hard invariant) · `important`
  (a real gap/ambiguity that will force a wrong guess) · `nit` (style/scan) · `suggestion` (deepening).
  Verdicts gate on `blocking` only.
- **Verify before flagging.** Read the actual artifact; quote `file:line` or the stable ID. A finding you
  can't ground is a guess — drop it.
- **Remediation routing (the most common way to corrupt a spec is to fix it in the wrong place):** an
  AUTHORED-zone defect (foundation, `04-domain/ddd`, `06-requirements/*`, `07-design-system`, `08-ux`,
  `11-commercial/*`, glossary/actors/ADRs) is fixed in place; a DERIVED-zone defect (`09-solution/*`,
  `05-functional-spec/`, `10-delivery/{conventions,tasks,impl-design}/`, root `CLAUDE.md`) is fixed by
  editing its UPSTREAM and re-deriving — **never** by hand-editing the derived file. State the route in
  the finding.

## Phase 0 — mechanical baseline (run, attribute, don't duplicate)
Run from the project root and record the raw counts:
`python3 ${CLAUDE_PLUGIN_ROOT}/tools/lint_spec.py` · `…/spec_status.py` · `…/guard_derived.py` (or its
check) · `…/impact.py` over any suspect IDs. **If `spec/09-solution/api` exists, also run
`…/check_contracts.py`** — it binds the machine contracts (`openapi.yaml`/`asyncapi.yaml`) to the ID graph:
every grillspec id a contract references (`x-grillspec-id` · `x-serves` · `SEC-` scopes · `x-data`) must
resolve to a real definition (ERROR), and every REST op must carry its traceability hooks + a mutation
security scope + an error response (WARN). It no-ops cleanly when PyYAML or the api folder is absent, so it
is safe to always attempt. Also run **`…/check_freshness.py`** (advisory) — it lists every artifact, grilled
OR derived, that cites an upstream definition which has CHANGED since the artifact was last reconciled
(`.claude/freshness.lock`). It never gates; it hands you the precise, complete candidate set for the
staleness judgment in Phase 2, so you no longer guess which IDs to spot-check. (No lock yet = a baseline gap
to note, not an error.) Every ERROR → `blocking`; every WARN → a `important`
candidate to confirm; every INFO heuristic → a candidate to judge (the linter flagged it precisely because
it cannot decide it — that decision is yours).

## Phase 1 — consistency judgment (what the linter can't decide soundly)
The predicates here are about MEANING, so no script is sound on them. Walk each:
- **Contradictions in prose** — the same number/policy/boundary stated twice that disagree (retention 30d
  in data vs 90d in compliance); a term used two ways within one bounded context; an actor named
  inconsistently across system-context, ddd, security, ux. The linter catches a *dangling* ID, never a
  *conflicting fact*. `blocking`.
- **Type-correctness within an allowed prefix** — an item filed as `NFR-` that is really an obligation
  (`OBL-`), a "requirement" that is actually a domain rule. Stage-purity caught the folder; only judgment
  catches the concept.
- **Scope adherence** — content that violates its own `scope:`/`excludes:` header; in/out-of-scope kept
  consistent across vision ↔ functional ↔ tasks (nothing built that's excluded, nothing required that's
  excluded).
- **Decision coherence** — every deliberate decision OR exclusion is an ADR (you can't detect an
  *unrecorded* decision mechanically); no two ADRs contradict; no artifact contradicts a live ADR.
- **Measurable-bar adequacy** — beyond the linter's adjective flag: is each requirement a real bar WITH a
  named enforcement (test · gate/fitness-fn · lint · infra · review), or a number with no teeth?
- **Adequacy ≠ presence** — the linter confirms a `THR-` has a linked `SEC-`; you judge whether the
  control actually mitigates the threat. Same for `OBL-`→control, `NFR-`→evidence.
- **House-style judgment** — the dev-trace/self-ref INFO candidates: is `new booking` legitimate domain
  language or a narration of the document's own edits? Are additions integrated in place, or bolted on at
  the end / duplicated in a parallel note beside content that already owns them?

## Phase 2 — structural verdicts (read the tool output, decide the gates)
- **Gate readiness** — architecture-readiness (requirements + design-system + ux carry no `UNRESOLVED`
  gap) before `09-solution/*` is trusted; implementation-readiness before `10-delivery`; delivery-readiness
  before code. Report each gate met / not-met with its blocking items. **Delivery-readiness explicitly requires
  the deploy spine the tasks/build will reference to exist**: `infra-ops/topology.md` names the **ratified
  environment set + promotion path**, `infra-ops/cicd.md` defines the **end-to-end promotion workflow** (ordered
  hops + per-hop gate), and `test/levels.md` names the **e2e target environment** (the preview/e2e/staging env
  e2e runs against) — a task that deploys to "the first env of the promotion path" or runs e2e "against the
  deployed env" is dangling if these aren't pinned. Missing any is a delivery-readiness blocker.
- **Artifact-staleness (grilled AND derived)** — does each artifact's content still follow from the CURRENT
  upstream? `guard_derived.py` proves a derived file wasn't hand-edited; it cannot prove it was re-derived
  after upstream moved, and it says nothing about a grilled artifact going stale. `check_freshness.py`
  (Phase 0) closes that: it hands you every artifact whose CITED upstream definition has drifted — work that
  candidate set, judging whether each drift is materially relevant (a renamed field that an NFR keys on vs a
  typo fix). A derived claim that no longer follows from current upstream → `blocking`, routed to "re-run the
  derive-* step"; a stale GRILLED artifact → `important`, routed to "re-grill the area against the corrected
  upstream." Freshness is advisory, not a verdict — a drift you judge immaterial is dismissed with a note,
  not a finding.

## Phase 3 — domain & usage completeness  *(--depth full only — the part nothing mechanical can do)*
You cannot find a MISSING requirement by checking that references resolve — a spec where every link
resolves can still omit an entire category of real behavior. You find it only by building an independent
model of the domain and diffing. Do it for real; this is the skill's reason to exist.

1. **Blind re-derivation, then diff (highest yield).** From discovery + vision + customers + market + your
   own knowledge of THIS domain, and BEFORE leaning on the ddd, independently write down the real entities,
   each entity's full lifecycle, the core business rules, the money/time/identity mechanics, the regulatory
   realities, and the full actor roster with each actor's real goal. THEN diff against the spec. Every item
   in your model with no home in the spec is a candidate missing branch. The spec can't show you its own
   blind spots — this is how you see them.
2. **Per-entity lifecycle reality.** For each entity, ask what states the BUSINESS needs — especially the
   abnormal terminations products forget: cancel · refund · dispute/chargeback · expire · suspend ·
   reactivate · merge · split · delete/right-to-erasure · archive · account-closure · fraud-hold. A missing
   state is a domain gap, not a graph error.
3. **Usage-side journeys.** Per persona × JTBD, walk the real journey through its unglamorous parts:
   first-run/empty state · abandon-and-return · permission changed mid-action · mobile/offline/flaky ·
   at-scale (1,000 at once) · undo · hit-a-limit · blocked-by-another-actor. At each step: "what does the
   system do here?" — no answer = a gap.
4. **Business-rule stress & interaction.** For each rule: its exceptions, its exact boundary, and — richest
   of all — what happens when it COLLIDES with another rule (refund on a partially-shipped order; two
   promotions stacking; cancellation during a migration; downgrade with usage already over the new limit).
   Rule conflicts almost never surface as a broken reference.
5. **Universal edge-generators** — apply each to the model: money (rounding · currency · negative/zero ·
   tax · partial) · time (timezone · DST · ordering · retroactive change · expiry · clock skew) · identity
   (duplicates · merges · renames · deletion of a referenced entity) · quantity (zero · one · max ·
   fractional · oversell) · concurrency (two actors, one resource · lost update) · dependents (what happens
   to children when a parent is removed). Each generator the model has no answer for is a gap.
6. **Is the model RIGHT, not just consistent?** Do the bounded-context boundaries match how the business
   segments the world? Are aggregate boundaries where the TRUE transactional invariants live? Is the
   ubiquitous language the domain expert's actual words, or invented? A wrong-but-consistent model produces
   correct code for the wrong thing — the most expensive failure.

**Know your limits — never rubber-stamp.** Where the domain is specialized and a claim can't be verified
from first principles (clinical logic, financial/tax regulation, safety rules, niche mechanics), flag it
`important: needs-domain-validation` and route it to a domain-expert review or a throwaway spike — do not
confirm a rule you can't actually check. A confident "looks complete" on an un-modeled domain is the
failure this phase exists to prevent.

## Phase 4 — code-gen readiness & the bet axis  *(--depth full only)*
- **Per buildable slice (`T-`):** would the coding agent have everything and guess NOTHING? All
  referenced IDs resolve and are settled (no `UNRESOLVED` it needs — `blocking` if not); its scoped inputs
  exist (boundary contracts + architecture seam + declared `role:` + conventions + relevant glossary; a UI
  slice has its `DS-` contract + the kept prototype); the test strategy MANUFACTURES the slice's edges;
  every decision the code needs is in the spec or an ADR. Zero load-bearing ambiguity. **Any non-`N/A`
  `human-prereq` on the slice is resolved (provisioned) or explicitly waived** — a slice that can't be built
  without an unmet human action is not ready (`blocking`).
- **Ratify axis — un-ratified user-owned values.** A user-owned VALUE the engines require to be ratified
  (NFR/SLA/SLO numbers · retention/residency · jurisdiction/regimes · pricing & tier limits · environments &
  git workflow · cloud/region/datastore/IdP commitments · a11y level · DR tier · cost ceiling · test-rigor
  thresholds · accepted-risk · authorization allow-rules · the MVP cut) that is still a `ratify`/`unconfirmed`
  proposed-default — i.e. a default the human never confirmed — is **not a settled requirement**. Flag every
  load-bearing one `important` (a CRITICAL-path one — an NFR a slice builds to, a price, a residency footprint —
  is `blocking`), routed to "surface for ratification." A green spec built on silently-picked user values is
  exactly the failure this catches; a complete schema is never proof the numbers are the user's.
- **Bet axis (Axis 2, kept separate):** every bet carries a validation status; every CRITICAL bet is
  Validated or Accepted-risk (an Invalidated critical bet is a high-priority open point); kill-criteria are
  present and measurable; every risk has category · probability · impact · owner · mitigation · status;
  every tech-debt item has a paydown trigger.

## Output
Write **`spec-audit-report.md` at the PROJECT ROOT** (a sibling of `spec/`, like `GRILLSPEC-FEEDBACK.md` —
it is meta-commentary, not timeless project documentation, so it never goes inside the closed-world `spec/`).
Print a summary to the session. The report contains:

**Session summary = ordered fix-chains, never authored/derived buckets.** A single fix often spans both
zones — a defect *located* in an authored artifact can be *root-caused* upstream and *propagate* into a
re-derive (a wrong `06-requirements` item whose real cause is `ddd`, fixed by editing ddd → re-deriving
`05-functional-spec` → re-grilling the requirement against the corrected 05). Splitting findings into a
flat "authored zone / derived zone" list hides this and reads as a contradiction (consuming a derived
artifact never makes the consumer derived; the fix-zone is set by who *writes* the file, propagation by the
reference graph). So print each finding as a **dependency-ordered chain** —
`<symptom location> → <upstream edit> → <re-derive step(s)> → <re-grill/verify>` — sequenced so every edit
precedes the re-derivations that depend on it (fix upstream first; re-derive a hinge like 05 before
re-grilling the authored areas that read it). The report contains:

| Section | Contents |
|---|---|
| Verdict header | per-gate go/no-go (desirability · architecture-readiness · implementation-readiness · delivery-readiness) + overall **CODE-GEN READINESS: READY / NOT-READY** (or `CONSISTENT (domain not assessed)` in `consistency` mode) + the blocking count |
| Findings | table sorted blocking → important → nit → suggestion: `severity · area · location (file:line / ID) · rule violated · finding · remediation route` |
| Coverage gaps | the missing branches from Phase 3, each concrete: "X exists but Y is missing" |
| Contradictions | each with both conflicting locations quoted |
| Stale-derived | derived artifacts that no longer follow from upstream + the re-derive step |
| Bet/risk snapshot | Axis 2, visibly separate from spec health |
| Top fixes | the must-fix-before-codegen items as dependency-ordered fix-chains (`symptom → upstream edit → re-derive → re-grill`), upstream edits before the re-derives that consume them — not authored/derived buckets |

No code, no `spec/` edits. **Never claim "complete" on an un-re-validated artifact** — re-run the
invariants across the content yourself; "looks complete" is never "is consistent." A defect in THIS SYSTEM
(an unsatisfiable rule, a wrong check) is routed via `${CLAUDE_PLUGIN_ROOT}/tools/plugin_feedback.py`, never
into the audit report.

## Resources
- `${CLAUDE_PLUGIN_ROOT}/grill-shared/exec-engine.md`
- Worked example: `examples.md`
