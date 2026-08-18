---
name: audit-spec
description: >-
  Audit an EXISTING spec for completeness, consistency, contradictions, and whether a coding agent can build it without guessing — the judgment layer above the mechanical tools. Report-only by default; --fix remediates in-session, --loop converges to zero findings. Only --depth full declares code-gen readiness. Loads the shared exec engine.
---

<!-- grillspec-portable-resources -->
> Resource paths in this skill are relative to this installed skill directory. Resolve `references/...` and `scripts/...` from that directory, not from the project working directory; use an absolute path when executing a bundled script.

# audit-spec

**Load `references/exec-engine.md` first and follow it.** This skill is the
**whole-spec audit**: a cross-area verification that the spec is complete, consistent, and buildable —
the **judgment layer above the deterministic tools**. The tools (`lint_spec.py`, `spec_status.py`,
`guard_derived.py`, `impact.py`, and — when API contracts exist — `check_contracts.py`) decide everything
mechanical; this skill makes only the calls a sound
script cannot. **Do not re-do what the tools already do** — run them, trust their output, and spend your
effort on meaning.

Two things stay separate throughout (the spec's two axes): **Axis 1 — is the spec consistent &
complete-enough?** vs **Axis 2 — do the BETS hold?** A green spec next to a red bet is the point; never
conflate them.

## The two boundaries this skill lives between
- **Below it — the linter.** Already enforces (don't repeat): closed-world & paths · file headers ·
  placeholders · dangling links · stable-ID resolution · **upstream-only reference direction** ·
  define-once · stage-purity · namespaced-ID ban · the downstream-coverage map (`CMD-→UC-→AC-→T-`,
  `AGG-→DATA-`, `NFR-→ASR-/SLO-`, `OBL-→control`, `EVT-→consumer`, …) · `THR-→SEC-` · `INV-→AC-` (an invariant is asserted by an AC, or enforced structurally) ·
  child→parent keying (`AC-`→`UC-`, `ASR-`→`NFR-`) · **derived→driver backref presence** (`JRN-`→`UC-`,
  `SLO-`→`NFR-`, `ML-`→`UC-`, each cited co-located on the child's own definition; an impl-design
  `<module>.md` names its `MOD-` + `T-`) · per-`T-` unresolved-gap (ERROR) · task-graph
  acyclicity (the `depends-on` DAG, ERROR) · task→upstream traceability · **AC single-owner** (each in-scope `AC-` claimed by exactly one task) · NFR `enforced-by` · module `role:` ·
  ADR status · **state-machine integrity (unreachable / dead-end / nondeterministic states)** ·
  **authorization completeness (every command has a rule; no blank decision cell)** · **typed-field
  consistency (a `retention`/`residency`/`class`/`SLA`/`price` stated twice must agree; every `DATA-` carries
  class/retention/residency)** · **task-cell integrity (an `afk:eligible` non-`N/A`-`ux` task's
  `prototype-review` review-cleared · a non-`N/A` `ux` cell structured — cites its `JRN-` + states · `ux`↔`a11y`
  consistency · a reuse-claim anchored to its `SCR-`)** · and the INFO heuristics for dev-trace language, skill/tool-name leaks, and
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

**Remediation modes** (report-only is the default; these are the sanctioned mutation modes):
| Mode | Does | Ends when |
|---|---|---|
| `--fix` | ONE audit pass, then remediate every finding at its correct fix-zone and **drain the propagation tail in-session** (the exit contract below) | findings fixed · impact set fully re-derived · mechanical baseline green |
| `--loop` | repeat `--fix` passes at full depth with a **parallel read-only auditor fan-out** — load `remediation-loop.md` (sibling of this SKILL.md) and follow it | **K=2 consecutive dry batches** + a final clean full sweep + baseline green |

**The fix-mode exit contract (what "fixed" is allowed to mean).** After the last upstream edit: run
`python3 scripts/impact.py <changed-IDs…>` (or `--since <ref>`) → for **every derived
artifact in the impact set**, re-run its owning derive step — explicitly including the terminal derived
layer a partial propagation most often strands: `10-delivery/conventions|tasks|impl-design` and the
root canonical `AGENTS.md` + import-only `CLAUDE.md`, not just `05`/`09` — → `python3 scripts/guard_derived.py --record <re-derived
paths>` + `…/check_freshness.py --record <all touched paths>` → re-run the Phase-0 baseline to green. **You
may not report "fixed" or "clean" while the impact set of your own edits contains a derived artifact that
was not re-derived** — a computed-but-unprocessed impact set is an unfinished fix, and saying otherwise is
the false-success this contract exists to stop. (A re-derive you genuinely can't run — a missing upstream
decision — is parked as an explicit stale hand-off in the report, never silently dropped.)

## Ground rules
- **Source-of-truth fence (from the engine).** Audit the CURRENT working tree only — never git history,
  never outside the project folder. A missing artifact is a FINDING, never something to reconstruct.
- **Audit, don't mutate — unless in `--fix`/`--loop`.** Default is report-only. In the remediation modes,
  every fix follows the routing below and the exit contract above; the fan-out auditors stay **read-only**
  in every mode. Never bend the spec to match code, nor edit a derived artifact by hand to mask an
  upstream gap.
- **Severity on every finding:** `blocking` (breaks build-correctness or a hard invariant) · `important`
  (a real gap/ambiguity that will force a wrong guess) · `nit` (style/scan) · `suggestion` (deepening).
  Verdicts gate on `blocking` only.
- **Verify before flagging.** Read the actual artifact; quote `file:line` or the stable ID. A finding you
  can't ground is a guess — drop it.
- **Remediation routing (the most common way to corrupt a spec is to fix it in the wrong place):** an
  AUTHORED-zone defect (foundation, `04-domain/ddd`, `06-requirements/*`, `07-design-system`, `08-ux`,
  `11-commercial/*`, glossary/actors/ADRs) is fixed in place; a DERIVED-zone defect (`09-solution/*`,
  `05-functional-spec/`, `10-delivery/{conventions,tasks,impl-design}/`, root canonical `AGENTS.md` + import-only `CLAUDE.md`) is fixed by
  editing its UPSTREAM and re-deriving — **never** by hand-editing the derived file. State the route in
  the finding.

## Phase 0 — mechanical baseline (run, attribute, don't duplicate)
Run from the project root and record the raw counts:
`python3 scripts/lint_spec.py` · `…/spec_status.py` · `…/guard_derived.py` (or its
check) · `…/impact.py` over any suspect IDs. **If `spec/09-solution/api` exists, also run
`…/check_contracts.py`** — it binds the machine contracts (`openapi.yaml`/`asyncapi.yaml`) to the ID graph:
every grillspec id a contract references (`x-grillspec-id` · `x-serves` · `SEC-` scopes · `x-data`) must
resolve to a real definition (ERROR), and every REST op must carry its traceability hooks + a mutation
security scope + an error response (WARN). It no-ops cleanly when PyYAML or the api folder is absent, so it
is safe to always attempt. Also run **`…/check_freshness.py`** (advisory) — it lists every artifact, grilled
OR derived, that cites an upstream definition which has CHANGED since the artifact was last reconciled
(`.grillspec/freshness.lock`). It never gates; it hands you the precise, complete candidate set for the
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
  slice has its `DS-` contract + its `JRN-` journey reference (+ the interaction-states it realises) + the kept prototype, and its `prototype-review` gate is settled — for an `afk: eligible` non-`N/A`-`ux` slice that means the prototype is **frozen (human-reviewed at finalization)** or explicitly `prototype-review: waived — <why>` (an unreviewed / JIT-generated screen riding an `eligible` slice, or an open HITL `visual/UX decision` escalation, is `blocking`); auto-AFK of this gate is legitimate only where `ux` is `N/A` (headless / reuses-DS); a UI slice also pins a non-`N/A` `a11y` cell, and an `obs`/`ml`-bearing spec reaches the slices through those dimensions — a cross-cutting obligation minted upstream but reaching no task's dimension cell is `important` (it will be silently dropped at build time)); the test strategy MANUFACTURES the slice's edges;
  every decision the code needs is in the spec or an ADR. Zero load-bearing ambiguity. **Any non-`N/A`
  `human-prereq` on the slice is resolved — its credential marked `provisioned` in the `_provisioning.md`
  register — or explicitly waived** — a slice that can't be built without an unmet human action is not ready
  (`blocking`); a bare free-prose ‘arrives via T-001’ with no `provisioned` register row does not count as resolved.
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
| Verdict header | per-gate go/no-go (desirability · architecture-readiness · implementation-readiness · delivery-readiness) + overall **CODE-GEN READINESS: READY / NOT-READY** (or `CONSISTENT (domain not assessed)` in `consistency` mode) + the blocking count + a **`depth:`** marker and a **`commit: <HEAD sha>`** stamp of the tree audited — the whole-build audit reads both to decide whether this report still evidences its spec-clean precondition (a report whose commit HEAD has moved past is stale) |
| Findings | table sorted blocking → important → nit → suggestion: `severity · area · location (file:line / ID) · rule violated · finding · remediation route` |
| Coverage gaps | the missing branches from Phase 3, each concrete: "X exists but Y is missing" |
| Contradictions | each with both conflicting locations quoted |
| Stale-derived | derived artifacts that no longer follow from upstream + the re-derive step |
| Bet/risk snapshot | Axis 2, visibly separate from spec health |
| Top fixes | the must-fix-before-codegen items as dependency-ordered fix-chains (`symptom → upstream edit → re-derive → re-grill`), upstream edits before the re-derives that consume them — not authored/derived buckets |

In `--fix`/`--loop`: the same report plus `audit-fixes-log.md` (cumulative per-pass fix log + findings-per-round trend) and `human-decisions-needed.md` (parked ratification items) at the project root — all three are meta-commentary siblings of `spec/`, transient and git-ignored, and the loop deletes `spec-audit-report.md` after each pass it fully remediates.

Report-only mode: no code, no `spec/` edits. **Never claim "complete" on an un-re-validated artifact** — re-run the
invariants across the content yourself; "looks complete" is never "is consistent." A defect in THIS SYSTEM
(an unsatisfiable rule, a wrong check) is routed via `scripts/plugin_feedback.py`, never
into the audit report.

## Resources
- `references/exec-engine.md`
- The `--loop` protocol: `remediation-loop.md` (sibling of this file — load it only in loop mode)
- Worked example: `examples.md`
